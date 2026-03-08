from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
import logging

# Configuration (move to config file in production)
logger = logging.getLogger(__name__)
SECRET_KEY = "your-secret-key-change-this-in-production"  # Change this!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Router
router = APIRouter(prefix="/api/auth", tags=["authentication"])

# Pydantic models
class UserCreate(BaseModel):
    """User registration schema"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    """User login schema"""
    username: str
    password: str

class Token(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Token data schema"""
    username: Optional[str] = None
    user_id: Optional[int] = None

class UserResponse(BaseModel):
    """User response schema"""
    id: int
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime

# Utility functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> TokenData:
    """Decode and validate a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return TokenData(username=username, user_id=user_id)
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Database functions (replace with your ORM)
async def get_user_by_username(db: Session, username: str):
    """Get user by username from database"""
    # Replace with actual database query
    # Example: return db.query(User).filter(User.username == username).first()
    pass

async def get_user_by_email(db: Session, email: str):
    """Get user by email from database"""
    # Replace with actual database query
    # Example: return db.query(User).filter(User.email == email).first()
    pass

async def create_user(db: Session, user: UserCreate):
    """Create a new user in database"""
    # Replace with actual database operation
    # Example:
    # db_user = User(
    #     email=user.email,
    #     username=user.username,
    #     hashed_password=get_password_hash(user.password),
    #     full_name=user.full_name
    # )
    # db.add(db_user)
    # db.commit()
    # db.refresh(db_user)
    # return db_user
    pass

# Dependency to get current user
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current authenticated user from token"""
    token_data = decode_token(token)
    
    # Get user from database
    # user = await get_user_by_username(db, username=token_data.username)
    # if user is None:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="User not found",
    #     )
    # return user
    
    return token_data  # Return token data for now

# API Endpoints
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    # db: Session = Depends(get_db)  # Add database dependency
):
    """
    Register a new user
    
    - **email**: User's email address
    - **username**: Unique username (3-50 characters)
    - **password**: Strong password (minimum 8 characters)
    - **full_name**: User's full name (optional)
    """
    try:
        # Check if user already exists
        # existing_user = await get_user_by_email(db, user_data.email)
        # if existing_user:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="Email already registered"
        #     )
        
        # existing_username = await get_user_by_username(db, user_data.username)
        # if existing_username:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="Username already taken"
        #     )
        
        # Create new user
        # new_user = await create_user(db, user_data)
        
        # For demonstration, return mock data
        return UserResponse(
            id=1,
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            is_active=True,
            created_at=datetime.utcnow()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    # db: Session = Depends(get_db)  # Add database dependency
):
    """
    Login with username and password
    
    Returns access and refresh tokens
    """
    try:
        # Authenticate user
        # user = await get_user_by_username(db, form_data.username)
        # if not user or not verify_password(form_data.password, user.hashed_password):
        #     raise HTTPException(
        #         status_code=status.HTTP_401_UNAUTHORIZED,
        #         detail="Incorrect username or password",
        #         headers={"WWW-Authenticate": "Bearer"},
        #     )
        
        # Create tokens
        access_token = create_access_token(
            data={"sub": form_data.username, "user_id": 1}  # Use actual user.id
        )
        refresh_token = create_refresh_token(
            data={"sub": form_data.username, "user_id": 1}  # Use actual user.id
        )
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    # db: Session = Depends(get_db)  # Add database dependency
):
    """
    Refresh access token using refresh token
    """
    try:
        # Decode refresh token
        token_data = decode_token(refresh_token)
        
        # Verify it's a refresh token
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Create new tokens
        access_token = create_access_token(
            data={"sub": token_data.username, "user_id": token_data.user_id}
        )
        new_refresh_token = create_refresh_token(
            data={"sub": token_data.username, "user_id": token_data.user_id}
        )
        
        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token refresh failed: {str(e)}"
        )

@router.post("/logout")
async def logout(
    current_user = Depends(get_current_user)
):
    """
    Logout current user
    
    In a real application, you might want to:
    - Blacklist the token
    - Clear refresh token from database
    - Log the logout event
    """
    try:
        # Add token to blacklist or invalidate refresh token in database
        # Example: await blacklist_token(token)
        
        return {
            "message": "Successfully logged out",
            "user": current_user.username
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(get_current_user),
    # db: Session = Depends(get_db)  # Add database dependency
):
    """
    Get current authenticated user information
    """
    try:
        # Get full user info from database
        # user = await get_user_by_username(db, current_user.username)
        
        # For demonstration, return mock data
        return UserResponse(
            id=current_user.user_id or 1,
            email="user@example.com",
            username=current_user.username,
            full_name="John Doe",
            is_active=True,
            created_at=datetime.utcnow()
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user info: {str(e)}"
        )

@router.post("/change-password")
async def change_password(
    current_password: str,
    new_password: str = Field(..., min_length=8),
    current_user = Depends(get_current_user),
    # db: Session = Depends(get_db)  # Add database dependency
):
    """
    Change password for authenticated user
    """
    try:
        # Verify current password
        # user = await get_user_by_username(db, current_user.username)
        # if not verify_password(current_password, user.hashed_password):
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="Current password is incorrect"
        #     )
        
        # Update password
        # user.hashed_password = get_password_hash(new_password)
        # db.commit()
        
        return {"message": "Password changed successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to change password: {str(e)}"
        )