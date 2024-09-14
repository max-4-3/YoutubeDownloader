import multiprocessing
import time


class Spinner:

    def __init__(self, msg: str = "", speed: float = 0.1) -> None:
        self.msg = msg
        self.speed = speed
        self.process = None  # Start with no process

    def spin(self):
        spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        n = 0
        while True:
            print(f'\r{spinner[n]} {f"[{self.msg}]" if self.msg else ""}', end="")
            n += 1
            if n >= len(spinner):
                n = 0
            time.sleep(self.speed)

    def start(self):
        if self.process and self.process.is_alive():
            self.process.terminate()

        # Reinitialize the process each time you start
        self.process = multiprocessing.Process(
            target=self.spin,
            args=(),
            name="Spinner"
        )
        self.process.start()

    def stop(self):
        if self.process and self.process.is_alive():
            self.process.kill()  # Terminate the process
            self.process = None  # Reset the process object
        else:
            print("Warning: Spinner is not running!")