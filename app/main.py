from fastapi import FastAPI,HTTPException,Query,Path,Request,Depends
from services.products import get_all_products,add_products,remove_product,change_product
from pydantic import BaseModel,Field
from typing import Annotated
from schema.product import Product,ProductUpdate
from uuid import uuid4,UUID
from datetime import datetime
from dotenv import load_dotenv
import os
from fastapi.responses import JSONResponse


app=FastAPI()

load_dotenv()

@app.middleware("http")
async def lifecycle(request:Request,call_next):
    print("Before request")
    response=await call_next(request)
    # response["lifecycle"]="was inside"
    print("After request")
    return response


def common_logic():
     return "Hello There"

@app.get("/",response_model=dict)
def root(dep=Depends(common_logic)):
    DB_PATH=os.getenv("BASE_URL")
    # return {"message":"Welcome to fastapi.","dependency":dep,"data_path":DB_PATH}
    return JSONResponse(
         status_code=200,
         content={
              "message":"Welcome to fastapi.","dependency":dep,"data_path":DB_PATH
              
         }
    )

# @app.get("/products")
# def get_products():
    
#     return get_all_products()

@app.get("/products")
def list_products(name:str=Query(
    default=None,
    min_length=1,
    max_length=50,
    description="Search by products name (case insensitive)",

),
    sort_by_price:bool=Query(
        default=False,description="Sort products by price"
    ),
    order:str=Query(
        default="asc",description="Sort order when sort_by_price=true (asc,desc)"
    ),
    limit:int=Query(
    default=10,
    ge=1,
    le=100,
    description="Number of items to return",),

    offset:int=Query(
         default=0,
         ge=0,
         description="Pagination Offset"
    )

):
    products=get_all_products()

    if name:
        needle=name.strip().lower()
        products=[p for p in products if needle in p.get("name","").lower()]

    if not products:
            raise HTTPException(
                status_code=404,detail=f"No product found matching name={name}"
            )

    if sort_by_price:
         reverse=order=="desc"
         products=sorted(products,key=lambda p:p.get("price",0),reverse=reverse)

    total=len(products)
    products=products[offset:offset+limit]

    return {
        "total":total,
        "limit":limit,
        "items":products
    }


@app.get("/products/{product_id}")
def get_product_id(product_id:str=Path(
     ..., min_length=36,max_length=36,description="UUID of the products",expample="",
)):
    products=get_all_products()
    for product in products:
         if product["id"]==product_id:
              return product

    raise HTTPException(status_code=404,detail="Product not found!")


# class Product(BaseModel):
#      id:str
#      sku:Annotated[str,Field(min_length=6,max_length=30,
#                              title="SKU",
#                              description="Stock Keeping Unit",
#                              examples=["734-hjd-378-3d"]
#                              )]

@app.post("/products",status_code=201)
def create_product(product:Product):
    product_dict=product.model_dump(mode="json")
    product_dict["id"]=str(uuid4())
    product_dict["created_at"]=datetime.utcnow().isoformat()+"Z"
    try:
          add_products(product_dict)
    except ValueError as e:
         raise HTTPException(status_code=400,detail=str(e))
     
    return product.model_dump(mode="json")


@app.delete("/products/{product_id}")
def delete_product(
     product_id:UUID=Path(...,description="Product UUID")
):
    try:
        res=remove_product(str(product_id))
        return res
    
    except Exception as e:
             raise HTTPException(status_code=400,detail=str(e))

@app.put("/products/{products_id}")
def update_product(product_id :UUID=Path(...,description="Product UUID"),payload:ProductUpdate=...,):
     try:
          update_product=change_product(str(product_id),payload.model_dump(mode="json",exclude_unset=True))
          return update_product
     except ValueError as e:
          raise HTTPException(status_code=404,detail=str(e))
     
