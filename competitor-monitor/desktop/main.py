import sys
import json
import base64
import requests
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLineEdit, QLabel, QFileDialog
)
from PyQt6.QtCore import Qt


API_BASE = "http://localhost:8000"


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Competitor Monitor — Desktop")
        self.resize(900, 700)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Backend URL:"))
        self.url_input = QLineEdit(API_BASE)
        layout.addWidget(self.url_input)

        layout.addWidget(QLabel("URL to parse:"))
        self.parse_input = QLineEdit()
        layout.addWidget(self.parse_input)

        btn_parse = QPushButton("Parse URL (/parse_demo)")
        btn_parse.clicked.connect(self.on_parse)
        layout.addWidget(btn_parse)

        btn_parse_all = QPushButton("Parse configured sites (/parse_all)")
        btn_parse_all.clicked.connect(self.on_parse_all)
        layout.addWidget(btn_parse_all)

        btn_analyze_text = QPushButton("Analyze sample text (/analyze_text)")
        btn_analyze_text.clicked.connect(self.on_analyze_text)
        layout.addWidget(btn_analyze_text)

        btn_analyze_image = QPushButton("Analyze image file (/analyze_image)")
        btn_analyze_image.clicked.connect(self.on_analyze_image)
        layout.addWidget(btn_analyze_image)

        layout.addWidget(QLabel("Output:"))
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        self.setLayout(layout)

    def log(self, text: str):
        self.output.append(text)

    def backend(self):
        return self.url_input.text().rstrip('/')

    def on_parse(self):
        url = self.parse_input.text().strip()
        if not url:
            self.log("Введите URL для парсинга")
            return
        endpoint = f"{self.backend()}/parse_demo"
        self.log(f"POST {endpoint} -> {url}")
        try:
            r = requests.post(endpoint, json={"url": url}, timeout=30)
            self.log(f"Status: {r.status_code}")
            self.log(json.dumps(r.json(), ensure_ascii=False, indent=2))
        except Exception as e:
            self.log(f"Ошибка: {e}")

    def on_parse_all(self):
        endpoint = f"{self.backend()}/parse_all"
        self.log(f"POST {endpoint}")
        try:
            r = requests.post(endpoint, timeout=120)
            self.log(f"Status: {r.status_code}")
            self.log(json.dumps(r.json(), ensure_ascii=False, indent=2))
        except Exception as e:
            self.log(f"Ошибка: {e}")

    def on_analyze_text(self):
        endpoint = f"{self.backend()}/analyze_text"
        sample = "Наша компания предлагает выгодные решения для бизнеса." * 2
        self.log(f"POST {endpoint} (sample text)")
        try:
            r = requests.post(endpoint, json={"text": sample}, timeout=60)
            self.log(f"Status: {r.status_code}")
            self.log(json.dumps(r.json(), ensure_ascii=False, indent=2))
        except Exception as e:
            self.log(f"Ошибка: {e}")

    def on_analyze_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "", "Images (*.png *.jpg *.jpeg *.gif *.webp)")
        if not path:
            return
        endpoint = f"{self.backend()}/analyze_image"
        self.log(f"POST {endpoint} file={path}")
        try:
            with open(path, 'rb') as f:
                files = {'file': (path.split('/')[-1], f, 'application/octet-stream')}
                r = requests.post(endpoint, files=files, timeout=120)
            self.log(f"Status: {r.status_code}")
            try:
                self.log(json.dumps(r.json(), ensure_ascii=False, indent=2))
            except Exception:
                self.log(r.text)
        except Exception as e:
            self.log(f"Ошибка: {e}")


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
