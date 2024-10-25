import threading
import time
import sys
from queue import Queue

class Spinner:
    def __init__(self, msg: str = "", speed: float = 0.1) -> None:
        self.msg = msg
        self.speed = speed
        self.spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.queue = Queue()
        self.stop_event = threading.Event()
        self.spinner_thread = threading.Thread(target=self._spin, daemon=True)
        self.original_stdout = sys.stdout

    def _spin(self):
        n = 0
        while not self.stop_event.is_set():
            # Move cursor up to redraw below new output
            sys.stdout.write(f'\r\033[K{self.spinner[n]} {self.msg}' if self.msg else f'\r\033[K{self.spinner[n]}')
            sys.stdout.flush()
            n = (n + 1) % len(self.spinner)
            time.sleep(self.speed)
            
            # Redraw if new text was output above
            if not self.queue.empty():
                sys.stdout.write('\033[K')  # Clear line
                self._print_queued_output()
                sys.stdout.write(f'\r{self.spinner[n]} {f"[{self.msg}]" if self.msg else ""}')
                sys.stdout.flush()

    def _print_queued_output(self):
        while not self.queue.empty():
            line = self.queue.get()
            sys.stdout.write(f'\n{line}\n')  # Print the queued line
            sys.stdout.flush()

    @property
    def is_running(self):
        """Returns True if the spinner thread is currently active."""
        return self.spinner_thread.is_alive() if self.spinner_thread else False

    def start(self):
        # Start spinner thread
        if not self.spinner_thread.is_alive():
            self.stop_event.clear()
            self.spinner_thread = threading.Thread(target=self._spin, daemon=True)
            self.spinner_thread.start()

    def stop(self):
        # Stop spinner thread
        if self.spinner_thread.is_alive():
            self.stop_event.set()
            self.spinner_thread.join()
            sys.stdout.write('\r\033[K')  # Clear spinner line
            sys.stdout.write('\n')
            sys.stdout.flush()
        sys.stdout = self.original_stdout  # Restore stdout

    def write(self, message):
        # Queue messages for output above spinner
        self.queue.put(message)

# Usage example
if __name__ == "__main__":
    spinner = Spinner("Loading...", 0.1)
    spinner.start()

    # Simulate printing other messages while spinner is running
    for i in range(5):
        time.sleep(1)
        spinner.write(f"Output message {i + 1}")

    spinner.stop()
