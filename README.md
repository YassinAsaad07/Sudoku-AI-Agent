# Sudoku CSP Solver with Arc Consistency (AC-3)

## Project Description
This project implements a Sudoku puzzle solver using Constraint Satisfaction Problem (CSP) techniques, specifically the AC-3 (Arc Consistency 3) algorithm combined with backtracking. The application features an interactive GUI built with Tkinter.


## Requirements

- Python 3.7 or higher
- tkinter (usually comes with Python)
- No external dependencies required!

## How to Run

### Option 1: Run from main.py
```bash
python main.py
```

### Option 2: Run GUI directly
```bash
python sudoku_gui.py
```

## Features

### ✅ Assignment Requirements Met

1. **Game GUI (Mode 1 & 2)**
   - Mode 1: Generate random puzzles with adjustable difficulty
   - Mode 2: User input with real-time constraint validation

2. **Backtracking Algorithm**
   - Validates puzzle solvability
   - Generates random solvable puzzles
   - Uses MRV (Minimum Remaining Values) heuristic

3. **Arc Consistency (AC-3)**
   - Full implementation of AC-3 algorithm
   - Domain initialization and reduction
   - Binary constraint enforcement
   - Arc revision tracking

### Bonus Features

- **Interactive Input Validation**: Cells turn red when constraints are violated
- **Visual Feedback**: Color-coded cells (gray=original, green=solved, white=empty, red=invalid)
- **Statistics Display**: Shows iterations, arc revisions, and solve time
- **Save/Load Puzzles**: Export and import puzzles as JSON files
- **Solution Log**: Detailed logging of the solving process
- **Domain Display**: Option to view possible values for each cell after AC-3

## How to Use

### Generate Mode
1. Select difficulty level (easy/medium/hard)
2. Click "Generate Puzzle"
3. Click "Solve with AC-3" to see the solution

### Input Mode
1. Select "Input Puzzle" radio button
2. Enter numbers manually (1-9)
3. Invalid entries will be highlighted in red
4. Click "Solve with AC-3" when ready

### Additional Functions
- **Clear Board**: Reset the entire puzzle
- **Validate Input**: Check if current board follows Sudoku rules
- **Save Puzzle**: Export current puzzle to JSON file
- **Load Puzzle**: Import puzzle from JSON file
- **Show Domains**: Toggle to see possible values for cells

##  Algorithm Details

### 1. Arc Consistency (AC-3)

The AC-3 algorithm enforces arc consistency by:
1. Initializing domains for each cell (1-9 for empty cells)
2. Creating binary constraints (arcs) between cells in same row/column/box
3. Iteratively revising domains to remove inconsistent values
4. Propagating constraints until no further changes occur

**Time Complexity**: O(ed³) where e is number of arcs and d is domain size

### 2. Backtracking with MRV Heuristic

After AC-3 reduces domains:
1. Select empty cell with smallest domain (MRV heuristic)
2. Try each value in the cell's domain
3. Recursively solve the remaining puzzle
4. Backtrack if no solution found

**Optimization**: AC-3 significantly reduces the search space for backtracking

##  Data Structures Used

### Main Data Structures

1. **Board**: `List[List[int]]` - 9x9 2D array representing the Sudoku grid
2. **Domains**: `List[List[List[int]]]` - 9x9 array of lists containing possible values for each cell
3. **Arcs**: `List[Tuple[Tuple[int, int], Tuple[int, int]]]` - Binary constraints between cells
4. **Queue**: `deque` - FIFO queue for AC-3 arc processing

### Cell Representation
- **0**: Empty cell
- **1-9**: Filled cell with digit

### Constraint Types
- **Row constraints**: All cells in same row must have different values
- **Column constraints**: All cells in same column must have different values
- **Box constraints**: All cells in same 3x3 box must have different values

## 📈 Performance Comparison

Expected performance (approximate):

| Difficulty | Empty Cells | Avg. Time | Avg. Iterations | Avg. Arc Revisions |
|-----------|-------------|-----------|-----------------|-------------------|
| Easy      | 30          | 0.01-0.05s| 10-50          | 500-1500         |
| Medium    | 40          | 0.05-0.20s| 50-200         | 1500-3000        |
| Hard      | 50          | 0.20-1.00s| 200-1000       | 3000-6000        |

*Note: Actual performance depends on specific puzzle configuration*

## 🎨 Color Coding

- **Gray (#e0e0e0)**: Original puzzle numbers (read-only)
- **White**: Empty cells (editable)
- **Light Green (#c8e6c9)**: Solved cells
- **Light Red (#ffcccc)**: Invalid input (violates constraints)

## 📝 Sample Puzzles

### Easy Puzzle
```
5 3 0 | 0 7 0 | 0 0 0
6 0 0 | 1 9 5 | 0 0 0
0 9 8 | 0 0 0 | 0 6 0
------+-------+------
8 0 0 | 0 6 0 | 0 0 3
4 0 0 | 8 0 3 | 0 0 1
7 0 0 | 0 2 0 | 0 0 6
------+-------+------
0 6 0 | 0 0 0 | 2 8 0
0 0 0 | 4 1 9 | 0 0 5
0 0 0 | 0 8 0 | 0 7 9
```

## 🐛 Troubleshooting

### Issue: "No module named 'tkinter'"
**Solution**: Install tkinter
- Ubuntu/Debian: `sudo apt-get install python3-tk`
- macOS: Tkinter comes with Python
- Windows: Tkinter comes with Python

### Issue: GUI not displaying correctly
**Solution**: Make sure you're using Python 3.7+

### Issue: Puzzle generation is slow
**Solution**: This is normal for hard puzzles. The algorithm ensures solvability.

## 📚 References

- Mackworth, A. K. (1977). "Consistency in Networks of Relations"
- Russell, S., & Norvig, P. (2020). "Artificial Intelligence: A Modern Approach" (4th ed.)
- Sudoku rules: https://en.wikipedia.org/wiki/Sudoku



## ✨ Extra Features Implemented

1. ✅ Interactive constraint validation
2. ✅ Real-time error highlighting
3. ✅ Domain visualization option
4. ✅ Puzzle save/load functionality
5. ✅ Comprehensive logging system
6. ✅ Performance statistics tracking
7. ✅ Multiple difficulty levels
8. ✅ Beautiful, user-friendly GUI

---
