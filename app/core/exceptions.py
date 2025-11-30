from fastapi import HTTPException, status

def bad_request(msg: str):
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

def unauthorized(msg: str = "Unauthorized"):
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)

def not_found(msg: str = "Not found"):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)

