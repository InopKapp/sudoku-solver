from typing import List, Optional
import copy

N = 9

def is_valid(board: List[List[int]], row: int, col: int, num: int) -> bool:
    for x in range(N):
        if board[row][x] == num or board[x][col] == num:
            return False
    start_row, start_col = row - row % 3, col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def solve_sudoku(board: List[List[int]]) -> bool:
    for row in range(N):
        for col in range(N):
            if board[row][col] == 0:
                for num in range(1, 10):
                    if is_valid(board, row, col, num):
                        board[row][col] = num
                        if solve_sudoku(board):
                            return True
                        board[row][col] = 0
                return False
    return True

def is_board_valid(board: List[List[int]]) -> bool:
    for i in range(N):
        for j in range(N):
            num = board[i][j]
            if num != 0:
                # temporarily remove and check
                board[i][j] = 0
                if not is_valid(board, i, j, num):
                    board[i][j] = num
                    return False
                board[i][j] = num
    return True

def solve_board(board: List[List[int]]) -> Optional[List[List[int]]]:
    b = [row.copy() for row in board]
    if not is_board_valid(b):
        return None
    if solve_sudoku(b):
        return b
    return None
