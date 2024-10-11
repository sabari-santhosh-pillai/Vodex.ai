from fastapi import APIRouter, HTTPException
from models.item import ItemCreate, ItemResponse, ItemUpdate
from database import db
from bson import ObjectId
from datetime import datetime

router = APIRouter()

# POST /items - Create Item
@router.post("/items", response_model=ItemResponse)
async def create_item(item: ItemCreate):
    item_data = item.dict()
    item_data["insert_date"] = datetime.utcnow().date()
    try:
        result = await db.Items.insert_one(item_data)
        return {**item_data, "id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inserting item: {str(e)}")

# GET /items/{id} - Get Item by ID
@router.get("/items/{id}", response_model=ItemResponse)
async def get_item(id: str):
    item = await db.Items.find_one({"_id": ObjectId(id)})
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return {**item, "id": str(item["_id"])}

# GET /items/filter - Filter Items by Name
@router.get("/items/filter", response_model=list[ItemResponse])
async def filter_items(name: str):
    items = await db.Items.find({"name": name}).to_list(length=None)
    return items

# PUT /items/{id} - Update Item by ID
@router.put("/items/{id}", response_model=ItemResponse)
async def update_item(id: str, item_update: ItemUpdate):
    item = await db.Items.find_one({"_id": ObjectId(id)})
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    updated_data = {k: v for k, v in item_update.dict().items() if v is not None}
    await db.Items.update_one({"_id": ObjectId(id)}, {"$set": updated_data})
    updated_item = await db.Items.find_one({"_id": ObjectId(id)})
    
    return {**updated_item, "id": str(updated_item["_id"])}

# DELETE /items/{id} - Delete Item by ID
@router.delete("/items/{id}")
async def delete_item(id: str):
    result = await db.Items.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted successfully"}
