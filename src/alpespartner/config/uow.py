from alpespartner.config.db import db
from alpespartner.seedwork.infraestructura.uow import UnidadTrabajo, Batch

class UnidadTrabajoSQLAlchemy(UnidadTrabajo):

    def __init__(self):
        self._batches: list[Batch] = list()

    def __enter__(self) -> UnidadTrabajo:
        return super().__enter__()

    def __exit__(self, *args):
        self.rollback()

    def _limpiar_batches(self):
        self._batches = list()

    @property
    def savepoints(self) -> list:
        # TODO Lea savepoint
        return []

    @property
    def batches(self) -> list[Batch]:
        return self._batches             

    def commit(self, repositorio_eventos_func=None):
        """
        Commit actualizado para soportar eventos CDC
        """
        # Ejecutar batches normales
        for batch in self.batches:
            lock = batch.lock
            batch.operacion(*batch.args, **batch.kwargs)
        
        # Obtener y procesar eventos si se proporciona función de repositorio de eventos
        if repositorio_eventos_func:
            eventos = self._obtener_eventos()
            if eventos:
                repo_eventos = repositorio_eventos_func()
                for evento in eventos:
                    repo_eventos.agregar(evento)
                
        db.session.commit() # Commits the transaction

        super().commit()

    def _obtener_eventos(self):
        """
        Obtiene eventos de todos los agregados que han sido tocados en esta transacción
        """
        eventos = []
        
        # Buscar en objetos de la sesión que implementen AgregacionRaiz
        for obj in db.session.identity_map.all_states():
            if hasattr(obj, 'eventos') and callable(getattr(obj, 'limpiar_eventos', None)):
                eventos.extend(obj.eventos)
                obj.limpiar_eventos()
                
        return eventos

    def rollback(self, savepoint=None):
        if savepoint:
            savepoint.rollback()
        else:
            db.session.rollback()
        
        super().rollback()
    
    def savepoint(self):
        # TODO Con MySQL y Postgres se debe usar el with para tener la lógica del savepoint
        # Piense como podría lograr esto ¿tal vez teniendo una lista de savepoints y momentos en el tiempo?
        ...

# Alias para facilitar importación en comandos
UnidadTrabajoPuerto = UnidadTrabajoSQLAlchemy