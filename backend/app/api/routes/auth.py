from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta
from app.schemas.user import UserCreate, UserLogin, Token, UserResponse
from app.db.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.config import settings

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, cursor=Depends(get_db)):
    """
    Register a new user.

    - **name**: User's full name
    - **mail_address**: User's email address (must be unique)
    - **phone_number**: User's phone number (optional)
    - **password**: User's password (will be hashed)
    - **type_id**: User type ID (1=Admin, 2=Organizer, 3=Venue Owner, 4=Attendee)
    """
    # Check if user already exists
    cursor.execute(
        "SELECT user_id FROM users WHERE mail_address = %s",
        (user.mail_address,)
    )
    if cursor.fetchone():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash password
    hashed_password = get_password_hash(user.password)

    # Insert new user
    cursor.execute(
        """
        INSERT INTO users (type_id, name, mail_address, phone_number, password_hash)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING user_id, type_id, name, mail_address, phone_number, created_at
        """,
        (user.type_id, user.name, user.mail_address, user.phone_number, hashed_password)
    )

    new_user = cursor.fetchone()
    return dict(new_user)


@router.post("/login", response_model=Token)
def login(user_credentials: UserLogin, cursor=Depends(get_db)):
    """
    Login with email and password.

    Returns a JWT access token that should be used in subsequent requests.

    - **mail_address**: User's email address
    - **password**: User's password
    """
    # Fetch user by email
    cursor.execute(
        "SELECT user_id, password_hash FROM users WHERE mail_address = %s",
        (user_credentials.mail_address,)
    )
    user = cursor.fetchone()

    # Verify user exists and password is correct
    if not user or not verify_password(user_credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user["user_id"])},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
