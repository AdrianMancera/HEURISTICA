import constraint
from constraint import *
import os
import numpy as np
import sys

class Barco():
    #
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

        if len(self.mapa) == 0:
            raise ("NO HAY MAPA")
        # tamaño tablero el cual restringe el dominio de las variables
        # tenemos las variables con sus variables en un array bidimensional

        path2 = os.path.abspath(pathContainers)
        self.lista_contendores_input = np.loadtxt(path2, dtype=str)

        if len(self.lista_contendores_input) == 0:
            raise ("NO HAY CONTENEDORES")


    def definirTipoCasillas(self):

        for i in range(len(self.mapa)):
            for j in range(len(self.mapa[i])):
                if self.mapa[i][j] == "E":
                    self.lista_casilla_carga.append([i + 1, j + 1])

                if self.mapa[i][j] == "N" or self.mapa[i][j] == "E":
                    self.lista_casilla_estandar.append([i + 1, j + 1])

                if self.mapa[i][j] != "X":
                    if self.mapa[i][j] == "E" and self.mapa[i + 1][j] == "X":
                        self.lista_casilla_suelo.append([i + 1, j + 1])

                if self.mapa[i][j] != "E" and self.mapa[i][j] != "X" and self.mapa[i][j]!="N":
                    raise ("EL MAPA ESTA MAL DEFINIDO")




        #pasamos de lista normal a tupla de tuplas
        for i in self.lista_casilla_carga:
            self.lista_casilla_carga_tupla.append(tuple(i))

        for i in self.lista_casilla_estandar:
            self.lista_casilla_estandar_tupla.append(tuple(i))

        for i in self.lista_casilla_suelo:
            self.lista_casilla_suelo_tupla.append(tuple(i))



        for i in self.lista_contendores_input:
            if i[1] == "S":
                self.lista_contenedor_estandar.append(i)
                self.problem.addVariables(i[0], self.lista_casilla_estandar_tupla)
            if i[1] == "R":
                self.lista_contenedor_carga.append(i)
                self.problem.addVariables(i[0], self.lista_casilla_carga_tupla)
            if i[1] != "R" and i[1] != "S":
                raise ("EL TIPO DE CONTENEDOR ESTA MAL DEFINIDO")

        if len( self.lista_casilla_carga) < len(self.lista_contenedor_carga):
            raise ("DEMASIODOS CONTENETEDORES REFIGRERADOS Y POCAS POSICIONES CARGA")

        if ((len(self.lista_casilla_estandar) < (len(self.lista_contenedor_carga)+len(self.lista_contenedor_estandar)))) :
            raise ("DEMASIADOS CONTENEDORES, MAPA PEQUEÑO")

    def constraits(self):

            # 1º RESTRICCION NINGUNA CONTENEDOR PUEDE TENER LA MISMA CASILLA
            self.problem.addConstraint(AllDifferentConstraint(), ([*self.problem._variables]))

            def check2under1(pos1, pos2):

                if pos1[1] == pos2[1]:
                    if pos1[0] < pos2[0]:
                        return True
                    return False
                return True

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

            self.problem.addConstraint(gravity, ([*self.problem._variables]))


    def getSolution(self):

        longuitud = len(self.problem.getSolutions())
        print(longuitud)
        with open('output.txt', 'w') as temp_file:
            temp_file.write("%s" % "NUMERO DE SOLUCIONES: " + str(longuitud) +"\n")
            for item in self.problem.getSolutions():
                temp_file.write("%s\n" % item)

        self.file = open('output.txt', 'r')


home = sys.argv[1]
mapa = sys.argv[2]
contenedores = sys.argv[3]
pathMap = home + '/' + mapa
pathContainers = home + '/' + contenedores


obj = Barco()
obj.cargaCondicionesIniciales()
obj.definirTipoCasillas()
obj.constraits()
obj.getSolution()
