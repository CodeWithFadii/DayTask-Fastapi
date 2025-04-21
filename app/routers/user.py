from typing import Optional
from uuid import UUID
from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from app import models, oauth2, schemas, utils
from app.database import get_db

from fastapi import File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import uuid

router = APIRouter(tags=["Users"])


# Getting a user by Token
@router.get("/user", response_model=schemas.UserOut)
def get_current_user(
    user_data: schemas.User = Depends(oauth2.get_current_user),
):
    try:
        return schemas.UserOut(user=user_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )


# Getting a user by ID
@router.get(
    "/users/{id}",
    response_model=schemas.UserOut,
    dependencies=[Depends(oauth2.check_token_validity)],
)
def get_user_by_id(
    id: UUID,
    db: Session = Depends(get_db),
):
    try:
        user_query = db.query(models.User).filter(models.User.id == id)
        user = user_query.first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"There is no user with id: {id}",
            )

        return schemas.UserOut(user=schemas.User.model_validate(user))

    except HTTPException as e:
        raise e  # Reraise the HTTPException for custom error handling
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching the user: {str(e)}",
        )


# Getting all users
@router.get(
    "/users",
    response_model=schemas.PaginatedUsers,
    dependencies=[Depends(oauth2.check_token_validity)],
)
def get_users_with_cursor(
    db: Session = Depends(get_db),
    limit: int = 10,  # Default to 10 users per page
    cursor: Optional[UUID] = None,  # Cursor to indicate where to start fetching users
):
    try:
        if limit > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit exceeds the maximum allowed value of 100.",
            )

        # Get the total number of users
        total_users = db.query(models.User).count()

        # Query for users starting from the given cursor (if any)
        query = db.query(models.User).order_by(models.User.id)

        if cursor:
            query = query.filter(models.User.id > cursor)

        users_query = query.limit(limit).all()

        if not users_query:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No users found.",
            )

        users_list = [schemas.User.model_validate(user) for user in users_query]

        # Get the id of the last user to be used as the cursor for the next request
        next_cursor = users_query[-1].id if users_query else None
        # Correctly assign the id value

        return schemas.PaginatedUsers(
            users=users_list, total_count=total_users, next_cursor=next_cursor  # type: ignore
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{str(e)}",
        )


# Static file serving
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
router.mount("/static", StaticFiles(directory="static"), name="static")


# Upload route
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
