from fastapi import HTTPException, status


class AuthException(HTTPException):
    def __init__(self, detail: str = "Ошибка авторизации"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)
