# AI Chatbot GUI with PyQt5 and Ollama

## Overview
This project is a **Graphical User Interface (GUI) chatbot application** built using **PyQt5**, integrating with **Ollama** for AI model execution. It allows users to interact with multiple AI chatbot models, manage chat history, and utilize text-to-speech functionality.

## Features

### 1. Multi-Model Chatbot Selection
- Users can choose from different AI models available in Ollama.
- Supports switching between chatbot models dynamically.
- Two chatbot models can be compared by running them separately.

### 2. Chat Interface
- A user-friendly UI for sending and receiving messages.
- Displays messages in a structured chat table.
- Markdown formatting support for enhanced message readability.

### 3. Chat History Management
- Save and load chat history using `.history` files.
- Uses Python's `pickle` module for efficient data storage.
- Option to clear chat history from the UI.

### 4. Voice Output
- Integrates `pyttsx3` for text-to-speech conversion.
- Customizable speech rate and volume.
- Reads chatbot responses aloud when enabled.

### 5. Chatbot Execution and Switching
- Uses **subprocess** commands to start and stop chatbot models.
- Automatically switches chatbot models based on user selection.
- Handles bot interactions in separate threads for a smooth UI experience.

### 6. Markdown Support
- Supports markdown formatting, including tables, lists, and code blocks.
- Messages are converted to HTML for proper rendering in the chat window.

### 7. Threaded Chat Processing
- Ensures non-blocking UI by processing chatbot responses in a separate thread.
- Utilizes `threading` to fetch responses while keeping the interface responsive.

## Installation
### Prerequisites
Ensure you have the following installed:
- Python 3.7+
- `pip`
- `Ollama` installed and configured
- Required Python libraries

### Setup Instructions
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/chatbot-gui.git
   cd chatbot-gui
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

## Usage
1. Start the application.
2. Select a chatbot model from the dropdown menu.
3. Type a message and press "Send" or hit `Enter`.
4. View responses in the chat window.
5. Enable voice output if desired.
6. Save or load chat history as needed.

## File Structure
```
chatbot-gui/
├── main.py          # Main application file
├── chatbot.py       # UI design file (PyQt5)
├── theme.qss        # Styling for the application
├── requirements.txt # Python dependencies
├── README.md        # Project documentation
```

## Dependencies
- `PyQt5`
- `pyttsx3`
- `markdown2`
- `pickle`
- `subprocess`
- `threading`
- `Ollama`

## Contributing
Contributions are welcome! Feel free to submit pull requests or open issues.

## License
None

## Author
- **Biswadarshi Naik** - [GitHub Profile](https://github.com/biswa365)
---
🚀 Enjoy using your AI chatbot!
