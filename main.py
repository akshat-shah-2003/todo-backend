from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
from mysql.connector import Error
from typing import List
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Todo List API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "rootuser1",
    "database": "todo_db"
}

class Todo(BaseModel):
    id: int = None
    title: str
    completed: bool = False

def get_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return

@app.get("/todos",response_model=List[Todo])
def read_todos():
    connection = get_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM todos")
    todos = cursor.fetchall()
    cursor.close()
    connection.close()
    return todos

@app.post("/todos",response_model=Todo)
def create_todo(todo: Todo):
    connection = get_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    cursor = connection.cursor()
    query = "INSERT INTO todos (title, completed) VALUES (%s,%s)"
    cursor.execute(query,(todo.title,todo.completed))
    connection.commit()
    todo.id = cursor.lastrowid
    cursor.close()
    connection.close()
    return todo

@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, todo: Todo):
    connection = get_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    cursor = connection.cursor()
    query = "UPDATE todos SET title = %s, completed = %s WHERE id = %s"
    cursor.execute(query,(todo.title,todo.completed,todo_id))
    connection.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail = "Todo not found")
    cursor.close()
    connection.close()
    todo.id = todo_id
    return todo

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    connection = get_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    cursor = connection.cursor()
    query = "DELETE FROM todos WHERE id = %s"
    cursor.execute(query,(todo_id,))
    connection.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail = "Todo not found")
    cursor.close()
    connection.close()
    return {"detail": "Todo deleted successfully"}

