import tkinter as tk
from tkinter import scrolledtext
import sys
import threading
from main import lambda_handler
import queue

class RedirectText:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.queue = queue.Queue()
        self.update_timer = None

    def write(self, string):
        self.queue.put(string)
        if self.update_timer is None:
            self.update_timer = self.text_widget.after(100, self.update_text)

    def update_text(self):
        while not self.queue.empty():
            string = self.queue.get()
            self.text_widget.configure(state='normal')
            self.text_widget.insert(tk.END, string)
            self.text_widget.see(tk.END)
            self.text_widget.configure(state='disabled')
        self.update_timer = None

    def flush(self):
        pass

class RobotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Leilões Imóvel Robot")
        self.root.geometry("800x600")
        
        # Create main frame
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create title label
        title_label = tk.Label(main_frame, text="Leilões Imóvel Robot", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Create start button
        self.start_button = tk.Button(main_frame, text="Iniciar Robot", command=self.start_robot, 
                                    bg="#4CAF50", fg="white", font=("Arial", 12))
        self.start_button.pack(pady=10)
        
        # Create log text area
        self.log_text = scrolledtext.ScrolledText(main_frame, height=20, width=80)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_text.configure(state='disabled')
        
        # Redirect stdout to the text widget
        self.redirect = RedirectText(self.log_text)
        sys.stdout = self.redirect

    def start_robot(self):
        self.start_button.configure(state='disabled')
        self.log_text.configure(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state='disabled')
        
        # Run the robot in a separate thread
        thread = threading.Thread(target=self.run_robot)
        thread.daemon = True
        thread.start()

    def run_robot(self):
        try:
            lambda_handler({}, {})
        except Exception as e:
            print(f"Erro: {str(e)}")
        finally:
            self.start_button.configure(state='normal')

if __name__ == "__main__":
    root = tk.Tk()
    app = RobotGUI(root)
    root.mainloop() 