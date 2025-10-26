import subprocess
import shlex
import sys
from disk_scheduling import fcfs_disk_schedule, scan_disk_scheduling, cscan_disk_scheduling
from memory_management import PagingSystem, SegmentationSystem, MemoryAllocator

# --- Helper Functions for User Input ---

def get_int(prompt):
    """Safely get an integer from the user."""
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a number.")

def get_requests(prompt):
    """Get a list of disk requests from the user."""
    while True:
        try:
            requests_str = input(prompt)
            return [int(r.strip()) for r in requests_str.split(',')]
        except ValueError:
            print("Invalid input. Please enter a list of numbers separated by commas (e.g., 98, 183, 37, 122)")

# --- Sub-Menu: Disk Scheduling ---

def run_disk_scheduling():
    """Menu for running disk scheduling algorithms."""
    print("\n--- 💿 Disk Scheduling Simulator ---")
    requests = get_requests("Enter disk requests (comma-separated): ")
    head = get_int("Enter initial head position: ")
    disk_size = get_int("Enter total disk size (e.g., 200): ")

    while True:
        print("\nDisk Algorithms:")
        print("  1. FCFS (First-Come, First-Served)")
        print("  2. SCAN")
        print("  3. C-SCAN (Circular SCAN)")
        print("  4. Back to Main Menu")
        choice = input("Choose an algorithm: ")

        if choice == '1':
            seq, seek = fcfs_disk_schedule(requests.copy(), head)
            print(f"  [FCFS] Sequence: {seq}")
            print(f"  [FCFS] Total Seek Time: {seek}")
        
        elif choice == '2':
            direction = input("  Enter direction ('left' or 'right'): ").lower()
            if direction not in ['left', 'right']:
                print("  Invalid direction. Defaulting to 'right'.")
                direction = 'right'
            seq, seek = scan_disk_scheduling(requests.copy(), head, disk_size, direction)
            print(f"  [SCAN] Sequence: {seq}")
            print(f"  [SCAN] Total Seek Time: {seek}")
            
        elif choice == '3':
            seq, seek = cscan_disk_scheduling(requests.copy(), head, disk_size)
            print(f"  [C-SCAN] Sequence: {seq}")
            print(f"  [C-SCAN] Total Seek Time: {seek}")
            
        elif choice == '4':
            break
        else:
            print("Invalid choice. Please try again.")

# --- Sub-Menu: Memory Management ---

def run_memory_management():
    """Menu for memory management simulations from the PDF."""
    print("\n--- 🧠 Memory Management Simulator ---")
    total_mem = get_int("Enter total memory size for Allocator (e.g., 1000): ")
    allocator = MemoryAllocator(total_mem)

    num_frames = get_int("Enter number of frames for Paging (e.g., 32): ")
    page_size = get_int("Enter page size (e.g., 16): ")
    paging = PagingSystem(num_frames, page_size)
    
    segmentation = SegmentationSystem()
    
    while True:
        print("\nMemory Management Techniques:")
        print("  (A) Contiguous Allocation")
        print("    1. Allocate (First Fit)")
        print("    2. Allocate (Best Fit)")
        print("    3. Free Memory")
        print("    4. Show Memory Map")
        print("  (B) Paging")
        print("    5. Allocate Process (Paging)")
        print("    6. Translate Address (Paging)")
        print("  (C) Segmentation")
        print("    7. Allocate Segment")
        print("    8. Translate Address (Segmentation)")
        print("  (D) Exit")
        print("    9. Back to Main Menu")
        
        choice = input("Choose an option: ")
        
        try:
            if choice == '1':
                pid = input("  Enter Process ID: ")
                size = get_int("  Enter memory size to allocate: ")
                allocator.first_fit(pid, size)
            elif choice == '2':
                pid = input("  Enter Process ID: ")
                size = get_int("  Enter memory size to allocate: ")
                allocator.best_fit(pid, size)
            elif choice == '3':
                pid = input("  Enter Process ID to free: ")
                allocator.free(pid)
            elif choice == '4':
                allocator.print_map()
            elif choice == '5':
                pid = input("  Enter Process ID: ")
                pages = get_int("  Enter number of pages: ")
                paging.allocate_process(pid, pages)
            elif choice == '6':
                pid = input("  Enter Process ID: ")
                addr = get_int("  Enter logical address: ")
                paging.translate_address(pid, addr)
            elif choice == '7':
                pid = input("  Enter Process ID: ")
                seg_num = get_int("  Enter segment number: ")
                base = get_int("  Enter base address: ")
                limit = get_int("  Enter segment limit: ")
                segmentation.allocate_segment(pid, seg_num, base, limit)
            elif choice == '8':
                pid = input("  Enter Process ID: ")
                seg_num = get_int("  Enter segment number: ")
                offset = get_int("  Enter offset: ")
                segmentation.translate_address(pid, seg_num, offset)
            elif choice == '9':
                break
            else:
                print("Invalid choice.")
        except Exception as e:
            print(f"An error occurred: {e}")

# --- Sub-Menu: Thread Synchronization ---

def run_thread_sync_demos():
    """Menu to run the multithreading synchronization demos."""
    print("\n--- 🧵 Thread Synchronization Demos ---")
    
    while True:
        print("\nSynchronization Scenarios:")
        print("  1. Race Condition Demo")
        print("  2. Mutex Demo")
        print("  3. Semaphore Demo")
        print("  4. Producer-Consumer Demo")
        print("  5. Run All")
        print("  6. Back to Main Menu")
        choice = input("Choose a demo: ")
        
        cmd = ["python", "Group5_Multithreading_and_Synchronization.py"]
        
        if choice == '1':
            subprocess.run(cmd + ["race"])
        elif choice == '2':
            subprocess.run(cmd + ["mutex_demo"])
        elif choice == '3':
            subprocess.run(cmd + ["semaphore_demo"])
        elif choice == '4':
            subprocess.run(cmd + ["prod_cons"])
        elif choice == '5':
            subprocess.run(cmd + ["all"])
        elif choice == '6':
            break
        else:
            print("Invalid choice.")

# --- Sub-Menu: System Call Simulator ---

def run_syscall_simulator():
    """Launches the miniOS system call simulator."""
    print("\n--- 📞 Launching System Call Simulator ---")
    print("Type 'help' inside the simulator for commands (e.g., ps, tree, run prog_echo 'hello').")
    print("Type 'quit' or 'exit' to return to the main menu.")
    
    try:
        subprocess.run(["python", "miniOS_systemcall_simulator.py"])
    except FileNotFoundError:
        print("Error: 'miniOS_systemcall_simulator.py' not found.")
    except Exception as e:
        print(f"Simulator exited with an error: {e}")
    print("\n--- Exited System Call Simulator ---")

# --- Main Menu ---

def main_menu():
    """Displays the main menu for the OS Simulator."""
    print("=" * 40)
    print("    🖥️ Welcome to the Mini OS Simulator")
    print("=" * 40)
    
    while True:
        print("\nMain Menu:")
        print("  1. Process & System Call Simulator (fork, exec, wait)")
        print("  2. Thread Synchronization Demos (Mutex, Semaphore)")
        print("  3. Disk Scheduling Algorithms (FCFS, SCAN, C-SCAN)")
        print("  4. Memory Management Techniques (Paging, Segmentation)")
        print("  5. Exit")
        
        choice = input("Select a module to run: ")
        
        if choice == '1':
            run_syscall_simulator()
        elif choice == '2':
            run_thread_sync_demos()
        elif choice == '3':
            run_disk_scheduling()
        elif choice == '4':
            run_memory_management()
        elif choice == '5':
            print("Exiting simulator. Goodbye!")
            break
        else:
            print("Invalid choice. Please select from 1-5.")

if __name__ == "__main__":
    main_menu()