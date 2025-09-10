from pydantic import BaseModel, Field
class CrearComisionDTO(BaseModel):
    conversionId:str; 
    affiliateId:str; 
    campaignId:str; 
    grossAmount:float; 
    currency:str=Field(min_length=3,max_length=3)

class AprobarComisionDTO(BaseModel): 
    commissionId:str
