import socket
import threading
from concurrent.futures import ThreadPoolExecutor
import mysql.connector
import datetime, time

mysql_host = "127.0.0.1"
mysql_user = "root"
mysql_password = "P@ssw0rd"
mysql_database = "sae309"




def authentification_serveur(conn):
    print(9)
    try:
        print(10)
        db = mysql.connector.connect(host=mysql_host, user=mysql_user, password=mysql_password, database=mysql_database)
        cursor = db.cursor()
        cursor.execute('SELECT * FROM serveur')
        serveur_info = cursor.fetchone()
        print(11)
        

        if serveur_info is None:
            print('La table est vide veuillez remplir les informations demandées')
            new_log = input('Nouvel indentifiant pour le serveur : ')
            new_mdp = input('Nouveau mot de passe pour le serveur : ')

            cursor.execute("INSERT INTO serveur (login , mdp) VALUES (%s, %s)", (new_log, new_mdp))
            db.commit()
            print("Informations du serveur ajoutées avec succès.")
            conn.send("Informations du serveur ajoutées avec succès.".encode())
            return True


        else:
            log = input('identifiant admin : ')
            mdp = input('identifiant admin : ')
            if log == serveur_info[1] and mdp == serveur_info[2]:
                print(12)
                conn.send('ok'.encode())
                return True



    except Exception as e:
        print(f"Erreur lors de l'authentification du serveur : {e}")
        conn.send("ERROR".encode())
        return False

    finally:
        db.close()
        

def authentification_user(conn):
    try:
        db = mysql.connector.connect(host=mysql_host, user=mysql_user, password=mysql_password, database=mysql_database)
        cursor = db.cursor()
        query='SELECT * FROM user where pseudo = %s and mdp = %s'
        
        message = conn.recv(1024).decode()
        info_user = message.split("/")
        if info_user[0] == "LOGIN":
            identifiant = info_user[1].split(',')
            cursor.execute(query,(identifiant[0] , identifiant[1]))
            resultat = cursor.fetchone()
            
            if resultat is None:
                   print('connexion refusé')
                   
            elif resultat:
               print('connexion accepté')
               message = 'ACCEPT' 
               conn.send(message.encode())
               
        
            else:
               print('connexion refusé ')
            
           
           
    except ConnectionAbortedError:
        print('La connexion a été coupée')
    except ConnectionRefusedError:
        print('La connexion a été refusée')
    except ConnectionResetError:
        print('La connexion a été réinitialisée')
    except OSError:
        pass
        
    else:
        pass
    
    finally:
        db.close()
        channel_verif(conn,identifiant[0])
           
           
def inscription(conn, message):
    try:
        print('icicicicici')
        db = mysql.connector.connect(host=mysql_host, user=mysql_user, password=mysql_password, database=mysql_database)
        cursor = db.cursor()
        
        info_user = message
        info_user = info_user.split("/")
        if info_user[0] == "INSCRI":
            print(5768)
            identifiant = info_user[1].split(',')
            new_log = identifiant[0]
            new_mdp = identifiant[1]
            new_alias = identifiant[2]
            
            cursor.execute("SELECT * FROM user WHERE alias = %s", (new_alias,))
            result = cursor.fetchone()
            
            if result :
                message = 'insertion_no'
                conn.send(message.encode())
                print('insertion_no')
                
    
            else:
                cursor.execute("INSERT INTO user (pseudo , mdp, alias) VALUES (%s, %s, %s)", (new_log, new_mdp, new_alias))
                db.commit()
                print('transaction effectué')
                message = 'insertion_ok' 
                conn.send(message.encode())
            
            
            

    except:
        pass
    else:
        pass
    
    finally:
        db.close()
        
        
def channel_verif(conn, pseudo):
    try:
        print('channel veirf')
        print(pseudo)
        db = mysql.connector.connect(host=mysql_host, user=mysql_user, password=mysql_password, database=mysql_database)
        cursor = db.cursor()
        cursor.execute("select channel_verif from user where pseudo = %s",(pseudo,))
        result = cursor.fetchone()
        correspondances = {'1': 'GB', '2': 'GI', '3': 'GM', '4': 'GC', '12': 'GBI', '13': 'GBM', '14': 'GBC', '23': 'GIM', '24': 'GIC', '34': 'GMC', '123': 'GBIM', '124': 'GBIC', '134': 'GBMC','234':'GIMC' ,'1234': 'GBIMC'}

        print(correspondances.get(result[0]))
        
        conn.send(f"ACCES/{correspondances.get(result[0], 'G')}".encode())
        
        
    except Exception as e:
        print(f"Erreur : {e}")

    finally:
        db.close()

    
        
def channel_acces(conn, message):
    try:
        print(1)
        db = mysql.connector.connect(host=mysql_host, user=mysql_user, password=mysql_password, database=mysql_database)
        print(2)
        cursor = db.cursor()
        print(3)
        info_user = message
        print(4)
        info_user = info_user.split("/")
        print(5)
        pseudo = info_user[2]
        print(6)
        cursor.execute("select channel_verif from user where pseudo = %s",(pseudo,))
        print(7)
        current_channel_verif = cursor.fetchone()
        print(current_channel_verif)
        
        if current_channel_verif is not None and current_channel_verif[0] is not None:
            current_channel_verif = int(current_channel_verif[0])
        else:
            current_channel_verif = ""
            
            

        if info_user[0] == "DEMANDE":
            if info_user[1] == "Blabla":
                variable = str(current_channel_verif) + str (1)
                cursor.execute("UPDATE user SET channel_verif = %s WHERE pseudo = %s", (variable, pseudo))
                db.commit()

                
                

            elif info_user[1] == "Informatique":
                verif = input('YES/NO : ')
                if verif.lower() == 'yes':
                    variable = str(current_channel_verif) +str(2)
                    cursor.execute("UPDATE user SET channel_verif = %s WHERE pseudo = %s", (variable, pseudo))
                    db.commit()
                else:
                   pass
                    
                                       
            elif info_user[1] == "Marketing":
                print(11)
                verif = input('YES/NO : ')
                if verif.lower() == 'yes':
                    variable = str(current_channel_verif) +str( 3)
                    print(variable)
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
        pass
    
    else:
        pass

    finally:
        db.close()
        tri(conn,pseudo)

        
                    
                    
                    
def tri(conn, pseudo):
    try:
        print('TRI')
        db = mysql.connector.connect(host=mysql_host, user=mysql_user, password=mysql_password, database=mysql_database)
        print('TRI2')
        cursor = db.cursor()
        cursor.execute("SELECT channel_verif FROM user WHERE pseudo = %s", (pseudo,))
        print('TRI3')
        resultat = cursor.fetchone()
        print(resultat)
        if resultat:
            # Accéder directement à l'élément de la tuple
            verif = ''.join(sorted(resultat[0]))
            print(verif)
            cursor.execute("UPDATE user SET channel_verif = %s WHERE pseudo = %s", (verif, pseudo))
            print('sardine')
            db.commit()
            db.close()


    except:
        pass

    finally:
        channel_verif(conn, pseudo)
        
        
        

        
        
        
def save_message(conn, message):
    try:
        print(1)
        db = mysql.connector.connect(host=mysql_host, user=mysql_user, password=mysql_password, database=mysql_database)
        cursor = db.cursor()
        info_user = message
        info_user = info_user.split("/")

        
        if info_user[0] == "MESSAGE":
            print(2)
            information = info_user[2].split(',')
            print(3)
            user = information[0]
            print(4)
            print (user)
            contenu = information[1]
            print (contenu)
            print(5)
            channel = info_user[1]
            print(6)
            
            cursor.execute("SELECT id_user from user WHERE pseudo = %s" ,(user,))
            user = cursor.fetchone()[0]
            print ( user)
            print('okok')
            
            cursor.execute("SELECT channel_id from channel WHERE nom_channel = %s" ,(channel,))
            channel = cursor.fetchone()[0]
            print(channel)
            print('okokok')
            
            cursor.execute("INSERT INTO message (contenu , id_user, channel_id) VALUES (%s, %s, %s)", (contenu, user, channel))

            db.commit()
            print('okokokok')
            
            broadcast(message, conn)
            
    except:
        pass
    else:
        pass
    finally:
        db.close()
        
    


    


def main():
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

    except ConnectionAbortedError:
        print('La connexion a été coupée')
    except ConnectionRefusedError:
        print('La connexion a été refusée')
    except ConnectionResetError:
        print('La connexion a été réinitialisée')
    except OSError:
        pass
    else:
        server_socket.close()


def handle_client(conn):
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
                print(4)
                conn.close()
                clients.remove(conn)  
                flag = True
                
            elif received_message.startswith("INSCRI/"):
                print (received_message)
                inscription(conn, received_message)
            
            elif received_message.startswith("LOGIN/"):
                print (received_message)
                authentification_user(conn)
                
            elif received_message.startswith("MESSAGE/"):
                print(99999)
                save_message(conn, received_message)
                
            elif received_message.startswith("DEMANDE/"):
                print('ouiouioui')
                channel_acces(conn, received_message)
                    

                



            else:
                broadcast(received_message, conn)

    except ConnectionAbortedError:
        print('La connexion a été coupée')
    except ConnectionResetError:
        print('La connexion a été réinitialisée')
    finally:
        conn.close()


def broadcast(message, sender_conn):
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
            print(content)
            print(sender_username)

            for client_conn in clients:
                if client_conn != sender_conn:
                    try:
                        # Modifiez l'en-tête du message pour inclure le nom du canal
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
