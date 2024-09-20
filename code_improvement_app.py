import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, QLineEdit, QProgressBar
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont
import anthropic

class ApiKeyInput(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Enter Anthropic API Key")
        self.setEchoMode(QLineEdit.EchoMode.Password)
        self.textChanged.connect(self.on_text_changed)

    def on_text_changed(self):
        if self.text():
            self.setStyleSheet("background-color: lightgreen;")
        else:
            self.setStyleSheet("")

class WorkerThread(QThread):
    result_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    def __init__(self, client, prompt, model="claude-3-5-sonnet-20240620"):
        super().__init__()
        self.client = client
        self.prompt = prompt
        self.model = model

    def run(self):
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": self.prompt}
                ]
            )
            self.result_signal.emit(response.content[0].text)
        except Exception as e:
            self.error_signal.emit(str(e))

class CodeImprovementApp(QWidget):
    def __init__(self):
        super().__init__()
        self.current_example = 1
        self.total_examples = 3
        self.score = 0
        self.client = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Code Improvement Learning App')
        self.setGeometry(100, 100, 1200, 1000)

        layout = QVBoxLayout()

        # Set larger font
        large_font = QFont()
        large_font.setPointSize(14)

        # API Key input
        api_key_layout = QHBoxLayout()
        api_key_layout.addStretch(1)
        self.api_key_input = ApiKeyInput()
        self.api_key_input.setFixedWidth(300)
        self.api_key_input.setFont(large_font)
        self.api_key_input.textChanged.connect(self.update_client)
        api_key_layout.addWidget(self.api_key_input)
        layout.addLayout(api_key_layout)

        # Area input
        self.area_input = QLineEdit()
        self.area_input.setFont(large_font)
        self.area_input.textChanged.connect(self.check_area_input)
        area_label = QLabel('Enter area to improve:')
        area_label.setFont(large_font)
        layout.addWidget(area_label)
        layout.addWidget(self.area_input)

        # Code display and input
        self.code_input = QTextEdit()
        self.code_input.setFont(large_font)
        code_label = QLabel('Bad Code Example <b>(Add your comments where the code is bad)</b>:')
        code_label.setFont(large_font)
        layout.addWidget(code_label)
        layout.addWidget(self.code_input)

        # Buttons
        button_layout = QHBoxLayout()
        self.create_btn = QPushButton('Create Example')
        self.create_btn.setFont(large_font)
        self.create_btn.clicked.connect(self.generate_bad_code)
        self.create_btn.setEnabled(False)  # Initially disabled
        self.submit_btn = QPushButton('Submit answer')
        self.submit_btn.setFont(large_font)
        self.submit_btn.clicked.connect(self.submit_annotation)
        self.next_btn = QPushButton('Next Example')
        self.next_btn.setFont(large_font)
        self.next_btn.clicked.connect(self.next_example)
        self.next_btn.setEnabled(False)
        button_layout.addWidget(self.create_btn)
        button_layout.addWidget(self.submit_btn)
        button_layout.addWidget(self.next_btn)
        layout.addLayout(button_layout)

        # Feedback display
        self.feedback_display = QTextEdit()
        self.feedback_display.setFont(large_font)
        self.feedback_display.setReadOnly(True)
        feedback_label = QLabel('Feedback:')
        feedback_label.setFont(large_font)
        layout.addWidget(feedback_label)
        layout.addWidget(self.feedback_display)

        # Add status label and progress bar
        self.status_label = QLabel()
        status_font = QFont()
        status_font.setPointSize(14)
        status_font.setBold(True)
        self.status_label.setFont(status_font)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.hide()
        layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

        # Disable submit button initially
        self.submit_btn.setEnabled(False)

    def show_loading(self, status):
        self.status_label.setText(status)
        self.status_label.show()
        self.progress_bar.show()
        self.create_btn.setEnabled(False)
        self.submit_btn.setEnabled(False)
        self.next_btn.setEnabled(False)
        self.api_key_input.setEnabled(False)
        QApplication.processEvents()

    def hide_loading(self):
        self.status_label.hide()
        self.progress_bar.hide()
        self.api_key_input.setEnabled(True)
        self.update_button_states()
        QApplication.processEvents()

    def generate_bad_code(self):
        if not self.client:
            self.feedback_display.setPlainText("Please enter a valid Anthropic API key.")
            return

        area = self.area_input.text()
        if not area:
            self.feedback_display.setPlainText("Please enter an area to improve.")
            return

        self.show_loading("Creating smelly code ...")
        prompt = f"Create a bad code example for {area}. The code should demonstrate poor practices related to {area}. Provide only the code without any explanations."
        
        self.worker = WorkerThread(self.client, prompt)
        self.worker.result_signal.connect(self.handle_bad_code_result)
        self.worker.error_signal.connect(self.handle_error)
        self.worker.start()

    def handle_bad_code_result(self, bad_code):
        self.code_input.setPlainText(bad_code)
        self.update_button_states()
        self.hide_loading()

    def submit_annotation(self):
        if not self.client:
            self.feedback_display.setPlainText("Please enter a valid Anthropic API key.")
            return

        self.show_loading("Grading answers ...")
        annotated_code = self.code_input.toPlainText()
        area = self.area_input.text()
        prompt = f"The following is a bad code example for {area} with user annotations. Grade the annotations and provide feedback. If the annotations are correct, give a short explanation. If they're incorrect, provide the solution with an explanation:\n\n{annotated_code}"
        
        self.worker = WorkerThread(self.client, prompt)
        self.worker.result_signal.connect(self.handle_annotation_result)
        self.worker.error_signal.connect(self.handle_error)
        self.worker.start()

    def handle_annotation_result(self, feedback):
        self.feedback_display.setPlainText(feedback)
        if "correct" in feedback.lower():
            self.score += 1
        self.next_btn.setEnabled(True)
        self.hide_loading()

    def next_example(self):
        self.current_example += 1
        if self.current_example <= self.total_examples:
            self.code_input.clear()
            self.feedback_display.clear()
            self.next_btn.setEnabled(False)
            self.generate_bad_code()
        else:
            self.show_final_score()

    def show_final_score(self):
        self.generate_funny_feedback()
        self.area_input.clear()

    def generate_funny_feedback(self):
        self.show_loading()
        prompt = f"Generate a funny and encouraging feedback message for a user who scored {self.score} out of {self.total_examples} in a code improvement exercise. Use a humorous tone."
        
        self.worker = WorkerThread(self.client, prompt)
        self.worker.result_signal.connect(self.handle_funny_feedback_result)
        self.worker.error_signal.connect(self.handle_error)
        self.worker.start()

    def handle_funny_feedback_result(self, feedback):
        self.feedback_display.setPlainText(feedback)
        self.area_input.clear()
        self.code_input.clear()
        self.create_btn.setEnabled(False)
        self.submit_btn.setEnabled(False)
        self.next_btn.setEnabled(False)
        self.hide_loading()

    def handle_error(self, error_message):
        self.feedback_display.setPlainText(f"An error occurred: {error_message}")
        self.hide_loading()

    def check_area_input(self):
        self.create_btn.setEnabled(bool(self.area_input.text().strip()))

    def update_client(self):
        api_key = self.api_key_input.text().strip()
        if api_key:
            self.client = anthropic.Anthropic(api_key=api_key)
        else:
            self.client = None
        self.update_button_states()

    def update_button_states(self):
        has_api_key = bool(self.api_key_input.text().strip())
        has_area = bool(self.area_input.text().strip())
        has_code = bool(self.code_input.toPlainText().strip())
        self.create_btn.setEnabled(has_api_key and has_area)
        self.submit_btn.setEnabled(has_api_key and has_code)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = CodeImprovementApp()
    ex.show()
    sys.exit(app.exec())
