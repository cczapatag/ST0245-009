### Este programa retorna un descenso de números desde los últimos dos números de un documento

def regresion_identidad(DI):
    last = int(DI[len(DI)-2:])
    string = str(last)
    if last < 2:  # Caso base.
        return string
    else:
        string = string + " " + regresion_identidad("0"+str(last-1))
        return string
        
DI = str(input("Ingrese su número de documento: "))
print(regresion_identidad(DI))