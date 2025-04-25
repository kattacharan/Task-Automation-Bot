import threading
import time
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List, Callable

class ReminderManager:
    def __init__(self, speak_callback: Callable[[str], None]):
        """
        Initialize the ReminderManager.
        
        Args:
            speak_callback (Callable[[str], None]): Function to speak reminders
        """
        self.reminders: List[Dict] = []
        self.speak = speak_callback
        self.running = False
        self.thread = None
        self.reminders_file = "reminders.json"
        self.load_reminders()

    def start(self) -> None:
        """Start the reminder checking thread."""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._check_reminders)
            self.thread.daemon = True
            self.thread.start()

    def stop(self) -> None:
        """Stop the reminder checking thread."""
        self.running = False
        if self.thread:
            self.thread.join()

    def add_reminder(self, task: str, time_str: str) -> bool:
        """
        Add a new reminder.
        
        Args:
            task (str): The task to be reminded about
            time_str (str): When to be reminded (format: "HH:MM" or "HH:MM AM/PM")
            
        Returns:
            bool: True if reminder was added successfully, False otherwise
        """
        try:
            # Clean up the time string
            time_str = time_str.lower().strip()
            
            # Handle different time formats
            time_formats = [
                "%I:%M %p",    # 4:00 PM
                "%I:%M%p",     # 4:00PM
                "%I %p",       # 4 PM
                "%I%p",        # 4PM
                "%I:%M",       # 4:00
                "%I",          # 4
                "%H:%M",       # 16:00 (24-hour format)
                "%H"           # 16 (24-hour format)
            ]
            
            time_obj = None
            for fmt in time_formats:
                try:
                    time_obj = datetime.strptime(time_str, fmt).time()
                    break
                except ValueError:
                    continue
            
            # If no format matched, try to parse manually
            if time_obj is None:
                # Try to extract hours and minutes
                parts = time_str.split(':')
                if len(parts) == 2:
                    try:
                        hours = int(parts[0])
                        minutes = int(parts[1].split()[0])  # Handle cases like "4:30 pm"
                        if 0 <= hours <= 23 and 0 <= minutes <= 59:
                            time_obj = datetime.strptime(f"{hours:02d}:{minutes:02d}", "%H:%M").time()
                    except ValueError:
                        pass
            
            if time_obj is None:
                return False
                
            now = datetime.now()
            reminder_time = datetime.combine(now.date(), time_obj)
            
            # If the time has already passed today, set it for tomorrow
            if reminder_time < now:
                reminder_time = datetime.combine(now.date(), time_obj) + timedelta(days=1)
            
            reminder = {
                "task": task,
                "time": reminder_time.strftime("%Y-%m-%d %I:%M %p"),
                "timestamp": reminder_time.timestamp()
            }
            
            self.reminders.append(reminder)
            self.save_reminders()
            return True
            
        except Exception as e:
            print(f"Error adding reminder: {e}")
            return False

    def get_all_reminders(self) -> List[Dict]:
        """Get all current reminders."""
        return self.reminders

    def remove_reminder(self, task: str) -> bool:
        """
        Remove a reminder by task name.
        
        Args:
            task (str): The task to remove
            
        Returns:
            bool: True if reminder was removed, False otherwise
        """
        for i, reminder in enumerate(self.reminders):
            if reminder["task"].lower() == task.lower():
                del self.reminders[i]
                self.save_reminders()
                return True
        return False

    def _check_reminders(self) -> None:
        """Background thread to check and trigger reminders."""
        while self.running:
            now = datetime.now()
            current_timestamp = now.timestamp()
            
            # Check each reminder
            for reminder in self.reminders[:]:  # Create a copy to safely modify during iteration
                if current_timestamp >= reminder["timestamp"]:
                    self.speak(f"Reminder: {reminder['task']}")
                    self.reminders.remove(reminder)
                    self.save_reminders()
            
            time.sleep(30)  # Check every 30 seconds

    def save_reminders(self) -> None:
        """Save reminders to file."""
        try:
            with open(self.reminders_file, 'w') as f:
                json.dump(self.reminders, f, indent=4)
        except Exception as e:
            print(f"Error saving reminders: {e}")

    def load_reminders(self) -> None:
        """Load reminders from file."""
        try:
            if os.path.exists(self.reminders_file):
                with open(self.reminders_file, 'r') as f:
                    self.reminders = json.load(f)
        except Exception as e:
            print(f"Error loading reminders: {e}")
            self.reminders = [] 