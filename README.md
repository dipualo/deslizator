# Deslizator

Este repositorio se basa en la práctica de paradigmas de programación del grado en ingeniería informática de la universidad de Valladolid. 
Este práctica es un videojuego de caida de bloques estilo tetris realizado en python con ayuda de la librería wxPython, se añade un video como ejemplo de una 
ejecución del juego.

## Reglas del juego

El juego se basa en que cada turno se crean unos bloques en la primera línea y el jugador puede hacer una jugada moviendo un bloque con el ratón hasta que colisione con otro bloque o una pared del juego o 
pulasar en una casilla vacia y que caiga la línea de arriba. El objetivo del juego es obtener la mayor puntación antes de que se acabe lo que ocurre cuando no se puede insetar una nueva fila arriba. 
Para ganar puntuación se deben eliminar filas lo que se consigue llenando una fila con bloque y se gana 10 puntos, además si los bloques de la fila son del mismo color se elimina todo el tablero y se 
ganaran tantos puntos como casillas ocupen los bloques en el tablero.

## Ayuda en el juego

En la parte inferior derecha aparece un mensaje de ayuda que indica en que situación del juego se está.

## Otras opciones

EL juego permite aumentar el tamaño de filas o cambiar la velociadad de la animación cambiando los valores correspondientes. También, los bloques que caen en cada línea se basan en una secuencia de bloques
que están representados en el fichero de texto lista_filas_a_caer.txt, que se puede modificar, y es necesario para ejecutar el juego como la librería wxPython y python. 
Y si se fijan en el juego se puede ver una lista de jugadas está es pedida para la práctica de la asignatura y se basa en los comandos por teclados que en las primeras versiones
se usan para realizar las jugadas del juego antes de que se hiciera la interfaz gráfica y el juego está diselñado a partir de estos comandos.
