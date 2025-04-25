import os
import logging
from typing import List, Optional, Dict
import PyPDF2
import datetime
from pathlib import Path

class NotesHandler:
    def __init__(self, notes_dir: str = None):
        """
        Initialize the notes handler.
        
        Args:
            notes_dir (str): Directory where notes are stored. If None, uses default location.
        """
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Set notes directory
        if notes_dir is None:
            self.notes_dir = os.path.join(os.path.expanduser("~"), "Documents", "Notes")
        else:
            self.notes_dir = notes_dir
            
        # Create notes directory if it doesn't exist
        if not os.path.exists(self.notes_dir):
            os.makedirs(self.notes_dir)
            
        # Create subdirectories for different note types
        self.subdirs = {
            'lectures': 'lecture_notes',
            'assignments': 'assignments',
            'projects': 'projects',
            'miscellaneous': 'miscellaneous'
        }
        
        for subdir in self.subdirs.values():
            path = os.path.join(self.notes_dir, subdir)
            if not os.path.exists(path):
                os.makedirs(path)

    def create_note(self, title: str, content: str, note_type: str = 'misc') -> bool:
        """
        Create a new note file.
        
        Args:
            title (str): Title of the note
            content (str): Content of the note
            note_type (str): Type of note (lectures, assignments, projects, misc)
            
        Returns:
            bool: True if note was created successfully, False otherwise
        """
        try:
            # Get the appropriate subdirectory
            subdir = self.subdirs.get(note_type, 'miscellaneous')
            note_dir = os.path.join(self.notes_dir, subdir)
            
            # Create filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{title.replace(' ', '_')}.txt"
            filepath = os.path.join(note_dir, filename)
            
            # Write the note
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Title: {title}\n")
                f.write(f"Created: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Type: {note_type}\n\n")
                f.write(content)
                
            self.logger.info(f"Created note: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating note: {str(e)}")
            return False

    def get_note_content(self, note_path: str) -> Optional[str]:
        """
        Get the content of a note file.
        
        Args:
            note_path (str): Path to the note file
            
        Returns:
            Optional[str]: Content of the note if successful, None otherwise
        """
        try:
            with open(note_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"Error reading note: {str(e)}")
            return None

    def list_notes(self, note_type: Optional[str] = None) -> Dict[str, List[str]]:
        """
        List all notes, optionally filtered by type.
        
        Args:
            note_type (Optional[str]): Type of notes to list (lectures, assignments, projects, misc)
            
        Returns:
            Dict[str, List[str]]: Dictionary mapping note types to lists of note paths
        """
        notes = {subdir: [] for subdir in self.subdirs.values()}
        
        try:
            if note_type:
                # List notes of specific type
                subdir = self.subdirs.get(note_type, 'miscellaneous')
                dir_path = os.path.join(self.notes_dir, subdir)
                if os.path.exists(dir_path):
                    notes[subdir] = [
                        os.path.join(dir_path, f) for f in os.listdir(dir_path)
                        if f.endswith('.txt')
                    ]
            else:
                # List all notes
                for subdir in self.subdirs.values():
                    dir_path = os.path.join(self.notes_dir, subdir)
                    if os.path.exists(dir_path):
                        notes[subdir] = [
                            os.path.join(dir_path, f) for f in os.listdir(dir_path)
                            if f.endswith('.txt')
                        ]
                        
            return notes
            
        except Exception as e:
            self.logger.error(f"Error listing notes: {str(e)}")
            return {}

    def search_notes(self, query: str) -> List[str]:
        """
        Search for notes containing the query string.
        
        Args:
            query (str): Search query
            
        Returns:
            List[str]: List of paths to matching notes
        """
        matching_notes = []
        
        try:
            for subdir in self.subdirs.values():
                dir_path = os.path.join(self.notes_dir, subdir)
                if os.path.exists(dir_path):
                    for filename in os.listdir(dir_path):
                        if filename.endswith('.txt'):
                            filepath = os.path.join(dir_path, filename)
                            content = self.get_note_content(filepath)
                            if content and query.lower() in content.lower():
                                matching_notes.append(filepath)
                                
            return matching_notes
            
        except Exception as e:
            self.logger.error(f"Error searching notes: {str(e)}")
            return []

    def open_pdf(self, pdf_path: str) -> bool:
        """
        Open a PDF file using the default application.
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            bool: True if PDF was opened successfully, False otherwise
        """
        if not os.path.exists(pdf_path):
            self.logger.error(f"PDF file not found: {pdf_path}")
            return False

        try:
            os.startfile(pdf_path)
            return True
        except Exception as e:
            self.logger.error(f"Error opening PDF: {str(e)}")
            return False

    def extract_pdf_text(self, pdf_path: str) -> Optional[str]:
        """
        Extract text from a PDF file.
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            Optional[str]: Extracted text if successful, None otherwise
        """
        if not os.path.exists(pdf_path):
            self.logger.error(f"PDF file not found: {pdf_path}")
            return None

        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            self.logger.error(f"Error extracting PDF text: {str(e)}")
            return None

if __name__ == "__main__":
    # Test the NotesHandler
    notes_handler = NotesHandler()
    
    # Test creating a note
    test_title = "Test Note"
    test_content = "This is a test note created by the NotesHandler class."
    notes_handler.create_note(test_title, test_content, 'lectures')
    
    # Test listing notes
    notes = notes_handler.list_notes()
    print("All notes:", notes)
    
    # Test searching notes
    search_results = notes_handler.search_notes("test")
    print("Search results:", search_results) 