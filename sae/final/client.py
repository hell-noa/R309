import sys
import socket
import threading
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

flag = False
client_socket = socket.socket()

# Variable globale pour stocker le canal actuel
current_channel = "Générale"

# Classe pour émettre un signal entre les threads
class MessageSignal(QObject):
    message_received = pyqtSignal(str)

# Ajoutez la classe Inscription
class Inscription(QWidget):
    # Ajoutez un signal pour la fermeture de la fenêtre
    close_window_signal = pyqtSignal()
    # Ajoutez un signal pour afficher le message d'erreur d'alias déjà utilisé
    alias_error_signal = pyqtSignal()

    def __init__(self, chat_window):
        super().__init__()
        self.chat_window = chat_window
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Page d\'Inscription')
        self.resize(500, 300)

        self.login = QLabel("nom d'utilisateur :")
        self.mdp = QLabel("mot de passe :")
        self.alias = QLabel("alias unique :")
        self.username_input = QLineEdit(self)
        self.password_input = QLineEdit(self)
        self.alias_input = QLineEdit(self)
        self.send_button = QPushButton('envoi :')
        self.send_button.clicked.connect(self.inscription)

        layout = QVBoxLayout()
        layout.addWidget(self.login)
        layout.addWidget(self.username_input)
        layout.addWidget(self.mdp)
        layout.addWidget(self.password_input)
        layout.addWidget(self.alias)
        layout.addWidget(self.alias_input)
        layout.addWidget(self.send_button)

        self.setLayout(layout)

        # Connecter le signal alias_error_signal à la méthode show_alias_error
        self.alias_error_signal.connect(self.show_alias_error)

    def inscription(self):
        username = self.username_input.text()
        password = self.password_input.text()
        alias = self.alias_input.text()
        client_socket.send(f"INSCRI/{username},{password},{alias}".encode())

    def closeEvent(self, event):
        # Émettre le signal pour fermer la fenêtre d'inscription
        self.close_window_signal.emit()
        event.accept()

    # Ajoutez la méthode pour afficher le message d'erreur d'alias déjà utilisé
    def show_alias_error(self):
        QMessageBox.critical(self, "Erreur d'alias", "Cet alias est déjà utilisé. Veuillez en choisir un autre.")

class Connexion(QWidget):
    auth_success_signal = pyqtSignal(str)

    def __init__(self, message_signal):
        super().__init__()
        self.message_signal = message_signal
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Page de Connexion')
        self.resize(300, 150)

        self.username_input = QLineEdit(self)
        self.password_input = QLineEdit(self)

        login_button = QPushButton('Se connecter', self)
        login_button.clicked.connect(self.authenticate)

        inscri_button = QPushButton("S'inscrire", self)
        inscri_button.clicked.connect(self.show_inscription_window)

        layout = QVBoxLayout()
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(login_button)
        layout.addWidget(inscri_button)

        self.setLayout(layout)

    def authenticate(self):
        username = self.username_input.text()
        password = self.password_input.text()
        client_socket.send(f"LOGIN/{username},{password}".encode())

        # Si l'authentification réussit, émettre le signal d'authentification réussie avec le nom d'utilisateur
        self.auth_success_signal.emit(username)

    def show_inscription_window(self):
        # Utiliser self.inscription_window pour garder une référence à la fenêtre d'inscription
        self.inscription_window = Inscription(chat_window)
        # Connecter le signal de fermeture de la fenêtre à la méthode d'ouverture
        self.inscription_window.close_window_signal.connect(self.show)
        self.inscription_window.show()

class DemandeAccesWindow(QWidget):
    # Ajoutez un signal pour transmettre le canal sélectionné
    access_requested_signal = pyqtSignal(str)

    def __init__(self, channels):
        super().__init__()
        self.channels = channels
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Demande d\'accès')
        self.resize(300, 150)

        self.channel_combo = QComboBox(self)
        self.channel_combo.addItems(["Sélectionnez un canal"] + self.channels)

        demander_button = QPushButton('Demander l\'accès', self)
        demander_button.clicked.connect(self.demander_acces)

        layout = QVBoxLayout()
        layout.addWidget(self.channel_combo)
        layout.addWidget(demander_button)

        self.setLayout(layout)

    def demander_acces(self):
        selected_channel = self.channel_combo.currentText()
        if selected_channel != "Sélectionnez un canal":
            # Émettre le signal avec le canal sélectionné
            self.access_requested_signal.emit(selected_channel)
            self.close()

class ChatWindow(QWidget):
    def __init__(self, client_socket, message_signal, connexion_window):
        super().__init__()
        self.client_socket = client_socket
        self.message_signal = message_signal
        self.connexion_window = connexion_window
        self.username = ""
        self.allowed_channels = []
        self.demande_acces_window = None  # Ajoutez cette ligne
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Chat')
        self.resize(800, 600)

        self.text_edits = {
            "Générale": QTextEdit(),
            "Blabla": QTextEdit(),
            "Informatique": QTextEdit(),
            "Marketing": QTextEdit(),
            "Comptabilité": QTextEdit()
        }

        for text_edit in self.text_edits.values():
            text_edit.setReadOnly(True)
        
        self.input_line = QLineEdit()
        self.send_button = QPushButton('envoi')
        self.qcombo = QComboBox()

        self.qcombo.addItems(["veuillez choisir un channel", "Générale", "Blabla", "Informatique", "Marketing", "Comptabilité"])

        self.qcombo.currentIndexChanged.connect(self.change_channel)

        layout = QVBoxLayout()
        layout.addWidget(self.qcombo)

        # Ajoutez tous les QTextEdit à votre mise en page
        for text_edit in self.text_edits.values():
            layout.addWidget(text_edit)
            text_edit.hide()

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_line)
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)
        self.setLayout(layout)

        self.send_button.clicked.connect(self.send_message)

        # Ajoutez un bouton pour demander l'accès
        self.demande_acces_button = QPushButton("Demander l'accès")
        self.demande_acces_button.clicked.connect(self.demande_acces)
        layout.addWidget(self.demande_acces_button)

        try:
            self.client_socket.connect((host, port))
            t1 = threading.Thread(target=self.reception)
            t1.start()
        except ConnectionAbortedError:
            print('La connexion a été coupée')
            fermeture()

    def send_message(self):
        message = self.input_line.text()
        if message:
            try:
                # Remplacez 'Générale' par le canal actuel sélectionné dans le QComboBox
                self.client_socket.send(f"MESSAGE/{current_channel}/{self.username},{message}".encode())
                print(f"{message}")
                # Remplacez self.text_edits["Générale"] par le QTextEdit correspondant au canal actuel
                self.text_edits[current_channel].append(f"moi: {message}")
                self.input_line.clear()
                if message == 'bye':
                    sys.exit()
            except ConnectionAbortedError:
                print('La connexion a été coupée')
                fermeture()
            except ConnectionResetError:
                print('La connexion a été réinitialisée')
                fermeture()
            except OSError:
                print('Vous avez bien été déconnecté')
                fermeture()

    def reception(self):
        global flag, current_channel
        while not flag:
            try:
                print("j'attends un message : ")
                reply = client_socket.recv(1024).decode()
                print(reply)
                # Utiliser invokeMethod pour mettre à jour l'interface utilisateur dans le thread principal
                if reply.startswith('MESSAGE/'):
                    messages = reply.split('/')
                    channel = messages[1]
                    user_and_message = messages[2].split(',')
                    username = user_and_message[0]
                    message_content = user_and_message[1]

                    if channel == current_channel:
                        print(1)
                        QMetaObject.invokeMethod(self, 'update_text_edit', Qt.QueuedConnection,
                                                 Q_ARG(str, reply), Q_ARG(str, channel), Q_ARG(str, username),
                                                 Q_ARG(str, message_content))

                if reply == 'bye':
                    fermeture()

                elif reply == "ACCEPT":
                    QTimer.singleShot(0, self.show_chat)

                elif reply == "insertion_ok":
                    QTimer.singleShot(0, self.close_inscription_window)

                elif reply == "insertion_no":
                    # Émettre le signal pour afficher le message d'erreur d'alias déjà utilisé
                    self.connexion_window.inscription_window.alias_error_signal.emit()

                elif reply.startswith("ACCES/"):
                    print(reply)
                    self.verif_channel(reply)

            except ConnectionAbortedError:
                print('La connexion a été coupée')
                fermeture()
            except ConnectionResetError:
                print('La connexion a été réinitialisée')
                fermeture()

        else:
            print('Fermeture de la connexion côté client')

    def change_channel(self, index):
        channels = ["Générale", "Blabla", "Informatique", "Marketing", "Comptabilité"]
        global current_channel
        new_channel = channels[index - 1]
        print(f'ici      {self.allowed_channels}')

        # Vérifier si le nouveau canal est autorisé
        if new_channel in self.allowed_channels:
            # Cachez tous les QTextEdit
            for text_edit in self.text_edits.values():
                text_edit.hide()

            # Changer le canal actuel seulement si le nouveau canal est autorisé
            current_channel = new_channel

            # Affichez le QTextEdit correspondant au channel sélectionné
            if current_channel in self.text_edits:
                self.text_edits[current_channel].show()
        else:
            # Le nouveau canal n'est pas autorisé, affichez un message d'erreur
            QMessageBox.warning(self, "Accès refusé",
                                f"Vous n'avez pas accès au canal {new_channel}")
            # Rétablissez la sélection précédente dans le QComboBox
            self.qcombo.setCurrentIndex(channels.index(current_channel) + 1)

    def verif_channel(self, reply):
        try:
            # Extraire les permissions du message de réponse
            permissions = reply.split('/')[1]
            print(permissions)
            correspondances = {'G': 'Générale', 'B': 'Blabla', 'I': 'Informatique', 'M': 'Marketing', 'C': 'Comptabilité'}

            # Créer une liste des canaux autorisés à partir des lettres
            self.allowed_channels = [correspondances[letter] for letter in permissions]

            print(f"Vous avez accès aux canaux suivants : {', '.join(self.allowed_channels)}")

        except Exception as e:
            print(f"Erreur lors de la vérification des canaux : {e}")

    def show_chat(self):
        self.connexion_window.hide()
        self.show()

    @pyqtSlot(str, str, str, str)
    def update_text_edit(self, reply, channel, username, message_content):
        # Remplacez self.text_edits["Générale"] par le QTextEdit correspondant au canal actuel
        self.text_edits[channel].append(f"{username}: {message_content}")

    def close_inscription_window(self):
        # Fermer la fenêtre d'inscription lorsque le signal est reçu
        self.connexion_window.inscription_window.close()

    def set_username(self, username):
        self.username = username
        # Utilisez self.username comme nécessaire dans votre application

    def demande_acces(self):
         # Afficher la fenêtre de demande d'accès avec la liste des canaux
         self.demande_acces_window = DemandeAccesWindow(["Générale", "Blabla", "Informatique", "Marketing", "Comptabilité"])

         # Connecter le signal access_requested_signal à la méthode process_access_request
         self.demande_acces_window.access_requested_signal.connect(self.process_access_request)

         self.demande_acces_window.show()

    def process_access_request(self, requested_channel):
        # Envoyer la demande d'accès au serveur
        print(self.username)
        self.client_socket.send(f"DEMANDE/{requested_channel}/{self.username}".encode())

def fermeture():
    global flag
    print('Fermeture demandée')
    flag = True
    
    
def get_address_ip():
    # utilisation d'un DNS public pour obtenir l'adresse IP externe
    try:
        address_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        address_socket.connect(("8.8.8.8", 80))
        address_ip = address_socket.getsockname()[0]
        address_socket.close()
        print(address_ip)
        return address_ip
    except socket.error:
        return None


host, port = (str(get_address_ip()), 1234)

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        message_signal = MessageSignal()
        connexion_window = Connexion(message_signal)
        chat_window = ChatWindow(client_socket, message_signal, connexion_window)

        # Connecter le signal d'authentification réussie à la méthode set_username dans ChatWindow
        connexion_window.auth_success_signal.connect(chat_window.set_username)

        connexion_window.show()
        sys.exit(app.exec_())

    finally:
        pass

