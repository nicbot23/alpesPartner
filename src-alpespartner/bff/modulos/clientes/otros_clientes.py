from typing import Any, Dict, List, Optional
from .base_cliente import BaseClienteHTTP
from ...config import config


class ClienteAfiliados(BaseClienteHTTP):
    """Cliente HTTP para el microservicio de afiliados"""
    
    def __init__(self):
        super().__init__(config.url_afiliados)
    
    async def obtener_afiliado(self, afiliado_id: str) -> Dict[str, Any]:
        """Obtiene información de un afiliado"""
        return await self.get(f"/afiliados/{afiliado_id}")
    
    async def listar_afiliados(
        self,
        activo: Optional[bool] = None,
        categoria: Optional[str] = None
    ) -> Dict[str, Any]:
        """Lista afiliados con filtros opcionales"""
        params = {}
        if activo is not None:
            params["activo"] = activo
        if categoria:
            params["categoria"] = categoria
        
        return await self.get("/afiliados/", params=params)
    
    async def buscar_afiliados_elegibles(self, criterios: Dict[str, Any]) -> Dict[str, Any]:
        """Busca afiliados elegibles para una campaña"""
        return await self.post("/afiliados/buscar-elegibles", criterios)


class ClienteComisiones(BaseClienteHTTP):
    """Cliente HTTP para el microservicio de comisiones"""
    
    def __init__(self):
        super().__init__(config.url_comisiones)
    
    async def obtener_comision(self, comision_id: str) -> Dict[str, Any]:
        """Obtiene información de una comisión"""
        return await self.get(f"/comisiones/{comision_id}")
    
    async def calcular_comision(self, datos_calculo: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula comisión para una venta"""
        return await self.post("/comisiones/calcular", datos_calculo)
    
    async def listar_comisiones_afiliado(self, afiliado_id: str) -> Dict[str, Any]:
        """Lista comisiones de un afiliado"""
        return await self.get(f"/comisiones/afiliado/{afiliado_id}")


class ClienteConversiones(BaseClienteHTTP):
    """Cliente HTTP para el microservicio de conversiones"""
    
    def __init__(self):
        super().__init__(config.url_conversiones)
    
    async def obtener_conversion(self, conversion_id: str) -> Dict[str, Any]:
        """Obtiene información de una conversión"""
        return await self.get(f"/conversiones/{conversion_id}")
    
    async def listar_conversiones_campania(self, campania_id: str) -> Dict[str, Any]:
        """Lista conversiones de una campaña"""
        return await self.get(f"/conversiones/campania/{campania_id}")
    
    async def obtener_metricas_campania(self, campania_id: str) -> Dict[str, Any]:
        """Obtiene métricas de conversión de una campaña"""
        return await self.get(f"/conversiones/campania/{campania_id}/metricas")


class ClienteNotificaciones(BaseClienteHTTP):
    """Cliente HTTP para el microservicio de notificaciones"""
    
    def __init__(self):
        super().__init__(config.url_notificaciones)
    
    async def enviar_notificacion(self, datos_notificacion: Dict[str, Any]) -> Dict[str, Any]:
        """Envía una notificación"""
        return await self.post("/notificaciones/enviar", datos_notificacion)
    
    async def obtener_historial_notificaciones(
        self,
        destinatario: Optional[str] = None,
        tipo: Optional[str] = None
    ) -> Dict[str, Any]:
        """Obtiene historial de notificaciones"""
        params = {}
        if destinatario:
            params["destinatario"] = destinatario
        if tipo:
            params["tipo"] = tipo
        
        return await self.get("/notificaciones/historial", params=params)


# Instancias singleton de los clientes
cliente_afiliados = ClienteAfiliados()
cliente_comisiones = ClienteComisiones()
cliente_conversiones = ClienteConversiones()
cliente_notificaciones = ClienteNotificaciones()