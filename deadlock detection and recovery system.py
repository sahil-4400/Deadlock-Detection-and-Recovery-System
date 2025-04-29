import tkinter as tk
from tkinter import messagebox

class Process:
    def __init__(self, pid, max_resources):
        self.pid = pid
        self.max_resources = max_resources
        self.allocated = [0] * len(max_resources)
        self.need = max_resources[:]

class DeadlockDetector:
    def __init__(self, processes, available_resources):
        self.processes = processes
        self.available_resources = available_resources

    def is_safe(self):
        work = self.available_resources[:]
        finish = [False] * len(self.processes)
        safe_sequence = []

        while len(safe_sequence) < len(self.processes):
            progress_made = False
            for i, process in enumerate(self.processes):
                if not finish[i] and all(process.need[j] <= work[j] for j in range(len(work))):
                    work = [work[j] + process.allocated[j] for j in range(len(work))]
                    finish[i] = True
                    safe_sequence.append(process.pid)
                    progress_made = True
            if not progress_made:
                break

        return finish, safe_sequence

    def detect_deadlock(self):
        finish, safe_sequence = self.is_safe()
        if all(finish):
            return False, safe_sequence  # No deadlock
        else:
            return True, []  # Deadlock detected

class DeadlockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Deadlock Detection and Recovery System")
        
        self.processes = []
        self.available_resources = []

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Number of Resources:").grid(row=0, column=0)
        self.resource_entry = tk.Entry(self.root)
        self.resource_entry.grid(row=0, column=1)

        tk.Label(self.root, text="Available Resources (comma-separated):").grid(row=1, column=0)
        self.available_entry = tk.Entry(self.root)
        self.available_entry.grid(row=1, column=1)

        tk.Button(self.root, text="Set Resources", command=self.set_resources).grid(row=2, columnspan=2)

        tk.Label(self.root, text="Process ID:").grid(row=3, column=0)
        self.pid_entry = tk.Entry(self.root)
        self.pid_entry.grid(row=3, column=1)

        tk.Label(self.root, text="Max Resources (comma-separated):").grid(row=4, column=0)
        self.max_entry = tk.Entry(self.root)
        self.max_entry.grid(row=4, column=1)

        tk.Button(self.root, text="Add Process", command=self.add_process).grid(row=5, columnspan=2)
        tk.Button(self.root, text="Check Deadlock", command=self.check_deadlock).grid(row=6, columnspan=2)

    def set_resources(self):
        resources = self.available_entry.get().split(',')
        self.available_resources = [int(r) for r in resources]

    def add_process(self):
        pid = self.pid_entry.get()
        max_resources = self.max_entry.get().split(',')
        max_resources = [int(r) for r in max_resources]
        self.processes.append(Process(pid, max_resources))

    def check_deadlock(self):
        detector = DeadlockDetector(self.processes, self.available_resources)
        deadlock, safe_sequence = detector.detect_deadlock()
        if deadlock:
            deadlock_processes = [process for process in self.processes if not all(process.need[j] <= self.available_resources[j] for j in range(len(self.available_resources)))]
            self.show_recovery_options(deadlock_processes)
        else:
            messagebox.showinfo("No Deadlock", f"System is in a safe state. Safe sequence: {safe_sequence}")

    def show_recovery_options(self, deadlock_processes):
        # Show the reason for deadlock
        messagebox.showinfo("Deadlock Detected", "Deadlock has been detected!")

        # Create a new window for recovery options
        recovery_window = tk.Toplevel(self.root)
        recovery_window.title("Deadlock Recovery Options")

        tk.Label(recovery_window, text="Select a process to terminate:").pack()

        for process in deadlock_processes:
            tk.Button(recovery_window, text=process.pid, command=lambda p=process: self.terminate_process(p)).pack()
            tk.Label(recovery_window, text="Select a process to preempt resources from:").pack()
        
        for process in deadlock_processes:
            tk.Button(recovery_window, text=f"Preempt from {process.pid}", command=lambda p=process: self.preempt_resources(p)).pack()

        tk.Button(recovery_window, text="Cancel", command=recovery_window.destroy).pack()

    def terminate_process(self, process):
        # Remove the process from the system
        self.processes.remove(process)
        messagebox.showinfo("Process Terminated", f"Process {process.pid} has been terminated.")
    
    def preempt_resources(self, process):
        # Show current allocation and allow user to specify how many resources to preempt
        preemption_window = tk.Toplevel(self.root)
        preemption_window.title(f"Preempt Resources from {process.pid}")

        tk.Label(preemption_window, text="Current Allocation:").pack()
        tk.Label(preemption_window, text=f"Resource Allocation: {process.allocated}").pack()

        tk.Label(preemption_window, text="Enter number of resources to preempt (comma-separated):").pack()
        preempt_entry = tk.Entry(preemption_window)
        preempt_entry.pack()

        def confirm_preemption():
            preempt_values = list(map(int, preempt_entry.get().split(',')))
            for i in range(len(process.allocated)):
                if preempt_values[i] > process.allocated[i]:
                    messagebox.showerror("Error", "Cannot preempt more resources than allocated.")
                    return
                # Update the allocated and available resources
                process.allocated[i] -= preempt_values[i]
                self.available_resources[i] += preempt_values[i]
            messagebox.showinfo("Resources Preempted", f"Resources preempted from {process.pid}.")
            preemption_window.destroy()

        tk.Button(preemption_window, text="Confirm Preemption", command=confirm_preemption).pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = DeadlockApp(root)
    root.mainloop()
