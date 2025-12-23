from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import decode_access_token
from app.db.database import get_db

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    cursor=Depends(get_db)
):
    """Dependency to get the current authenticated user"""
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: int = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch user from database
    cursor.execute(
        "SELECT user_id, type_id, name, mail_address FROM users WHERE user_id = %s",
        (user_id,)
    )
    user = cursor.fetchone()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return dict(user)


def require_role(required_auth_level: int):
    """Dependency to check if user has required authorization level"""
    def role_checker(current_user: dict = Depends(get_current_user), cursor=Depends(get_db)):
        # Get user's authorization level
        cursor.execute(
            """
            SELECT ut.authorization_level
            FROM users u
            JOIN user_type ut ON u.type_id = ut.user_type_id
            WHERE u.user_id = %s
            """,
            (current_user["user_id"],)
        )
        result = cursor.fetchone()

        if not result or result["authorization_level"] < required_auth_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )

        return current_user

    return role_checker
