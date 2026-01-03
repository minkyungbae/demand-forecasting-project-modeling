from fastapi import HTTPException, status

class NotFoundError(HTTPException):
    """리소스를 찾을 수 없을 때 발생하는 예외"""
    def __init__(self, detail: str = "리소스를 찾을 수 없습니다"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class ValidationError(HTTPException):
    """유효성 검증 실패 시 발생하는 예외"""
    def __init__(self, detail: str = "유효성 검증에 실패했습니다"):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)

class UnauthorizedError(HTTPException):
    """인증 실패 시 발생하는 예외"""
    def __init__(self, detail: str = "인증이 필요합니다"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

class ForbiddenError(HTTPException):
    """권한 없음 시 발생하는 예외"""
    def __init__(self, detail: str = "권한이 없습니다"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

