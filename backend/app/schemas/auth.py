from pydantic import BaseModel, EmailStr

class Login(BaseModel):
    email: EmailStr
    password: str

class Msg(BaseModel):
    msg: str

class TokenRefresh(BaseModel):
    refresh_token: str

class ResetPassword(BaseModel):
    token: str
    new_password: str

class ForgotPassword(BaseModel):
    email: EmailStr
class ZoomOAuthCallback(BaseModel):
    code: str
    state: str | None = None
class GoogleOAuthCallback(BaseModel):
    code: str
    state: str | None = None
