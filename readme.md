# Vision Text OCR Service

This project is the backend API service for the Vision Text OCR application. A service that captures text from images using optical character recognition. See frontend ui service [here](https://github.com/hartake/vision-text-ocr-ui)

## Purpose

This FastAPI service provides REST endpoints for uploading images and extracting text from them using OCR technology. It processes image files, runs OCR analysis, and stores the extracted text in a PostgreSQL database for future retrieval.

## Core Technology Stack

- **FastAPI:** A modern, fast web framework for building APIs with Python.
- **PostgreSQL:** A relational database for storing OCR results.
- **asyncpg:** An asynchronous PostgreSQL database adapter for Python.
- **pytesseract:** Python wrapper for Google's Tesseract OCR engine.
- **Pydantic:** Data validation and settings management using Python type annotations.

## Architecture

This service is the backend component of a client-server decoupled full-stack application. It handles the core business logic, image processing, OCR operations, and data persistence for the Vision Text application. It provides a REST API that the frontend React application consumes.


## API Endpoints

- `POST /api/v1/extract_text_async` - Upload images and extract text asynchronously
- `GET /api/v1/load_saved_text_from_db` - Retrieve saved OCR results
- `GET /api/v1/load_saved_text_from_db/{id}` - Retrieve a specific OCR result by ID
- `POST /api/v1/save_text_to_db` - Save OCR text to database
- `POST /api/v1/feedback` - Submit feedback about the service


## Local Development Setup

1.  **Create and activate a virtual environment**:

    *   On Windows:
        ```sh
        python -m venv venv
        .\venv\Scripts\activate
        ```

    *   On macOS & Linux:
        ```sh
        python3 -m venv venv
        source venv/bin/activate
        ```

2.  **Install Dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

3.  **Environment Variables**:
    Create a `.env` file by copying the example template. This file will hold your local database credentials and is ignored by Git.

    ```sh
    cp .env.example .env
    ```
    
    Now, open the `.env` file and fill in your database connection details.

4.  **Accessing the Database (Optional)**:
    You can use a database management tool like [pgAdmin](https://www.pgadmin.org/) or DBeaver to connect to your PostgreSQL database, view the tables, and query data directly.

5.  **Run the Application**:
    For development with auto-reload, run:
    ```sh
    python main.py
    ```
    Or with Uvicorn:
    ```sh
    uvicorn main:app --reload
    ```
    The application will be running on `http://localhost:8000`.

## API Preview

![API Swagger Docs](preview/api-swagger.png)