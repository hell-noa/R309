import sys
import socket
import threading
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

flag = False
client_socket = socket.socket()
current_channel = "Générale"



class MessageSignal(QObject):
    """
    Classe pour émettre un signal entre les threads.
    
    Signal:
        message_received (pyqtSignal): Signal émis lorsqu'un message est reçu.
    """
    message_received = pyqtSignal(str)



class Inscription(QWidget):
    """
    Classe représentant la fenêtre d'inscription.

    Signal:
        close_window_signal (pyqtSignal): Signal émis lors de la fermeture de la fenêtre d'inscription.
        alias_error_signal (pyqtSignal): Signal émis pour afficher le message d'erreur d'alias déjà utilisé.
    """
    close_window_signal = pyqtSignal()
    alias_error_signal = pyqtSignal()
    

    def __init__(self, chat_window):
        """
        Initialise la fenêtre d'inscription.

        :param chat_window: Fenêtre principale du chat.
        :type chat_window: ChatWindow
        """
        
        super().__init__()
        self.chat_window = chat_window
        self.init_ui()
        

    def init_ui(self):
        """
        Initialise l'interface utilisateur de la fenêtre d'inscription.
        """
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
        self.alias_error_signal.connect(self.show_alias_error)
        

    def inscription(self):
        """
        Traite le processus d'inscription en récupérant les informations de l'utilisateur.
        """
        username = self.username_input.text()
        password = self.password_input.text()
        alias = self.alias_input.text()
        client_socket.send(f"INSCRI/{username},{password},{alias}".encode())
        

    def closeEvent(self, event):
        """
        Événement déclenché lors de la fermeture de la fenêtre d'inscription.

        :param event: Événement de fermeture.
        :type event: QCloseEvent
        """
        self.close_window_signal.emit()
        event.accept()
        

    def show_alias_error(self):
        """
        Affiche le message d'erreur d'alias déjà utilisé.
        """
        QMessageBox.critical(self, "Erreur d'alias", "Cet alias est déjà utilisé. Veuillez en choisir un autre.")

class Connexion(QWidget):
    """
    Gère l'interface de la fenêtre de connexion.

    Signal:
        auth_success_signal (pyqtSignal): Signal émis lors de l'authentification réussie avec le nom d'utilisateur.
    """
    auth_success_signal = pyqtSignal(str)
    

    def __init__(self, message_signal):
        """
        Initialise la fenêtre de connexion.

        :param message_signal: Objet de signal pour la communication entre threads.
        :type message_signal: MessageSignal
        """
        super().__init__()
        self.message_signal = message_signal
        self.init_ui()
        

    def init_ui(self):
        """
        Initialise l'interface utilisateur de la fenêtre de connexion.
        """
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
        """
        Traite le processus d'authentification en récupérant les informations de l'utilisateur.
        """
        username = self.username_input.text()
        password = self.password_input.text()
        client_socket.send(f"LOGIN/{username},{password}".encode())
        self.auth_success_signal.emit(username)
        

    def show_inscription_window(self):
        """
        Affiche la fenêtre d'inscription lorsqu'elle est demandée.
        """
        self.inscription_window = Inscription(chat_window)
        self.inscription_window.close_window_signal.connect(self.show)
        self.inscription_window.show()
        
        

class DemandeAccesWindow(QWidget):
    """
    Gère l'interface de la fenêtre de demande d'accès à un canal.

    Signal:
        access_requested_signal (pyqtSignal): Signal émis avec le canal sélectionné pour la demande d'accès.
    """
    access_requested_signal = pyqtSignal(str)

    def __init__(self, channels):
        """
        Initialise la fenêtre de demande d'accès.

        :param channels: Liste des canaux disponibles.
        :type channels: list
        """
        super().__init__()
        self.channels = channels
        self.init_ui()
        

    def init_ui(self):
        """
        Initialise l'interface utilisateur de la fenêtre de demande d'accès.
        """
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
        """
        Traite la demande d'accès en récupérant le canal sélectionné.
        """
        selected_channel = self.channel_combo.currentText()
        if selected_channel != "Sélectionnez un canal":
            self.access_requested_signal.emit(selected_channel)
            self.close()
            
            

class ChatWindow(QWidget):
    def __init__(self, client_socket, message_signal, connexion_window):
        """
        Initialise la fenêtre principale du chat.

        :param client_socket: Objet socket pour la communication avec le serveur.
        :type client_socket: socket.socket
        :param message_signal: Objet de signal pour la communication entre threads.
        :type message_signal: MessageSignal
        :param connexion_window: Fenêtre de connexion associée.
        :type connexion_window: Connexion
        """
        super().__init__()
        self.client_socket = client_socket
        self.message_signal = message_signal
        self.connexion_window = connexion_window
        self.username = ""
        self.allowed_channels = []
        self.demande_acces_window = None  
        self.init_ui()


    def init_ui(self):
        """
        Initialise l'interface utilisateur de la fenêtre principale du chat.
        """
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

        for text_edit in self.text_edits.values():
            layout.addWidget(text_edit)
            text_edit.hide()

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_line)
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)
        self.setLayout(layout)

        self.send_button.clicked.connect(self.send_message)

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
        """
        Envoie un message au serveur.
        """
        message = self.input_line.text()
        if message:
            try:
                self.client_socket.send(f"MESSAGE/{current_channel}/{self.username},{message}".encode())
                print(f"{message}")
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
        """
        Traite les messages reçus du serveur.
        """
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
        """
        Change le canal de discussion actuel.

        :param index: Indice du canal sélectionné dans le QComboBox.
        :type index: int
        """
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
        """
        Vérifie les autorisations d'accès aux canaux.

        :param reply: Message de réponse du serveur contenant les autorisations.
        :type reply: str
        """
        try:
            permissions = reply.split('/')[1]
            print(permissions)
            correspondances = {'G': 'Générale', 'B': 'Blabla', 'I': 'Informatique', 'M': 'Marketing', 'C': 'Comptabilité'}

            self.allowed_channels = [correspondances[letter] for letter in permissions]

            print(f"Vous avez accès aux canaux suivants : {', '.join(self.allowed_channels)}")

        except Exception as e:
            print(f"Erreur lors de la vérification des canaux : {e}")


    def show_chat(self):
        """
        Affiche la fenêtre principale du chat.
        """
        self.connexion_window.hide()
        self.show()


    @pyqtSlot(str, str, str, str)
    def update_text_edit(self, reply, channel, username, message_content):
        """
        Met à jour l'interface utilisateur avec un nouveau message.

        :param reply: Message complet reçu du serveur.
        :type reply: str
        :param channel: Canal auquel le message est destiné.
        :type channel: str
        :param username: Nom d'utilisateur de l'expéditeur du message.
        :type username: str
        :param message_content: Contenu du message.
        :type message_content: str
        """
        
        self.text_edits[channel].append(f"{username}: {message_content}")


    def close_inscription_window(self):
        """
        Ferme la fenêtre d'inscription.
        """
        self.connexion_window.inscription_window.close()
        

    def set_username(self, username):
        """
        Définit le nom d'utilisateur de l'utilisateur courant.

        :param username: Nom d'utilisateur de l'utilisateur courant.
        :type username: str
        """
        self.username = username


    def demande_acces(self):
        """
        Affiche la fenêtre de demande d'accès.
        """
         self.demande_acces_window = DemandeAccesWindow(["Générale", "Blabla", "Informatique", "Marketing", "Comptabilité"])
         self.demande_acces_window.access_requested_signal.connect(self.process_access_request)
         self.demande_acces_window.show()


    def process_access_request(self, requested_channel):
        """
        Traite la demande d'accès à un canal.

        :param requested_channel: Canal pour lequel l'accès est demandé.
        :type requested_channel: str
        """
        print(self.username)
        self.client_socket.send(f"DEMANDE/{requested_channel}/{self.username}".encode())


def fermeture():
    """
    Fonction pour gérer la fermeture de l'application.
    """
    global flag
    print('Fermeture demandée')
    flag = True
    
    
def get_address_ip():
    """
    Obtient l'adresse IP externe de l'utilisateur à l'aide d'un DNS public.

    :return: Adresse IP externe de l'utilisateur.
    :rtype: str ou None
    """
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

