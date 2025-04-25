# Task Automation Bot 🤖

A powerful and intuitive task automation assistant that combines voice commands with a modern web interface to help you stay organized and productive. Whether you prefer speaking or clicking, this bot has you covered!

## 🌟 Key Features

### 🎯 Smart Reminders
- Set reminders using natural voice commands or text input
- Flexible time formats (e.g., "4pm", "2:30 pm", "16:00")
- View and manage all your reminders in one place
- Automatic notifications to keep you on track

### 📝 Intelligent Notes
- Create notes using voice dictation or typing
- Organize notes into categories (lectures, assignments, projects, misc)
- Powerful search functionality to find notes instantly
- Support for multi-part notes with voice input

### 📂 Smart File Organization
- Automatically organize your desktop and downloads
- Customizable organization paths
- Intelligent file categorization
- One-click cleanup for messy folders

### 📄 PDF Management
- Quick search across your entire system
- Customizable search paths
- Easy PDF opening and viewing
- Organized document access

## 🚀 Why Choose Task Automation Bot?

- **Dual Interface**: Choose between voice commands or a beautiful web interface
- **Privacy Focused**: All processing happens locally on your machine
- **Easy to Use**: Intuitive design with clear instructions
- **Customizable**: Adapt the bot to your specific needs
- **Cross-Platform**: Works on Windows, macOS, and Linux

## 🛠️ Technical Features

- **Voice Recognition**: Advanced speech-to-text capabilities
- **Modern UI**: Built with Streamlit for a smooth experience
- **File Management**: Intelligent file organization algorithms
- **Reminder System**: Robust scheduling and notification system
- **Note Management**: Efficient storage and retrieval of notes

## 📦 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/TaskAutomationBot.git
cd TaskAutomationBot
```

2. Create a virtual environment (recommended):
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## 💻 Usage

### Web Interface (Default)
```bash
python main.py
```
Access the interface at `http://localhost:8501`

### Voice Mode
```bash
python main.py --mode voice
```

## 📋 Requirements

- Python 3.8 or higher
- Dependencies listed in `requirements.txt`:
  - SpeechRecognition==3.10.0
  - pyaudio==0.2.13
  - pyttsx3==2.90
  - python-dotenv==1.0.0
  - schedule==1.2.0
  - PyAutoGUI==0.9.54
  - python-dateutil==2.8.2
  - PyPDF2==3.0.1
  - streamlit==1.31.0

## 📁 Project Structure

```
TaskAutomationBot/
├── main.py              # Main application entry point
├── ui.py                # Streamlit UI implementation
├── requirements.txt     # Project dependencies
├── README.md           # This file
└── modules/            # Core functionality modules
    ├── voice_io.py     # Voice input/output handling
    ├── reminders.py    # Reminder management
    ├── file_manager.py # File organization
    └── notes_handler.py # Notes management
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

Please read our [Contributing Guidelines](CONTRIBUTING.md) for more details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Thanks to all the open-source libraries that made this project possible
- Special thanks to the Streamlit team for their amazing UI framework
- Inspired by the need for better task automation tools

## 📞 Support

If you encounter any issues or have suggestions, please:
1. Check the [Issues](https://github.com/yourusername/TaskAutomationBot/issues) page
2. Create a new issue if needed
3. We'll get back to you as soon as possible! 
