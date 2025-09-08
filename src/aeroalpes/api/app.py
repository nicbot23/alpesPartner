from flask import Flask, request, jsonify
from aeroalpes.modulos.comisiones.aplicacion.dto import CrearComisionDTO, AprobarComisionDTO
from aeroalpes.modulos.comisiones.aplicacion.comandos.crear_comision import CrearComision
from aeroalpes.modulos.comisiones.aplicacion.comandos.aprobar_comision import AprobarComision
from aeroalpes.modulos.comisiones.aplicacion.queries.comision_por_conversion import ComisionPorConversion
from aeroalpes.seedwork.aplicacion.mediador import ejecutar_comando, ejecutar_query
from aeroalpes.modulos.comisiones.infraestructura.modelos import Base
from aeroalpes.seedwork.infraestructura.db import engine
from aeroalpes.modulos.comisiones.aplicacion import handlers as _handlers  # noqa

app=Flask(__name__)
Base.metadata.create_all(bind=engine)

@app.post('/commissions/calculate')
def calculate():
    dto=CrearComisionDTO(**request.get_json(force=True))
    res=ejecutar_comando(CrearComision(**dto.model_dump()))
    return jsonify(res),201

@app.post('/commissions/approve')
def approve():
    dto=AprobarComisionDTO(**request.get_json(force=True))
    res=ejecutar_comando(AprobarComision(**dto.model_dump()))
    return jsonify(res),202

@app.get('/commissions/by-conversion/<cid>')
def by_conv(cid:str):
    res=ejecutar_query(ComisionPorConversion(conversionId=cid)); return jsonify(res or {}),200
@app.get('/health')
def health(): return {'ok':True}
