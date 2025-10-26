# This code is transcribed from 'Os code member 3-5.pdf' [cite: 1]

# --- Member 3 - Paging Implementation --- [cite: 2]
class PagingSystem:
    def __init__(self, num_frames, page_size): # [cite: 5]
        self.num_frames = num_frames # [cite: 6]
        self.page_size = page_size # [cite: 7]
        self.page_table = {} # [cite: 8] # process_id -> {page_number: frame_number} [cite: 9]
        self.frames = [None] * num_frames # [cite: 10, 11]

    def allocate_process(self, process_id, num_pages): # [cite: 12]
        print(f"Allocating {num_pages} pages for process {process_id}...") # [cite: 13]
        free_frames = [i for i, f in enumerate(self.frames) if f is None]
        if len(free_frames) < num_pages:
            print("Error: Not enough frames available!") # [cite: 14]
            return
            
        self.page_table[process_id] = {} # [cite: 15]
        for i in range(num_pages): # [cite: 16]
            frame = free_frames[i] # [cite: 17]
            self.frames[frame] = (process_id, i) # [cite: 18]
            self.page_table[process_id][i] = frame
        print(f"Process {process_id} allocated successfully!") # [cite: 19]

    def translate_address(self, process_id, logical_address): # [cite: 20]
        page_number = logical_address // self.page_size
        offset = logical_address % self.page_size
        
        if process_id not in self.page_table or page_number not in self.page_table[process_id]: # [cite: 21]
            print(f"Page fault! Page {page_number} of process {process_id} not in frame.") # [cite: 21]
            return None
            
        frame_number = self.page_table[process_id][page_number] # [cite: 22]
        physical_address = frame_number * self.page_size + offset # [cite: 23]
        print(f"Logical address {logical_address} -> Physical address {physical_address}") # [cite: 24]
        return physical_address # [cite: 25]

# --- Member 4 - Segmentation Implementation --- [cite: 26]
class SegmentationSystem:
    def __init__(self): # [cite: 29]
        self.segment_table = {} # process_id -> {segment_number: (base, limit)} [cite: 30]
        self.memory = {} # [cite: 30]

    def allocate_segment(self, process_id, segment_number, base, limit): # [cite: 31]
        if process_id not in self.segment_table: # [cite: 32]
            self.segment_table[process_id] = {} # [cite: 33]
        self.segment_table[process_id][segment_number] = (base, limit) # [cite: 34]
        print(f"Allocated segment {segment_number} for process {process_id}: base={base}, limit={limit}") # [cite: 35]

    def translate_address(self, process_id, segment_number, offset): # [cite: 36]
        if process_id not in self.segment_table or segment_number not in self.segment_table[process_id]: # [cite: 37]
            print("Error: Invalid segment number!") # [cite: 37]
            return None # [cite: 38]
            
        base, limit = self.segment_table[process_id][segment_number] # [cite: 39, 41]
        
        if offset >= limit: # [cite: 40]
            print("Error: Offset out of bounds!") # [cite: 42]
            return None # [cite: 43]
            
        physical_address = base + offset # [cite: 44, 45]
        print(f"Logical address (Segment {segment_number}, Offset {offset}) -> Physical address {physical_address}") # [cite: 46]
        return physical_address # [cite: 46]

# --- Member 5 - Memory Allocation / Deallocation --- [cite: 47]
class MemoryAllocator:
    def __init__(self, total_memory): # [cite: 50]
        self.total_memory = total_memory # [cite: 51, 52]
        self.free_blocks = [(0, total_memory)] # (start, size) [cite: 53]
        self.allocated = {} # process_id -> (start, size) [cite: 53, 55]

    def first_fit(self, process_id, size): # [cite: 54]
        for i, (start, free_size) in enumerate(self.free_blocks): # [cite: 56]
            if free_size >= size: # [cite: 57]
                self.allocated[process_id] = (start, size) # [cite: 58]
                if free_size == size: # [cite: 59]
                    self.free_blocks.pop(i) # [cite: 60]
                else:
                    self.free_blocks[i] = (start + size, free_size - size) # [cite: 61, 62]
                print(f"Process {process_id} allocated {size} units using First Fit at {start}") # [cite: 63]
                return
        print("Error: Not enough memory (First Fit).") # [cite: 64]

    def best_fit(self, process_id, size): # [cite: 65]
        best_index = -1 # [cite: 66]
        best_size = float('inf') # [cite: 67] corrected from None
        
        for i, (start, free_size) in enumerate(self.free_blocks): # [cite: 68]
            if free_size >= size and free_size < best_size: # [cite: 69]
                best_index, best_size = i, free_size
                
        if best_index == -1: # [cite: 70]
            print("Error: Not enough memory (Best Fit).") # [cite: 71]
            return
            
        start, free_size = self.free_blocks[best_index] # [cite: 72]
        self.allocated[process_id] = (start, size) # [cite: 72]
        
        if free_size == size: # [cite: 72]
            self.free_blocks.pop(best_index) # [cite: 74]
        else:
            self.free_blocks[best_index] = (start + size, free_size - size) # [cite: 73, 75, 76]
        
        print(f"Process {process_id} allocated {size} units using Best Fit at {start}") # [cite: 77]

    def free(self, process_id): # [cite: 78]
        if process_id not in self.allocated: # [cite: 79]
            print("Error: Process not found!") # [cite: 80]
            return
            
        start, size = self.allocated.pop(process_id) # [cite: 81]
        self.free_blocks.append((start, size)) # [cite: 82]
        self.free_blocks.sort() # [cite: 83]
        # (Merging adjacent free blocks would be a good addition here)
        print(f"Process {process_id} deallocated memory block from {start} to {start + size}.") # [cite: 84]

    def print_map(self):
        """Helper function to show current memory state."""
        print("\n--- Memory Map ---")
        print(f"Total Memory: {self.total_memory}")
        print("Allocated Blocks:")
        if not self.allocated:
            print("  (None)")
        for pid, (start, size) in self.allocated.items():
            print(f"  PID {pid}: Start {start}, Size {size}")
        
        print("Free Blocks:")
        if not self.free_blocks:
            print("  (None - Full)")
        for (start, size) in self.free_blocks:
            print(f"  Free: Start {start}, Size {size}")
        print("-" * 18)