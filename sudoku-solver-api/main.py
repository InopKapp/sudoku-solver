from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from typing import Optional, List, Annotated
from fastapi.middleware.cors import CORSMiddleware
from solver import solve_board, is_board_valid, find_invalid_cells
from ocr.pipeline import run_ocr_pipeline
import shutil
import os
import uuid

# strong validation: each row is exactly 9 ints between 0 and 9

Row = Annotated[list[int], Field(min_length=9, max_length=9)]
Grid = Annotated[list[Row], Field(min_length=9, max_length=9)]

class Puzzle(BaseModel):
    board: Grid

class Solution(BaseModel):
    solved: bool
    board: Optional[List[List[int]]] = None

class ValidationResult(BaseModel):
    valid: bool
    invalid_cells: List[List[int]]

app = FastAPI(title="Sudoku Solver API", version="0.1")

# CORS - allow all for development (change in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"ok": True, "message": "Sudoku Solver API running"}

@app.post("/solve", response_model=Solution)
async def solve(puzzle: Puzzle):
    board = [list(row) for row in puzzle.board]
    if not is_board_valid(board):
        raise HTTPException(status_code=400, detail="Invalid initial board (duplicate numbers)")
    solved = solve_board(board)
    if solved is None:
        return {"solved": False, "board": None}
    return {"solved": True, "board": solved}

@app.post("/validate", response_model=ValidationResult)
async def validate(puzzle: Puzzle):
    board = [list(row) for row in puzzle.board]

    invalid = find_invalid_cells(board)

    return {
        "valid": len(invalid) == 0,
        "invalid_cells": invalid
    }

@app.post("/ocr")
async def ocr_sudoku(image: UploadFile = File(...), debug: bool = True):
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type")

    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)

    temp_filename = f"{uuid.uuid4()}.png"
    temp_path = os.path.join(temp_dir, temp_filename)

    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        board = run_ocr_pipeline(temp_path, debug=debug)

        return {
            "board": board
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        print("OCR ERROR:", repr(e))
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)