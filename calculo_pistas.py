from pila import Pila
from cola import Cola
import soko
import gamelib

def buscar_solucion(estado_inicial):
    visitados = set()
    return backtrack(estado_inicial,visitados)[1]

def backtrack(estado,visitados):
    visitados.add(convertir_nivel_a_cadena(estado))
    if soko.juego_ganado(estado):
        #Encontramos la solucion
        return True,[]
    direcciones = [soko.NORTE,soko.SUR,soko.ESTE,soko.OESTE]
    for direccion in direcciones:
        nuevo_estado = soko.mover(estado,direccion)
        if convertir_nivel_a_cadena(nuevo_estado) in visitados:
            continue
        sol_encontrada,acciones = backtrack(nuevo_estado,visitados)
    
        if sol_encontrada:
            return True, acciones + [direccion]
    return False, ""

def convertir_nivel_a_cadena(nivel):
    cadena = ""
    for linea in nivel:
        cadena += "".join(linea) + "_"
    return cadena

def obtener_pistas(estado):
    pistas = buscar_solucion(estado)
    cola_pistas = Cola()
    for pista in pistas[::-1]: #invierto la lista para que esté en el orden correcto para que funcione.
        cola_pistas.encolar(pista)
    
    return cola_pistas

def comprobar_pistas(d):
    if not d["condicion_pistas"]:
        d["pistas"] = obtener_pistas(d["nivel"])
        d["condicion_pistas"] = True
        gamelib.say("Hay pistas disponibles")
    else:
        d["estados_rehacer"] = Pila()
        d["estados_deshacer"].apilar(d["nivel"])
        d["pista"] = d["pistas"].desencolar()
        d["nivel"] = soko.mover(d["nivel"],d["pista"])

def comprobar_estado_pistas(direccion,d):
    if d["pistas"].esta_vacia():
        d["condicion_pistas"] = False
    elif direccion != d["pistas"].frente:
        gamelib.say("Se borraron las pistas")
        d["condicion_pistas"] = False
        d["pistas"] = Cola()
    else:
        d["condicion_pistas"] = True