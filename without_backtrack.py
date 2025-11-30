    # def solve_with_ac3(self, board):
    #     self.board = [row[:] for row in board]  # Deep copy
    #     self.iterations = 0
    #     self.arc_revisions = 0

    #     start_time = time.time()

    #     # Step 1: Initialize domains based on current board
    #     self.initialize_domains(self.board)

    #     # Step 2: Apply AC-3 to reduce domains
    #     if not self.ac3():
    #         return None, "Unsolvable (empty domain found)"

    #     # Step 3: Apply singleton domains (values AC-3 fully determined)
    #     self.apply_singleton_domains()

    #     solve_time = time.time() - start_time

    #     # Step 4: Check if AC-3 solved the puzzle
    #     is_complete = all(
    #         self.board[i][j] != 0
    #         for i in range(9)
    #         for j in range(9)
    #     )

    #     if is_complete:
    #         return self.board,solve_time
    #     else:
    #         return self.board, solve_time