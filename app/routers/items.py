from fastapi import APIRouter, HTTPException
from models.item import ItemCreate, ItemResponse, ItemUpdate
from database import db
from bson import ObjectId
from datetime import datetime
from loguru import logger
from bson.errors import InvalidId

router = APIRouter()

@router.post("/items", response_model=ItemResponse)
async def create_item(item: ItemCreate):
    item_data = item.dict()
    # Convert datetime.date to ISO format string
    item_data["expiry_date"] = item_data["expiry_date"].isoformat()
    item_data["insert_date"] = datetime.utcnow().date().isoformat()
    try:
        result = await db.Items.insert_one(item_data)
        return {**item_data, "id": str(result.inserted_id)}
    except Exception as e:
        logger.error(f"Error inserting item: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error inserting item: {str(e)}")

@router.get("/items/{id}", response_model=ItemResponse)
async def get_item(id: str):
    try:
        item = await db.Items.find_one({"_id": ObjectId(id)})
        if item is None:
            raise HTTPException(status_code=404, detail="Item not found")
        # Convert ISO format string back to date object
        item["expiry_date"] = datetime.fromisoformat(item["expiry_date"]).date()
        item["insert_date"] = datetime.fromisoformat(item["insert_date"]).date()
        return {**item, "id": str(item["_id"])}
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid item ID")

@router.get("/items/filter", response_model=list[ItemResponse])
async def filter_items(name: str):
    try:
        items = await db.Items.find({"name": name}).to_list(length=None)
        for item in items:
            # Convert ISO format string back to date object
            item["expiry_date"] = datetime.fromisoformat(item["expiry_date"]).date()
            item["insert_date"] = datetime.fromisoformat(item["insert_date"]).date()
        return [{**item, "id": str(item["_id"])} for item in items]
    except Exception as e:
        logger.error(f"Error filtering items: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error filtering items: {str(e)}")

@router.put("/items/{id}", response_model=ItemResponse)
async def update_item(id: str, item_update: ItemUpdate):
    try:
        item = await db.Items.find_one({"_id": ObjectId(id)})
        if item is None:
            raise HTTPException(status_code=404, detail="Item not found")
        
        updated_data = {k: v for k, v in item_update.dict().items() if v is not None}
        if "expiry_date" in updated_data:
            updated_data["expiry_date"] = updated_data["expiry_date"].isoformat()
        
        await db.Items.update_one({"_id": ObjectId(id)}, {"$set": updated_data})
        updated_item = await db.Items.find_one({"_id": ObjectId(id)})
        
        # Convert ISO format string back to date object
        updated_item["expiry_date"] = datetime.fromisoformat(updated_item["expiry_date"]).date()
        updated_item["insert_date"] = datetime.fromisoformat(updated_item["insert_date"]).date()
        
        return {**updated_item, "id": str(updated_item["_id"])}
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid item ID")
    except Exception as e:
        logger.error(f"Error updating item: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating item: {str(e)}")

@router.delete("/items/{id}")
async def delete_item(id: str):
    try:
        result = await db.Items.delete_one({"_id": ObjectId(id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"message": "Item deleted successfully"}
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid item ID")
    except Exception as e:
        logger.error(f"Error deleting item: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting item: {str(e)}")