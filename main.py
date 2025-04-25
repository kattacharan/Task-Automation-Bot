import os
import logging
import time
from typing import Dict, Optional
import json
from datetime import datetime
import argparse

from modules.voice_io import VoiceIO
from modules.reminders import ReminderManager
from modules.file_manager import FileManager
from modules.notes_handler import NotesHandler
from ui import TaskAutomationUI

class TaskAutomationBot:
    def __init__(self):
        """Initialize the Task Automation Bot."""
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.voice_io = VoiceIO()
        self.reminder_mgr = ReminderManager(self.voice_io.speak)
        self.file_mgr = FileManager()
        self.notes_handler = NotesHandler()
        
        # Load configuration
        self.config = self._load_config()
        
        # Start reminder manager
        self.reminder_mgr.start()
        
        self.logger.info("Task Automation Bot initialized")

    def _load_config(self) -> Dict:
        """Load configuration from file."""
        config_path = "config.json"
        default_config = {
            "voice_enabled": True,
            "default_notes_dir": os.path.join(os.path.expanduser("~"), "Documents", "Notes"),
            "backup_dir": os.path.join(os.path.expanduser("~"), "Documents", "Backups")
        }
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    return json.load(f)
            else:
                with open(config_path, 'w') as f:
                    json.dump(default_config, f, indent=4)
                return default_config
        except Exception as e:
            self.logger.error(f"Error loading config: {str(e)}")
            return default_config

    def process_command(self, command: str) -> bool:
        """
        Process a voice command.
        
        Args:
            command (str): The voice command to process
            
        Returns:
            bool: True if command was processed successfully, False otherwise
        """
        command = command.lower()
        
        try:
            # Reminder commands
            if "remind" in command or "reminder" in command:
                if "list" in command:
                    self._handle_list_reminders()
                else:
                    self._handle_set_reminder(command)
                return True
                
            # File management commands
            elif "clean" in command:
                if "desktop" in command:
                    self._handle_clean_desktop()
                elif "downloads" in command:
                    self._handle_clean_downloads()
                return True
                
            # Notes commands
            elif "note" in command or "notes" in command:
                if "create" in command:
                    self._handle_create_note(command)
                elif "open" in command:
                    self._handle_open_note(command)
                elif "search" in command:
                    self._handle_search_notes(command)
                return True
                
            # PDF commands
            elif "pdf" in command:
                if "open" in command:
                    self._handle_open_pdf(command)
                return True
                
            # Help command
            elif "help" in command:
                self._handle_help()
                return True
                
            else:
                self.voice_io.speak("I'm sorry, I didn't understand that command.")
                return False
                
        except Exception as e:
            self.logger.error(f"Error processing command: {str(e)}")
            self.voice_io.speak("I encountered an error while processing your command.")
            return False

    def _handle_set_reminder(self, command: str) -> None:
        """Handle setting a reminder."""
        try:
            # Extract time and task from the command
            time_keywords = ["at", "on", "by"]
            task_keywords = ["to", "about", "that"]
            
            # Find the time and task parts
            time_part = None
            task_part = None
            
            # First try to find the time part
            for keyword in time_keywords:
                if keyword in command:
                    parts = command.split(keyword, 1)
                    if len(parts) > 1:
                        time_part = parts[1].strip()
                        # Look for task keywords in the time part
                        for task_keyword in task_keywords:
                            if task_keyword in time_part:
                                time_task = time_part.split(task_keyword, 1)
                                time_part = time_task[0].strip()
                                task_part = time_task[1].strip()
                                break
                        break
            
            # If we couldn't find the parts, try alternative parsing
            if not time_part or not task_part:
                # Try to find task first
                for task_keyword in task_keywords:
                    if task_keyword in command:
                        parts = command.split(task_keyword, 1)
                        if len(parts) > 1:
                            task_part = parts[1].strip()
                            # Look for time in the first part
                            for time_keyword in time_keywords:
                                if time_keyword in parts[0]:
                                    time_part = parts[0].split(time_keyword, 1)[1].strip()
                                    break
                            break
            
            if not time_part or not task_part:
                self.voice_io.speak("I couldn't understand the reminder command. Please try again with a format like 'remind me at 4pm to water the plants'")
                return
                
            # Try to add the reminder
            if self.reminder_mgr.add_reminder(task_part, time_part):
                self.voice_io.speak(f"I'll remind you about {task_part} at {time_part}")
            else:
                self.voice_io.speak("I couldn't set that reminder. Please try again with a valid time format like '4pm' or '2:30 pm'")
                
        except Exception as e:
            self.logger.error(f"Error setting reminder: {str(e)}")
            self.voice_io.speak("I encountered an error while setting your reminder. Please try again.")

    def _handle_list_reminders(self) -> None:
        """Handle listing all reminders."""
        reminders = self.reminder_mgr.get_all_reminders()
        if reminders:
            self.voice_io.speak("Here are your reminders:")
            for reminder in reminders:
                self.voice_io.speak(f"{reminder['task']} at {reminder['time']}")
        else:
            self.voice_io.speak("You don't have any reminders set.")

    def _handle_clean_desktop(self) -> None:
        """Handle cleaning the desktop."""
        if self.voice_io.confirm_command("clean your desktop"):
            result = self.file_mgr.clean_desktop()
            self.voice_io.speak(f"Cleaned your desktop. Moved {sum(result.values())} files to their appropriate folders.")

    def _handle_clean_downloads(self) -> None:
        """Handle cleaning the downloads folder."""
        if self.voice_io.confirm_command("clean your downloads folder"):
            result = self.file_mgr.clean_downloads()
            self.voice_io.speak(f"Cleaned your downloads folder. Moved {sum(result.values())} files to their appropriate folders.")

    def _handle_create_note(self, command: str) -> None:
        """Handle creating a new note."""
        self.voice_io.speak("What would you like to name this note?")
        title = self.voice_io.listen()
        
        if title:
            self.voice_io.speak("What would you like to write in the note?")
            content = self.voice_io.listen()
            
            if content:
                if self.notes_handler.create_note(title, content):
                    self.voice_io.speak(f"Created note: {title}")
                else:
                    self.voice_io.speak("I couldn't create that note. Please try again.")

    def _handle_open_note(self, command: str) -> None:
        """Handle opening a note."""
        self.voice_io.speak("Which note would you like to open?")
        note_name = self.voice_io.listen()
        
        if note_name:
            notes = self.notes_handler.search_notes(note_name)
            if notes:
                self.voice_io.speak(f"Found {len(notes)} matching notes. Opening the first one.")
                self.notes_handler.get_note_content(notes[0])
            else:
                self.voice_io.speak("I couldn't find any notes matching that name.")

    def _handle_search_notes(self, command: str) -> None:
        """Handle searching notes."""
        self.voice_io.speak("What would you like to search for in your notes?")
        query = self.voice_io.listen()
        
        if query:
            results = self.notes_handler.search_notes(query)
            if results:
                self.voice_io.speak(f"Found {len(results)} matching notes.")
                for i, note in enumerate(results[:3], 1):
                    self.voice_io.speak(f"Note {i}: {os.path.basename(note)}")
            else:
                self.voice_io.speak("I couldn't find any notes matching your search.")

    def _handle_open_pdf(self, command: str) -> None:
        """Handle opening a PDF file."""
        self.voice_io.speak("Which PDF would you like to open?")
        pdf_name = self.voice_io.listen()
        
        if pdf_name:
            pdfs = self.file_mgr.find_files(os.path.expanduser("~"), f"*{pdf_name}*.pdf")
            if pdfs:
                self.voice_io.speak(f"Found {len(pdfs)} matching PDFs. Opening the first one.")
                self.notes_handler.open_pdf(pdfs[0])
            else:
                self.voice_io.speak("I couldn't find any PDFs matching that name.")

    def _handle_help(self) -> None:
        """Handle help command."""
        help_text = """
        I can help you with:
        - Setting reminders (e.g., "remind me at 4pm to water the plants")
          Supported time formats:
          - 12-hour format: 4pm, 4:00pm, 4:00 pm, 4:00, 4 PM
          - 24-hour format: 16:00, 16
        - Cleaning your desktop and downloads folder
        - Creating and managing notes
        - Opening PDF files
        - Searching through your notes
        
        You can also say:
        - "stop", "exit", "quit", or "goodbye" to end the session
        
        Just tell me what you'd like me to do!
        """
        self.voice_io.speak(help_text)

    def run_voice_mode(self) -> None:
        """Run the bot in voice mode."""
        self.voice_io.speak("Hello! I'm your Task Automation Bot. How can I help you today?")
        
        while True:
            try:
                self.voice_io.speak("Listening for your command...")
                command = self.voice_io.listen()
                
                if command:
                    if command.lower() in ["stop", "exit", "quit", "goodbye"]:
                        self.voice_io.speak("Goodbye! Have a great day!")
                        self.reminder_mgr.stop()
                        break
                        
                    self.process_command(command)
                    # Wait a moment before listening again
                    time.sleep(2)
                else:
                    # If no command was recognized, wait a bit before trying again
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                self.logger.info("Shutting down...")
                self.reminder_mgr.stop()
                break
            except Exception as e:
                self.logger.error(f"Error in main loop: {str(e)}")
                time.sleep(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Task Automation Bot')
    parser.add_argument('--mode', choices=['voice', 'ui'], default='ui',
                      help='Choose the mode to run the bot in (default: ui)')
    args = parser.parse_args()
    
    if args.mode == 'voice':
        bot = TaskAutomationBot()
        bot.run_voice_mode()
    else:
        ui = TaskAutomationUI()
        ui.run() 