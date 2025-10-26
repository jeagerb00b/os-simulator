Visual OS Simulator Desktop

This project is a visual, desktop-style simulator for core Operating Systems concepts, built entirely in Python using **CustomTkinter**. It provides a hands-on, interactive environment to understand complex OS topics that are normally just theoretical.

The interface mimics a modern desktop (like Ubuntu) with a top bar, a left-side dock, and draggable application windows for each simulation module.

Features

* Ubuntu-style Desktop GUI:** A modern, dark-mode interface with a dock and draggable application windows.
* Four Core OS Modules:
    1.  **Process & System Calls:** Simulate `fork()`, `exec()`, `wait()`, and `exit()`, and manage processes.
    2.  **Thread Synchronization:** Visualize race conditions, mutexes, semaphores, and the Producer-Consumer problem.
    3.  **Disk Scheduling:** Compare FCFS, SCAN, and C-SCAN algorithms and see the total head movement.
    4.  **Memory Management:** Simulate paging, segmentation, and contiguous memory allocation (First-Fit, Best-Fit).
* Live, Streamed Output:** See the results of your simulations in real-time, just like in a real terminal.

How to Run

1.  Clone the repository:
    ```bash
    git clone [https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git](https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git)
    cd YOUR-REPO-NAME
    ```

2.  Install dependencies:
    This project requires the **CustomTkinter** library.
    ```bash
    pip install customtkinter
    ```

3.  Ensure all files are present:
    Make sure all the Python files are in the same directory:
    * `ubuntu_desktop_gui.py` (The main file to run)
    * `miniOS_systemcall_simulator.py`
    * `Group5_Multithreading_and_Synchronization.py`
    * `memory_management.py`
    * `disk_scheduling.py`
    * `fcfs_code.py`
    * `scan_code.py`
    * `cscan_code.py`

4.  Run the application:
    ```bash
    python ubuntu_desktop_gui.py
    ```

Modules Included

Process & System Call Simulator
* Launches an interactive terminal to simulate a process table.
* Commands:** `run <prog_name>`, `ps` (process status), `tree` (process tree), `exit`, `wait`, and `fork`.
* Demonstrates how `fork()` creates a child process and how `wait()` blocks the parent.

Memory Management Simulator
* Contiguous Allocation:Allocate and free processes from memory using **First-Fit** and **Best-Fit** algorithms.
* Paging:Simulate logical-to-physical address translation using a page table.
* Segmentation:Simulate logical-to-physical address translation using a segment table.

Disk Scheduling Simulator
* Enter a list of disk requests (e.g., `176, 79, 34, 60`) and an initial head position.
* Compares the total head movement (seek time) for:
    * FCFS(First-Come, First-Served)
    * SCAN(Elevator algorithm)
    * C-SCAN(Circular SCAN)

Thread Synchronization Simulator
* Race Condition:Watch two threads try to increment a counter without locks, leading to an incorrect final value.
* Mutex Demo:See how a `Mutex` (mutual exclusion) lock fixes the race condition.
* Semaphore Demo:Run a simulation of a resource pool (like 2 connections) being managed by a semaphore.
* Producer-Consumer:A classic simulation of a shared buffer being safely accessed by a producer thread and a consumer thread.
