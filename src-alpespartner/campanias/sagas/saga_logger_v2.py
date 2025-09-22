# campanias/sagas/saga_logger_v2.py
from __future__ import annotations

import os
import json
import uuid
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

log = logging.getLogger(__name__)
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

# BD de SAGAS (contenerizada)
DEFAULT_URL = "mysql+pymysql://root:adminadmin@sagas-mysql:3306/sagas?charset=utf8mb4"

class EstadoSaga:
    PENDIENTE   = "PENDIENTE"
    INICIADA    = "INICIADA"
    EN_PROGRESO = "EN_PROGRESO"
    COMPLETADA  = "COMPLETADA"
    FALLIDA     = "FALLIDA"
    CANCELADA   = "CANCELADA"
    COMPENSANDO = "COMPENSANDO"
    COMPENSADA  = "COMPENSADA"

class EstadoPaso:
    PENDIENTE  = "PENDIENTE"
    EJECUTANDO = "EJECUTANDO"
    OK         = "OK"
    FALLIDO    = "FALLIDO"
    COMPENSADO = "COMPENSADO"

_TERMINALES = {
    EstadoSaga.COMPLETADA,
    EstadoSaga.FALLIDA,
    EstadoSaga.CANCELADA,
    EstadoSaga.COMPENSADA,
}

def _now_utc() -> datetime:
    return datetime.utcnow()

class SagaLoggerV2:
    """Compat layer esperado por consumidores/ despachadores, respaldado en MySQL (BD `sagas`)."""

    # ------- bootstrap --------
    @classmethod
    def init_db(cls) -> None:
        """Mantener compat: aquí solo validamos que existan tablas; no migramos nada."""
        try:
            inst = cls()
            inst._detect_schema()
            log.info("SagaLoggerV2.init_db(): esquema detectado OK (BD sagas).")
        except Exception as e:
            log.warning("SagaLoggerV2.init_db(): no se pudo validar esquema: %s", e)

    def __init__(self, storage_type: Optional[str] = None, db_url: Optional[str] = None) -> None:
        # storage_type se ignora a propósito (compat)
        self.db_url = db_url or os.getenv("SAGAS_DB_URL", DEFAULT_URL)
        self.engine: Engine = create_engine(self.db_url, pool_pre_ping=True, future=True)
        self._detect_schema()

    # ------- introspección --------
    def _cols(self, table: str) -> List[str]:
        with self.engine.begin() as conn:
            rows = conn.execute(
                text("""
                    SELECT COLUMN_NAME
                    FROM information_schema.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME=:t
                """),
                {"t": table}
            ).fetchall()
        return [r[0] for r in rows]

    def _detect_schema(self) -> None:
        # sagas
        sc = set(self._cols("sagas"))
        if not sc:
            raise RuntimeError("No existe la tabla `sagas` en la BD actual.")
        # PK
        self.pk_saga = "id" if "id" in sc else ("saga_id" if "saga_id" in sc else None)
        if not self.pk_saga:
            raise RuntimeError("La tabla `sagas` no tiene `id` ni `saga_id`.")
        # comunes/variantes
        self.c_sagas = {
            "pk": self.pk_saga,
            "estado": "estado" if "estado" in sc else None,
            "nombre": "nombre_saga" if "nombre_saga" in sc else ("nombre" if "nombre" in sc else None),
            "contexto": "contexto" if "contexto" in sc else ("datos" if "datos" in sc else None),
            "error": "error_mensaje" if "error_mensaje" in sc else None,
            "fi": "fecha_inicio" if "fecha_inicio" in sc else None,
            "ff": "fecha_fin" if "fecha_fin" in sc else None,
        }
        self.sagas_cols = sc

        # saga_pasos (opcional)
        pc = set(self._cols("saga_pasos"))
        self.tiene_pasos = len(pc) > 0
        self.c_pasos = {
            "id": "id" if "id" in pc else None,  # tu esquema: VARCHAR(36) NOT NULL
            "saga_id": "saga_id" if "saga_id" in pc else None,
            "paso_numero": "paso_numero" if "paso_numero" in pc else None,
            "nombre_paso": "nombre_paso" if "nombre_paso" in pc else ("paso" if "paso" in pc else None),
            "servicio": "servicio" if "servicio" in pc else None,
            "comando": "comando" if "comando" in pc else None,
            "tipo_operacion": "tipo_operacion" if "tipo_operacion" in pc else None,
            "estado": "estado" if "estado" in pc else None,
            "req": "request_data" if "request_data" in pc else ("detalle" if "detalle" in pc else None),
            "res": "response_data" if "response_data" in pc else None,
            "err": "error_mensaje" if "error_mensaje" in pc else None,
            "fi": "fecha_inicio" if "fecha_inicio" in pc else None,
            "ff": "fecha_fin" if "fecha_fin" in pc else None,
        }
        self.pasos_cols = pc

        log.info("SagaLoggerV2 listo. sagas.pk=%s, pasos=%s", self.pk_saga, "sí" if self.tiene_pasos else "no")

    # ------- helpers --------
    def _insert_ignore(self, table: str, cols_vals: Dict[str, Any]) -> None:
        cols = list(cols_vals.keys())
        placeholders = [f":{c}" for c in cols]
        sql = f"INSERT IGNORE INTO {table} ({', '.join(cols)}) VALUES ({', '.join(placeholders)})"
        with self.engine.begin() as conn:
            conn.execute(text(sql), cols_vals)

    def _update_by_pk(self, table: str, pk_col: str, pk_val: Any, updates: Dict[str, Any]) -> None:
        if not updates:
            return
        set_sql = ", ".join([f"{k}=:{k}" for k in updates.keys()])
        params = dict(updates); params["__pk"] = pk_val
        sql = f"UPDATE {table} SET {set_sql} WHERE {pk_col}=:__pk"
        with self.engine.begin() as conn:
            conn.execute(text(sql), params)

    def _next_paso_num(self, saga_id: str) -> int:
        if not (self.tiene_pasos and self.c_pasos["paso_numero"] and self.c_pasos["saga_id"]):
            return 1
        sql = f"SELECT COALESCE(MAX({self.c_pasos['paso_numero']}),0)+1 AS n FROM saga_pasos WHERE {self.c_pasos['saga_id']}=:sid"
        with self.engine.begin() as conn:
            n = conn.execute(text(sql), {"sid": saga_id}).scalar_one()
        return int(n or 1)

    def _map_estado_paso(self, s: str) -> str:
        m = {
            "pendiente": EstadoPaso.PENDIENTE,
            "ejecutando": EstadoPaso.EJECUTANDO,
            "en_progreso": EstadoPaso.EJECUTANDO,
            "enviado": EstadoPaso.EJECUTANDO,
            "ok": EstadoPaso.OK,
            "completado": EstadoPaso.OK,
            "fallido": EstadoPaso.FALLIDO,
            "compensado": EstadoPaso.COMPENSADO,
        }
        return m.get(str(s).lower(), EstadoPaso.EJECUTANDO)

    # ------- API (sagas) --------
    def iniciar_saga(self, saga_id: str, tipo: str, campania_id: Optional[str] = None,
                     metadatos: Optional[Dict[str, Any]] = None, nombre: Optional[str] = None) -> None:
        """Crea la saga si no existe y la deja EN_PROGRESO, guardando contexto/metadata."""
        ctx = {"tipo": tipo, "campania_id": campania_id}
        if metadatos: ctx["metadatos"] = metadatos

        # build insert
        data = { self.c_sagas["pk"]: saga_id }
        if self.c_sagas["nombre"]:  data[self.c_sagas["nombre"]]  = nombre or tipo
        if self.c_sagas["estado"]:  data[self.c_sagas["estado"]]  = EstadoSaga.EN_PROGRESO
        if self.c_sagas["fi"]:      data[self.c_sagas["fi"]]      = _now_utc()
        if self.c_sagas["contexto"]:data[self.c_sagas["contexto"]] = json.dumps(ctx, ensure_ascii=False)

        self._insert_ignore("sagas", data)

    def actualizar_estado_saga(self, saga_id: str, nuevo_estado: str, mensaje: Optional[str] = None) -> None:
        ups: Dict[str, Any] = {}
        if self.c_sagas["estado"]:
            ups[self.c_sagas["estado"]] = nuevo_estado
        if nuevo_estado in _TERMINALES and self.c_sagas["ff"]:
            ups[self.c_sagas["ff"]] = _now_utc()
        if mensaje and self.c_sagas["contexto"]:
            # merge mensaje en JSON contexto/datos
            sql = f"SELECT {self.c_sagas['contexto']} FROM sagas WHERE {self.c_sagas['pk']}=:pk"
            with self.engine.begin() as conn:
                raw = conn.execute(text(sql), {"pk": saga_id}).scalar_one_or_none()
            base = {}
            try:
                base = json.loads(raw or "{}")
            except Exception:
                base = {}
            base["mensaje"] = mensaje
            ups[self.c_sagas["contexto"]] = json.dumps(base, ensure_ascii=False)

        self._update_by_pk("sagas", self.c_sagas["pk"], saga_id, ups)

    def marcar_completada(self, saga_id: str, datos_extra: Optional[Dict[str, Any]] = None) -> None:
        self.actualizar_estado_saga(saga_id, EstadoSaga.COMPLETADA)
        if datos_extra and self.c_sagas["contexto"]:
            sql = f"SELECT {self.c_sagas['contexto']} FROM sagas WHERE {self.c_sagas['pk']}=:pk"
            with self.engine.begin() as conn:
                raw = conn.execute(text(sql), {"pk": saga_id}).scalar_one_or_none()
            base = {}
            try:
                base = json.loads(raw or "{}")
            except Exception:
                base = {}
            base.update(datos_extra)
            self._update_by_pk("sagas", self.c_sagas["pk"], saga_id, {
                self.c_sagas["contexto"]: json.dumps(base, ensure_ascii=False)
            })

    def marcar_fallida(self, saga_id: str, mensaje: Optional[str] = None, paso_id: Optional[str] = None) -> None:
        # agrega error/ paso_fallido al JSON si existe
        extra: Dict[str, Any] = {}
        if mensaje: extra["error"] = mensaje
        if paso_id: extra["paso_fallido"] = paso_id
        self.actualizar_estado_saga(saga_id, EstadoSaga.FALLIDA, mensaje or None)
        if extra and self.c_sagas["contexto"]:
            sql = f"SELECT {self.c_sagas['contexto']} FROM sagas WHERE {self.c_sagas['pk']}=:pk"
            with self.engine.begin() as conn:
                raw = conn.execute(text(sql), {"pk": saga_id}).scalar_one_or_none()
            base = {}
            try:
                base = json.loads(raw or "{}")
            except Exception:
                base = {}
            base.update(extra)
            self._update_by_pk("sagas", self.c_sagas["pk"], saga_id, {
                self.c_sagas["contexto"]: json.dumps(base, ensure_ascii=False)
            })

    def compensar_saga(self, saga_id: str, paso_id: Optional[str] = None, razon: Optional[str] = None) -> None:
        # marca paso compensado si viene
        if paso_id and self.tiene_pasos and self.c_pasos["id"]:
            sql = f"UPDATE saga_pasos SET {self.c_pasos['estado']}=:st, {self.c_pasos['ff']}=:ff WHERE {self.c_pasos['id']}=:pid"
            with self.engine.begin() as conn:
                conn.execute(text(sql), {"st": EstadoPaso.COMPENSADO, "ff": _now_utc(), "pid": paso_id})
        self.actualizar_estado_saga(saga_id, EstadoSaga.COMPENSADA, razon or "Compensación aplicada")

    def cancelar_saga(self, saga_id: str, razon: str) -> bool:
        self.actualizar_estado_saga(saga_id, EstadoSaga.CANCELADA, razon)
        return True

    def saga_completada(self, saga_id: str) -> bool:
        # si saga ya está COMPLETADA, corto
        sql = f"SELECT {self.c_sagas['estado']} FROM sagas WHERE {self.c_sagas['pk']}=:pk"
        with self.engine.begin() as conn:
            st = conn.execute(text(sql), {"pk": saga_id}).scalar_one_or_none()
        if st == EstadoSaga.COMPLETADA:
            return True
        # si hay pasos, verifica que todos estén OK
        if not self.tiene_pasos or not self.c_pasos["estado"] or not self.c_pasos["saga_id"]:
            return False
        sql = f"SELECT COUNT(*) FROM saga_pasos WHERE {self.c_pasos['saga_id']}=:sid"
        sql_no_ok = f"SELECT COUNT(*) FROM saga_pasos WHERE {self.c_pasos['saga_id']}=:sid AND {self.c_pasos['estado']}!=:ok"
        with self.engine.begin() as conn:
            total = conn.execute(text(sql), {"sid": saga_id}).scalar_one()
            no_ok = conn.execute(text(sql_no_ok), {"sid": saga_id, "ok": EstadoPaso.OK}).scalar_one()
        return (total or 0) > 0 and (no_ok or 0) == 0

    # ------- API (pasos) --------
    def registrar_paso_saga(
        self,
        saga_id: str,
        nombre_paso: Optional[str] = None,
        paso_nombre: Optional[str] = None,     # compat
        servicio_destino: Optional[str] = None,
        microservicio: Optional[str] = None,   # compat
        topico_pulsar: Optional[str] = None,
        descripcion: Optional[str] = None,
        datos_entrada: Optional[Dict[str, Any]] = None
    ) -> str:
        if not self.tiene_pasos:
            # no hay tabla; devolvemos un id virtual para no romper
            return str(uuid.uuid4())

        pid = str(uuid.uuid4())
        paso = nombre_paso or paso_nombre or "paso"
        servicio = servicio_destino or microservicio or "desconocido"
        n = self._next_paso_num(saga_id)

        payload = {
            "descripcion": descripcion or f"Envío a {servicio}",
            "servicio": servicio,
            "topico": topico_pulsar,
            "entrada": datos_entrada
        }

        cols_vals: Dict[str, Any] = {}
        # columnas obligatorias según tu esquema
        if self.c_pasos["id"]:          cols_vals[self.c_pasos["id"]] = pid
        if self.c_pasos["saga_id"]:     cols_vals[self.c_pasos["saga_id"]] = saga_id
        if self.c_pasos["paso_numero"]: cols_vals[self.c_pasos["paso_numero"]] = n
        if self.c_pasos["nombre_paso"]: cols_vals[self.c_pasos["nombre_paso"]] = paso
        if self.c_pasos["servicio"]:    cols_vals[self.c_pasos["servicio"]] = servicio
        if self.c_pasos["tipo_operacion"]: cols_vals[self.c_pasos["tipo_operacion"]] = "ACCION"
        if self.c_pasos["estado"]:      cols_vals[self.c_pasos["estado"]] = EstadoPaso.PENDIENTE
        if self.c_pasos["req"]:         cols_vals[self.c_pasos["req"]] = json.dumps(datos_entrada or {}, ensure_ascii=False)
        if self.c_pasos["fi"]:          cols_vals[self.c_pasos["fi"]] = _now_utc()
        if self.c_pasos["comando"] and topico_pulsar:
            cols_vals[self.c_pasos["comando"]] = topico_pulsar

        self._insert_ignore("saga_pasos", cols_vals)
        return pid

    def actualizar_estado_paso_por_id(self, paso_id: str, nuevo_estado: str, detalle: Optional[Dict[str, Any] | str] = None) -> None:
        if not (self.tiene_pasos and self.c_pasos["id"] and self.c_pasos["estado"]):
            return
        st = self._map_estado_paso(nuevo_estado)
        ups: Dict[str, Any] = { self.c_pasos["estado"]: st }
        if isinstance(detalle, dict) and self.c_pasos["res"]:
            ups[self.c_pasos["res"]] = json.dumps(detalle, ensure_ascii=False)
        elif isinstance(detalle, str) and self.c_pasos["err"]:
            ups[self.c_pasos["err"]] = detalle
        if st in {EstadoPaso.OK, EstadoPaso.FALLIDO, EstadoPaso.COMPENSADO} and self.c_pasos["ff"]:
            ups[self.c_pasos["ff"]] = _now_utc()
        self._update_by_pk("saga_pasos", self.c_pasos["id"], paso_id, ups)

    def actualizar_estado_paso(self, saga_id: str, paso: str, estado: str,
                               detalle: Optional[Dict[str, Any] | str] = None) -> None:
        """Actualiza por (saga_id, nombre_paso/paso). Si no existe, lo crea."""
        if not self.tiene_pasos or not self.c_pasos["saga_id"] or not self.c_pasos["nombre_paso"] or not self.c_pasos["estado"]:
            return
        st = self._map_estado_paso(estado)

        # ¿existe?
        sql_sel = f"""
            SELECT {self.c_pasos['id']}
            FROM saga_pasos
            WHERE {self.c_pasos['saga_id']}=:sid AND {self.c_pasos['nombre_paso']}=:p
            ORDER BY {self.c_pasos.get('paso_numero','1')} DESC
            LIMIT 1
        """
        with self.engine.begin() as conn:
            row = conn.execute(text(sql_sel), {"sid": saga_id, "p": paso}).first()

        if row and row[0]:
            self.actualizar_estado_paso_por_id(row[0], st, detalle)
            return

        # si no existe, crearlo con estado solicitado
        pid = self.registrar_paso_saga(
            saga_id=saga_id, nombre_paso=paso, servicio_destino="desconocido",
            topico_pulsar=None, datos_entrada=None
        )
        self.actualizar_estado_paso_por_id(pid, st, detalle)

    # ------- consultas --------
    def obtener_estado_saga(self, saga_id: str) -> Optional[Dict[str, Any]]:
        select_cols = [self.c_sagas["pk"]]
        for key in ("nombre", "estado", "contexto", "fi", "ff"):
            c = self.c_sagas.get(key)
            if c: select_cols.append(c)
        sql = f"SELECT {', '.join(select_cols)} FROM sagas WHERE {self.c_sagas['pk']}=:pk"
        with self.engine.begin() as conn:
            row = conn.execute(text(sql), {"pk": saga_id}).mappings().first()
        if not row:
            return None
        data = dict(row)
        data["saga_id"] = data.pop(self.c_sagas["pk"])
        # normaliza nombres
        if self.c_sagas["nombre"] and self.c_sagas["nombre"] in data:
            data["nombre"] = data.pop(self.c_sagas["nombre"])
        if self.c_sagas["contexto"] and self.c_sagas["contexto"] in data:
            try:
                data["contexto"] = json.loads(data.pop(self.c_sagas["contexto"]))
            except Exception:
                data["contexto"] = data.pop(self.c_sagas["contexto"])
        if self.c_sagas["fi"] and self.c_sagas["fi"] in data and isinstance(data[self.c_sagas["fi"]], datetime):
            data["fecha_inicio"] = data.pop(self.c_sagas["fi"]).isoformat() + "Z"
        if self.c_sagas["ff"] and self.c_sagas["ff"] in data and isinstance(data[self.c_sagas["ff"]], datetime):
            data["fecha_fin"] = data.pop(self.c_sagas["ff"]).isoformat() + "Z"
        data["finalizada"] = data.get("estado") in _TERMINALES
        return data

    def obtener_progreso_detallado(self, saga_id: str) -> Optional[Dict[str, Any]]:
        base = self.obtener_estado_saga(saga_id)
        if not base:
            return None
        pasos: List[Dict[str, Any]] = []
        if self.tiene_pasos:
            order = self.c_pasos.get("fi") or self.c_pasos.get("paso_numero") or self.c_pasos["id"]
            sql = f"""
               SELECT {', '.join([c for c in self.c_pasos.values() if c])}
               FROM saga_pasos
               WHERE {self.c_pasos['saga_id']}=:sid
               ORDER BY {order} ASC
            """
            with self.engine.begin() as conn:
                rows = conn.execute(text(sql), {"sid": saga_id}).mappings().all()
            for r in rows:
                item = dict(r)
                if self.c_pasos["id"] and self.c_pasos["id"] in item:
                    item["paso_id"] = item.pop(self.c_pasos["id"])
                if self.c_pasos["nombre_paso"] and self.c_pasos["nombre_paso"] in item:
                    item["paso"] = item.pop(self.c_pasos["nombre_paso"])
                if self.c_pasos["req"] and self.c_pasos["req"] in item and isinstance(item[self.c_pasos["req"]], (str, bytes)):
                    try:
                        item["detalle"] = json.loads(item.pop(self.c_pasos["req"]))
                    except Exception:
                        item["detalle"] = item.pop(self.c_pasos["req"])
                if self.c_pasos["fi"] and self.c_pasos["fi"] in item and isinstance(item[self.c_pasos["fi"]], datetime):
                    item["fecha_inicio"] = item.pop(self.c_pasos["fi"]).isoformat() + "Z"
                if self.c_pasos["ff"] and self.c_pasos["ff"] in item and isinstance(item[self.c_pasos["ff"]], datetime):
                    item["fecha_fin"] = item.pop(self.c_pasos["ff"]).isoformat() + "Z"
                pasos.append(item)
        return {"saga": base, "pasos": pasos}
    


# Alias legacy que algunos módulos podrían importar
SagaLogger = SagaLoggerV2
