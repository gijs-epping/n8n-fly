from fastapi import FastAPI, HTTPException
from flask import Flask
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict
import uvicorn
import re
import os
import sqlite3





from src.api_functions import (
    handle_get_recent_orders,
    handle_get_order_info,
    handle_get_debtor_orders,
    handle_get_delivery_time_order,
    handle_get_delivery_time_product
)


app = Flask(__name__)

class FunctionRequest(BaseModel):
    function: str
    params: List[Dict[str, str]]

class QueryRequest(BaseModel):
    query: str

def is_safe_query(query: str) -> bool:
    # Check for dangerous SQL operations
    dangerous_patterns = [
        r'\bDROP\b',
        r'\bDELETE\b',
        r'\bUPDATE\b',
        r'\bINSERT\b',
        r'\bALTER\b',
        r'\bCREATE\b',
        r'\bTRUNCATE\b',
        r'\bREPLACE\b',
        r';.*',  # Prevent multiple statements
        r'--',   # Prevent comments
        r'/\*'   # Prevent block comments
    ]
    
    query = query.upper()
    return not any(re.search(pattern, query, re.IGNORECASE) for pattern in dangerous_patterns)

def get_db_connection():
    return sqlite3.connect('database/backorders.db')

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": str(exc)
        }
    )

@app.get("/")
async def root():
    return JSONResponse(
        content={
            "status": "success",
            "message": "Python API server is running"
        }
    )

@app.post("/api/query")
async def execute_query(request: QueryRequest):
    if not request.query:
        raise HTTPException(status_code=400, detail="Query is required")
    
    if not is_safe_query(request.query):
        raise HTTPException(status_code=400, detail="Invalid or unsafe query")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(request.query)
        
        # Get column names from cursor description
        columns = [description[0] for description in cursor.description]
        
        # Convert rows to list of dictionaries
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return JSONResponse(content={
            "status": "success",
            "data": results
        })
    except sqlite3.Error as e:
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

@app.post("/api/function")
async def execute_function(request: FunctionRequest):
    try:
        handlers = {
            "get_recent_orders": handle_get_recent_orders,
            "get_order_info": handle_get_order_info,
            "get_debtor_orders": handle_get_debtor_orders,
            "get_delivery_time_order": handle_get_delivery_time_order,
            "get_delivery_time_product": handle_get_delivery_time_product
        }
        
        handler = handlers.get(request.function)
        if handler:
            return JSONResponse(content=handler(request.params))
        else:
            raise HTTPException(status_code=400, detail=f"Unknown function: {request.function}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)





