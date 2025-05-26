from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from app import models, oauth2, schemas, utils
from app.database import get_db
from sqlalchemy.exc import SQLAlchemyError
from app.services.otp_service import send_otp_email
import httpx
import os
from datetime import datetime

router = APIRouter(tags=["Authentication"])

# Existing login route
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

# Existing register route
@router.post(
    "/register", response_model=schemas.UserAuthOut, status_code=status.HTTP_201_CREATED
)
def register(user: schemas.UserRegister, db: Session = Depends(get_db)):
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

# Existing change password route
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

# Existing send OTP route
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

# New Google authentication route
@router.post("/google_auth", response_model=schemas.UserAuthOut)
async def google_auth(code: str, db: Session = Depends(get_db)):    
    try:
        # Exchange authorization code for access token
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                    "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                    "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI"),
                    "grant_type": "authorization_code",
                },
            )

        if token_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to obtain access token from Google",
            )

        token_data = token_response.json()
        access_token = token_data.get("access_token")

        # Fetch user info from Google
        async with httpx.AsyncClient() as client:
            user_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )

        if user_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to fetch user info from Google",
            )

        user_data = user_response.json()
        email = user_data.get("email")
        name = user_data.get("name", "Google User")

        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not provided by Google",
            )

        # Check if user exists in the database
        user = db.query(models.User).filter(models.User.email == email).first()

        if not user:
            # Create a new user if they don't exist
            new_user = models.User(
                email=email,
                name=name,
                password=utils.get_password_hash("google-auth-placeholder"),  # Placeholder password
                created_at=datetime.utcnow(),
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            user = new_user

        # Generate JWT token
        jwt_token = oauth2.create_access_token({"user_id": str(user.id)})

        return schemas.UserAuthOut(
            access_token=jwt_token,
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
        
        
        
        
        
# client-id = 151562397949-31badqvl99slo1v8p8j50l0logtigosm.apps.googleusercontent.com