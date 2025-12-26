from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Annotated
from fastapi.middleware.cors import CORSMiddleware

# strong validation: each row is exactly 9 ints between 0 and 9

Row = Annotated[list[int], Field(min_length=9, max_length=9)]
Grid = Annotated[list[Row], Field(min_length=9, max_length=9)]

class Puzzle(BaseModel):
    board: Grid

class Solution(BaseModel):
    solved: bool
    board: Optional[List[List[int]]] = None

app = FastAPI(title="Sudoku Solver API", version="0.1")

# CORS - allow all for development (change in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from solver import solve_board, is_board_valid

@app.get("/")
def root():
    return {"ok": True, "message": "Sudoku Solver API running"}

@app.post("/solve", response_model=Solution)
async def solve(puzzle: Puzzle):
    board = [list(row) for row in puzzle.board]  # ensure regular lists
    # Extra sanity check (should already be validated by Pydantic types)
    if not is_board_valid(board):
        raise HTTPException(status_code=400, detail="Invalid initial board (duplicate numbers)")
    solved = solve_board(board)
    if solved is None:
        return {"solved": False, "board": None}
    return {"solved": True, "board": solved}
