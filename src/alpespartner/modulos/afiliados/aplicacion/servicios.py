"""
Servicios de aplicación para el módulo de Afiliados
Coordinan operaciones complejas y casos de uso de negocio
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal

from alpespartner.seedwork.aplicacion.servicios import ServicioAplicacion
from alpespartner.seedwork.infraestructura.uow import UnidadTrabajo

from ..dominio.repositorios import RepositorioAfiliados
from ..dominio.servicios import ServicioDominioAfiliados
from ..dominio.excepciones import AfiliadoNoExiste, AfiliadoInactivoParaOperacion

from .comandos import (
    ComandoCrearAfiliado, ComandoActivarAfiliado, ComandoActualizarDatosBancarios,
    ComandoAgregarReferencia
)
from .queries import (
    QueryObtenerAfiliado, QueryBuscarAfiliados, QueryObtenerEstadisticasAfiliados,
    QueryCalcularComisiones
)


class ServicioAplicacionAfiliados(ServicioAplicacion):
    """
    Servicio de aplicación para coordinar operaciones de Afiliados.
    Maneja casos de uso complejos que involucran múltiples operaciones.
    """
    
    def __init__(self, uow: UnidadTrabajo):
        self._uow = uow
    
    def registrar_afiliado_completo(
        self,
        datos_personales: Dict[str, Any],
        datos_contacto: Dict[str, Any],
        datos_documento: Dict[str, Any],
        configuracion_negocio: Dict[str, Any],
        datos_bancarios: Optional[Dict[str, Any]] = None,
        afiliado_referente_id: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Registra un afiliado completo con todos sus datos y lo activa.
        
        Args:
            datos_personales: Nombres, apellidos, fecha nacimiento
            datos_contacto: Email, teléfono, dirección, etc.
            datos_documento: Tipo y número de documento
            configuracion_negocio: Tipo afiliado, comisiones
            datos_bancarios: Datos bancarios opcionales
            afiliado_referente_id: ID del afiliado referente opcional
            correlation_id: ID de correlación
            
        Returns:
            Dict con datos del afiliado creado y activado
        """
        with self._uow:
            # Paso 1: Crear afiliado
            comando_crear = ComandoCrearAfiliado(
                nombres=datos_personales['nombres'],
                apellidos=datos_personales['apellidos'],
                fecha_nacimiento=datos_personales.get('fecha_nacimiento'),
                tipo_documento=datos_documento['tipo'],
                numero_documento=datos_documento['numero'],
                fecha_expedicion_documento=datos_documento.get('fecha_expedicion'),
                email=datos_contacto['email'],
                telefono=datos_contacto.get('telefono'),
                direccion=datos_contacto.get('direccion'),
                ciudad=datos_contacto.get('ciudad'),
                pais=datos_contacto.get('pais'),
                tipo_afiliado=configuracion_negocio['tipo_afiliado'],
                porcentaje_comision_base=configuracion_negocio['porcentaje_comision_base'],
                porcentaje_comision_premium=configuracion_negocio.get('porcentaje_comision_premium'),
                monto_minimo_comision=configuracion_negocio.get('monto_minimo_comision'),
                afiliado_referente_id=afiliado_referente_id,
                correlation_id=correlation_id
            )
            
            # Ejecutar creación
            from .handlers import crear_afiliado_handler
            crear_afiliado_handler(comando_crear, self._uow)
            
            # Obtener el afiliado creado
            repositorio: RepositorioAfiliados = self._uow._repositorio_afiliados
            afiliado = repositorio.obtener_por_documento(
                datos_documento['tipo'], 
                datos_documento['numero']
            )
            
            if not afiliado:
                raise Exception("Error creando afiliado")
            
            # Paso 2: Activar afiliado
            comando_activar = ComandoActivarAfiliado(
                afiliado_id=afiliado.id,
                correlation_id=correlation_id
            )
            
            from .handlers import activar_afiliado_handler
            activar_afiliado_handler(comando_activar, self._uow)
            
            # Paso 3: Agregar datos bancarios si se proporcionan
            if datos_bancarios:
                comando_bancarios = ComandoActualizarDatosBancarios(
                    afiliado_id=afiliado.id,
                    banco=datos_bancarios['banco'],
                    tipo_cuenta=datos_bancarios['tipo_cuenta'],
                    numero_cuenta=datos_bancarios['numero_cuenta'],
                    titular_cuenta=datos_bancarios['titular_cuenta'],
                    correlation_id=correlation_id
                )
                
                from .handlers import actualizar_datos_bancarios_handler
                actualizar_datos_bancarios_handler(comando_bancarios, self._uow)
            
            self._uow.commit()
            
            # Retornar datos del afiliado completo
            query_afiliado = QueryObtenerAfiliado(afiliado_id=afiliado.id)
            from .query_handlers import obtener_afiliado_handler
            return obtener_afiliado_handler(query_afiliado, self._uow)
    
    def procesar_referencia_masiva(
        self,
        afiliado_referente_id: str,
        afiliados_referidos_ids: List[str],
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Procesa múltiples referencias de afiliados en lote.
        
        Args:
            afiliado_referente_id: ID del afiliado que hace las referencias
            afiliados_referidos_ids: Lista de IDs de afiliados a referenciar
            correlation_id: ID de correlación
            
        Returns:
            Dict con resultados del procesamiento
        """
        with self._uow:
            repositorio: RepositorioAfiliados = self._uow._repositorio_afiliados
            servicio_dominio = ServicioDominioAfiliados(repositorio)
            
            # Validar afiliado referente
            afiliado_referente = repositorio.obtener_por_id(afiliado_referente_id)
            if not afiliado_referente:
                raise AfiliadoNoExiste(afiliado_referente_id)
            
            resultados = {
                'exitosos': [],
                'fallidos': [],
                'total_procesados': 0
            }
            
            for afiliado_referido_id in afiliados_referidos_ids:
                try:
                    # Validar que puede ser referido
                    if not servicio_dominio.puede_referenciar_afiliado(afiliado_referido_id):
                        resultados['fallidos'].append({
                            'afiliado_id': afiliado_referido_id,
                            'error': 'Afiliado no puede ser referido'
                        })
                        continue
                    
                    # Verificar referencia circular
                    servicio_dominio.verificar_referencia_circular(
                        afiliado_referido_id, afiliado_referente_id
                    )
                    
                    # Crear comando y ejecutar
                    comando = ComandoAgregarReferencia(
                        afiliado_referente_id=afiliado_referente_id,
                        afiliado_referido_id=afiliado_referido_id,
                        correlation_id=correlation_id
                    )
                    
                    from .handlers import agregar_referencia_handler
                    agregar_referencia_handler(comando, self._uow)
                    
                    resultados['exitosos'].append(afiliado_referido_id)
                    
                except Exception as e:
                    resultados['fallidos'].append({
                        'afiliado_id': afiliado_referido_id,
                        'error': str(e)
                    })
                
                resultados['total_procesados'] += 1
            
            self._uow.commit()
            return resultados
    
    def generar_reporte_comisiones(
        self,
        fecha_desde: datetime,
        fecha_hasta: datetime,
        tipos_afiliado: Optional[List[str]] = None,
        solo_activos: bool = True
    ) -> Dict[str, Any]:
        """
        Genera un reporte detallado de comisiones de afiliados.
        
        Args:
            fecha_desde: Fecha inicio del período
            fecha_hasta: Fecha fin del período
            tipos_afiliado: Lista de tipos a incluir (opcional)
            solo_activos: Si incluir solo afiliados activos
            
        Returns:
            Dict con reporte de comisiones
        """
        with self._uow:
            repositorio: RepositorioAfiliados = self._uow._repositorio_afiliados
            servicio_dominio = ServicioDominioAfiliados(repositorio)
            
            # Construir filtros
            filtros = {
                'fecha_desde': fecha_desde,
                'fecha_hasta': fecha_hasta
            }
            
            if solo_activos:
                filtros['estado'] = 'ACTIVO'
            
            # Obtener afiliados
            afiliados = repositorio.buscar_con_filtros(filtros=filtros, limite=1000)
            
            reporte = {
                'periodo': {
                    'fecha_desde': fecha_desde.isoformat(),
                    'fecha_hasta': fecha_hasta.isoformat()
                },
                'resumen': {
                    'total_afiliados': len(afiliados),
                    'por_tipo': {},
                    'comisiones_simuladas': {}
                },
                'detalle_afiliados': []
            }
            
            # Simular comisiones con montos estándar para el reporte
            montos_simulacion = [Decimal('100000'), Decimal('500000'), Decimal('1000000')]
            
            for afiliado in afiliados:
                # Contadores por tipo
                tipo_afiliado = afiliado.tipo_afiliado.value
                if tipo_afiliado not in reporte['resumen']['por_tipo']:
                    reporte['resumen']['por_tipo'][tipo_afiliado] = 0
                reporte['resumen']['por_tipo'][tipo_afiliado] += 1
                
                # Calcular comisiones simuladas
                comisiones_afiliado = {}
                for monto in montos_simulacion:
                    comision = servicio_dominio.calcular_comisiones_escalonadas(afiliado, monto)
                    comisiones_afiliado[f'monto_{monto}'] = float(comision)
                
                # Detalle del afiliado
                detalle = {
                    'id': afiliado.id,
                    'nombres': f"{afiliado.datos_personales.nombres} {afiliado.datos_personales.apellidos}",
                    'tipo_afiliado': tipo_afiliado,
                    'estado': afiliado.estado.value,
                    'configuracion_comisiones': {
                        'porcentaje_base': float(afiliado.configuracion_comisiones.porcentaje_base),
                        'porcentaje_premium': float(afiliado.configuracion_comisiones.porcentaje_premium) if afiliado.configuracion_comisiones.porcentaje_premium else None
                    },
                    'comisiones_simuladas': comisiones_afiliado,
                    'referencias_count': len(afiliado.referencias),
                    'tiene_referente': afiliado.afiliado_referente_id is not None
                }
                
                reporte['detalle_afiliados'].append(detalle)
            
            # Calcular promedios de comisiones por tipo
            for tipo in reporte['resumen']['por_tipo']:
                afiliados_tipo = [a for a in afiliados if a.tipo_afiliado.value == tipo]
                if afiliados_tipo:
                    # Promedio para monto estándar de 500k
                    comisiones_tipo = [
                        servicio_dominio.calcular_comisiones_escalonadas(a, Decimal('500000'))
                        for a in afiliados_tipo
                    ]
                    promedio = sum(comisiones_tipo) / len(comisiones_tipo)
                    
                    if tipo not in reporte['resumen']['comisiones_simuladas']:
                        reporte['resumen']['comisiones_simuladas'][tipo] = {}
                    
                    reporte['resumen']['comisiones_simuladas'][tipo]['promedio_500k'] = float(promedio)
            
            return reporte
    
    def obtener_dashboard_afiliado(self, afiliado_id: str) -> Dict[str, Any]:
        """
        Obtiene datos completos para dashboard de un afiliado.
        
        Args:
            afiliado_id: ID del afiliado
            
        Returns:
            Dict con datos completos del dashboard
        """
        with self._uow:
            repositorio: RepositorioAfiliados = self._uow._repositorio_afiliados
            servicio_dominio = ServicioDominioAfiliados(repositorio)
            
            # Obtener afiliado principal
            afiliado = repositorio.obtener_por_id(afiliado_id)
            if not afiliado:
                raise AfiliadoNoExiste(afiliado_id)
            
            # Datos básicos del afiliado
            query_afiliado = QueryObtenerAfiliado(afiliado_id=afiliado_id)
            from .query_handlers import obtener_afiliado_handler
            datos_basicos = obtener_afiliado_handler(query_afiliado, self._uow)
            
            # Obtener referidos activos
            referidos_activos = servicio_dominio.obtener_afiliados_referidos_activos(afiliado_id)
            
            # Calcular comisiones ejemplo
            query_comisiones = QueryCalcularComisiones(
                afiliado_id=afiliado_id,
                monto_transaccion='500000',  # Monto ejemplo
                incluir_comision_referencia=True
            )
            from .query_handlers import calcular_comisiones_handler
            ejemplo_comisiones = calcular_comisiones_handler(query_comisiones, self._uow)
            
            # Estadísticas del período actual (último mes)
            fecha_hasta = datetime.now()
            fecha_desde = fecha_hasta - timedelta(days=30)
            
            estadisticas_generales = repositorio.obtener_estadisticas(fecha_desde, fecha_hasta)
            
            dashboard = {
                'afiliado': datos_basicos,
                'referidos': {
                    'activos': len(referidos_activos),
                    'detalle': [
                        {
                            'id': ref.id,
                            'nombres': f"{ref.datos_personales.nombres} {ref.datos_personales.apellidos}",
                            'estado': ref.estado.value,
                            'fecha_creacion': ref.fecha_creacion.isoformat() if ref.fecha_creacion else None
                        }
                        for ref in referidos_activos[:10]  # Primeros 10
                    ]
                },
                'comisiones_ejemplo': ejemplo_comisiones,
                'estadisticas_contexto': {
                    'total_afiliados_sistema': estadisticas_generales['total_afiliados'],
                    'posicion_relativa': 'premium' if afiliado.tipo_afiliado.value == 'PREMIUM' else 'estándar'
                },
                'fecha_consulta': datetime.now().isoformat()
            }
            
            return dashboard