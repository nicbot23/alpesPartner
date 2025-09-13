# 🗺️ CONTEXT MAP - AlpesPartner DDD

## Bounded Contexts Definidos

### 1. 🎯 **Comisiones** (Core Domain)
- **Responsabilidad**: Cálculo, aprobación y gestión del ciclo de vida de comisiones
- **Agregados**: `Comision`
- **Objetos Valor**: `Dinero`, `Porcentaje`
- **Eventos**: `ComisionCalculada`, `ComisionAprobada`
- **Base de datos**: MySQL (transaccional, ACID)
- **Patrón**: CRUD + Outbox

### 2. 📢 **Campañas** (Supporting Domain)
- **Responsabilidad**: Gestión de campañas de marketing, términos y condiciones
- **Agregados**: `Campana`
- **Objetos Valor**: `PeriodoVigencia`, `TerminosComision`
- **Eventos**: `CampanaCreada`, `CampanaActivada`, `CampanaDesactivada`
- **Base de datos**: PostgreSQL (flexibilidad para consultas)
- **Patrón**: CRUD clásico

### 3. 👥 **Afiliados** (Supporting Domain)
- **Responsabilidad**: Onboarding, gestión y estados de afiliados
- **Agregados**: `Afiliado`
- **Objetos Valor**: `DatosContacto`, `InformacionBancaria`, `EstadoAfiliado`
- **Eventos**: `AfiliadoRegistrado`, `AfiliadoActivado`, `AfiliadoSuspendido`
- **Base de datos**: MongoDB (schema flexible para onboarding)
- **Patrón**: Event Sourcing (para auditoría completa)

### 4. 🔗 **Portal** (Generic Domain - BFF)
- **Responsabilidad**: Orquestación de consultas, vistas materializadas, API externa
- **Agregados**: `ConsultaIntegrada`
- **Objetos Valor**: `FiltroConsulta`, `ResultadoPaginado`
- **Eventos**: `ConsultaEjecutada`, `VistaActualizada`
- **Base de datos**: Redis (caché de vistas)
- **Patrón**: CQRS + Read Models

## Relaciones entre Contextos

### Comisiones → Campañas (Customer/Supplier)
- **Anti-Corruption Layer**: `ServicioCampanas`
- **Eventos de Integración**: `ValidacionCampanaRequerida`
- **Comunicación**: Asíncrona vía Pulsar

### Comisiones → Afiliados (Customer/Supplier)  
- **Anti-Corruption Layer**: `ServicioAfiliados`
- **Eventos de Integración**: `ValidacionAfiliadoRequerida`
- **Comunicación**: Asíncrona vía Pulsar

### Portal → Todos (Conformist)
- **Adaptadores**: Para cada bounded context
- **Eventos de Integración**: Subscribe a todos los eventos
- **Comunicación**: Solo lectura, vistas materializadas

## Eventos de Integración vs Dominio

### Eventos de Dominio (internos al contexto):
- `ComisionCalculada` → Solo dentro de Comisiones
- `CampanaActivada` → Solo dentro de Campañas
- `AfiliadoRegistrado` → Solo dentro de Afiliados

### Eventos de Integración (entre contextos):
- `ComisionProcesadaIntegracion` → Todos los contextos
- `CampanaModificadaIntegracion` → Comisiones + Portal
- `AfiliadoCambioEstadoIntegracion` → Comisiones + Portal

## Esquemas Avro por Contexto

Cada contexto tendrá su registry de esquemas independiente para evolución autónoma.
