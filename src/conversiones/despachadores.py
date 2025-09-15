"""
Despachadores para publicación de eventos en Pulsar
"""
import logging
import json
import pulsar
from conversiones.config import settings
from conversiones.eventos import EventoConversion

class Despachador:
    """Despachador de eventos para el microservicio Conversiones"""
    
    def __init__(self):
        self.pulsar_url = settings.PULSAR_URL
        self.logger = logging.getLogger(__name__)
    
    def publicar_mensaje(self, mensaje, topico: str):
        """
        Publicar un mensaje en un tópico específico
        """
        client = None
        try:
            client = pulsar.Client(self.pulsar_url)
            producer = client.create_producer(topico)
            
            # Serializar el mensaje
            if hasattr(mensaje, '__dict__'):
                mensaje_json = json.dumps(mensaje.__dict__, default=str)
            else:
                mensaje_json = json.dumps(mensaje, default=str)
            
            # Enviar mensaje
            producer.send(mensaje_json.encode('utf-8'))
            
            self.logger.info(f"📤 Mensaje enviado exitosamente al tópico: {topico}")
            
            producer.close()
            
        except Exception as e:
            self.logger.error(f"❌ Error enviando mensaje al tópico {topico}: {str(e)}")
            raise
        finally:
            if client:
                client.close()
    
    def publicar_evento_conversion(self, evento: EventoConversion):
        """Publicar evento de conversión"""
        self.publicar_mensaje(evento, "evento-conversion")
    
    def publicar_comando_detectar_conversion(self, comando):
        """Publicar comando detectar conversión"""
        self.publicar_mensaje(comando, "comando-detectar-conversion")
    
    def publicar_comando_validar_conversion(self, comando):
        """Publicar comando validar conversión"""
        self.publicar_mensaje(comando, "comando-validar-conversion")
    
    def publicar_comando_confirmar_conversion(self, comando):
        """Publicar comando confirmar conversión"""
        self.publicar_mensaje(comando, "comando-confirmar-conversion")
    
    def publicar_comando_rechazar_conversion(self, comando):
        """Publicar comando rechazar conversión"""
        self.publicar_mensaje(comando, "comando-rechazar-conversion")
    
    def publicar_comando_cancelar_conversion(self, comando):
        """Publicar comando cancelar conversión"""
        self.publicar_mensaje(comando, "comando-cancelar-conversion")