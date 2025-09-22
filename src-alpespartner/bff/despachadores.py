"""
🚀 Despachador de eventos para el BFF
Publica comandos hacia microservicios siguiendo el patrón establecido
"""

import pulsar
from pulsar.schema import *
import logging
import traceback
import uuid
from datetime import datetime
from typing import Any, Dict

from bff.comandos import ComandoLanzarCampaniaCompleta, ComandoCancelarSaga, LanzarCampaniaCompletaPayload, CancelarSagaPayload
from bff.config import config


class DespachadorBFF:
    """
    Despachador de eventos para el BFF.
    Publica comandos hacia microservicios usando Pulsar.
    """
    
    def __init__(self):
        self.broker_url = f'pulsar://{config.pulsar_host}:6650'
        
    def publicar_comando(self, comando, topico: str):
        """
        Publica un comando en un tópico específico de Pulsar.
        
        Args:
            comando: Objeto del comando a publicar
            topico: Nombre del tópico destino
        """
        cliente = None
        try:
            print(f"📤 BFF publicando {type(comando).__name__} en tópico: {topico}")
            
            cliente = pulsar.Client(self.broker_url)
            publicador = cliente.create_producer(
                topico, 
                schema=AvroSchema(comando.__class__)
            )
            
            # Enviar comando
            publicador.send(comando)
            print(f"✅ Comando publicado exitosamente: {type(comando).__name__}")
            
            return True
            
        except Exception as e:
            logging.error(f"Error publicando comando {type(comando).__name__} en {topico}: {str(e)}")
            traceback.print_exc()
            return False
            
        finally:
            if cliente:
                cliente.close()

    # ==========================================
    # COMANDOS ESPECÍFICOS HACIA campanias
    # ==========================================
    
    def lanzar_campania_completa(self, datos_campania: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envía comando para lanzar una campaña completa hacia el microservicio de campanias.
        
        Args:
            datos_campania: Datos de la campaña a crear
            
        Returns:
            Dict con el resultado del envío del comando
        """
        try:
            # Convertir fechas a timestamps (milisegundos)
            from datetime import datetime as dt
            
            # Manejar tanto objetos datetime como strings
            fecha_inicio = datos_campania['fecha_inicio']
            fecha_fin = datos_campania['fecha_fin']
            
            if isinstance(fecha_inicio, str):
                fecha_inicio_dt = dt.fromisoformat(fecha_inicio.replace('Z', '+00:00'))
            else:
                fecha_inicio_dt = fecha_inicio
                
            if isinstance(fecha_fin, str):
                fecha_fin_dt = dt.fromisoformat(fecha_fin.replace('Z', '+00:00'))
            else:
                fecha_fin_dt = fecha_fin
            
            fecha_inicio_ts = int(fecha_inicio_dt.timestamp() * 1000)
            fecha_fin_ts = int(fecha_fin_dt.timestamp() * 1000)
            
            # Crear payload
            payload = LanzarCampaniaCompletaPayload(
                nombre=datos_campania['nombre'],
                descripcion=datos_campania.get('descripcion', ''),
                tipo=datos_campania['tipo'],
                canal_publicidad=datos_campania.get('canal_publicidad', 'online'),
                objetivo=datos_campania.get('objetivo', 'conversion'),
                fecha_inicio=fecha_inicio_ts,
                fecha_fin=fecha_fin_ts,
                presupuesto=float(datos_campania.get('presupuesto', 0.0)),
                moneda=datos_campania.get('moneda', 'USD'),
                segmento_audiencia=datos_campania.get('segmento_audiencia', 'general')
            )
            
            # Crear comando CloudEvent
            now_millis = int(datetime.utcnow().timestamp() * 1000)
            comando = ComandoLanzarCampaniaCompleta(
                id=str(uuid.uuid4()),
                time=now_millis,
                ingestion=now_millis,
                specversion="1.0",
                type="ComandoLanzarCampaniaCompleta",
                datacontenttype="application/json",
                service_name="bff",
                data=payload
            )
            
            # Publicar comando
            exito = self.publicar_comando(comando, "comando-lanzar-campania-completa")
            
            if exito:
                return {
                    "exito": True,
                    "comando_id": comando.id,
                    "mensaje": "Comando de lanzar campaña enviado exitosamente",
                    "topico": "comando-lanzar-campania-completa",
                    "timestamp": comando.time
                }
            else:
                return {
                    "exito": False,
                    "error": "Error al publicar comando",
                    "mensaje": "No se pudo enviar el comando al microservicio de campanias"
                }
                
        except Exception as e:
            logging.error(f"Error preparando comando lanzar campaña: {str(e)}")
            return {
                "exito": False,
                "error": str(e),
                "mensaje": "Error interno al preparar comando"
            }
    
    def cancelar_saga(self, saga_id: str, razon: str = "Cancelado por usuario") -> Dict[str, Any]:
        """
        Envía comando para cancelar una saga en progreso.
        
        Args:
            saga_id: ID de la saga a cancelar
            razon: Razón de la cancelación
            
        Returns:
            Dict con el resultado del envío del comando
        """
        try:
            # Crear payload
            payload = CancelarSagaPayload(
                saga_id=saga_id,
                razon=razon
            )
            
            # Crear comando CloudEvent
            now_millis = int(datetime.utcnow().timestamp() * 1000)
            comando = ComandoCancelarSaga(
                id=str(uuid.uuid4()),
                time=now_millis,
                ingestion=now_millis,
                specversion="1.0",
                type="ComandoCancelarSaga",
                datacontenttype="application/json",
                service_name="bff",
                data=payload
            )
            
            exito = self.publicar_comando(comando, "comando-cancelar-saga")
            
            if exito:
                return {
                    "exito": True,
                    "comando_id": comando.id,
                    "saga_id": saga_id,
                    "mensaje": "Comando de cancelación enviado exitosamente"
                }
            else:
                return {
                    "exito": False,
                    "error": "Error al publicar comando de cancelación"
                }
                
        except Exception as e:
            logging.error(f"Error cancelando saga {saga_id}: {str(e)}")
            return {
                "exito": False,
                "error": str(e),
                "mensaje": "Error interno al cancelar saga"
            }


# Instancia singleton del despachador
despachador_bff = DespachadorBFF()