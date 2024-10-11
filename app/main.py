from fastapi import FastAPI
from dotenv import load_dotenv 
from routers import items, clock_in

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Include routers
app.include_router(items.router)
app.include_router(clock_in.router)
