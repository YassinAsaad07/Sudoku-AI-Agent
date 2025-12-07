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
        arcs = set()
        
        # Row constraints
        for i in range(9):   
            for j in range(9):
                for k in range(9):
                    if j != k:
                        arcs.add(((i, j), (i, k)))
        
        # Column constraints
        for j in range(9):
            for i in range(9):
                for k in range(9):
                    if i != k:
                        arcs.add(((i, j), (k, j)))
        
        # 3x3 box constraints
        for box_row in range(0, 9, 3):
            for box_col in range(0, 9, 3):
                cells = []
                for i in range(box_row, box_row + 3):
                    for j in range(box_col, box_col + 3):
                        cells.append((i, j))
                
                for i in range(len(cells)):
                    for j in range(len(cells)):
                        if i != j:
                            arcs.add((cells[i], cells[j]))
        
        return list(arcs)
    
    def revise(self, xi, xj): # For each value in the domain of Xi, check if there is a consistent value in the domain of Xj
        revised = False
        i1, j1 = xi
        i2, j2 = xj

        before = self.domains[i1][j1][:]
        
        values_to_remove = []
        for value in self.domains[i1][j1]:
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
        #self.arc_revisions = 0
        
        while queue:
            xi, xj = queue.popleft()
            self.arc_revisions += 1
            
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
####################################Solving using arc consistency + backtracking ##############################    
    def backtrack_solve(self, board, first_call=True):     
        self.iterations += 1
        
        # Only initialize on first call
        if first_call:
            self.initialize_domains(board)
        
        # Repeat AC-3 + singleton propagation until stable
        while True:
            if not self.ac3():
                return False
            
            changed = False
            for i in range(9):
                for j in range(9):
                    if len(self.domains[i][j]) == 1 and board[i][j] == 0:
                        board[i][j] = self.domains[i][j][0]
                        changed = True
            
            if not changed:
                break
        
        # Check if complete
        next_cell = self.MRV_heuristic(board)
        if not next_cell:
            return True
        
        row, col = next_cell
        
        # Save domain state for backtracking
        saved_domains = [[d[:] for d in row] for row in self.domains]
        
        for num in self.domains[row][col]:           # Try each possible value
            if self.is_valid(board, row, col, num):
                board[row][col] = num
                self.domains[row][col] = [num]
                
                # Recursive call WITHOUT reinitializing
                if self.backtrack_solve(board, first_call=False):
                    return True
                
                # Restore state
                board[row][col] = 0
                self.domains = [[d[:] for d in row] for row in saved_domains]
        
        return False
    
    def MRV_heuristic(self, board): # heuristuc MRV 
        
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
        self.arc_consistency_tree=[]
        self.board = [row[:] for row in board]  
        self.iterations = 0
        self.arc_revisions = 0
        
        start_time = time.time()
        
        # Initialize domains once
        self.initialize_domains(self.board)
        
        # Interleave AC-3 with singleton propagation
        while True:
            if not self.ac3():
                return None, 0
            
            Stable = False
            for i in range(9):
                for j in range(9):
                    if len(self.domains[i][j]) == 1 and self.board[i][j] == 0 :     #apply singleton domain until stable
                        self.board[i][j] = self.domains[i][j][0]
                        self.domains[i][j] = [self.board[i][j]]
                        Stable = True
            
            if not Stable:
                break
        
        # Backtracking for remaining cells after making the board stable (domains already initialized)
        if self.backtrack_solve(self.board, first_call=False):
            solve_time = time.time() - start_time
            return self.board, solve_time
        
        return None, 0
    
    def apply_singleton_domains(self):
        for i in range(9):
            for j in range(9):
                if len(self.domains[i][j]) == 1 and self.board[i][j] == 0:
                    self.board[i][j] = self.domains[i][j][0]

##################################Generating Puzzle using backtracking###################################################

    def generate_puzzle(self, difficulty='medium'):
         
         # Start with empty board
        board = [[0 for _ in range(9)] for _ in range(9)]

        def backtrack_to_generate(b):       #doesn't used the old backtracking to avoid MRV bias i want everything to be random here
            for r in range(9):
                for c in range(9):
                    if b[r][c] == 0:
                        nums = list(range(1, 10))
                        random.shuffle(nums)
                        for num in nums:
                            if self.is_valid(b, r, c, num):
                                b[r][c] = num
                                if backtrack_to_generate(b):
                                    return True
                                b[r][c] = 0
                        return False
            return True
         
        backtrack_to_generate(board)
        solution = [row[:] for row in board]
        cells_to_remove = {
            'easy': 30,      # Remove 30 cells 
            'medium': 40,    # Remove 40 cells 
            'hard': 50       # Remove 50 cells 
        }

        remove_count = cells_to_remove.get(difficulty, 40)

        # Random order of all cells
        cells = [(i, j) for i in range(9) for j in range(9)]
        random.shuffle(cells)

        puzzle = [row[:] for row in board]

        removed = 0
        for r, c in cells:
            if removed >= remove_count:
                break

            backup = puzzle[r][c]
            puzzle[r][c] = 0

            if not self.has_unique_solution(puzzle):
                puzzle[r][c] = backup  # undo
            else:
                removed += 1

        return puzzle
    

    def has_unique_solution(self , board):
            temp = SudokuCSP()
            temp.load_puzzle([row[:] for row in board])
            return temp.count_solutions(limit=2) == 1
    
    def load_puzzle(self, board):
        self.board = [row[:] for row in board]
        self.initialize_domains(self.board)
    
    def count_solutions(self, limit=None):     #using backtracking to count solutions
        
        count = [0]  
        
        def backtrack_count(board):
            if limit and count[0] >= limit:
                return  # Stop counting if limit reached
            
            empty_cell = self.MRV_heuristic(board)
            if not empty_cell:
                count[0] += 1
                return
            
            row, col = empty_cell
            for num in range(1, 10):
                if self.is_valid(board, row, col, num):
                    board[row][col] = num
                    backtrack_count(board)
                    board[row][col] = 0
        
        # Create a copy to avoid modifying original
        board_copy = [row[:] for row in self.board]
        backtrack_count(board_copy)
        return count[0]


######################################## Statictics to be printed ##############################################################3
    def get_statistics(self):
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



              