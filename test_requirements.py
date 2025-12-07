from SudokuSolver import SudokuCSP

print("=" * 60)
print("TESTING ALL REQUIREMENTS")
print("=" * 60)

# Test 1: Arc count (no duplicates)
print("\nTest 1: Arc Count")
csp = SudokuCSP()
arcs = csp.get_all_arcs()
print(f"  Total arcs: {len(arcs)}")
print(f"  Expected: 1620")
print(f"  Result: {'PASS' if len(arcs) == 1620 else 'FAIL'}")

# Test 2: Easy puzzle - AC-3 should solve completely
print("\nTest 2: Easy Puzzle (AC-3 should solve without backtracking)")
easy_puzzle = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9]
]

csp = SudokuCSP()
solution, solve_time = csp.solve_with_ac3(easy_puzzle)
print(f"  Solved: {solution is not None}")
print(f"  Time: {solve_time:.4f}s")
print(f"  Iterations: {csp.iterations}")
print(f"  Arc revisions: {csp.arc_revisions}")
print(f"  Result: {'PASS' if solution is not None else 'FAIL'}")

# Test 3: Hard puzzle - requires backtracking with AC-3
print("\nTest 3: Hard Puzzle (requires backtracking + AC-3)")
hard_puzzle = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 3, 0, 8, 5],
    [0, 0, 1, 0, 2, 0, 0, 0, 0],
    [0, 0, 0, 5, 0, 7, 0, 0, 0],
    [0, 0, 4, 0, 0, 0, 1, 0, 0],
    [0, 9, 0, 0, 0, 0, 0, 0, 0],
    [5, 0, 0, 0, 0, 0, 0, 7, 3],
    [0, 0, 2, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 4, 0, 0, 0, 9]
]

csp = SudokuCSP()
solution, solve_time = csp.solve_with_ac3(hard_puzzle)
print(f"  Solved: {solution is not None}")
print(f"  Time: {solve_time:.4f}s")
print(f"  Iterations: {csp.iterations}")
print(f"  Arc revisions: {csp.arc_revisions}")
print(f"  Result: {'PASS' if solution is not None else 'FAIL'}")

# Test 4: Verify AC-3 runs during backtracking
print("\nTest 4: AC-3 Interleaving (domains reinitialize)")
csp = SudokuCSP()
# Use a puzzle that requires backtracking
test_puzzle = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0]
]
solution, solve_time = csp.solve_with_ac3(test_puzzle)
print(f"  Solved: {solution is not None}")
print(f"  Iterations (should be > 1): {csp.iterations}")
print(f"  Arc revisions (should be > 1620): {csp.arc_revisions}")
print(f"  Result: {'PASS' if csp.iterations > 1 and csp.arc_revisions > 1620 else 'FAIL'}")

print("\n" + "=" * 60)
print("ALL TESTS COMPLETED")
print("=" * 60)
