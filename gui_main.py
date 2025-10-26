import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, StringVar, Frame, Label, Entry, Button, Radiobutton
import subprocess
import sys
import os
import io
from contextlib import redirect_stdout

# Import the logic from your existing files
try:
    from disk_scheduling import fcfs_disk_schedule, scan_disk_scheduling, cscan_disk_scheduling
    from memory_management import PagingSystem, SegmentationSystem, MemoryAllocator
except ImportError as e:
    messagebox.showerror("Error", f"Could not find required files: {e}\n\nPlease make sure all .py files are in the same directory.")
    sys.exit(1)

# --- Helper function to capture 'print' output for the GUI ---

def capture_print_output(func, *args, **kwargs):
    """
    Runs a function, captures its 'print' statements, 
    and returns them as a string.
    """
    f = io.StringIO()
    try:
        with redirect_stdout(f):
            func(*args, **kwargs)
        return f.getvalue()
    except Exception as e:
        return f"An error occurred: {e}\n{f.getvalue()}"


class OS_Simulator_GUI(tk.Tk):
    """Main application window."""
    def __init__(self):
        super().__init__()
        self.title("🖥️ Mini OS Simulator")
        self.geometry("400x350")
        
        self.configure(bg='#f0f0f0')
        
        title = Label(self, text="Mini OS Simulator", font=("Helvetica", 18, "bold"), bg='#f0f0f0')
        title.pack(pady=20)
        
        style = ttk.Style()
        style.configure("TButton", font=("Helvetica", 12), padding=10)
        
        btn_frame = Frame(self, bg='#f0f0f0')
        btn_frame.pack(fill='x', padx=50)

        ttk.Button(btn_frame, text="Process & System Calls", command=self.open_syscalls).pack(fill='x', pady=5)
        ttk.Button(btn_frame, text="Thread Synchronization", command=self.open_threads).pack(fill='x', pady=5)
        ttk.Button(btn_frame, text="Disk Scheduling", command=self.open_disk_scheduler).pack(fill='x', pady=5)
        ttk.Button(btn_frame, text="Memory Management", command=self.open_memory_manager).pack(fill='x', pady=5)

        Label(self, text="Created by integrating your Python modules.", font=("Helvetica", 8), bg='#f0f0f0').pack(side='bottom', pady=10)

    def open_syscalls(self):
        """
        Launches the system call simulator in a NEW terminal window.
        This module is a REPL (interactive prompt) and runs best in its own console.
        """
        messagebox.showinfo("Launcher", 
            "The System Call Simulator is an interactive prompt.\n\n"
            "It will be launched in a **new terminal window**.\n\n"
            "Type 'quit' in that new window to close it.")
        
        try:
            if sys.platform == "win32":
                # For Windows
                subprocess.Popen(["python", "miniOS_systemcall_simulator.py"], creationflags=subprocess.CREATE_NEW_CONSOLE)
            elif sys.platform == "darwin":
                # For macOS
                subprocess.Popen(["open", "-a", "Terminal.app", "python", "miniOS_systemcall_simulator.py"])
            else:
                # For Linux (assumes x-terminal-emulator is available)
                subprocess.Popen(["x-terminal-emulator", "-e", "python miniOS_systemcall_simulator.py"])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch terminal: {e}\n\nMake sure 'miniOS_systemcall_simulator.py' exists.")

    def open_threads(self):
        """Opens the thread synchronization demo window."""
        win = tk.Toplevel(self)
        win.title("🧵 Thread Synchronization")
        win.geometry("700x500")

        btn_frame = Frame(win, pady=10)
        btn_frame.pack(fill='x', padx=10)

        output_box = scrolledtext.ScrolledText(win, wrap=tk.WORD, width=80, height=25, font=("Courier New", 9))
        output_box.pack(padx=10, pady=10, fill='both', expand=True)

        def run_demo(demo_name):
            output_box.delete('1.0', tk.END)
            output_box.insert(tk.END, f"--- Running {demo_name} ---\n\n")
            try:
                # Run the script as a subprocess and capture its output
                cmd = ["python", "Group5_Multithreading_and_Synchronization.py", demo_name]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True, encoding='utf-8')
                output_box.insert(tk.END, result.stdout)
                output_box.insert(tk.END, f"\n\n--- {demo_name} Complete ---")
            except subprocess.CalledProcessError as e:
                output_box.insert(tk.END, f"ERROR:\n{e.stderr}\n{e.stdout}")
            except FileNotFoundError:
                output_box.insert(tk.END, "Error: 'Group5_Multithreading_and_Synchronization.py' not found.")

        ttk.Button(btn_frame, text="Race Condition", command=lambda: run_demo("race")).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Mutex Demo", command=lambda: run_demo("mutex_demo")).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Semaphore Demo", command=lambda: run_demo("semaphore_demo")).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Producer-Consumer", command=lambda: run_demo("prod_cons")).pack(side='left', padx=5)

    def open_disk_scheduler(self):
        """Opens the disk scheduling input window."""
        win = tk.Toplevel(self)
        win.title("💿 Disk Scheduling")
        win.geometry("500x500")

        input_frame = Frame(win, pady=10, padx=10)
        input_frame.pack(fill='x')

        Label(input_frame, text="Requests (e.g., 98, 183, 37):").grid(row=0, column=0, sticky='w')
        ent_requests = Entry(input_frame, width=40)
        ent_requests.grid(row=0, column=1, padx=5)
        ent_requests.insert(0, "176, 79, 34, 60, 92, 11, 41, 114")

        Label(input_frame, text="Initial Head:").grid(row=1, column=0, sticky='w')
        ent_head = Entry(input_frame, width=10)
        ent_head.grid(row=1, column=1, sticky='w', padx=5)
        ent_head.insert(0, "50")

        Label(input_frame, text="Disk Size:").grid(row=2, column=0, sticky='w')
        ent_disk_size = Entry(input_frame, width=10)
        ent_disk_size.grid(row=2, column=1, sticky='w', padx=5)
        ent_disk_size.insert(0, "200")

        Label(input_frame, text="SCAN Direction:").grid(row=3, column=0, sticky='w')
        scan_dir = StringVar(value="right")
        Radiobutton(input_frame, text="Left", variable=scan_dir, value="left").grid(row=3, column=1, sticky='w', padx=5)
        Radiobutton(input_frame, text="Right", variable=scan_dir, value="right").grid(row=3, column=1, sticky='e', padx=15)
        
        btn_frame = Frame(win, pady=10)
        btn_frame.pack()
        
        output_box = scrolledtext.ScrolledText(win, wrap=tk.WORD, height=15, font=("Courier New", 10))
        output_box.pack(padx=10, pady=10, fill='both', expand=True)

        def run_alg(alg_name):
            try:
                requests = [int(r.strip()) for r in ent_requests.get().split(',')]
                head = int(ent_head.get())
                disk_size = int(ent_disk_size.get())
                
                output_box.delete('1.0', tk.END)
                output_box.insert(tk.END, f"--- Running {alg_name} ---\n")
                
                if alg_name == "FCFS":
                    seq, seek = fcfs_disk_schedule(requests.copy(), head)
                elif alg_name == "SCAN":
                    direction = scan_dir.get()
                    seq, seek = scan_disk_scheduling(requests.copy(), head, disk_size, direction)
                elif alg_name == "C-SCAN":
                    seq, seek = cscan_disk_scheduling(requests.copy(), head, disk_size)
                
                output_box.insert(tk.END, f"Seek Sequence: {seq}\n")
                output_box.insert(tk.END, f"Total Seek Time: {seek}\n")

            except Exception as e:
                messagebox.showerror("Input Error", f"Invalid input: {e}")

        ttk.Button(btn_frame, text="Run FCFS", command=lambda: run_alg("FCFS")).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Run SCAN", command=lambda: run_alg("SCAN")).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Run C-SCAN", command=lambda: run_alg("C-SCAN")).pack(side='left', padx=5)

    def open_memory_manager(self):
        """Opens the memory management window with tabs."""
        win = tk.Toplevel(self)
        win.title("🧠 Memory Management")
        win.geometry("700x600")

        notebook = ttk.Notebook(win)
        notebook.pack(pady=10, padx=10, fill='both', expand=True)
        
        # --- Instantiate the memory systems ---
        # We use placeholder values, which can be configured by the user if needed
        try:
            self.allocator = MemoryAllocator(total_memory=1000)
            self.paging_system = PagingSystem(num_frames=32, page_size=16)
            self.segment_system = SegmentationSystem()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize memory systems: {e}")
            win.destroy()
            return

        # --- Tab 1: Contiguous Allocation ---
        self.create_allocator_tab(notebook)
        
        # --- Tab 2: Paging ---
        self.create_paging_tab(notebook)

        # --- Tab 3: Segmentation ---
        self.create_segmentation_tab(notebook)
        
    def create_allocator_tab(self, notebook):
        tab = Frame(notebook, pady=10, padx=10)
        notebook.add(tab, text="Contiguous Allocation")

        controls = Frame(tab)
        controls.pack(fill='x')
        Label(controls, text="PID:").grid(row=0, column=0, sticky='w')
        ent_alloc_pid = Entry(controls, width=10)
        ent_alloc_pid.grid(row=0, column=1, padx=5, sticky='w')
        
        Label(controls, text="Size:").grid(row=0, column=2, sticky='w', padx=(10,0))
        ent_alloc_size = Entry(controls, width=10)
        ent_alloc_size.grid(row=0, column=3, padx=5, sticky='w')

        ttk.Button(controls, text="Alloc (First Fit)", command=lambda: run_alloc_ff()).grid(row=1, column=0, pady=5)
        ttk.Button(controls, text="Alloc (Best Fit)", command=lambda: run_alloc_bf()).grid(row=1, column=1, pady=5)
        ttk.Button(controls, text="Free PID", command=lambda: run_alloc_free()).grid(row=1, column=2, pady=5, padx=(10,0))
        ttk.Button(controls, text="Show Memory Map", command=lambda: show_map()).grid(row=1, column=3, pady=5)

        output_box = scrolledtext.ScrolledText(tab, wrap=tk.WORD, height=25, font=("Courier New", 10))
        output_box.pack(padx=5, pady=10, fill='both', expand=True)
        output_box.insert(tk.END, "Allocator initialized with 1000 units.\n")

        def show_map():
            # Special case for print_map to make it look nice
            output = capture_print_output(self.allocator.print_map)
            output_box.insert(tk.END, f"\n{output}\n")
            output_box.see(tk.END)
            
        def run_alloc_ff():
            try:
                pid, size = ent_alloc_pid.get(), int(ent_alloc_size.get())
                if not pid: raise ValueError("PID cannot be empty")
                out = capture_print_output(self.allocator.first_fit, pid, size)
                output_box.insert(tk.END, out)
                show_map()
            except Exception as e: output_box.insert(tk.END, f"Error: {e}\n")

        def run_alloc_bf():
            try:
                pid, size = ent_alloc_pid.get(), int(ent_alloc_size.get())
                if not pid: raise ValueError("PID cannot be empty")
                out = capture_print_output(self.allocator.best_fit, pid, size)
                output_box.insert(tk.END, out)
                show_map()
            except Exception as e: output_box.insert(tk.END, f"Error: {e}\n")

        def run_alloc_free():
            try:
                pid = ent_alloc_pid.get()
                if not pid: raise ValueError("PID cannot be empty")
                out = capture_print_output(self.allocator.free, pid)
                output_box.insert(tk.END, out)
                show_map()
            except Exception as e: output_box.insert(tk.END, f"Error: {e}\n")

    def create_paging_tab(self, notebook):
        tab = Frame(notebook, pady=10, padx=10)
        notebook.add(tab, text="Paging")

        controls = Frame(tab)
        controls.pack(fill='x')
        
        Label(controls, text="--- Allocate Process ---").grid(row=0, column=0, columnspan=4, sticky='w', pady=(0,5))
        Label(controls, text="PID:").grid(row=1, column=0, sticky='w')
        ent_page_pid = Entry(controls, width=10)
        ent_page_pid.grid(row=1, column=1, padx=5, sticky='w')
        Label(controls, text="# Pages:").grid(row=1, column=2, sticky='w', padx=(10,0))
        ent_page_num = Entry(controls, width=10)
        ent_page_num.grid(row=1, column=3, padx=5, sticky='w')
        ttk.Button(controls, text="Allocate", command=lambda: run_page_alloc()).grid(row=1, column=4, padx=10)

        Label(controls, text="--- Translate Address ---").grid(row=2, column=0, columnspan=4, sticky='w', pady=(10,5))
        Label(controls, text="PID:").grid(row=3, column=0, sticky='w')
        ent_page_t_pid = Entry(controls, width=10)
        ent_page_t_pid.grid(row=3, column=1, padx=5, sticky='w')
        Label(controls, text="Logical Addr:").grid(row=3, column=2, sticky='w', padx=(10,0))
        ent_page_t_addr = Entry(controls, width=10)
        ent_page_t_addr.grid(row=3, column=3, padx=5, sticky='w')
        ttk.Button(controls, text="Translate", command=lambda: run_page_trans()).grid(row=3, column=4, padx=10)

        output_box = scrolledtext.ScrolledText(tab, wrap=tk.WORD, height=20, font=("Courier New", 10))
        output_box.pack(padx=5, pady=10, fill='both', expand=True)
        output_box.insert(tk.END, "Paging system initialized (32 frames, page size 16).\n")

        def run_page_alloc():
            try:
                pid, num = ent_page_pid.get(), int(ent_page_num.get())
                out = capture_print_output(self.paging_system.allocate_process, pid, num)
                output_box.insert(tk.END, f"\n{out}")
            except Exception as e: output_box.insert(tk.END, f"\nError: {e}\n")

        def run_page_trans():
            try:
                pid, addr = ent_page_t_pid.get(), int(ent_page_t_addr.get())
                out = capture_print_output(self.paging_system.translate_address, pid, addr)
                output_box.insert(tk.END, f"\n{out}")
            except Exception as e: output_box.insert(tk.END, f"\nError: {e}\n")

    def create_segmentation_tab(self, notebook):
        tab = Frame(notebook, pady=10, padx=10)
        notebook.add(tab, text="Segmentation")

        controls = Frame(tab)
        controls.pack(fill='x')
        
        Label(controls, text="--- Allocate Segment ---").grid(row=0, column=0, columnspan=6, sticky='w', pady=(0,5))
        Label(controls, text="PID:").grid(row=1, column=0, sticky='w')
        ent_seg_pid = Entry(controls, width=8)
        ent_seg_pid.grid(row=1, column=1, padx=5, sticky='w')
        Label(controls, text="Seg #:").grid(row=1, column=2, sticky='w', padx=(10,0))
        ent_seg_num = Entry(controls, width=8)
        ent_seg_num.grid(row=1, column=3, padx=5, sticky='w')
        Label(controls, text="Base:").grid(row=1, column=4, sticky='w', padx=(10,0))
        ent_seg_base = Entry(controls, width=8)
        ent_seg_base.grid(row=1, column=5, padx=5, sticky='w')
        Label(controls, text="Limit:").grid(row=1, column=6, sticky='w', padx=(10,0))
        ent_seg_limit = Entry(controls, width=8)
        ent_seg_limit.grid(row=1, column=7, padx=5, sticky='w')
        ttk.Button(controls, text="Allocate", command=lambda: run_seg_alloc()).grid(row=1, column=8, padx=10)

        Label(controls, text="--- Translate Address ---").grid(row=2, column=0, columnspan=6, sticky='w', pady=(10,5))
        Label(controls, text="PID:").grid(row=3, column=0, sticky='w')
        ent_seg_t_pid = Entry(controls, width=8)
        ent_seg_t_pid.grid(row=3, column=1, padx=5, sticky='w')
        Label(controls, text="Seg #:").grid(row=3, column=2, sticky='w', padx=(10,0))
        ent_seg_t_num = Entry(controls, width=8)
        ent_seg_t_num.grid(row=3, column=3, padx=5, sticky='w')
        Label(controls, text="Offset:").grid(row=3, column=4, sticky='w', padx=(10,0))
        ent_seg_t_off = Entry(controls, width=8)
        ent_seg_t_off.grid(row=3, column=5, padx=5, sticky='w')
        ttk.Button(controls, text="Translate", command=lambda: run_seg_trans()).grid(row=3, column=8, padx=10)

        output_box = scrolledtext.ScrolledText(tab, wrap=tk.WORD, height=20, font=("Courier New", 10))
        output_box.pack(padx=5, pady=10, fill='both', expand=True)
        output_box.insert(tk.END, "Segmentation system initialized.\n")

        def run_seg_alloc():
            try:
                pid, num = ent_seg_pid.get(), int(ent_seg_num.get())
                base, limit = int(ent_seg_base.get()), int(ent_seg_limit.get())
                out = capture_print_output(self.segment_system.allocate_segment, pid, num, base, limit)
                output_box.insert(tk.END, f"\n{out}")
            except Exception as e: output_box.insert(tk.END, f"\nError: {e}\n")
        
        def run_seg_trans():
            try:
                pid, num = ent_seg_t_pid.get(), int(ent_seg_t_num.get())
                offset = int(ent_seg_t_off.get())
                out = capture_print_output(self.segment_system.translate_address, pid, num, offset)
                output_box.insert(tk.END, f"\n{out}")
            except Exception as e: output_box.insert(tk.END, f"\nError: {e}\n")


if __name__ == "__main__":
    app = OS_Simulator_GUI()
    app.mainloop()