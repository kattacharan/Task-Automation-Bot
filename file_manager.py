import os
import shutil
import logging
from typing import List, Dict,Optional
import datetime
import glob
import pyautogui
from pathlib import Path

class FileManager:
    def __init__(self):
        """Initialize the file manager."""
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Common file extensions and their categories
        self.file_categories = {
            'documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'],
            'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg'],
            'videos': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv'],
            'audio': ['.mp3', '.wav', '.ogg', '.m4a', '.flac'],
            'archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
            'code': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c'],
            'spreadsheets': ['.xls', '.xlsx', '.csv', '.ods'],
            'presentations': ['.ppt', '.pptx', '.odp']
        }

    def organize_directory(self, directory: str) -> Dict[str, int]:
        """
        Organize files in a directory into subdirectories based on their types.
        
        Args:
            directory (str): Path to the directory to organize
            
        Returns:
            Dict[str, int]: Count of files moved to each category
        """
        if not os.path.exists(directory):
            self.logger.error(f"Directory not found: {directory}")
            return {}

        # Create category directories if they don't exist
        for category in self.file_categories.keys():
            category_path = os.path.join(directory, category)
            if not os.path.exists(category_path):
                os.makedirs(category_path)

        # Track files moved to each category
        files_moved = {category: 0 for category in self.file_categories.keys()}
        files_moved['others'] = 0

        # Move files to appropriate directories
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                file_ext = os.path.splitext(file)[1].lower()
                moved = False

                # Check each category
                for category, extensions in self.file_categories.items():
                    if file_ext in extensions:
                        dest_path = os.path.join(directory, category, file)
                        try:
                            shutil.move(file_path, dest_path)
                            files_moved[category] += 1
                            moved = True
                            break
                        except Exception as e:
                            self.logger.error(f"Error moving file {file}: {str(e)}")

                if not moved:
                    # Move to 'others' category
                    others_path = os.path.join(directory, 'others')
                    if not os.path.exists(others_path):
                        os.makedirs(others_path)
                    try:
                        shutil.move(file_path, os.path.join(others_path, file))
                        files_moved['others'] += 1
                    except Exception as e:
                        self.logger.error(f"Error moving file {file} to others: {str(e)}")

        return files_moved

    def clean_desktop(self) -> Dict[str, int]:
        """
        Clean and organize the desktop.
        
        Returns:
            Dict[str, int]: Count of files moved to each category
        """
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        return self.organize_directory(desktop_path)

    def clean_downloads(self) -> Dict[str, int]:
        """
        Clean and organize the downloads folder.
        
        Returns:
            Dict[str, int]: Count of files moved to each category
        """
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
        return self.organize_directory(downloads_path)

    def find_files(self, directory: str, pattern: str) -> List[str]:
        """
        Find files matching a pattern in a directory.
        
        Args:
            directory (str): Directory to search in
            pattern (str): File pattern to match (e.g., "*.pdf")
            
        Returns:
            List[str]: List of matching file paths
        """
        if not os.path.exists(directory):
            self.logger.error(f"Directory not found: {directory}")
            return []

        try:
            return glob.glob(os.path.join(directory, pattern))
        except Exception as e:
            self.logger.error(f"Error finding files: {str(e)}")
            return []

    def open_file(self, file_path: str) -> bool:
        """
        Open a file using the default application.
        
        Args:
            file_path (str): Path to the file to open
            
        Returns:
            bool: True if file was opened successfully, False otherwise
        """
        if not os.path.exists(file_path):
            self.logger.error(f"File not found: {file_path}")
            return False

        try:
            os.startfile(file_path)
            return True
        except Exception as e:
            self.logger.error(f"Error opening file: {str(e)}")
            return False

    def create_backup(self, source_dir: str, backup_dir: str) -> bool:
        """
        Create a backup of a directory.
        
        Args:
            source_dir (str): Directory to backup
            backup_dir (str): Directory to store the backup
            
        Returns:
            bool: True if backup was successful, False otherwise
        """
        if not os.path.exists(source_dir):
            self.logger.error(f"Source directory not found: {source_dir}")
            return False

        try:
            # Create backup directory with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(backup_dir, f"backup_{timestamp}")
            
            # Copy the directory
            shutil.copytree(source_dir, backup_path)
            self.logger.info(f"Backup created at: {backup_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error creating backup: {str(e)}")
            return False

if __name__ == "__main__":
    # Test the FileManager
    file_mgr = FileManager()
    
    # Test organizing a directory
    test_dir = "test_directory"
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
        
    # Create some test files
    test_files = {
        'test1.pdf': 'documents',
        'test2.jpg': 'images',
        'test3.mp4': 'videos',
        'test4.py': 'code',
        'test5.zip': 'archives'
    }
    
    for file, category in test_files.items():
        with open(os.path.join(test_dir, file), 'w') as f:
            f.write("test content")
    
    # Organize the test directory
    result = file_mgr.organize_directory(test_dir)
    print("Files moved to categories:", result)
    
    # Clean up
    shutil.rmtree(test_dir) 