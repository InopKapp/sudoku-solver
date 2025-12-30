from typing import List, Optional
import copy

N = 9

def find_invalid_cells(board):
    invalid = set()

    def check_unit(cells):
        seen = {}
        for r, c in cells:
            val = board[r][c]
            if val == 0:
                continue
            if val in seen:
                invalid.add((r, c))
                invalid.add(seen[val])
            else:
                seen[val] = (r, c)

    # rows
    for r in range(9):
        check_unit([(r, c) for c in range(9)])

    # columns
    for c in range(9):
        check_unit([(r, c) for r in range(9)])

    # 3x3 boxes
    for br in range(0, 9, 3):
        for bc in range(0, 9, 3):
            check_unit([
                (r, c)
                for r in range(br, br + 3)
                for c in range(bc, bc + 3)
            ])

    return [[r, c] for r, c in invalid]

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
