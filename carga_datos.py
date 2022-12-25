def is_text(str_input,simbolos=[]):
    """Recibe una cadena y devuelve True o False si es texto alfanumerico o no.
    Recibe como parametro opcional una lista con simbolos que también serán considerados
    como texto."""
    for simbolo in simbolos:
        str_input = str_input.replace(simbolo,"")
    return str_input.isalnum()

def leer_niveles(ruta_archivo):
    """Recibe una ruta relativa como parámetro para leer un txt, obtener los niveles del juego 
    y devolverlos en un diccionario con el formato <numero_nivel>:<descripcion_nivel>."""
    try:
        with open(ruta_archivo) as f:
            niveles = {}
            contador = 0
            for linea in f:
                linea = linea.rstrip()
                if "Level" in linea:
                    nivel = int(linea.split()[1])
                    niveles[nivel] = []
                    continue
                elif linea == "":
                    continue
                elif is_text(linea,[" ","(",")","'"]):
                    #la linea contiene el nombre del nivel, la salteo también.
                    continue
                niveles[nivel].append(linea)
                contador += 1
        return niveles
    except FileNotFoundError:
        msg = "Ha ocurrido un error al momento de acceder a los niveles del juego.\n"
        msg += "\nRevisar que el juego haya sido correctamente instalado, y que el archivo niveles.txt "
        msg += "esté en la misma carpeta que el juego."
        raise FileNotFoundError(msg)

def importar_teclas(ruta_teclas):
    """Recibe como parametro una ruta relativa para leer la configuracion de teclas del juego
     y devuelve un diccionario con el formato <tecla>:<accion>"""
    try:
        with open(ruta_teclas) as f:
            teclas = {}
            for linea in f:
                linea = linea.rstrip()
                if linea == "":
                    continue
                tecla,accion = linea.split("=")
                tecla,accion = tecla.strip(),accion.strip()
                teclas[tecla] = accion
        return teclas
    except FileNotFoundError:
        msg = "Ha ocurrido un error al momento de acceder a la configuracion de teclas del juego.\n"
        msg += "Revisar que el juego haya sido correctamente instalado, y que el archivo teclas.txt "
        msg += "esté en la misma carpeta que el juego."
        raise FileNotFoundError(msg)