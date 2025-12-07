from SudokuSolver import SudokuCSP

# Test with a simpler hard puzzle
hard_puzzle = [
    [0, 0, 0, 2, 6, 0, 7, 0, 1],
    [6, 8, 0, 0, 7, 0, 0, 9, 0],
    [1, 9, 0, 0, 0, 4, 5, 0, 0],
    [8, 2, 0, 1, 0, 0, 0, 4, 0],
    [0, 0, 4, 6, 0, 2, 9, 0, 0],
    [0, 5, 0, 0, 0, 3, 0, 2, 8],
    [0, 0, 9, 3, 0, 0, 0, 7, 4],
    [0, 4, 0, 0, 5, 0, 0, 3, 6],
    [7, 0, 3, 0, 1, 8, 0, 0, 0]
]

print("Testing hard puzzle...")
csp = SudokuCSP()
solution, solve_time = csp.solve_with_ac3(hard_puzzle)

if solution:
    print(f"SOLVED in {solve_time:.4f}s")
    print(f"Iterations: {csp.iterations}")
    print(f"Arc revisions: {csp.arc_revisions}")
    print("\nSolution:")
    for row in solution:
        print(row)
else:
    print("FAILED to solve")
    print(f"Iterations: {csp.iterations}")
    print(f"Arc revisions: {csp.arc_revisions}")
