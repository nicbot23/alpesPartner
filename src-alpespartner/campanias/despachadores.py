# campanias/despachadores.py
import os, logging, traceback, uuid, json
from typing import Any, Dict

import pulsar
from pulsar.schema import AvroSchema, Record

from campanias.seedwork.infraestructura import utils
from campanias.sagas.saga_logger_v2 import SagaLoggerV2, EstadoSaga
from campanias.modulos.infraestructura.schema.v1.comandos import (
    ComandoBuscarAfiliadosElegibles,
    BuscarAfiliadosElegiblesPayload,
)

class Despachador:
    """
    Orquesta la saga de campaña completa enviando comandos por Pulsar
    y registra el progreso en SagaLoggerV2.
    """
    def __init__(self):
        self.broker_url = f'pulsar://{utils.broker_host()}:6650'
        storage_type = os.getenv("SAGAS_STORAGE_TYPE", "sqlite")
        self.saga_logger = SagaLoggerV2(storage_type=storage_type)
        print(f"🎭 Despachador inicializado con SagaLogger {storage_type.upper()}")


    # --------- Publicación ----------
    def _send_avro(self, cliente: pulsar.Client, topico: str, mensaje: Record):
        productor = cliente.create_producer(topico, schema=AvroSchema(mensaje.__class__))
        productor.send(mensaje)

    def _send_json(self, cliente: pulsar.Client, topico: str, payload: Dict[str, Any]):
        productor = cliente.create_producer(topico)
        productor.send(json.dumps(payload).encode("utf-8"))

    def publicar_mensaje(self, mensaje, topico: str):
        cliente = None
        try:
            cliente = pulsar.Client(self.broker_url)
            if isinstance(mensaje, Record):
                self._send_avro(cliente, topico, mensaje)
            elif isinstance(mensaje, dict):
                self._send_json(cliente, topico, mensaje)
            else:
                try:
                    self._send_avro(cliente, topico, mensaje)
                except Exception:
                    self._send_json(cliente, topico, {"payload": str(mensaje)})
            print(f"✅ Evento publicado en {topico}")
        except Exception as e:
            logging.error(f"Error publicando en {topico}: {e}")
            traceback.print_exc()
        finally:
            if cliente:
                cliente.close()

    def publicar_evento(self, evento, topico: str):
        self.publicar_mensaje(evento, topico)

    # --------- SAGA: Lanzar campaña completa ----------
    def orquestar_saga_campania_completa(self, datos_campania: Dict[str, Any]) -> str:
        saga_id = datos_campania.get('saga_id') or str(uuid.uuid4())
        try:
            print(f"🎭 INICIANDO SAGA: {saga_id} - Lanzar Campaña Completa")
            self.saga_logger.iniciar_saga(
                saga_id=saga_id,
                tipo="lanzar_campania_completa",
                campania_id=datos_campania.get('id'),
                metadatos={"campania_nombre": datos_campania.get('nombre'), "entrada": datos_campania}
            )

            # Paso 1: Afiliados
            self.solicitar_afiliados_elegibles(datos_campania, saga_id)
            # if not self.solo_afiliados:
            #     # Paso 2: Comisiones
            #     self.configurar_comisiones(datos_campania, saga_id)   # o configurar_comisiones_campania si usas la Opción B
            #     # Paso 3: Conversiones
            #     self.inicializar_tracking_conversiones(datos_campania, saga_id)
            #     # Paso 4: Notificaciones
            #     self.preparar_notificaciones_campania(datos_campania, saga_id)

            self.saga_logger.actualizar_estado_saga(saga_id, EstadoSaga.EN_PROGRESO, "Comando de afiliados enviado")
            print(f"✅ SAGA {saga_id} en progreso")
            return saga_id
        except Exception as e:
            self.saga_logger.actualizar_estado_saga(saga_id, EstadoSaga.FALLIDA, f"Error: {e}")
            logging.error(f"Error en saga {saga_id}: {e}")
            self.compensar_saga_campania(datos_campania, saga_id)
            raise


    def solicitar_afiliados_elegibles(self, datos_campania: Dict[str, Any], saga_id: str):
        paso_id = None
        try:
            paso_id = self.saga_logger.registrar_paso_saga(
                saga_id=saga_id,
                nombre_paso="solicitar_afiliados_elegibles",
                servicio_destino="afiliados",
                topico_pulsar="comando-buscar-afiliados-elegibles",
                datos_entrada={
                    "campania_id": datos_campania["id"],
                    "criterios": datos_campania.get("segmento_audiencia", "general"),
                },
            )

            # ==== Construcción EXACTA del envelope que exige el tópico ====
            payload = BuscarAfiliadosElegiblesPayload(
                campania_id=datos_campania["id"],
                campania_nombre=datos_campania["nombre"],
                tipo_campania=datos_campania["tipo"],
                canal_publicidad=datos_campania["canal_publicidad"],
                objetivo_campania=datos_campania["objetivo"],
                segmento_audiencia=datos_campania.get("segmento_audiencia", "general"),
                # En el schema actual son STRING. Convertimos epoch→ISO o a string simple.
                fecha_inicio=str(datos_campania["fecha_inicio"]),
                fecha_fin=str(datos_campania["fecha_fin"]),
                criterios_elegibilidad={
                    "segmento_requerido": datos_campania.get("segmento_audiencia", "general"),
                    "canal_compatible": datos_campania["canal_publicidad"],
                    "nivel_minimo": "basico",
                },
            )

            env = ComandoBuscarAfiliadosElegibles(
                id=saga_id,
                time=int(__import__("time").time() * 1000),
                ingestion=int(__import__("time").time() * 1000),
                specversion="1.0",
                type="comando.buscar_afiliados_elegibles",
                datacontenttype="application/avro",
                service_name="campanias",
                data=payload,
            )
            # ===============================================================

            # Publicar con AvroSchema de la clase envelope
            import pulsar
            cliente = pulsar.Client(self.broker_url)
            try:
                prod = cliente.create_producer(
                    "comando-buscar-afiliados-elegibles",
                    schema=AvroSchema(ComandoBuscarAfiliadosElegibles),
                )
                prod.send(env)
            finally:
                cliente.close()

            self.saga_logger.actualizar_estado_paso_por_id(paso_id, "enviado")

        except Exception as e:
            if paso_id:
                self.saga_logger.actualizar_estado_paso_por_id(paso_id, "fallido", str(e))
            raise

    def inicializar_tracking_conversiones(self, datos_campania: Dict[str, Any], saga_id: str):
        try:
            paso_id = self.saga_logger.registrar_paso_saga(
                saga_id=saga_id,
                nombre_paso="inicializar_tracking_conversiones",
                servicio_destino="conversiones",
                topico_pulsar="comando-inicializar-tracking-campania",
                datos_entrada={"campania_id": datos_campania["id"], "objetivo": datos_campania["objetivo"]}
            )
            from campanias.comandos import ComandoInicializarTrackingCampania
            comando = ComandoInicializarTrackingCampania(
                campania_id=datos_campania["id"],
                campania_nombre=datos_campania["nombre"],
                objetivo_campania=datos_campania["objetivo"],
                canal_publicidad=datos_campania["canal_publicidad"],
                metricas_objetivo=self._definir_metricas_por_objetivo(datos_campania["objetivo"]),
                metas_numericas={
                    "conversiones_esperadas": self._calcular_meta_conversiones(datos_campania),
                    "ingresos_objetivo": datos_campania.get("presupuesto", 0.0) * 3,
                    "afiliados_participantes": 50
                },
                fecha_inicio=datos_campania["fecha_inicio"],
                fecha_fin=datos_campania["fecha_fin"]
            )
            self.publicar_mensaje(comando, "comando-inicializar-tracking-campania")
            self.saga_logger.actualizar_estado_paso_por_id(paso_id, "enviado")
        except Exception as e:
            self.saga_logger.actualizar_estado_paso_por_id(paso_id, "fallido", str(e))
            raise

    def preparar_notificaciones_campania(self, datos_campania: Dict[str, Any], saga_id: str):
        try:
            paso_id = self.saga_logger.registrar_paso_saga(
                saga_id=saga_id,
                nombre_paso="preparar_notificaciones_campania",
                servicio_destino="notificaciones",
                topico_pulsar="comando-preparar-notificaciones-campania",
                datos_entrada={"campania_id": datos_campania["id"], "canal": datos_campania["canal_publicidad"]}
            )
            from campanias.comandos import ComandoPrepararNotificacionesCampania
            comando = ComandoPrepararNotificacionesCampania(
                campania_id=datos_campania["id"],
                campania_nombre=datos_campania["nombre"],
                canal_publicidad=datos_campania["canal_publicidad"],
                templates_notificacion={
                    "email": "campania_nueva_email.html",
                    "sms": "campania_nueva_sms.txt",
                    "push": "campania_nueva_push.json",
                    "web": "campania_nueva_banner.html"
                },
                contenido_personalizado={
                    "titulo": f"Nueva campaña: {datos_campania['nombre']}",
                    "descripcion": datos_campania.get("descripcion", ""),
                    "fecha_inicio": datos_campania["fecha_inicio"],
                    "fecha_fin": datos_campania["fecha_fin"],
                    "call_to_action": "Participar en campaña"
                },
                criterios_envio={
                    "solo_afiliados_confirmados": True,
                    "respetar_preferencias": True,
                    "horario_optimo": True
                }
            )
            self.publicar_mensaje(comando, "comando-preparar-notificaciones-campania")
            self.saga_logger.actualizar_estado_paso_por_id(paso_id, "enviado")
        except Exception as e:
            self.saga_logger.actualizar_estado_paso_por_id(paso_id, "fallido", str(e))
            raise

    def compensar_saga_campania(self, datos_campania: Dict[str, Any], saga_id: str):
        try:
            print(f"⚠️ COMPENSANDO SAGA {saga_id}...")
            self.saga_logger.actualizar_estado_saga(saga_id, EstadoSaga.COMPENSANDO, "Iniciando compensación")

            # Ejemplos de comandos de compensación (como JSON si no hay Avro definido)
            p1 = self.saga_logger.registrar_paso_saga(
                saga_id=saga_id,
                nombre_paso="compensar_busqueda_afiliados",
                servicio_destino="afiliados",
                topico_pulsar="comando-cancelar-busqueda-afiliados",
                datos_entrada={"campania_id": datos_campania["id"], "accion": "cancelar"}
            )
            self.publicar_mensaje({"campania_id": datos_campania["id"], "accion": "cancelar"}, "comando-cancelar-busqueda-afiliados")
            self.saga_logger.actualizar_estado_paso_por_id(p1, "enviado")

            p2 = self.saga_logger.registrar_paso_saga(
                saga_id=saga_id,
                nombre_paso="compensar_comisiones",
                servicio_destino="comisiones",
                topico_pulsar="comando-desconfigurar-comisiones",
                datos_entrada={"campania_id": datos_campania["id"], "accion": "desconfigurar"}
            )
            self.publicar_mensaje({"campania_id": datos_campania["id"], "accion": "desconfigurar"}, "comando-desconfigurar-comisiones")
            self.saga_logger.actualizar_estado_paso_por_id(p2, "enviado")

            self.saga_logger.actualizar_estado_saga(saga_id, EstadoSaga.COMPENSADA, "Compensación completada")
        except Exception as e:
            self.saga_logger.actualizar_estado_saga(saga_id, EstadoSaga.FALLIDA, f"Error en compensación: {e}")
            logging.error(f"Error compensando saga {saga_id}: {e}")

    # --------- Utilidades ---------
    def _calcular_comision_base(self, tipo_campania: str) -> float:
        return {"promocional": 0.05, "descuento": 0.03, "cashback": 0.08}.get(tipo_campania, 0.05)

    def _definir_metricas_por_objetivo(self, objetivo: str) -> Dict[str, Any]:
        metricas = {
            "incrementar_ventas": ["conversion_rate", "revenue", "order_value"],
            "fidelizar_clientes": ["retention_rate", "repeat_purchases", "lifetime_value"],
            "captar_nuevos_clientes": ["new_signups", "first_purchase", "activation_rate"],
        }
        return metricas.get(objetivo, ["conversion_rate", "revenue"])

    def _calcular_meta_conversiones(self, datos_campania: Dict[str, Any]) -> int:
        presupuesto = datos_campania.get("presupuesto", 1000)
        tipo = datos_campania.get("tipo", "promocional")
        costo_por_conversion = {"promocional": 25, "descuento": 15, "cashback": 30}
        return int(presupuesto / costo_por_conversion.get(tipo, 25))








