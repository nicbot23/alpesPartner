# ==========================================
# SAGA LOGGER - NUEVA IMPLEMENTACIÓN
# ==========================================
# Importa la nueva versión híbrida MySQL/SQLite

# from .saga_logger_v2 import (
#     SagaLoggerV2,
#     EstadoSaga,
#     EstadoPaso,
#     #init_db,
#     Saga,
#     SagaPaso,          # nombre real en V2
# )

from .saga_logger_v2 import SagaLogger as SagaLoggerV2

# Estados para mantener compatibilidad con consumidores y despachadores
class EstadoSaga:
    INICIADA = "INICIADA"
    EN_PROGRESO = "EN_PROGRESO"
    COMPLETADA = "COMPLETADA"
    FALLIDA = "FALLIDA"
    COMPENSANDO = "COMPENSANDO"
    COMPENSADA = "COMPENSADA"
    CANCELADA = "CANCELADA"


class EstadoPaso:
    PENDIENTE = "PENDIENTE"
    EJECUTANDO = "EJECUTANDO"
    OK = "OK"
    FALLIDO = "FALLIDO"
    COMPENSADO = "COMPENSADO"

# Alias de compatibilidad para código legado
#PasoSaga = SagaPaso

# Alias conveniente (mismo nombre que usas en otros módulos)
# SagaLogger = SagaLoggerV2


# # Para mantener compatibilidad con código existente
# __all__ = [
#     "SagaLoggerV2",
#     "SagaLogger",      # alias
#     "EstadoSaga",
#     "EstadoPaso",
#     "init_db",
#     "Saga",
#     "SagaPaso",
#     "PasoSaga",        # alias legacy
# ]