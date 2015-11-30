#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
genetico.py
------------
Este modulo incluye el algoritmo genérico para algoritmos genéticos, así como un
algoritmo genético adaptado a problemas de permutaciones, como el problema de las
n-reinas o el agente viajero.
Como tarea se pide desarrollar otro algoritmo genético con el fin de probar otro tipo
de métodos internos, así como ajustar ambos algortmos para que funcionen de la mejor
manera posible.
Para que funcione, este modulo debe de encontrarse en la misma carpeta que blocales.py
y nreinas.py vistas en clase.
"""

__author__ = 'Escribe aquí tu nombre'

import nreinas
import random
import time


class Genetico:
    """
    Clase genérica para un algoritmo genético.
    Contiene el algoritmo genético general y las clases abstractas.
    """

    def busqueda(self, problema,Hacer_C, n_poblacion=10, n_generaciones=30, elitismo=True):
        """
        Algoritmo genético general
        @param problema: Un objeto de la clase blocal.problema
        @param n_poblacion: Entero con el tamaño de la población
        @param n_generaciones: Número de generaciones a simular
        @param elitismo: Booleano, para aplicar o no el elitismo
        @return: Un estado del problema
        """
        poblacion = [problema.estado_aleatorio() for _ in range(n_poblacion)]
        if Hacer_C == 2:
            for _ in range(n_generaciones):
                #Como usaremos la selecion por ruleta. 
                #Se ultiliza dos funciones para el calculo de la aptitud. 
                #La primera parte, realiza la suma del costo de TODA la Poblacion
                #Esto se puede hacer en una sola funcion de aptiud, pero realisar la suma Total de las aptitudes
                #para calcular la aoptitud de cada individuo. Seria gasto de tiempo. 
                #Por cada generacion de la poblacion, solo se necesita hacer la suma total de las aptitudes una sola ves. 
                Costo_Total = self.calcula_aptitud2(poblacion,problema.costo)
                #La segunda, saca el porcentaje de la poblacion. Por individuo. 
                #El costo total es el 100% y cada individuo tiene una x parte de ese costo.
                #Aqui se hace el cambio: En lugar de usar porcentaje entre 0 y 100 usamos numeros entre 0 y 1
                aptitud = [self.calcula_aptitud(individuo,problema.costo, Costo_Total) for individuo in poblacion]

                elite = min(poblacion, key=problema.costo) if elitismo else None

                padres, madres = self.seleccion(poblacion, aptitud)

                poblacion = self.mutacion(self.cruza_listas(padres, madres))

                poblacion = poblacion[:n_poblacion]

                if elitismo:
                    poblacion.append(elite)

            e = min(poblacion, key=problema.costo)
        else:
            for _ in range(n_generaciones):

                aptitud = [self.calcula_aptitud(individuo, problema.costo) for individuo in poblacion]

                elite = min(poblacion, key=problema.costo) if elitismo else None

                padres, madres = self.seleccion(poblacion, aptitud)

                poblacion = self.mutacion(self.cruza_listas(padres, madres))

                poblacion = poblacion[:n_poblacion]

                if elitismo:
                    poblacion.append(elite)

            e = min(poblacion, key=problema.costo)
        return e

    def calcula_aptitud(self, individuo, costo=None):
        """
        Calcula la adaptación de un individuo al medio, mientras más adaptado mejor, por default
        es inversamente proporcionl al costo (mayor costo, menor adaptción).
        @param individuo: Un estado el problema
        @param costo: Una función de costo (recibe un estado y devuelve un número)
        @return un número con la adaptación del individuo
        """
        #return max(0, len(individuo) - costo(individuo))
        return 1.0 / (1.0 + costo(individuo))

    def seleccion(self, poblacion, aptitud):
        """
        Seleccion de estados
        @param poblacion: Una lista de individuos
        @return: Dos listas, una con los padres y otra con las madres.
        estas listas tienen una dimensión int(len(poblacion)/2)
        """
        raise NotImplementedError("¡Este metodo debe ser implementado por la subclase!")

    def cruza_listas(self, padres, madres):
        """
        Cruza una lista de padres con una lista de madres, cada pareja da dos hijos
        @param padres: Una lista de individuos
        @param madres: Una lista de individuos
        @return: Una lista de individuos
        """
        hijos = []
        for (padre, madre) in zip(padres, madres):
            hijos.extend(self.cruza(padre, madre))
        return hijos

    def cruza(self, padre, madre):
        """
        Cruza a un padre con una madre y devuelve una lista de hijos, mínimo 2
        """
        raise NotImplementedError("¡Este metodo debe ser implementado por la subclase!")

    def mutacion(self, poblacion):
        """
        Mutación de una población. Devuelve una población mutada
        """
        raise NotImplementedError("¡Este metodo debe ser implementado por la subclase!")


class GeneticoPermutaciones1(Genetico):
    """
    Clase con un algoritmo genético adaptado a problemas de permutaciones
    """
    def __init__(self, prob_muta=0.7):
        """
        @param prob_muta : Probabilidad de mutación de un cromosoma (0.01 por defualt)
        """
        #Agregamos la probabilidad de cruza
        self.prob_muta = prob_muta
        self.nombre = 'propuesto por el profesor con prob. de mutación ' + str(prob_muta)

    def seleccion(self, poblacion, aptitud):
        """
        Selección por torneo.
        """
        padres = []
        baraja = range(len(poblacion))
        random.shuffle(baraja)
        for (ind1, ind2) in [(baraja[i], baraja[i+1]) for i in range(0, len(poblacion)-1, 2)]:
            ganador = ind1 if aptitud[ind1] > aptitud[ind2] else ind2
            padres.append(poblacion[ganador])

        madres = []
        random.shuffle(baraja)
        for (ind1, ind2) in [(baraja[i], baraja[i+1]) for i in range(0, len(poblacion)-1, 2)]:
            ganador = ind1 if aptitud[ind1] > aptitud[ind2] else ind2
            madres.append(poblacion[ganador])

        return padres, madres

    def cruza(self, padre, madre):
        """
        Cruza especial para problemas de permutaciones
        @param padre: Una tupla con un individuo
        @param madre: Una tupla con otro individuo
        @return: Dos individuos resultado de cruzar padre y madre con permutaciones
        """
        hijo1, hijo2 = list(padre), list(madre)
        corte1 = random.randint(0, len(padre)-1)
        corte2 = random.randint(corte1+1, len(padre))
        for i in range(len(padre)):
            if i < corte1 or i >= corte2:
                hijo1[i], hijo2[i] = hijo2[i], hijo1[i]
                while hijo1[i] in padre[corte1:corte2]:
                    hijo1[i] = madre[padre.index(hijo1[i])]
                while hijo2[i] in madre[corte1:corte2]:
                    hijo2[i] = padre[madre.index(hijo2[i])]
        return [tuple(hijo1), tuple(hijo2)]

    def mutacion(self, poblacion):
        """
        Mutación para individus con permutaciones. Utiliza la variable local self.prob_muta
        @param poblacion: Una lista de individuos (tuplas).
        @return: Los individuos mutados
        """
        poblacion_mutada = []
        for individuo in poblacion:
            individuo = list(individuo)
            for i in range(len(individuo)):
                if random.random() < self.prob_muta:
                    k = random.randint(0, len(individuo) - 1)
                    individuo[i], individuo[k] = individuo[k], individuo[i]
            poblacion_mutada.append(tuple(individuo))
        return poblacion_mutada


################################################################################################
#  AQUI EMPIEZA LO QUE HAY QUE HACER CON LA TAREA
################################################################################################

class GeneticoPermutaciones2(Genetico):
    """
    Clase con un algoritmo genético adaptado a problemas de permutaciones
    """
    def __init__(self, prob_muta):
        """
        Aqui puedes poner algunos de los parámetros que quieras utilizar en tu clase
        """
        self.prob_muta = prob_muta
        self.nombre = 'propuesto por Angelica Maria' + str(prob_muta)
        #
        # ------ IMPLEMENTA AQUI TU CÓDIGO ------------------------------------------------------------------------
        #

    def calcula_aptitud2(self,poblacion, costo):
        #Saca el costo total de los individuos. 
        #La suma del costo de toda poblacion. Para ultilisarce despues. 
        Costo_Total = 0
       
        for ind in range(len(poblacion)):
            individuo = poblacion[ind]
            Costo_Total = Costo_Total + costo(individuo)
        return Costo_Total

    def calcula_aptitud(self,individuo, costo,Costo_Total):
        """
        Desarrolla un método específico de medición de aptitud.
        """
        ####################################################################
        #                          20 PUNTOS
        ####################################################################
        #
        # ------ IMPLEMENTA AQUI TU CÓDIGO --------------------------------
        #
        #Regla de 3:
        '''
        Si el costo total es el :1.0 
        Entonces cada individuo tiene una parte de ese numero.
        '''
        Costo_I = costo(individuo)
        Porcentaje = (Costo_I*1.0)/Costo_Total
        return Porcentaje
        #raise NotImplementedError("¡Este metodo debe ser implementado!")

    def seleccion(self, poblacion, aptitud):
        """
        Desarrolla un método específico de selección.
        """
        #####################################################################
        #                          20 PUNTOS
        #####################################################################
        #
        # ------ IMPLEMENTA AQUI TU CÓDIGO ----------------------------------
        #CodigoPrestado
        '''
        Aqui se hace una suma de cada una de los aptitudes de los individuos. 
        Debe ser iagual a auno.
        Descomentar para ver la suma de todas las aoptitudes.
        '''
        #total = 0
        #for i in range(len(aptitud)):
        #    total = total + aptitud[i]
        #print 'Total: ', total
        padres = []
        for ind in range(len(poblacion)):
            Numero_Aleatorio = random.random() #Numero aleatorio, entre 0 y 1
            Suma_Porcentajes = 0
            for ind2 in range(len(poblacion)):
                Suma_Porcentajes =Suma_Porcentajes + aptitud[ind2] #Se estan sumando las aotitudes
                if Suma_Porcentajes >= Numero_Aleatorio: #Si es mayor o igual, se agrega
                    padres.append(poblacion[ind2])
                    continue
        madres = []
        for ind in range(len(poblacion)):
            Numero_Aleatorio = random.random() #Numero aleatorio, entre 0 y 1
            Suma_Porcentajes = 0
            for ind2 in range(len(poblacion)):
                Suma_Porcentajes =Suma_Porcentajes + aptitud[ind2] #Se estan sumando las aotitudes
                if Suma_Porcentajes >= Numero_Aleatorio: #Si es mayor o igual, se agrega
                    madres.append(poblacion[ind2])
                    continue


        return padres, madres
        #raise NotImplementedError("¡Este metodo debe ser implementado!")

    def cruza(self, padre, madre):
        """
        Cruza especial para problemas de permutaciones
        @param padre: Una tupla con un individuo
        @param madre: Una tupla con otro individuo
        @return: Dos individuos resultado de cruzar padre y madre con permutaciones
        """
        hijo1, hijo2 = list(padre), list(madre)
        corte1 = random.randint(0, len(padre)-1)
        corte2 = random.randint(corte1+1, len(padre))
        for i in range(len(padre)):
            if i < corte1 or i >= corte2:
                hijo1[i], hijo2[i] = hijo2[i], hijo1[i]
                while hijo1[i] in padre[corte1:corte2]:
                    hijo1[i] = madre[padre.index(hijo1[i])]
                while hijo2[i] in madre[corte1:corte2]:
                    hijo2[i] = padre[madre.index(hijo2[i])]
        return [tuple(hijo1), tuple(hijo2)]

    def mutacion(self, poblacion):
        """
        Desarrolla un método específico de mutación.

        """
        ###################################################################
        #                          20 PUNTOS
        ###################################################################
        '''
        METODO DE Mutación Insert
        Se elije dos puntos. Se acomodan cual es mayor y menor. 
        El menor se pone en la posicion del mayo y desde ahi en adelante se recoren. 
        Ejemplo:
        Teniendo>>> 5,1,2,4,3,6,9,8,7
        Los puntos son: 2 y 8
        Los numeros de esas posiciones son 2>1 y 8>8
        Primer paso: Ponemos el punto menor en posicion del punto mayor, esto se hace recoriendo
            primero>> 5,(1),2,4,3,6,9,8,7
            segundo>> 5,2,(1),4,3,6,9,8,7
            tercero>> 5,2,4,(1),3,6,9,8,7
            cuarto>>  5,2,4,3,(1),6,9,8,7
            quito>>   5,2,4,3,6,(1),9,8,7
            sexto>>   5,2,4,3,6,9,(1),8,7
            septimo>> 5,2,4,3,6,9,8,(1),7
        Antes:   5,(1),2,4,3,6,9,8,7
        Despues: 5,2,4,3,6,9,8,(1),7
        Nota: Los numeros fuera del rango, no se mueven, ya que no se tienen tomados en cuenta.
        '''
        poblacion_mutada = []
        i = 0
        for individuo in poblacion:
            #El individuo, se muta o no se muta
            #Se hace lista, para facil manejo
            individuo = list(individuo)
            if random.random() < self.prob_muta:
                
            #Se hace un ciclo para asegurar que los puntos sean diferentes
                P_menor=P_mayor=0
            #mientras los puntos sean iguales el ciclo sigue
                while P_mayor==P_menor:
                    P_menor = random.randint(0, len(individuo)-1)
                    P_mayor = random.randint(0, len(individuo)-1)
            #cuando sale del ciclo quiere decir que los puntos son diferentes
            #Se asegura que las variables sean menor o mayor, deacuerdo al nombre de la variable
            #Nota solo el numero de las posiciones, no el numero en en la posicion del individuo.
                if P_mayor<P_menor:
                    k=P_menor
                    P_menor=P_mayor
                    P_mayor=k 
                for P_menor in range(P_mayor):
                    Dato2=individuo[P_menor]
                    individuo[P_menor]=individuo[P_menor+1]
                    individuo[P_menor+1]=Dato2
            #se agrega el individuo a la poblacion mutada...
            #Nota: Si se muta ao no el individuo se agrega
            poblacion_mutada.append(tuple(individuo))    

        #se regresa la poblacion mutada.
        return poblacion_mutada
        #raise NotImplementedError("¡Este metodo debe ser implementado!")

def prueba_genetico_nreinas(algo_genetico, problema, n_poblacion, n_generaciones):
    tiempo_inicial = time.time()
    solucion = algo_genetico.busqueda(problema,1,n_poblacion, n_generaciones, elitismo=True)
    tiempo_final = time.time()
    #print "\nUtilizando el algoritmo genético " + algo_genetico.nombre
    #print "Con poblacion de dimensión ", n_poblacion
    #print "Con ", str(n_generaciones), " generaciones"
    #print "Costo de la solución encontrada: ", problema.costo(solucion)
    #print "Tiempo de ejecución en segundos: ", tiempo_final - tiempo_inicial
    return problema.costo(solucion)
 
def prueba_genetico_nreinas2(algo_genetico, problema, n_poblacion, n_generaciones):
    tiempo_inicial = time.time()
    solucion = algo_genetico.busqueda(problema,2, n_poblacion, n_generaciones, elitismo=True)
    tiempo_final = time.time()
    print "\nUtilizando el algoritmo genético " + algo_genetico.nombre
    print "Con poblacion de dimensión ", n_poblacion
    print "Con ", str(n_generaciones), " generaciones"
    print "Costo de la solución encontrada: ", problema.costo(solucion)
    print "Tiempo de ejecución en segundos: ", tiempo_final - tiempo_inicial
    return solucion



if __name__ == "__main__":

    #################################################################################################
    #                          20 PUNTOS
    #################################################################################################
    # Modifica los valores de la función siguiente (o el parámetro del algo_genetico)
    # buscando que el algoritmo encuentre SIEMPRE una solución óptima, utilizando el menor tiempo
    # posible en promedio. Realiza esto para las 8, 16 y 32 reinas.
    #   -- ¿Cuales son en cada caso los mejores valores (escribelos abajo de esta lines)
    '''
    Se encontran mejores resultados si la mutacion sucede. AUnque sea solo un probabilidad.
    Con 8 reinas y  100 generaciones y 100 corridas> Se obtubo un promedio de 0.407449998856
    Con 16 reynas y 100 generaciones y 100 corridas> Se obtubo un promedio de 1.42738000393
    Con 32 reynas y 100 generaciones y 100 corridas> Se obtubo un promedio de 4.4942199931
    '''
    
    #   -- ¿Que reglas podrías establecer para asignar valores segun tu experiencia
    '''
    Se puede decir, que se podria horrar tiempo, si la probabilidad de mutacion es menor. 
    Y podria ser poco posible que el algoritmo realizarse la mutacion, pero al ahorarse tiempo en no hacer esto,
    puede no llegar a resultados optimos.
    Con la mutacion, se toma mas tiempo, pero tiene mayor probabilidad de encontar solucion optima.
    
    solucion = 0
    Promediar =100
    for  i in range (Promediar):
        solucion += prueba_genetico_nreinas(algo_genetico=GeneticoPermutaciones1(0.15),
                                                    problema=nreinas.ProblemaNreinas(16),
                                                    n_poblacion=32,
                                                    n_generaciones=100, 
                                                    )
    print 'Tiempo Promedio: ', (solucion/Promediar)
    '''
    #################################################################################################
    #                          20 PUNTOS
    #################################################################################################
    # Modifica los valores de la función siguiente (o los posibles parámetro del algo_genetico)
    # buscando que el algoritmo encuentre SIEMPRE una solución óptima, utilizando el menor tiempo
    # posible en promedio. Realiza esto para las 8, 16 y 32 reinas.
    #   -- ¿Cuales son en cada caso los mejores valores (escribelos abajo de esta lines)
    #   `Prob Muta> 0.00001
    #    Con 8 reinas: costo 0 y 3 segundos.
    #    Con 16 reinas:  costo 1 en 5 segundos 
    #    Con 32 reinas: costo 6 y 13 segundos
    #    Prob Muta> 0.01
    #    Con 8 reinas: costo 0 y 3 segundos.
    #    Con 16 reinas:  costo 2 en 5 segundos 
    #    Con 32 reinas: costo 4 y 13 segundos
    #
    #   -- ¿Que reglas podrías establecer para asignar valores segun tu experiencia? Escribelo aqui
    #   abajo, utilizando tnto espacio como consideres necesario.
    #   El metodo de selecion por ruleta, es mas efectivo, ya que por mayor probabilidad de que los mejores padres se cruzen
    # Razon por las cual los resultados son mejores, al compararlos por la selecion por torneo. 
    # Tambien con mayor numero de generaciones, mejor posibilidades, pero el algoritmo tarda mas.
    # Recuerda de quitar los comentarios de las lineas siguientes:
    solucion = prueba_genetico_nreinas2(algo_genetico=GeneticoPermutaciones2(0.5),
                                            problema=nreinas.ProblemaNreinas(8),
                                            n_poblacion=32,
                                            n_generaciones=100)