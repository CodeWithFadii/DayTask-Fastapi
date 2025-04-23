from fastapi import HTTPException, APIRouter
from fastapi import File, UploadFile
from fastapi.staticfiles import StaticFiles
import shutil
import os
import uuid
import pytesseract
import re
from app.utils import preprocess_image  # Ensure this function is defined correctly

router = APIRouter(tags=["Additional"])

# Static file serving
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
router.mount("/static", StaticFiles(directory="static"), name="static")

# Optional: Explicitly set the path to Tesseract if needed
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"



# Upload route
@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    ext = file.filename.split(".")[-1]  # type: ignore
    filename = f"{uuid.uuid4()}.{ext}"
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "filename": filename,
        "url": f"http://13.50.169.165/static/uploads/{filename}",
    }


# Read Text From Image
@router.post("/read-text")
async def read_text(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):  # type: ignore
        raise HTTPException(status_code=400, detail="Please upload a valid image.")

    try:
        contents = await file.read()

        # Preprocess for better OCR
        image = preprocess_image(contents)

        # Use pytesseract to extract text from image
        text = pytesseract.image_to_string(image)

        # Optional: Clean up the text
        cleaned_text = re.sub(r"[^\x00-\x7F]+", "", text).strip()

        return {"text": cleaned_text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read text: {str(e)}")
