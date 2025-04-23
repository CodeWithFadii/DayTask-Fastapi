from fastapi import APIRouter, File, UploadFile, HTTPException
import shutil
import os
import uuid
import pytesseract
import re
from app.utils import preprocess_image  # Make sure this exists and works

router = APIRouter(tags=["Additional"])

# Setup upload folder
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Set tesseract path if needed
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"


# Route: Upload image
@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    ext = file.filename.split(".")[-1] # type: ignore
    filename = f"{uuid.uuid4()}.{ext}"
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "filename": filename,
        "url": f"http://13.50.169.165/static/uploads/{filename}",
    }


# Route: Read text from image
@router.post("/read-text")
async def read_text(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"): # type: ignore
        raise HTTPException(status_code=400, detail="Please upload a valid image.")

    try:
        contents = await file.read()
        image = preprocess_image(contents)
        text = pytesseract.image_to_string(image)
        cleaned_text = re.sub(r"[^\x00-\x7F]+", "", text).strip()
        return {"text": cleaned_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read text: {str(e)}")
