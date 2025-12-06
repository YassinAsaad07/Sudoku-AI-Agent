import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import json
import threading
import time
from SudokuSolver import SudokuCSP


class SudokuGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku CSP Solver")
        self.root.geometry("1400x900")
        self.root.resizable(True, True)
        self.root.configure(bg='#f5f5f5')

        self.solver = SudokuCSP()
        self.cells = [[None for _ in range(9)] for _ in range(9)]
        self.original_board = [[0 for _ in range(9)] for _ in range(9)]
        self.current_domains = [[[] for _ in range(9)] for _ in range(9)]
        self.step_delay_ms = 100
        self._stop_animation = False

        self.setup_ui()
        self.apply_modern_style()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        left_pane = ttk.Frame(main_frame)
        left_pane.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        right_pane = ttk.Frame(main_frame)
        right_pane.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        self.create_board_panel(left_pane)
        self.create_control_panel(left_pane)
        self.create_info_panel(right_pane)
        self.create_ac3_panel(right_pane)

    def create_board_panel(self, parent):
        board_frame = ttk.LabelFrame(parent, text="Sudoku Board", padding="10")
        board_frame.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)

        board_container = tk.Frame(board_frame, bg='black', bd=2, relief=tk.SOLID)
        board_container.pack(padx=5, pady=5)

        for i in range(9):
            for j in range(9):
                padx = (1, 1)
                pady = (1, 1)
                if j % 3 == 0 and j != 0:
                    padx = (3, 1)
                if j == 8:
                    padx = (1, 0)
                if i % 3 == 0 and i != 0:
                    pady = (3, 1)
                if i == 8:
                    pady = (1, 0)

                cell = tk.Entry(board_container, width=2, font=("Arial", 16, "bold"),
                               justify='center', validate='key', bd=0, relief=tk.FLAT,
                               highlightthickness=0)
                cell['validatecommand'] = (cell.register(self.validate_input), '%P')
                cell.grid(row=i, column=j, padx=padx, pady=pady, ipady=5)

                cell.bind('<KeyRelease>', lambda e, r=i, c=j: self.on_cell_change(r, c))

                self.cells[i][j] = cell

    def create_control_panel(self, parent):
        control_frame = ttk.LabelFrame(parent, text="Controls", padding="15")
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        # Mode Selection
        mode_frame = ttk.Frame(control_frame)
        mode_frame.pack(fill=tk.X, pady=8)

        ttk.Label(mode_frame, text="Mode:", font=("Segoe UI", 11, 'bold')).pack(side=tk.LEFT, padx=5)
        
        self.mode_var = tk.StringVar(value='generate')
        ttk.Radiobutton(mode_frame, text="Generate Puzzle", variable=self.mode_var,
                       value='generate', command=self.on_mode_change).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(mode_frame, text="Input Puzzle", variable=self.mode_var,
                       value='input', command=self.on_mode_change).pack(side=tk.LEFT, padx=10)

        # Difficulty Selection
        self.diff_frame = ttk.Frame(control_frame)
        self.diff_frame.pack(fill=tk.X, pady=8)

        ttk.Label(self.diff_frame, text="Difficulty:", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=5)
        self.difficulty_var = tk.StringVar(value='medium')
        ttk.Combobox(self.diff_frame, textvariable=self.difficulty_var,
                    values=['easy', 'medium', 'hard'], state='readonly', width=12, font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=5)

        # Solve Mode Selection
        self.solve_mode_frame = ttk.Frame(control_frame)
        self.solve_mode_frame.pack(fill=tk.X, pady=8)

        ttk.Label(self.solve_mode_frame, text="Solve Mode:", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=5)
        self.solve_mode_var = tk.StringVar(value='step')
        ttk.Radiobutton(self.solve_mode_frame, text="Step-by-Step", variable=self.solve_mode_var,
                       value='step').pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(self.solve_mode_frame, text="Instant", variable=self.solve_mode_var,
                       value='instant').pack(side=tk.LEFT, padx=10)

        # Speed Control
        self.speed_frame = ttk.Frame(control_frame)
        self.speed_frame.pack(fill=tk.X, pady=8)
        ttk.Label(self.speed_frame, text="Speed (ms):", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=5)
        self.speed_var = tk.IntVar(value=self.step_delay_ms)
        ttk.Scale(self.speed_frame, from_=20, to=500, orient=tk.HORIZONTAL,
                 variable=self.speed_var, length=250).pack(side=tk.LEFT, padx=5)

        # Buttons Container
        self.btn_container = ttk.Frame(control_frame)
        self.btn_container.pack(fill=tk.X, pady=10)

        # Generate Mode Buttons
        self.generate_btn = ttk.Button(self.btn_container, text="Generate Puzzle", command=self.generate_puzzle)
        self.solve_btn = ttk.Button(self.btn_container, text="Solve", command=self.solve_puzzle)
        self.stop_btn = ttk.Button(self.btn_container, text="Stop", command=self.stop_animation)
        self.clear_btn = ttk.Button(self.btn_container, text="Clear Board", command=self.clear_board)
        self.ai_continue_btn = ttk.Button(self.btn_container, text="AI Continue", command=self.ai_continue)

        self.update_button_visibility()

    def create_info_panel(self, parent):
        info_frame = ttk.LabelFrame(parent, text="Statistics & Log", padding="15")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        stats_frame = tk.Frame(info_frame, bg='#ecf0f1', relief=tk.SOLID, bd=1)
        stats_frame.pack(fill=tk.X, pady=10, padx=5)

        self.stats_label = tk.Label(stats_frame, text="Ready to solve!\n\nTime: 0.00s\nIterations: 0\nArc Revisions: 0\nStatus: Waiting",
                                     font=("Segoe UI", 11), justify=tk.LEFT, bg='#ecf0f1', fg='#2c3e50', pady=10)
        self.stats_label.pack()

        log_frame = ttk.LabelFrame(info_frame, text="Solution Log", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.log_text = scrolledtext.ScrolledText(log_frame, width=50, height=15, font=("Consolas", 9), wrap=tk.WORD, bg='#fafafa')
        self.log_text.pack(fill=tk.BOTH, expand=True)

        self.log_text.tag_config('header', foreground='#2980b9', font=("Consolas", 9, 'bold'))
        self.log_text.tag_config('success', foreground='#27ae60', font=("Consolas", 9, 'bold'))
        self.log_text.tag_config('error', foreground='#e74c3c', font=("Consolas", 9, 'bold'))
        self.log_text.tag_config('info', foreground='#34495e')

        self.log_message("Welcome to Sudoku CSP Solver!", 'header')
        self.log_message("Using Arc Consistency (AC-3) Algorithm\n", 'info')

    def create_ac3_panel(self, parent):
        ac3_frame = ttk.LabelFrame(parent, text="Arc Consistency Revisions", padding="15")
        ac3_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.ac3_text = scrolledtext.ScrolledText(ac3_frame, width=60, height=30, font=("Consolas", 10), wrap=tk.WORD, bg='#fafafa')
        self.ac3_text.pack(fill=tk.BOTH, expand=True)

        self.ac3_text.tag_config('arc_header', foreground='#2980b9', font=("Consolas", 10, 'bold'))
        self.ac3_text.tag_config('arc_detail', foreground='#27ae60', font=("Consolas", 10))
        self.ac3_text.tag_config('arc_change', foreground='#e74c3c', font=("Consolas", 10, 'bold'))

    def validate_input(self, value):
        if value == "":
            return True
        if value.isdigit() and 1 <= int(value) <= 9 and len(value) == 1:
            return True
        return False

    def on_cell_change(self, row, col):
        if self.mode_var.get() == 'input':
            value = self.cells[row][col].get()
            if value:
                num = int(value)
                temp_board = self.get_board()
                temp_board[row][col] = 0
                if not self.solver.is_valid(temp_board, row, col, num):
                    self.cells[row][col].config(bg='#ffcccc')
                    messagebox.showerror("Constraint Violation", 
                                       f"Number {num} at position ({row+1}, {col+1}) violates Sudoku constraints!\n\n"
                                       f"This number already exists in the same row, column, or 3x3 box.")
                    self.cells[row][col].delete(0, tk.END)
                    self.cells[row][col].config(bg='white')
                else:
                    self.cells[row][col].config(bg='white')
            else:
                self.cells[row][col].config(bg='white')

    def on_mode_change(self):
        if self.mode_var.get() == 'input':
            self.log_message("Input mode: Enter numbers manually", 'info')
            self.clear_board()
        else:
            self.log_message("Generate mode: Create random puzzles", 'info')
        self.update_button_visibility()

    def update_button_visibility(self):
        # Clear all buttons first
        for widget in self.btn_container.winfo_children():
            widget.pack_forget()

        if self.mode_var.get() == 'generate':
            # Mode 1: Generate - show Generate, Solve, Stop
            self.generate_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            self.solve_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            self.stop_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        else:
            # Mode 2: Input - show AI Continue, Stop, Clear
            self.ai_continue_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            self.stop_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            self.clear_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

    def get_board(self):
        board = [[0 for _ in range(9)] for _ in range(9)]
        for i in range(9):
            for j in range(9):
                value = self.cells[i][j].get()
                if value:
                    board[i][j] = int(value)
        return board

    def set_board(self, board, is_original=True):
        for i in range(9):
            for j in range(9):
                self.cells[i][j].config(state='normal')
                self.cells[i][j].delete(0, tk.END)

                if board[i][j] != 0:
                    self.cells[i][j].insert(0, str(board[i][j]))
                    if is_original:
                        self.cells[i][j].config(bg='#e0e0e0', state='readonly')
                        self.original_board[i][j] = board[i][j]
                    else:
                        self.cells[i][j].config(bg='#c8e6c9', state='readonly')
                else:
                    self.cells[i][j].config(bg='white', state='normal')

    def generate_puzzle(self):
        self.log_message("\n" + "="*40, 'header')
        self.log_message("Generating puzzle...", 'header')
        difficulty = self.difficulty_var.get()
        puzzle = self.solver.generate_puzzle(difficulty)

        if puzzle:
            self.clear_board()
            self.set_board(puzzle, is_original=True)
            filled = sum(1 for i in range(9) for j in range(9) if puzzle[i][j] != 0)
            self.log_message(f"Generated {difficulty} puzzle successfully!", 'success')
            self.log_message(f"Cells filled: {filled}/81", 'info')
        else:
            messagebox.showerror("Error", "Failed to generate puzzle")
            self.log_message("Failed to generate puzzle", 'error')

    def solve_puzzle(self):
        board = self.get_board()
        if all(board[i][j] == 0 for i in range(9) for j in range(9)):
            messagebox.showwarning("Warning", "Please enter a puzzle or generate one first!")
            return

        is_valid, error_msg = self.solver.validate_board(board)
        if not is_valid:
            messagebox.showerror("Invalid Board", error_msg)
            self.log_message(f"{error_msg}", 'error')
            return

        self.log_message("\n" + "="*40, 'header')
        self.log_message(f"Starting solver in {self.solve_mode_var.get()} mode...", 'header')
        self._stop_animation = False

        if self.solve_mode_var.get() == 'instant':
            self.solve_instant()
        else:
            self.solve_step_by_step()

    def solve_instant(self):
        def run_solve():
            start = time.time()
            board = self.get_board()
            self.solver.board = [row[:] for row in board]
            self.solver.initialize_domains(self.solver.board)
            self.solver.ac3()
            solved = self.solver.backtrack_solve(self.solver.board)
            solve_time = time.time() - start

            if solved:
                self.root.after(0, lambda: self.show_solution(self.solver.board, solve_time))
            else:
                self.root.after(0, lambda: self.handle_unsolvable())

        threading.Thread(target=run_solve, daemon=True).start()

    def solve_step_by_step(self):
        def run_ac3():
            board = self.get_board()
            self.solver.arc_consistency_tree = []
            self.solver.board = [row[:] for row in board]
            self.solver.initialize_domains(self.solver.board)
            ac3_result = self.solver.ac3()
            self.current_domains = [[list(d) for d in row] for row in self.solver.domains]
            self.root.after(0, lambda: self.animate_ac3(ac3_result))

        threading.Thread(target=run_ac3, daemon=True).start()

    def animate_ac3(self, ac3_result):
        steps = list(self.solver.arc_consistency_tree)
        delay = max(20, int(self.speed_var.get()))
        self.ac3_text.delete(1.0, tk.END)
        self.ac3_text.insert(tk.END, "=== Arc Consistency Revisions ===\n\n", 'arc_header')

        def play_step(idx):
            if self._stop_animation or idx >= len(steps):
                self.ac3_text.insert(tk.END, f"\n=== Total Revisions: {self.solver.arc_revisions} ===\n", 'arc_header')
                self.root.after(200, self.apply_singletons_and_backtrack)
                return

            log = steps[idx]
            if "arc" in log:
                xi, xj = log["arc"]
                i1, j1 = xi
                i2, j2 = xj
                before = log.get('before', [])
                after = log.get('after', [])
                self.current_domains[i1][j1] = list(after)

                # Display in AC3 panel
                self.ac3_text.insert(tk.END, f"Step {idx+1}: Arc ({i1+1},{j1+1}) -> ({i2+1},{j2+1})\n", 'arc_header')
                self.ac3_text.insert(tk.END, f"  Before: {before}\n", 'arc_detail')
                self.ac3_text.insert(tk.END, f"  After:  {after}\n", 'arc_change')
                if len(before) != len(after):
                    self.ac3_text.insert(tk.END, f"  Removed: {set(before) - set(after)}\n\n", 'arc_change')
                else:
                    self.ac3_text.insert(tk.END, "\n")
                self.ac3_text.see(tk.END)

                if len(after) == 1 and self.original_board[i1][j1] == 0:
                    self.cells[i1][j1].config(bg='#fff9c4')
                    self.log_message(f"Cell ({i1+1},{j1+1}) -> {after}", 'info')

            self.root.after(delay, lambda: play_step(idx+1))

        play_step(0)

    def apply_singletons_and_backtrack(self):
        singletons = []
        for i in range(9):
            for j in range(9):
                dom = self.solver.domains[i][j]
                if len(dom) == 1 and self.original_board[i][j] == 0:
                    singletons.append((i, j, dom[0]))

        delay = max(20, int(self.speed_var.get()))

        def apply_idx(idx):
            if self._stop_animation or idx >= len(singletons):
                self.log_message("Starting backtracking...", 'info')
                threading.Thread(target=self.run_backtrack_and_show_result, daemon=True).start()
                return

            i, j, val = singletons[idx]
            self.cells[i][j].config(state='normal')
            self.cells[i][j].delete(0, tk.END)
            self.cells[i][j].insert(0, str(val))
            self.cells[i][j].config(bg='#c8e6c9', state='readonly')
            self.log_message(f"Applied {val} to ({i+1},{j+1})", 'success')
            self.root.after(delay, lambda: apply_idx(idx+1))

        apply_idx(0)

    def run_backtrack_and_show_result(self):
        start = time.time()
        board = self.get_board()
        self.solver.board = [row[:] for row in board]
        if not any(self.solver.domains[0][0]):
            self.solver.initialize_domains(self.solver.board)

        solved = self.solver.backtrack_solve(self.solver.board)
        solve_time = time.time() - start

        if solved:
            self.root.after(0, lambda: self.show_solution(self.solver.board, solve_time))
        else:
            self.root.after(0, lambda: self.handle_unsolvable())

    def show_solution(self, solution_board, solve_time):
        self.set_board(solution_board, is_original=False)
        for i in range(9):
            for j in range(9):
                if self.original_board[i][j] != 0:
                    self.cells[i][j].config(bg='#e0e0e0', state='readonly')

        self.log_message(f"\nPuzzle solved in {solve_time:.4f}s!", 'success')
        self.log_message(f"Iterations: {self.solver.iterations}", 'info')
        self.log_message(f"Arc Revisions: {self.solver.arc_revisions}", 'info')
        self.update_statistics(solve_time, 'Solved')
        messagebox.showinfo("Success!", f"Puzzle solved in {solve_time:.4f}s!\n\nIterations: {self.solver.iterations}\nArc Revisions: {self.solver.arc_revisions}")

    def handle_unsolvable(self):
        self.log_message("\nPuzzle is unsolvable!", 'error')
        self.update_statistics(0, 'Unsolvable')
        messagebox.showerror("Error", "This puzzle has no solution!")

    def stop_animation(self):
        self._stop_animation = True
        self.log_message("Animation stopped", 'info')

    def clear_board(self):
        for i in range(9):
            for j in range(9):
                self.cells[i][j].config(state='normal', bg='white')
                self.cells[i][j].delete(0, tk.END)

        self.original_board = [[0 for _ in range(9)] for _ in range(9)]
        self.current_domains = [[[] for _ in range(9)] for _ in range(9)]
        self.log_message("\nBoard cleared!", 'info')
        self.update_statistics(0, 'Ready')



    def ai_continue(self):
        """AI continues solving from current user input"""
        board = self.get_board()
        empty_count = sum(1 for i in range(9) for j in range(9) if board[i][j] == 0)
        
        if empty_count == 0:
            messagebox.showinfo("Info", "Board is already complete!")
            return
        
        if empty_count == 81:
            messagebox.showwarning("Warning", "Please enter some numbers first!")
            return

        is_valid, error_msg = self.solver.validate_board(board)
        if not is_valid:
            messagebox.showerror("Invalid Board", error_msg)
            self.log_message(f"{error_msg}", 'error')
            return

        # Store current board as original
        for i in range(9):
            for j in range(9):
                if board[i][j] != 0:
                    self.original_board[i][j] = board[i][j]
                    self.cells[i][j].config(bg='#e0e0e0', state='readonly')

        self.log_message(f"\nAI continuing from your input ({81-empty_count} cells filled)...", 'header')
        self.solve_puzzle()



    def update_statistics(self, solve_time, status):
        stats_text = f"Status: {status}\n\n"
        stats_text += f"Time: {solve_time:.4f}s\n"
        stats_text += f"Iterations: {self.solver.iterations}\n"
        stats_text += f"Arc Revisions: {self.solver.arc_revisions}"
        self.stats_label.config(text=stats_text)

    def log_message(self, message, tag='info'):
        self.log_text.insert(tk.END, message + "\n", tag)
        self.log_text.see(tk.END)
        self.root.update()

    def apply_modern_style(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure modern colors
        style.configure('TLabelframe', background='#ffffff', borderwidth=2, relief='solid')
        style.configure('TLabelframe.Label', font=('Segoe UI', 12, 'bold'), foreground='#2c3e50')
        style.configure('TFrame', background='#ffffff')
        style.configure('TLabel', background='#ffffff', font=('Segoe UI', 10))
        style.configure('TRadiobutton', background='#ffffff', font=('Segoe UI', 10))
        style.configure('TButton', font=('Segoe UI', 11, 'bold'), padding=10)
        
        # Button colors
        style.map('TButton',
                 background=[('active', '#3498db'), ('!active', '#2980b9')],
                 foreground=[('active', 'white'), ('!active', 'white')])


def main():
    root = tk.Tk()
    app = SudokuGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
