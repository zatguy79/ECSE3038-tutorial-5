import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["ecse3038"]
devices = db["tutorial5"]

app = FastAPI()


class Device(BaseModel):
    name: str
    room: str
    temp: float
    online: bool


# Your handlers go below this line.

readings = []


@app.get("/devices")
def get_devices():
    return list(devices.find({}, {"_id": 0}))

@app.get("/devices/{name}")
def get_device(name: str):
    device = devices.find_one({"name": name}, {"_id": 0})
    if device is None:
        raise HTTPException(status_code=404, detail="No device called " + name)
    return device

@app.post("/devices", status_code=201)
def create_device(device: Device):
    new_device = device.model_dump()
    try:
        devices.insert_one(new_device)    
    except DuplicateKeyError:
        raise HTTPException(
            status_code=409,
            detail=f"A device named '{device.name}' already exists."
        )
    new_device.pop("_id")
    return new_device

@app.put("/devices/{name}")
def put_device(name: str, updated_device: Device):
    device_data = updated_device.model_dump()

    #Update the document in MongoDB
    result = devices.find_one_and_update(
        {"name": name},
        {"$set": device_data},
        return_document=True  # Returns the updated document
    )

    if not result:
        raise HTTPException(status_code=404, detail=f"No device called {name}")

    #Remove ObjectId so FastAPI can serialize the response cleanly
    result.pop("_id", None)
    return result