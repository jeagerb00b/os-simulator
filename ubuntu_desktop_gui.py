import customtkinter as ctk
import tkinter as tk
import time
import subprocess
import sys
import os
import io
import threading
import traceback
from contextlib import redirect_stdout

# Import the logic from your existing files
try:
    from disk_scheduling import fcfs_disk_schedule, scan_disk_scheduling, cscan_disk_scheduling
    from memory_management import PagingSystem, SegmentationSystem, MemoryAllocator
except ImportError as e:
    # Use a simple tkinter messagebox if CTk isn't ready
    tk.messagebox.showerror("Error", f"Could not find required files: {e}\n\nPlease make sure all .py files are in the same directory.")
    sys.exit(1)

# Set the theme to match Ubuntu's dark feel
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AppWindow(ctk.CTkFrame):
    """A draggable, closable window to hold an app."""
    
    # --- THIS IS THE FIXED __init__ ---
    def __init__(self, parent, title, x, y, width, height):
        # Pass width/height to the constructor, NOT to .place()
        super().__init__(parent, width=width, height=height, 
                         fg_color="#2b2b2b", border_width=1, border_color="#555555")
        
        self.parent = parent
        # Only pass x/y to .place()
        self.place(x=x, y=y)

        # Title Bar
        self.title_bar = ctk.CTkFrame(self, height=30, fg_color="#242424", corner_radius=0)
        self.title_bar.pack(fill="x", side="top")

        self.title_label = ctk.CTkLabel(self.title_bar, text=title, font=ctk.CTkFont(size=13, weight="bold"))
        self.title_label.pack(side="left", padx=10)

        self.close_button = ctk.CTkButton(self.title_bar, text="✕", width=30, height=25,
                                           command=self.close, fg_color="#e04a4a", hover_color="#b03a3a")
        self.close_button.pack(side="right", padx=5)

        # Content Area
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Drag functionality
        self.title_bar.bind("<ButtonPress-1>", self.start_drag)
        self.title_bar.bind("<B1-Motion>", self.do_drag)
        self.title_label.bind("<ButtonPress-1>", self.start_drag)
        self.title_label.bind("<B1-Motion>", self.do_drag)

    def start_drag(self, event):
        self._drag_start_x = event.x
        self._drag_start_y = event.y
    
    def do_drag(self, event):
        new_x = self.winfo_x() - self._drag_start_x + event.x
        new_y = self.winfo_y() - self._drag_start_y + event.y
        self.place(x=new_x, y=new_y)
        self.lift()

    def close(self):
        print(f"--- Closing window: {self.title_label.cget('text')} ---")
        self.destroy()

class UbuntuSimulator(ctk.CTk):
    """Main application class simulating the Ubuntu Desktop."""
    
    def __init__(self):
        super().__init__()

        self.title("Ubuntu OS Simulator")
        self.geometry("1280x720")
        
        self.grid_rowconfigure(1, weight=1)    
        self.grid_columnconfigure(1, weight=1) 

        self.windows = {}

        print("--- Initializing GUI ---")
        self.create_top_bar()
        self.create_dock()
        
        self.desktop_area = ctk.CTkFrame(self, fg_color="#4B3A5A", corner_radius=0)
        self.desktop_area.grid(row=1, column=1, sticky="nsew")
        print("--- GUI Initialized Successfully ---")

    def create_top_bar(self):
        top_bar = ctk.CTkFrame(self, height=30, fg_color="#1e1e1e", corner_radius=0)
        top_bar.grid(row=0, column=0, columnspan=2, sticky="ew")
        ctk.CTkLabel(top_bar, text="Activities", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=20)
        self.clock_label = ctk.CTkLabel(top_bar, font=ctk.CTkFont(size=13))
        self.clock_label.pack(side="right", padx=20)
        self.update_clock()
        print("Top bar created.")

    def update_clock(self):
        now = time.strftime("%a %b %d  %I:%M:%S %p")
        self.clock_label.configure(text=now)
        self.after(1000, self.update_clock)

    def create_dock(self):
        self.dock = ctk.CTkFrame(self, width=60, fg_color="#1e1e1e", corner_radius=0) 
        self.dock.grid(row=1, column=0, sticky="ns")
        self.dock.pack_propagate(False)

        self.add_dock_button(self.dock, "📞", "System Calls", self.launch_syscalls_app)
        self.add_dock_button(self.dock, "🧵", "Thread Sync", lambda: self.open_app_window("threads", "🧵 Thread Synchronization", 700, 500))
        self.add_dock_button(self.dock, "💿", "Disk Scheduler", lambda: self.open_app_window("disk", "💿 Disk Scheduling", 500, 550))
        self.add_dock_button(self.dock, "🧠", "Memory Manager", lambda: self.open_app_window("memory", "🧠 Memory Management", 700, 600))
        print("Dock created.")

    def add_dock_button(self, parent, text, tooltip, command):
        
        def command_wrapper():
            print(f"\nDock icon '{text}' clicked. Executing command...")
            try:
                command()
                print(f"Command for '{text}' executed.")
            except Exception as e:
                print(f"--- 🛑 ERROR executing command for '{text}' ---")
                print(f"Error: {e}")
                traceback.print_exc()

        btn = ctk.CTkButton(
            parent,
            text=text,
            width=45,
            height=45,
            font=ctk.CTkFont(size=24),
            fg_color="#3a3a3a",
            hover_color="#555555",
            command=command_wrapper  # Use the wrapper
        )
        btn.pack(pady=7, padx=7)

    def open_app_window(self, app_name, title, width, height):
        print(f"  Attempting to open app window: {app_name}")
        if self.windows.get(app_name) and self.windows[app_name].winfo_exists():
            print(f"  Window '{app_name}' already exists. Lifting to front.")
            self.windows[app_name].lift()
            return
        
        print(f"  Creating new AppWindow for '{app_name}'...")
        x = 100 + len(self.windows) * 30
        y = 50 + len(self.windows) * 30
        
        win = AppWindow(self.desktop_area, title, x, y, width, height)
        self.windows[app_name] = win
        print(f"  AppWindow created.")
        
        win.bind("<Destroy>", lambda e, name=app_name: (
            print(f"Window '{name}' closed."), self.windows.pop(name, None)
        ))

        try:
            print(f"  Populating content for '{app_name}'...")
            if app_name == "threads":
                self.populate_thread_window(win.content_frame)
            elif app_name == "disk":
                self.populate_disk_window(win.content_frame)
            elif app_name == "memory":
                self.populate_memory_window(win.content_frame)
            print(f"  Content for '{app_name}' populated successfully.")
        except Exception as e:
            print(f"--- 🛑 ERROR populating content for '{app_name}' ---")
            print(f"Error: {e}")
            traceback.print_exc()

    def launch_syscalls_app(self):
        print(f"  Attempting to open app window: syscalls")
        if self.windows.get("syscalls") and self.windows["syscalls"].winfo_exists():
            print(f"  Window 'syscalls' already exists. Lifting to front.")
            self.windows["syscalls"].lift()
            return

        print(f"  Creating new AppWindow for 'syscalls'...")
        win = AppWindow(self.desktop_area, "📞 System Call Launcher", 200, 100, 400, 200)
        self.windows["syscalls"] = win
        win.bind("<Destroy>", lambda e: (
             print(f"Window 'syscalls' closed."), self.windows.pop("syscalls", None)
        ))
        
        label = ctk.CTkLabel(win.content_frame, text="This app runs in its own terminal.\nClick below to launch.",
                             font=ctk.CTkFont(size=13))
        label.pack(pady=20, padx=20)
        
        btn = ctk.CTkButton(win.content_frame, text="🚀 Launch Terminal",
                            command=self.launch_syscall_terminal)
        btn.pack(pady=10)
        print(f"  Content for 'syscalls' populated.")

    def launch_syscall_terminal(self):
        print("    Attempting to launch external terminal for syscalls...")
        try:
            if sys.platform == "win32":
                subprocess.Popen(["python", "miniOS_systemcall_simulator.py"], creationflags=subprocess.CREATE_NEW_CONSOLE)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", "-a", "Terminal.app", "python", "miniOS_systemcall_simulator.py"])
            else:
                subprocess.Popen(["x-terminal-emulator", "-e", "python miniOS_systemcall_simulator.py"])
            print("    Syscall terminal launched successfully.")
        except Exception as e:
            print(f"--- 🛑 ERROR launching syscall terminal ---")
            print(f"Error: {e}")
            traceback.print_exc()
            tk.messagebox.showerror("Error", f"Failed to launch terminal: {e}\n\nMake sure 'miniOS_systemcall_simulator.py' exists.")
            
    def populate_thread_window(self, parent_frame):
        parent_frame.grid_columnconfigure(0, weight=1)
        parent_frame.grid_rowconfigure(1, weight=1)

        btn_frame = ctk.CTkFrame(parent_frame)
        btn_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        output_box = ctk.CTkTextbox(parent_frame, wrap=tk.WORD, font=("Courier New", 10))
        output_box.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

        def stream_output(demo_name):
            output_box.delete('1.0', tk.END)
            output_box.insert(tk.END, f"--- Running {demo_name} ---\n\n")
            try:
                cmd = ["python", "Group5_Multithreading_and_Synchronization.py", demo_name]
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                           text=True, encoding='utf-8', bufsize=1)
                for line in iter(process.stdout.readline, ''):
                    output_box.insert(tk.END, line)
                    output_box.see(tk.END)
                process.stdout.close()
                process.wait()
                output_box.insert(tk.END, f"\n--- {demo_name} Complete ---")
            except Exception as e:
                output_box.insert(tk.END, f"\n--- ERROR ---\n{e}\n")
                traceback.print_exc()

        def run_demo_threaded(demo_name):
            threading.Thread(target=stream_output, args=(demo_name,), daemon=True).start()

        ctk.CTkButton(btn_frame, text="Race Condition", command=lambda: run_demo_threaded("race")).pack(side='left', padx=5, pady=5)
        ctk.CTkButton(btn_frame, text="Mutex Demo", command=lambda: run_demo_threaded("mutex_demo")).pack(side='left', padx=5, pady=5)
        ctk.CTkButton(btn_frame, text="Semaphore", command=lambda: run_demo_threaded("semaphore_demo")).pack(side='left', padx=5, pady=5)
        ctk.CTkButton(btn_frame, text="Producer-Consumer", command=lambda: run_demo_threaded("prod_cons")).pack(side='left', padx=5, pady=5)
    
    def populate_disk_window(self, parent_frame):
        parent_frame.grid_columnconfigure(0, weight=1)
        parent_frame.grid_rowconfigure(2, weight=1)

        input_frame = ctk.CTkFrame(parent_frame)
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(input_frame, text="Requests:").grid(row=0, column=0, padx=10, pady=5, sticky='w')
        ent_requests = ctk.CTkEntry(input_frame, width=250)
        ent_requests.grid(row=0, column=1, columnspan=3, padx=10, pady=5, sticky='w')
        ent_requests.insert(0, "176, 79, 34, 60, 92, 11, 41, 114")

        ctk.CTkLabel(input_frame, text="Initial Head:").grid(row=1, column=0, padx=10, pady=5, sticky='w')
        ent_head = ctk.CTkEntry(input_frame, width=100)
        ent_head.grid(row=1, column=1, padx=10, pady=5, sticky='w')
        ent_head.insert(0, "50")

        ctk.CTkLabel(input_frame, text="Disk Size:").grid(row=2, column=0, padx=10, pady=5, sticky='w')
        ent_disk_size = ctk.CTkEntry(input_frame, width=100)
        ent_disk_size.grid(row=2, column=1, padx=10, pady=5, sticky='w')
        ent_disk_size.insert(0, "200")

        ctk.CTkLabel(input_frame, text="SCAN Direction:").grid(row=3, column=0, padx=10, pady=5, sticky='w')
        scan_dir = ctk.StringVar(value="right")
        ctk.CTkRadioButton(input_frame, text="Left", variable=scan_dir, value="left").grid(row=3, column=1, sticky='w', padx=10)
        ctk.CTkRadioButton(input_frame, text="Right", variable=scan_dir, value="right").grid(row=3, column=2, sticky='w', padx=10)

        btn_frame = ctk.CTkFrame(parent_frame)
        btn_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        output_box = ctk.CTkTextbox(parent_frame, wrap=tk.WORD, font=("Courier New", 10))
        output_box.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="nsew")

        def run_alg(alg_name):
            try:
                requests = [int(r.strip()) for r in ent_requests.get().split(',')]
                head = int(ent_head.get())
                disk_size = int(ent_disk_size.get())
                
                output_box.delete('1.0', tk.END)
                output_box.insert(tk.END, f"--- Running {alg_name} ---\n\n")
                
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
                tk.messagebox.showerror("Input Error", f"Invalid input: {e}")
                traceback.print_exc()

        ctk.CTkButton(btn_frame, text="Run FCFS", command=lambda: run_alg("FCFS")).pack(side='left', padx=10, pady=5)
        ctk.CTkButton(btn_frame, text="Run SCAN", command=lambda: run_alg("SCAN")).pack(side='left', padx=10, pady=5)
        ctk.CTkButton(btn_frame, text="Run C-SCAN", command=lambda: run_alg("C-SCAN")).pack(side='left', padx=10, pady=5)

    def populate_memory_window(self, parent_frame):
        parent_frame.grid_rowconfigure(0, weight=1)
        parent_frame.grid_columnconfigure(0, weight=1)
        
        try:
            self.allocator = MemoryAllocator(total_memory=1000)
            self.paging_system = PagingSystem(num_frames=32, page_size=16)
            self.segment_system = SegmentationSystem()
        except Exception as e:
            ctk.CTkLabel(parent_frame, text=f"Error initializing memory systems: {e}").pack()
            traceback.print_exc()
            return

        nested_tabs = ctk.CTkTabview(parent_frame)
        nested_tabs.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        nested_tabs.add("Allocation")
        nested_tabs.add("Paging")
        nested_tabs.add("Segmentation")

        self.create_alloc_sub_tab(nested_tabs.tab("Allocation"))
        self.create_paging_sub_tab(nested_tabs.tab("Paging"))
        self.create_seg_sub_tab(nested_tabs.tab("Segmentation"))
    
    def capture_print(self, func, *args, **kwargs):
        f = io.StringIO()
        try:
            with redirect_stdout(f):
                func(*args, **kwargs)
            return f.getvalue()
        except Exception as e:
            traceback.print_exc()
            return f"An error occurred: {e}\n{f.getvalue()}"
            
    def create_alloc_sub_tab(self, tab):
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        controls = ctk.CTkFrame(tab)
        controls.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        ctk.CTkLabel(controls, text="PID:").grid(row=0, column=0, sticky='w', padx=10)
        ent_alloc_pid = ctk.CTkEntry(controls, width=100)
        ent_alloc_pid.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        ctk.CTkLabel(controls, text="Size:").grid(row=0, column=2, sticky='w', padx=10)
        ent_alloc_size = ctk.CTkEntry(controls, width=100)
        ent_alloc_size.grid(row=0, column=3, padx=5, pady=5, sticky='w')
        ctk.CTkButton(controls, text="Alloc (First Fit)", command=lambda: run_alloc_ff()).grid(row=1, column=0, pady=10, padx=5)
        ctk.CTkButton(controls, text="Alloc (Best Fit)", command=lambda: run_alloc_bf()).grid(row=1, column=1, pady=10, padx=5)
        ctk.CTkButton(controls, text="Free PID", command=lambda: run_alloc_free()).grid(row=1, column=2, pady=10, padx=5)
        ctk.CTkButton(controls, text="Show Map", command=lambda: show_map(), fg_color="gray").grid(row=1, column=3, pady=10, padx=5)
        output_box = ctk.CTkTextbox(tab, wrap=tk.WORD, font=("Courier New", 10))
        output_box.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        output_box.insert(tk.END, "Allocator initialized with 1000 units.\n")

        def show_map():
            output = self.capture_print(self.allocator.print_map)
            output_box.insert(tk.END, f"\n{output}\n"); output_box.see(tk.END)
        def run_alloc_ff():
            try: pid, size = ent_alloc_pid.get(), int(ent_alloc_size.get()); out = self.capture_print(self.allocator.first_fit, pid, size); output_box.insert(tk.END, out); show_map()
            except Exception as e: output_box.insert(tk.END, f"Error: {e}\n"); traceback.print_exc()
        def run_alloc_bf():
            try: pid, size = ent_alloc_pid.get(), int(ent_alloc_size.get()); out = self.capture_print(self.allocator.best_fit, pid, size); output_box.insert(tk.END, out); show_map()
            except Exception as e: output_box.insert(tk.END, f"Error: {e}\n"); traceback.print_exc()
        def run_alloc_free():
            try: pid = ent_alloc_pid.get(); out = self.capture_print(self.allocator.free, pid); output_box.insert(tk.END, out); show_map()
            except Exception as e: output_box.insert(tk.END, f"Error: {e}\n"); traceback.print_exc()

    def create_paging_sub_tab(self, tab):
        tab.grid_columnconfigure(0, weight=1); tab.grid_rowconfigure(2, weight=1)
        frame1 = ctk.CTkFrame(tab); frame1.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        ctk.CTkLabel(frame1, text="--- Allocate Process ---", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=3, sticky='w', pady=5, padx=10)
        ctk.CTkLabel(frame1, text="PID:").grid(row=1, column=0, sticky='w', padx=10)
        ent_page_pid = ctk.CTkEntry(frame1, width=100); ent_page_pid.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        ctk.CTkLabel(frame1, text="# Pages:").grid(row=1, column=2, sticky='w', padx=10)
        ent_page_num = ctk.CTkEntry(frame1, width=100); ent_page_num.grid(row=1, column=3, padx=5, pady=5, sticky='w')
        ctk.CTkButton(frame1, text="Allocate", command=lambda: run_page_alloc()).grid(row=1, column=4, padx=10, pady=5)
        frame2 = ctk.CTkFrame(tab); frame2.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        ctk.CTkLabel(frame2, text="--- Translate Address ---", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=3, sticky='w', pady=5, padx=10)
        ctk.CTkLabel(frame2, text="PID:").grid(row=1, column=0, sticky='w', padx=10)
        ent_page_t_pid = ctk.CTkEntry(frame2, width=100); ent_page_t_pid.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        ctk.CTkLabel(frame2, text="Logical Addr:").grid(row=1, column=2, sticky='w', padx=10)
        ent_page_t_addr = ctk.CTkEntry(frame2, width=100); ent_page_t_addr.grid(row=1, column=3, padx=5, pady=5, sticky='w')
        ctk.CTkButton(frame2, text="Translate", command=lambda: run_page_trans()).grid(row=1, column=4, padx=10, pady=5)
        output_box = ctk.CTkTextbox(tab, wrap=tk.WORD, font=("Courier New", 10)); output_box.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        output_box.insert(tk.END, "Paging system initialized (32 frames, page size 16).\n")
        
        def run_page_alloc():
            try: pid, num = ent_page_pid.get(), int(ent_page_num.get()); out = self.capture_print(self.paging_system.allocate_process, pid, num); output_box.insert(tk.END, f"\n{out}")
            except Exception as e: output_box.insert(tk.END, f"\nError: {e}\n"); traceback.print_exc()
        def run_page_trans():
            try: pid, addr = ent_page_t_pid.get(), int(ent_page_t_addr.get()); out = self.capture_print(self.paging_system.translate_address, pid, addr); output_box.insert(tk.END, f"\n{out}")
            except Exception as e: output_box.insert(tk.END, f"\nError: {e}\n"); traceback.print_exc()

    def create_seg_sub_tab(self, tab):
        tab.grid_columnconfigure(0, weight=1); tab.grid_rowconfigure(2, weight=1)
        frame1 = ctk.CTkFrame(tab); frame1.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        ctk.CTkLabel(frame1, text="--- Allocate Segment ---", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=7, sticky='w', pady=5, padx=10)
        ctk.CTkLabel(frame1, text="PID:").grid(row=1, column=0, sticky='w', padx=5); ent_seg_pid = ctk.CTkEntry(frame1, width=70); ent_seg_pid.grid(row=1, column=1, padx=5, pady=5)
        ctk.CTkLabel(frame1, text="Seg #:").grid(row=1, column=2, sticky='w', padx=5); ent_seg_num = ctk.CTkEntry(frame1, width=70); ent_seg_num.grid(row=1, column=3, padx=5, pady=5)
        ctk.CTkLabel(frame1, text="Base:").grid(row=1, column=4, sticky='w', padx=5); ent_seg_base = ctk.CTkEntry(frame1, width=70); ent_seg_base.grid(row=1, column=5, padx=5, pady=5)
        ctk.CTkLabel(frame1, text="Limit:").grid(row=1, column=6, sticky='w', padx=5); ent_seg_limit = ctk.CTkEntry(frame1, width=70); ent_seg_limit.grid(row=1, column=7, padx=5, pady=5)
        ctk.CTkButton(frame1, text="Allocate", command=lambda: run_seg_alloc()).grid(row=1, column=8, padx=10, pady=5)
        frame2 = ctk.CTkFrame(tab); frame2.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        ctk.CTkLabel(frame2, text="--- Translate Address ---", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=5, sticky='w', pady=5, padx=10)
        ctk.CTkLabel(frame2, text="PID:").grid(row=1, column=0, sticky='w', padx=5); ent_seg_t_pid = ctk.CTkEntry(frame2, width=70); ent_seg_t_pid.grid(row=1, column=1, padx=5, pady=5)
        ctk.CTkLabel(frame2, text="Seg #:").grid(row=1, column=2, sticky='w', padx=5); ent_seg_t_num = ctk.CTkEntry(frame2, width=70); ent_seg_t_num.grid(row=1, column=3, padx=5, pady=5)
        ctk.CTkLabel(frame2, text="Offset:").grid(row=1, column=4, sticky='w', padx=5); ent_seg_t_off = ctk.CTkEntry(frame2, width=70); ent_seg_t_off.grid(row=1, column=5, padx=5, pady=5)
        
        # --- THIS IS THE FIXED LINE (padx=10) ---
        ctk.CTkButton(frame2, text="Translate", command=lambda: run_seg_trans()).grid(row=1, column=8, padx=10, pady=5)
        
        output_box = ctk.CTkTextbox(tab, wrap=tk.WORD, font=("Courier New", 10)); output_box.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        output_box.insert(tk.END, "Segmentation system initialized.\n")

        def run_seg_alloc():
            try: pid, num = ent_seg_pid.get(), int(ent_seg_num.get()); base, limit = int(ent_seg_base.get()), int(ent_seg_limit.get()); out = self.capture_print(self.segment_system.allocate_segment, pid, num, base, limit); output_box.insert(tk.END, f"\n{out}")
            except Exception as e: output_box.insert(tk.END, f"\nError: {e}\n"); traceback.print_exc()
        def run_seg_trans():
            try: pid, num = ent_seg_t_pid.get(), int(ent_seg_t_num.get()); offset = int(ent_seg_t_off.get()); out = self.capture_print(self.segment_system.translate_address, pid, num, offset); output_box.insert(tk.END, f"\n{out}")
            except Exception as e: output_box.insert(tk.END, f"\nError: {e}\n"); traceback.print_exc()

if __name__ == "__main__":
    print("Starting application...")
    app = UbuntuSimulator()
    app.mainloop()
    print("Application closed.")