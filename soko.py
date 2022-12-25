VACIA = " "
PARED = "#"
CAJA = "$"
JUGADOR = "@"
OBJETIVO = "."
OBJETIVO_MAS_CAJA = "*"
OBJETIVO_MAS_JUGADOR = "+"
PISO = "?"

OESTE = (-1, 0)    
ESTE = (1, 0)         
NORTE = (0, -1)    
SUR = (0, 1)     

def crear_grilla(desc):
    '''Crea una grilla a partir de la descripción del estado inicial.

    La descripción es una lista de cadenas, cada cadena representa una
    fila y cada caracter una celda. Los caracteres pueden ser los siguientes:

    Caracter  Contenido de la celda
    --------  ---------------------
           #  Pared
           $  Caja
           @  Jugador
           .  Objetivo
           *  Objetivo + Caja
           +  Objetivo + Jugador

    Ejemplo:

    >>> crear_grilla([
        '#####',
        '#.$ #',
        '#@  #',
        '#####',
    ])
    '''
    grilla = []

    for i in range(len(desc)):
        fila = []
        for j in range(len(desc[i])):
            fila.append(desc[i][j])
        grilla.append(fila)

    return grilla

def dimensiones(grilla):
    '''Devuelve una tupla con la cantidad de columnas y filas de la grilla.'''
    filas = len(grilla)
    columnas = len(grilla[0])
    return columnas, filas

def hay_vacio(grilla, c, f):
    '''Devuelve True si hay vacio en la columna y fila (c, f).'''
    return grilla[f][c] == VACIA

def hay_pared(grilla, c, f):
    '''Devuelve True si hay una pared en la columna y fila (c, f).'''
    return grilla[f][c] == PARED

def hay_objetivo(grilla, c, f):
    '''Devuelve True si hay un objetivo en la columna y fila (c, f).'''
    return grilla[f][c] in [OBJETIVO, OBJETIVO_MAS_CAJA, OBJETIVO_MAS_JUGADOR]

def hay_caja(grilla, c, f):
    '''Devuelve True si hay una caja en la columna y fila (c, f).'''
    return grilla[f][c] in [CAJA, OBJETIVO_MAS_CAJA]

def hay_jugador(grilla, c, f):
    '''Devuelve True si el jugador está en la columna y fila (c, f).'''
    return grilla[f][c] in [JUGADOR, OBJETIVO_MAS_JUGADOR]

def juego_ganado(grilla):
    '''Devuelve True si el juego está ganado.'''
    for i in range(len(grilla)):
        for j in range(len(grilla[i])):
            if grilla[i][j] in [OBJETIVO, OBJETIVO_MAS_JUGADOR]:
                return False
    return True

def mover(grilla, direccion):
    '''Mueve el jugador en la dirección indicada.

    La dirección es una tupla con el movimiento horizontal y vertical. Dado que
    no se permite el movimiento diagonal, la dirección puede ser una de cuatro
    posibilidades:

    direccion  significado
    ---------  -----------
    (-1, 0)    Oeste
    (1, 0)     Este
    (0, -1)    Norte
    (0, 1)     Sur

    La función debe devolver una grilla representando el estado siguiente al
    movimiento efectuado. La grilla recibida NO se modifica; es decir, en caso
    de que el movimiento sea válido, la función devuelve una nueva grilla.
    '''
    grilla_copia = copiar_grilla(grilla)

    if not direccion in [OESTE, ESTE, NORTE, SUR]:
        return grilla_copia

    mov_x, mov_y = direccion
    x_ini, y_ini = posicion_jugador(grilla)
    x_fin, y_fin = (x_ini + mov_x, y_ini + mov_y)
    
    if hay_pared(grilla_copia, x_fin, y_fin):
        #El jugador se choca contra la pared, devuelvo una copia de la grilla original sin cambios.
        return grilla_copia

    elif hay_caja(grilla_copia, x_fin, y_fin):
        #El contenido de la celda vecina es una caja o un objetivo + caja. 
        #Evaluo el contenido de la celda adyacente a esta. 
        x_ady, y_ady = (x_fin + mov_x, y_fin + mov_y)

        if hay_caja(grilla_copia, x_ady, y_ady) or hay_pared(grilla_copia, x_ady, y_ady):
            #La grilla no se modifica
            return grilla_copia

        if hay_vacio(grilla_copia, x_ady, y_ady) or hay_objetivo(grilla_copia, x_ady, y_ady):
            modificar_celda_inicial(grilla_copia, x_ini, y_ini)  
            modificar_celda_adyacente_y_vecina(grilla_copia, x_fin, y_fin, x_ady, y_ady)

    else:
        #la celda vecina esta vacia o es un objetivo.  
        if hay_vacio(grilla_copia, x_fin, y_fin):
            grilla_copia[y_fin][x_fin] = JUGADOR
        else:
            grilla_copia[y_fin][x_fin] = OBJETIVO_MAS_JUGADOR
        modificar_celda_inicial(grilla_copia, x_ini, y_ini) 
        
    return grilla_copia

def copiar_grilla(grilla):
    """
    Recibe por parametro una grilla y devuelve una copia de la misma.
    """
    grilla_copia = []

    for fila in grilla:
        fila_copia = fila.copy()
        grilla_copia.append(fila_copia)

    return grilla_copia

def posicion_jugador(grilla):
    """
    Recibe por parametro una grilla y devuelve una tupla con la posicion del jugador en la grilla.
    """
    for i in range(len(grilla)):
        for j in range(len(grilla[i])):
            #Evaluo si la posicion es jugador u objetivo + jugador
            if grilla[i][j] in [JUGADOR, OBJETIVO_MAS_JUGADOR]:
                return (j,i)

def modificar_celda_inicial(grilla, x_ini, y_ini):
    """
    Recibe por parametro una grilla, las coordenadas de la posicion inicial del jugador y muta en la 
    grilla el valor de dicha posicion en funcion de su valor inicial. 
    """
    celda_inicial = grilla[y_ini][x_ini]
    if celda_inicial == JUGADOR:
        grilla[y_ini][x_ini] = VACIA
    else:
        grilla[y_ini][x_ini] = OBJETIVO  

def modificar_celda_adyacente_y_vecina(grilla, x_fin, y_fin, x_ady, y_ady):
    """
    Recibe por parametro una grilla, las coordenadas de la posicion final del jugador  y las coordenadas
    de la posicion adyacente a esta en la misma dirección.
    Muta en la grilla la posicion de la celda vecina y la celda adyacente a esta en funcion de sus valores 
    iniciales, considerando previamente que en la celda adyacente y en la celda vecina el movimiento es valido.
    """
    if hay_vacio(grilla, x_ady, y_ady):
        grilla[y_ady][x_ady] = CAJA
    else:
        grilla[y_ady][x_ady] = OBJETIVO_MAS_CAJA

    if hay_objetivo(grilla, x_fin, y_fin): 
        grilla[y_fin][x_fin] = OBJETIVO_MAS_JUGADOR
    else:
        grilla[y_fin][x_fin] = JUGADOR


