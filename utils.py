import shutil
import os

# New constant for the temp directory
TEMP_DIR = "temp"


def _save_file_to_server(uploaded_file, path=TEMP_DIR, save_as="default"):
    extension = os.path.splitext(uploaded_file.filename)[-1]
    
    temp_file = os.path.join(path, save_as + extension) if extension not in save_as else os.path.join(path, save_as)

    with open(temp_file, "wb") as buffer:
        shutil.copyfileobj(uploaded_file.file, buffer)

    return temp_file

