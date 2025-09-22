import asyncio
from typing import Any, Dict, Optional, List
from abc import ABC, abstractmethod
import logging
import requests
from ...config import config

logger = logging.getLogger(__name__)


class ClienteHTTPException(Exception):
    """Excepción para errores del cliente HTTP"""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Any = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(message)


class BaseClienteHTTP(ABC):
    """Cliente HTTP base para comunicación con microservicios"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
    async def _hacer_request(
        self,
        metodo: str,
        endpoint: str,
        datos: Optional[Dict] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Realiza una petición HTTP con reintentos"""
        
        url = f"{self.base_url}{endpoint}"
        request_headers = self.session.headers.copy()
        if headers:
            request_headers.update(headers)
        
        for intento in range(config.reintentos):
            try:
                # Ejecutar en thread pool para no bloquear el loop asyncio
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.session.request(
                        metodo,
                        url,
                        json=datos,
                        params=params,
                        headers=request_headers,
                        timeout=config.timeout_segundos
                    )
                )
                
                if response.status_code >= 400:
                    raise ClienteHTTPException(
                        f"Error HTTP {response.status_code}: {response.text}",
                        status_code=response.status_code,
                        response_data=response.text
                    )
                
                return response.json()
                        
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout en intento {intento + 1} para {url}")
                if intento == config.reintentos - 1:
                    raise ClienteHTTPException(f"Timeout después de {config.reintentos} intentos")
                await asyncio.sleep(2 ** intento)  # Backoff exponencial
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Error de cliente en intento {intento + 1}: {e}")
                if intento == config.reintentos - 1:
                    raise ClienteHTTPException(f"Error de conexión: {str(e)}")
                await asyncio.sleep(2 ** intento)
    
    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Realiza una petición GET"""
        return await self._hacer_request("GET", endpoint, params=params)
    
    async def post(self, endpoint: str, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Realiza una petición POST"""
        return await self._hacer_request("POST", endpoint, datos=datos)
    
    async def put(self, endpoint: str, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Realiza una petición PUT"""
        return await self._hacer_request("PUT", endpoint, datos=datos)
    
    async def delete(self, endpoint: str) -> Dict[str, Any]:
        """Realiza una petición DELETE"""
        return await self._hacer_request("DELETE", endpoint)