from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Optional

app = FastAPI(
    title="Book Management API",
    description="A simple CRUD API built with FastAPI",
    version="1.0.0"
)

# 1. Data Schema (Pydantic Model for request validation)
class Book(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, example="The Hobbit")
    author: str = Field(..., min_length=1, max_length=50, example="J.R.R. Tolkien")
    pages: int = Field(..., gt=0, example=295)
    published_year: Optional[int] = Field(None, example=1937)

class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    author: Optional[str] = Field(None, min_length=1, max_length=50)
    pages: Optional[int] = Field(None, gt=0)
    published_year: Optional[int] = Field(None)

# 2. In-Memory Database Simulation
# Using a dictionary where the key is the book_id (int) and the value is a dict of book data
db: Dict[int, dict] = {}
id_counter = 1


# ==================== CRUD ENDPOINTS ====================

# CREATE: Add a new book
@app.post(
    "/books/", 
    status_code=status.HTTP_201_CREATED, 
    response_model=dict,
    summary="Create a new book"
)
def create_book(book: Book):
    global id_counter
    
    # Optional: Logic check to prevent duplicate titles if needed
    for existing_book in db.values():
        if existing_book["title"].lower() == book.title.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A book with this title already exists."
            )
            
    new_book = book.model_dump() # Converts Pydantic model to Python dict
    new_book["id"] = id_counter
    db[id_counter] = new_book
    
    id_counter += 1
    return {"message": "Book created successfully", "data": new_book}


# READ: Get all books or a specific book by ID
@app.get(
    "/books/", 
    status_code=status.HTTP_200_OK, 
    summary="Get all books"
)
def get_all_books():
    return {"data": list(db.values())}


@app.get(
    "/books/{book_id}", 
    status_code=status.HTTP_200_OK, 
    summary="Get a book by ID"
)
def get_book_by_id(book_id: int):
    if book_id not in db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found."
        )
    return {"data": db[book_id]}


# UPDATE: Modify an existing book partially or fully
@app.put(
    "/books/{book_id}", 
    status_code=status.HTTP_200_OK, 
    summary="Update an existing book"
)
def update_book(book_id: int, book_update: BookUpdate):
    if book_id not in db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} cannot be updated because it does not exist."
        )
        
    stored_book_data = db[book_id]
    
    # Filter out fields that weren't explicitly provided in the request body
    update_data = book_update.model_dump(exclude_unset=True)
    
    # If the user sent an empty body, raise an error
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid fields provided for update."
        )
        
    # Merge old data with new updates
    updated_book = {**stored_book_data, **update_data}
    db[book_id] = updated_book
    
    return {"message": "Book updated successfully", "data": updated_book}


# DELETE: Remove a book by ID
@app.delete(
    "/books/{book_id}", 
    status_code=status.HTTP_200_OK, # Or 240 No Content, but 200 lets us return a message
    summary="Delete a book"
)
def delete_book(book_id: int):
    if book_id not in db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} cannot be deleted because it does not exist."
        )
        
    deleted_book = db.pop(book_id)
    return {"message": f"Book '{deleted_book['title']}' has been deleted successfully."}