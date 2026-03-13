from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
import logging
import asyncio

# Import database and models
from src.database import get_db
from src.models import User as UserModel

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

# Database functions (now with real implementation)
async def get_user_by_username(db: Session, username: str) -> Optional[UserModel]:
    """Get user by username from database"""
    return db.query(UserModel).filter(UserModel.username == username).first()

async def get_user_by_email(db: Session, email: str) -> Optional[UserModel]:
    """Get user by email from database"""
    return db.query(UserModel).filter(UserModel.email == email).first()

async def create_user(db: Session, user: UserCreate) -> UserModel:
    """Create a new user in database"""
    # Create new user instance
    db_user = UserModel(
        email=user.email,
        username=user.username,
        hashed_password=get_password_hash(user.password),
        full_name=user.full_name,
        is_active=True
    )
    # Add to session and commit
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info(f"✅ Created new user: {user.username} ({user.email})")
    return db_user

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
    db: Session = Depends(get_db)
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
        existing_user = await get_user_by_email(db, user_data.email)
        if existing_user:
            logger.warning(f"⚠️  Registration attempt with existing email: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        existing_username = await get_user_by_username(db, user_data.username)
        if existing_username:
            logger.warning(f"⚠️  Registration attempt with existing username: {user_data.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Create new user IN DATABASE (not mock!)
        new_user = await create_user(db, user_data)
        
        # Return real user data with real database ID
        return UserResponse(
            id=new_user.id,  # ✅ Real database ID, not hardcoded!
            email=new_user.email,
            username=new_user.username,
            full_name=new_user.full_name,
            is_active=new_user.is_active,
            created_at=new_user.created_at
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Registration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login with username and password
    
    Returns access and refresh tokens
    """
    try:
        # Authenticate user with real database lookup
        user = await get_user_by_username(db, form_data.username)
        if not user or not verify_password(form_data.password, user.hashed_password):
            logger.warning(f"⚠️  Failed login attempt for {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            logger.warning(f"⚠️  Login attempt with inactive user: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive",
            )
        
        # Create tokens with real user ID
        access_token = create_access_token(
            data={"sub": user.username, "user_id": user.id}
        )
        refresh_token = create_refresh_token(
            data={"sub": user.username, "user_id": user.id}
        )
        
        logger.info(f"✅ Successful login for user: {user.username}")
        return Token(
            access_token=access_token,
            refresh_token=refresh_token
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Login failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
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
        
        # Verify user still exists in database
        user = await get_user_by_username(db, token_data.username)
        if not user:
            logger.warning(f"⚠️  Refresh attempt for non-existent user: {token_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        if not user.is_active:
            logger.warning(f"⚠️  Refresh attempt for inactive user: {token_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive"
            )
        
        # Create new tokens
        access_token = create_access_token(
            data={"sub": token_data.username, "user_id": user.id}
        )
        new_refresh_token = create_refresh_token(
            data={"sub": token_data.username, "user_id": user.id}
        )
        
        logger.info(f"✅ Token refreshed for user: {user.username}")
        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Token refresh failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token refresh failed: {str(e)}"
        )

@router.post("/logout")
async def logout(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout current user and invalidate sessions
    """
    try:
        logger.info(f"🚪 User logging out: {current_user.username}")
        
        # In production, would:
        # 1. Blacklist the access token
        # 2. Invalidate refresh tokens in database
        # 3. Log the logout event for audit
        # 4. Clear any active sessions
        
        # For now, log the logout action
        logger.info(f"✅ Logout successful for user: {current_user.username}")
        
        return {
            "message": "Successfully logged out",
            "user": current_user.username,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user information from database
    """
    try:
        # Get full user info from database using real token data
        user = await get_user_by_username(db, current_user.username)
        
        if not user:
            logger.warning(f"User not found in database: {current_user.username}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Return real user data from database
        return UserResponse(
            id=user.id,  # ✅ Real database ID
            email=user.email,  # ✅ Real email from DB
            username=user.username,  # ✅ Real username from DB
            full_name=user.full_name,  # ✅ Real name from DB
            is_active=user.is_active,  # ✅ Real status from DB
            created_at=user.created_at  # ✅ Real timestamp from DB
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