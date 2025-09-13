"""
Handlers de comandos para el módulo de Afiliados
Coordinan la lógica de aplicación y orquestan las operaciones del dominio
"""

from typing import Optional
from datetime import datetime
from decimal import Decimal

from alpespartner.seedwork.aplicacion.handlers import Handler
from alpespartner.seedwork.aplicacion.comandos import ejecutar_commando as comando
from alpespartner.seedwork.infraestructura.uow import UnidadTrabajo

from ..dominio.agregados import Afiliado
from ..dominio.repositorios import RepositorioAfiliados
from ..dominio.fabricas import FabricaAfiliados
from ..dominio.servicios import ServicioDominioAfiliados
from ..dominio.excepciones import (
    AfiliadoNoExiste, DocumentoYaRegistrado, EmailYaRegistrado,
    ComisionInvalida, AfiliadoInactivoParaOperacion
)
from ..infraestructura.repositorios import RepositorioAfiliadosSQLAlchemy

from .comandos import (
    ComandoCrearAfiliado, ComandoActivarAfiliado, ComandoDesactivarAfiliado,
    ComandoSuspenderAfiliado, ComandoBloquearAfiliado, ComandoActualizarDatosBancarios,
    ComandoActualizarConfiguracionComisiones, ComandoAgregarReferencia,
    ComandoActualizarDatosPersonales, ComandoActualizarMetadatos, ComandoValidarAfiliado
)


@Handler(ComandoCrearAfiliado)
def crear_afiliado_handler(comando: ComandoCrearAfiliado, uow: UnidadTrabajo):
    """
    Handler para crear un nuevo afiliado.
    
    Args:
        comando: Comando con datos del afiliado a crear
        uow: Unidad de trabajo para manejo de transacciones
    """
    with uow:
        # Obtener repositorio y servicio de dominio
        repositorio: RepositorioAfiliados = uow._repositorio_afiliados
        servicio_dominio = ServicioDominioAfiliados(repositorio)
        
        # Validar unicidad de documento y email
        servicio_dominio.verificar_unicidad_documento(
            comando.tipo_documento, 
            comando.numero_documento
        )
        servicio_dominio.verificar_unicidad_email(comando.email)
        
        # Validar configuración de comisiones
        servicio_dominio.validar_configuracion_comisiones(
            comando.porcentaje_comision_base,
            comando.porcentaje_comision_premium,
            comando.monto_minimo_comision
        )
        
        # Verificar afiliado referente si se especifica
        if comando.afiliado_referente_id:
            afiliado_referente = repositorio.obtener_por_id(comando.afiliado_referente_id)
            if not afiliado_referente:
                raise AfiliadoNoExiste(comando.afiliado_referente_id)
        
        # Crear el afiliado usando la fábrica
        afiliado = FabricaAfiliados.crear_afiliado(
            nombres=comando.nombres,
            apellidos=comando.apellidos,
            email=comando.email,
            tipo_documento=comando.tipo_documento,
            numero_documento=comando.numero_documento,
            tipo_afiliado=comando.tipo_afiliado,
            porcentaje_comision_base=comando.porcentaje_comision_base,
            telefono=comando.telefono,
            direccion=comando.direccion,
            ciudad=comando.ciudad,
            pais=comando.pais,
            fecha_nacimiento=comando.fecha_nacimiento,
            fecha_expedicion_documento=comando.fecha_expedicion_documento,
            porcentaje_comision_premium=comando.porcentaje_comision_premium,
            monto_minimo_comision=comando.monto_minimo_comision,
            afiliado_referente_id=comando.afiliado_referente_id,
            metadata=comando.metadata,
            correlation_id=comando.correlation_id,
            causation_id=comando.causation_id
        )
        
        # Guardar en repositorio
        repositorio.guardar(afiliado)
        uow.commit()


@Handler(ComandoActivarAfiliado)
def activar_afiliado_handler(comando: ComandoActivarAfiliado, uow: UnidadTrabajo):
    """
    Handler para activar un afiliado.
    
    Args:
        comando: Comando con ID del afiliado a activar
        uow: Unidad de trabajo
    """
    with uow:
        repositorio: RepositorioAfiliados = uow._repositorio_afiliados
        servicio_dominio = ServicioDominioAfiliados(repositorio)
        
        # Obtener el afiliado
        afiliado = repositorio.obtener_por_id(comando.afiliado_id)
        if not afiliado:
            raise AfiliadoNoExiste(comando.afiliado_id)
        
        # Generar código de referencia si no tiene
        codigo_referencia = comando.codigo_referencia
        if not codigo_referencia:
            base = f"{afiliado.datos_personales.nombres}{afiliado.datos_personales.apellidos}"
            codigo_referencia = servicio_dominio.generar_codigo_referencia_unico(base)
        
        # Activar afiliado
        afiliado.activar(
            codigo_referencia=codigo_referencia,
            correlation_id=comando.correlation_id,
            causation_id=comando.causation_id
        )
        
        repositorio.guardar(afiliado)
        uow.commit()


@Handler(ComandoDesactivarAfiliado)
def desactivar_afiliado_handler(comando: ComandoDesactivarAfiliado, uow: UnidadTrabajo):
    """
    Handler para desactivar un afiliado.
    
    Args:
        comando: Comando con ID del afiliado a desactivar
        uow: Unidad de trabajo
    """
    with uow:
        repositorio: RepositorioAfiliados = uow._repositorio_afiliados
        
        afiliado = repositorio.obtener_por_id(comando.afiliado_id)
        if not afiliado:
            raise AfiliadoNoExiste(comando.afiliado_id)
        
        afiliado.desactivar(
            correlation_id=comando.correlation_id,
            causation_id=comando.causation_id
        )
        
        repositorio.guardar(afiliado)
        uow.commit()


@Handler(ComandoSuspenderAfiliado)
def suspender_afiliado_handler(comando: ComandoSuspenderAfiliado, uow: UnidadTrabajo):
    """
    Handler para suspender un afiliado.
    
    Args:
        comando: Comando con datos de suspensión
        uow: Unidad de trabajo
    """
    with uow:
        repositorio: RepositorioAfiliados = uow._repositorio_afiliados
        
        afiliado = repositorio.obtener_por_id(comando.afiliado_id)
        if not afiliado:
            raise AfiliadoNoExiste(comando.afiliado_id)
        
        afiliado.suspender(
            correlation_id=comando.correlation_id,
            causation_id=comando.causation_id
        )
        
        repositorio.guardar(afiliado)
        uow.commit()


@Handler(ComandoBloquearAfiliado)
def bloquear_afiliado_handler(comando: ComandoBloquearAfiliado, uow: UnidadTrabajo):
    """
    Handler para bloquear un afiliado.
    
    Args:
        comando: Comando con datos de bloqueo
        uow: Unidad de trabajo
    """
    with uow:
        repositorio: RepositorioAfiliados = uow._repositorio_afiliados
        
        afiliado = repositorio.obtener_por_id(comando.afiliado_id)
        if not afiliado:
            raise AfiliadoNoExiste(comando.afiliado_id)
        
        afiliado.bloquear(
            correlation_id=comando.correlation_id,
            causation_id=comando.causation_id
        )
        
        repositorio.guardar(afiliado)
        uow.commit()


@Handler(ComandoActualizarDatosBancarios)
def actualizar_datos_bancarios_handler(comando: ComandoActualizarDatosBancarios, uow: UnidadTrabajo):
    """
    Handler para actualizar datos bancarios de un afiliado.
    
    Args:
        comando: Comando con nuevos datos bancarios
        uow: Unidad de trabajo
    """
    with uow:
        repositorio: RepositorioAfiliados = uow._repositorio_afiliados
        
        afiliado = repositorio.obtener_por_id(comando.afiliado_id)
        if not afiliado:
            raise AfiliadoNoExiste(comando.afiliado_id)
        
        afiliado.actualizar_datos_bancarios(
            banco=comando.banco,
            tipo_cuenta=comando.tipo_cuenta,
            numero_cuenta=comando.numero_cuenta,
            titular=comando.titular_cuenta,
            correlation_id=comando.correlation_id,
            causation_id=comando.causation_id
        )
        
        repositorio.guardar(afiliado)
        uow.commit()


@Handler(ComandoActualizarConfiguracionComisiones)
def actualizar_configuracion_comisiones_handler(
    comando: ComandoActualizarConfiguracionComisiones, 
    uow: UnidadTrabajo
):
    """
    Handler para actualizar configuración de comisiones.
    
    Args:
        comando: Comando con nueva configuración
        uow: Unidad de trabajo
    """
    with uow:
        repositorio: RepositorioAfiliados = uow._repositorio_afiliados
        servicio_dominio = ServicioDominioAfiliados(repositorio)
        
        afiliado = repositorio.obtener_por_id(comando.afiliado_id)
        if not afiliado:
            raise AfiliadoNoExiste(comando.afiliado_id)
        
        # Construir nueva configuración
        nueva_config = {
            'porcentaje_base': comando.porcentaje_comision_base or afiliado.configuracion_comisiones.porcentaje_base,
            'porcentaje_premium': comando.porcentaje_comision_premium or afiliado.configuracion_comisiones.porcentaje_premium,
            'monto_minimo': comando.monto_minimo_comision or afiliado.configuracion_comisiones.monto_minimo
        }
        
        # Validar nueva configuración
        servicio_dominio.validar_configuracion_comisiones(
            nueva_config['porcentaje_base'],
            nueva_config['porcentaje_premium'],
            nueva_config['monto_minimo']
        )
        
        afiliado.actualizar_configuracion_comisiones(
            **nueva_config,
            correlation_id=comando.correlation_id,
            causation_id=comando.causation_id
        )
        
        repositorio.guardar(afiliado)
        uow.commit()


@Handler(ComandoAgregarReferencia)
def agregar_referencia_handler(comando: ComandoAgregarReferencia, uow: UnidadTrabajo):
    """
    Handler para agregar una referencia entre afiliados.
    
    Args:
        comando: Comando con datos de la referencia
        uow: Unidad de trabajo
    """
    with uow:
        repositorio: RepositorioAfiliados = uow._repositorio_afiliados
        servicio_dominio = ServicioDominioAfiliados(repositorio)
        
        # Obtener afiliado referente
        afiliado_referente = repositorio.obtener_por_id(comando.afiliado_referente_id)
        if not afiliado_referente:
            raise AfiliadoNoExiste(comando.afiliado_referente_id)
        
        # Validar que el afiliado referido existe y puede ser referido
        if not servicio_dominio.puede_referenciar_afiliado(comando.afiliado_referido_id):
            raise AfiliadoInactivoParaOperacion(comando.afiliado_referido_id, "no puede ser referido")
        
        # Verificar referencia circular
        servicio_dominio.verificar_referencia_circular(
            comando.afiliado_referido_id, 
            comando.afiliado_referente_id
        )
        
        # Agregar referencia
        afiliado_referente.agregar_referencia(
            afiliado_referido_id=comando.afiliado_referido_id,
            fecha_referencia=comando.fecha_referencia or datetime.now(),
            correlation_id=comando.correlation_id,
            causation_id=comando.causation_id
        )
        
        repositorio.guardar(afiliado_referente)
        uow.commit()


@Handler(ComandoActualizarDatosPersonales)
def actualizar_datos_personales_handler(comando: ComandoActualizarDatosPersonales, uow: UnidadTrabajo):
    """
    Handler para actualizar datos personales de un afiliado.
    
    Args:
        comando: Comando con nuevos datos personales
        uow: Unidad de trabajo
    """
    with uow:
        repositorio: RepositorioAfiliados = uow._repositorio_afiliados
        
        afiliado = repositorio.obtener_por_id(comando.afiliado_id)
        if not afiliado:
            raise AfiliadoNoExiste(comando.afiliado_id)
        
        afiliado.actualizar_datos_contacto(
            telefono=comando.telefono,
            direccion=comando.direccion,
            ciudad=comando.ciudad,
            pais=comando.pais,
            correlation_id=comando.correlation_id,
            causation_id=comando.causation_id
        )
        
        repositorio.guardar(afiliado)
        uow.commit()


@Handler(ComandoActualizarMetadatos)
def actualizar_metadatos_handler(comando: ComandoActualizarMetadatos, uow: UnidadTrabajo):
    """
    Handler para actualizar metadatos de un afiliado.
    
    Args:
        comando: Comando con nuevos metadatos
        uow: Unidad de trabajo
    """
    with uow:
        repositorio: RepositorioAfiliados = uow._repositorio_afiliados
        
        afiliado = repositorio.obtener_por_id(comando.afiliado_id)
        if not afiliado:
            raise AfiliadoNoExiste(comando.afiliado_id)
        
        # Actualizar metadatos (asumiendo que hay un método en el agregado)
        afiliado._metadata.datos.update(comando.metadata)
        afiliado._marcar_como_modificado()
        
        repositorio.guardar(afiliado)
        uow.commit()


@Handler(ComandoValidarAfiliado)
def validar_afiliado_handler(comando: ComandoValidarAfiliado, uow: UnidadTrabajo):
    """
    Handler para validar un afiliado.
    
    Args:
        comando: Comando con datos de validación
        uow: Unidad de trabajo
    """
    with uow:
        repositorio: RepositorioAfiliados = uow._repositorio_afiliados
        
        afiliado = repositorio.obtener_por_id(comando.afiliado_id)
        if not afiliado:
            raise AfiliadoNoExiste(comando.afiliado_id)
        
        # Marcar validaciones realizadas en metadatos
        validaciones_metadata = {
            'validaciones': comando.validaciones,
            'fecha_validacion': datetime.now().isoformat(),
            'observaciones': comando.observaciones
        }
        
        afiliado._metadata.datos.update({'ultima_validacion': validaciones_metadata})
        afiliado._marcar_como_modificado()
        
        repositorio.guardar(afiliado)
        uow.commit()