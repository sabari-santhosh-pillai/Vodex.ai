from fastapi import APIRouter, HTTPException
from models.clock_in import ClockInCreate, ClockInResponse, ClockInUpdate
from database import db
from bson import ObjectId
from datetime import datetime

router = APIRouter()

# POST /clock-in - Create Clock In Record
@router.post("/clock-in", response_model=ClockInResponse)
async def create_clock_in(record: ClockInCreate):
    record_data = record.dict()
    record_data["insert_datetime"] = datetime.utcnow()
    result = await db.clock_in_records.insert_one(record_data)
    return {**record_data, "id": str(result.inserted_id)}

# GET /clock-in/{id} - Get Clock In Record by ID
@router.get("/clock-in/{id}", response_model=ClockInResponse)
async def get_clock_in(id: str):
    record = await db.clock_in_records.find_one({"_id": ObjectId(id)})
    if record is None:
        raise HTTPException(status_code=404, detail="Clock In record not found")
    return {**record, "id": str(record["_id"])}

# GET /clock-in/filter - Filter Clock In Records by Email
@router.get("/clock-in/filter", response_model=list[ClockInResponse])
async def filter_clock_in(email: str):
    records = await db.clock_in_records.find({"email": email}).to_list(length=None)
    return records

# PUT /clock-in/{id} - Update Clock In Record by ID
@router.put("/clock-in/{id}", response_model=ClockInResponse)
async def update_clock_in(id: str, clock_in_update: ClockInUpdate):
    record = await db.clock_in_records.find_one({"_id": ObjectId(id)})
    if record is None:
        raise HTTPException(status_code=404, detail="Clock In record not found")
    
    updated_data = {k: v for k, v in clock_in_update.dict().items() if v is not None}
    await db.clock_in_records.update_one({"_id": ObjectId(id)}, {"$set": updated_data})
    updated_record = await db.clock_in_records.find_one({"_id": ObjectId(id)})
    
    return {**updated_record, "id": str(updated_record["_id"])}

# DELETE /clock-in/{id} - Delete Clock In Record by ID
@router.delete("/clock-in/{id}")
async def delete_clock_in(id: str):
    result = await db.clock_in_records.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Clock In record not found")
    return {"message": "Clock In record deleted successfully"}
