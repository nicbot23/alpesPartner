"""
Excepciones del dominio Marketing
"""
from typing import Optional


class ExcepcionDominio(Exception):
    """Excepción base del dominio"""
    
    def __init__(self, mensaje: str, codigo: Optional[str] = None):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.codigo = codigo


class ExcepcionReglaNegocio(ExcepcionDominio):
    """Excepción cuando se viola una regla de negocio"""
    pass


class ExcepcionValidacion(ExcepcionDominio):
    """Excepción de validación de datos"""
    pass


class ExcepcionInfraestructura(ExcepcionDominio):
    """Excepción de infraestructura"""
    pass