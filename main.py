from pila import Pila
from cola import Cola
import carga_datos
import soko
import gamelib
import calculo_pistas

RUTA_NIVELES = "niveles.txt"
RUTA_TECLAS = "teclas.txt"
CARPETA_IMAGENES = "img/"
TAMAÑO_IMAGEN = 64
TAMAÑO_MAX_X = 1330
TAMAÑO_MAX_Y = 700

IMAGENES = {
    "caja":CARPETA_IMAGENES + "box.gif",
    "objetivo":CARPETA_IMAGENES + "goal.gif",
    "piso":CARPETA_IMAGENES + "ground.gif",
    "jugador":CARPETA_IMAGENES + "player.gif",
    "pared":CARPETA_IMAGENES + "wall.gif"
}

def obtener_tamaño(grilla):
    """Recibe como parametro una grilla (sin formatear) y devuelve sus dimensiones como
    si todas filas tuvieran la misma cantidad de elementos."""
    grilla_formateada = formatear_nivel(grilla)
    return soko.dimensiones(grilla_formateada)

def configurar_ventana(juego):
    tamaño_x,tamaño_y = obtener_tamaño(juego["nivel"])
    if tamaño_y * TAMAÑO_IMAGEN > TAMAÑO_MAX_Y or tamaño_x * TAMAÑO_IMAGEN > TAMAÑO_MAX_X:
        juego["num_nivel_actual"] += 1
        juego["condicion_inicio"] = True
    else:
        juego["condicion_inicio"] = False
        gamelib.resize(tamaño_x * TAMAÑO_IMAGEN,tamaño_y * TAMAÑO_IMAGEN)

def formatear_nivel(nivel):
    """Recibe como parametro una grilla, y lo itera para crear una nueva grilla
    formateada. Esta nueva grilla tendrá la misma cantidad de columnas que la fila mas larga.
    A las filas mas cortas se les agregarán '?' para completar la diferencia.
    Ademas, los espacios vacios tambien se reemplazaran con ese simbolo."""
    largo_mayor = 0
    nivel_formateado = []
    for linea in nivel:
        if len(linea)>largo_mayor:
            largo_mayor = len(linea)

    for i_linea,linea in enumerate(nivel):
        linea_a_formatear = linea.copy()
        for i_celda,celda in enumerate(linea_a_formatear):
            if celda == soko.VACIA:
                linea_a_formatear[i_celda] = soko.PISO   
        if len(linea_a_formatear) < largo_mayor:
            diferencia_largo = largo_mayor - len(linea_a_formatear) 
            linea_a_formatear.extend([soko.PISO] * diferencia_largo)
        nivel_formateado.append(linea_a_formatear)
    return nivel_formateado

def dibujar_celda(celda,x,y):
    """Recibe el contenido de una celda y unas coordenadas x e y.
    En base al contenido de la celda, insertará las imagenes correspondientes en el juego, en las
    coordenadas indicadas y en el orden correcto.
    """
    contenido_a_dibujar = {
        soko.PISO:[IMAGENES["piso"]],
        soko.PARED:[IMAGENES["piso"],IMAGENES["pared"]],
        soko.JUGADOR:[IMAGENES["piso"],IMAGENES["jugador"]],
        soko.CAJA:[IMAGENES["piso"],IMAGENES["caja"]],
        soko.OBJETIVO:[IMAGENES["piso"],IMAGENES["objetivo"]],
        soko.OBJETIVO_MAS_CAJA:[IMAGENES["piso"],IMAGENES["caja"],IMAGENES["objetivo"]],   
        soko.OBJETIVO_MAS_JUGADOR:[IMAGENES["piso"],IMAGENES["objetivo"],IMAGENES["jugador"]]  
    }
    imagenes = contenido_a_dibujar[celda]
    for imagen in imagenes:    
        gamelib.draw_image(imagen,x,y)

def dibujar_nivel(nivel):
    """Recibe una grilla (sin formatear) y la dibuja."""
    gamelib.draw_begin()
    nivel = formatear_nivel(nivel)
    for y,linea in enumerate(nivel):
        for x,celda in enumerate(linea):
            dibujar_celda(celda,x * TAMAÑO_IMAGEN,y * TAMAÑO_IMAGEN)
    gamelib.draw_end()

def obtener_direccion(tecla,teclas_config):
    """Recibe la tecla presionada y la configuracion de teclas.
    Devuelve la tupla que representa el movimiento en la direccion asociada segun la configuracion."""
    direcciones = {"NORTE":soko.NORTE,"SUR":soko.SUR,"OESTE":soko.OESTE,"ESTE":soko.ESTE}
    direccion = direcciones[teclas_config[tecla]]
    return direccion

def rehacer_deshacer_movimientos(accion,juego):
    if accion == "DESHACER":
        if not juego["estados_deshacer"].esta_vacia():
            juego["estados_rehacer"].apilar(juego["nivel"])
            juego["nivel"] = juego["estados_deshacer"].desapilar()
    else:
        if not juego["estados_rehacer"].esta_vacia():
            juego["estados_deshacer"].apilar(juego["nivel"])
            juego["nivel"] = juego["estados_rehacer"].desapilar()   

def iniciar_nivel(juego):
    if not juego["num_nivel_actual"] in juego["niveles"]:
        gamelib.say("\n¡Has finalizado todos los niveles, felicidades!")
        juego["condicion_juego_terminado"] = True
        return
    if not juego["condicion_reinicio"]:
        gamelib.say(f"\n¡Comienza el nivel {juego['num_nivel_actual']}!\n")
        
    juego["nivel"] = soko.crear_grilla(juego["niveles"][juego["num_nivel_actual"]])
    #Configuro el tamaño de la ventana segun el nivel. Si la ventana no entra
    #en mi pantalla, paso al siguiente nivel, poniendo condicion de inicio como True.
    configurar_ventana(juego)
    if juego["condicion_inicio"]:
        msg = f"El nivel {juego['num_nivel_actual']-1} es muy grande y no entra en la pantalla,"
        msg += " se pasará automáticamente al siguiente nivel."
        gamelib.say(msg)
        return
    juego["condicion_reinicio"] = False
    juego["condicion_pistas"] = False
    juego["pistas"] = Cola()
    juego["estados_rehacer"] = Pila()
    juego["estados_deshacer"] = Pila()

def nivel_terminado(juego):
    gamelib.say(f"¡Felicidades has terminado el nivel {juego['num_nivel_actual']}!")
    juego["condicion_inicio"] = True
    juego["num_nivel_actual"] += 1

def acciones_especiales(accion,juego):
    if accion == "REINICIAR":
        juego["condicion_reinicio"] = True
    elif accion in ["DESHACER","REHACER"]:
        rehacer_deshacer_movimientos(accion,juego)
        calculo_pistas.comprobar_estado_pistas((-2,-2),juego)
    elif accion == "PISTA":
        calculo_pistas.comprobar_pistas(juego)
    else:
        pass

def realizar_jugada(juego,tecla_presionada):
    juego["estados_rehacer"] = Pila()
    juego["estados_deshacer"].apilar(juego["nivel"])
    direccion = obtener_direccion(tecla_presionada,juego["teclas_config"])
    calculo_pistas.comprobar_estado_pistas(direccion,juego)
    juego["nivel"] = soko.mover(juego["nivel"],direccion)

def main():
    try:
        teclas = carga_datos.importar_teclas(RUTA_TECLAS)
        niveles = carga_datos.leer_niveles(RUTA_NIVELES)
    except Exception as e:
        gamelib.say(e)
        return
    juego = {"num_nivel_actual":1,"condicion_inicio":True,"condicion_reinicio":False,"nivel":[],
    "estados_deshacer":Pila(),"estados_rehacer":Pila(),
    "pistas_disponibles":False,"pistas":Cola(),"condicion_pistas":False,
    "teclas_config":teclas,"niveles":niveles,"condicion_juego_terminado": False}

    while gamelib.is_alive():
        if juego["condicion_inicio"] or juego["condicion_reinicio"]:
            if juego["condicion_juego_terminado"]:
                return
            iniciar_nivel(juego)
            continue

        if soko.juego_ganado(juego["nivel"]):
            nivel_terminado(juego)
            continue

        dibujar_nivel(juego["nivel"])

        ev = gamelib.wait(gamelib.EventType.KeyPress)
        if not ev:
            return
        tecla_presionada = ev.key
        accion = juego["teclas_config"].get(tecla_presionada,"")
        if accion == "SALIR":
            gamelib.say("Has salido del juego correctamente.")
            return
        if accion in ["REINICIAR","DESHACER","REHACER","PISTA",""]:
            acciones_especiales(accion,juego)
            continue
        realizar_jugada(juego,tecla_presionada)

gamelib.init(main)

