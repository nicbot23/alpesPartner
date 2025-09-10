from typing import Callable, Dict
from .comandos import Comando
from .queries import Query
_command_handlers: Dict[type, Callable] = {}
_query_handlers: Dict[type, Callable] = {}
_event_handlers: Dict[str, list[Callable]] = {}

def manejador_comando(tipo: type):
    def deco(fn: Callable): _command_handlers[tipo]=fn; return fn
    return deco

def manejador_query(tipo: type):
    def deco(fn: Callable): _query_handlers[tipo]=fn; return fn
    return deco

def manejador_evento(nombre: str):
    def deco(fn: Callable): _event_handlers.setdefault(nombre,[]).append(fn); return fn
    return deco

def ejecutar_comando(cmd: Comando):
    t=type(cmd); 
    if t not in _command_handlers: raise KeyError(f'No handler para {t}')
    return _command_handlers[t](cmd)

def ejecutar_query(q: Query):
    t=type(q); 
    if t not in _query_handlers: raise KeyError(f'No handler para {t}')
    return _query_handlers[t](q)

def publicar_evento(nombre: str, payload: dict):
    for fn in _event_handlers.get(nombre,[]): fn(payload)
