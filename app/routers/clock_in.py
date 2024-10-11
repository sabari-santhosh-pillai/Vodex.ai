from fastapi import APIRouter, HTTPException
from models.clock_in import ClockInCreate, ClockInResponse, ClockInUpdate
from database import db
from bson import ObjectId
from datetime import datetime
from loguru import logger
from bson.errors import InvalidId

router = APIRouter()

@router.post("/clock-in", response_model=ClockInResponse)
async def create_clock_in(record: ClockInCreate):
    record_data = record.dict()
    record_data["insert_datetime"] = datetime.utcnow()
    try:
        result = await db.user_clock_in_records.insert_one(record_data)
        return {**record_data, "id": str(result.inserted_id)}
    except Exception as e:
        logger.error(f"Error inserting clock-in record: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error inserting clock-in record: {str(e)}")

@router.get("/clock-in/{id}", response_model=ClockInResponse)
async def get_clock_in(id: str):
    try:
        record = await db.user_clock_in_records.find_one({"_id": ObjectId(id)})
        if record is None:
            raise HTTPException(status_code=404, detail="Clock In record not found")
        return {**record, "id": str(record["_id"])}
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid clock-in record ID")

@router.get("/clock-in/filter", response_model=list[ClockInResponse])
async def filter_clock_in(email: str):
    try:
        records = await db.user_clock_in_records.find({"email": email}).to_list(length=None)
        return [{**record, "id": str(record["_id"])} for record in records]
    except Exception as e:
        logger.error(f"Error filtering clock-in records: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error filtering clock-in records: {str(e)}")

@router.put("/clock-in/{id}", response_model=ClockInResponse)
async def update_clock_in(id: str, clock_in_update: ClockInUpdate):
    try:
        record = await db.user_clock_in_records.find_one({"_id": ObjectId(id)})
        if record is None:
            raise HTTPException(status_code=404, detail="Clock In record not found")
        
        updated_data = {k: v for k, v in clock_in_update.dict().items() if v is not None}
        await db.user_clock_in_records.update_one({"_id": ObjectId(id)}, {"$set": updated_data})
        updated_record = await db.user_clock_in_records.find_one({"_id": ObjectId(id)})
        
        return {**updated_record, "id": str(updated_record["_id"])}
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid clock-in record ID")
    except Exception as e:
        logger.error(f"Error updating clock-in record: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating clock-in record: {str(e)}")

@router.delete("/clock-in/{id}")
async def delete_clock_in(id: str):
    try:
        result = await db.user_clock_in_records.delete_one({"_id": ObjectId(id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Clock In record not found")
        return {"message": "Clock In record deleted successfully"}
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid clock-in record ID")
    except Exception as e:
        logger.error(f"Error deleting clock-in record: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting clock-in record: {str(e)}")