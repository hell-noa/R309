flag = False

while flag == False:
    arg = input("nom du fichier : ")
    try:
        fichier = open(arg,'r')


    except FileNotFoundError:
        print("le fichier n'a pas été trouvé")
            
    except IOError:
        print("probleme input output")
            
    except FileExistsError:
        print("le fichier existe deja")
            
    except PermissionError:
        print("permission non suffisante")
          
    else:
        print(fichier.read())
        fichier.close()
        flag= True
 
    finally:
        print("fin du programme" )

