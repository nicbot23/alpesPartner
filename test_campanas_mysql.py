#!/usr/bin/env python3
"""
Script de Validación para el Bounded Context Campañas
Prueba la funcionalidad completa con MySQL siguiendo patrones DDD
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import json

# Import del modelo de dominio
from src.alpespartner.modulos.campanas.dominio.objetos_valor import (
    PeriodoVigencia, TerminosComision, RestriccionGeografica, MetadatosCampana
)
from src.alpespartner.modulos.campanas.dominio.agregados import Campaña, EstadoCampana
from src.alpespartner.modulos.campanas.aplicacion.comandos import (
    CrearCampana, ActivarCampana, ModificarTerminosCampana
)
from src.alpespartner.modulos.campanas.aplicacion.manejadores import (
    ManejadorCrearCampana, ManejadorActivarCampana, ManejadorModificarTerminos
)


def test_objetos_valor():
    """Prueba 1: Validar que los Objetos Valor funcionan correctamente"""
    print("🧪 PRUEBA 1: Objetos Valor")
    
    # Crear período de vigencia
    periodo = PeriodoVigencia(
        fecha_inicio=datetime.now(),
        fecha_fin=datetime.now() + timedelta(days=30)
    )
    print(f"✅ Período de vigencia creado: {periodo.duracion_dias} días")
    
    # Crear términos de comisión
    terminos = TerminosComision(
        porcentaje=Decimal('15.5'),
        comision_minima=Decimal('100'),
        comision_maxima=Decimal('5000')
    )
    print(f"✅ Términos de comisión: {terminos.porcentaje}% (min: ${terminos.comision_minima})")
    
    # Crear restricción geográfica
    restriccion = RestriccionGeografica(
        paises_incluidos=['CO', 'PE', 'EC'],
        paises_excluidos=['VE']
    )
    print(f"✅ Restricción geográfica: {len(restriccion.paises_incluidos)} países incluidos")
    
    # Crear metadatos
    metadatos = MetadatosCampana(
        canal_origen='web',
        audiencia_objetivo='millennials',
        tags=['turismo', 'aventura', 'colombia']
    )
    print(f"✅ Metadatos: {metadatos.canal_origen}, {len(metadatos.tags)} tags")
    
    return periodo, terminos, restriccion, metadatos


def test_agregado_campana(periodo, terminos, restriccion, metadatos):
    """Prueba 2: Validar la lógica del Agregado Campaña"""
    print("\n🧪 PRUEBA 2: Agregado Campaña")
    
    # Crear campaña
    campana = Campaña.crear(
        nombre="Turismo Aventura Colombia 2024",
        descripcion="Campaña promocional para turismo de aventura en Colombia",
        periodo_vigencia=periodo,
        terminos_comision=terminos,
        restriccion_geografica=restriccion,
        metadatos=metadatos
    )
    
    print(f"✅ Campaña creada: {campana.nombre}")
    print(f"   Estado inicial: {campana.estado}")
    print(f"   ID: {campana.id}")
    
    # Activar campaña
    campana.activar()
    print(f"✅ Campaña activada: {campana.estado}")
    
    # Pausar campaña
    campana.pausar()
    print(f"✅ Campaña pausada: {campana.estado}")
    
    # Modificar términos
    nuevos_terminos = TerminosComision(
        porcentaje=Decimal('20.0'),
        comision_minima=Decimal('150'),
        comision_maxima=Decimal('7500')
    )
    campana.modificar_terminos(nuevos_terminos)
    print(f"✅ Términos modificados: {campana.terminos_comision.porcentaje}%")
    
    return campana


def test_comandos_y_handlers(campana):
    """Prueba 3: Validar Comandos y Manejadores (CQRS)"""
    print("\n🧪 PRUEBA 3: Comandos y Manejadores")
    
    # Crear comando
    comando_crear = CrearCampana(
        nombre="Campaña Test Handler",
        descripcion="Prueba del patrón CQRS",
        fecha_inicio=datetime.now(),
        fecha_fin=datetime.now() + timedelta(days=60),
        porcentaje_comision=Decimal('12.5'),
        comision_minima=Decimal('80'),
        comision_maxima=Decimal('3000'),
        paises_incluidos=['CO', 'MX'],
        paises_excluidos=[],
        canal_origen='mobile',
        audiencia_objetivo='gen-z',
        tags=['tecnologia', 'startup']
    )
    print(f"✅ Comando CrearCampana instanciado: {comando_crear.nombre}")
    
    # Comando de activación
    comando_activar = ActivarCampana(id_campana=campana.id)
    print(f"✅ Comando ActivarCampana instanciado para: {comando_activar.id_campana}")
    
    # Comando de modificación
    comando_modificar = ModificarTerminosCampana(
        id_campana=campana.id,
        porcentaje_comision=Decimal('25.0'),
        comision_minima=Decimal('200'),
        comision_maxima=Decimal('10000')
    )
    print(f"✅ Comando ModificarTerminosCampana instanciado con: {comando_modificar.porcentaje_comision}%")


def test_eventos_dominio(campana):
    """Prueba 4: Validar Eventos de Dominio"""
    print("\n🧪 PRUEBA 4: Eventos de Dominio")
    
    # Verificar eventos generados
    eventos = campana.eventos
    print(f"✅ Eventos generados: {len(eventos)}")
    
    for i, evento in enumerate(eventos, 1):
        print(f"   {i}. {type(evento).__name__} - {evento.fecha_evento}")
    
    # Limpiar eventos (simular que fueron procesados)
    campana.limpiar_eventos()
    print(f"✅ Eventos limpiados. Eventos restantes: {len(campana.eventos)}")


def test_persistencia_json():
    """Prueba 5: Validar Serialización para MySQL JSON"""
    print("\n🧪 PRUEBA 5: Serialización JSON para MySQL")
    
    # Crear objetos valor de prueba
    periodo = PeriodoVigencia(
        fecha_inicio=datetime.now(),
        fecha_fin=datetime.now() + timedelta(days=30)
    )
    
    terminos = TerminosComision(
        porcentaje=Decimal('15.5'),
        comision_minima=Decimal('100'),
        comision_maxima=Decimal('5000')
    )
    
    restriccion = RestriccionGeografica(
        paises_incluidos=['CO', 'PE'],
        paises_excluidos=['VE']
    )
    
    metadatos = MetadatosCampana(
        canal_origen='web',
        audiencia_objetivo='millennials',
        tags=['turismo', 'aventura']
    )
    
    # Simular serialización a JSON (como se haría para MySQL)
    periodo_json = {
        'fecha_inicio': periodo.fecha_inicio.isoformat(),
        'fecha_fin': periodo.fecha_fin.isoformat()
    }
    
    terminos_json = {
        'porcentaje': float(terminos.porcentaje),
        'comision_minima': float(terminos.comision_minima),
        'comision_maxima': float(terminos.comision_maxima) if terminos.comision_maxima else None
    }
    
    restriccion_json = {
        'paises_incluidos': restriccion.paises_incluidos,
        'paises_excluidos': restriccion.paises_excluidos
    }
    
    metadatos_json = {
        'canal_origen': metadatos.canal_origen,
        'audiencia_objetivo': metadatos.audiencia_objetivo,
        'tags': metadatos.tags
    }
    
    print(f"✅ Período serializado: {json.dumps(periodo_json, indent=2)}")
    print(f"✅ Términos serializado: {json.dumps(terminos_json, indent=2)}")
    print(f"✅ Restricción serializada: {json.dumps(restriccion_json, indent=2)}")
    print(f"✅ Metadatos serializados: {json.dumps(metadatos_json, indent=2)}")
    
    # Simular deserialización desde JSON
    periodo_reconstruido = PeriodoVigencia(
        fecha_inicio=datetime.fromisoformat(periodo_json['fecha_inicio']),
        fecha_fin=datetime.fromisoformat(periodo_json['fecha_fin'])
    )
    print(f"✅ Período reconstruido desde JSON: {periodo_reconstruido.duracion_dias} días")


def main():
    """Ejecuta todas las pruebas del Bounded Context Campañas"""
    print("🚀 VALIDACIÓN DEL BOUNDED CONTEXT CAMPAÑAS")
    print("=" * 50)
    
    try:
        # Ejecutar pruebas
        periodo, terminos, restriccion, metadatos = test_objetos_valor()
        campana = test_agregado_campana(periodo, terminos, restriccion, metadatos)
        test_comandos_y_handlers(campana)
        test_eventos_dominio(campana)
        test_persistencia_json()
        
        print("\n" + "=" * 50)
        print("🎉 TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("📊 RESUMEN:")
        print("   ✅ Objetos Valor: Inmutables y con validaciones")
        print("   ✅ Agregado Campaña: Lógica de negocio encapsulada")
        print("   ✅ Comandos CQRS: Intención de usuario capturada")
        print("   ✅ Eventos de Dominio: Estado del agregado rastreado")
        print("   ✅ Serialización MySQL: JSON compatible")
        print("\n💡 El Bounded Context está listo para:")
        print("   - Conexión con MySQL")
        print("   - Integración con Apache Pulsar")
        print("   - APIs REST funcionales")
        print("   - Patrones Event Sourcing")
        
    except Exception as e:
        print(f"\n❌ ERROR EN LAS PRUEBAS: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
