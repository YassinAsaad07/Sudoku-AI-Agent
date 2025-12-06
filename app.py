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
    
    start = time.time()
    solver.initialize_domains(solver.board)
    ac3_result = solver.ac3()
    
    if not ac3_result:
        return jsonify({'success': False, 'message': 'Puzzle is unsolvable'})
    
    solved = solver.backtrack_solve(solver.board)
    solve_time = time.time() - start
    
    if solved:
        return jsonify({
            'success': True,
            'board': solver.board,
            'iterations': solver.iterations,
            'arc_revisions': solver.arc_revisions,
            'time': round(solve_time, 4),
            'ac3_steps': solver.arc_consistency_tree if mode == 'step' else []
        })
    else:
        return jsonify({'success': False, 'message': 'No solution found'})

@app.route('/validate', methods=['POST'])
def validate():
    data = request.json
    board = data.get('board')
    row = data.get('row')
    col = data.get('col')
    num = data.get('num')
    
    temp_board = [row[:] for row in board]
    temp_board[row][col] = 0
    
    is_valid = solver.is_valid(temp_board, row, col, num)
    return jsonify({'valid': is_valid})

if __name__ == '__main__':
    app.run(debug=True)
