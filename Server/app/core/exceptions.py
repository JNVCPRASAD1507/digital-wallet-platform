from fastapi.responses import JSONResponse


class DomainError(Exception):
    def __init__(self, code: str, message: str, status: int = 400):
        self.code = code
        self.message = message
        self.status = status
        super().__init__(code, message, status)


async def handler(request, exc: DomainError):
    return JSONResponse(
        status_code=exc.status,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
            },
        },
    )
