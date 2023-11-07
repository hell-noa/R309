import sys

def divEntier(x: int, y: int) -> int:
    try:
        if x < 0 or y<0:
            raise ValueError
        elif x < y:
            return 0
        else:
            x = x - y
        return divEntier(x, y) + 1
        
    except ValueError:
        return (print("entrer un int positif"), main())

    



#ce code permet de faire une division euclidienne
#essaie avec 20 et 5 resultat 4

def main():
    try:
        x = int(input("x = "))
        y = int(input("y = "))
        if y == 0:
            raise ZeroDivisionError
        
    except ValueError:
        return (print("entrer un int"), main())
    
    except ZeroDivisionError:
        return (print("y ne doit etre egale a 0"),main())

    else:
        print(divEntier(x,y))


if __name__ == '__main__':
    main()
