import time
import os
import random
import base64
from PIL import ImageGrab
import schedule
from datetime import datetime, timedelta
import psutil
import win32gui
import win32process
from io import BytesIO
import ctypes
import sys
import logging
from pathlib import Path
import pystray
from PIL import Image
import threading
import json
from transformers import pipeline
import customtkinter as ctk
from typing import Optional

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Re-run the program with admin rights"""
    try:
        if sys.argv[-1] != 'asadmin':
            script = os.path.abspath(sys.argv[0])
            params = ' '.join([script] + sys.argv[1:] + ['asadmin'])
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
            sys.exit()
    except Exception as e:
        print(f"Failed to run as admin: {e}")
        sys.exit(1)

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)

class DurationSelector(ctk.CTk): 
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("FocusLock")
        self.geometry("300x500")
        self.resizable(False, False)  # Disable maximizing
        
        # Configure grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Create main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # App Logo/Icon
        try:
            logo_path = resource_path("logo.png")
            logo_image = Image.open(logo_path)
            logo_image = logo_image.resize((80,80), Image.Resampling.LANCZOS)
            self.logo = ctk.CTkImage(light_image=logo_image,
                                   dark_image=logo_image,
                                   size=(80,80))
            
            self.logo_label = ctk.CTkLabel(
                self.main_frame,
                image=self.logo,
                text=""
            )
            self.logo_label.grid(row=0, column=0, pady=(0, 10))
        except Exception as e:
            logging.error(f"Error loading logo: {e}")
            self.logo_label = None

        # Title label
        self.title_label = ctk.CTkLabel(
            self.main_frame, 
            text="FocusLock",
            font=("Arial", 24, "bold")
        )
        self.title_label.grid(row=1, column=0, pady=(0, 30))
        
        # Time input container
        self.time_frame = ctk.CTkFrame(self.main_frame)
        self.time_frame.grid(row=2, column=0, padx=10, pady=10)
        self.time_frame.grid_columnconfigure(0, weight=1)
        
        # Hours frame
        self.hours_label = ctk.CTkLabel(self.time_frame, text="Hours")
        self.hours_label.grid(row=0, column=0, padx=5, pady=5)
        
        self.hours_entry = ctk.CTkEntry(
            self.time_frame,
            width=100,
            placeholder_text="0"
        )
        self.hours_entry.grid(row=1, column=0, padx=5, pady=(0, 15))
        
        # Minutes frame
        self.minutes_label = ctk.CTkLabel(self.time_frame, text="Minutes")
        self.minutes_label.grid(row=2, column=0, padx=5, pady=5)
        
        self.minutes_entry = ctk.CTkEntry(
            self.time_frame,
            width=100,
            placeholder_text="0"
        )
        self.minutes_entry.grid(row=3, column=0, padx=5, pady=(0, 15))
        
        # Start button
        self.start_button = ctk.CTkButton(
            self.main_frame,
            text="Start Monitoring",
            command=self.start_monitoring,
            width=200
        )
        self.start_button.grid(row=3, column=0, pady=(20, 10))
        
        # View Logs button
        self.logs_button = ctk.CTkButton(
            self.main_frame,
            text="View Logs",
            command=self.view_logs,
            width=200,
            fg_color="#666",  # Darker color for secondary button
            hover_color="#555"
        )
        self.logs_button.grid(row=4, column=0, pady=(0, 20))
        
        self.duration: Optional[float] = None

    def view_logs(self):
        """Open the log file with the default text editor"""
        log_file = os.path.join(os.path.expanduser("~"), "FocusLock", "study_monitor.log")
        if os.path.exists(log_file):
            os.startfile(log_file)
        else:
            error_window = ctk.CTkToplevel(self)
            error_window.title("Error")
            error_window.geometry("300x100")
            error_window.resizable(False, False)
            
            error_label = ctk.CTkLabel(
                error_window,
                text="No logs found"
            )
            error_label.pack(pady=20)
            
            ok_button = ctk.CTkButton(
                error_window,
                text="OK",
                command=error_window.destroy
            )
            ok_button.pack(pady=10)

    def start_monitoring(self):
        try:
            hours = float(self.hours_entry.get() or 0)
            minutes = float(self.minutes_entry.get() or 0)
            
            if hours < 0 or minutes < 0:
                raise ValueError("Duration cannot be negative")
            
            if hours == 0 and minutes == 0:
                raise ValueError("Duration cannot be zero")
                
            if minutes >= 60:
                raise ValueError("Minutes should be less than 60")
            
            self.duration = hours + (minutes / 60)
            self.quit()
            
        except ValueError as e:
            error_window = ctk.CTkToplevel(self)
            error_window.title("Error")
            error_window.geometry("300x100")
            error_window.resizable(False, False)
            
            error_label = ctk.CTkLabel(
                error_window,
                text=str(e) if str(e) else "Please enter valid numbers"
            )
            error_label.pack(pady=20)
            
            ok_button = ctk.CTkButton(
                error_window,
                text="OK",
                command=error_window.destroy
            )
            ok_button.pack(pady=10)

class StudyMonitor:
    def __init__(self, block_duration_hours=1):
        # Create application directory
        self.app_dir = os.path.join(os.path.expanduser("~"), "FocusLock")
        os.makedirs(self.app_dir, exist_ok=True)
        
        # Set up logging
        self.setup_logging()
        
        # Load configuration
        self.config = self.load_config()
        
        # Convert screenshot interval from list to tuple
        self.screenshot_interval = tuple(self.config['screenshot_interval'])
        
        self.block_duration = timedelta(hours=block_duration_hours)
        self.running = True
        self.pause_monitoring = False
        
        # Initialize the VQA (Visual Question Answering) model
        try:
            self.vqa_pipeline = pipeline("visual-question-answering", 
                                      model="Salesforce/blip-vqa-base")
            logging.info("VQA model initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize VQA model: {e}")
            sys.exit(1)
            
        self.ignored_processes = self.config['ignored_processes']

    def setup_logging(self):
        """Set up logging configuration"""
        log_file = os.path.join(self.app_dir, "study_monitor.log")
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

    def load_config(self):
        """Load configuration with defaults"""
        default_config = {
            'screenshot_interval': [10, 30],
            'ignored_processes': [
                'cmd.exe', 'powershell.exe', 'explorer.exe',
                'taskmgr.exe', 'SystemSettings.exe', 'SearchApp.exe',
                'Taskmgr.exe', 'WindowsTerminal.exe', 'python.exe',
                'Code.exe', 'notepad.exe', 'notepad++.exe'
            ]
        }
        
        config_path = os.path.join(self.app_dir, "config.json")
        if not os.path.exists(config_path):
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=4)
        else:
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                logging.error(f"Error loading config file: {e}")
                
        return default_config

    def analyze_image_with_ai(self, image_base64, max_retries=3):
        if not self.vqa_pipeline:
            logging.error("VQA model not initialized")
            return False
            
        for attempt in range(max_retries):
            try:
                logging.info(f"Analyzing image (attempt {attempt + 1}/{max_retries})")
                
                image_bytes = base64.b64decode(image_base64)
                image = Image.open(BytesIO(image_bytes))
                
                question = "Answer only with 'yes' or 'no': Is this image showing entertainment - related content or playing a game?"
                result = self.vqa_pipeline(image=image, question=question, top_k=1)
                
                answer = result[0]['answer'].lower()
                is_entertainment = answer == 'yes'
                
                logging.info(f"AI Analysis result: {answer}")
                return is_entertainment
                
            except Exception as e:
                logging.error(f"Error in AI analysis (attempt {attempt + 1}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(min(2 ** attempt, 8))
                    continue
                return False
        
        return False

    def toggle_pause(self):
        self.pause_monitoring = not self.pause_monitoring
        status = "paused" if self.pause_monitoring else "resumed"
        logging.info(f"Monitoring {status}")
        
    def exit_app(self):
        self.running = False
        sys.exit(0)

    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return os.getuid() == 0

    def take_screenshot(self):
        try:
            logging.info("Taking screenshot...")
            hwnd = win32gui.GetForegroundWindow()
            rect = win32gui.GetWindowRect(hwnd)
            x, y = rect[0], rect[1]
            width = rect[2] - x
            height = rect[3] - y
            
            screenshot = ImageGrab.grab(bbox=(x, y, x+width, y+height))
            
            max_dimension = 2000
            if screenshot.size[0] > max_dimension or screenshot.size[1] > max_dimension:
                ratio = min(max_dimension / screenshot.size[0], max_dimension / screenshot.size[1])
                new_size = (int(screenshot.size[0] * ratio), int(screenshot.size[1] * ratio))
                screenshot = screenshot.resize(new_size, Image.Resampling.LANCZOS)
            
            logging.info(f"Screenshot size after processing: {screenshot.size}")
            
            buffered = BytesIO()
            screenshot.save(buffered, format="JPEG", quality=85, optimize=True)
            base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            return base64_image
            
        except Exception as e:
            logging.error(f"Error taking screenshot: {e}")
            return None

    def get_active_window_info(self):
        try:
            window = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(window)
            process = psutil.Process(pid)
            return {
                'title': win32gui.GetWindowText(window),
                'process_name': process.name(),
                'executable': process.exe()
            }
        except Exception as e:
            logging.error(f"Error getting window info: {e}")
            return None

    def monitor_activity(self):
        if self.pause_monitoring:
            return
            
        try:
            window_info = self.get_active_window_info()
            if not window_info or window_info['process_name'].lower() in self.ignored_processes:
                return

            image_base64 = self.take_screenshot()
            if not image_base64:
                return
                
            is_entertainment = self.analyze_image_with_ai(image_base64)
            if is_entertainment:
                self._handle_non_study_activity(window_info)
                
        except Exception as e:
            logging.error(f"Error in monitor_activity: {e}")
        finally:
            if self.running:
                schedule.every(
                    random.randint(*self.screenshot_interval)
                ).seconds.do(self.monitor_activity)

    def _handle_non_study_activity(self, window_info):
        try:
            hwnd = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            
            if process.name().lower() not in self.ignored_processes:
                logging.info(f"Closing non-study application: {process.name()}")
                try:
                    process.terminate()
                    process.wait(timeout=3)
                except psutil.TimeoutExpired:
                    process.kill()
                
        except Exception as e:
            logging.error(f"Error closing application: {e}")
            try:
                os.system(f'taskkill /F /PID {pid}')
            except Exception as e2:
                logging.error(f"Failed to force close process: {e2}")

def main():
    if not is_admin():
        run_as_admin()
        return

    ctk.set_appearance_mode("dark")
    app = DurationSelector()
    app.mainloop()
    
    duration = app.duration
    app.destroy()
    
    if duration is None:
        sys.exit(0)
    
    print(f"\nStarting Study Monitor with {duration:.1f} hour blocking duration...")
    
    monitor = StudyMonitor(block_duration_hours=duration)
    
    monitor.monitor_activity()
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down Study Monitor...")
        monitor.exit_app()

if __name__ == "__main__":
    main()
