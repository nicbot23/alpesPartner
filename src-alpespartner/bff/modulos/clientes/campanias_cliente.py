from typing import Any, Dict, List, Optional
from .base_cliente import BaseClienteHTTP
from ...config import config


class ClienteCampanias(BaseClienteHTTP):
    """Cliente HTTP para el microservicio de campanias"""
    
    def __init__(self):
        super().__init__(config.url_campanias)
    
    # Endpoints de gestión básica de campanias
    async def crear_campania(self, datos_campania: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una nueva campaña"""
        return await self.post("/campanias/", datos_campania)
    
    async def obtener_campania(self, campania_id: str) -> Dict[str, Any]:
        """Obtiene una campaña por ID"""
        return await self.get(f"/campanias/{campania_id}")
    
    async def listar_campanias(self) -> List[Dict[str, Any]]:
        return await self.get("/campanias/")
    
    # async def listar_campanias(
    #     self,
    #     estado: Optional[str] = None,
    #     tipo: Optional[str] = None,
    #     fecha_inicio: Optional[str] = None,
    #     fecha_fin: Optional[str] = None
    # ) -> Dict[str, Any]:
    #     """Lista campanias con filtros opcionales"""
    #     params = {}
    #     if estado:
    #         params["estado"] = estado
    #     if tipo:
    #         params["tipo"] = tipo
    #     if fecha_inicio:
    #         params["fecha_inicio"] = fecha_inicio
    #     if fecha_fin:
    #         params["fecha_fin"] = fecha_fin
        
    #     return await self.get("/campanias/", params=params)
    
    async def activar_campania(self, campania_id: str) -> Dict[str, Any]:
        """Activa una campaña"""
        return await self.put(f"/campanias/{campania_id}/activar", {})
    
    async def pausar_campania(self, campania_id: str) -> Dict[str, Any]:
        """Pausa una campaña"""
        return await self.put(f"/campanias/{campania_id}/pausar", {})
    
    async def finalizar_campania(self, campania_id: str) -> Dict[str, Any]:
        """Finaliza una campaña"""
        return await self.put(f"/campanias/{campania_id}/finalizar", {})
    
###SAGAS###

    # Endpoints para sagas (funcionalidad principal del BFF)
    async def lanzar_campania_completa(self, datos_saga: Dict[str, Any]) -> Dict[str, Any]:
        """Inicia una saga completa de campaña Este es el endpoint principal que el BFF usa para delegar sagas"""
        return await self.post("/campanias/lanzar-completa", datos_saga)
    
    async def consultar_estado_saga(self, saga_id: str) -> Dict[str, Any]:
        """Consulta el estado actual de una saga"""
        return await self.get(f"/sagas/{saga_id}/estado")
    
    async def obtener_progreso_saga(self, saga_id: str) -> Dict[str, Any]:
        """Obtiene el progreso detallado de una saga"""
        return await self.get(f"/sagas/{saga_id}/progreso")
    
    async def cancelar_saga(self, saga_id: str) -> Dict[str, Any]:
        """Cancela una saga en progreso"""
        return await self.post(f"/sagas/{saga_id}/cancelar", {})
    
    # Gestión de afiliados en campanias ---------
    async def agregar_afiliado_campania(self, campania_id: str, afiliado_id: str) -> Dict[str, Any]:
        """Agrega un afiliado a una campaña"""
        return await self.post(f"/campanias/{campania_id}/afiliados", {"afiliado_id": afiliado_id})
    
    async def remover_afiliado_campania(self, campania_id: str, afiliado_id: str) -> Dict[str, Any]:
        """Remueve un afiliado de una campaña"""
        return await self.delete(f"/campanias/{campania_id}/afiliados/{afiliado_id}")
    
    async def listar_afiliados_campania(self, campania_id: str) -> Dict[str, Any]:
        """Lista los afiliados de una campaña"""
        return await self.get(f"/campanias/{campania_id}/afiliados")


# Instancia singleton del cliente
cliente_campanias = ClienteCampanias()