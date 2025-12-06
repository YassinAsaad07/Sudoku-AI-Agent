# ---- test_get_all_arcs.py ----

from SudokuSolver import SudokuCSP  # adjust if needed

csp = SudokuCSP()

arcs = csp.get_all_arcs()

print("Total arcs returned:", arcs)

# Full list for deeper testing
arc_list = []
# Re-run the code but returning list instead of count
def get_arcs_only():
             #1620 total arcs
        arcs = []
        
        # Row constraints - each pair of cells in same row
        for i in range(9):   
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
                            # if (cells[i],cells[j]) not in arcs : 
                              arcs.append((cells[i], cells[j]))
                         
        
        return arcs

full_list = get_arcs_only()

print("Actual list length:", len(full_list))

# Check for duplicates
unique_arcs = set(full_list)
print("Unique arcs:", len(unique_arcs))

# Show duplicates count
print("Duplicate arcs:", len(full_list) - len(unique_arcs))

# Show first few arcs
print("First 20 arcs:", list(unique_arcs)[:20])
