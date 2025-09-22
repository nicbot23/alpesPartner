from campanias.seedwork.aplicacion.comandos import Comando, ComandoHandler
from campanias.seedwork.aplicacion.comandos import ejecutar_commando as comando
from dataclasses import dataclass
from typing import Optional
import uuid

@dataclass
class RegistrarAfiliadoEnCampana(Comando):
    """Comando para registrar un afiliado en una campaña específica"""
    id_campana: str
    id_afiliado: str
    codigo_afiliado: str
    nombre_afiliado: str
    email_afiliado: str
    tipo_afiliado: str  # INDIVIDUAL, EMPRESA, INFLUENCER
    nivel_comision: str  # BASICO, PREMIUM, VIP
    fecha_registro: str = None
    condiciones_especiales: Optional[str] = None

@dataclass
class ValidarAfiliadoParaCampana(Comando):
    """Comando para validar que un afiliado cumple requisitos de la campaña"""
    id_campana: str
    id_afiliado: str
    criterios_validacion: dict

@dataclass
class ActivarAfiliadoEnCampana(Comando):
    """Comando para activar un afiliado en una campaña tras validación"""
    id_campana: str
    id_afiliado: str
    fecha_activacion: str = None

@dataclass
class DesactivarAfiliadoEnCampana(Comando):
    """Comando para desactivar un afiliado de una campaña"""
    id_campana: str
    id_afiliado: str
    razon: str
    fecha_desactivacion: str = None

@dataclass
class AsignarCodigoPromocionalAfiliado(Comando):
    """Comando para asignar código promocional único a afiliado"""
    id_campana: str
    id_afiliado: str
    codigo_promocional: str
    condiciones_uso: dict

class RegistrarAfiliadoEnCampanaHandler(ComandoHandler):
    def handle(self, comando: RegistrarAfiliadoEnCampana):
        """Procesa el registro de afiliado en campaña"""
        try:
            # TODO: Validar que la campaña existe y está activa
            # TODO: Validar que el afiliado no está ya registrado
            # TODO: Crear entidad AfiliadoCampana
            # TODO: Persistir en repositorio
            # TODO: Publicar evento AfiliadoRegistradoEnCampana
            # TODO: Iniciar proceso de validación automática
            
            print(f"Afiliado {comando.id_afiliado} registrado en campaña {comando.id_campana}")
            
        except Exception as e:
            # TODO: Publicar evento RegistroAfiliadoFallido
            raise e

class ValidarAfiliadoParaCampanaHandler(ComandoHandler):
    def handle(self, comando: ValidarAfiliadoParaCampana):
        """Valida si el afiliado cumple con los criterios de la campaña"""
        try:
            # TODO: Obtener información del afiliado
            # TODO: Obtener criterios de la campaña
            # TODO: Ejecutar validaciones (KYC, historial, etc.)
            # TODO: Publicar evento AfiliadoValidado o AfiliadoRechazado
            
            print(f"Validando afiliado {comando.id_afiliado} para campaña {comando.id_campana}")
            
        except Exception as e:
            # TODO: Publicar evento ValidacionAfiliadoFallida
            raise e

class ActivarAfiliadoEnCampanaHandler(ComandoHandler):
    def handle(self, comando: ActivarAfiliadoEnCampana):
        """Activa un afiliado validado en la campaña"""
        try:
            # TODO: Verificar que el afiliado está validado
            # TODO: Cambiar estado a ACTIVO
            # TODO: Generar código promocional único
            # TODO: Enviar notificación de activación
            # TODO: Publicar evento AfiliadoActivadoEnCampana
            
            print(f"Afiliado {comando.id_afiliado} activado en campaña {comando.id_campana}")
            
        except Exception as e:
            # TODO: Publicar evento ActivacionAfiliadoFallida
            raise e

class DesactivarAfiliadoEnCampanaHandler(ComandoHandler):
    def handle(self, comando: DesactivarAfiliadoEnCampana):
        """Desactiva un afiliado de la campaña"""
        try:
            # TODO: Cambiar estado a INACTIVO
            # TODO: Invalidar códigos promocionales
            # TODO: Calcular comisiones pendientes
            # TODO: Publicar evento AfiliadoDesactivadoEnCampana
            
            print(f"Afiliado {comando.id_afiliado} desactivado en campaña {comando.id_campana}")
            
        except Exception as e:
            raise e

class AsignarCodigoPromocionalAfiliadoHandler(ComandoHandler):
    def handle(self, comando: AsignarCodigoPromocionalAfiliado):
        """Asigna código promocional único al afiliado"""
        try:
            # TODO: Generar código único
            # TODO: Validar que no existe
            # TODO: Persistir código con condiciones
            # TODO: Publicar evento CodigoPromocionalAsignado
            
            print(f"Código {comando.codigo_promocional} asignado al afiliado {comando.id_afiliado}")
            
        except Exception as e:
            raise e

# Registrar todos los handlers
@comando.register(RegistrarAfiliadoEnCampana)
def ejecutar_registrar_afiliado(comando: RegistrarAfiliadoEnCampana):
    handler = RegistrarAfiliadoEnCampanaHandler()
    handler.handle(comando)

@comando.register(ValidarAfiliadoParaCampana)
def ejecutar_validar_afiliado(comando: ValidarAfiliadoParaCampana):
    handler = ValidarAfiliadoParaCampanaHandler()
    handler.handle(comando)

@comando.register(ActivarAfiliadoEnCampana)
def ejecutar_activar_afiliado(comando: ActivarAfiliadoEnCampana):
    handler = ActivarAfiliadoEnCampanaHandler()
    handler.handle(comando)

@comando.register(DesactivarAfiliadoEnCampana)
def ejecutar_desactivar_afiliado(comando: DesactivarAfiliadoEnCampana):
    handler = DesactivarAfiliadoEnCampanaHandler()
    handler.handle(comando)

@comando.register(AsignarCodigoPromocionalAfiliado)
def ejecutar_asignar_codigo(comando: AsignarCodigoPromocionalAfiliado):
    handler = AsignarCodigoPromocionalAfiliadoHandler()
    handler.handle(comando)