from flask import Flask, render_template, request, jsonify
from SudokuSolver import SudokuCSP
import time

app = Flask(__name__)
solver = SudokuCSP()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    difficulty = data.get('difficulty', 'medium')
    puzzle = solver.generate_puzzle(difficulty)
    return jsonify({'board': puzzle})

@app.route('/solve', methods=['POST'])
def solve():
    data = request.json
    board = data.get('board')
    mode = data.get('mode', 'instant')
    
    solver.arc_consistency_tree = []
    solver.board = [row[:] for row in board]
    solver.iterations = 0
    solver.arc_revisions = 0

    solved_board, solve_time = solver.solve_with_ac3(board)
    if solved_board:
        return jsonify({
            'success': True,
            'board': solved_board,
            'iterations': solver.iterations,
            'arc_revisions': solver.arc_revisions,
            'time': round(solve_time, 4),
            'ac3_steps': solver.arc_consistency_tree if mode == 'step' else []
        })
    else:
        return jsonify({'success': False, 'message': 'Puzzle is unsolvable'})
    

@app.route('/validate', methods=['POST'])
def validate():
    data = request.json
    board = data.get('board')
    row = data.get('row')
    col = data.get('col')
    num = data.get('num')
    
    temp_board = [row[:] for row in board]
    temp_board[row][col] = 0
    
    # Check immediate constraints
    is_valid = solver.is_valid(temp_board, row, col, num)
    return jsonify({'valid': is_valid})

@app.route('/check_solvable', methods=['POST'])
def check_solvable():
    """Check if current board is solvable using backtracking"""
    data = request.json
    board = data.get('board')
    
    test_board = [row[:] for row in board]
    test_solver = SudokuCSP()
    
    # Try to solve with backtracking
    test_solver.initialize_domains(test_board)

    solved = test_solver.backtrack_solve(test_board, first_call=False)
    
    if solved:
        return jsonify({'solvable': True, 'message': 'Puzzle is solvable'})
    else:
        return jsonify({'solvable': False, 'message': 'Puzzle is not solvable (backtracking failed)'})

if __name__ == '__main__':
    app.run(debug=True)
