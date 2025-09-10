"""Excepciones para la capa de infraestructura de comisiones

En este archivo usted encontrará las excepciones específicas
de la capa de infraestructura del dominio de comisiones

"""

from alpespartner.seedwork.dominio.excepciones import ExcepcionDominio

class ExcepcionFabrica(ExcepcionDominio):
    def __init__(self, mensaje):
        self.__mensaje = mensaje
    
    def __str__(self):
        return str(self.__mensaje)
