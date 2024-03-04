import tkinter as tk
from tkinter import Toplevel, scrolledtext, Frame, Scale, Button, Checkbutton, Label, Entry
from subprocess import Popen, PIPE
import threading
import re
import time
import subprocess


class PingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        button_frame = Frame(self)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.exit_button = Button(button_frame, text="Exit", command=self.close_app)
        self.interval = 5
        self.title("Ping Application")
        self.green_threshold = 50  # Default green threshold
        self.geometry("160x1000")  # Initial size, can show last 50 replies
        self.overrideredirect(True)  # Remove the title bar
        self.attributes("-alpha", 0.5)
        self.ip_address = "8.8.8.8"  # Default IP address
        self.always_on_top_var = tk.BooleanVar(value=True)
        self.set_always_on_top()
        # self.always_on_top_var = tk.BooleanVar(value=True)
        # Make the window draggable
        self.bind("<Button-1>", self.start_move)
        self.bind("<ButtonRelease-1>", self.stop_move)
        self.bind("<B1-Motion>", self.do_move)
        
        custom_text = "Github: aliakbarhoriat"
        custom_label = Label(self, text=custom_text)
        custom_label.pack(side=tk.BOTTOM, fill=tk.X, pady=(0, 5))  # Adjust padding as needed
        
        # Main frame for buttons
        button_frame = Frame(self)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Start-Stop Button
        self.start_stop_button = Button(button_frame, text="Start", command=self.toggle_pinging)
        self.start_stop_button.pack(side=tk.LEFT, padx=5)

        # Options Button
        self.options_button = Button(button_frame, text="Options", command=self.show_options)
        self.options_button.pack(side=tk.LEFT, padx=5)

        # Exit Button
        self.exit_button = Button(button_frame, text="Exit", command=self.close_app)
        self.exit_button.pack(side=tk.LEFT, padx=5)

        # ScrolledText for Ping Output, with background color set to black
        self.output_text = scrolledtext.ScrolledText(self, wrap=tk.WORD, height=25, bg="black", fg="gray")
        self.output_text.pack(expand=True, fill=tk.BOTH)

        # Thread control
        self.ping_thread = None
        self.pinging = False

        # Options Window (not opened until 'Options' button is clicked)
        self.options_window = None

    def show_options(self):
        # Create a new top-level window for the options if it does not exist
        if not self.options_window:
            self.options_window = Toplevel(self)
            self.options_window.title("Options")
            # Additional setup for self.options_window
            self.options_window.protocol("WM_DELETE_WINDOW", self.on_close_options_window)

            # Frame for IP Address Entry
            ip_frame = Frame(self.options_window)
            ip_frame.pack(pady=5, padx=5, fill='x')
            Label(ip_frame, text="IP:").pack(side=tk.LEFT)
            self.ip_entry = Entry(ip_frame, width=15)
            self.ip_entry.pack(side=tk.LEFT, expand=True, fill='x')
            # Insert default IP address into the ip_entry field
            self.ip_entry.insert(0, "8.8.8.8")

            # Frame for Interval Entry
            interval_frame = Frame(self.options_window)
            interval_frame.pack(pady=5, padx=5, fill='x')
            Label(interval_frame, text="Interval (s):").pack(side=tk.LEFT)
            self.interval_entry = Entry(interval_frame, width=5)
            self.interval_entry.pack(side=tk.LEFT, expand=True, fill='x')
            self.interval_entry.insert(0, "6")

            # Frame for Always on Top Checkbox
            always_on_top_frame = Frame(self.options_window)
            always_on_top_frame.pack(pady=5, padx=5, fill='x')
            # self.attributes("-topmost", self.always_on_top_var.get())
            # self.always_on_top_var = tk.BooleanVar(value=True)  # Initialize with True for default checked
            Checkbutton(always_on_top_frame, text="Always on Top", variable=self.always_on_top_var).pack(side=tk.LEFT)

            # Frame for Opacity Scale
            opacity_frame = Frame(self.options_window)
            opacity_frame.pack(pady=5, padx=5, fill='x')
            Label(opacity_frame, text="Opacity:").pack(side=tk.LEFT)
            self.opacity_scale = Scale(opacity_frame, from_=0.1, to=1.0, resolution=0.1, orient=tk.HORIZONTAL)
            self.opacity_scale.set(1.0)  # Set initial opacity to 100%
            self.opacity_scale.pack(side=tk.LEFT, expand=True, fill='x')

            # Frame for Green Threshold Entry
            green_threshold_frame = Frame(self.options_window)
            green_threshold_frame.pack(pady=5, padx=5, fill='x')
            Label(green_threshold_frame, text="Green Threshold (ms):").pack(side=tk.LEFT)
            self.green_threshold_entry = Entry(green_threshold_frame, width=5)
            self.green_threshold_entry.pack(side=tk.LEFT, expand=True, fill='x')
            self.green_threshold_entry.insert(0, "50")  # Default value for green threshold

            # Apply Button
            Button(self.options_window, text="Apply", command=self.apply_options).pack(pady=10)

           

    def on_close_options_window(self):
        if self.options_window is not None:
            self.options_window.destroy()  # This will close the options window
            self.options_window = None     # Reset the reference to indicate the window is closed
            
       
    def close_app(self):
        # This method will be called when the "Exit" button is pressed
        self.destroy()  # Closes the application window
    def apply_options(self):
        # Check if the options window (and thus the entry widgets) still exists
        if self.options_window:
            try:
                # Apply IP Address
                self.ip_address = self.ip_entry.get().strip()
                
                # Apply Interval
                self.interval = int(self.interval_entry.get().strip())
                
                # Apply Green Threshold
                self.green_threshold = int(self.green_threshold_entry.get().strip())
                
                # Apply Always on Top and Opacity
                self.set_always_on_top()
                self.adjust_opacity(self.opacity_scale.get())
                
            except ValueError as e:
                print(f"Invalid input: {e}")
                return  # Exit the method to prevent applying incorrect settings.
            
            self.on_close_options_window()

     

    def set_always_on_top(self):
        # Set or unset the window's 'always on top' state
        if self.always_on_top_var.get():
            self.attributes("-topmost", True)
        else:
            self.attributes("-topmost", False)

    def adjust_opacity(self, value):
        # Adjust the window's opacity
        self.attributes("-alpha", float(value))
        

    def on_close_options_window(self):
        if self.options_window is not None:
            self.options_window.destroy()  # This will close the options window
            self.options_window = None     # Reset the reference to indicate the window is closed


    def toggle_pinging(self):
        if self.pinging:
            # Stop pinging
            self.pinging = False
            self.start_stop_button.config(text="Start")
        else:
            # Start pinging
            self.pinging = True
            self.start_stop_button.config(text="Stop")
            self.start_pinging()

    def start_pinging(self):
        ip = self.ip_address
        if not ip:
            print("No IP address specified.")
            return
        interval = self.interval  # Use the stored interval value
        if not self.ping_thread or not self.ping_thread.is_alive():
            self.ping_thread = threading.Thread(target=self.ping, args=(ip, interval), daemon=True)
            self.ping_thread.start()


    def ping(self, ip, interval):
        while self.pinging:
            process = subprocess.Popen(['ping', ip, '-n', '1'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            output, _ = process.communicate()
            if self.pinging:  # Check again to avoid race condition
                self.process_output(output)
            time.sleep(interval)



    def process_output(self, output):
        green_threshold = self.green_threshold  # Use the stored threshold
        
        if "Request timed out" in output or "Destination host unreachable" in output:
            message = "Request timed out"
            color = "red"
        else:
            match = re.search(r"time[<=](\d+)ms", output)
            if match:
                time_ms = int(match.group(1))
                if time_ms <= green_threshold:
                    color = "green"
                else:
                    color = "yellow"
                message = f"Reply in {time_ms} ms"
            else:
                message = "Ping failed"
                color = "red"
        
        # Safely update the GUI from another thread
        self.display_ping_result(message, color)


    def display_ping_result(self, message, color):
        # Insert the new message at the beginning (top) of the text area
        self.output_text.insert('1.0', message + "\n")
        self.output_text.tag_add(color, '1.0', '1.end')

        # Configure text color for different types of messages
        self.output_text.tag_configure("green", foreground="green")
        self.output_text.tag_configure("yellow", foreground="yellow")
        self.output_text.tag_configure("red", foreground="red")

        # Limit the display to the last 60 entries
        lines = int(self.output_text.index('end-1c').split('.')[0])
        if lines > 60:
            # If more than 60 lines, delete the oldest entries to maintain only the last 50
            self.output_text.delete('60.0', 'end')

        # Ensure the scrollbar adjusts to show the top (most recent) entry
        self.output_text.see('1.0')


    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

if __name__ == "__main__":
    app = PingApp()
    app.mainloop()
