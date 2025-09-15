"""
Inicialización del módulo de dominio de Afiliados
"""

from .agregados import Afiliado
from .objetos_valor import (
    TipoAfiliado, EstadoAfiliado, DatosPersonales, DocumentoIdentidad,
    DatosContacto, DatosBancarios, ConfiguracionComisiones, MetadatosAfiliado,
    TipoDocumento, Referencia
)
from .eventos import (
    AffiliateCreated, AffiliateActivated, AffiliateSuspended, AffiliateBlocked,
    AffiliateDeactivated, AffiliateBankingDataUpdated, AffiliateCommissionConfigUpdated,
    AffiliateReferenceAdded, AffiliateValidated, AffiliateBankingDataValidated,
    AffiliateCommissionCalculated
)
from .repositorios import RepositorioAfiliados
from .fabricas import FabricaAfiliados
from .servicios import ServicioDominioAfiliados
from .excepciones import (
    ExcepcionAfiliados, AfiliadoNoExiste, DocumentoYaRegistrado,
    EmailYaRegistrado, CodigoReferenciaYaExiste, TransicionEstadoInvalida,
    AfiliadoYaSuspendido, AfiliadoYaBloqueado, AfiliadoInactivoParaOperacion,
    ReferenciaCircular, AfiliadoYaReferido, ComisionInvalida,
    DatosBancariosIncompletos, TipoAfiliadoInvalido, DocumentoInvalido
)

__all__ = [
    # Agregados
    'Afiliado',
    
    # Objetos de valor
    'TipoAfiliado',
    'EstadoAfiliado', 
    'DatosPersonales',
    'DocumentoIdentidad',
    'DatosContacto',
    'DatosBancarios',
    'ConfiguracionComisiones',
    'MetadatosAfiliado',
    'TipoDocumento',
    'Referencia',
    
    # Eventos de integración
    'AffiliateCreated',
    'AffiliateActivated',
    'AffiliateSuspended',
    'AffiliateBlocked',
    'AffiliateDeactivated',
    'AffiliateBankingDataUpdated',
    'AffiliateCommissionConfigUpdated',
    'AffiliateReferenceAdded',
    
    # Eventos internos
    'AffiliateValidated',
    'AffiliateBankingDataValidated',
    'AffiliateCommissionCalculated',
    
    # Repositorios
    'RepositorioAfiliados',
    
    # Fábricas
    'FabricaAfiliados',
    
    # Servicios
    'ServicioDominioAfiliados',
    
    # Excepciones
    'ExcepcionAfiliados',
    'AfiliadoNoExiste',
    'DocumentoYaRegistrado',
    'EmailYaRegistrado',
    'CodigoReferenciaYaExiste',
    'TransicionEstadoInvalida',
    'AfiliadoYaSuspendido',
    'AfiliadoYaBloqueado',
    'AfiliadoInactivoParaOperacion',
    'ReferenciaCircular',
    'AfiliadoYaReferido',
    'ComisionInvalida',
    'DatosBancariosIncompletos',
    'TipoAfiliadoInvalido',
    'DocumentoInvalido'
]
