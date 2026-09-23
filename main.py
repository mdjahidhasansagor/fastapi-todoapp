from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import models 
from models import Todos, User
from typing import Annotated, Optional
from database import engine, sessionLocal
from fastapi.responses import JSONResponse
from typing import Optional
from router import auth, admin
from router.auth import get_current_user

app = FastAPI()

class Todo(BaseModel):
    id : int
    title : str
    description : str = Field(max_length=100)
    priority : int = Field(gt=0, lt=6)
    completed : bool

class TodoUpdate(BaseModel):
    title : Optional[str] = Field(default=None)
    description : Optional[str] = Field(default=None, max_length=100)
    priority : Optional[int] = Field(default=None, gt=0, lt=6)
    completed : Optional[bool] = Field(default=None)

models.Base.metadata.create_all(bind=engine)
app.include_router(auth.router)
app.include_router(admin.router)

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@app.get("/")
def read_todos(user : user_dependency, db : db_dependency):

    if user is None:
        raise HTTPException(status_code=404, detail='Faield Authenticated')

    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()


@app.get("/todo/{todo_id}")
def read_specfice_todos(user : user_dependency, db : db_dependency, todo_id : int):

    if user is None:
        raise HTTPException(status_code=404, detail='Faield Authenticated')
    
    spacific_todo = db.query(Todos).filter(Todos.owner_id == user.get('id')).filter(Todos.id == todo_id).first()

    if spacific_todo is not None:
        return spacific_todo
    else:
        raise HTTPException(status_code=404, detail="Todo Not Found!")


# Create

@app.post("/create/")
def create_todos(user : user_dependency, db : db_dependency, new_todo : Todo):

    if user is None:
        raise HTTPException(status_code=404, detail='Faield Authenticated')
    todo_model = Todos(**new_todo.model_dump(), owner_id = user.get('id'))
    db.add(todo_model)
    db.commit()

    return JSONResponse(status_code=201, content={'massage' : 'Todo create successfully!'})

# Update

@app.put("/edit/{todo_id}")
def update_todos(user : user_dependency, db : db_dependency, todo_id : int, update_todo : TodoUpdate):

    if user is None:
        raise HTTPException(status_code=404, detail='Faield Authenticated')

    todo = db.query(Todos).filter(Todos.owner_id == user.get('id')).filter(Todos.id == todo_id).first()

    if todo is None:
        raise HTTPException(status_code=404, detail="Todo Not Found!")

    update_data = update_todo.model_dump(exclude_unset=True)

    for key,value in update_data.items():
        setattr(todo,key,value)

    db.commit()

    return JSONResponse(status_code=200, content={'message': 'Todo Update successfully!'})

# Delete

@app.delete("/delete/{todo_id}")
def delete_todos(user : user_dependency, db : db_dependency, todo_id : int):

    if user is None:
        raise HTTPException(status_code=404, detail='Faield Authenticated')

    todo = db.query(Todos).filter(Todos.owner_id == user.get('id')).filter(Todos.id == todo_id).first()

    if todo is None:
        raise HTTPException(status_code=404, detail="Todo Not found!")

    db.query(Todos).filter(Todos.owner_id == user.get('id')).filter(Todos.id == todo_id).delete()

    db.commit()
    return JSONResponse(status_code=200, content={'massage' : 'Todo delete successfully!'})


@app.get('/user')
def get_user(user : user_dependency, db : db_dependency):

    if user is None:
        raise HTTPException(status_code=401, detail="Failed Authenticated")

    return db.query(User).filter(User.id == user.get('id')).first()