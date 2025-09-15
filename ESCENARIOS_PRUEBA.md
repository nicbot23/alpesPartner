# ✅ Escenarios de Prueba - Arquitectura Event-Driven Marketing

Este documento describe cada escenario cubierto por `script_escenarios_pruebas.sh`, los objetivos, pasos, validaciones y notas de evolución futura.

---
## 📌 Resumen Rápido

| # | Escenario | Objetivo | Validación Principal |
|---|-----------|----------|----------------------|
| 1 | Flujo Exitoso Básico | Pipeline completo | Campaña + evento comisión + logs |
| 2 | Fechas Inválidas | Detectar falta de validación | Campaña creada (marcar mejora) |
| 3 | Porcentaje Extremo | Lógica de negocio pendiente | Terminos comisión >100% |
| 4 | Duplicado Nombre | Idempotencia inexistente | Dos filas con distinto id |
| 5 | Consumo Histórico | Reproducibilidad de eventos | Pulsar Earliest muestra históricos |
| 6 | Correlación | Trazabilidad multi-evento | Logs filtrables por correlation_id |
| 7 | Resiliencia Restart | Robustez tras reinicio | Procesa comandos antes/después |
| 8 | Fallo Comisión (manual) | Resiliencia parcial | Campaña sin evento comisión |

---
## 🔧 Preparación Global

1. Stack levantado:
```bash
docker-compose up -d
```
2. Servicios sanos:
```bash
curl -s http://localhost:9000/health
curl -s http://localhost:8003/health
```
3. Opcional: instalar jq
```bash
brew install jq
```
4. Dar permiso ejecución al script:
```bash
chmod +x script_escenarios_pruebas.sh
```

---
## 1️⃣ Escenario: Flujo Exitoso Básico
**Comando:**
```bash
./script_escenarios_pruebas.sh 1
```
**Objetivo:** Validar el camino feliz: comando → consumidor → persistencia → eventos.
**Validar:**
- BD: fila en `campanas`.
- Comisión: fila en `commission` (si hubo cálculo con porcentaje > 0 y lógica configurada; en inicial puede ser monto base 0).
- Eventos: usar histórico (Escenario 5) si no estaban listeners activos.
**Logs esperados:**
```
[Campañas][CommandConsumer] Ejecutando handler_crear_campana
[Comisiones][Handler] Persistiendo comisión inicial
[Comisiones][Handler] Evento ComisionCalculada publicado
```
**Mejoras futuras:** añadir verificación automática de recepción de eventos.

---
## 2️⃣ Escenario: Fechas Inválidas
**Comando:**
```bash
./script_escenarios_pruebas.sh 2
```
**Objetivo:** Exhibir que aún no se valida `fecha_inicio < fecha_fin`.
**Resultado actual:** Campaña se acepta.
**Validar:**
```sql
SELECT id, fecha_inicio, fecha_fin FROM campanas ORDER BY creada_en DESC LIMIT 1;
```
**Futuro:** Agregar validación a nivel handler o entidad (`ConfiguracionCampana`).

---
## 3️⃣ Escenario: Comisión Porcentaje Extremo
**Comando:**
```bash
./script_escenarios_pruebas.sh 3
```
**Objetivo:** Mostrar ausencia de límite para `comision_porcentaje`.
**Validar:**
```sql
SELECT id, terminos_comision FROM campanas ORDER BY creada_en DESC LIMIT 1;
```
**Futuro:** Rechazar > 1.0 (100%) o negativos.

---
## 4️⃣ Escenario: Duplicado de Nombre
**Comando:**
```bash
./script_escenarios_pruebas.sh 4
```
**Objetivo:** Mostrar que no existe control de unicidad de nombre.
**Validar:**
```sql
SELECT id, nombre, creada_en FROM campanas ORDER BY creada_en DESC LIMIT 2;
```
**Resultado esperado:** Dos filas con nombres iguales y IDs distintos.
**Futuro:** Constraint lógico (único por rango fecha o soft-check).

---
## 5️⃣ Escenario: Consumo Histórico de Eventos
**Comando:**
```bash
./script_escenarios_pruebas.sh 5
```
**Objetivo:** Ver eventos previos aunque no hubiese consumer en vivo.
**Validar salida:** Debe aparecer JSON de `CampanaCreada`, `NotificacionSolicitada` y `ComisionCalculada` (si se generó) en topics:
- `marketing.eventos`
- `marketing.comisiones.eventos`
**Notas:** Si vacío, ejecutar primero escenario 1 y luego repetir.

---
## 6️⃣ Escenario: Correlación de Eventos
**Comando:**
```bash
./script_escenarios_pruebas.sh 6
```
**Objetivo:** Generar múltiples campañas con correlation_ids controlados.
**Validar:**
```bash
docker logs alpes-marketing | grep corr-demo
```
**Futuro:** Persistir correlation_id en una tabla de auditoría u outbox.

---
## 7️⃣ Escenario: Resiliencia tras Restart
**Comando:**
```bash
./script_escenarios_pruebas.sh 7
```
**Objetivo:** Asegurar que tras reinicio el consumer vuelve a procesar comandos.
**Validar:**
- BD contiene campañas antes y después del restart.
- Logs muestran nuevo consumidor levantado: `🛰️ Consumidor de comandos Campañas escuchando ...`
**Futuro:** Confirmar reentrega exacta (usar subscription durable + ack handling robusto).

---
## 8️⃣ Escenario: Simulación de Fallo Comisión (Manual)
**Comando documental:**
```bash
./script_escenarios_pruebas.sh 8
```
**Objetivo:** Probar resiliencia parcial cuando comisión falla.
**Pasos manuales sugeridos:**
1. Editar `calculo_inicial_handler.py` y añadir:
```python
raise Exception("Simulación error comisión")
```
antes de `await self.repo.guardar_comision_calculada(...)`.
2. Reiniciar marketing:
```bash
docker-compose restart marketing
```
3. Ejecutar Escenario 1.
4. Validar:
   - Campaña persistida.
   - NO existe fila nueva en `commission`.
   - Logs: `ComisionesConfiguradasError`.
5. Revertir el cambio y reiniciar.
**Futuro:** Implementar Outbox + reintentos / DLQ.

---
## 📊 Validaciones SQL Recurrentes

Campañas recientes:
```sql
SELECT id, nombre, estado, creada_en FROM campanas ORDER BY creada_en DESC LIMIT 5;
```
Comisiones recientes:
```sql
SELECT id, campaign_id, percentage, status, calculated_at FROM commission ORDER BY calculated_at DESC LIMIT 5;
```

---
## 🧪 Ejecución Masiva
Para correr todos los escenarios (1-7 + documentación 8):
```bash
./script_escenarios_pruebas.sh all
```

---
## 🚀 Roadmap de Calidad (Post-Demo)
- Validaciones de negocio: fechas, porcentajes.
- Outbox real + dispatcher periódico.
- Enriquecer esquema eventos (schema registry / Avro).
- Retry & DLQ para publicación comisión.
- Métricas (latencia publicación, tiempos handler).
- Tests automatizados (pytest + containers ephemeral).

---
## 📝 Notas Finales
- Algunos escenarios exponen carencias deliberadas como oportunidades de mejora arquitectónica.
- Los correlation_id aún no se persisten: se habilitaría fácilmente extendiendo `outbox_event` o agregando tabla `event_trace`.
- Este set de pruebas sirve tanto para demo como para baseline antes de refactors.

---
**Autor:** Sistema de soporte arquitectónico  
**Última actualización:** $(date +%Y-%m-%d)
