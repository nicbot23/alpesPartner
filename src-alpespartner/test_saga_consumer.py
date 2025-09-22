#!/usr/bin/env python3
"""
Test standalone para verificar el flujo BFF -> Pulsar -> campanias
"""
import sys
import asyncio
import os

# Add src-alpespartner to path
sys.path.append('/Users/nicolasibarra/uniandes/miso-uniandes/semestre4/ciclo 1/Diseño y cosntrucción de soluciones no monoliticas/semana 7/tutorial-8-sagas/src-alpespartner')

# Set Pulsar host
os.environ['PULSAR_HOST'] = 'alpespartner-broker'

from campanias.modulos.infraestructura.schema.v1.comandos import ComandoLanzarCampaniaCompleta
from campanias.consumidores import suscribirse_a_topico

async def test_saga_flow():
    """
    Consumidor standalone para verificar que el flujo de sagas funciona
    """
    print("🚀 Iniciando consumidor standalone para testing...")
    print("📡 Configurado para broker: alpespartner-broker:6650")
    print("🎯 Tópico: comando-lanzar-campania-completa")
    print("📥 Suscripción: test-saga-standalone")
    print()
    print("Envía comandos desde BFF y verifica que llegan aquí...")
    print("Usa Ctrl+C para terminar")
    print("=" * 60)
    
    await suscribirse_a_topico(
        'comando-lanzar-campania-completa', 
        'test-saga-standalone', 
        ComandoLanzarCampaniaCompleta
    )

if __name__ == "__main__":
    asyncio.run(test_saga_flow())