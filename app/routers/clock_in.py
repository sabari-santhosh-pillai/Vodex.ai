from fastapi import APIRouter, HTTPException, Query, Request
from models.clock_in import ClockInCreate, ClockInResponse, ClockInUpdate
from database import db
from bson import ObjectId
from datetime import datetime
from loguru import logger
from bson.errors import InvalidId

router = APIRouter()

@router.post("/", response_model=ClockInResponse)
async def create_clock_in(record: ClockInCreate):
    logger.info(f"Attempting to create clock-in record: {record}")
    record_data = record.dict()
    record_data["insert_datetime"] = datetime.utcnow()
    try:
        result = await db.user_clock_in_records.insert_one(record_data)
        logger.info(f"Successfully created clock-in record with ID: {result.inserted_id}")
        return {**record_data, "id": str(result.inserted_id)}
    except Exception as e:
        logger.error(f"Error inserting clock-in record: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error inserting clock-in record: {str(e)}")

@router.get("/filter", response_model=list[ClockInResponse])
async def filter_clock_in(
    request: Request,
    email: str = Query(None, description="Filter by exact email match"),
    location: str = Query(None, description="Filter by exact location match"),
    after_datetime: datetime = Query(None, description="Filter clock-ins after this date and time")
):
    logger.info(f"Received filter request: email={email}, location={location}, after_datetime={after_datetime}")
    logger.info(f"Full request path: {request.url.path}")
    logger.info(f"Full query params: {request.query_params}")
    
    try:
        filter_query = {}
        if email:
            filter_query["email"] = email
        if location:
            filter_query["location"] = location
        if after_datetime:
            filter_query["insert_datetime"] = {"$gt": after_datetime}

        logger.info(f"Applying filter query: {filter_query}")
        records = await db.user_clock_in_records.find(filter_query).to_list(length=None)
        logger.info(f"Found {len(records)} matching records")
        return [{**record, "id": str(record["_id"])} for record in records]
    except Exception as e:
        logger.error(f"Error filtering clock-in records: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error filtering clock-in records: {str(e)}")

@router.get("/{id}", response_model=ClockInResponse)
async def get_clock_in(id: str):
    logger.info(f"Attempting to retrieve clock-in record with ID: {id}")
    try:
        record = await db.user_clock_in_records.find_one({"_id": ObjectId(id)})
        if record is None:
            logger.warning(f"Clock-in record not found for ID: {id}")
            raise HTTPException(status_code=404, detail="Clock In record not found")
        logger.info(f"Successfully retrieved clock-in record with ID: {id}")
        return {**record, "id": str(record["_id"])}
    except InvalidId:
        logger.error(f"Invalid clock-in record ID provided: {id}")
        raise HTTPException(status_code=400, detail="Invalid clock-in record ID")

@router.put("/{id}", response_model=ClockInResponse)
async def update_clock_in(id: str, clock_in_update: ClockInUpdate):
    logger.info(f"Attempting to update clock-in record with ID: {id}")
    try:
        record = await db.user_clock_in_records.find_one({"_id": ObjectId(id)})
        if record is None:
            logger.warning(f"Clock-in record not found for update, ID: {id}")
            raise HTTPException(status_code=404, detail="Clock In record not found")
        
        updated_data = {k: v for k, v in clock_in_update.dict().items() if v is not None}
        await db.user_clock_in_records.update_one({"_id": ObjectId(id)}, {"$set": updated_data})
        updated_record = await db.user_clock_in_records.find_one({"_id": ObjectId(id)})
        
        logger.info(f"Successfully updated clock-in record with ID: {id}")
        return {**updated_record, "id": str(updated_record["_id"])}
    except InvalidId:
        logger.error(f"Invalid clock-in record ID provided for update: {id}")
        raise HTTPException(status_code=400, detail="Invalid clock-in record ID")
    except Exception as e:
        logger.error(f"Error updating clock-in record: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating clock-in record: {str(e)}")

@router.delete("/{id}")
async def delete_clock_in(id: str):
    logger.info(f"Attempting to delete clock-in record with ID: {id}")
    try:
        result = await db.user_clock_in_records.delete_one({"_id": ObjectId(id)})
        if result.deleted_count == 0:
            logger.warning(f"Clock-in record not found for deletion, ID: {id}")
            raise HTTPException(status_code=404, detail="Clock In record not found")
        logger.info(f"Successfully deleted clock-in record with ID: {id}")
        return {"message": "Clock In record deleted successfully"}
    except InvalidId:
        logger.error(f"Invalid clock-in record ID provided for deletion: {id}")
        raise HTTPException(status_code=400, detail="Invalid clock-in record ID")
    except Exception as e:
        logger.error(f"Error deleting clock-in record: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting clock-in record: {str(e)}")