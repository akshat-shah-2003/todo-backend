from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2 import OperationalError
from typing import List
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Todo List API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# PostgreSQL Database Configuration
db_config = {
    "host": "dpg-cvv3cqidbo4c73fdg650-a",
    "user": "postgresu",  # Your PostgreSQL username
    "password": "t9RROnumHTv4za5RPkmoHvMi7URB3FoO",  # Your PostgreSQL password
    "database": "todo_db_0naq"  # Your PostgreSQL database name
}

class Todo(BaseModel):
    id: int = None
    title: str
    completed: bool = False

def get_connection():
    try:
        # Create a connection to PostgreSQL
        connection = psycopg2.connect(**db_config)
        return connection
    except OperationalError as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return

@app.get("/todos", response_model=List[Todo])
def read_todos():
    connection = get_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM todos")
    todos = cursor.fetchall()
    cursor.close()
    connection.close()
    return [{"id": todo[0], "title": todo[1], "completed": todo[2]} for todo in todos]

@app.post("/todos", response_model=Todo)
def create_todo(todo: Todo):
    connection = get_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    cursor = connection.cursor()
    query = "INSERT INTO todos (title, completed) VALUES (%s, %s) RETURNING id"
    cursor.execute(query, (todo.title, todo.completed))
    todo.id = cursor.fetchone()[0]
    connection.commit()
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
    cursor.execute(query, (todo.title, todo.completed, todo_id))
    connection.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Todo not found")
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
    cursor.execute(query, (todo_id,))
    connection.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Todo not found")
    cursor.close()
    connection.close()
    return {"detail": "Todo deleted successfully"}
