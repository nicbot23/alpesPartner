"""
Excepciones específicas del dominio de Afiliados
Manejan los casos de error del negocio
"""

from alpespartner.seedwork.dominio.excepciones import ExcepcionDominio


class ExcepcionAfiliados(ExcepcionDominio):
    """Excepción base para el dominio de afiliados."""
    pass


class AfiliadoNoExiste(ExcepcionAfiliados):
    """Se lanza cuando se intenta acceder a un afiliado que no existe."""
    
    def __init__(self, afiliado_id: str):
        super().__init__(f"El afiliado con ID {afiliado_id} no existe")


class DocumentoYaRegistrado(ExcepcionAfiliados):
    """Se lanza cuando se intenta registrar un documento ya existente."""
    
    def __init__(self, tipo_documento: str, numero_documento: str):
        super().__init__(
            f"El documento {tipo_documento} {numero_documento} ya está registrado"
        )


class EmailYaRegistrado(ExcepcionAfiliados):
    """Se lanza cuando se intenta registrar un email ya existente."""
    
    def __init__(self, email: str):
        super().__init__(f"El email {email} ya está registrado")


class CodigoReferenciaYaExiste(ExcepcionAfiliados):
    """Se lanza cuando se intenta asignar un código de referencia ya existente."""
    
    def __init__(self, codigo_referencia: str):
        super().__init__(f"El código de referencia {codigo_referencia} ya existe")


class TransicionEstadoInvalida(ExcepcionAfiliados):
    """Se lanza cuando se intenta hacer una transición de estado inválida."""
    
    def __init__(self, estado_actual: str, estado_destino: str):
        super().__init__(
            f"No se puede cambiar de estado {estado_actual} a {estado_destino}"
        )


class AfiliadoYaSuspendido(ExcepcionAfiliados):
    """Se lanza cuando se intenta suspender un afiliado ya suspendido."""
    
    def __init__(self, afiliado_id: str):
        super().__init__(f"El afiliado {afiliado_id} ya está suspendido")


class AfiliadoYaBloqueado(ExcepcionAfiliados):
    """Se lanza cuando se intenta bloquear un afiliado ya bloqueado."""
    
    def __init__(self, afiliado_id: str):
        super().__init__(f"El afiliado {afiliado_id} ya está bloqueado")


class AfiliadoInactivoParaOperacion(ExcepcionAfiliados):
    """Se lanza cuando se intenta realizar una operación con un afiliado inactivo."""
    
    def __init__(self, afiliado_id: str, estado_actual: str):
        super().__init__(
            f"No se puede realizar la operación. El afiliado {afiliado_id} "
            f"está en estado {estado_actual}"
        )


class ReferenciaCircular(ExcepcionAfiliados):
    """Se lanza cuando se detecta una referencia circular."""
    
    def __init__(self, afiliado_id: str, afiliado_referente_id: str):
        super().__init__(
            f"Se detectó una referencia circular entre {afiliado_id} "
            f"y {afiliado_referente_id}"
        )


class AfiliadoYaReferido(ExcepcionAfiliados):
    """Se lanza cuando se intenta referenciar un afiliado ya referido."""
    
    def __init__(self, afiliado_referido_id: str):
        super().__init__(f"El afiliado {afiliado_referido_id} ya ha sido referido")


class ComisionInvalida(ExcepcionAfiliados):
    """Se lanza cuando se configuran comisiones inválidas."""
    
    def __init__(self, mensaje: str):
        super().__init__(f"Configuración de comisión inválida: {mensaje}")


class DatosBancariosIncompletos(ExcepcionAfiliados):
    """Se lanza cuando los datos bancarios están incompletos."""
    
    def __init__(self):
        super().__init__(
            "Los datos bancarios deben incluir banco, tipo de cuenta, "
            "número de cuenta y titular"
        )


class TipoAfiliadoInvalido(ExcepcionAfiliados):
    """Se lanza cuando se especifica un tipo de afiliado inválido."""
    
    def __init__(self, tipo_afiliado: str):
        super().__init__(f"El tipo de afiliado '{tipo_afiliado}' no es válido")


class DocumentoInvalido(ExcepcionAfiliados):
    """Se lanza cuando el formato del documento es inválido."""
    
    def __init__(self, tipo_documento: str, numero_documento: str):
        super().__init__(
            f"El formato del documento {tipo_documento} {numero_documento} es inválido"
        )