# File: sudoku_csp.py
import time
from collections import deque
import random


class SudokuCSP:
    def __init__(self):
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.domains = [[[] for _ in range(9)] for _ in range(9)]
        self.arc_consistency_tree = []
        self.iterations = 0
        self.arc_revisions = 0
        
    def initialize_domains(self, board):
        for i in range(9):
            for j in range(9):
                if board[i][j] != 0:
                    self.domains[i][j] = [board[i][j]]
                else:
                    self.domains[i][j] = list(range(1, 10))
    
    def get_all_arcs(self):
        arcs = []
        
        # Row constraints - each pair of cells in same row
        for i in range(9):   #row
            for j in range(9):
                for k in range(9):
                    if j != k:
                        arcs.append(((i, j), (i, k)))
        
        # Column constraints - each pair of cells in same column
        for j in range(9):
            for i in range(9):
                for k in range(9):
                    if i != k:
                        arcs.append(((i, j), (k, j)))
        
        # 3x3 box constraints - each pair of cells in same box
        for box_row in range(0, 9, 3):
            for box_col in range(0, 9, 3):
                cells = []
                for i in range(box_row, box_row + 3):
                    for j in range(box_col, box_col + 3):
                        cells.append((i, j))
                
                # Create arcs between all pairs in the box
                for i in range(len(cells)):
                    for j in range(len(cells)):
                        if i != j:
                            arcs.append((cells[i], cells[j]))
        
        return arcs
    
    def revise(self, xi, xj):
        revised = False
        i1, j1 = xi
        i2, j2 = xj

        before = self.domains[i1][j1][:]
        
        values_to_remove = []
        for value in self.domains[i1][j1]:
            # Check if there exists a consistent value in domain of Xj
            # (a value that doesn't conflict with current value)
            has_consistent_value = False
            for other_value in self.domains[i2][j2]:
                if value != other_value:
                    has_consistent_value = True
                    break
            
            # If no consistent value found, remove this value
            if not has_consistent_value and len(self.domains[i2][j2]) > 0:
                values_to_remove.append(value)
                revised = True
        
        # Remove all inconsistent values
        for value in values_to_remove:
            self.domains[i1][j1].remove(value)

        after = self.domains[i1][j1][:]    

        if before != after:
            self.arc_consistency_tree.append({
                "arc": (xi, xj),
                "before": before,
                "after": after
            }) 
        
        return revised
    
    def ac3(self):
        
        # Initialize queue with all arcs
        queue = deque(self.get_all_arcs())
        self.arc_revisions = 0
        
        while queue:
            xi, xj = queue.popleft()
            self.arc_revisions += 1
            
            # If Xi's domain was revised
            if self.revise(xi, xj):
                i, j = xi
                
                # If domain becomes empty, puzzle is unsolvable
                if len(self.domains[i][j]) == 0:
                    return False
                
                # Add all arcs (Xk, Xi) to queue where Xk is neighbor of Xi (except Xj)
                neighbors = self.get_neighbors(xi)
                for xk in neighbors:
                    if xk != xj:
                        queue.append((xk, xi))
        
        return True
    
    def get_neighbors(self, cell):
        """
        Get all neighboring cells (cells in same row, column, or 3x3 box)
        
        Args:
            cell: Tuple (row, col)
            
        Returns:
            List of neighbor cell coordinates
        """
        i, j = cell
        neighbors = []
        
        # Row neighbors
        for col in range(9):
            if col != j:
                neighbors.append((i, col))
        
        # Column neighbors
        for row in range(9):
            if row != i:
                neighbors.append((row, j))
        
        # 3x3 box neighbors
        box_row, box_col = 3 * (i // 3), 3 * (j // 3)
        for row in range(box_row, box_row + 3):
            for col in range(box_col, box_col + 3):
                if (row, col) != (i, j) and (row, col) not in neighbors:
                    neighbors.append((row, col))
        
        return neighbors
    
    def is_valid(self, board, row, col, num):
        """
        Check if placing num at (row, col) is valid according to Sudoku rules
        
        Args:
            board: Current board state
            row: Row index
            col: Column index
            num: Number to place
            
        Returns:
            True if placement is valid, False otherwise
        """
        # Check row constraint
        if num in board[row]:
            return False
        
        # Check column constraint
        for i in range(9):
            if board[i][col] == num:
                return False
        
        # Check 3x3 box constraint
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if board[i][j] == num:
                    return False
        
        return True
    
    def backtrack_solve(self, board):
        self.iterations += 1
        
        # Find next empty cell using MRV heuristic
        empty_cell = self.find_empty_cell(board)
        if not empty_cell:
            return True  
        
        row, col = empty_cell
        
        # Try values from domain (prioritized by AC-3) or all values 1-9
        possible_values = self.domains[row][col] if len(self.domains[row][col]) > 0 else range(1, 10)
        
        for num in possible_values:
            if self.is_valid(board, row, col, num):
                # Make assignment
                board[row][col] = num
                
                # Recursively solve
                if self.backtrack_solve(board):
                    return True
                
                # Backtrack if solution not found
                board[row][col] = 0
        
        return False
    
    def find_empty_cell(self, board):
        """
        Find next empty cell using Minimum Remaining Values (MRV) heuristic
        Selects cell with smallest domain (most constrained)
        
        Args:
            board: Current board state
            
        Returns:
            Tuple (row, col) of best empty cell, or None if board is full
        """
        min_domain_size = 10
        best_cell = None
        
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    domain_size = len(self.domains[i][j])
                    if domain_size < min_domain_size:
                        min_domain_size = domain_size
                        best_cell = (i, j)
        
        return best_cell
    
    def solve_with_ac3(self, board):
        self.board = [row[:] for row in board]  # Deep copy
        self.iterations = 0
        self.arc_revisions = 0
        
        start_time = time.time()
        
        # Step 1: Initialize domains based on current board
        self.initialize_domains(self.board)
        
        # Step 2: Apply AC-3 to reduce domains
        if not self.ac3():
            return None, 0  # Unsolvable - empty domain found
        
        # Step 3: Update board with singleton domains
        self.apply_singleton_domains()
        
        # Step 4: Use backtracking for remaining cells (specially appear in hard generated puzzle)
        if self.backtrack_solve(self.board):
            solve_time = time.time() - start_time
            return self.board, solve_time
        
        return None, 0  # No solution found
    
    def apply_singleton_domains(self):
        """
        Apply values from singleton domains (domains with only one value) to the board
        This is done after AC-3 to fill in determined cells
        """
        for i in range(9):
            for j in range(9):
                if len(self.domains[i][j]) == 1 and self.board[i][j] == 0:
                    self.board[i][j] = self.domains[i][j][0]
    
    def generate_puzzle(self, difficulty='medium'):
        
        # Start with empty board
        board = [[0 for _ in range(9)] for _ in range(9)]
        
        # Fill diagonal 3x3 boxes (they don't interfere with each other)
        for box in range(0, 9, 3):
            nums = list(range(1, 10))
            random.shuffle(nums)
            idx = 0
            for i in range(box, box + 3):
                for j in range(box, box + 3):
                    board[i][j] = nums[idx]
                    idx += 1
        
        # Solve the board using backtrack to get a complete valid solution
        temp_solver = SudokuCSP()
        # solved_board, _ = temp_solver.solve_with_ac3(board)
        
        # if solved_board is None:
        #     # If failed, try again
        #     return self.generate_puzzle(difficulty)

        solved = temp_solver.backtrack_solve(board)
        if not solved :
          return self.generate_puzzle(difficulty)
        # Remove numbers based on difficulty level
        cells_to_remove = {
            'easy': 30,      # Remove 30 cells 
            'medium': 40,    # Remove 40 cells 
            'hard': 50       # Remove 50 cells 
        }
        remove_count = cells_to_remove.get(difficulty, 40)
        
        # Create puzzle by removing cells
        puzzle = [row[:] for row in board]
        cells = [(i, j) for i in range(9) for j in range(9)]
        random.shuffle(cells)
        
        for i, j in cells[:remove_count]:
            puzzle[i][j] = 0
        
        return puzzle
    
    def validate_board(self, board):
        """
        Validate if the board follows Sudoku constraints
        
        Args:
            board: 9x9 2D list
            
        Returns:
            Tuple (is_valid, error_message)
        """
        # Check rows
        for i in range(9):
            nums = [board[i][j] for j in range(9) if board[i][j] != 0]
            if len(nums) != len(set(nums)):
                return False, f"Row {i+1} has duplicate numbers"
        
        # Check columns
        for j in range(9):
            nums = [board[i][j] for i in range(9) if board[i][j] != 0]
            if len(nums) != len(set(nums)):
                return False, f"Column {j+1} has duplicate numbers"
        
        # Check 3x3 boxes
        for box_row in range(0, 9, 3):
            for box_col in range(0, 9, 3):
                nums = []
                for i in range(box_row, box_row + 3):
                    for j in range(box_col, box_col + 3):
                        if board[i][j] != 0:
                            nums.append(board[i][j])
                if len(nums) != len(set(nums)):
                    return False, f"Box at ({box_row//3 + 1},{box_col//3 + 1}) has duplicate numbers"
        
        return True, "Board is valid"
    
    def get_statistics(self):
        """
        Get solving statistics
        
        Returns:
            Dictionary with statistics
        """
        return {
            'iterations': self.iterations,
            'arc_revisions': self.arc_revisions,
            'domains': self.domains
        }
    
    def print_ac3_tree(self):
        print("\n=== ARC CONSISTENCY TREE ===")
        for step_num, log in enumerate(self.arc_consistency_tree, 1):
            if "arc" in log:
                xi, xj = log["arc"]
                print(f"\nStep {step_num}: Revising {xi} → {xj}")
                print(f"  Before: {log['before']}")
                print(f"  After:  {log['after']}")

            elif "checking" in log:
                xi, xj = log["checking"]
                print(f"\nChecking arc {xi} → {xj}")
                print(f"  Domain Xi: {log['domain_xi']}")
                print(f"  Domain Xj: {log['domain_xj']}")