import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import math
import cmath
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sympy as sp
import re
import json
import os
from decimal import Decimal, getcontext
from typing import Union, Callable, Dict, List, Optional, Tuple
from enum import Enum, auto
from dataclasses import dataclass
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('AdvancedCalculator')
getcontext().prec = 28
class CalculatorError(Exception):
    pass
class MathError(CalculatorError):
    pass
class InputError(CalculatorError):
    pass
class CalculationMode(Enum):
    STANDARD = auto()
    SCIENTIFIC = auto()
    PROGRAMMER = auto()
    GRAPHING = auto()
    STATISTICS = auto()
class ThemeManager:
    THEMES = {
        'Light': {
            'bg': '#f0f0f0',
            'button_bg': '#e0e0e0',
            'button_active': '#d0d0d0',
            'text': '#000000',
            'operator': '#ff8c00',
            'special': '#4a86e8',
            'display_bg': '#ffffff',
            'highlight_bg': '#e6f3ff'
        },
        'Dark': {
            'bg': '#2d2d2d',
            'button_bg': '#444444',
            'button_active': '#555555',
            'text': '#ffffff',
            'operator': '#ff9500',
            'special': '#64b5f6',
            'display_bg': '#1e1e1e',
            'highlight_bg': '#3d3d3d'
        },
        'Blue': {
            'bg': '#1a237e',
            'button_bg': '#283593',
            'button_active': '#3949ab',
            'text': '#ffffff',
            'operator': '#ff9100',
            'special': '#00bcd4',
            'display_bg': '#0d1642',
            'highlight_bg': '#303f9f'
        },
        'Green': {
            'bg': '#1b5e20',
            'button_bg': '#2e7d32',
            'button_active': '#388e3c',
            'text': '#ffffff',
            'operator': '#ffc107',
            'special': '#4fc3f7',
            'display_bg': '#0d3a12',
            'highlight_bg': '#43a047'
        }
    }
    @staticmethod
    def get_theme(name):
        return ThemeManager.THEMES.get(name, ThemeManager.THEMES['Light'])
@dataclass
class MemoryItem:
    value: float
    expression: str
    timestamp: str
class MemoryManager:
    def __init__(self):
        self.memory: List[MemoryItem] = []
        self.memory_register: float = 0
        self.history: List[str] = []
        self.load_memory()
    def add_to_memory(self, value: float, expression: str) -> None:
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.memory.append(MemoryItem(value, expression, timestamp))
        self.save_memory()
    def clear_memory(self) -> None:
        self.memory = []
        self.save_memory()
    def add_to_history(self, expression: str, result: str) -> None:
        entry = f"{expression} = {result}"
        self.history.append(entry)
    def clear_history(self) -> None:
        self.history = []
    def save_memory(self) -> None:
        try:
            memory_data = {
                'memory_register': self.memory_register,
                'memory_items': [(item.value, item.expression, item.timestamp) for item in self.memory]
            }
            with open('calculator_memory.json', 'w') as f:
                json.dump(memory_data, f)
        except Exception as e:
            logger.error(f"Error saving memory: {e}")
    def load_memory(self) -> None:
        try:
            if os.path.exists('calculator_memory.json'):
                with open('calculator_memory.json', 'r') as f:
                    memory_data = json.load(f)
                    self.memory_register = memory_data.get('memory_register', 0)
                    self.memory = [
                        MemoryItem(value, expr, timestamp) 
                        for value, expr, timestamp in memory_data.get('memory_items', [])
                    ]
        except Exception as e:
            logger.error(f"Error loading memory: {e}")
class CalculatorEngine:
    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.constants = {
            'pi': math.pi,
            'e': math.e,
            'phi': (1 + math.sqrt(5)) / 2,
            'tau': 2 * math.pi,
            'inf': float('inf')
        }
        self.angle_mode = 'radians'
    def evaluate(self, expression: str) -> Union[float, complex]:
        try:
            for name, value in self.constants.items():
                expression = re.sub(r'\b' + name + r'\b', str(value), expression)
            expression = self._handle_special_functions(expression)
            x = sp.symbols('x')
            evaluated = sp.sympify(expression).evalf()
            if isinstance(evaluated, sp.core.numbers.Float):
                return float(evaluated)
            elif isinstance(evaluated, sp.core.numbers.Integer):
                return float(evaluated)
            elif isinstance(evaluated, sp.core.numbers.Rational):
                return float(evaluated)
            elif isinstance(evaluated, sp.core.numbers.ComplexNumber):
                return complex(evaluated)
            else:
                return evaluated
        except Exception as e:
            logger.error(f"Evaluation error: {e}")
            raise MathError(f"Error evaluating expression: {e}")
    def _handle_special_functions(self, expression: str) -> str:
        if self.angle_mode == 'degrees':
            trig_funcs = ['sin', 'cos', 'tan', 'cot', 'sec', 'csc']
            for func in trig_funcs:
                pattern = r'{}\(([^\)]+)\)'.format(func)
                expression = re.sub(pattern, r'{}(\1 * pi/180)'.format(func), expression)
        return expression
    def solve_equation(self, equation: str, variable: str = 'x') -> List[float]:
        try:
            x = sp.symbols(variable)
            if '=' in equation:
                left, right = equation.split('=', 1)
                eq = sp.Eq(sp.sympify(left.strip()), sp.sympify(right.strip()))
                solutions = sp.solve(eq, x)
            else:
                eq = sp.Eq(sp.sympify(equation), 0)
                solutions = sp.solve(eq, x)

            results = []
            for sol in solutions:
                try:
                    results.append(float(sol))
                except:
                    results.append(sol)
            return results
        except Exception as e:
            logger.error(f"Equation solving error: {e}")
            raise MathError(f"Error solving equation: {e}")
    def differentiate(self, expression: str, variable: str = 'x', order: int = 1) -> str:
        try:
            x = sp.symbols(variable)
            expr = sp.sympify(expression)
            result = sp.diff(expr, x, order)
            return str(result)
        except Exception as e:
            logger.error(f"Differentiation error: {e}")
            raise MathError(f"Error differentiating expression: {e}")
    def integrate(self, expression: str, variable: str = 'x', limits: Optional[Tuple[float, float]] = None) -> str:
        try:
            x = sp.symbols(variable)
            expr = sp.sympify(expression)
            if limits is not None:
                lower, upper = limits
                result = sp.integrate(expr, (x, lower, upper))
            else:
                result = sp.integrate(expr, x)
            return str(result)
        except Exception as e:
            logger.error(f"Integration error: {e}")
            raise MathError(f"Error integrating expression: {e}")
class AdvancedCalculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Advanced Calculator - Dev DriizzyyB")
        self.geometry("1200x800")
        self.minsize(800, 600)
        self.engine = CalculatorEngine()
        self.memory_manager = MemoryManager()
        self.current_mode = CalculationMode.STANDARD
        self.current_theme = "Dark"
        self.status_var = tk.StringVar(value="Ready")
        self.apply_theme(self.current_theme)
        self.graph_expressions = []
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self._create_menu()
        self._create_display()
        self._create_button_panels()
        self._create_sidebar()
        self.operation_pressed = False
        self._bind_keyboard_events()
        self.switch_mode(CalculationMode.STANDARD)
        self.center_window()
        self.status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        logger.info("Calculator initialized successfully")
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    def apply_theme(self, theme_name):
        self.current_theme = theme_name
        theme = ThemeManager.get_theme(theme_name)
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('TFrame', background=theme['bg'])
        style.configure('TButton', 
                       background=theme['button_bg'], 
                       foreground=theme['text'],
                       padding=5)
        style.map('TButton',
                 background=[('active', theme['button_active'])])
        style.configure('Operator.TButton', 
                       background=theme['operator'], 
                       foreground=theme['text'])
        style.map('Operator.TButton',
                 background=[('active', theme['operator'])])
        style.configure('Special.TButton', 
                       background=theme['special'], 
                       foreground=theme['text'])
        style.map('Special.TButton',
                 background=[('active', theme['special'])])
        style.configure('TLabel', 
                       background=theme['bg'], 
                       foreground=theme['text'])
        style.configure('TEntry', 
                       fieldbackground=theme['display_bg'], 
                       foreground=theme['text'])
        self.configure(background=theme['bg'])
        for widget in self.winfo_children():
            if isinstance(widget, ttk.Frame) or isinstance(widget, ttk.LabelFrame):
                widget.configure(style='TFrame')
        if hasattr(self, 'display'):
            self.display.configure(background=theme['display_bg'], foreground=theme['text'])
        if hasattr(self, 'result_display'):
            self.result_display.configure(background=theme['display_bg'], foreground=theme['text'])
    def _create_menu(self):
        self.menu_bar = tk.Menu(self)
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="New Calculation", command=self.clear_all, accelerator="Ctrl+N")
        file_menu.add_separator()
        file_menu.add_command(label="Save History", command=self.save_history)
        file_menu.add_command(label="Load History", command=self.load_history)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit, accelerator="Alt+F4")
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        edit_menu.add_command(label="Copy", command=self.copy_result, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste_to_display, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Clear Display", command=self.clear_display, accelerator="Esc")
        edit_menu.add_command(label="Clear All", command=self.clear_all)
        self.menu_bar.add_cascade(label="Edit", menu=edit_menu)
        view_menu = tk.Menu(self.menu_bar, tearoff=0)
        mode_menu = tk.Menu(view_menu, tearoff=0)
        mode_menu.add_command(label="Standard", command=lambda: self.switch_mode(CalculationMode.STANDARD))
        mode_menu.add_command(label="Scientific", command=lambda: self.switch_mode(CalculationMode.SCIENTIFIC))
        mode_menu.add_command(label="Programmer", command=lambda: self.switch_mode(CalculationMode.PROGRAMMER))
        mode_menu.add_command(label="Graphing", command=lambda: self.switch_mode(CalculationMode.GRAPHING))
        mode_menu.add_command(label="Statistics", command=lambda: self.switch_mode(CalculationMode.STATISTICS))
        view_menu.add_cascade(label="Mode", menu=mode_menu)
        theme_menu = tk.Menu(view_menu, tearoff=0)
        for theme in ThemeManager.THEMES:
            theme_menu.add_command(label=theme, command=lambda t=theme: self.apply_theme(t))
        view_menu.add_cascade(label="Theme", menu=theme_menu)
        view_menu.add_separator()
        view_menu.add_command(label="Show History", command=self.toggle_history)
        view_menu.add_command(label="Show Memory", command=self.toggle_memory)
        self.menu_bar.add_cascade(label="View", menu=view_menu)
        tools_menu = tk.Menu(self.menu_bar, tearoff=0)
        tools_menu.add_command(label="Unit Converter", command=self.show_unit_converter)
        tools_menu.add_command(label="Date Calculator", command=self.show_date_calculator)
        tools_menu.add_command(label="Equation Solver", command=self.show_equation_solver)
        self.menu_bar.add_cascade(label="Tools", menu=tools_menu)
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label="Help Topics", command=self.show_help)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self.show_about)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)
        self.config(menu=self.menu_bar)
    def _create_display(self):
        display_frame = ttk.Frame(self.main_frame)
        display_frame.pack(fill=tk.X, padx=5, pady=5)
        self.display = tk.Entry(display_frame, font=("Consolas", 20), bd=5, justify=tk.RIGHT)
        self.display.pack(fill=tk.X, pady=5)
        self.result_display = tk.Entry(display_frame, font=("Consolas", 16), bd=3, justify=tk.RIGHT, state="readonly")
        self.result_display.pack(fill=tk.X, pady=2)
        self.info_var = tk.StringVar()
        self.info_label = ttk.Label(display_frame, textvariable=self.info_var, anchor=tk.E)
        self.info_label.pack(fill=tk.X, pady=2)
    def _create_button_panels(self):
        self.button_container = ttk.Frame(self.main_frame)
        self.button_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.standard_frame = ttk.Frame(self.button_container)
        self.scientific_frame = ttk.Frame(self.button_container)
        self.programmer_frame = ttk.Frame(self.button_container)
        self.graphing_frame = ttk.Frame(self.button_container)
        self.statistics_frame = ttk.Frame(self.button_container)
        self._create_standard_buttons()
        self._create_scientific_buttons()
        self._create_programmer_buttons()
        self._create_graphing_panel()
        self._create_statistics_panel()
    def _create_sidebar(self):
        self.sidebar = ttk.Frame(self.main_frame, width=300)
        self.sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        self.sidebar_tabs = ttk.Notebook(self.sidebar)
        self.sidebar_tabs.pack(fill=tk.BOTH, expand=True)
        self.history_frame = ttk.Frame(self.sidebar_tabs)
        self.sidebar_tabs.add(self.history_frame, text="History")
        self.history_text = scrolledtext.ScrolledText(self.history_frame, wrap=tk.WORD, width=30)
        self.history_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        history_buttons = ttk.Frame(self.history_frame)
        history_buttons.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(history_buttons, text="Clear History", command=self.clear_history).pack(side=tk.LEFT, padx=2)
        ttk.Button(history_buttons, text="Copy Selected", command=self.copy_history_selection).pack(side=tk.LEFT, padx=2)
        self.memory_frame = ttk.Frame(self.sidebar_tabs)
        self.sidebar_tabs.add(self.memory_frame, text="Memory")
        self.memory_text = scrolledtext.ScrolledText(self.memory_frame, wrap=tk.WORD, width=30)
        self.memory_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        memory_buttons = ttk.Frame(self.memory_frame)
        memory_buttons.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(memory_buttons, text="Store (MS)", command=self.memory_store).pack(side=tk.LEFT, padx=2)
        ttk.Button(memory_buttons, text="Recall (MR)", command=self.memory_recall).pack(side=tk.LEFT, padx=2)
        ttk.Button(memory_buttons, text="Clear (MC)", command=self.memory_clear).pack(side=tk.LEFT, padx=2)
        self.sidebar.pack_forget()
    def _create_standard_buttons(self):
        standard_pad = ttk.Frame(self.standard_frame)
        standard_pad.pack(fill=tk.BOTH, expand=True)
        standard_buttons = [
            ('MC', 0, 0, self.memory_clear), ('MR', 0, 1, self.memory_recall), 
            ('MS', 0, 2, self.memory_store), ('M+', 0, 3, self.memory_add), 
            ('M-', 0, 4, self.memory_subtract),
            ('CE', 1, 0, self.clear_entry), ('C', 1, 1, self.clear_all), 
            ('⌫', 1, 2, self.backspace), ('±', 1, 3, self.negate), 
            ('√', 1, 4, lambda: self.insert_function('sqrt')),
            ('7', 2, 0, lambda: self.add_to_display('7')), 
            ('8', 2, 1, lambda: self.add_to_display('8')), 
            ('9', 2, 2, lambda: self.add_to_display('9')), 
            ('÷', 2, 3, lambda: self.add_to_display('/')), 
            ('%', 2, 4, lambda: self.add_to_display('%')),
            ('4', 3, 0, lambda: self.add_to_display('4')), 
            ('5', 3, 1, lambda: self.add_to_display('5')), 
            ('6', 3, 2, lambda: self.add_to_display('6')), 
            ('×', 3, 3, lambda: self.add_to_display('*')), 
            ('1/x', 3, 4, lambda: self.insert_function('1/')),
            ('1', 4, 0, lambda: self.add_to_display('1')), 
            ('2', 4, 1, lambda: self.add_to_display('2')), 
            ('3', 4, 2, lambda: self.add_to_display('3')), 
            ('-', 4, 3, lambda: self.add_to_display('-')), 
            ('=', 4, 4, self.calculate),
            ('0', 5, 0, lambda: self.add_to_display('0')), 
            ('.', 5, 2, lambda: self.add_to_display('.')), 
            ('+', 5, 3, lambda: self.add_to_display('+')), 
        ]
        for (text, row, col, command) in standard_buttons:
            button_style = 'TButton'
            if text in ['+', '-', '×', '÷', '=']:
                button_style = 'Operator.TButton'
            elif text in ['MC', 'MR', 'MS', 'M+', 'M-', 'CE', 'C', '√', '%', '1/x', '±']:
                button_style = 'Special.TButton'
            if text == '0':
                btn = ttk.Button(standard_pad, text=text, command=command, style=button_style)
                btn.grid(row=row, column=col, columnspan=2, padx=2, pady=2, sticky='nsew')
            else:
                btn = ttk.Button(standard_pad, text=text, command=command, style=button_style)
                btn.grid(row=row, column=col, padx=2, pady=2, sticky='nsew')
        for i in range(6):
            standard_pad.rowconfigure(i, weight=1)
        for i in range(5):
            standard_pad.columnconfigure(i, weight=1)
    def _create_scientific_buttons(self):
        scientific_pad = ttk.Frame(self.scientific_frame)
        scientific_pad.pack(fill=tk.BOTH, expand=True)
        scientific_top_buttons = [
            ('Deg', 0, 0, self.toggle_angle_mode), ('Hyp', 0, 1, self.toggle_hyperbolic),
            ('F-E', 0, 2, self.toggle_scientific_notation), ('MC', 0, 3, self.memory_clear), 
            ('MR', 0, 4, self.memory_recall), ('MS', 0, 5, self.memory_store), 
            ('M+', 0, 6, self.memory_add), ('M-', 0, 7, self.memory_subtract)
        ]
        scientific_func_buttons = [
            ('2nd', 1, 0, self.toggle_second_function), ('π', 1, 1, lambda: self.add_to_display('pi')),
            ('e', 1, 2, lambda: self.add_to_display('e')), ('C', 1, 3, self.clear_all),
            ('⌫', 1, 4, self.backspace), ('x²', 1, 5, lambda: self.add_to_display('^2')),
            ('1/x', 1, 6, lambda: self.insert_function('1/')), ('|x|', 1, 7, lambda: self.insert_function('abs'))
        ]
        scientific_trig_buttons = [
            ('x^y', 2, 0, lambda: self.add_to_display('^')), ('sin', 2, 1, lambda: self.insert_function('sin')),
            ('cos', 2, 2, lambda: self.insert_function('cos')), ('tan', 2, 3, lambda: self.insert_function('tan')),
            ('√', 2, 4, lambda: self.insert_function('sqrt')), ('∛', 2, 5, lambda: self.insert_function('cbrt')),
            ('(', 2, 6, lambda: self.add_to_display('(')), (')', 2, 7, lambda: self.add_to_display(')'))
        ]
        scientific_main_buttons = [
            ('7', 3, 4, lambda: self.add_to_display('7')), 
            ('8', 3, 5, lambda: self.add_to_display('8')), 
            ('9', 3, 6, lambda: self.add_to_display('9')), 
            ('÷', 3, 7, lambda: self.add_to_display('/')),
            ('ln', 4, 0, lambda: self.insert_function('log')), 
            ('log₁₀', 4, 1, lambda: self.insert_function('log10')),
            ('log₂', 4, 2, lambda: self.insert_function('log2')),
            ('n!', 4, 3, lambda: self.insert_function('factorial')),
            ('4', 4, 4, lambda: self.add_to_display('4')), 
            ('5', 4, 5, lambda: self.add_to_display('5')), 
            ('6', 4, 6, lambda: self.add_to_display('6')), 
            ('×', 4, 7, lambda: self.add_to_display('*')),
            ('sinh', 5, 0, lambda: self.insert_function('sinh')),
            ('cosh', 5, 1, lambda: self.insert_function('cosh')),
            ('tanh', 5, 2, lambda: self.insert_function('tanh')),
            ('Mod', 5, 3, lambda: self.add_to_display('%')),
            ('1', 5, 4, lambda: self.add_to_display('1')), 
            ('2', 5, 5, lambda: self.add_to_display('2')), 
            ('3', 5, 6, lambda: self.add_to_display('3')), 
            ('-', 5, 7, lambda: self.add_to_display('-')),
            ('Rand', 6, 0, lambda: self.insert_function('random')),
            ('EE', 6, 1, lambda: self.add_to_display('E')),
            ('Rad', 6, 2, self.toggle_angle_mode),
            ('±', 6, 3, self.negate),
            ('0', 6, 4, lambda: self.add_to_display('0')), 
            ('.', 6, 5, lambda: self.add_to_display('.')),
            ('=', 6, 6, self.calculate),
            ('+', 6, 7, lambda: self.add_to_display('+'))
        ]
        all_buttons = scientific_top_buttons + scientific_func_buttons + scientific_trig_buttons + scientific_main_buttons
        for (text, row, col, command) in all_buttons:
            button_style = 'TButton'
            if text in ['+', '-', '×', '÷', '=']:
                button_style = 'Operator.TButton'
            elif text not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.', '(', ')']:
                button_style = 'Special.TButton'
            btn = ttk.Button(scientific_pad, text=text, command=command, style=button_style)
            btn.grid(row=row, column=col, padx=2, pady=2, sticky='nsew')
        for i in range(7):
            scientific_pad.rowconfigure(i, weight=1)
        for i in range(8):
            scientific_pad.columnconfigure(i, weight=1)
    def _create_programmer_buttons(self):
        programmer_pad = ttk.Frame(self.programmer_frame)
        programmer_pad.pack(fill=tk.BOTH, expand=True)
        number_system_frame = ttk.LabelFrame(programmer_pad, text="Number System")
        number_system_frame.grid(row=0, column=0, columnspan=8, padx=5, pady=5, sticky='ew')
        self.number_system = tk.StringVar(value="DEC")
        systems = [("HEX", "hexadecimal"), ("DEC", "decimal"), 
                  ("OCT", "octal"), ("BIN", "binary")]
        for i, (text, system) in enumerate(systems):
            rb = ttk.Radiobutton(number_system_frame, text=text, value=text, 
                                variable=self.number_system, 
                                command=lambda s=system: self.change_number_system(s))
            rb.grid(row=0, column=i, padx=10, pady=5)
        number_system_frame.columnconfigure(0, weight=1)
        number_system_frame.columnconfigure(1, weight=1)
        number_system_frame.columnconfigure(2, weight=1)
        number_system_frame.columnconfigure(3, weight=1)
        word_size_frame = ttk.LabelFrame(programmer_pad, text="Word Size")
        word_size_frame.grid(row=1, column=0, columnspan=8, padx=5, pady=5, sticky='ew')
        self.word_size = tk.StringVar(value="QWORD")
        sizes = [("QWORD", 64), ("DWORD", 32), ("WORD", 16), ("BYTE", 8)]
        for i, (text, bits) in enumerate(sizes):
            rb = ttk.Radiobutton(word_size_frame, text=f"{text} ({bits}-bit)", 
                                value=text, variable=self.word_size, 
                                command=lambda b=bits: self.change_word_size(b))
            rb.grid(row=0, column=i, padx=10, pady=5)
        word_size_frame.columnconfigure(0, weight=1)
        word_size_frame.columnconfigure(1, weight=1)
        word_size_frame.columnconfigure(2, weight=1)
        word_size_frame.columnconfigure(3, weight=1)
        bit_buttons = [
            ('AND', 2, 0, lambda: self.add_to_display(' & ')),
            ('OR', 2, 1, lambda: self.add_to_display(' | ')),
            ('XOR', 2, 2, lambda: self.add_to_display(' ^ ')),
            ('NOT', 2, 3, lambda: self.insert_function('~')),
            ('<<', 2, 4, lambda: self.add_to_display(' << ')),
            ('>>', 2, 5, lambda: self.add_to_display(' >> ')),
            ('C', 2, 6, self.clear_all),
            ('⌫', 2, 7, self.backspace)
        ]
        hex_buttons = [
            ('A', 3, 0, lambda: self.add_to_display('A')),
            ('B', 3, 1, lambda: self.add_to_display('B')),
            ('C', 3, 2, lambda: self.add_to_display('C')),
            ('D', 3, 3, lambda: self.add_to_display('D')),
            ('E', 3, 4, lambda: self.add_to_display('E')),
            ('F', 3, 5, lambda: self.add_to_display('F')),
            ('(', 3, 6, lambda: self.add_to_display('(')),
            (')', 3, 7, lambda: self.add_to_display(')'))
        ]
        main_buttons = [
            ('Mod', 4, 0, lambda: self.add_to_display(' % ')),
            ('CE', 4, 1, self.clear_entry),
            ('7', 4, 4, lambda: self.add_to_display('7')),
            ('8', 4, 5, lambda: self.add_to_display('8')),
            ('9', 4, 6, lambda: self.add_to_display('9')),
            ('÷', 4, 7, lambda: self.add_to_display(' / ')),
            ('Lsh', 5, 0, lambda: self.add_to_display(' << ')),
            ('Rsh', 5, 1, lambda: self.add_to_display(' >> ')),
            ('4', 5, 4, lambda: self.add_to_display('4')),
            ('5', 5, 5, lambda: self.add_to_display('5')),
            ('6', 5, 6, lambda: self.add_to_display('6')),
            ('×', 5, 7, lambda: self.add_to_display(' * ')),
            ('Or', 6, 0, lambda: self.add_to_display(' | ')),
            ('Xor', 6, 1, lambda: self.add_to_display(' ^ ')),
            ('1', 6, 4, lambda: self.add_to_display('1')),
            ('2', 6, 5, lambda: self.add_to_display('2')),
            ('3', 6, 6, lambda: self.add_to_display('3')),
            ('-', 6, 7, lambda: self.add_to_display(' - ')),
            ('And', 7, 0, lambda: self.add_to_display(' & ')),
            ('Not', 7, 1, lambda: self.insert_function('~')),
            ('0', 7, 4, lambda: self.add_to_display('0')),
            ('=', 7, 6, self.calculate),
            ('+', 7, 7, lambda: self.add_to_display(' + '))
        ]
        all_buttons = bit_buttons + hex_buttons + main_buttons
        for (text, row, col, command) in all_buttons:
            button_style = 'TButton'
            if text in ['+', '-', '×', '÷', '=']:
                button_style = 'Operator.TButton'
            elif text not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '(', ')']:
                button_style = 'Special.TButton'
            btn = ttk.Button(programmer_pad, text=text, command=command, style=button_style)
            btn.grid(row=row, column=col, padx=2, pady=2, sticky='nsew')
        for i in range(8):
            programmer_pad.rowconfigure(i, weight=1)
        for i in range(8):
            programmer_pad.columnconfigure(i, weight=1)
    def _create_graphing_panel(self):
        graphing_frame = ttk.Frame(self.graphing_frame)
        graphing_frame.pack(fill=tk.BOTH, expand=True)
        controls_frame = ttk.LabelFrame(graphing_frame, text="Graph Controls")
        controls_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5, pady=5)
        ttk.Label(controls_frame, text="Expressions:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.expressions_frame = ttk.Frame(controls_frame)
        self.expressions_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        self._add_expression_row()
        ttk.Button(controls_frame, text="+ Add Expression", 
                  command=self._add_expression_row).grid(row=2, column=0, sticky='ew', padx=5, pady=5)
        range_frame = ttk.LabelFrame(controls_frame, text="Graph Range")
        range_frame.grid(row=3, column=0, sticky='ew', padx=5, pady=5)
        ttk.Label(range_frame, text="X min:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.x_min = ttk.Entry(range_frame, width=8)
        self.x_min.insert(0, "-10")
        self.x_min.grid(row=0, column=1, sticky='w', padx=5, pady=2)
        ttk.Label(range_frame, text="X max:").grid(row=0, column=2, sticky='w', padx=5, pady=2)
        self.x_max = ttk.Entry(range_frame, width=8)
        self.x_max.insert(0, "10")
        self.x_max.grid(row=0, column=3, sticky='w', padx=5, pady=2)
        ttk.Label(range_frame, text="Y min:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.y_min = ttk.Entry(range_frame, width=8)
        self.y_min.insert(0, "-10")
        self.y_min.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        ttk.Label(range_frame, text="Y max:").grid(row=1, column=2, sticky='w', padx=5, pady=2)
        self.y_max = ttk.Entry(range_frame, width=8)
        self.y_max.insert(0, "10")
        self.y_max.grid(row=1, column=3, sticky='w', padx=5, pady=2)
        ttk.Button(controls_frame, text="Plot Graph", 
                  command=self.plot_graph).grid(row=4, column=0, sticky='ew', padx=5, pady=5)
        ttk.Button(controls_frame, text="Clear Graph", 
                  command=self.clear_graph).grid(row=5, column=0, sticky='ew', padx=5, pady=5)
        self.graph_frame = ttk.LabelFrame(graphing_frame, text="Graph")
        self.graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.fig = plt.Figure(figsize=(6, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('y')
        self.ax.grid(True)
        self.canvas = FigureCanvasTkAgg(self.fig, self.graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        controls_frame.config(width=300)
    def _add_expression_row(self):
        row_frame = ttk.Frame(self.expressions_frame)
        row_frame.pack(fill=tk.X, pady=2)
        expr_var = tk.StringVar()
        expr_entry = ttk.Entry(row_frame, textvariable=expr_var, width=20)
        expr_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        color_var = tk.StringVar(value="blue")
        colors = ["blue", "red", "green", "purple", "orange", "cyan", "magenta", "black"]
        color_menu = ttk.Combobox(row_frame, textvariable=color_var, values=colors, width=8)
        color_menu.pack(side=tk.LEFT, padx=2)
        remove_btn = ttk.Button(row_frame, text="✕", width=3, 
                              command=lambda: self._remove_expression_row(row_frame))
        remove_btn.pack(side=tk.LEFT, padx=2)
        self.graph_expressions.append((expr_var, color_var))
    def _remove_expression_row(self, row_frame):
        idx = list(self.expressions_frame.children.values()).index(row_frame)
        row_frame.destroy()
        if idx < len(self.graph_expressions):
            del self.graph_expressions[idx]
    def _create_statistics_panel(self):
        stats_frame = ttk.Frame(self.statistics_frame)
        stats_frame.pack(fill=tk.BOTH, expand=True)
        input_frame = ttk.LabelFrame(stats_frame, text="Data Input")
        input_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        ttk.Label(input_frame, text="Enter data (comma or space separated):").pack(anchor='w', padx=5, pady=5)
        self.data_entry = scrolledtext.ScrolledText(input_frame, height=8)
        self.data_entry.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        data_buttons = ttk.Frame(input_frame)
        data_buttons.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(data_buttons, text="Calculate", 
                  command=self.calculate_statistics).pack(side=tk.LEFT, padx=2)
        ttk.Button(data_buttons, text="Clear", 
                  command=lambda: self.data_entry.delete(1.0, tk.END)).pack(side=tk.LEFT, padx=2)
        ttk.Button(data_buttons, text="Sample Data", 
                  command=self.load_sample_data).pack(side=tk.LEFT, padx=2)
        results_frame = ttk.LabelFrame(stats_frame, text="Statistics Results")
        results_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.stats_results = scrolledtext.ScrolledText(results_frame, height=15, width=40)
        self.stats_results.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.stats_results.config(state=tk.DISABLED)
        graph_options = ttk.LabelFrame(results_frame, text="Visualization")
        graph_options.pack(fill=tk.X, padx=5, pady=5)
        self.graph_type = tk.StringVar(value="histogram")
        graph_types = [("Histogram", "histogram"), ("Box Plot", "boxplot"), 
                      ("Scatter Plot", "scatter"), ("Normal Probability", "probplot")]
        for i, (text, value) in enumerate(graph_types):
            ttk.Radiobutton(graph_options, text=text, value=value, 
                           variable=self.graph_type).grid(row=i//2, column=i%2, sticky='w', padx=5, pady=2)
        ttk.Button(graph_options, text="Generate Plot", 
                  command=self.generate_stats_plot).grid(row=2, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
    def _bind_keyboard_events(self):
        self.bind('<Return>', lambda event: self.calculate())
        self.bind('<KP_Enter>', lambda event: self.calculate())
        self.bind('<Escape>', lambda event: self.clear_display())
        self.bind('<BackSpace>', lambda event: self.backspace())
        self.bind('<Delete>', lambda event: self.clear_entry())
        for i in range(10):
            self.bind(str(i), lambda event, digit=i: self.add_to_display(str(digit)))
            self.bind(f'<KP_{i}>', lambda event, digit=i: self.add_to_display(str(digit)))
        self.bind('+', lambda event: self.add_to_display('+'))
        self.bind('<KP_Add>', lambda event: self.add_to_display('+'))
        self.bind('-', lambda event: self.add_to_display('-'))
        self.bind('<KP_Subtract>', lambda event: self.add_to_display('-'))
        self.bind('*', lambda event: self.add_to_display('*'))
        self.bind('<KP_Multiply>', lambda event: self.add_to_display('*'))
        self.bind('/', lambda event: self.add_to_display('/'))
        self.bind('<KP_Divide>', lambda event: self.add_to_display('/'))
        self.bind('.', lambda event: self.add_to_display('.'))
        self.bind('<KP_Decimal>', lambda event: self.add_to_display('.'))
        self.bind('(', lambda event: self.add_to_display('('))
        self.bind(')', lambda event: self.add_to_display(')'))
        self.bind('<Control-c>', lambda event: self.copy_result())
        self.bind('<Control-v>', lambda event: self.paste_to_display())
        self.bind('<Control-n>', lambda event: self.clear_all())
    def switch_mode(self, mode):
        self.standard_frame.pack_forget()
        self.scientific_frame.pack_forget()
        self.programmer_frame.pack_forget()
        self.graphing_frame.pack_forget()
        self.statistics_frame.pack_forget()
        if mode == CalculationMode.STANDARD:
            self.standard_frame.pack(fill=tk.BOTH, expand=True)
            self.current_mode = CalculationMode.STANDARD
            self.info_var.set("Standard Mode")
        elif mode == CalculationMode.SCIENTIFIC:
            self.scientific_frame.pack(fill=tk.BOTH, expand=True)
            self.current_mode = CalculationMode.SCIENTIFIC
            self.info_var.set("Scientific Mode")
        elif mode == CalculationMode.PROGRAMMER:
            self.programmer_frame.pack(fill=tk.BOTH, expand=True)
            self.current_mode = CalculationMode.PROGRAMMER
            self.info_var.set("Programmer Mode")
        elif mode == CalculationMode.GRAPHING:
            self.graphing_frame.pack(fill=tk.BOTH, expand=True)
            self.current_mode = CalculationMode.GRAPHING
            self.info_var.set("Graphing Mode")
        elif mode == CalculationMode.STATISTICS:
            self.statistics_frame.pack(fill=tk.BOTH, expand=True)
            self.current_mode = CalculationMode.STATISTICS
            self.info_var.set("Statistics Mode")
        self.status_var.set(f"Switched to {mode.name} Mode")
    def add_to_display(self, text):
        current_text = self.display.get()
        cursor_position = self.display.index(tk.INSERT)
        self.operation_pressed = text in ['+', '-', '*', '/', '^', '%']
        new_text = current_text[:cursor_position] + text + current_text[cursor_position:]
        self.display.delete(0, tk.END)
        self.display.insert(0, new_text)
        self.display.icursor(cursor_position + len(text))
        self.evaluate_as_you_type()
    def insert_function(self, func_name):
        current_text = self.display.get()
        cursor_position = self.display.index(tk.INSERT)
        try:
            selection = self.display.selection_get()
            start = self.display.index(tk.SEL_FIRST)
            end = self.display.index(tk.SEL_LAST)
            current_text = current_text[:start] + current_text[end:]
            cursor_position = start
            if func_name.endswith('/'):
                new_text = current_text[:cursor_position] + func_name + f"({selection})" + current_text[cursor_position:]
            else:
                new_text = current_text[:cursor_position] + f"{func_name}({selection})" + current_text[cursor_position:]
        except tk.TclError:
            if func_name.endswith('/'):
                new_text = current_text[:cursor_position] + func_name + "()" + current_text[cursor_position:]
                cursor_position = cursor_position + len(func_name) + 1
            else:
                new_text = current_text[:cursor_position] + f"{func_name}()" + current_text[cursor_position:]
                cursor_position = cursor_position + len(func_name) + 1
        self.display.delete(0, tk.END)
        self.display.insert(0, new_text)
        self.display.icursor(cursor_position)
        self.evaluate_as_you_type()
    def evaluate_as_you_type(self):
        expression = self.display.get().strip()
        if not expression:
            self.result_display.config(state=tk.NORMAL)
            self.result_display.delete(0, tk.END)
            self.result_display.config(state="readonly")
            return
        try:
            if expression[-1] in ['+', '-', '*', '/', '^', '(', '%']:
                return
            result = self.engine.evaluate(expression)
            self.result_display.config(state=tk.NORMAL)
            self.result_display.delete(0, tk.END)
            if isinstance(result, complex):
                self.result_display.insert(0, str(result))
            elif result == int(result):
                self.result_display.insert(0, str(int(result)))
            else:
                self.result_display.insert(0, str(result))
            self.result_display.config(state="readonly")
        except:
            self.result_display.config(state=tk.NORMAL)
            self.result_display.delete(0, tk.END)
            self.result_display.config(state="readonly")
    def calculate(self):
        expression = self.display.get()
        if not expression:
            return
        try:
            if self.current_mode == CalculationMode.PROGRAMMER:
                safe_expr = re.sub(r'[^0-9A-Fa-f+\-*/&|^~%<>()\s]', '', expression)
                result = eval(safe_expr)
                number_system = self.number_system.get()
                if number_system == "HEX":
                    result_str = hex(int(result))
                elif number_system == "OCT":
                    result_str = oct(int(result))
                elif number_system == "BIN":
                    result_str = bin(int(result))
                else:
                    result_str = str(int(result))
            else:
                result = self.engine.evaluate(expression)
                if isinstance(result, complex):
                    result_str = str(result)
                elif result == int(result):
                    result_str = str(int(result))
                else:
                    result_str = str(result)
            self.result_display.config(state=tk.NORMAL)
            self.result_display.delete(0, tk.END)
            self.result_display.insert(0, result_str)
            self.result_display.config(state="readonly")
            self.memory_manager.add_to_history(expression, result_str)
            self.update_history_display()
            self.status_var.set("Calculation complete")
        except Exception as e:
            self.result_display.config(state=tk.NORMAL)
            self.result_display.delete(0, tk.END)
            self.result_display.insert(0, f"Error: {str(e)}")
            self.result_display.config(state="readonly")
            self.status_var.set(f"Error: {str(e)}")
            logger.error(f"Calculation error: {e}")
    def clear_display(self):
        self.display.delete(0, tk.END)
        self.result_display.config(state=tk.NORMAL)
        self.result_display.delete(0, tk.END)
        self.result_display.config(state="readonly")
        self.status_var.set("Display cleared")
    def clear_entry(self):
        self.display.delete(0, tk.END)
        self.status_var.set("Entry cleared")
    def clear_all(self):
        self.display.delete(0, tk.END)
        self.result_display.config(state=tk.NORMAL)
        self.result_display.delete(0, tk.END)
        self.result_display.config(state="readonly")
        self.info_var.set(f"{self.current_mode.name} Mode")
        self.status_var.set("Calculator reset")
    def backspace(self):
        current_text = self.display.get()
        cursor_position = self.display.index(tk.INSERT)
        if cursor_position > 0:
            new_text = current_text[:cursor_position-1] + current_text[cursor_position:]
            self.display.delete(0, tk.END)
            self.display.insert(0, new_text)
            self.display.icursor(cursor_position - 1)
            self.evaluate_as_you_type()
    def negate(self):
        current_text = self.display.get()
        cursor_position = self.display.index(tk.INSERT)
        try:
            selection = self.display.selection_get()
            start = self.display.index(tk.SEL_FIRST)
            end = self.display.index(tk.SEL_LAST)
            try:
                value = float(selection)
                negated = -value
                if negated == int(negated):
                    negated_text = str(int(negated))
                else:
                    negated_text = str(negated)
                new_text = current_text[:start] + negated_text + current_text[end:]
                new_cursor = start + len(negated_text)
            except ValueError:
                new_text = current_text[:start] + f"-({selection})" + current_text[end:]
                new_cursor = start + len(f"-({selection})")
            self.display.delete(0, tk.END)
            self.display.insert(0, new_text)
            self.display.icursor(new_cursor)
        except tk.TclError:
            if current_text and current_text[0] == '-':
                self.display.delete(0, 1)
            else:
                self.display.insert(0, '-')
        self.evaluate_as_you_type()
    def memory_store(self):
        try:
            result_text = self.result_display.get()
            if result_text:
                value = float(result_text)
                expression = self.display.get()
                self.memory_manager.add_to_memory(value, expression)
                self.memory_manager.memory_register = value
                self.update_memory_display()
                self.status_var.set(f"Value {value} stored in memory")
        except Exception as e:
            self.status_var.set(f"Error storing in memory: {str(e)}")
    def memory_recall(self):
        try:
            value = self.memory_manager.memory_register
            current_text = self.display.get()
            cursor_position = self.display.index(tk.INSERT)
            if value == int(value):
                insert_text = str(int(value))
            else:
                insert_text = str(value)
            new_text = current_text[:cursor_position] + insert_text + current_text[cursor_position:]
            self.display.delete(0, tk.END)
            self.display.insert(0, new_text)
            self.display.icursor(cursor_position + len(insert_text))
            self.status_var.set(f"Recalled value {value} from memory")
            self.evaluate_as_you_type()
        except Exception as e:
            self.status_var.set(f"Error recalling from memory: {str(e)}")
    def memory_add(self):
        try:
            result_text = self.result_display.get()
            if result_text:
                value = float(result_text)
                self.memory_manager.memory_register += value
                self.update_memory_display()
                self.status_var.set(f"Added {value} to memory")
        except Exception as e:
            self.status_var.set(f"Error adding to memory: {str(e)}")
    def memory_subtract(self):
        try:
            result_text = self.result_display.get()
            if result_text:
                value = float(result_text)
                self.memory_manager.memory_register -= value
                self.update_memory_display()
                self.status_var.set(f"Subtracted {value} from memory")
        except Exception as e:
            self.status_var.set(f"Error subtracting from memory: {str(e)}")
    def memory_clear(self):
        try:
            self.memory_manager.memory_register = 0
            self.memory_manager.clear_memory()
            self.update_memory_display()
            self.status_var.set("Memory cleared")
        except Exception as e:
            self.status_var.set(f"Error clearing memory: {str(e)}")
    def update_memory_display(self):
        if hasattr(self, 'memory_text'):
            self.memory_text.config(state=tk.NORMAL)
            self.memory_text.delete(1.0, tk.END)
            value = self.memory_manager.memory_register
            if value == int(value):
                value_str = str(int(value))
            else:
                value_str = str(value)
            self.memory_text.insert(tk.END, f"Current Memory: {value_str}\n\n")
            if self.memory_manager.memory:
                self.memory_text.insert(tk.END, "Memory History:\n")
                for item in reversed(self.memory_manager.memory):
                    if item.value == int(item.value):
                        value_str = str(int(item.value))
                    else:
                        value_str = str(item.value)
                    self.memory_text.insert(tk.END, f"{item.timestamp}\n{item.expression} = {value_str}\n\n")
            self.memory_text.config(state=tk.DISABLED)
    def update_history_display(self):
        if hasattr(self, 'history_text'):
            self.history_text.config(state=tk.NORMAL)
            self.history_text.delete(1.0, tk.END)
            if self.memory_manager.history:
                for entry in reversed(self.memory_manager.history):
                    self.history_text.insert(tk.END, f"{entry}\n\n")
            self.history_text.config(state=tk.DISABLED)
    def clear_history(self):
        self.memory_manager.clear_history()
        self.update_history_display()
        self.status_var.set("History cleared")
    def copy_history_selection(self):
        try:
            selected_text = self.history_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(selected_text)
            self.status_var.set("Selection copied to clipboard")
        except tk.TclError:
            self.status_var.set("No text selected")
    def copy_result(self):
        result = self.result_display.get()
        if result:
            self.clipboard_clear()
            self.clipboard_append(result)
            self.status_var.set("Result copied to clipboard")
    def paste_to_display(self):
        try:
            clipboard_content = self.clipboard_get()
            current_text = self.display.get()
            cursor_position = self.display.index(tk.INSERT)
            new_text = current_text[:cursor_position] + clipboard_content + current_text[cursor_position:]
            self.display.delete(0, tk.END)
            self.display.insert(0, new_text)
            self.display.icursor(cursor_position + len(clipboard_content))
            self.status_var.set("Pasted from clipboard")
            self.evaluate_as_you_type()
        except Exception as e:
            self.status_var.set(f"Error pasting: {str(e)}")
    def toggle_history(self):
        if self.sidebar.winfo_ismapped():
            if self.sidebar_tabs.index(self.sidebar_tabs.select()) == 0:
                self.sidebar.pack_forget()
            else:
                self.sidebar_tabs.select(0)
        else:
            self.sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
            self.sidebar_tabs.select(0)
    def toggle_memory(self):
        if self.sidebar.winfo_ismapped():
            if self.sidebar_tabs.index(self.sidebar_tabs.select()) == 1:
                self.sidebar.pack_forget()
            else:
                self.sidebar_tabs.select(1)
        else:
            self.sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
            self.sidebar_tabs.select(1)
    def toggle_angle_mode(self):
        if self.engine.angle_mode == 'radians':
            self.engine.angle_mode = 'degrees'
            self.info_var.set("Angle Mode: Degrees")
        else:
            self.engine.angle_mode = 'radians'
            self.info_var.set("Angle Mode: Radians")
    def toggle_hyperbolic(self):
        self.status_var.set("Hyperbolic functions toggled")
    def toggle_scientific_notation(self):
        self.status_var.set("Scientific notation toggled")
    def toggle_second_function(self):
        self.status_var.set("Secondary functions toggled")
    def change_number_system(self, system):
        self.status_var.set(f"Number system changed to {system}")
        try:
            result_text = self.result_display.get()
            if result_text and result_text != '0':
                if 'x' in result_text:
                    value = int(result_text, 16)
                elif 'o' in result_text:
                    value = int(result_text, 8)
                elif 'b' in result_text:
                    value = int(result_text, 2)
                else:
                    value = int(float(result_text))
                self.result_display.config(state=tk.NORMAL)
                self.result_display.delete(0, tk.END)
                if system == 'hexadecimal':
                    self.result_display.insert(0, hex(value))
                elif system == 'octal':
                    self.result_display.insert(0, oct(value))
                elif system == 'binary':
                    self.result_display.insert(0, bin(value))
                else:  # decimal
                    self.result_display.insert(0, str(value))
                self.result_display.config(state="readonly")
        except Exception as e:
            logger.debug(f"Error converting number system: {e}")
    def change_word_size(self, bits):
        self.status_var.set(f"Word size changed to {bits}-bit")
    def plot_graph(self):
        try:
            self.ax.clear()
            x_min = float(self.x_min.get())
            x_max = float(self.x_max.get())
            y_min = float(self.y_min.get())
            y_max = float(self.y_max.get())
            x = np.linspace(x_min, x_max, 1000)
            legend_entries = []
            for expr_var, color_var in self.graph_expressions:
                expr = expr_var.get().strip()
                color = color_var.get()
                if expr:
                    expr_with_np = expr.replace('x', 'x_vals')
                    namespace = {
                        'x_vals': x,
                        'sin': np.sin,
                        'cos': np.cos,
                        'tan': np.tan,
                        'exp': np.exp,
                        'log': np.log,
                        'log10': np.log10,
                        'sqrt': np.sqrt,
                        'abs': np.abs,
                        'pi': np.pi,
                        'e': np.e
                    }
                    y = eval(expr_with_np, namespace)
                    self.ax.plot(x, y, color=color, label=expr)
                    legend_entries.append(expr)
            self.ax.set_xlim(x_min, x_max)
            self.ax.set_ylim(y_min, y_max)
            self.ax.set_xlabel('x')
            self.ax.set_ylabel('y')
            self.ax.grid(True)
            if legend_entries:
                self.ax.legend()
            self.canvas.draw()
            self.status_var.set("Graph plotted successfully")
        except Exception as e:
            messagebox.showerror("Plotting Error", f"Error plotting graph: {str(e)}")
            self.status_var.set(f"Error plotting graph: {str(e)}")
            logger.error(f"Plotting error: {e}")
    def clear_graph(self):
        self.ax.clear()
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('y')
        self.ax.grid(True)
        self.canvas.draw()
        self.status_var.set("Graph cleared")
    def parse_data(self):
        data_text = self.data_entry.get(1.0, tk.END).strip()
        if ',' in data_text:
            data_points = data_text.split(',')
        else:
            data_points = data_text.split()
        try:
            data = [float(x.strip()) for x in data_points if x.strip()]
            return data
        except ValueError as e:
            messagebox.showerror("Data Error", f"Error parsing data: {str(e)}")
            return []
    def calculate_statistics(self):
        data = self.parse_data()
        if not data:
            return
        try:
            count = len(data)
            mean = np.mean(data)
            median = np.median(data)
            std_dev = np.std(data)
            variance = np.var(data)
            data_min = np.min(data)
            data_max = np.max(data)
            data_range = data_max - data_min
            data_sum = np.sum(data)
            if count > 1:
                sorted_data = sorted(data)
                q1 = np.percentile(data, 25)
                q3 = np.percentile(data, 75)
                iqr = q3 - q1
                skewness = float(sp.skew(data))
                kurtosis = float(sp.kurtosis(data))
            else:
                q1 = q3 = iqr = skewness = kurtosis = float('nan')
            self.stats_results.config(state=tk.NORMAL)
            self.stats_results.delete(1.0, tk.END)
            results = f"""Data Statistics Summary:
Count: {count}
Sum: {data_sum:.6g}
Minimum: {data_min:.6g}
Maximum: {data_max:.6g}
Range: {data_range:.6g}

Mean: {mean:.6g}
Median: {median:.6g}
Standard Deviation: {std_dev:.6g}
Variance: {variance:.6g}

Quartile 1 (Q1): {q1:.6g}
Quartile 3 (Q3): {q3:.6g}
Interquartile Range: {iqr:.6g}

Skewness: {skewness:.6g}
Kurtosis: {kurtosis:.6g}
"""
            self.stats_results.insert(tk.END, results)
            self.stats_results.config(state=tk.DISABLED)
            self.status_var.set("Statistics calculated successfully")
        except Exception as e:
            messagebox.showerror("Statistics Error", f"Error calculating statistics: {str(e)}")
            self.status_var.set(f"Error calculating statistics: {str(e)}")
            logger.error(f"Statistics calculation error: {e}")
    def generate_stats_plot(self):
        data = self.parse_data()
        if not data:
            return
        try:
            plot_window = tk.Toplevel(self)
            plot_window.title("Statistical Plot")
            plot_window.geometry("800x600")
            fig = plt.Figure(figsize=(8, 6), dpi=100)
            ax = fig.add_subplot(111)
            plot_type = self.graph_type.get()
            if plot_type == "histogram":
                ax.hist(data, bins='auto', alpha=0.7, color='blue', edgecolor='black')
                ax.set_title("Histogram")
                ax.set_xlabel("Value")
                ax.set_ylabel("Frequency")
                ax.axvline(np.mean(data), color='r', linestyle='--', label=f"Mean: {np.mean(data):.2f}")
                ax.axvline(np.median(data), color='g', linestyle=':', label=f"Median: {np.median(data):.2f}")
                ax.legend()
            elif plot_type == "boxplot":
                ax.boxplot(data, vert=False, patch_artist=True)
                ax.set_title("Box Plot")
                ax.set_xlabel("Value")
                ax.set_yticklabels(["Data"])
            elif plot_type == "scatter":
                indices = np.arange(len(data))
                ax.scatter(indices, data, alpha=0.7, color='blue', edgecolor='black')
                ax.set_title("Scatter Plot")
                ax.set_xlabel("Index")
                ax.set_ylabel("Value")
            elif plot_type == "probplot":
                import scipy.stats as stats
                stats.probplot(data, dist="norm", plot=ax)
                ax.set_title("Normal Probability Plot")
            ax.grid(True, linestyle='--', alpha=0.7)
            canvas = FigureCanvasTkAgg(fig, plot_window)
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
            toolbar = NavigationToolbar2Tk(canvas, plot_window)
            toolbar.update()
            self.status_var.set(f"{plot_type.title()} plot generated successfully")
        except Exception as e:
            messagebox.showerror("Plot Error", f"Error generating plot: {str(e)}")
            self.status_var.set(f"Error generating plot: {str(e)}")
            logger.error(f"Statistical plot error: {e}")
    def load_sample_data(self):
        np.random.seed(42)
        sample_data = np.random.normal(loc=50, scale=15, size=100)
        data_str = ", ".join([f"{x:.2f}" for x in sample_data])
        self.data_entry.delete(1.0, tk.END)
        self.data_entry.insert(1.0, data_str)
        self.status_var.set("Sample data loaded")
    def show_unit_converter(self):
        self.status_var.set("Unit converter tool not implemented yet")
    def show_date_calculator(self):
        self.status_var.set("Date calculator tool not implemented yet")
    def show_equation_solver(self):
        self.status_var.set("Equation solver tool not implemented yet")
    def save_history(self):
        if not self.memory_manager.history:
            messagebox.showinfo("Save History", "No history to save.")
            return
        try:
            file_path = tk.filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Save History"
            )
            if file_path:
                with open(file_path, 'w') as f:
                    f.write("\n\n".join(self.memory_manager.history))
                self.status_var.set(f"History saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Error saving history: {str(e)}")
            self.status_var.set(f"Error saving history: {str(e)}")
    def load_history(self):
        try:
            file_path = tk.filedialog.askopenfilename(
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Load History"
            )
            if file_path:
                with open(file_path, 'r') as f:
                    content = f.read()
                    entries = [entry for entry in content.split('\n\n') if entry.strip()]
                    self.memory_manager.history = entries
                    self.update_history_display()
                self.status_var.set(f"History loaded from {file_path}")
        except Exception as e:
            messagebox.showerror("Load Error", f"Error loading history: {str(e)}")
            self.status_var.set(f"Error loading history: {str(e)}")
    def show_help(self):
        help_window = tk.Toplevel(self)
        help_window.title("Calculator Help")
        help_window.geometry("800x600")
        help_notebook = ttk.Notebook(help_window)
        help_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        help_tab = ttk.Frame(help_notebook)
        help_notebook.add(help_tab, text="Help")
        help_text = scrolledtext.ScrolledText(help_tab, wrap=tk.WORD)
        help_text.pack(fill=tk.BOTH, expand=True)
        help_content = """
# Advanced Scientific Calculator Help

## General Usage
This calculator provides multiple modes for different types of calculations:

- **Standard Mode**: Basic arithmetic operations
- **Scientific Mode**: Advanced mathematical functions and calculations
- **Programmer Mode**: Bit manipulation and number system conversion
- **Graphing Mode**: Plot functions and equations
- **Statistics Mode**: Statistical calculations and data analysis

## Basic Operations
- Use the number buttons or keyboard to enter values
- Use operation buttons (+, -, ×, ÷) to perform calculations
- Press = or Enter to calculate the result
- Press C to clear the display
- Press CE to clear the current entry
- Press ⌫ to delete the last character

## Memory Functions
- MS: Store the current value in memory
- MR: Recall the value from memory
- MC: Clear the memory
- M+: Add the current value to memory
- M-: Subtract the current value from memory

## Scientific Functions
- Trigonometric functions: sin, cos, tan
- Logarithmic functions: ln, log₁₀, log₂
- Powers and roots: x^y, √, ∛
- Constants: π, e

## Programmer Functions
- Bit operations: AND, OR, XOR, NOT
- Shift operations: <<, >>
- Number system conversion: DEC, HEX, OCT, BIN

## Graphing Functions
- Enter expressions with variable x
- Set the range for x and y axes
- Multiple expressions with different colors

## Statistics Functions
- Enter data separated by commas or spaces
- Calculate basic and advanced statistics
- Generate different types of plots

## Keyboard Shortcuts
- Enter: Calculate result
- Escape: Clear display
- Backspace: Delete last character
- Ctrl+C: Copy result
- Ctrl+V: Paste to display
- Ctrl+N: New calculation
"""
        help_text.insert(tk.END, help_content)
        help_text.config(state=tk.DISABLED)
        socials_tab = ttk.Frame(help_notebook)
        help_notebook.add(socials_tab, text="Socials")
        ttk.Label(socials_tab, text="Connect with the Developer", 
                 font=("Helvetica", 16, "bold")).pack(pady=(20, 30))
        github_frame = ttk.Frame(socials_tab)
        github_frame.pack(fill=tk.X, padx=50, pady=10)
        ttk.Label(github_frame, text="GitHub:", 
                 font=("Helvetica", 12, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        github_link = ttk.Label(github_frame, text="driizzyy", 
                              foreground="blue", cursor="hand2")
        github_link.pack(side=tk.LEFT)
        github_link.bind("<Button-1>", lambda e: self._open_url("https://github.com/driizzyy"))
        discord_frame = ttk.Frame(socials_tab)
        discord_frame.pack(fill=tk.X, padx=50, pady=10)
        ttk.Label(discord_frame, text="Discord:", 
                 font=("Helvetica", 12, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        discord_username = ttk.Label(discord_frame, text="drakko5.56", 
                                   foreground="black")
        discord_username.pack(side=tk.LEFT, padx=(0, 20))
        discord_link = ttk.Label(discord_frame, text="Join Discord Server", 
                               foreground="blue", cursor="hand2")
        discord_link.pack(side=tk.LEFT)
        discord_link.bind("<Button-1>", lambda e: self._open_url("https://discord.gg/fCvyfUUc7w"))
        ttk.Separator(socials_tab, orient="horizontal").pack(fill=tk.X, padx=50, pady=20)
        info_text = ttk.Label(socials_tab, 
                            text="Feel free to reach out for support, feature requests,\nor to report bugs!", 
                            font=("Helvetica", 11))
        info_text.pack(pady=10)
    def _open_url(self, url):
        import webbrowser
        webbrowser.open_new_tab(url)
    def show_shortcuts(self):
        shortcuts_window = tk.Toplevel(self)
        shortcuts_window.title("Keyboard Shortcuts")
        shortcuts_window.geometry("500x400")
        shortcuts_text = scrolledtext.ScrolledText(shortcuts_window, wrap=tk.WORD)
        shortcuts_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        shortcuts_content = """
# Keyboard Shortcuts

## General
- Enter/Return: Calculate result
- Escape: Clear display
- Delete: Clear entry
- Backspace: Delete last character
- Ctrl+N: New calculation
- Alt+F4: Exit

## Editing
- Ctrl+C: Copy result
- Ctrl+V: Paste to display

## Numbers and Operators
- 0-9: Input numbers
- +: Addition
- -: Subtraction
- *: Multiplication
- /: Division
- .: Decimal point
- (: Open parenthesis
- ): Close parenthesis
"""
        shortcuts_text.insert(tk.END, shortcuts_content)
        shortcuts_text.config(state=tk.DISABLED)
    def show_about(self):
        about_window = tk.Toplevel(self)
        about_window.title("About Calculator")
        about_window.geometry("400x300")
        about_window.resizable(False, False)
        frame = ttk.Frame(about_window, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(frame, text="Advanced Scientific Calculator", 
                 font=("Helvetica", 16, "bold")).pack(pady=(0, 10))
        ttk.Label(frame, text="Version 1.0.0").pack(pady=(0, 20))
        description = """A comprehensive calculator application with multiple modes including standard, scientific, programmer, graphing, and statistics. Designed with an intuitive interface and powerful features."""
        desc_label = ttk.Label(frame, text=description, wraplength=350, justify=tk.CENTER)
        desc_label.pack(pady=(0, 20))
        ttk.Label(frame, text="© 2025 driizzyy").pack(pady=(0, 5))
        import platform
        python_version = platform.python_version()
        ttk.Label(frame, text=f"Compatible with Python {python_version}").pack(pady=(0, 5))
        ttk.Button(frame, text="Close", command=about_window.destroy).pack(pady=(10, 0))
if __name__ == "__main__":
    app = AdvancedCalculator()
    app.mainloop()
