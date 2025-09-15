#!/usr/bin/env python3
"""
Script para enviar campaña de prueba y monitorear eventos
"""

import json
import requests
import time
from datetime import datetime
from colorama import init, Fore, Back, Style

# Inicializar colorama
init(autoreset=True)

def colored_output(text, color=Fore.WHITE):
    """Función para texto coloreado"""
    return f"{color}{text}{Style.RESET_ALL}"

def get_timestamp():
    """Obtiene timestamp actual"""
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]

def send_campaign():
    """Envía una campaña de prueba"""
    
    campaign_data = {
        "nombre": f"TEST EVENTOS - {get_timestamp()}",
        "descripcion": "Campaña para probar flujo de eventos en tiempo real",
        "fecha_inicio": "2024-01-01",
        "fecha_fin": "2024-12-31",
        "presupuesto": 100000,
        "meta_conversiones": 5000,
        "tipo_campana": "digital",
        "estado": "activa",
        "afiliados": [
            {"id": "af1", "nombre": "Afiliado Test Eventos 1"},
            {"id": "af2", "nombre": "Afiliado Test Eventos 2"},
            {"id": "af3", "nombre": "Afiliado Test Eventos 3"}
        ],
        "porcentaje_comision": 12.5
    }
    
    print(f"{colored_output('='*60, Fore.BLUE)}")
    print(f"{colored_output('🚀 ENVIANDO CAMPAÑA DE PRUEBA', Fore.BLUE)}")
    print(f"{colored_output('='*60, Fore.BLUE)}")
    print()
    
    print(f"{colored_output(f'[{get_timestamp()}] Preparando campaña...', Fore.YELLOW)}")
    print(f"{colored_output('📝 Nombre: ' + campaign_data['nombre'], Fore.WHITE)}")
    print(f"{colored_output('💰 Presupuesto: $' + str(campaign_data['presupuesto']), Fore.WHITE)}")
    print(f"{colored_output('👥 Afiliados: ' + str(len(campaign_data['afiliados'])), Fore.WHITE)}")
    print(f"{colored_output('💵 Comisión: ' + str(campaign_data['porcentaje_comision']) + '%', Fore.WHITE)}")
    print()
    
    try:
        print(f"{colored_output(f'[{get_timestamp()}] 📡 Enviando POST a http://localhost:8003/campanas...', Fore.CYAN)}")
        
        response = requests.post(
            'http://localhost:8003/campanas',
            headers={'Content-Type': 'application/json'},
            json=campaign_data,
            timeout=10
        )
        
        print(f"{colored_output(f'[{get_timestamp()}] ✅ Respuesta recibida: {response.status_code}', Fore.GREEN)}")
        
        if response.status_code == 200 or response.status_code == 201:
            result = response.json()
            print(f"{colored_output('🎉 CAMPAÑA CREADA EXITOSAMENTE!', Fore.GREEN, Back.BLACK)}")
            print(f"{colored_output('📋 ID: ' + str(result.get('id', 'N/A')), Fore.WHITE)}")
            print(f"{colored_output('📊 Estado: ' + str(result.get('estado', 'N/A')), Fore.WHITE)}")
            
            print()
            print(f"{colored_output('🔥 EVENTOS ESPERADOS:', Fore.MAGENTA)}")
            print(f"{colored_output('  1. 📢 marketing.eventos - Creación de campaña', Fore.CYAN)}")
            print(f"{colored_output('  2. 💰 comisiones.eventos - Configuración de comisiones', Fore.GREEN)}")
            print(f"{colored_output('  3. 👥 afiliados.eventos - Asignación de afiliados', Fore.YELLOW)}")
            print(f"{colored_output('  4. 🎯 conversiones.eventos - Setup para tracking', Fore.MAGENTA)}")
            print(f"{colored_output('  5. ⚙️  sistema.eventos - Eventos del sistema', Fore.WHITE)}")
            
        else:
            print(f"{colored_output('❌ Error en la respuesta: ' + str(response.status_code), Fore.RED)}")
            print(f"{colored_output('📄 Contenido: ' + response.text, Fore.RED)}")
            
    except requests.exceptions.ConnectionError:
        print(f"{colored_output(f'[{get_timestamp()}] ❌ Error: No se puede conectar al servicio de marketing', Fore.RED)}")
        print(f"{colored_output('💡 Verifica que docker-compose esté ejecutándose', Fore.YELLOW)}")
        
    except requests.exceptions.Timeout:
        print(f"{colored_output(f'[{get_timestamp()}] ⏱️ Error: Timeout en la solicitud', Fore.RED)}")
        
    except Exception as e:
        print(f"{colored_output('[' + get_timestamp() + '] ❌ Error inesperado: ' + str(e), Fore.RED)}")
    
    print()
    print(f"{colored_output('-'*60, Fore.WHITE)}")

if __name__ == "__main__":
    send_campaign()