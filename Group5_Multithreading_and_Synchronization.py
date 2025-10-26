from collections import deque
import sys

# ----------------------------- Core Simulation Types -----------------------------
class SimThread:
    NEW, READY, RUNNING, BLOCKED, TERMINATED = 'NEW','READY','RUNNING','BLOCKED','TERMINATED'

    def __init__(self, tid, instructions):
        self.tid = tid
        self.instructions = deque(instructions)
        self.state = SimThread.NEW
        self.pc = 0

    def is_done(self):
        return len(self.instructions) == 0

    def pop_inst(self):
        if self.instructions:
            self.pc += 1
            return self.instructions.popleft()
        return None

# ----------------------------- Synchronization Primitives -----------------------------
class Mutex:
    def __init__(self, name):
        self.name = name
        self.owner = None
        self.wait_queue = deque()

    def acquire(self, thread, scheduler):
        if self.owner is None:
            self.owner = thread
            print(f"[{scheduler.time:03}] {thread.tid} acquired mutex {self.name}")
            return True
        else:
            print(f"[{scheduler.time:03}] {thread.tid} blocked on mutex {self.name}")
            self.wait_queue.append(thread)
            thread.state = SimThread.BLOCKED
            return False

    def release(self, thread, scheduler):
        if self.owner != thread:
            raise RuntimeError(f"{thread.tid} tried to release mutex {self.name} but is not owner")
        print(f"[{scheduler.time:03}] {thread.tid} released mutex {self.name}")
        if self.wait_queue:
            nxt = self.wait_queue.popleft()
            self.owner = nxt
            nxt.state = SimThread.READY
            scheduler.ready_queue.append(nxt)
            print(f"[{scheduler.time:03}] {nxt.tid} unblocked and granted mutex {self.name}")
        else:
            self.owner = None

class Semaphore:
    def __init__(self, name, initial):
        self.name = name
        self.value = initial
        self.wait_queue = deque()

    def wait(self, thread, scheduler):
        if self.value > 0:
            self.value -= 1
            print(f"[{scheduler.time:03}] {thread.tid} acquired semaphore {self.name} (value={self.value})")
            return True
        else:
            print(f"[{scheduler.time:03}] {thread.tid} blocked on semaphore {self.name} (value={self.value})")
            self.wait_queue.append(thread)
            thread.state = SimThread.BLOCKED
            return False

    def signal(self, scheduler):
        self.value += 1
        print(f"[{scheduler.time:03}] semaphore {self.name} signaled (value={self.value})")
        if self.wait_queue:
            nxt = self.wait_queue.popleft()
            nxt.state = SimThread.READY
            scheduler.ready_queue.append(nxt)
            self.value -= 1
            print(f"[{scheduler.time:03}] {nxt.tid} unblocked by semaphore {self.name} (value now={self.value})")

# ----------------------------- Scheduler -----------------------------
class Scheduler:
    def __init__(self, time_slice=1):
        self.time_slice = time_slice
        self.ready_queue = deque()
        self.time = 0

    def add_thread(self, thread):
        thread.state = SimThread.READY
        self.ready_queue.append(thread)

    def run(self, max_ticks=1000):
        ticks = 0
        while self.ready_queue and ticks < max_ticks:
            thread = self.ready_queue.popleft()
            if thread.state == SimThread.BLOCKED:
                continue
            thread.state = SimThread.RUNNING
            inst = thread.pop_inst()
            print(f"[{self.time:03}] RUNNING {thread.tid} -> {inst}")
            self.execute_instruction(thread, inst)
            if thread.is_done():
                thread.state = SimThread.TERMINATED
                print(f"[{self.time:03}] {thread.tid} terminated")
            elif thread.state == SimThread.RUNNING:
                thread.state = SimThread.READY
                self.ready_queue.append(thread)
            self.time += 1
            ticks += 1
        if ticks >= max_ticks:
            print("[!] reached max ticks, stopping simulation")

    def execute_instruction(self, thread, inst):
        op = inst[0]
        if op == 'COMPUTE':
            pass
        elif op == 'ENTER_MUTEX':
            mutex = inst[1]
            ok = mutex.acquire(thread, self)
            if not ok: return
        elif op == 'EXIT_MUTEX':
            mutex = inst[1]
            mutex.release(thread, self)
        elif op == 'WAIT_SEM':
            sem = inst[1]
            ok = sem.wait(thread, self)
            if not ok: return
        elif op == 'SIGNAL_SEM':
            sem = inst[1]
            sem.signal(self)
        elif op == 'INC':
            key = inst[1]
            self.shared[key] = self.shared.get(key, 0) + 1
            print(f"[{self.time:03}] {thread.tid} incremented {key} -> {self.shared[key]}")
        elif op == 'YIELD':
            pass
        else:
            raise ValueError(f"Unknown instruction: {op}")

class DemoScheduler(Scheduler):
    def __init__(self, time_slice=1):
        super().__init__(time_slice)
        self.shared = {}

# ----------------------------- Demo Scenarios -----------------------------
def make_counter_threads(increments=5, use_mutex=None):
    insts = []
    for _ in range(increments):
        if use_mutex: insts.append(('ENTER_MUTEX', use_mutex))
        insts.append(('COMPUTE',))
        insts.append(('INC', 'counter'))
        if use_mutex: insts.append(('EXIT_MUTEX', use_mutex))
        insts.append(('YIELD',))
    t1 = SimThread('T1', insts.copy())
    t2 = SimThread('T2', insts.copy())
    return [t1, t2]

def demo_race(increments=5):
    print('\\n========== RACE (no synchronization) ==========')
    sched = DemoScheduler()
    threads = make_counter_threads(increments=increments)
    for t in threads:
        sched.add_thread(t)
    sched.run()
    print(f"Final counter (unsynchronized): {sched.shared.get('counter', 0)}")

def demo_mutex(increments=5):
    print('\\n========== MUTEX PROTECTED ==========')
    m = Mutex('M')
    sched = DemoScheduler()
    threads = make_counter_threads(increments=increments, use_mutex=m)
    for t in threads:
        sched.add_thread(t)
    sched.run()
    print(f"Final counter (mutex): {sched.shared.get('counter', 0)}")

def demo_semaphore(increments=3):
    print('\\n========== SEMAPHORE DEMO ==========')
    pool = Semaphore('POOL', initial=2)
    def make_worker(name, times=3):
        insts = []
        for _ in range(times):
            insts.append(('WAIT_SEM', pool))
            insts.append(('COMPUTE',))
            insts.append(('SIGNAL_SEM', pool))
            insts.append(('YIELD',))
        return SimThread(name, insts)
    sched = Scheduler()
    for i in range(4):
        t = make_worker(f'W{i+1}', times=increments)
        sched.add_thread(t)
    sched.run()

def demo_producer_consumer(items=3):
    print('\\n========== PRODUCER-CONSUMER ==========')
    mutex = Mutex('buf_mutex')
    empty = Semaphore('empty', 2)
    full = Semaphore('full', 0)

    def make_producer(name, to_produce=items):
        insts = []
        for _ in range(to_produce):
            insts.append(('WAIT_SEM', empty))
            insts.append(('ENTER_MUTEX', mutex))
            insts.append(('INC', 'produced'))
            insts.append(('EXIT_MUTEX', mutex))
            insts.append(('SIGNAL_SEM', full))
            insts.append(('YIELD',))
        return SimThread(name, insts)

    def make_consumer(name, to_consume=items):
        insts = []
        for _ in range(to_consume):
            insts.append(('WAIT_SEM', full))
            insts.append(('ENTER_MUTEX', mutex))
            insts.append(('INC', 'consumed'))
            insts.append(('EXIT_MUTEX', mutex))
            insts.append(('SIGNAL_SEM', empty))
            insts.append(('YIELD',))
        return SimThread(name, insts)

    sched = DemoScheduler()
    sched.add_thread(make_producer('P1', items))
    sched.add_thread(make_consumer('C1', items))
    sched.run()
    print(f"Produced: {sched.shared.get('produced', 0)}, Consumed: {sched.shared.get('consumed', 0)}")

# ----------------------------- Main -----------------------------
if __name__ == '__main__':
    arg = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if arg == 'race':
        demo_race()
    elif arg == 'mutex_demo':
        demo_mutex()
    elif arg == 'semaphore_demo':
        demo_semaphore()
    elif arg == 'prod_cons':
        demo_producer_consumer()
    elif arg == 'all':
        demo_race()
        demo_mutex()
        demo_semaphore()
        demo_producer_consumer()
    else:
        print("Use: race | mutex_demo | semaphore_demo | prod_cons | all")
