"""Objetos valor base parte del seedwork del proyecto

En este archivo usted encontrará los objetos valor base reusables parte del seedwork del proyecto

"""

from dataclasses import dataclass
from abc import ABC


@dataclass(frozen=True)
class ObjetoValor:
    """Clase base abstracta para todos los objetos valor del dominio"""
    ...
