from typing import List
from fastapi import APIRouter, File, UploadFile, HTTPException
import fitz
import os, uuid, pytesseract, shutil, re
from app import schemas
from deepface import DeepFace
from PIL import Image
import io
import cv2
import numpy as np
from fastapi.responses import JSONResponse
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
    try:
        ext = file.filename.split(".")[-1]  # type: ignore
        filename = f"{uuid.uuid4()}=-0987654321.{ext}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {
            "filename": filename,
            "url": f"http://13.50.169.165/static/uploads/{filename}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")


# Route: Read text from image
@router.post("/read-text")
async def read_text(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):  # type: ignore
        raise HTTPException(status_code=400, detail="Please upload a valid image.")

    try:
        contents = await file.read()
        image = preprocess_image(contents)
        text = pytesseract.image_to_string(image, lang="eng")
        cleaned_text = re.sub(r"[^\x00-\x7F]+", "", text).strip()
        return {"text": cleaned_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read text: {str(e)}")


@router.post("/read-pdf", response_model=List[schemas.ExtractionResult])
async def read_pdf(files: List[UploadFile] = File(...)):
    # Check if any files were uploaded
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")

    results = []
    for file in files:
        # Validate that the file is a PDF
        if file.content_type != "application/pdf":
            results.append(
                schemas.ExtractionResult(filename=file.filename, error="Not a PDF file.")  # type: ignore
            )
            continue

        try:
            # Read the file contents asynchronously
            contents = await file.read()

            # Load the PDF from bytes
            pdf = fitz.open(stream=contents, filetype="pdf")

            # Extract text from all pages
            text = ""
            for page in pdf:
                text += page.get_text()  # type: ignore

            # Clean the extracted text
            cleaned_text = text.strip()

            # Close the PDF to free resources
            pdf.close()

            # Add successful extraction to results
            results.append(schemas.ExtractionResult(filename=file.filename, text=cleaned_text))  # type: ignore

        except Exception as e:
            # Add error information if processing fails
            results.append(
                schemas.ExtractionResult(filename=file.filename, error=str(e))  # type: ignore
            )

    return results


def read_image(file: UploadFile):
    content = np.frombuffer(file.file.read(), np.uint8)
    image = cv2.imdecode(content, cv2.IMREAD_COLOR)
    return image


@router.post("/verify-face")
async def verify_faces(image1: UploadFile = File(...), image2: UploadFile = File(...)):
    img1 = read_image(image1)
    img2 = read_image(image2)

    try:
        result = DeepFace.verify(img1, img2, enforce_detection=True)
        is_verified = result["verified"]
        return {"match": is_verified}
    except Exception as e:
        return {"error": str(e)}
