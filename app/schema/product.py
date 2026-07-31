from pydantic import BaseModel,Field,AnyUrl,field_validator,model_validator,computed_field,EmailStr
from typing import Annotated,Literal,Optional,List
from uuid import UUID
from datetime import datetime


# Create Pydantic

class DimensionsCM(BaseModel):
     length:Annotated[float,Field(gt=0,strict=True,description="Length in cm")]
     width:Annotated[float,Field(gt=0,strict=True,description="Width in cm")]
     height:Annotated[float,Field(gt=0,strict=True,description="Height in cm")]

class Seller(BaseModel):
     id:UUID
     name:Annotated[
          str,
          Field(
               min_length=2,
               max_length=80,
               title="Seller Name",
               description="Name of the seller (2-60 chars)",
               examples=["Mi store","Apple store india"],
          ),
     ]

     email:EmailStr
     website:AnyUrl

     @field_validator("email",mode="after")
     @classmethod
     def validate_seller_email_domain(cls, value:EmailStr):
          allowed_domains=["mistore.in","hpworld.in"]
          domain=str(value).split("@")[-1].lower()
          if domain not in allowed_domains:
               raise ValueError(f"Seller email domain not allowed : {domain}")
     
          return value
     

     





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

     dimensions_cm: DimensionsCM
     seller:Seller
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

     @computed_field
     @property
     def final_price(self)->float:
          return round(self.price * (1-self.discount_person / 100),)

     @computed_field
     @property
     def volume_cm3(self)->float:
          d=self.dimensions_cm
          return round(d.length * d.width * d.height,2)



# Update pydantic


class DimensionsCMUpdate(BaseModel):
    length: Optional[float] = Field(gt=0)
    width: Optional[float] = Field(gt=0)
    height: Optional[float] = Field(gt=0)


class SellerUpdate(BaseModel):
    name: Optional[str] = Field(min_length=2, max_length=50)
    email: Optional[EmailStr]
    website: Optional[AnyUrl]

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(min_length=3, max_length=80)
    description: Optional[str] = Field(max_length=200)
    category: Optional[str]
    brand: Optional[str]

    price: Optional[float] = Field(gt=0)
    currency: Optional[Literal["INR"]]

    discount_percent: Optional[int] = Field(ge=0, le=90)
    stock: Optional[int] = Field(ge=0)
    is_active: Optional[bool]
    rating: Optional[float] = Field(ge=0, le=5)
    tags: Optional[List[str]] = Field(max_length=10)
    image_urls: Optional[List[AnyUrl]]

    dimensions_cm: Optional[DimensionsCMUpdate]
    seller: Optional[SellerUpdate]


    