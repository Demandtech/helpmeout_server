from .. import models, schemas, database, utils, oauth2
from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import session
import logging
import secrets

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
async def create_user(user: schemas.CreateUser, db: session = Depends(database.get_db)):
    try:
        existing_user = db.query(models.User).filter(
            models.User.email == user.email).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exist")

        if not utils.is_strong_password(user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Enter a strong password.",
            )

        if not utils.is_name_str(user.first_name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Enter a valid first name"
            )

        if not utils.is_name_str(user.last_name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Enter a valid last name"
            )

        hashed_password = await utils.hash(user.password)
        otp_code = str(secrets.randbelow(100000))

        new_user = models.User(
            email=user.email,
            password=hashed_password,
            verification_token=otp_code,
            first_name=user.first_name,
            last_name=user.last_name
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        await utils.send_verification_email(
            user.email, otp_code, 'Verify Your account')

        return {"message": "Account created Successfully, and Verification email sent", "user": new_user}
    except Exception as e:
        logger.exception(f"Error creating user: {e}")
        raise


@router.post('/verify', status_code=status.HTTP_202_ACCEPTED)
async def verify_user(payload: schemas.VerifyUser, db: session = Depends(database.get_db)):
    unverified_user = db.query(models.User).filter(
        models.User.verification_token == payload.otp_code, models.User.id == payload.user_id, models.User.is_verified == False).first()

    if not unverified_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")

    unverified_user.is_verified = True
    unverified_user.verification_token = None
    db.commit()
    db.refresh(unverified_user)

    await utils.send_confirmation_email(
        unverified_user.email, 'http://localhost:5173/auth', 'Email Verification Successfull! Welcome to HelpMeOut')

    return {"message": "Account verification successful"}


@router.get('/me')
def get_user(db: session = Depends(database.get_db), current_user: dict = Depends(oauth2.get_current_user)):
    try:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Aunthorized user")
        return current_user
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Aunthorized user")
