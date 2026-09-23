# from fastapi import FastAPI, APIRouter, Depends, HTTPException
# from pydantic import BaseModel
# from models import User
# from datetime import timedelta, datetime, timezone
# from fastapi.responses import JSONResponse
# from passlib.context import CryptContext
# from sqlalchemy.orm import Session
# from typing import Annotated
# from database import engine, sessionLocal
# from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
# from jose import jwt, JWTError

# router = APIRouter()


# bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
# OAuth2_bearer = OAuth2PasswordBearer(tokenUrl="login")

# SECRET_KEY = '5b70dc4b0006fdf65224e06aa2edb30c4f00b02ea1e85dc48ee4ea2997edf4ac'
# ALGORITHM = 'HS256'

# class CreateUser(BaseModel):
#     email : str
#     username : str
#     firstname : str
#     lastname : str
#     password : str
#     role : str

# def authenticated_user(username, password, db):
#     user = db.query(User).filter(User.username == user).first()

#     if user is None:
#         return False

#     if bcrypt_context.verify(password, user.hash_pasword):
#         return user
#     return False


# def create_access_token(username : str, user_id : int, role : str, expires_delta : timedelta):

#     encode = {'sub' : username, 'id' : user_id, 'role' : role}
#     expires = datetime.now(timezone.utc) + expires_delta
#     encode.update({'exp' : expires})
#     return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


# def get_curretn_user(token : Annotated[str, Depends(OAuth2_bearer)]):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username : str = payload.get('sub')
#         user_id : int = payload.get('id')
#         role : str = payload.get('role')

#         if username is None or user_id is None:
#             raise HTTPException(status_code=404, detail="User not found")
#         return {'username' : username, 'id' : user_id, 'role' : role}
#     except:
#         raise HTTPException(status_code=404, detail="User not found")


# def get_db():
#     db = sessionLocal()

#     try:
#         yield db
#     finally:
#         db.close()

# db_dependency = Annotated[Session, Depends(get_db)]

# @router.post("/create")
# def create_users(db : db_dependency, new_user : CreateUser):

#     user_model = User(
#         emai = new_user.email,
#         username = new_user.username,
#         fastname = new_user.firstname,
#         lastname = new_user.lastname,
#         hash_password = bcrypt_context.hash(new_user.password),
#         is_active = True,
#         role = new_user.role
#     )

#     db.add(user_model)
#     db.commit()

#     return JSONResponse(status_code=201, content={'massage' : 'User create successfully'})

# @router.post('login')
# def login_user(db : db_dependency, from_data : Annotated[OAuth2PasswordRequestForm, Depends()]):

#     user = authenticated_user(from_data.username, from_data.password, db)

#     if not user:
#         return "Faield Authenticated"

#     token = create_access_token(user.username, user.id, user.role, timedelta(minutes=30))
#     return {'access_token' : token, 'token_type' : 'bearer'}


from fastapi import FastAPI, APIRouter, Depends, HTTPException
from pydantic import BaseModel
from models import User
from datetime import timedelta, datetime, timezone
from fastapi.responses import JSONResponse
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from typing import Annotated
from database import engine, sessionLocal
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from router.auth import get_current_user
from models import Todos


router = APIRouter()

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get('/admin/todo')
def read_all(user : user_dependency, db : db_dependency):

    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=404, detail="Failed Authenticated!")

    return db.query(Todos).all()


@router.delete('/admin/delete/{todo_id}')
def delete_todos_by_admin(user : user_dependency, db : db_dependency, todo_id : int):


    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=404, detail="Faield Authenticated")

    todo = db.query(Todos).filter(Todos.id == todo_id).first()

    if todo is None:
        raise HTTPException(status_code=404, detail="Todo Not Found!")

    db.query(Todos).filter(Todos.id == todo_id).delete()

    db.commit()
    return JSONResponse(status_code=200, content={'massage' : "Todo delete successfully"})