import constraint
from constraint import *
import os
import numpy as np
import sys

class Barco():

    def __init__(self):
        self.problem = constraint.Problem()
        self.contenedores = []
        self.mapa = []
        self.lista_contendores_input =[]
        self.lista_casilla_carga = []
        self.lista_casilla_estandar = []
        self.lista_casilla_suelo = []
        #TENEMOS CLASIFICADOS LOS TIPO DE CONTENEDORES
        self.lista_contenedor_estandar = []
        self.lista_contenedor_carga = []
        #TUPLAS QUE LUEGO SON LAS QUE USAMOS PARA METER EL DOMINIO
        self.lista_casilla_carga_tupla = []
        self.lista_casilla_estandar_tupla = []
        self.lista_casilla_suelo_tupla = []
        self.file=""



    def cargaCondicionesIniciales(self):
        path = os.path.abspath(pathMap)
        self.mapa = np.loadtxt(path, dtype=str)

        #Se comprueba si se ha introducido un mapa
        if len(self.mapa) == 0:
            raise ("NO HAY MAPA")

        path2 = os.path.abspath(pathContainers)
        self.lista_contendores_input = np.loadtxt(path2, dtype=str)

        #Se comprueba si se han introducido contenedores
        if len(self.lista_contendores_input) == 0:
            raise ("NO HAY CONTENEDORES")


    def definirTipoCasillas(self):
        #Recorremos el mapa e introducimos cada tipo de casilla en su respectiva lista
        for i in range(len(self.mapa)):
            for j in range(len(self.mapa[i])):

                if self.mapa[i][j] == "E":
                    self.lista_casilla_carga.append([i + 1, j + 1])

                #Estas casillas se usaran para los contenedores estandar, por eso se añaden tanto tipo N como E
                if self.mapa[i][j] == "N" or self.mapa[i][j] == "E":
                    self.lista_casilla_estandar.append([i + 1, j + 1])

                if self.mapa[i][j] != "X":
                    if self.mapa[i][j] == "E" and self.mapa[i + 1][j] == "X":
                        self.lista_casilla_suelo.append([i + 1, j + 1])

                #Comprobamos si las casillas se corresponden con los valores definidos en el enunciado
                if self.mapa[i][j] != "E" and self.mapa[i][j] != "X" and self.mapa[i][j]!="N":
                    raise ("EL MAPA ESTA MAL DEFINIDO")

                #Comprobamos que en la última línea del mapa hay suelo
                if self.mapa[len(self.mapa)-1][j] != "X":
                    raise ("NO HAY SUELO")


        #pasamos de lista normal a tupla de tuplas
        for i in self.lista_casilla_carga:
            self.lista_casilla_carga_tupla.append(tuple(i))

        for i in self.lista_casilla_estandar:
            self.lista_casilla_estandar_tupla.append(tuple(i))

        for i in self.lista_casilla_suelo:
            self.lista_casilla_suelo_tupla.append(tuple(i))


        #Se recorre la lista de contenedores,se comprueba su tipo y se añade cada contenedor como variable
        for i in self.lista_contendores_input:
            #Contenedores de tipo estándar
            if i[1] == "S":
                self.lista_contenedor_estandar.append(i)
                self.problem.addVariables(i[0], self.lista_casilla_estandar_tupla)
            #Contenedores de tipo refrigerado
            if i[1] == "R":
                self.lista_contenedor_carga.append(i)
                self.problem.addVariables(i[0], self.lista_casilla_carga_tupla)
            #Comprobación de que se introduce un tipo correcto de contenedor
            if i[1] != "R" and i[1] != "S":
                raise ("EL TIPO DE CONTENEDOR ESTA MAL DEFINIDO")
            #Comprobación de que el puerto al que va el contenedor es el correcto
            if (i[2] != "1") and (i[2] != "2"):
                raise ("EL PUERTO ESTA MAL DEFINIDO")

        #Comprobación de que no puede haber más contenedores refrigerados que casillas con carga
        if len( self.lista_casilla_carga) < len(self.lista_contenedor_carga):
            raise ("DEMASIODOS CONTENETEDORES REFIGRERADOS Y POCAS POSICIONES CARGA")

        #Comprobación de que no puede haber más contenedores que casillas
        if ((len(self.lista_casilla_estandar) < (len(self.lista_contenedor_carga)+len(self.lista_contenedor_estandar)))) :
            raise ("DEMASIADOS CONTENEDORES, MAPA PEQUEÑO")

    def constraits(self):

            # 1ª RESTRICCIÓN: No puede haber dos contenedores en la misma casilla
            self.problem.addConstraint(AllDifferentConstraint(), ([*self.problem._variables]))

            def check2under1(pos1, pos2):

                if pos1[1] == pos2[1]:
                    if pos1[0] < pos2[0]:
                        return True
                    return False
                return True

            #2ª RESTRICCIÓN: Los contenedores de tipo 2 tienen que estar debajo de los de tipo 1
            for i in  self.lista_contendores_input:
                for j in  self.lista_contendores_input:
                    if i[0] != j[0] and i[2] == "1" and j[2] == "2":
                        self.problem.addConstraint(check2under1, (i[0], j[0]))

            def gravity(*args):
                return_list = []
                for i in list(args):
                    if i in self.lista_casilla_suelo_tupla:
                        return_list.append(True)
                    else:
                        resultado = False
                        for j in list(args):
                            if (j != i):
                                if i[1] == j[1]:
                                    if i[0] + 1 == j[0]:
                                        resultado = True
                        return_list.append(resultado)
                return all(return_list)

            #3ª RESTRICCIÓN: Los contenedores han de estar apoyados en otro contenedor o en el suelo
            self.problem.addConstraint(gravity, ([*self.problem._variables]))


    def getSolution(self):

        longuitud = len(self.problem.getSolutions())
        with open(mapa[:-4] + "-" + contenedores[:-4] + ".output", 'w') as temp_file:
            temp_file.write("%s" % "NUMERO DE SOLUCIONES: " + str(longuitud) + "\n")
            for item in self.problem.getSolutions():
                temp_file.write("%s\n" % item)

        self.file = open(mapa[:-4] + "-" + contenedores[:-4] + ".output", 'r')

#Introducción de parámetros de entrada y paths
home = sys.argv[1]
mapa = sys.argv[2]
contenedores = sys.argv[3]
pathMap = home + '/' + mapa
pathContainers = home + '/' + contenedores


#Código para el funcionamiento del programa
obj = Barco()
obj.cargaCondicionesIniciales()
obj.definirTipoCasillas()
obj.constraits()
obj.getSolution()
