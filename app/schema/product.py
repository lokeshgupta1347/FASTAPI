from pydantic import BaseModel,Field,AnyUrl,field_validator,model_validator,computed_field
from typing import Annotated,Literal,Optional,List
from uuid import UUID
from datetime import datetime





class Product(BaseModel):
     id:UUID
     sku:Annotated[str,Field(min_length=6,max_length=30,
                             title="SKU",
                             description="Stock Keeping Unit",
                             examples=["734-hjd-378-3d","sjnsnn-snj-njj"]
                             ),
                            ]
     name:str

     tags:Annotated[
          Optional[List[str]],
          Field(
             default=None,max_length=10,description="Up to 10 tags"
          ),
     ]

     image_urls:Annotated[
               list[AnyUrl],
               Field(
                  max_length=10,description="At least 1 image url"
               ),
          ]

     #dimensions_cm
     #seller
     created_at:datetime

     @field_validator("sku",mode="after")
     @classmethod
     def validate_sku_format(cls, value:str):
         if "-" not in value:
              raise ValueError("SKU must have '-' ")

         last=value.split("-")[-1]
         if not (len(last)==3 and last.isdigit()):
              raise ValueError("SKU must end with a 3-digit sequence like -234")

         return value

     @model_validator(mode="after")
     @classmethod
     def validate_business_rules(cls, model:"Product"):
        if model.stock==0 and model.is_active is True:
            raise ValueError("If stock is 0 , is-active must be false")

        if model.discount>0 and model.rating==0:
                    raise ValueError("Discounted product must have a rating (rating!=0)")

        return model