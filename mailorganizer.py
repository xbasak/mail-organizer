# This Python file uses the following encoding: utf-8
import sys
import imaplib
import email
import threading
# noinspection PyUnresolvedReferences
import resources_rc
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMainWindow, QListWidgetItem
from PySide6.QtCore import Slot, Qt, Signal, QObject
from PySide6.QtUiTools import QUiLoader


# noinspection PyUnresolvedReferences
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Mail organizer')
        self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        loader = QUiLoader()
        self.window = loader.load("mainwindow.ui", self)
        self.window.progressBar.setVisible(False)
        self.show()
        self.window.comboBox.activated.connect(self.setSite) #Picking mail server
        self.window.confirmLogin.clicked.connect(self.confirmLogin) #Logging
        self.window.confirmFolder.clicked.connect(self.confirmFolder) #Picking folder
        self.network_process = None


    def closeEvent(self, event):
        if self.network_process is not None:
            self.network_process.running = False
            self.network_process.join()  # Waiting for thread to end
        event.accept()


    @Slot()
    def confirmFolder(self):
        checkedItems = []
        #creating list of folders
        for index in range(self.window.list.count()):
            item = self.window.list.item(index)
            if item.checkState() == Qt.Checked:
                checkedItems.append(item.text())


        if checkedItems:
            self.network_process = NetworkProcess(self.server, self.username, self.password,self.mail, checkedItems, self.window)
            self.network_process.signals.progress_updated.connect(self.progress_update)
            self.network_process.signals.append_text.connect(self.text_append)
            self.network_process.start()
            self.window.progressBar.setVisible(True)
            self.window.label_7.setText('Reading messages... ')

    @Slot()
    def confirmLogin(self):
        self.window.label_6.setText('Starting to log in...')
        self.username = self.window.usr_mail.text()
        self.password = self.window.usr_passwd.text()
        self.server = self.window.comboBox.currentText()
        try:
            #connecting with IMAP server
            self.mail = imaplib.IMAP4_SSL(self.server, 993)
            self.mail.login(self.username, self.password)
            self.window.label_6.setText('Login successful')
            self.window.label_6.setStyleSheet('color: green')
            for i in self.mail.list()[-1]:
                directories = str(i)
                directory = str(directories.split('"')[-2])
                # directory = directory.replace('&AUI-','ł')
                # directory = directory.replace('&AVs-', 'ś')
                item = QListWidgetItem(directory)
                self.window.list.addItem(item)
                item.setCheckState(Qt.Unchecked)
        except Exception as e:
            self.window.label_6.setText('An error occured. Try again')
            self.window.label_6.setStyleSheet('color: red')
            print("An error occured:", str(e))

    @Slot()
    def setSite(self):
        return self.window.comboBox.currentText()

    @Slot(int)
    def progress_update(self, value):
        self.window.progressBar.setValue(value)

    @Slot(str)
    def text_append(self, text, counter):
        self.window.textEdit.append(text)
        self.window.label_12.setText(str(counter))

class WorkerSignals(QObject):
    progress_updated = Signal(int)
    append_text = Signal(str,int)

# noinspection PyTypeChecker
class NetworkProcess(threading.Thread):
    def __init__(self, server, username, password,mail, selected_folders, window):
        super().__init__()
        self.server = server
        self.username = username
        self.password = password
        self.mail = mail
        self.selected_folders = selected_folders
        self.window = window
        self.signals = WorkerSignals()
        self.running = True

    def run(self):
        with open('data.txt', 'r') as file:
            lines = [line.strip() for line in file]
        file.close()
        print(lines)
        self.window.setWindowFlags(Qt.WindowMinimizeButtonHint)
        try:
            for folder in self.selected_folders:
                counter = 0
                self.window.label_14.setText(folder)
                if not self.running:
                    break
                self.mail.select(folder)
                _, message_numbers = self.mail.search(None, "ALL") # getting all messages
                message_numbers = message_numbers[0].split()
                length = len(message_numbers)
                self.window.label_13.setText(str(length))
                i = 0
                self.window.progressBar.setRange(0,length)
                for num in message_numbers:
                    if not self.running:
                        break
                    print(num)
                    _, message_data = self.mail.fetch(num, "(RFC822)")
                    try:
                        message_data_bytes = message_data[0][1]
                        message = email.message_from_bytes(message_data_bytes)
                        mail_source = message['From']
                        if message_data is not None:
                            for source in lines:
                                print(mail_source.find(source))
                                if mail_source.find(source) > 0:
                                    self.mail.store(num, '+FLAGS', '\\Deleted')
                                    counter += 1
                                    self.signals.append_text.emit("From: " + message["From"],counter)
                    except Exception as e:
                        print("Error processing message: ", str(e))
                    self.signals.progress_updated.emit(i+1)
                    i+=1
                self.signals.append_text.emit("", counter)
        except Exception as e:
            self.window.label_6.setText('Try again. An error occured: '+str(e))
            print('Try again. An error occured: '+str(e))
        self.mail.logout()
        self.window.label_7.setText('Cleaning completed!')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('images/icon.png'))
    win = MainWindow()
    sys.exit(app.exec())
