# File: sudoku_gui.py
"""
GUI for Sudoku CSP Solver
Provides interactive interface for solving Sudoku puzzles
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from SudokuSolver import SudokuCSP
import json


class SudokuGUI:
    """
    Graphical User Interface for Sudoku CSP Solver
    Features:
    - Two modes: Generate puzzle or Input puzzle
    - Real-time constraint validation
    - Visual feedback for solving process
    - Statistics and logging
    """
    
    def __init__(self, root):
        """
        Initialize the GUI
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("Sudoku CSP Solver with Arc Consistency")
        self.root.geometry("1100x750")
        self.root.resizable(False, False)
        
        # Initialize solver
        self.solver = SudokuCSP()
        
        
        # GUI state variables
        self.cells = [[None for _ in range(9)] for _ in range(9)]
        self.original_board = [[0 for _ in range(9)] for _ in range(9)]
        self.current_domains = [[[] for _ in range(9)] for _ in range(9)]
        
        # Setup user interface
        self.setup_ui()
        
        # Apply theme
        self.apply_theme()
    
    def setup_ui(self):
        """Setup all UI components"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Left panel - Sudoku board
        self.create_board_panel(main_frame)
        
        # Control panel
        self.create_control_panel(main_frame)
        
        # Right panel - Information
        self.create_info_panel(main_frame)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
    
    def create_board_panel(self, parent):
        """
        Create the Sudoku board panel
        
        Args:
            parent: Parent widget
        """
        board_frame = ttk.LabelFrame(parent, text="Sudoku Board", padding="10")
        board_frame.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.N, tk.W, tk.E))
        
        # Create 9x9 grid of entry cells
        for i in range(9):
            for j in range(9):
                # Calculate padding for 3x3 box borders
                padx = (2, 2)
                pady = (2, 2)
                if j % 3 == 0:
                    padx = (4, 2)
                if i % 3 == 0:
                    pady = (4, 2)
                
                # Create cell entry widget
                cell = tk.Entry(board_frame, width=3, font=('Arial', 18, 'bold'),
                               justify='center', validate='key')
                cell['validatecommand'] = (cell.register(self.validate_input), '%P')
                cell.grid(row=i, column=j, padx=padx, pady=pady)
                
                # Bind events for interactive validation
                cell.bind('<KeyRelease>', lambda e, r=i, c=j: self.on_cell_change(r, c))
                cell.bind('<FocusIn>', lambda e, r=i, c=j: self.on_cell_focus(r, c))
                
                self.cells[i][j] = cell
    
    def create_control_panel(self, parent):
        """
        Create the control panel with buttons and options
        
        Args:
            parent: Parent widget
        """
        control_frame = ttk.LabelFrame(parent, text="Controls", padding="10")
        control_frame.grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Mode selection
        mode_frame = ttk.Frame(control_frame)
        mode_frame.grid(row=0, column=0, columnspan=3, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(mode_frame, text="Mode:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        self.mode_var = tk.StringVar(value='generate')
        ttk.Radiobutton(mode_frame, text="Generate Puzzle", variable=self.mode_var,
                       value='generate', command=self.on_mode_change).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="Input Puzzle", variable=self.mode_var,
                       value='input', command=self.on_mode_change).pack(side=tk.LEFT, padx=5)
        
        # Difficulty selection
        difficulty_frame = ttk.Frame(control_frame)
        difficulty_frame.grid(row=1, column=0, columnspan=3, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(difficulty_frame, text="Difficulty:", font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        self.difficulty_var = tk.StringVar(value='medium')
        difficulty_combo = ttk.Combobox(difficulty_frame, textvariable=self.difficulty_var,
                                       values=['easy', 'medium', 'hard'], state='readonly', width=10)
        difficulty_combo.pack(side=tk.LEFT, padx=5)
        
        # Action buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Generate Puzzle", 
                  command=self.generate_puzzle).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Solve with AC-3", 
                  command=self.solve_puzzle).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Board", 
                  command=self.clear_board).pack(side=tk.LEFT, padx=5)
        
        # Additional controls
        extra_frame = ttk.Frame(control_frame)
        extra_frame.grid(row=3, column=0, columnspan=3, pady=5)
        
        ttk.Button(extra_frame, text="Save Puzzle", 
                  command=self.save_puzzle).pack(side=tk.LEFT, padx=5)
        ttk.Button(extra_frame, text="Load Puzzle", 
                  command=self.load_puzzle).pack(side=tk.LEFT, padx=5)
        ttk.Button(extra_frame, text="Validate Input", 
                  command=self.validate_current_board).pack(side=tk.LEFT, padx=5)
        
        # Show domains checkbox
        self.show_domains_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(control_frame, text="Show Domains (after AC-3)", 
                       variable=self.show_domains_var,
                       command=self.toggle_domains).grid(row=4, column=0, columnspan=3, pady=5)
    
    def create_info_panel(self, parent):
        """
        Create the information panel with statistics and logs
        
        Args:
            parent: Parent widget
        """
        info_frame = ttk.LabelFrame(parent, text="Information & Log", padding="10")
        info_frame.grid(row=0, column=1, rowspan=2, padx=5, pady=5, sticky=(tk.N, tk.S, tk.W, tk.E))
        
        # Statistics display
        stats_frame = ttk.LabelFrame(info_frame, text="Statistics", padding="10")
        stats_frame.pack(fill=tk.X, pady=5)
        
        self.stats_label = ttk.Label(stats_frame, 
                                     text="Ready to solve!\n\nIterations: 0\nArc Revisions: 0\nTime: 0.00s\nStatus: Waiting",
                                     font=('Arial', 10), justify=tk.LEFT)
        self.stats_label.pack()
        
        # Solution log
        log_frame = ttk.LabelFrame(info_frame, text="Solution Log", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, width=45, height=30, 
                                                  font=('Courier', 9), wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for colored output
        self.log_text.tag_config('header', foreground='blue', font=('Courier', 9, 'bold'))
        self.log_text.tag_config('success', foreground='green', font=('Courier', 9, 'bold'))
        self.log_text.tag_config('error', foreground='red', font=('Courier', 9, 'bold'))
        self.log_text.tag_config('info', foreground='black')
        
        # Initial welcome message
        self.log_message("Welcome to Sudoku CSP Solver!", 'header')
        self.log_message("Using Arc Consistency (AC-3) Algorithm\n", 'info')
        self.log_message("Instructions:", 'header')
        self.log_message("1. Generate a random puzzle or input your own", 'info')
        self.log_message("2. Click 'Solve with AC-3' to see the solution", 'info')
        self.log_message("3. Invalid entries will be highlighted in red\n", 'info')
    
    def validate_input(self, value):
        """
        Validate cell input (only 1-9 or empty)
        
        Args:
            value: Input string
            
        Returns:
            True if valid, False otherwise
        """
        if value == "":
            return True
        if value.isdigit() and 1 <= int(value) <= 9 and len(value) == 1:
            return True
        return False
    
    def on_cell_change(self, row, col):
        """
        Handle cell value change with real-time constraint validation
        
        Args:
            row: Row index
            col: Column index
        """
        if self.mode_var.get() == 'input':
            value = self.cells[row][col].get()
            if value:
                num = int(value)
                # Temporarily set to 0 to check validity
                temp_board = self.get_board()
                temp_board[row][col] = 0
                
                # Check if placement violates constraints
                if not self.solver.is_valid(temp_board, row, col, num):
                    self.cells[row][col].config(bg='#ffcccc')  # Light red for invalid
                    self.log_message(f"⚠ Invalid: {num} at cell ({row+1},{col+1}) violates constraints", 'error')
                else:
                    self.cells[row][col].config(bg='white')
            else:
                self.cells[row][col].config(bg='white')
    
    def on_cell_focus(self, row, col):
        """
        Handle cell focus event - show domain if available
        
        Args:
            row: Row index
            col: Column index
        """
        if self.show_domains_var.get() and len(self.current_domains[row][col]) > 0:
            domain = self.current_domains[row][col]
            self.log_message(f"Cell ({row+1},{col+1}) domain: {domain}", 'info')
    
    def on_mode_change(self):
        """Handle mode change event"""
        if self.mode_var.get() == 'input':
            self.log_message("Input mode: Enter numbers manually", 'info')
        else:
            self.log_message("Generate mode: Create random puzzles", 'info')
    
    def get_board(self):
        """
        Get current board state from GUI
        
        Returns:
            9x9 2D list representing the board
        """
        board = [[0 for _ in range(9)] for _ in range(9)]
        for i in range(9):
            for j in range(9):
                value = self.cells[i][j].get()
                if value:
                    board[i][j] = int(value)
        return board
    
    def set_board(self, board, is_original=True):
        """
        Set board in GUI
        
        Args:
            board: 9x9 2D list
            is_original: If True, cells are marked as original (read-only)
        """
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
                        self.cells[i][j].config(bg='#c8e6c9', state='readonly')  # Light green for solved
                else:
                    self.cells[i][j].config(bg='white', state='normal')
    
    def generate_puzzle(self):
        """Generate a new random puzzle"""
        self.log_message("\n" + "="*40, 'header')
        self.log_message("Generating puzzle...", 'header')
        
        difficulty = self.difficulty_var.get()
        puzzle = self.solver.generate_puzzle(difficulty)
        
        if puzzle:
            self.clear_board()
            self.set_board(puzzle, is_original=True)
            self.log_message(f"✓ Generated {difficulty} puzzle successfully!", 'success')
            self.log_message(f"Cells filled: {sum(1 for i in range(9) for j in range(9) if puzzle[i][j] != 0)}/81", 'info')
        else:
            messagebox.showerror("Error", "Failed to generate puzzle")
            self.log_message("✗ Failed to generate puzzle", 'error')
    
    def solve_puzzle(self):
        """Solve the current puzzle using AC-3 and backtracking"""
        board = self.get_board()
        
        # Check if board has at least one number
        if all(board[i][j] == 0 for i in range(9) for j in range(9)):
            messagebox.showwarning("Warning", "Please enter a puzzle or generate one first!")
            return
        
        # Validate board first
        is_valid, error_msg = self.solver.validate_board(board)
        if not is_valid:
            messagebox.showerror("Invalid Board", error_msg)
            self.log_message(f"✗ {error_msg}", 'error')
            return
        
        self.log_message("\n" + "="*40, 'header')
        self.log_message("Starting AC-3 Algorithm...", 'header')
        self.log_message("="*40, 'header')
        
        # Update UI
        self.root.update()
        
        # Solve
        solution, solve_time = self.solver.solve_with_ac3(board)
        
        if solution:
            self.set_board(solution, is_original=False)
            
            # Reset original cells to readonly with original color
            for i in range(9):
                for j in range(9):
                    if self.original_board[i][j] != 0:
                        self.cells[i][j].config(bg='#e0e0e0', state='readonly')
            
            # Store domains for display
            self.current_domains = self.solver.domains
            
            # Log success
            self.log_message(f"\n✓ Puzzle solved successfully!", 'success')
            self.log_message(f"Time: {solve_time:.4f} seconds", 'info')
            self.log_message(f"Backtracking iterations: {self.solver.iterations}", 'info')
            self.log_message(f"Arc revisions: {self.solver.arc_revisions}", 'info')
            
            # Update statistics
            self.update_statistics(solve_time, 'Solved')
            
            messagebox.showinfo("Success", f"Puzzle solved in {solve_time:.4f} seconds!\n\n"
                                         f"Iterations: {self.solver.iterations}\n"
                                         f"Arc Revisions: {self.solver.arc_revisions}")
        else:
            self.log_message("\n✗ Puzzle is unsolvable!", 'error')
            self.update_statistics(0, 'Unsolvable')
            messagebox.showerror("Error", "This puzzle has no solution!")
    
    def clear_board(self):
        """Clear the entire board"""
        for i in range(9):
            for j in range(9):
                self.cells[i][j].config(state='normal', bg='white')
                self.cells[i][j].delete(0, tk.END)
        
        self.original_board = [[0 for _ in range(9)] for _ in range(9)]
        self.current_domains = [[[] for _ in range(9)] for _ in range(9)]
        self.log_message("\n✓ Board cleared!", 'info')
        self.update_statistics(0, 'Ready')
    
    def validate_current_board(self):
        """Validate the current board state"""
        board = self.get_board()
        is_valid, error_msg = self.solver.validate_board(board)
        
        if is_valid:
            messagebox.showinfo("Valid", "Board follows all Sudoku constraints!")
            self.log_message(f"✓ {error_msg}", 'success')
        else:
            messagebox.showerror("Invalid", error_msg)
            self.log_message(f"✗ {error_msg}", 'error')
    
    def save_puzzle(self):
        """Save current puzzle to file"""
        board = self.get_board()
        filename = filedialog.asksaveasfilename(defaultextension=".json",
                                                filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if filename:
            with open(filename, 'w') as f:
                json.dump(board, f)
            self.log_message(f"✓ Puzzle saved to {filename}", 'success')
    
    def load_puzzle(self):
        """Load puzzle from file"""
        filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if filename:
            try:
                with open(filename, 'r') as f:
                    board = json.load(f)
                self.clear_board()
                self.set_board(board, is_original=True)
                self.log_message(f"✓ Puzzle loaded from {filename}", 'success')
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load puzzle: {str(e)}")
                self.log_message(f"✗ Failed to load puzzle: {str(e)}", 'error')
    
    def toggle_domains(self):
        """Toggle domain display"""
        if self.show_domains_var.get():
            self.log_message("Domain display enabled - click cells to see domains", 'info')
        else:
            self.log_message("Domain display disabled", 'info')
    
    def update_statistics(self, solve_time, status):
        """
        Update statistics display
        
        Args:
            solve_time: Time taken to solve
            status: Current status string
        """
        stats_text = f"Status: {status}\n\n"
        stats_text += f"Iterations: {self.solver.iterations}\n"
        stats_text += f"Arc Revisions: {self.solver.arc_revisions}\n"
        stats_text += f"Time: {solve_time:.4f}s"
        self.stats_label.config(text=stats_text)
    
    def log_message(self, message, tag='info'):
        """
        Add message to log with optional color tag
        
        Args:
            message: Message string
            tag: Color tag ('header', 'success', 'error', 'info')
        """
        self.log_text.insert(tk.END, message + "\n", tag)
        self.log_text.see(tk.END)
        self.root.update()
    
    def apply_theme(self):
        """Apply custom theme/styling"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('TLabelframe', background='#f0f0f0')
        style.configure('TLabelframe.Label', font=('Arial', 10, 'bold'))


def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = SudokuGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()