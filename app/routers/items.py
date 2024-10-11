from fastapi import APIRouter, HTTPException, Query
from ..models.item import ItemCreate, ItemResponse, ItemUpdate
from ..database import db
from bson import ObjectId
from datetime import datetime, date
from loguru import logger
from bson.errors import InvalidId
from typing import Optional, List
from pydantic import ValidationError

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

@router.get("/items/filter", response_model=List[ItemResponse])
async def filter_items(
    email: Optional[str] = Query(None, description="Filter by exact email match"),
    expiry_date: Optional[date] = Query(None, description="Filter items expiring after this date"),
    insert_date: Optional[date] = Query(None, description="Filter items inserted after this date"),
    quantity: Optional[int] = Query(None, ge=0, description="Filter items with quantity greater than or equal to this number")
):
    try:
        # Initialize filter dictionary
        filter_query = {}

        # Add filters based on provided parameters
        if email:
            filter_query["email"] = email
        
        if expiry_date:
            filter_query["expiry_date"] = {
                "$gte": expiry_date.isoformat()
            }
        
        if insert_date:
            filter_query["insert_date"] = {
                "$gte": insert_date.isoformat()
            }
        
        if quantity is not None:
            filter_query["quantity"] = {
                "$gte": quantity
            }

        logger.debug(f"Applying filter: {filter_query}")
        
        # Execute the query
        cursor = db.Items.find(filter_query)
        items = await cursor.to_list(length=None)
        
        # Process the results
        processed_items = []
        for item in items:
            try:
                processed_item = {
                    "id": str(item["_id"]),
                    "name": item["name"],
                    "email": item["email"],
                    "item_name": item["item_name"],
                    "quantity": item["quantity"],
                    "expiry_date": datetime.fromisoformat(item["expiry_date"]).date(),
                    "insert_date": datetime.fromisoformat(item["insert_date"]).date()
                }
                processed_items.append(processed_item)
            except KeyError as ke:
                logger.error(f"Missing required field in item {item.get('_id', 'unknown')}: {ke}")
                continue
            except Exception as e:
                logger.error(f"Error processing item {item.get('_id', 'unknown')}: {str(e)}")
                continue
        
        return processed_items

    except Exception as e:
        logger.error(f"Error in filter_items: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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