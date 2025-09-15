"""
Comandos específicos del microservicio Afiliados
Implementa CQRS y principios SOLID
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ..seedwork.aplicacion.comandos import Comando, ResultadoComando, ManejadorComando
from ..seedwork.aplicacion.outbox import ServicioOutbox
from ..dominio.entidades import DocumentoIdentidad, DatosPersonales, TipoDocumento, EstadoAfiliado
from ..dominio.repositorios import RepositorioAfiliados
from ..dominio.eventos import (
    AfiliadoAprobadoIntegracion, 
    AfiliadoDesactivadoIntegracion, 
    DatosAfiliadoActualizadosIntegracion
)

# Comandos

@dataclass
class RegistrarAfiliado(Comando):
    """Comando para registrar un nuevo afiliado"""
    tipo_documento: str
    numero_documento: str
    nombres: str
    apellidos: str
    email: str
    telefono: str
    fecha_nacimiento: datetime

@dataclass
class AprobarAfiliado(Comando):
    """Comando para aprobar un afiliado"""
    afiliado_id: str
    usuario_responsable: str
    observaciones: str = ""

@dataclass
class RechazarAfiliado(Comando):
    """Comando para rechazar un afiliado"""
    afiliado_id: str
    usuario_responsable: str
    motivo: str

@dataclass
class ActivarAfiliado(Comando):
    """Comando para activar un afiliado"""
    afiliado_id: str
    usuario_responsable: str

@dataclass
class DesactivarAfiliado(Comando):
    """Comando para desactivar un afiliado"""
    afiliado_id: str
    usuario_responsable: str
    motivo: str = ""

@dataclass
class ActualizarDatosAfiliado(Comando):
    """Comando para actualizar datos personales de un afiliado"""
    afiliado_id: str
    nombres: str
    apellidos: str
    email: str
    telefono: str
    fecha_nacimiento: datetime
    usuario_responsable: str

# Resultados de comandos

@dataclass
class ResultadoAfiliadoRegistrado(ResultadoComando):
    """Resultado del comando RegistrarAfiliado"""
    afiliado_id: str
    estado: str

@dataclass
class ResultadoAfiliadoAprobado(ResultadoComando):
    """Resultado del comando AprobarAfiliado"""
    afiliado_id: str
    fecha_aprobacion: datetime

@dataclass
class ResultadoAfiliadoRechazado(ResultadoComando):
    """Resultado del comando RechazarAfiliado"""
    afiliado_id: str
    fecha_rechazo: datetime
    motivo: str

@dataclass
class ResultadoAfiliadoActivado(ResultadoComando):
    """Resultado del comando ActivarAfiliado"""
    afiliado_id: str
    fecha_activacion: datetime

@dataclass
class ResultadoAfiliadoDesactivado(ResultadoComando):
    """Resultado del comando DesactivarAfiliado"""
    afiliado_id: str
    fecha_desactivacion: datetime

@dataclass
class ResultadoDatosActualizados(ResultadoComando):
    """Resultado del comando ActualizarDatosAfiliado"""
    afiliado_id: str
    fecha_actualizacion: datetime

# Manejadores de comandos

class ManejadorRegistrarAfiliado(ManejadorComando[RegistrarAfiliado, ResultadoAfiliadoRegistrado]):
    """
    Manejador para el comando RegistrarAfiliado
    Principio de Responsabilidad Única
    """
    
    def __init__(
        self, 
        repositorio_afiliados: RepositorioAfiliados,
        servicio_outbox: ServicioOutbox
    ):
        self._repositorio = repositorio_afiliados
        self._outbox = servicio_outbox
    
    async def handle(self, comando: RegistrarAfiliado) -> ResultadoAfiliadoRegistrado:
        """Maneja el registro de un nuevo afiliado"""
        
        # Validar que no exista el documento
        documento = DocumentoIdentidad(
            tipo=TipoDocumento(comando.tipo_documento),
            numero=comando.numero_documento
        )
        
        if await self._repositorio.existe_documento(documento):
            raise ValueError(f"Ya existe un afiliado con documento {comando.numero_documento}")
        
        # Validar que no exista el email
        if await self._repositorio.existe_email(comando.email):
            raise ValueError(f"Ya existe un afiliado con email {comando.email}")
        
        # Crear datos personales
        datos_personales = DatosPersonales(
            nombres=comando.nombres,
            apellidos=comando.apellidos,
            email=comando.email,
            telefono=comando.telefono,
            fecha_nacimiento=comando.fecha_nacimiento
        )
        
        # Crear afiliado
        from ..dominio.entidades import Afiliado
        afiliado = Afiliado(
            documento=documento,
            datos_personales=datos_personales
        )
        
        # Guardar en repositorio
        await self._repositorio.agregar(afiliado)
        
        # Guardar eventos en outbox para consistencia eventual
        await self._outbox.guardar_eventos_agregado(afiliado.id, afiliado.eventos)
        
        return ResultadoAfiliadoRegistrado(
            exitoso=True,
            afiliado_id=afiliado.id,
            estado=afiliado.estado.value
        )

class ManejadorAprobarAfiliado(ManejadorComando[AprobarAfiliado, ResultadoAfiliadoAprobado]):
    """
    Manejador para el comando AprobarAfiliado
    Principio de Responsabilidad Única
    """
    
    def __init__(
        self, 
        repositorio_afiliados: RepositorioAfiliados,
        servicio_outbox: ServicioOutbox
    ):
        self._repositorio = repositorio_afiliados
        self._outbox = servicio_outbox
    
    async def handle(self, comando: AprobarAfiliado) -> ResultadoAfiliadoAprobado:
        """Maneja la aprobación de un afiliado"""
        
        # Obtener afiliado
        afiliado = await self._repositorio.obtener_por_id(comando.afiliado_id)
        if not afiliado:
            raise ValueError(f"No se encontró afiliado con ID {comando.afiliado_id}")
        
        # Aprobar afiliado
        afiliado.aprobar(comando.usuario_responsable, comando.observaciones)
        
        # Actualizar en repositorio
        await self._repositorio.actualizar(afiliado)
        
        # Crear evento de integración
        evento_integracion = AfiliadoAprobadoIntegracion(
            afiliado_id=afiliado.id,
            documento_numero=afiliado.documento.numero,
            nombre_completo=afiliado.datos_personales.nombre_completo,
            email=afiliado.datos_personales.email,
            fecha_aprobacion=datetime.now()
        )
        
        # Guardar eventos en outbox
        eventos_completos = afiliado.eventos + [evento_integracion]
        await self._outbox.guardar_eventos_agregado(afiliado.id, eventos_completos)
        
        return ResultadoAfiliadoAprobado(
            exitoso=True,
            afiliado_id=afiliado.id,
            fecha_aprobacion=datetime.now()
        )

class ManejadorDesactivarAfiliado(ManejadorComando[DesactivarAfiliado, ResultadoAfiliadoDesactivado]):
    """
    Manejador para el comando DesactivarAfiliado
    Principio de Responsabilidad Única
    """
    
    def __init__(
        self, 
        repositorio_afiliados: RepositorioAfiliados,
        servicio_outbox: ServicioOutbox
    ):
        self._repositorio = repositorio_afiliados
        self._outbox = servicio_outbox
    
    async def handle(self, comando: DesactivarAfiliado) -> ResultadoAfiliadoDesactivado:
        """Maneja la desactivación de un afiliado"""
        
        # Obtener afiliado
        afiliado = await self._repositorio.obtener_por_id(comando.afiliado_id)
        if not afiliado:
            raise ValueError(f"No se encontró afiliado con ID {comando.afiliado_id}")
        
        # Desactivar afiliado
        afiliado.desactivar(comando.usuario_responsable, comando.motivo)
        
        # Actualizar en repositorio
        await self._repositorio.actualizar(afiliado)
        
        # Crear evento de integración
        evento_integracion = AfiliadoDesactivadoIntegracion(
            afiliado_id=afiliado.id,
            documento_numero=afiliado.documento.numero,
            motivo=comando.motivo,
            fecha_desactivacion=datetime.now()
        )
        
        # Guardar eventos en outbox
        eventos_completos = afiliado.eventos + [evento_integracion]
        await self._outbox.guardar_eventos_agregado(afiliado.id, eventos_completos)
        
        return ResultadoAfiliadoDesactivado(
            exitoso=True,
            afiliado_id=afiliado.id,
            fecha_desactivacion=datetime.now()
        )

class ManejadorActualizarDatosAfiliado(ManejadorComando[ActualizarDatosAfiliado, ResultadoDatosActualizados]):
    """
    Manejador para el comando ActualizarDatosAfiliado
    Principio de Responsabilidad Única
    """
    
    def __init__(
        self, 
        repositorio_afiliados: RepositorioAfiliados,
        servicio_outbox: ServicioOutbox
    ):
        self._repositorio = repositorio_afiliados
        self._outbox = servicio_outbox
    
    async def handle(self, comando: ActualizarDatosAfiliado) -> ResultadoDatosActualizados:
        """Maneja la actualización de datos de un afiliado"""
        
        # Obtener afiliado
        afiliado = await self._repositorio.obtener_por_id(comando.afiliado_id)
        if not afiliado:
            raise ValueError(f"No se encontró afiliado con ID {comando.afiliado_id}")
        
        # Verificar que el nuevo email no esté en uso (si cambió)
        if comando.email != afiliado.datos_personales.email:
            if await self._repositorio.existe_email(comando.email):
                raise ValueError(f"Ya existe un afiliado con email {comando.email}")
        
        # Crear nuevos datos personales
        datos_anteriores = afiliado.datos_personales
        nuevos_datos = DatosPersonales(
            nombres=comando.nombres,
            apellidos=comando.apellidos,
            email=comando.email,
            telefono=comando.telefono,
            fecha_nacimiento=comando.fecha_nacimiento
        )
        
        # Actualizar datos
        afiliado.actualizar_datos_personales(nuevos_datos, comando.usuario_responsable)
        
        # Actualizar en repositorio
        await self._repositorio.actualizar(afiliado)
        
        # Crear evento de integración si cambió el email
        eventos_integracion = []
        if comando.email != datos_anteriores.email:
            evento_integracion = DatosAfiliadoActualizadosIntegracion(
                afiliado_id=afiliado.id,
                documento_numero=afiliado.documento.numero,
                email_anterior=datos_anteriores.email,
                email_nuevo=nuevos_datos.email,
                nombre_completo_nuevo=nuevos_datos.nombre_completo,
                fecha_actualizacion=datetime.now()
            )
            eventos_integracion.append(evento_integracion)
        
        # Guardar eventos en outbox
        eventos_completos = afiliado.eventos + eventos_integracion
        await self._outbox.guardar_eventos_agregado(afiliado.id, eventos_completos)
        
        return ResultadoDatosActualizados(
            exitoso=True,
            afiliado_id=afiliado.id,
            fecha_actualizacion=datetime.now()
        )