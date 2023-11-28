import tkinter as tk
from tkinter import filedialog
import subprocess

class PeopleCountingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("People Counting Application")

        self.prototxt_label = tk.Label(root, text="Prototxt file:")
        self.prototxt_label.pack()

        self.prototxt_entry = tk.Entry(root)
        self.prototxt_entry.pack(fill=tk.X)

        self.caffemodel_label = tk.Label(root, text="Caffemodel file:")
        self.caffemodel_label.pack()

        self.caffemodel_entry = tk.Entry(root)
        self.caffemodel_entry.pack(fill=tk.X)

        self.input_label = tk.Label(root, text="Input video file:")
        self.input_label.pack()

        self.input_entry = tk.Entry(root)
        self.input_entry.pack(fill=tk.X)

        self.output_label = tk.Label(root, text="Output video file:")
        self.output_label.pack()

        self.output_entry = tk.Entry(root)
        self.output_entry.pack(fill=tk.X)

        self.run_button = tk.Button(root, text="Run", command=self.run_command)
        self.run_button.pack()

        # Allow the window to dynamically resize
        root.pack_propagate(False)

    def run_command(self):
        prototxt = self.prototxt_entry.get()
        caffemodel = self.caffemodel_entry.get()
        input_file = self.input_entry.get()
        output_file = self.output_entry.get()

        if not all([prototxt, caffemodel, input_file, output_file]):
            tk.messagebox.showerror("Error", "All fields must be filled.")
            return

        command = [
            "python3",
            "PeopleCounting.py",
            "--prototxt",
            prototxt,
            "--caffemodel",
            caffemodel,
            "--input",
            input_file,
            "--output",
            output_file
        ]

        try:
            subprocess.run(command, check=True)
            tk.messagebox.showinfo("Success", "Command executed successfully!")
        except subprocess.CalledProcessError as e:
            tk.messagebox.showerror("Error", f"Error executing command: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PeopleCountingApp(root)
    root.mainloop()
