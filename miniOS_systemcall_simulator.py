import threading
import time
import shlex
import sys
from typing import Callable, Dict, List, Optional

class ProcessState:
    READY = 'READY'
    RUNNING = 'RUNNING'
    BLOCKED = 'BLOCKED'
    EXITED = 'EXITED'

class Process:
    def __init__(self, pid:int, ppid:int, program:str, args:List[str], ptable:'ProcessTable'):
        self.pid = pid
        self.ppid = ppid
        self.program = program
        self.args = args[:]  
        self.state = ProcessState.READY
        self.exit_code: Optional[int] = None
        self.children: List[int] = []
        self._ptable = ptable
        self._cond = threading.Condition()
        self._thread: Optional[threading.Thread] = None

    def set_thread(self, t:threading.Thread):
        self._thread = t

    def wait_until_exit(self, timeout:Optional[float]=None):
        with self._cond:
            if self.state != ProcessState.EXITED:
                self._cond.wait(timeout=timeout)

    def notify_exit(self):
        with self._cond:
            self._cond.notify_all()

    def __repr__(self):
        return f"Process(pid={self.pid}, ppid={self.ppid}, prog={self.program}, args={self.args}, state={self.state}, exit={self.exit_code})"

class ProcessTable:
    def __init__(self):
        self._lock = threading.Lock()
        self._next_pid = 100
        self._procs: Dict[int, Process] = {}

    def allocate_pid(self) -> int:
        with self._lock:
            pid = self._next_pid
            self._next_pid += 1
            return pid

    def add(self, proc: Process):
        with self._lock:
            self._procs[proc.pid] = proc

    def get(self, pid:int) -> Optional[Process]:
        with self._lock:
            return self._procs.get(pid)

    def list_all(self) -> List[Process]:
        with self._lock:
            return list(self._procs.values())

    def remove(self, pid:int):
        with self._lock:
            if pid in self._procs:
                del self._procs[pid]

ProgramCallable = Callable[['ProcEnv'], None]
PROGRAMS: Dict[str, ProgramCallable] = {}

def register_program(name:str):
    def deco(fn:ProgramCallable):
        PROGRAMS[name] = fn
        return fn
    return deco

class ExecReplacement(Exception):
    def __init__(self, prog_name, args):
        super().__init__(f"exec -> {prog_name}")
        self.prog_name = prog_name
        self.args = args

class ProcEnv:
    def __init__(self, proc:Process, ptable:ProcessTable):
        self._proc = proc
        self._ptable = ptable
        self._fork_ret: Optional[int] = None

    def getpid(self) -> int:
        return self._proc.pid

    def getppid(self) -> int:
        return self._proc.ppid

    def fork(self) -> int:
        parent = self._proc
        child_pid = self._ptable.allocate_pid()
        child = Process(pid=child_pid, ppid=parent.pid, program=parent.program, args=list(parent.args), ptable=self._ptable)
        self._ptable.add(child)
        parent.children.append(child.pid)

        def child_runner():
            child.state = ProcessState.RUNNING
            env = ProcEnv(child, self._ptable)
            env._fork_ret = 0  # child sees 0
            try:
                prog = PROGRAMS.get(child.program)
                if not prog:
                    print(f"[child {child.pid}] exec failed: program '{child.program}' not found")
                    child.exit_code = 1
                else:
                    prog(env)
            except SystemExit as se:
                child.exit_code = getattr(se,'code',0)
            except Exception as e:
                print(f"[child {child.pid}] crashed: {e}")
                child.exit_code = 1
            child.state = ProcessState.EXITED
            child.notify_exit()

        t = threading.Thread(target=child_runner, name=f"proc-{child_pid}", daemon=True)
        child.set_thread(t)
        t.start()

        return child_pid

    def exec(self, program_name:str, *args:str):
        if program_name not in PROGRAMS:
            raise FileNotFoundError(f"program '{program_name}' not found")
        self._proc.program = program_name
        self._proc.args = list(args)
        raise ExecReplacement(program_name, args)

    def wait(self, child_pid:int) -> int:
        proc = self._proc
        if child_pid not in proc.children:
            raise ValueError(f"pid {child_pid} is not a child of {proc.pid}")
        child = self._ptable.get(child_pid)
        if child is None:
            return 0
        child.wait_until_exit()
        return child.exit_code if child.exit_code is not None else 0

    def exit(self, code:int=0):
        p = self._proc
        p.exit_code = code
        p.state = ProcessState.EXITED
        p.notify_exit()
        raise SystemExit(code)

    def fork_return_value(self) -> Optional[int]:
        return self._fork_ret


@register_program('prog_echo')
def prog_echo(env:ProcEnv):
    print(f"[pid {env.getpid()}] echo:", *env._proc.args)
    env.exit(0)

@register_program('prog_count')
def prog_count(env:ProcEnv):
    n = int(env._proc.args[0]) if env._proc.args else 5
    for i in range(1, n+1):
        print(f"[pid {env.getpid()}] count {i}/{n}")
        time.sleep(1)
    env.exit(0)

@register_program('prog_sleep_exit')
def prog_sleep_exit(env:ProcEnv):
    s = int(env._proc.args[0]) if env._proc.args else 2
    code = int(env._proc.args[1]) if len(env._proc.args)>1 else 0
    time.sleep(s)
    print(f"[pid {env.getpid()}] slept {s}s, exiting {code}")
    env.exit(code)

@register_program('prog_parent_demo')
def prog_parent_demo(env:ProcEnv):
    print(f"[parent {env.getpid()}] starting demo")
    child_pid = env.fork()
    # after fork: parent continues here (child runs in separate thread)
    fork_ret = env.fork_return_value()
    # fork_return_value is set only for child runner; for parent it is None here
    if fork_ret == 0:
        # child (this branch will actually execute inside child's thread only if we set _fork_ret)
        print(f"[child {env.getpid()}] child branch (fork returned 0)")
        env.exec('prog_echo', 'child-did-exec')
    else:
        # parent
        print(f"[parent {env.getpid()}] forked child {child_pid}; waiting...")
        code = env.wait(child_pid)
        print(f"[parent {env.getpid()}] child {child_pid} exited with code {code}")
        env.exit(0)


class Simulator:
    def __init__(self):
        self.ptable = ProcessTable()
        init = Process(pid=1, ppid=0, program='init', args=[], ptable=self.ptable)
        init.state = ProcessState.RUNNING
        self.ptable.add(init)
        self.init = init
        self._attached: Optional[int] = None

    def spawn(self, program:str, args:List[str]) -> int:
        pid = self.ptable.allocate_pid()
        proc = Process(pid=pid, ppid=self.init.pid, program=program, args=args, ptable=self.ptable)
        self.ptable.add(proc)
        self.init.children.append(pid)

        def runner():
            proc.state = ProcessState.RUNNING
            env = ProcEnv(proc, self.ptable)
            try:
                prog = PROGRAMS.get(proc.program)
                if not prog:
                    print(f"[proc {proc.pid}] program '{proc.program}' not found")
                    proc.exit_code = 1
                else:
                    while True:
                        try:
                            prog(env)
                            break
                        except ExecReplacement as ex:
                            proc.program = ex.prog_name
                            proc.args = list(ex.args)
                            prog = PROGRAMS.get(proc.program)
                            if prog is None:
                                print(f"[proc {proc.pid}] exec failed: {proc.program} not found")
                                proc.exit_code = 1
                                break
                            continue
            except SystemExit as se:
                proc.exit_code = getattr(se,'code',0)
            except Exception as e:
                print(f"[proc {proc.pid}] crashed: {e}")
                proc.exit_code = 1
            proc.state = ProcessState.EXITED
            proc.notify_exit()

        t = threading.Thread(target=runner, name=f"proc-{pid}", daemon=True)
        proc.set_thread(t)
        t.start()
        return pid

    def ps(self):
        for p in sorted(self.ptable.list_all(), key=lambda x: x.pid):
            print(f"PID {p.pid:4d} PPID {p.ppid:4d} STATE {p.state:7s} PROG {p.program} ARGS {p.args} EXIT {p.exit_code}")

    def tree(self):
        roots = [p for p in self.ptable.list_all() if p.ppid==0]
        def print_sub(pid:int, prefix=''):
            p = self.ptable.get(pid)
            if not p: return
            print(prefix + f"{p.pid} ({p.program}) [{p.state}]")
            for c in p.children:
                print_sub(c, prefix + '  ')
        for r in roots:
            print_sub(r.pid)

    def attach_interactive(self, pid:int):
        p = self.ptable.get(pid)
        if not p:
            print("no such pid")
            return
        print(f"Attached to pid {pid}. Commands: fork, exec <prog> [args], wait <pid>, getpid, getppid, exit <code>, show")
        while True:
            try:
                line = input(f"proc[{pid}]> ").strip()
            except EOFError:
                print()
                break
            if not line: continue
            parts = shlex.split(line)
            cmd = parts[0]
            env = ProcEnv(p, self.ptable)
            try:
                if cmd == 'fork':
                    child_pid = env.fork()
                    print(f"[attached parent {p.pid}] fork created child {child_pid}")
                elif cmd == 'exec':
                    if len(parts)<2:
                        print("usage: exec <program> [args...]")
                        continue
                    prog = parts[1]; args = parts[2:]
                    try:
                        env.exec(prog, *args)
                    except ExecReplacement:
                        print(f"exec requested: replaced program for pid {p.pid} -> {prog} {args}")
                elif cmd == 'wait':
                    if len(parts)!=2:
                        print("usage: wait <child-pid>")
                        continue
                    child_pid = int(parts[1])
                    code = env.wait(child_pid)
                    print(f"wait returned child {child_pid} exit code {code}")
                elif cmd == 'getpid':
                    print(env.getpid())
                elif cmd == 'getppid':
                    print(env.getppid())
                elif cmd == 'exit':
                    code = int(parts[1]) if len(parts)>1 else 0
                    try:
                        env.exit(code)
                    except SystemExit:
                        print(f"process {p.pid} set to exit {code}")
                        break
                elif cmd == 'show':
                    print(p)
                elif cmd == 'detach':
                    break
                else:
                    print("unknown attach command")
            except Exception as e:
                print("error:", e)
        print("detached")


def repl(sim:Simulator):
    print("Mini OS System Call Simulator (type 'help')")
    while True:
        try:
            line = input('> ').strip()
        except EOFError:
            print()
            break
        if not line: continue
        parts = shlex.split(line)
        cmd = parts[0]
        if cmd == 'help':
            print("commands: help, ps, tree, run <prog> [args...], attach <pid>, quit")
            print("programs available:", list(PROGRAMS.keys()))
        elif cmd == 'ps':
            sim.ps()
        elif cmd == 'tree':
            sim.tree()
        elif cmd == 'run':
            if len(parts)<2:
                print("usage: run <program> [args...]")
                continue
            prog = parts[1]; args = parts[2:]
            if prog not in PROGRAMS:
                print("program not found. available:", list(PROGRAMS.keys()))
                continue
            pid = sim.spawn(prog, args)
            print(f"spawned pid {pid} running {prog} {args}")
        elif cmd == 'attach':
            if len(parts)!=2:
                print("usage: attach <pid>")
                continue
            sim.attach_interactive(int(parts[1]))
        elif cmd in ('quit','exit'):
            print("exiting simulator")
            break
        else:
            print("unknown command; type help")

if __name__ == '__main__':
    sim = Simulator()

    # register an idle init program so init 'process' exists (we won't run it)
    @register_program('init')
    def _init(env:ProcEnv):
        while True:
            time.sleep(10)

    repl(sim)
