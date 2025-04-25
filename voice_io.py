import speech_recognition as sr
import pyttsx3
import logging
from typing import Optional

class VoiceIO:
    def __init__(self):
        """Initialize voice input/output components."""
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        
        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()
        
        # Configure voice properties
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('rate', 150)    # Speed of speech
        self.engine.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)
        
        # Set female voice if available
        for voice in voices:
            if "female" in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def listen(self, timeout: int = 5) -> Optional[str]:
        """
        Listen for voice input and convert to text.
        
        Args:
            timeout (int): Maximum time to listen for input in seconds
            
        Returns:
            str: Recognized text or None if recognition fails
        """
        try:
            with sr.Microphone() as source:
                self.logger.info("Listening...")
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                # Listen for user input
                audio = self.recognizer.listen(source, timeout=timeout)
                
                self.logger.info("Processing speech...")
                # Convert speech to text
                text = self.recognizer.recognize_google(audio)
                self.logger.info(f"Recognized: {text}")
                return text.lower()
                
        except sr.WaitTimeoutError:
            self.logger.warning("Listening timed out")
            return None
        except sr.UnknownValueError:
            self.logger.warning("Could not understand audio")
            return None
        except sr.RequestError as e:
            self.logger.error(f"Could not request results: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Error in speech recognition: {str(e)}")
            return None

    def speak(self, text: str) -> None:
        """
        Convert text to speech and play it.
        
        Args:
            text (str): Text to be converted to speech
        """
        try:
            self.logger.info(f"Speaking: {text}")
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            self.logger.error(f"Error in text-to-speech: {str(e)}")

    def confirm_command(self, command: str) -> bool:
        """
        Ask for user confirmation before executing a command.
        
        Args:
            command (str): Command to be confirmed
            
        Returns:
            bool: True if user confirms, False otherwise
        """
        self.speak(f"Do you want me to {command}? Please say yes or no.")
        response = self.listen(timeout=5)
        return response is not None and "yes" in response.lower()

if __name__ == "__main__":
    # Test the VoiceIO class
    voice_io = VoiceIO()
    voice_io.speak("Hello! I am your task automation assistant. What can I do for you?")
    user_input = voice_io.listen()
    if user_input:
        voice_io.speak(f"You said: {user_input}")
    else:
        voice_io.speak("Sorry, I couldn't understand that.") 