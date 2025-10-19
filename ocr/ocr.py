import pytesseract
import asyncio

async def read_image(img_path, lang='eng'):
    try:
        text = pytesseract.image_to_string(img_path, lang=lang)
        await asyncio.sleep(2)
        return text
    except Exception as e:
        err_msg = f"[ERROR] Unable to process file: {img_path}. Exception: {e}"
        print(err_msg)
        return err_msg
