import streamlit as st
import os
from datetime import datetime, time
import json
from modules.voice_io import VoiceIO
from modules.reminders import ReminderManager
from modules.file_manager import FileManager
from modules.notes_handler import NotesHandler

class TaskAutomationUI:
    def __init__(self):
        """Initialize the UI components."""
        # Initialize voice_io but don't start the event loop
        self.voice_io = VoiceIO()
        self.reminder_mgr = ReminderManager(self.voice_io.speak)
        self.file_mgr = FileManager()
        self.notes_handler = NotesHandler()
        
        # Start reminder manager
        self.reminder_mgr.start()
        
        # Set page config
        st.set_page_config(
            page_title="Task Automation Bot",
            page_icon="🤖",
            layout="wide"
        )

    def run(self):
        """Run the Streamlit UI."""
        st.title("🤖 Task Automation Bot")
        
        # Create tabs for different functionalities
        tab1, tab2, tab3, tab4 = st.tabs(["Reminders", "Notes", "File Organization", "PDF Tools"])
        
        with tab1:
            self._reminders_tab()
            
        with tab2:
            self._notes_tab()
            
        with tab3:
            self._file_org_tab()
            
        with tab4:
            self._pdf_tab()

    def _reminders_tab(self):
        """Reminders tab content."""
        st.header("📅 Reminders")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Set New Reminder")
            
            # Voice input for reminder
            if st.button("🎤 Listen for Reminder", key="reminder_voice"):
                st.info("Listening... Speak your reminder")
                reminder_text = self.voice_io.listen()
                if reminder_text:
                    st.session_state.reminder_text = reminder_text
                    st.success(f"Heard: {reminder_text}")
            
            # Display the heard reminder if available
            if 'reminder_text' in st.session_state:
                st.text_input("Reminder Text", value=st.session_state.reminder_text, key="reminder_input")
            
            # Time input
            time_input = st.time_input("When?", time(12, 0))
            
            # Set reminder button
            if st.button("Set Reminder"):
                if 'reminder_text' in st.session_state and st.session_state.reminder_text:
                    time_str = time_input.strftime("%I:%M %p")
                    if self.reminder_mgr.add_reminder(st.session_state.reminder_text, time_str):
                        st.success(f"Reminder set: {st.session_state.reminder_text} at {time_str}")
                        del st.session_state.reminder_text
                    else:
                        st.error("Failed to set reminder")
                else:
                    st.warning("Please record a reminder first")
        
        with col2:
            st.subheader("Current Reminders")
            reminders = self.reminder_mgr.get_all_reminders()
            if reminders:
                for idx, reminder in enumerate(reminders):
                    with st.expander(f"🔔 {reminder['task']} at {reminder['time']}"):
                        # Use a unique key combining task and index
                        delete_key = f"del_{reminder['task']}_{idx}"
                        if st.button("Delete", key=delete_key):
                            self.reminder_mgr.remove_reminder(reminder['task'])
                            st.experimental_rerun()
            else:
                st.info("No reminders set yet")

    def _notes_tab(self):
        """Notes tab content."""
        st.header("📝 Notes")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Create New Note")
            
            # Voice input for note title
            if st.button("🎤 Listen for Note Title", key="note_title_voice"):
                st.info("Listening... Speak the note title")
                title = self.voice_io.listen()
                if title:
                    st.session_state.note_title = title
                    st.success(f"Heard: {title}")
            
            # Display the heard title if available
            if 'note_title' in st.session_state:
                st.text_input("Note Title", value=st.session_state.note_title, key="title_input")
            
            # Voice input for note content
            if st.button("🎤 Listen for Note Content", key="note_content_voice"):
                st.info("Listening... Speak the note content")
                content = self.voice_io.listen()
                if content:
                    if 'note_content' not in st.session_state:
                        st.session_state.note_content = []
                    st.session_state.note_content.append(content)
                    st.success(f"Added: {content}")
            
            # Display the heard content if available
            if 'note_content' in st.session_state and st.session_state.note_content:
                st.text_area("Note Content", value="\n".join(st.session_state.note_content), key="content_input")
            
            # Note type selection
            note_type = st.selectbox(
                "Note Type",
                ["lectures", "assignments", "projects", "misc"]
            )
            
            # Create note button
            if st.button("Create Note"):
                if 'note_title' in st.session_state and 'note_content' in st.session_state:
                    if self.notes_handler.create_note(
                        st.session_state.note_title,
                        "\n".join(st.session_state.note_content),
                        note_type
                    ):
                        st.success(f"Note created: {st.session_state.note_title}")
                        del st.session_state.note_title
                        del st.session_state.note_content
                    else:
                        st.error("Failed to create note")
                else:
                    st.warning("Please record both title and content first")
        
        with col2:
            st.subheader("Search Notes")
            search_query = st.text_input("Search notes")
            if search_query:
                results = self.notes_handler.search_notes(search_query)
                if results:
                    for note in results:
                        with st.expander(os.path.basename(note)):
                            content = self.notes_handler.get_note_content(note)
                            st.text(content)
                else:
                    st.info("No matching notes found")

    def _file_org_tab(self):
        """File organization tab content."""
        st.header("🗂️ File Organization")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Clean Desktop")
            desktop_path = st.text_input("Enter Desktop Path", value=os.path.join(os.path.expanduser("~"), "Desktop"))
            if st.button("Clean Desktop"):
                if os.path.exists(desktop_path):
                    result = self.file_mgr.clean_desktop(desktop_path)
                    st.success(f"Cleaned desktop. Moved {sum(result.values())} files")
                    st.json(result)
                else:
                    st.error("Invalid desktop path")
        
        with col2:
            st.subheader("Clean Downloads")
            downloads_path = st.text_input("Enter Downloads Path", value=os.path.join(os.path.expanduser("~"), "Downloads"))
            if st.button("Clean Downloads"):
                if os.path.exists(downloads_path):
                    result = self.file_mgr.clean_downloads(downloads_path)
                    st.success(f"Cleaned downloads. Moved {sum(result.values())} files")
                    st.json(result)
                else:
                    st.error("Invalid downloads path")

    def _pdf_tab(self):
        """PDF tools tab content."""
        st.header("📄 PDF Tools")
        
        st.subheader("Open PDF")
        search_path = st.text_input("Enter Search Path", value=os.path.expanduser("~"))
        pdf_name = st.text_input("Enter PDF name to search")
        
        if pdf_name and os.path.exists(search_path):
            pdfs = self.file_mgr.find_files(search_path, f"*{pdf_name}*.pdf")
            if pdfs:
                selected_pdf = st.selectbox("Select PDF to open", pdfs)
                if st.button("Open PDF"):
                    if self.notes_handler.open_pdf(selected_pdf):
                        st.success(f"Opening {os.path.basename(selected_pdf)}")
                    else:
                        st.error("Failed to open PDF")
            else:
                st.info("No matching PDFs found")
        elif not os.path.exists(search_path):
            st.error("Invalid search path")

if __name__ == "__main__":
    ui = TaskAutomationUI()
    ui.run() 