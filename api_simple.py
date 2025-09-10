#!/usr/bin/env python3

"""
Versión simplificada de la API para pruebas CDC
Sin dependencias complejas de eventos, solo enfocada en probar el outbox pattern
"""

import uuid
import json
from datetime import datetime
from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'mysql',
    'port': 3306,
    'user': 'alpes',
    'password': 'alpes',
    'database': 'alpes'
}

def get_db_connection():
    """Obtener conexión a la base de datos"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error conectando a MySQL: {e}")
        return None

def insert_outbox_event(aggregate_id, event_type, payload):
    """Insertar evento en la tabla outbox_event para CDC"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        query = """
        INSERT INTO outbox_event (
            id, aggregate_type, aggregate_id, event_type, payload, occurred_at, published
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        event_id = str(uuid.uuid4())
        occurred_at = datetime.utcnow()
        
        cursor.execute(query, (
            event_id,
            'Commission',
            aggregate_id,
            event_type,
            json.dumps(payload),
            occurred_at,
            False
        ))
        
        connection.commit()
        print(f"✅ Evento insertado en outbox: {event_type} para {aggregate_id}")
        return True
        
    except Error as e:
        print(f"❌ Error insertando evento: {e}")
        return False
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/health')
def health():
    """Endpoint de salud"""
    return {'status': 'ok', 'message': 'API simplificada para CDC funcionando'}

@app.route('/commissions/calculate', methods=['POST'])
def calculate_commission():
    """Endpoint simplificado para calcular comisión"""
    try:
        data = request.get_json()
        
        # Validaciones básicas
        required_fields = ['conversionId', 'affiliateId', 'campaignId', 'grossAmount', 'currency']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo requerido: {field}'}), 400
        
        # Generar ID de comisión
        commission_id = str(uuid.uuid4())
        
        # Simular cálculo de comisión (12.5%)
        gross_amount = float(data['grossAmount'])
        percentage = 12.5
        net_amount = gross_amount * (percentage / 100)
        
        # Insertar en tabla commission
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                insert_commission = """
                INSERT INTO commission (
                    id, conversion_id, affiliate_id, campaign_id, 
                    gross_amount, gross_currency, percentage, 
                    net_amount, net_currency, status, calculated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(insert_commission, (
                    commission_id,
                    data['conversionId'],
                    data['affiliateId'], 
                    data['campaignId'],
                    gross_amount,
                    data['currency'],
                    percentage,
                    net_amount,
                    data['currency'],
                    'CALCULATED',
                    datetime.utcnow()
                ))
                
                connection.commit()
                print(f"✅ Comisión creada: {commission_id}")
                
            except Error as e:
                print(f"❌ Error creando comisión: {e}")
                return jsonify({'error': 'Error creando comisión'}), 500
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
        
        # Crear evento para outbox (CDC)
        event_payload = {
            "eventVersion": 2,
            "commissionId": commission_id,
            "conversionId": data['conversionId'],
            "affiliateId": data['affiliateId'],
            "campaignId": data['campaignId'],
            "grossAmount": {
                "amount": gross_amount,
                "currency": data['currency']
            },
            "percentage": percentage,
            "netAmount": {
                "amount": net_amount,
                "currency": data['currency']
            },
            "calculatedAt": datetime.utcnow().isoformat() + 'Z'
        }
        
        # Insertar evento en outbox
        if insert_outbox_event(commission_id, 'CommissionCalculated', event_payload):
            return jsonify({
                'commissionId': commission_id,
                'status': 'calculated',
                'netAmount': net_amount,
                'message': 'Comisión calculada y evento enviado al CDC'
            }), 201
        else:
            return jsonify({
                'commissionId': commission_id,
                'status': 'calculated',
                'netAmount': net_amount,
                'warning': 'Comisión creada pero evento CDC falló'
            }), 201
            
    except Exception as e:
        print(f"❌ Error en calculate_commission: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/commissions/approve', methods=['POST'])
def approve_commission():
    """Endpoint simplificado para aprobar comisión"""
    try:
        data = request.get_json()
        
        if 'commissionId' not in data:
            return jsonify({'error': 'Campo requerido: commissionId'}), 400
            
        commission_id = data['commissionId']
        
        # Actualizar estado en base de datos
        connection = get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                update_query = """
                UPDATE commission 
                SET status = 'APPROVED', approved_at = %s 
                WHERE id = %s
                """
                
                approved_at = datetime.utcnow()
                cursor.execute(update_query, (approved_at, commission_id))
                
                if cursor.rowcount == 0:
                    return jsonify({'error': 'Comisión no encontrada'}), 404
                    
                connection.commit()
                print(f"✅ Comisión aprobada: {commission_id}")
                
            except Error as e:
                print(f"❌ Error aprobando comisión: {e}")
                return jsonify({'error': 'Error aprobando comisión'}), 500
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
        
        # Crear evento para outbox (CDC)
        event_payload = {
            "eventVersion": 1,
            "commissionId": commission_id,
            "approvedAt": datetime.utcnow().isoformat() + 'Z'
        }
        
        # Insertar evento en outbox
        if insert_outbox_event(commission_id, 'CommissionApproved', event_payload):
            return jsonify({
                'commissionId': commission_id,
                'status': 'approved',
                'message': 'Comisión aprobada y evento enviado al CDC'
            }), 200
        else:
            return jsonify({
                'commissionId': commission_id,
                'status': 'approved',
                'warning': 'Comisión aprobada pero evento CDC falló'
            }), 200
            
    except Exception as e:
        print(f"❌ Error en approve_commission: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/commissions/by-conversion/<conversion_id>')
def get_commission_by_conversion(conversion_id):
    """Obtener comisión por conversion_id"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Error de conexión a base de datos'}), 500
            
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT id, conversion_id, affiliate_id, campaign_id,
               gross_amount, gross_currency, percentage,
               net_amount, net_currency, status,
               calculated_at, approved_at
        FROM commission 
        WHERE conversion_id = %s
        """
        
        cursor.execute(query, (conversion_id,))
        result = cursor.fetchone()
        
        if result:
            # Convertir datetime a string para JSON
            if result['calculated_at']:
                result['calculated_at'] = result['calculated_at'].isoformat()
            if result['approved_at']:
                result['approved_at'] = result['approved_at'].isoformat()
                
            return jsonify(result), 200
        else:
            return jsonify({}), 200
            
    except Error as e:
        print(f"❌ Error consultando comisión: {e}")
        return jsonify({'error': 'Error consultando comisión'}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/debug/outbox')
def debug_outbox():
    """Endpoint para depurar tabla outbox_event"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Error de conexión'}), 500
            
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, aggregate_type, aggregate_id, event_type, 
                   payload, occurred_at, published
            FROM outbox_event 
            ORDER BY occurred_at DESC 
            LIMIT 10
        """)
        
        results = cursor.fetchall()
        
        # Convertir datetime a string
        for result in results:
            if result['occurred_at']:
                result['occurred_at'] = result['occurred_at'].isoformat()
                
        return jsonify({
            'total_events': len(results),
            'events': results
        }), 200
        
    except Error as e:
        print(f"❌ Error consultando outbox: {e}")
        return jsonify({'error': 'Error consultando outbox'}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
