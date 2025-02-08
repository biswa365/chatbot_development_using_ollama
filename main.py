import sys
import os
from pathlib import Path
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from chatbot import Ui_chatbot
from ollama import chat
from ollama import ListResponse, list
import threading
import pickle
import subprocess
import markdown2
import pyttsx3

class MainWindow(QtWidgets.QMainWindow, Ui_chatbot):
    print_message = pyqtSignal(str)
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.center()
        
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)    # Speed of speech
        self.engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)
        
        self.chatbot_name = "gemma2:2b"
        subprocess.run("ollama run gemma2:2b", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        response: ListResponse = list()
        self.cbxModels.clear()
        self.cbxModel1.clear()
        self.cbxModel2.clear()
        for model in response.models:
            self.cbxModels.addItem(model.model)
            self.cbxModel1.addItem(model.model)
            self.cbxModel2.addItem(model.model)     
        
        self.icebreak = False
        index = self.cbxModels.findText("gemma2:2b")
        if index >= 0:
            self.cbxModels.setCurrentIndex(index)
        
        self.chat_history = []
        
        self.chat_table.setSelectionMode(QAbstractItemView.NoSelection)
        self.chat_table.setVerticalScrollMode(self.chat_table.ScrollPerPixel)
        self.chat_table.setHorizontalScrollMode(self.chat_table.ScrollPerPixel)
        self.btnSend.clicked.connect(self.sendClicked)
        self.btnClearChat.clicked.connect(self.clearChatClicked)
        self.btnShowDetails.clicked.connect(self.showDetailsClicked)
        self.btnModel1Talk.clicked.connect(self.runModel1)
        self.btnModel2Talk.clicked.connect(self.runModel2)
        self.input_area.returnPressed.connect(self.sendClicked)
        self.cbxModels.currentIndexChanged.connect(self.cbxModelsIndexChanged)
        self.actionLoad_Chat_History.triggered.connect(self.loadChatHistory)
        self.actionSave_Chat_History.triggered.connect(self.saveChatHistory)
        self.actionSave_As_Chat_History.triggered.connect(self.saveAsChatHistory)
        self.print_message.connect(self.addReplyMessage)
    
    def center(self):
        """
        Centers the window on the screen.

        This method calculates the center position of the screen and moves the window
        to that position. It uses the screen geometry to determine the screen's width
        and height, and the window's geometry to determine its width and height.
        """
        screen = QApplication.desktop().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2) 

    def saveChatHistory(self):
        """
        Saves the chat history to a file specified by txtChatHistoryPath.

        This method serializes the chat history using the pickle module and writes it to a file in binary mode.
        A message box is displayed to inform the user that the chat history has been saved.

        Raises:
            IOError: If the file cannot be opened or written to.
        """
        if os.path.exists(self.txtChatHistoryPath.text()):
            with open(self.txtChatHistoryPath.text(), 'wb') as file:
                try:
                    pickle.dump(self.chat_history, file)
                    QMessageBox.information(self, 'Information', 'Chat history saved.')
                except (pickle.PicklingError, IOError) as e:
                    QMessageBox.critical(self, 'Error', f'Failed to save chat history: {e}')

    def saveAsChatHistory(self):
        """
        Opens a file dialog to save the current chat history to a file.

        This method uses a QFileDialog to prompt the user to select a location and
        filename for saving the chat history. The chat history is then serialized
        and saved to the specified file using the pickle module.

        The saved file will have a ".history" extension.

        Returns:
            None
        """
        file_dialog_options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Save File...", "", "History Files (*.history)", options=file_dialog_options)
        if fileName:
            with open(fileName, 'wb') as file:
                pickle.dump(self.chat_history, file)

    def loadChatHistory(self):
        """
        Opens a file dialog to select a chat history file and loads the chat history from the selected file.

        This method uses a QFileDialog to allow the user to select a file with a .history extension. 
        If a file is selected, it updates the txtChatHistoryPath with the file path and loads the chat 
        history from the file using pickle.

        Raises:
            Exception: If there is an error loading the chat history from the file.
        """
        file_dialog_options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open File...", "", "History Files (*.history)", options=file_dialog_options)
        if fileName:
            self.txtChatHistoryPath.setText(fileName)
            with open(fileName, 'rb') as file:
                self.chat_history = pickle.load(file) 

    def clearChatClicked(self):
        """
        Clears all rows from the chat table.

        This method is triggered when the clear chat button is clicked. It removes
        all rows from the chat table one by one until the table is empty.
        """
        while self.chat_table.rowCount() > 0:
            self.chat_table.removeRow(0)
    
    def runModel1(self):
        """
        Executes the first chatbot model and manages the chat history and UI updates.
        This method performs the following steps:
        1. Initializes the chat history and icebreaker text if it's the first interaction.
        2. Stops the second chatbot model if it is running.
        3. Runs the first chatbot model.
        4. Appends the user's input to the chat history.
        5. Updates the chat table in the UI with the new input.
        6. Starts a new thread to get a reply from the chatbot model.
        Attributes:
            icebreak (bool): Indicates if the icebreaker text has been set.
            chat_history (list): Stores the history of chat messages.
            talk (str): The initial icebreaker text.
            cbxModel1 (QComboBox): UI element to select the first chatbot model.
            cbxModel2 (QComboBox): UI element to select the second chatbot model.
            spinWords (QSpinBox): UI element to specify the number of words for the chatbot's response.
            chat_table (QTableWidget): UI element to display the chat history.
            row_position (int): The current row position in the chat table.
        """
        if not self.icebreak:
            self.chat_history = []
            self.talk = self.txtIceBreaker.text()
            self.icebreak = True
        
        chatbot_name = self.cbxModel1.currentText().strip()
        chatbot_name2 = self.cbxModel2.currentText().strip()
        subprocess.run("ollama stop " + chatbot_name2, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run("ollama run " + chatbot_name, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.chat_history.append({'role': 'user', 'content': f"{self.talk} in {self.spinWords.value()} words"})  
        self.row_position = self.chat_table.rowCount()
        self.chat_table.insertRow(self.row_position)
        chatbot_name = self.cbxModel1.currentText().strip()
        get_replay_thread = threading.Thread(target=self.get_reply, args=(chatbot_name,))
        get_replay_thread.start()
        
    def runModel2(self):
        """
        Executes the second chatbot model.
        This method performs the following steps:
        1. Initializes the chat history and icebreaker text if not already done.
        2. Stops the currently running chatbot model specified in cbxModel1.
        3. Runs the chatbot model specified in cbxModel2.
        4. Appends the user's input to the chat history.
        5. Inserts a new row in the chat table for the user's input.
        6. Starts a new thread to get a reply from the chatbot model.
        Attributes:
            self.icebreak (bool): Indicates if the icebreaker text has been set.
            self.chat_history (list): Stores the chat history.
            self.talk (str): The icebreaker text.
            self.cbxModel2 (QComboBox): ComboBox containing the second chatbot model names.
            self.cbxModel1 (QComboBox): ComboBox containing the first chatbot model names.
            self.spinWords (QSpinBox): SpinBox to specify the number of words for the chatbot's response.
            self.chat_table (QTableWidget): Table widget to display the chat history.
            self.row_position (int): The current row position in the chat table.
        """
        if not self.icebreak:
            self.chat_history = []
            self.talk = self.txtIceBreaker.text()
            self.icebreak = True
            
        chatbot_name = self.cbxModel2.currentText().strip()
        chatbot_name2 = self.cbxModel1.currentText().strip()
        subprocess.run("ollama stop " + chatbot_name2, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run("ollama run " + chatbot_name, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.chat_history.append({'role': 'user', 'content': f"{self.talk} in {self.spinWords.value()} words"})
        self.row_position = self.chat_table.rowCount()
        self.chat_table.insertRow(self.row_position)
        chatbot_name = self.cbxModel2.currentText().strip()
        get_replay_thread = threading.Thread(target=self.get_reply, args=(chatbot_name,))
        get_replay_thread.start()
    
    def showDetailsClicked(self):
        """
        Handles the event when the "Show Details" button is clicked.

        This method retrieves the currently selected chatbot model name from the combo box,
        executes a shell command to show details of the selected chatbot using the `ollama` tool,
        and displays the output in the chat table.

        Steps:
        1. Get the selected chatbot model name from the combo box.
        2. Run the `ollama show` command with the selected chatbot name.
        3. Capture the output of the command.
        4. Insert a new row in the chat table.
        5. Add the command output as a reply message in the chat table.

        Note:
        - This method assumes that the `ollama` tool is installed and available in the system's PATH.
        - The method uses `subprocess.run` to execute the shell command.

        Returns:
            None
        """
        chatbot_name = self.cbxModels.currentText().strip()
        result = subprocess.run("ollama show " + chatbot_name, shell=True, capture_output=True, text=True)
        out = result.stdout
        self.row_position = self.chat_table.rowCount()
        self.chat_table.insertRow(self.row_position)
        self.addReplyMessage(out)
    
    def cbxModelsIndexChanged(self):
        """
        Handles the event when the index of the model selection combo box changes.

        This method stops the currently running chatbot process and starts a new one
        based on the newly selected model from the combo box.

        Steps:
        1. Stops the current chatbot process using the `ollama stop` command.
        2. Retrieves the newly selected chatbot model name from the combo box.
        3. Updates the `self.chatbot_name` attribute with the new model name.
        4. Starts a new chatbot process using the `ollama run` command with the new model name.

        Note:
        - This method suppresses the standard output and error output of the subprocess commands.

        """
        subprocess.run("ollama stop " + self.chatbot_name, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        chatbot_name = self.cbxModels.currentText().strip()
        self.chatbot_name = chatbot_name
        subprocess.run("ollama run " + chatbot_name, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
    def sendClicked(self):
        """
        Handles the event when the send button is clicked.
        This method retrieves the message from the input area, adds it to the chat table,
        and initiates the process to get a reply from the selected chatbot model.
        Steps:
        1. Retrieve the message from the input area.
        2. If the message is not empty, add it to the chat table with the sender's name "You".
        3. Insert a new row in the chat table for the message.
        4. Get the selected chatbot model name from the combo box.
        5. Run the selected chatbot model using a subprocess.
        6. Append the user's message to the chat history.
        7. Start a new thread to get a reply from the chatbot model.
        8. Clear the input area.
        Note:
        - The subprocess runs the chatbot model command silently without showing any output.
        - The reply from the chatbot model is fetched in a separate thread to avoid blocking the UI.
        Args:
            None
        Returns:
            None
        """
        message = self.input_area.text().strip()
        if message:
            self.addSendMessage("You", message) 
            self.row_position = self.chat_table.rowCount()
            self.chat_table.insertRow(self.row_position)
            
            chatbot_name = self.cbxModels.currentText().strip()
            subprocess.run("ollama run " + chatbot_name, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.chat_history.append({'role': 'user', 'content': message})
                    
            get_replay_thread = threading.Thread(target=self.get_reply, args=(chatbot_name, ))      
            get_replay_thread.start()
            self.input_area.clear()
    def get_reply(self, chatbot_name): 
        """
        Generates a reply from the chatbot and updates the chat history.
        Args:
            chatbot_name (str): The name of the chatbot model to use for generating replies.
        Emits:
            print_message (str): Emits the current reply text with the chatbot's name as a header.
        Updates:
            self.chat_history (list): Appends the generated reply to the chat history.
            self.talk (str): Stores the generated reply text.
        """
        stream = chat(
                        model=chatbot_name,
                        messages=self.chat_history,
                        stream=True,
                    )
        
        header_text = f"🤖**{chatbot_name}**🤖:<br>"
        reply_text = ""
        for chunk in stream:
            reply_content = chunk['message']['content']
            reply_text += reply_content
            self.print_message.emit(header_text + reply_text)     
        self.chat_history.append({'role': 'assistant', 'content': reply_text}) 
        self.talk = reply_text
        if self.cbEnableVoice.isChecked():
            sentences = self.talk.split('.')
            for sentence in sentences:
                if sentence:
                    # Vary rate and volume for expression
                    self.engine.setProperty('rate', 150 if '!' not in sentence else 180)
                    self.engine.setProperty('volume', 0.9 if '?' not in sentence else 0.8)
                    self.engine.say(sentence)
                    self.engine.runAndWait()
    
    def addSendMessage(self, sender, message):
        """
        Adds a message to the chat table with the specified sender and message content.
        Args:
            sender (str): The name of the sender.
            message (str): The message content to be added.
        This method formats the message using markdown, converts it to HTML, and creates a QLabel
        to display the message. The QLabel is then added to a new row in the chat table, and the
        table is updated to fit the new content and scroll to the bottom.
        """
        md_text = f"😎**{sender}**😎:<br> {message}"
        html_text = markdown2.markdown(md_text)
        send_label = QLabel(html_text)
        send_label.setObjectName("send_label")
        send_label.setAlignment(Qt.AlignLeft)
        send_label.setWordWrap(True)
        
        row_position = self.chat_table.rowCount()
        self.chat_table.insertRow(row_position)
        self.chat_table.setCellWidget(row_position, 0, send_label)
        self.chat_table.resizeRowsToContents()
        self.chat_table.scrollToBottom()
            
    def addReplyMessage(self, reply_text):
        """
        Adds a reply message to the chat table.
        This method takes a reply message in markdown format, converts it to HTML,
        and adds it as a QLabel widget to the chat table. The label is configured
        to adjust its size, align text to the left, wrap words, and allow external
        links to be opened.
        Args:
            reply_text (str): The reply message in markdown format.
        """
        if reply_text:
            markdown_text = reply_text.strip()
            html_text = markdown2.markdown(markdown_text, extras=["fenced-code-blocks", "tables", "strike", "target-blank-links"])
            reply_label = QLabel(html_text)
            reply_label.adjustSize()
            reply_label.setObjectName("reply_label")
            reply_label.setAlignment(Qt.AlignLeft)
            reply_label.setWordWrap(True)
            reply_label.setOpenExternalLinks(True)
        
            if self.row_position < self.chat_table.rowCount():
                self.chat_table.setCellWidget(self.row_position, 0, reply_label)
            self.chat_table.resizeRowsToContents()
            self.chat_table.scrollToBottom()


app = QtWidgets.QApplication(sys.argv)
app.setStyleSheet(Path('theme.qss').read_text())
window = MainWindow()
window.show()
app.exec()