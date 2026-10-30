from fastapi import Request
from fastapi.responses import JSONResponse
class DomainError(Exception):
    def __init__(self,code,message,status=400):
        self.code=code; self.message=message; self.status=status
def handler(request:Request,exc:DomainError):
    return JSONResponse(exc.status,{"success":False,"error":{"code":exc.code,"message":exc.message}})
