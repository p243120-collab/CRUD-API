


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# Your mock database (a list of strings)
tasks = ["Buy groceries", "Clean the room", "Study FastAPI"]

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

@app.get("/")
def read_root():
    return tasks

def put_task(tasks_id: int, updated_text: str):
    if tasks_id < 0 or tasks_id >= len(tasks):
        raise HTTPException(status_code=404, detail="Task ID not found")
    if tasks.title is None and tasks.done is None:        
     raise HTTPException(status_code=400, detail="Empty body")
      
    tasks[tasks_id] = updated_text
    return {"message": "Task updated successfully", "updated_tasks": tasks} 

@app.post("/tasks")
# FIX: Cleaned up parameters and variables to match your string list
def create_new(task_title: str):
    if not task_title.strip():        
        raise HTTPException(status_code=400, detail="The 'title' field cannot be empty.")
    
    tasks.append(task_title)
    return {"message": "Created", "tasks": tasks}

@app.put("/tasks/{tasks_id}")
# Pass individual fields as arguments with default values
def put_task(tasks_id: int, title: Optional[str] = None, done: Optional[bool] = None):
    if tasks_id < 0 or tasks_id >= len(tasks):
        raise HTTPException(status_code=404, detail="Task ID not found")
        
    # Check if both fields were left blank in Swagger
    if title is None and done is None:        
        raise HTTPException(status_code=400, detail="Empty parameters")
      
    # Update the text if a title was provided
    if title:
        tasks[tasks_id] = title
        
    return {"message": "Task updated successfully", "updated_tasks": tasks}

@app.get("/tasks/{tasks_id}")
def get_item(tasks_id: int) -> str:
    if tasks_id < 0 or tasks_id >= len(tasks):
        raise HTTPException(status_code=404, detail="ID not found")
    
    return tasks[tasks_id]

@app.delete("/tasks/{tasks_id}") 
def delete_task(tasks_id: int):
    if tasks_id < 0 or tasks_id >= len(tasks):
        raise HTTPException(status_code=404, detail="Task ID not found")
       
    removed_item = tasks.pop(tasks_id)
    return {"message": f"Deleted task: '{removed_item}'", "remaining_tasks": tasks}
