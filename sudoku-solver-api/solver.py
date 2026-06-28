from typing import List, Optional, Tuple, Set
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
    # check row and column
    for x in range(N):
        if board[row][x] == num or board[x][col] == num:
            return False
    # check 3x3 box
    start_row, start_col = row - row % 3, col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def get_candidates(board: List[List[int]], r: int, c: int) -> Set[int]:
    if board[r][c] != 0:
        return set()
    used = set()
    # row and col
    for i in range(9):
        used.add(board[r][i])
        used.add(board[i][c])
    # 3x3 Box
    br, bc = r - r % 3, c - c % 3
    for i in range(3):
        for j in range(3):
            used.add(board[br + i][bc + j])
            
    return set(range(1, 10)) - used

def solve_sudoku_mrv(board: List[List[int]]) -> bool:
    # find the empty cell with the fewest possible candidates, min remaining val (MRV)
    min_candidates = 10
    best_cell = None
    best_options = None
    
    for r in range(N):
        for c in range(N):
            if board[r][c] == 0:
                options = get_candidates(board, r, c)
                if len(options) == 0:
                    return False # dead end
                if len(options) < min_candidates:
                    min_candidates = len(options)
                    best_cell = (r, c)
                    best_options = options
                    
    # if no empty cell found, it's solved
    if best_cell is None:
        return True
        
    r, c = best_cell
    for num in best_options:
        board[r][c] = num
        if solve_sudoku_mrv(board):
            return True
        board[r][c] = 0
            
    return False

def solve_sudoku(board: List[List[int]]) -> bool:
    return solve_sudoku_mrv(board)

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
