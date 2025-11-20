from fastapi import APIRouter, File, UploadFile, status, HTTPException
from typing import List
import time
import asyncio
import ocr.ocr as ocr
import utils
import database.database as database
import os
from models.models import OCRResultBase, OCRResultInDB, FeedbackBase, FeedbackInDB


TABLE_NAME = database.TABLE_NAME

router = APIRouter(prefix="/api/v1")

@router.post("/extract_text")
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
        texts = await asyncio.gather(*tasks)
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
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    time_taken = round((time.time() - s), 2)
    print(f"Total time taken (including DB save): {time_taken} seconds")

    return saved_ocr_results


@router.get("/load_saved_text_from_db", response_model=List[OCRResultInDB])
async def load_saved_text_from_db(limit: int = 100, offset: int = 0):
    async with database.cached_db_pool.acquire() as connection:
        query = f"""
            SELECT id, filename, extracted_text, created_at
            FROM {TABLE_NAME}
            ORDER BY created_at DESC
            LIMIT $1 OFFSET $2;
        """
        records = await connection.fetch(query, limit, offset)
        
        return [OCRResultInDB(**dict(record)) for record in records]


@router.get("/load_saved_text_from_db/{ocr_id}", response_model=OCRResultInDB)
async def load_saved_text_from_db_by_id(ocr_id: int):
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


@router.post("/save_text_to_db", response_model=OCRResultInDB, status_code=status.HTTP_201_CREATED)
async def save_text_to_db(ocr_result: OCRResultBase):
    async with database.cached_db_pool.acquire() as connection:
        query = f"""
            INSERT INTO {TABLE_NAME} (filename, extracted_text)
            VALUES ($1, $2)
            RETURNING id, filename, extracted_text, created_at;
        """
        saved_record = await connection.fetchrow(query, ocr_result.filename, ocr_result.extracted_text)
        
        if saved_record:
            return OCRResultInDB(**dict(saved_record))
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save OCR result.")


@router.post("/feedback", response_model=FeedbackInDB, status_code=status.HTTP_201_CREATED)
async def save_feedback(feedback: FeedbackBase):
    async with database.cached_db_pool.acquire() as connection:
        query = """
            INSERT INTO vision_text_feedback (comment)
            VALUES ($1)
            RETURNING id, comment, created_at;
        """
        saved_record = await connection.fetchrow(query, feedback.comment)
        
        if saved_record:
            return FeedbackInDB(**dict(saved_record))
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save feedback.")

