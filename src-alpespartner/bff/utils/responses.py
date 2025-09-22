from typing import Any, Dict, Optional
from datetime import datetime
from fastapi import status
from fastapi.responses import JSONResponse


class RespuestaBFF:
    """Clase para estandarizar respuestas del BFF"""
    
    @staticmethod
    def exitosa(
        datos: Any,
        mensaje: str = "Operación exitosa",
        codigo_estado: int = status.HTTP_200_OK
    ) -> JSONResponse:
        """Crea una respuesta exitosa estándar"""
        respuesta = {
            "exito": True,
            "mensaje": mensaje,
            "datos": datos,
            "timestamp": datetime.utcnow().isoformat(),
            "codigo": codigo_estado
        }
        return JSONResponse(content=respuesta, status_code=codigo_estado)
    
    @staticmethod
    def error(
        mensaje: str,
        detalle: Optional[str] = None,
        codigo_estado: int = status.HTTP_400_BAD_REQUEST,
        datos_adicionales: Optional[Dict] = None
    ) -> JSONResponse:
        """Crea una respuesta de error estándar"""
        respuesta = {
            "exito": False,
            "mensaje": mensaje,
            "detalle": detalle,
            "timestamp": datetime.utcnow().isoformat(),
            "codigo": codigo_estado
        }
        
        if datos_adicionales:
            respuesta.update(datos_adicionales)
        
        return JSONResponse(content=respuesta, status_code=codigo_estado)
    
    @staticmethod
    def saga_iniciada(
        saga_id: str,
        campania_id: Optional[str] = None,
        mensaje: str = "Saga iniciada exitosamente"
    ) -> JSONResponse:
        """Respuesta específica para sagas iniciadas"""
        datos = {
            "saga_id": saga_id,
            "estado": "INICIADA",
            "campania_id": campania_id,
            "urls_seguimiento": {
                "estado": f"/bff/sagas/{saga_id}/estado",
                "progreso": f"/bff/sagas/{saga_id}/progreso",
                "cancelar": f"/bff/sagas/{saga_id}/cancelar"
            }
        }
        
        return RespuestaBFF.exitosa(
            datos=datos,
            mensaje=mensaje,
            codigo_estado=status.HTTP_202_ACCEPTED
        )
    
    @staticmethod
    def saga_estado(
        saga_id: str,
        estado: str,
        progreso: Optional[int] = None,
        detalles: Optional[Dict] = None
    ) -> JSONResponse:
        """Respuesta específica para estado de saga"""
        datos = {
            "saga_id": saga_id,
            "estado": estado,
            "progreso_porcentaje": progreso,
            "detalles": detalles or {}
        }
        
        return RespuestaBFF.exitosa(
            datos=datos,
            mensaje=f"Estado de saga: {estado}"
        )
    
    @staticmethod
    def lista_paginada(
        elementos: list,
        total: int,
        pagina: int = 1,
        tamanio_pagina: int = 10,
        mensaje: str = "Lista obtenida exitosamente"
    ) -> JSONResponse:
        """Respuesta para listas paginadas"""
        datos = {
            "elementos": elementos,
            "paginacion": {
                "total": total,
                "pagina": pagina,
                "tamanio_pagina": tamanio_pagina,
                "total_paginas": (total + tamanio_pagina - 1) // tamanio_pagina,
                "tiene_anterior": pagina > 1,
                "tiene_siguiente": pagina * tamanio_pagina < total
            }
        }
        
        return RespuestaBFF.exitosa(datos=datos, mensaje=mensaje)
    
    @staticmethod
    def dashboard(
        resumen: Dict,
        datos_principales: Dict,
        mensaje: str = "Dashboard obtenido exitosamente"
    ) -> JSONResponse:
        """Respuesta específica para dashboard"""
        datos = {
            "resumen": resumen,
            "datos": datos_principales,
            "ultima_actualizacion": datetime.utcnow().isoformat()
        }
        
        return RespuestaBFF.exitosa(datos=datos, mensaje=mensaje)


class ManejadorErroresBFF:
    """Manejador centralizado de errores del BFF"""
    
    @staticmethod
    def procesar_error_microservicio(e: Exception, microservicio: str) -> JSONResponse:
        """Procesa errores de comunicación con microservicios"""
        if "timeout" in str(e).lower():
            return RespuestaBFF.error(
                mensaje=f"Timeout al comunicarse con {microservicio}",
                detalle="El microservicio no respondió en el tiempo esperado",
                codigo_estado=status.HTTP_504_GATEWAY_TIMEOUT
            )
        elif "404" in str(e):
            return RespuestaBFF.error(
                mensaje="Recurso no encontrado",
                detalle=f"El recurso solicitado no existe en {microservicio}",
                codigo_estado=status.HTTP_404_NOT_FOUND
            )
        elif "500" in str(e):
            return RespuestaBFF.error(
                mensaje=f"Error interno en {microservicio}",
                detalle="Error interno del microservicio",
                codigo_estado=status.HTTP_502_BAD_GATEWAY
            )
        else:
            return RespuestaBFF.error(
                mensaje=f"Error de comunicación con {microservicio}",
                detalle=str(e),
                codigo_estado=status.HTTP_502_BAD_GATEWAY
            )
    
    @staticmethod
    def error_validacion(campo: str, valor: Any, razon: str) -> JSONResponse:
        """Error de validación de datos"""
        return RespuestaBFF.error(
            mensaje="Error de validación",
            detalle=f"Campo '{campo}' con valor '{valor}': {razon}",
            codigo_estado=status.HTTP_422_UNPROCESSABLE_ENTITY,
            datos_adicionales={"campo": campo, "valor": valor}
        )
    
    @staticmethod
    def error_saga_no_encontrada(saga_id: str) -> JSONResponse:
        """Error específico para saga no encontrada"""
        return RespuestaBFF.error(
            mensaje="Saga no encontrada",
            detalle=f"No se encontró la saga con ID: {saga_id}",
            codigo_estado=status.HTTP_404_NOT_FOUND,
            datos_adicionales={"saga_id": saga_id}
        )