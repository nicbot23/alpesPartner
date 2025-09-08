from decimal import Decimal
from aeroalpes.modulos.comisiones.dominio.agregados import Comision
from aeroalpes.modulos.comisiones.dominio.objetos_valor.dinero import Dinero

class FabricaComisiones:
    
    @staticmethod
    def crear_calculada(conversion_id, affiliate_id, campaign_id, amount:float, currency:str, pct:float)->Comision:
        
        return Comision.calcular(conversion_id, 
                                 affiliate_id, 
                                 campaign_id, 
                                 Dinero(Decimal(str(amount)), currency.upper()), 
                                 Decimal(str(pct)))
