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

def configurar_ventana(d):
    tamaño_x,tamaño_y = obtener_tamaño(d["nivel"])
    if tamaño_y * TAMAÑO_IMAGEN > TAMAÑO_MAX_Y or tamaño_x * TAMAÑO_IMAGEN > TAMAÑO_MAX_X:
        d["num_nivel_actual"] += 1
        d["condicion_inicio"] = True
    else:
        d["condicion_inicio"] = False
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

def rehacer_deshacer_movimientos(accion,d):
    if accion == "DESHACER":
        if not d["estados_deshacer"].esta_vacia():
            d["estados_rehacer"].apilar(d["nivel"])
            d["nivel"] = d["estados_deshacer"].desapilar()
    else:
        if not d["estados_rehacer"].esta_vacia():
            d["estados_deshacer"].apilar(d["nivel"])
            d["nivel"] = d["estados_rehacer"].desapilar()   

def iniciar_nivel(d):
    if not d["num_nivel_actual"] in d["niveles"]:
        gamelib.say("\n¡Has finalizado todos los niveles, felicidades!")
        d["condicion_juego_terminado"] = True
        return
    if not d["condicion_reinicio"]:
        gamelib.say(f"\n¡Comienza el nivel {d['num_nivel_actual']}!\n")
        
    d["nivel"] = soko.crear_grilla(d["niveles"][d["num_nivel_actual"]])
    #Configuro el tamaño de la ventana segun el nivel. Si la ventana no entra
    #en mi pantalla, paso al siguiente nivel, poniendo condicion de inicio como True.
    configurar_ventana(d)
    if d["condicion_inicio"]:
        msg = f"El nivel {d['num_nivel_actual']-1} es muy grande y no entra en la pantalla,"
        msg += " se pasará automáticamente al siguiente nivel."
        gamelib.say(msg)
        return
    d["condicion_reinicio"] = False
    d["condicion_pistas"] = False
    d["pistas"] = Cola()
    d["estados_rehacer"] = Pila()
    d["estados_deshacer"] = Pila()

def nivel_terminado(d):
    gamelib.say(f"¡Felicidades has terminado el nivel {d['num_nivel_actual']}!")
    d["condicion_inicio"] = True
    d["num_nivel_actual"] += 1

def acciones_especiales(accion,d):
    if accion == "REINICIAR":
        d["condicion_reinicio"] = True
    elif accion in ["DESHACER","REHACER"]:
        rehacer_deshacer_movimientos(accion,d)
        calculo_pistas.comprobar_estado_pistas((-2,-2),d)
    elif accion == "PISTA":
        calculo_pistas.comprobar_pistas(d)
    else:
        pass

def realizar_jugada(d,tecla_presionada):
    d["estados_rehacer"] = Pila()
    d["estados_deshacer"].apilar(d["nivel"])
    direccion = obtener_direccion(tecla_presionada,d["teclas_config"])
    calculo_pistas.comprobar_estado_pistas(direccion,d)
    d["nivel"] = soko.mover(d["nivel"],direccion)

def main():
    try:
        teclas = carga_datos.importar_teclas(RUTA_TECLAS)
        niveles = carga_datos.leer_niveles(RUTA_NIVELES)
    except Exception as e:
        gamelib.say(e)
        return
    d = {"num_nivel_actual":1,"condicion_inicio":True,"condicion_reinicio":False,"nivel":[],
    "estados_deshacer":Pila(),"estados_rehacer":Pila(),
    "pistas_disponibles":False,"pistas":Cola(),"condicion_pistas":False,
    "teclas_config":teclas,"niveles":niveles,"condicion_juego_terminado": False}

    while gamelib.is_alive():
        if d["condicion_inicio"] or d["condicion_reinicio"]:
            if d["condicion_juego_terminado"]:
                return
            iniciar_nivel(d)
            continue

        if soko.juego_ganado(d["nivel"]):
            nivel_terminado(d)
            continue

        dibujar_nivel(d["nivel"])

        ev = gamelib.wait(gamelib.EventType.KeyPress)
        if not ev:
            return
        tecla_presionada = ev.key
        accion = d["teclas_config"].get(tecla_presionada,"")
        if accion == "SALIR":
            gamelib.say("Has salido del juego correctamente.")
            return
        if accion in ["REINICIAR","DESHACER","REHACER","PISTA",""]:
            acciones_especiales(accion,d)
            continue
        realizar_jugada(d,tecla_presionada)

gamelib.init(main)

