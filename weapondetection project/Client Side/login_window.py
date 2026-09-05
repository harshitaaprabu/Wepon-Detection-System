from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.uic import loadUi
from settings_window import SettingsWindow
import webbrowser
import requests

class LoginWindow(QMainWindow):
    def __init__(self):
        super(LoginWindow, self).__init__()
        loadUi('UI/login_window.ui', self)

        self.register_button.clicked.connect(self.go_to_register_page)
        self.login_button.clicked.connect(self.login)

        self.show()

    def go_to_register_page(self):
        webbrowser.open('http://127.0.0.1:8000/register/')

    def login(self):
        try:
            url = 'http://127.0.0.1:8000/api/get_auth_token/'

            response = requests.post(
                url,
                data={
                    'username': self.username_input.text(),
                    'password': self.password_input.text()
                }
            )

            print("STATUS CODE:", response.status_code)
            print("RESPONSE TEXT:", response.text)

            if response.status_code == 200:
                json_response = response.json()
                print("JSON RESPONSE:", json_response)

                token = json_response['token']
                self.open_settings_window(token)

            else:
                msg = QMessageBox()
                msg.setWindowTitle("Login Failed")
                msg.setText("Username or Password is not correct")
                msg.exec_()

        except Exception as e:
            print("REAL ERROR:", e)

            msg = QMessageBox()
            msg.setWindowTitle("Error")
            msg.setText(str(e))
            msg.exec_()

    def open_settings_window(self, token):
        self.settings_window = SettingsWindow(token)  # ✅ PASS TOKEN
        self.settings_window.displayInfo()
        self.close()