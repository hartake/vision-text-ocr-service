from fastapi import APIRouter, File, UploadFile, status, HTTPException
from typing import List
import time
import asyncio
import ocr.ocr as ocr
import utils
import database.database as database
import os
from models.models import OCRResultBase, OCRResultInDB


TABLE_NAME = database.TABLE_NAME

router = APIRouter()

@router.get("/")
def home():
    return {"message": "Visit the endpoint: /api/v1/extract_text to perform OCR."}

@router.post("/api/v1/extract_text")
async def extract_text(Images: List[UploadFile] = File(...)):
    response = {}
    s = time.time()
    for img in Images:
        temp_file = None
        try:
            temp_file = utils._save_file_to_server(img, save_as=img.filename)
            print("Images Uploaded: ", img.filename)
            text = await ocr.read_image(temp_file)
            response[img.filename] = text
        finally:
            if temp_file and os.path.exists(temp_file):
                os.remove(temp_file)
    response["Time Taken"] = round((time.time() - s),2)

    return response

@router.post("/api/v1/extract_text_async", response_model=List[OCRResultInDB])
async def extract_text_async(Images: List[UploadFile] = File(...)):
    s = time.time()
    
    saved_ocr_results: List[OCRResultInDB] = []
    
    tasks = []
    temp_files = []
    for img in Images:
        temp_file = utils._save_file_to_server(img, save_as=img.filename)
        temp_files.append(temp_file)
        print("Images Uploaded: ", img.filename)
        tasks.append(asyncio.create_task(ocr.read_image(temp_file)))

    try:
        texts = await asyncio.gather(*tasks) # Execute all OCR tasks concurrently

        async with database.cached_db_pool.acquire() as connection:
            for i, raw_extracted_text in enumerate(texts):
                original_filename = Images[i].filename
                
                processed_extracted_text = raw_extracted_text.replace('\n', ' ').replace('\r', '').strip()
                
                query = f"""
                    INSERT INTO {TABLE_NAME} (filename, extracted_text)
                    VALUES ($1, $2)
                    RETURNING id, filename, extracted_text, created_at;
                """
                
                saved_record = await connection.fetchrow(query, original_filename, processed_extracted_text)
                print("saved_record:",saved_record)
                
                if saved_record:
                    saved_ocr_results.append(OCRResultInDB(**dict(saved_record)))
                else:
                    # Todo: in prod space - log this error or handle it more robustly per image
                    print(f"Warning: Failed to save OCR result for {original_filename} to database.")
    finally:
        # Clean up parsed files
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    time_taken = round((time.time() - s), 2)
    print(f"Total time taken (including DB save): {time_taken} seconds")

    return saved_ocr_results


@router.get("/api/v1/load_saved_text_from_db", response_model=List[OCRResultInDB])
async def load_saved_text_from_db(limit: int = 100, offset: int = 0):
    """
    Retrieves a list of all saved OCR results from the database.
    Supports pagination with 'limit' and 'offset' query parameters.
    """
    async with database.cached_db_pool.acquire() as connection:
        query = f"""
            SELECT id, filename, extracted_text, created_at
            FROM {TABLE_NAME}
            ORDER BY created_at DESC
            LIMIT $1 OFFSET $2;
        """
        records = await connection.fetch(query, limit, offset)
        
        # Convert each asyncpg.Record to an OCRResultInDB Pydantic model
        return [OCRResultInDB(**dict(record)) for record in records]


@router.get("/api/v1/load_saved_text_from_db/{ocr_id}", response_model=OCRResultInDB)
async def load_saved_text_from_db_by_id(ocr_id: int):
    """
    Retrieves a single saved OCR result from the database by its ID.
    """
    async with database.cached_db_pool.acquire() as connection:
        query = f"""
            SELECT id, filename, extracted_text, created_at
            FROM {TABLE_NAME}
            WHERE id = $1;
        """
        record = await connection.fetchrow(query, ocr_id)
        
        if record:
            return OCRResultInDB(**dict(record))
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"OCR Result with ID {ocr_id} not found.")


@router.post("/api/v1/save_text_to_db", response_model=OCRResultInDB, status_code=status.HTTP_201_CREATED)
async def save_text_to_db(ocr_result: OCRResultBase):
    """
    Saves the extracted OCR text for a given filename to the database.
    """
    async with database.cached_db_pool.acquire() as connection:
        # SQL INSERT statement to save data, returning the generated id and created_at
        query = f"""
            INSERT INTO {TABLE_NAME} (filename, extracted_text)
            VALUES ($1, $2)
            RETURNING id, filename, extracted_text, created_at;
        """
        # Execute the query, passing Pydantic model fields as arguments
        # asyncpg returns a Record object, which we convert to a dictionary
        saved_record = await connection.fetchrow(query, ocr_result.filename, ocr_result.extracted_text)
        
        if saved_record: # Check if a record was actually returned
            # Convert the asyncpg.Record to a dictionary and then to our Pydantic model
            return OCRResultInDB(**dict(saved_record))
        else:
            # This case should ideally not be reached with RETURNING, but good for robustness
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save OCR result.")

