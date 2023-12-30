import socket
import threading
from concurrent.futures import ThreadPoolExecutor
import mysql.connector

#entrez vos informations MySQL
mysql_host = ""
mysql_user = ""
mysql_password = ""
mysql_database = ""

def authentification_serveur(conn):
    """
    Gère les informaions admin du serveur grace a la table 'serveur' de la base de données MySQL.
    Si la table est vide, elle demande à l'utilisateur d'ajouter des informations sur le serveur.

    :param conn: Objet de connexion socket avec le serveur
    :type conn: socket.socket
    :return: True si l'authentification est réussie, False sinon
    :rtype: str
    """
    try:
        db = mysql.connector.connect(host=mysql_host, user=mysql_user, password=mysql_password, database=mysql_database)
        cursor = db.cursor()
        cursor.execute('SELECT * FROM serveur')
        serveur_info = cursor.fetchone()

        if serveur_info is None:
            new_log = input('Nouvel identifiant pour le serveur : ')
            new_mdp = input('Nouveau mot de passe pour le serveur : ')

            cursor.execute("INSERT INTO serveur (login , mdp) VALUES (%s, %s)", (new_log, new_mdp))
            db.commit()
            conn.send("Informations du serveur ajoutées avec succès.".encode())
            return True
        else:
            log = input('Identifiant admin : ')
            mdp = input('Mot de passe admin : ')
            if log == serveur_info[1] and mdp == serveur_info[2]:
                conn.send('ok'.encode())
                return True

    except Exception as e:
        print(f"Erreur lors de l'authentification du serveur : {e}")
        conn.send("ERROR".encode())
        return False

    finally:
        db.close()

def authentification_user(conn):
    """
    Gère l'authentification des utilisateurs avec une base de données MySQL.

    :param conn: Objet de connexion socket avec le client
    :type conn: socket.socket
    """
    try:
        db = mysql.connector.connect(host=mysql_host, user=mysql_user, password=mysql_password, database=mysql_database)
        cursor = db.cursor()
        query = 'SELECT * FROM user where pseudo = %s and mdp = %s'

        message = conn.recv(1024).decode()
        info_user = message.split("/")
        
        if info_user[0] == "LOGIN":
            identifiant = info_user[1].split(',')
            cursor.execute(query, (identifiant[0], identifiant[1]))
            resultat = cursor.fetchone()
            
            if resultat is None:
                print('Connexion refusée')
                   
            elif resultat:
                print('Connexion acceptée')
                message = 'ACCEPT'
                conn.send(message.encode())
                
            else:
                print('Connexion refusée')

    except (ConnectionAbortedError, ConnectionRefusedError, ConnectionResetError, OSError) as e:
        print(f"Erreur de connexion : {e}")

    finally:
        db.close()
        channel_verif(conn, identifiant[0])

def inscription(conn, message):
    """
    Gère le processus d'inscription des utilisateurs en ajoutant de nouveaux utilisateurs à la base de données.

    :param conn: Objet de connexion socket avec le client
    :type conn: socket.socket
    :param message: Message reçu du client contenant les informations d'inscription
    :type message: str
    """
    try:
        db = mysql.connector.connect(host=mysql_host, user=mysql_user, password=mysql_password, database=mysql_database)
        cursor = db.cursor()

        info_user = message.split("/")
        if info_user[0] == "INSCRI":
            identifiant = info_user[1].split(',')
            new_log = identifiant[0]
            new_mdp = identifiant[1]
            new_alias = identifiant[2]

            cursor.execute("SELECT * FROM user WHERE alias = %s", (new_alias,))
            result = cursor.fetchone()

            if result:
                message = 'insertion_no'
                conn.send(message.encode())
                print('Insertion échouée')

            else:
                cursor.execute("INSERT INTO user (pseudo , mdp, alias) VALUES (%s, %s, %s)", (new_log, new_mdp, new_alias))
                db.commit()
                print('Transaction effectuée')
                message = 'insertion_ok'
                conn.send(message.encode())

    except Exception as e:
        print(f"Erreur lors de l'inscription : {e}")

    finally:
        db.close()

def channel_verif(conn, pseudo):
    """
    Vérifie les autorisations d'accès aux canaux pour un utilisateur spécifique.

    :param conn: Objet de connexion socket avec le client
    :type conn: socket.socket
    :param pseudo: Pseudo de l'utilisateur
    :type pseudo: str
    """
    try:
        db = mysql.connector.connect(host=mysql_host, user=mysql_user, password=mysql_password, database=mysql_database)
        cursor = db.cursor()
        cursor.execute("SELECT channel_verif FROM user WHERE pseudo = %s", (pseudo,))
        result = cursor.fetchone()
        correspondances = {'1': 'GB', '2': 'GI', '3': 'GM', '4': 'GC', '12': 'GBI', '13': 'GBM', '14': 'GBC', '23': 'GIM',
                           '24': 'GIC', '34': 'GMC', '123': 'GBIM', '124': 'GBIC', '134': 'GBMC', '234': 'GIMC',
                           '1234': 'GBIMC'}

        conn.send(f"ACCES/{correspondances.get(result[0], 'G')}".encode())

    except Exception as e:
        print(f"Erreur : {e}")

    finally:
        db.close()

def channel_acces(conn, message):
    """
    Gère les demandes d'accès aux canaux et met à jour les autorisations dans la base de données.

    :param conn: Objet de connexion socket avec le client
    :type conn: socket.socket
    :param message: Message reçu du client contenant la demande d'accès à un canal
    :type message: str
    """
    try:
        db = mysql.connector.connect(host=mysql_host, user=mysql_user, password=mysql_password, database=mysql_database)
        cursor = db.cursor()

        info_user = message.split("/")
        pseudo = info_user[2]
        cursor.execute("SELECT channel_verif FROM user WHERE pseudo = %s", (pseudo,))
        current_channel_verif = cursor.fetchone()

        if current_channel_verif is not None and current_channel_verif[0] is not None:
            current_channel_verif = int(current_channel_verif[0])
        else:
            current_channel_verif = ""

        if info_user[0] == "DEMANDE":
            if info_user[1] == "Blabla":
                variable = str(current_channel_verif) + str(1)
                cursor.execute("UPDATE user SET channel_verif = %s WHERE pseudo = %s", (variable, pseudo))
                db.commit()

            elif info_user[1] == "Informatique":
                verif = input('YES/NO : ')
                if verif.lower() == 'yes':
                    variable = str(current_channel_verif) + str(2)
                    cursor.execute("UPDATE user SET channel_verif = %s WHERE pseudo = %s", (variable, pseudo))
                    db.commit()
                else:
                    pass

            elif info_user[1] == "Marketing":
                verif = input('YES/NO : ')
                if verif.lower() == 'yes':
                    variable = str(current_channel_verif) + str(3)
                    cursor.execute("UPDATE user SET channel_verif = %s WHERE pseudo = %s", (variable, pseudo))
                    db.commit()
                else:
                    pass

            elif info_user[1] == "Comptabilité":
                verif = input('YES/NO : ')
                if verif.lower() == 'yes':
                    variable = str(current_channel_verif) + str(4)
                    cursor.execute("UPDATE user SET channel_verif = %s WHERE pseudo = %s", (variable, pseudo))
                    db.commit()
                else:
                    pass

    except Exception as e:
        print(f"Erreur : {e}")

    else:
        pass

    finally:
        db.close()
        tri(conn, pseudo)

def tri(conn, pseudo):
    """
    Trie les autorisations d'accès aux canaux pour un utilisateur spécifique.

    :param conn: Objet de connexion socket avec le client
    :type conn: socket.socket
    :param pseudo: Pseudo de l'utilisateur
    :type pseudo: str
    """
    try:
        db = mysql.connector.connect(host=mysql_host, user=mysql_user, password=mysql_password, database=mysql_database)
        cursor = db.cursor()
        cursor.execute("SELECT channel_verif FROM user WHERE pseudo = %s", (pseudo,))
        resultat = cursor.fetchone()
        if resultat:
            verif = ''.join(sorted(resultat[0]))
            cursor.execute("UPDATE user SET channel_verif = %s WHERE pseudo = %s", (verif, pseudo))
            db.commit()
            db.close()

    except Exception as e:
        print(f"Erreur : {e}")

    finally:
        channel_verif(conn, pseudo)

def save_message(conn, message):
    """
    Enregistre les messages dans la base de données et les diffuse aux autres clients connectés.

    :param conn: Objet de connexion socket avec le client
    :type conn: socket.socket
    :param message: Message reçu du client contenant le message à enregistrer
    :type message: str
    """
    try:
        db = mysql.connector.connect(host=mysql_host, user=mysql_user, password=mysql_password, database=mysql_database)
        cursor = db.cursor()
        info_user = message
        info_user = info_user.split("/")

        if info_user[0] == "MESSAGE":
            information = info_user[2].split(',')
            user = information[0]
            contenu = information[1]
            channel = info_user[1]

            cursor.execute("SELECT id_user from user WHERE pseudo = %s", (user,))
            user = cursor.fetchone()[0]

            cursor.execute("SELECT channel_id from channel WHERE nom_channel = %s", (channel,))
            channel = cursor.fetchone()[0]

            cursor.execute("INSERT INTO message (contenu , id_user, channel_id) VALUES (%s, %s, %s)",
                           (contenu, user, channel))

            db.commit()
            broadcast(message, conn)

    except Exception as e:
        pass

    else:
        pass

    finally:
        db.close()

def main():
    """
    Fonction principale du serveur de chat.
    """
    port = 1234
    try:
        global server_socket
        server_socket = socket.socket()
        server_socket.bind(('0.0.0.0', port))
        server_socket.listen(5)
        global serv_start
        serv_start = True

        global clients
        clients = []

        with ThreadPoolExecutor(max_workers=5) as executor:
            while serv_start:
                conn, address = server_socket.accept()
                authentification_user(conn)
                print('Nouvelle connexion')
                clients.append(conn)
                executor.submit(handle_client, conn)

    except (ConnectionAbortedError, ConnectionRefusedError, ConnectionResetError, OSError) as e:
        print(f"Erreur lors du lancement du serveur : {e}")

    else:
        server_socket.close()

def handle_client(conn):
    """
    Gère la connexion avec un client.

    :param conn: Objet de connexion socket avec le client
    :type conn: socket.socket
    """
    try:
        global flag, serv_start
        flag = False
        while not flag:
            received_message = conn.recv(1024).decode()
            print(f"Reçu du client : {received_message}")

            if received_message == 'bye':
                conn.close()
                clients.remove(conn)
                flag = True

            elif not received_message:
                conn.close()
                clients.remove(conn)
                flag = True

            elif received_message.startswith("INSCRI/"):
                inscription(conn, received_message)

            elif received_message.startswith("LOGIN/"):
                authentification_user(conn, received_message)

            elif received_message.startswith("MESSAGE/"):
                save_message(conn, received_message)

            elif received_message.startswith("DEMANDE/"):
                channel_acces(conn, received_message)

            else:
                broadcast(received_message, conn)

    except (ConnectionAbortedError, ConnectionResetError) as e:
        print(f"Erreur lors de la gestion du client : {e}")

    finally:
        conn.close()


def broadcast(message, sender_conn):
    """
    Diffuse un message à tous les clients connectés.

    :param message: Message à diffuser
    :type message: str
    :param sender_conn: Connexion socket du client émetteur
    :type sender_conn: socket.socket
    """
    try:
        print("dans le broadcast")
        db = mysql.connector.connect(host=mysql_host, user=mysql_user, password=mysql_password, database=mysql_database)
        cursor = db.cursor()
        info_message = message.split("/")
        if info_message[0] == "MESSAGE":
            channel_name = info_message[1]
            info_messages = info_message[2].split(",")
            content = info_messages[1]
            sender_username = info_messages[0]


            for client_conn in clients:
                if client_conn != sender_conn:
                    try:
                        message_with_channel = f"MESSAGE/{channel_name}/{sender_username},{content}"
                        client_conn.send(message_with_channel.encode())
                    except Exception as e:
                        print(f"Erreur lors de l'envoi au client : {e}")
                        pass
    except Exception as e:
        print(f"Erreur lors du broadcast : {e}")
    finally:
        db.close()




if __name__ == '__main__':
    main()
