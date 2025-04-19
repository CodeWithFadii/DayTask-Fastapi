from fastapi import Depends, HTTPException, status, APIRouter
from pydantic import EmailStr
from sqlalchemy.orm import Session
from app import models, oauth2, schemas, utils
from app.database import get_db
from sqlalchemy.exc import SQLAlchemyError

from app.services.otp_service import send_otp_email

router = APIRouter(tags=["Authentication"])


@router.post("/login", response_model=schemas.UserAuthOut)
def login(credential: schemas.UserLogin, db: Session = Depends(get_db)):
    try:
        user = (
            db.query(models.User).filter(models.User.email == credential.email).first()
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email does not exist",
            )

        if not utils.verify_password(credential.password, user.password) is True:  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Credentials",
            )

        access_token = oauth2.create_access_token({"user_id": str(user.id)})

        return schemas.UserAuthOut(
            access_token=access_token,
            token_type="bearer",
            user=schemas.User.model_validate(user),
        )

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        )


@router.post(
    "/register", response_model=schemas.UserAuthOut, status_code=status.HTTP_201_CREATED
)
def create_user(user: schemas.UserRegister, db: Session = Depends(get_db)):
    try:
        existing = db.query(models.User).filter(models.User.email == user.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists",
            )

        hashed_password = utils.get_password_hash(user.password)
        user.password = hashed_password
        new_user = models.User(**user.model_dump())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        access_token = oauth2.create_access_token({"user_id": str(new_user.id)})
        return schemas.UserAuthOut(
            access_token=access_token,
            token_type="bearer",
            user=schemas.User.model_validate(new_user),
        )

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )


# Change Password
@router.post("/change_password", response_model=schemas.ChangePasswordOut)
def change_password(request: schemas.ChangePassword, db: Session = Depends(get_db)):
    try:
        # Find the user
        existing = (
            db.query(models.User).filter(models.User.email == request.email).first()
        )
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email does not exist",
            )

        # Check if old password is correct
        is_verified = utils.verify_password(request.old_password, existing.password)  # type: ignore
        if not is_verified:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect current password",
            )

        # Update to new hashed password
        hashed_password = utils.get_password_hash(request.new_password)
        existing.password = hashed_password  # type: ignore
        db.commit()

        return schemas.ChangePasswordOut(
            success=True, message="Password updated successfully"
        )

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )


# Send Otp


@router.post(
    "/send_otp",
    response_model=schemas.OtpOut,
)
def send_otp(request: schemas.Otp):
    try:
        otp = send_otp_email(receiver_email=request.email)
        return schemas.OtpOut(otp=otp, message="Otp sent successfully")

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending otp: {str(e)}",
        )
