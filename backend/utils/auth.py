from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from ..config import settings
from ..database.neo4j_client import Neo4jClient

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()
db_client = Neo4jClient()

class Auth:
    def __init__(self):
        self.secret = settings.SECRET_KEY

    def encode_token(self, user_id: str) -> str:
        """Generate JWT token."""
        payload = {
            'exp': datetime.utcnow() + timedelta(days=1),
            'iat': datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(
            payload,
            self.secret,
            algorithm='HS256'
        )

    def decode_token(self, token: str) -> str:
        """Decode JWT token."""
        try:
            payload = jwt.decode(token, self.secret, algorithms=['HS256'])
            return payload['sub']
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Token has expired')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Invalid token')

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password."""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash password."""
        return pwd_context.hash(password)

    async def authenticate_user(self, username: str, password: str) -> Optional[str]:
        """Authenticate user and return user_id if valid."""
        user = db_client.get_user_by_username(username)
        if not user:
            return None
        if not self.verify_password(password, user['hashed_password']):
            return None
        return user['id']

    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
        """Get current user from JWT token."""
        token = credentials.credentials
        user_id = self.decode_token(token)
        if not db_client.user_exists(user_id):
            raise HTTPException(
                status_code=401,
                detail='Invalid user'
            )
        return user_id
