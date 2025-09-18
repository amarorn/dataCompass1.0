"""
Authentication Service
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt

from ..entities.user import User


class AuthService:
    """Service for authentication and authorization"""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def hash_password(self, password: str) -> str:
        """Hash a password"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(
        self, 
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        
        return encoded_jwt
    
    def create_refresh_token(
        self, 
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT refresh token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None
    
    def verify_api_key(self, api_key: str, stored_key: str) -> bool:
        """Verify an API key"""
        return api_key == stored_key
    
    def generate_password_reset_token(self, user_id: str) -> str:
        """Generate a password reset token"""
        data = {
            "user_id": user_id,
            "type": "password_reset"
        }
        return self.create_access_token(data, expires_delta=timedelta(hours=1))
    
    def verify_password_reset_token(self, token: str) -> Optional[str]:
        """Verify a password reset token and return user_id"""
        payload = self.verify_token(token)
        
        if payload and payload.get("type") == "password_reset":
            return payload.get("user_id")
        
        return None
    
    def generate_email_verification_token(self, user_id: str, email: str) -> str:
        """Generate an email verification token"""
        data = {
            "user_id": user_id,
            "email": email,
            "type": "email_verification"
        }
        return self.create_access_token(data, expires_delta=timedelta(hours=24))
    
    def verify_email_verification_token(self, token: str) -> Optional[Dict[str, str]]:
        """Verify an email verification token"""
        payload = self.verify_token(token)
        
        if payload and payload.get("type") == "email_verification":
            return {
                "user_id": payload.get("user_id"),
                "email": payload.get("email")
            }
        
        return None
    
    def check_password_strength(self, password: str) -> Dict[str, Any]:
        """Check password strength and return requirements"""
        issues = []
        score = 0
        
        # Length check
        if len(password) >= 8:
            score += 25
        else:
            issues.append("Password must be at least 8 characters long")
        
        # Uppercase check
        if any(c.isupper() for c in password):
            score += 25
        else:
            issues.append("Password must contain at least one uppercase letter")
        
        # Lowercase check
        if any(c.islower() for c in password):
            score += 25
        else:
            issues.append("Password must contain at least one lowercase letter")
        
        # Number check
        if any(c.isdigit() for c in password):
            score += 25
        else:
            issues.append("Password must contain at least one number")
        
        # Special character check (bonus)
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if any(c in special_chars for c in password):
            score = min(100, score + 10)
        
        return {
            "score": score,
            "is_strong": score >= 75,
            "issues": issues
        }
    
    def generate_session_token(self, user: User) -> Dict[str, str]:
        """Generate session tokens for a user"""
        access_token_expires = timedelta(minutes=1440)  # 24 hours
        refresh_token_expires = timedelta(days=7)
        
        access_token = self.create_access_token(
            data={
                "sub": user.id,
                "username": user.username,
                "role": user.role.value,
                "permissions": user.permissions
            },
            expires_delta=access_token_expires
        )
        
        refresh_token = self.create_refresh_token(
            data={"sub": user.id},
            expires_delta=refresh_token_expires
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }