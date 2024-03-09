"""
Práctica de la asignatura paradigmas de programacion basada en u juego estilo tetris con la libreria wxPYTHON

Está práctica esta hecha con usando wx panel para representar el tablero.

Se ha considerado que los colores según la letra :
a o A o carácter no identificado: verde oscuro, b o B: azul, c o C: rojo

Se usado la clase tablero, fila y bloque de la práctica anterior (con alguna pequeña modificación y revisión de
comentarios) y se han modificado partes del código de la práctica interior para insertarlo en está en la clase
MyFrame

Para realizar jugadas hay que desplazar los bloques al lado que se quiera o pulsar una posicion sin bloques para dejar caer
la fila de arriba
"""

import wx

class MyFrame(wx.Frame):

    # Se inicializa la interfaz gráfica
    def __init__(self, *args, **kwds):
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((650, 450))
        self.SetTitle("Deslizator")
        sizer_0 = wx.BoxSizer(wx.VERTICAL)

        sizer_arriba = wx.BoxSizer(wx.HORIZONTAL)
        sizer_0.Add(sizer_arriba, 1, wx.ALL | wx.EXPAND, 5 )

        sizer_izq = wx.BoxSizer(wx.VERTICAL)
        sizer_arriba.Add(sizer_izq, 1, wx.ALL | wx.EXPAND, 5)

        sizer_fich = wx.BoxSizer(wx.HORIZONTAL)
        sizer_izq.Add(sizer_fich, 0, 0, 0)

        self.inic_partida = wx.Button(self, wx.ID_ANY, "Nueva partida")
        sizer_izq.Add(self.inic_partida, 0, wx.ALL | wx.EXPAND, 5)

        sizer_velocidad = wx.BoxSizer(wx.HORIZONTAL)
        sizer_izq.Add(sizer_velocidad, 0, 0, 0)

        label_4 = wx.StaticText(self, wx.ID_ANY, u"Velocidad animación: ")
        sizer_velocidad.Add(label_4, 0, wx.ALL, 5)

        self.velocidad = wx.SpinCtrl(self, wx.ID_ANY, "50", min=1, max=100)
        sizer_velocidad.Add(self.velocidad, 0, 0, 0)

        sizer_n_filas = wx.BoxSizer(wx.HORIZONTAL)
        sizer_izq.Add(sizer_n_filas, 0, 0, 0)

        label_3 = wx.StaticText(self, wx.ID_ANY, u"Nº filas: ")
        sizer_n_filas.Add(label_3, 0, wx.ALL, 5)

        self.ins_n_filas = wx.SpinCtrl(self, wx.ID_ANY, "12", min=2, max=23)
        sizer_n_filas.Add(self.ins_n_filas, 0, 0, 0)

        label_2 = wx.StaticText(self, wx.ID_ANY, "Lista de jugadas:")
        sizer_izq.Add(label_2, 0, 0, 0)

        self.lista_jugadas = wx.ListBox(self, wx.ID_ANY, choices=[], style=wx.LB_MULTIPLE)
        sizer_izq.Add(self.lista_jugadas, 1, wx.EXPAND, 0)

        self.puntuacion = wx.StaticText(self, wx.ID_ANY, "Puntuación: 0")
        self.puntuacion.SetForegroundColour(wx.Colour(255, 0, 0))
        self.puntuacion.SetFont(wx.Font(15, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, "Arial"))
        sizer_izq.Add(self.puntuacion, 0, 0, 0)

        sizer_der = wx.BoxSizer(wx.HORIZONTAL)
        sizer_arriba.Add(sizer_der, 3, wx.ALL | wx.EXPAND, 5)

        self.sizer_letras = wx.BoxSizer(wx.VERTICAL)
        sizer_der.Add(self.sizer_letras, 0, wx.BOTTOM | wx.TOP | wx.EXPAND, 10)

        self.n_filas = self.ins_n_filas.GetValue()
        self.se_puede_empezar = False

        self.pintar_letras()

        self.sizer_tablero_y_num = wx.BoxSizer(wx.VERTICAL)
        sizer_der.Add(self.sizer_tablero_y_num, 3, wx.ALL | wx.EXPAND, 5)
        self.tablero_grafico = wx.GridBagSizer(2, 0)
        self.sizer_tablero_y_num.Add(self.tablero_grafico, 10, wx.EXPAND, 1)

        self.anadir_col = True #Sirve para no añadir y eliminar columnas growbles de nuevo al cambiar el n de filas
        self.llenar_tablero_grafico()
        self.anadir_col = False

        sizer_numeros = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_tablero_y_num.Add(sizer_numeros, 0, wx.LEFT | wx.EXPAND, 20)
        for num in range(10):
            numero = wx.StaticText(self, wx.ID_ANY, str(num))
            numero.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
            sizer_numeros.Add(numero, 1, wx.ALIGN_CENTER_VERTICAL , 0)

        self.estado = wx.StaticText(self, wx.ID_ANY, "Introduzca un fichero y un nº de filas para empezar")
        self.estado.SetFont(wx.Font(15, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, "Arial"))
        sizer_0.Add(self.estado, 0, 0, 0)

        self.leer_fich()

        self.SetSizer(sizer_0)

        self.Layout()
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.pintar_siguiente_estado, self.timer)
        self.Bind(wx.EVT_BUTTON, self.on_click_inic_partida, self.inic_partida)
        self.Bind(wx.EVT_SPINCTRL, self.on_spin_filas, self.ins_n_filas)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_spin_filas, self.ins_n_filas)
        self.Bind(wx.EVT_SPINCTRL, self.on_spin_velocidad, self.velocidad)
        self.Bind(wx.EVT_TEXT, self.on_spin_velocidad, self.velocidad)
        self.esperando_jugada = False
        self.haciendo_jugada = False
        self.tiempo_pintar_sig_estado = 1800 // self.n_filas #Cuántas más filas más rápido y cuántas menos más lento

    def on_spin_velocidad(self, event):
        self.variacion_tiempo = 50/self.velocidad.Value
        self.tiempo_pintar_sig_estado = int((1800 // self.n_filas) * self.variacion_tiempo)
        return None

    def leer_fich(self):
        fichero = "lista_filas_a_caer.txt" 
        try:
            f = open(fichero, "r")
            lista_de_lineas = []
            cant_lineas = 0
            for linea in f.readlines():
                lista_de_lineas.append(linea)
                cant_lineas += 1
            f.close
            self.cant_lineas = cant_lineas
            self.lista_de_lineas = lista_de_lineas
            self.linea_a_leer = 0 
            self.estado.SetLabel("Puede iniciar la partida.")
            self.se_puede_empezar = True
        except:
            self.estado.SetLabel("Error asegurese de que tiene el archivo f.txt en la misma carpeta que el juego.")
        return None

    #Inicia el juego reiniciando la puntación a 0, ponuendo arriba la primer fila del bloque...
    def on_click_inic_partida(self, event): 
        self.iniciar_partida()
    
    def iniciar_partida(self):
        if self.se_puede_empezar == True:
            self.puntuacion.SetLabel("Puntuación: 0")
            self.lista_jugadas.Clear()
            self.vaciar_tablero_grafico()
            self.estado.SetLabel("Partida iniciada, esperando jugada.")
            self.tablero = Tablero(self.n_filas, self.lista_de_lineas, self.linea_a_leer, self.cant_lineas)
            self.tablero.leer_linea()
            self.pintar_tablero()
            self.esperando_jugada = True
        else:
            self.estado.SetLabel("No se puede empezar no se ha leido el fichero.")
        return None

    # Pinta en el tablero con la animacion los moviemtos que suceden a la jugada
    def pintar_jugada(self):
        self.haciendo_jugada = True
        if self.tiempo_pintar_sig_estado > 1000: 
            self.tiempo_pintar_sig_estado = 1000
        self.falta_pintar_caida_por_bloques = False
        self.timer.Start(self.tiempo_pintar_sig_estado)

    # Mueve las fichas hacia abajo y comprueba en cada iteración si se puede eliminar una fila
    def pintar_siguiente_estado(self, event):
        self.fin_caida = False
        while self.fila != -1:  #Si la fila es -1 ya han caido todas
            if self.fila != self.n_filas - 1 and self.tablero.filas[self.fila].bloques != []:
                # No tiene sentido intentar hacer que caiga la ultima fila o una vacia
                while self.tablero.filas[self.fila + 1].bloques == []: 
                    self.tablero.caida_libre(self.fila)
                    self.pintar_tablero()
                    self.fila += 1
                    if self.fila == self.n_filas - 1:
                        self.fin_caida = True  #¡
                        break
                    return None
                if self.fin_caida == False:
                    self.tablero.caida_por_bloques(self.fila)
                    # Si la siguiente fila tiene bloques miro a ver si algún bloque de está puede caer
                    self.falta_pintar_caida_por_bloques = True
                    # No lo pinto aún espera a ver si puede caer alguna fila de arriba
            # Intento hacer que caiga la siguiente fila
            self.fila -= 1  
        if self.falta_pintar_caida_por_bloques == True:
                self.pintar_tablero()
                self.falta_pintar_caida_por_bloques = False
                return None
        se_eliminaron_filas, fila_de_la_ultima_eliminada = self.tablero.intentar_eliminar_filas()
        if se_eliminaron_filas:
            if fila_de_la_ultima_eliminada == -1:
                self.estado.SetLabel("Eliminaste una fila con todos los bloques del mismo color!!")
            elif fila_de_la_ultima_eliminada == self.n_filas - 1:
                fila_de_la_ultima_eliminada = self.n_filas - 2
            self.fila = fila_de_la_ultima_eliminada
            self.puntuacion.SetLabel("Puntuación: " + str(self.tablero.puntuacion))
            self.pintar_tablero()
            return None
        else:
            self.tablero.leer_linea()
            self.pintar_tablero()
        if self.tablero.game_over == True:
            self.estado.SetLabel("Game over!!!!!!!!!!!")
            self.esperando_jugada = False
        self.timer.Stop()
        self.haciendo_jugada = False
        return None

    def pintar_letras(self):
        self.sizer_letras.Clear(True)
        for fila in range(self.n_filas):
            letra = wx.StaticText(self, wx.ID_ANY, chr(ord("A") + fila))
            letra.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
            self.sizer_letras.Add(letra, 1, wx.ALIGN_CENTER_HORIZONTAL, 0)
        return None

    def pintar_tablero(self):
        self.vaciar_tablero_grafico()
        for fila in range(self.n_filas):
            for bloque in self.tablero.filas[fila].bloques:
                self.pintar_bloque(bloque, fila)
        self.Update()
        return None

    def pintar_bloque(self, bloque, fila):
        if bloque.simbolo == "#":
            #Se pinta el bloque y los separadores
            for col in range(2 * bloque.inic, (2 * (bloque.inic + bloque.longitud)) -1 ):
                self.matriz_paneles[fila][col].SetBackgroundColour((0,100,0))
                self.matriz_paneles[fila][col].Refresh()
        elif bloque.simbolo == "$":
            for col in range(2 * bloque.inic, (2 * (bloque.inic + bloque.longitud)) -1 ):
                self.matriz_paneles[fila][col].SetBackgroundColour(wx.Colour("blue"))
                self.matriz_paneles[fila][col].Refresh()
        else:
            for col in range(2 * bloque.inic, (2 * (bloque.inic + bloque.longitud)) -1 ):
                self.matriz_paneles[fila][col].SetBackgroundColour(wx.Colour("red"))
                self.matriz_paneles[fila][col].Refresh()
        return None

    def llenar_tablero_grafico(self):
        self.matriz_paneles = []
        for fila in range(self.n_filas):
            self.matriz_paneles.append([])
            for col in range(19):
                panel = wx.Panel(self, wx.ID_ANY)
                panel.Bind(wx.EVT_LEFT_DOWN, self.on_click_panel)
                panel.Bind(wx.EVT_LEFT_UP, self.off_click)
                panel.SetBackgroundColour(wx.Colour("white"))
                self.tablero_grafico.Add(panel, (fila, col),(0, 0), wx.EXPAND, 0)
                panel.Refresh()
                self.matriz_paneles[fila].append(panel)
        self.ID_panel0 = self.matriz_paneles[0][0].GetId()

        for fila in range(self.n_filas):
            self.tablero_grafico.AddGrowableRow(fila)  
        if self.anadir_col:
            for col in range(19):
                if col % 2 == 0: 
                    self.tablero_grafico.AddGrowableCol(col)
        return None

    def vaciar_tablero_grafico(self):
        for fila in range(self.n_filas):
            for col in range (19):
                self.matriz_paneles[fila][col].SetBackgroundColour("white")
                self.matriz_paneles[fila][col].Refresh()
        return None

    def eliminar_tablero_grafico(self):
        for fila in range(self.n_filas):
            self.tablero_grafico.RemoveGrowableRow(fila)  
        self.tablero_grafico.Clear(True)
        return None

    def on_click_panel(self, event):
        if self.esperando_jugada == True:
            if self.haciendo_jugada == False:
                self.X = event.GetX()
                pos_panel_pulsado = abs(event.GetId() - self.ID_panel0)
                self.n_letra, self.num_int = self.obtener_primera_parte_jugada(pos_panel_pulsado)
                if self.matriz_paneles[self.n_letra][self.num_int].GetBackgroundColour() == (255, 255, 255, 255):
                    self.estado.SetLabel("Ratón pulsado, sueltelo fuera del tablero para anular la jugada vacia.")
                    self.letra = "-"
                    self.num_char = "-"
                else:
                    self.estado.SetLabel("Suelte el bloque sin moverlo o fuera del tablero para anular la jugada.")
                    self.letra = chr(65 + self.n_letra)
                    self.num_char = str(self.num_int//2)
            else:
                self.estado.SetLabel("Espere a que la jugada acabe para hacer otra.")
        else:
            try:
                if self.tablero.game_over == True:
                    self.estado.SetLabel("EMPIEZE OTRA PARTIDA, ESTA YA HA TERMINADO!!!!")
            except:
                self.estado.SetLabel("No hay una partida empezada.")
        return None

    def obtener_primera_parte_jugada(self, pos_panel_pulsado):
        n_letra = pos_panel_pulsado // 19
        num = pos_panel_pulsado % 19
        return n_letra, num

    def off_click(self, event):
        if self.esperando_jugada == True:
            if self.haciendo_jugada == False:
                if self.num_char == "-":
                    sentido = "-"
                else:
                    pos_panel_soltado = abs(event.GetId() - self.ID_panel0)
                    n_letra, num_int = self.obtener_primera_parte_jugada(pos_panel_soltado)
                    if num_int != self.num_int:
                        if num_int > self.num_int:
                            sentido = ">"
                        else:
                            sentido = "<"
                    else:
                        if event.GetX() > self.X:
                            sentido = ">"
                        elif event.GetX() < self.X:
                            sentido = "<"
                        else:
                            sentido =""
                jugada = self.letra + self.num_char + sentido
                self.realizar_jugada_raton(jugada)
            return None
        else:
            return None

    def realizar_jugada_raton(self, jugada):#Ordeno los bloques segun su inic
        if self.esperando_jugada:
            if self.tablero.game_over == False:
                if self.tablero.validar_jugada_y_realizarla(jugada) == 0:
                    self.lista_jugadas.Insert(jugada, 0)
                    if jugada != "---":
                        self.fila = ord(jugada[0]) - 65
                    else:
                        self.fila = 0
                    self.pintar_tablero()
                    self.pintar_jugada()  # Hace una jugada y la pinta
                else:
                    self.estado.SetLabel(self.tablero.validar_jugada_y_realizarla(jugada))
            else:
                self.estado.SetLabel("La partida ya se ha acabado")
        else:
            self.estado.SetLabel("No hay un juego iniciado, empieza uno.")
        return None

    def on_spin_filas(self, event):
        
        self.esperando_jugada = False
        self.iniciar_partida()
        self.eliminar_tablero_grafico()
        self.n_filas = self.ins_n_filas.Value
        self.pintar_letras()
        self.llenar_tablero_grafico()
        self.esperando_jugada = False
        self.estado.SetLabel("Nº de filas modificado revise si el tamaño de la pantalla es adecuado.")
        self.Layout()
        # Cuántas más filas más rápido y cuántas menos más lento
        self.tiempo_pintar_sig_estado = 1800 // self.n_filas  
        return None


class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True

class Tablero():
    def __init__(self, n_filas, lista_de_lineas, linea_a_leer, cant_lineas):
        self.n_filas = n_filas
        self.lista_de_lineas = lista_de_lineas
        self.linea_a_leer = linea_a_leer
        self.cant_lineas = cant_lineas
        self.filas = []
        for i in range(self.n_filas):
            self.filas.append(Fila())
        self.game_over = False
        self.puntuacion = 0
        return None

    def leer_linea(self):
        if self.filas[0].bloques != []:
            self.game_over = True 
            return None
        else:
            if self.cant_lineas - 1 == self.linea_a_leer:
                self.linea_a_leer = 0
            linea = self.lista_de_lineas[self.linea_a_leer]
            if len(linea) > 11:  #Por si se pone más de 10 cosas en una linea
                linea = linea[0:10]
                print("Asegurese de que el fichero es correcto!!! (hay más de 10 caracteres en esa fila)")
            if ord(linea[len(linea) - 1]) != 10:
                linea += chr(10)  
            self.linea_a_leer += 1
            self.colocar_linea_leida(linea)
            return None

    # Añade la linea leida del fichero al tablero con sus bloques
    def colocar_linea_leida(self, linea):
        pos = 0
        while pos < (len(linea) - 1):
            #No me interesa el salto de linea que está en la última posición: linea[len(linea) - 1]
            if linea[pos] != " ":
                longitud = 0
                pos_inic = pos
                if linea[pos] == "b" or linea[pos] == "B":
                    caracter = linea[pos]
                    while caracter == linea[pos]:
                        if longitud == 0:
                            inic = pos_inic #La posicion inicial es la primera vez que el caracter es b o B
                        longitud += 1  #Si en la siguiente posición el simbolo es el mismo el bloque tiene más longitud
                        if pos == len(linea) - 1:#No interesa la última posición porque es el salto de línea
                            break
                        pos += 1
                    simbolo = "$" #Si ha pasado por este bucle el simbolo del bloque es $
                elif linea[pos] == "c" or linea[pos] == "C":
                    caracter = linea[pos]
                    while caracter == linea[pos]:
                        if longitud == 0:
                            inic = pos_inic #La posicion inicial es la primera vez que el caracter es b o B
                        longitud += 1 #Si en la siguiente posición el simbolo es el mismo el bloque tiene más longitud
                        if pos == len(linea) - 1:#No interesa la última posición porque es el salto de línea
                            break
                        pos += 1
                    simbolo = "%" #Si ha pasado por este bucle el simbolo del bloque es %
                else: #Si lo que se esta leyendo no es una b o B entonces debe ser una a o A y se hara algo parecido a si es b o B
                    caracter = linea[pos]
                    while caracter == linea[pos]:
                        if longitud == 0:
                            inic = pos_inic
                        longitud += 1
                        if pos == len(linea) - 1:
                            break
                        pos += 1
                    simbolo = "#"
                self.filas[0].anadir_bloque(inic, longitud, simbolo)
            else:
                pos += 1
        return None

    # Se informa de sintaxis en la jugada (que sea --- o una letra mayuscula entre A y L, un numero positivo menor que 
    # el numero de filas y un simbolo > o < que indique hacia donde se quiere mover el bloque) y si se pueden realizar
    def validar_jugada_y_realizarla(self, jugada): 
        if len(jugada) == 3:                      
            if jugada == "---":
                return 0
            else:  
                #Paso la fila de letra mayuscula a numero
                fila = (int(ord(jugada[0]) - 65)) 
                if fila < 0 or fila > self.n_filas-1:
                    return "Error de sintaxis en la primera posición, debe ser una fila."
                try:
                    casilla_a_mover = int(jugada[1]) 
                except:                              
                    return "Error de sintaxis en la segunda posición, debe ser un nº."
                casilla = Bloque(casilla_a_mover, 1, "X") 
                #Se crea un bloque de longitud uno que se usa para ver si hay un bloque en esa posicion
                hay_bloque_en_casilla = False 
                pos = 0 
                for bloque in self.filas[fila].bloques:
                    if bloque.comparten_posicion_bloques(casilla) == True:
                        hay_bloque_en_casilla = True
                        break 
                    pos += 1  
                if hay_bloque_en_casilla == False:
                    return "Error, no hay un bloque en esa celda."
                else:
                    if jugada[2] == "<":
                        if pos == 0:
                            if self.filas[fila].bloques[pos].inic == 0:
                                return "Error el bloque está pegado al borde de la izquierda."
                            else: 
                                # Para mover un bloque que sea el primero y que no este pegado al borde izquierdo se le pega a ese borde
                                self.filas[fila].bloques[pos].inic = 0
                                return 0
                        else:
                            # Se mueve el bloque si se puede
                            return self.realizar_jugada_izq(fila, pos)
                    elif jugada[2] == ">": 
                        if len(self.filas[fila].bloques) == pos + 1:
                            if self.filas[fila].bloques[pos].inic + self.filas[fila].bloques[pos].longitud - 1 == 9:
                                return "Error el borde está pegado al borde de la  derecha."
                            else:
                                self.filas[fila].bloques[pos].inic = 10 - self.filas[fila].bloques[pos].longitud
                                return 0
                        else:
                                return self.realizar_jugada_der(fila, pos)
                    else:
                        return "No se ha dectectado movimiento."
        else:
            return "Debes mover el ratón antes de dejar de pulsarlo, para realizar jugadas."

    def realizar_jugada_izq(self, fila, pos):
        # Comprueba que los bloques contiguos no esten pegados
        if ((self.filas[fila].bloques[pos-1].inic + self.filas[fila].bloques[pos-1].longitud) -
            self.filas[fila].bloques[pos].inic)== 0: 
            return "Error, el bloque está pegado a otro por la izquierda."
        else:  
            # Muevo el bloque a la izquierda hasta pegarlo con el anterior
            self.filas[fila].bloques[pos].inic = (self.filas[fila].bloques[pos - 1].inic +
                                                  self.filas[fila].bloques[pos - 1].longitud)
            return 0

    # Lo mismo de arriba, pero con la derecha
    def realizar_jugada_der(self, fila, pos):
        if (self.filas[fila].bloques[pos + 1].inic - (self.filas[fila].bloques[pos].inic +
            self.filas[fila].bloques[pos].longitud)) == 0:
            return "Error, el bloque esta pegado a otro por la derecha."
        else:
            self.filas[fila].bloques[pos].inic = (self.filas[fila].bloques[pos + 1].inic -
                                                  self.filas[fila].bloques[pos].longitud)
            return 0

    def caida(self, fila):
        while self.filas[fila+1].bloques == []: 
            #Si la fila de abajo no tiene bloques cae directamente
            self.caida_libre(fila)
            fila += 1
            if fila == self.n_filas-1:
                return None #Ya se ha acabado la caida se llega a la ultima fila
        self.caida_por_bloques(fila) 
        #Si ha hecho caida libre y no está en la último fila miro a ver si algún bloque puede caer
        return None

    def caida_libre(self, fila):
        for bloque in self.filas[fila].bloques:
            # Copia la fila de arriba en la de abajo bloque a bloque
            self.filas[fila + 1].bloques.append(bloque)
        # Borra los bloques de la fila de arriba
        self.filas[fila].bloques = [] 
        return None

    def caida_por_bloques(self, fila):
        pos_bloque = 0
        # Guardo los bloques que caen para borrarles de la fila de la que caen
        bloques_a_eliminar = []  
        for bloque in self.filas[fila].bloques:
            if self.puede_caer(bloque, fila):
                bloques_a_eliminar, pos_nueva = self.caida_de_bloque(fila, bloque, pos_bloque, bloques_a_eliminar)
                fila_bloque = fila + 1 #La fila_bloque se usa para ver si el bloque puede caer a la siguiente fila
                if fila_bloque != self.n_filas-1:
                    while self.puede_caer(bloque, fila_bloque): #Se mira se el bloque puede caer aún más filas
                        bloques_a_eliminar, pos_nueva = self.caida_de_bloque(fila_bloque, bloque, pos_nueva, bloques_a_eliminar)
                        fila_bloque += 1  #Se mira si el bloque puede seguir cayendo y se apunta el bloque a eliminar
                        if fila_bloque == self.n_filas-1:
                            break
            pos_bloque += 1
        self.elimina_bloques(bloques_a_eliminar) 
        return None

    def puede_caer(self, bloque_arriba, fila):
        puede_caer = True
        for bloque_debajo in self.filas[fila + 1].bloques:
            # Si el bloque comparte posición con uno de debajo entonces no puede caer
            if bloque_arriba.comparten_posicion_bloques(bloque_debajo) == True:
                puede_caer = False 
                break
        return puede_caer
    
    def elimina_bloques(self, bloques_a_eliminar):

        pos = 0 
        # Cantidad de bloques eliminados por fila
        cant_bloques_eliminados = [0]*self.n_filas 
        for numero in bloques_a_eliminar:
            # Si la posición es par se lee la fila del bloque
            if pos % 2 == 0: 
                fila = numero
            # Si es impar se lee su posicion en la fila
            else:
                pos_bloque = numero 
                pos_bloque -= cant_bloques_eliminados[fila]
                # La posición del bloque en la lista de bloques cambia si ya se han elimnado bloques en esa fila
                # disminuye por cada bloque eliminado en la fila ya que se empieza eliminando de izq a der
                self.filas[fila].bloques.pop(pos_bloque)
                self.filas[fila].bloques.sort()
                cant_bloques_eliminados[fila] += 1 
            pos += 1                            
        return None                                

    def caida_de_bloque(self, fila, bloque, pos_bloque, bloques_a_eliminar):
        self.filas[fila + 1].bloques.append(bloque)
        bloques_a_eliminar.append(fila)
        bloques_a_eliminar.append(pos_bloque)
        #Ordeno los bloques en la fila
        pos_bloque = self.filas[fila + 1].ordenar_bloques() 
        return bloques_a_eliminar, pos_bloque      

    def contar_puntos_en_tablero(self):
        puntos = 0
        for filas in self.filas:
            for bloque in filas.bloques:
                # Suma puntos según la longitud de cada bloque (las casillas que ocupan)
                puntos += bloque.longitud 
        return puntos

    def intentar_eliminar_filas(self):
        #Se usara para saber que fila eliminar en caso de ser necesario
        pos_fila = 0 
        for fila in self.filas:
            if fila.bloques != []: 
                bloques_con_mismo_simbolo = True 
                simbolo_bloques = fila.bloques[0].simbolo
                # Sera una cadena con las posiciones de las casillas de los bloques de la fila del 0 al 9
                casillas_ocupadas = ""
                for bloque in fila.bloques:
                    if bloque.simbolo != simbolo_bloques and bloques_con_mismo_simbolo:
                        bloques_con_mismo_simbolo = False
                    casillas_ocupadas += bloque.casillas_bloque()
                # Si hay 10 casillas ocupadas entonces la fila esta llena y se debe borrar
                if len(casillas_ocupadas) == 10: 
                    self.puntuacion += 10
                    self.filas[pos_fila].bloques = [] 
                    #Si los bloques tienen el mismo simbolo se borra el tablero y se suman los puntos
                    if bloques_con_mismo_simbolo == True:
                        self.puntuacion += self.contar_puntos_en_tablero()
                        self.filas = []
                        for i in range(self.n_filas):
                            self.filas.append(Fila())
                        return True, -1 # Tras elimina el tablero no se sigue intentando eliminar mas filas
                    else:
                        return True, pos_fila
            pos_fila += 1 #Miro si se puede eliminar la siguiente fila
        return False, -1

class Fila():

    def __init__(self):
        self.bloques = []

    def anadir_bloque(self, inic, longitud, simbolo):
        #Ordeno los bloques segun su inic
        self.bloques.append(Bloque(inic, longitud, simbolo))
        return None

    # Ordena los bloques de una fila segun sus posiciones iniciales y devuelvo la posicion del último bloque 
    def ordenar_bloques(self): 
        pos_nueva = 0         
        for bloque in self.bloques:
            if bloque.inic > self.bloques[len(self.bloques) - 1].inic or pos_nueva == len(self.bloques) - 1:
                break    
            pos_nueva += 1
        self.bloques.sort() 
        return pos_nueva

class Bloque():

    def __init__(self, inic, longitud, simbolo):
        self.inic = inic
        self.longitud = longitud
        self.simbolo = simbolo
        return None

    # Devuelve las posiciones de las casillas en las que esta el bloque en un string
    def casillas_bloque(self): 
        casillas_del_bloque = ""
        for longitud in range(self.longitud):
            casillas_del_bloque += str((self.inic + longitud))
        return casillas_del_bloque

    # Devuelve True si comparten posicion los bloques y False si no lo hacen
    def comparten_posicion_bloques(self, bloque_debajo): 
        comparten_posicion = False
        #Este es un string que tiene todas las casillas en las que esta el bloque de arriba
        casillas_bloque_de_arriba = self.casillas_bloque() 
        for longitud in range(bloque_debajo.longitud):
            # Si hay alguna casilla que comparten entonces comparten posicion
            if casillas_bloque_de_arriba.find(str(bloque_debajo.inic + longitud)) != -1:
                comparten_posicion = True
                break #No es necesario comprobar mas ya se sabe que comparten una posicion
        return comparten_posicion

    def __lt__(self, other):
        return self.inic < other.inic
                # Suma puntos según la longitud de cada bloque (las casillas que ocupan)
if __name__ == "__main__":
    app = MyApp(0)
    app.MainLoop()
