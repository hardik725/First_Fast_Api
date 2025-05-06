from fastapi import FastAPI
# this is the core framework on which whole api is built
from pydantic import BaseModel
# this is the used for validation the req and res that we send and recieve the structure of it can be 
# modified using pydantic
from typing import List

from pymongo.mongo_client import MongoClient
#this is a client which helps us to interact with mongodb
from pymongo.server_api import ServerApi
# this helps us to decide the type of server to use to connect to mongo db
#without this it will take a default latest server

app = FastAPI()

uri = "mongodb+srv://purplescissorsorg:7B6IgeNZKd3hrewl@cluster0.uvaagdj.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(uri, server_api=ServerApi('1'))


# here client is instance object made to interact with mongo db and admin is main database which handle commands and command is 
# req send to db and ping checks for connection has been done or not
try: 
    client.admin.command('ping')
    print("✅ Successfully connected to MongoDB")
except Exception as e:
    print("❌ Failed to connect to MongoDB:", e)

class Tea(BaseModel):
    id: int
    name: str
    origin: str

teas: List[Tea] = []
# this is a list that contain the data structure Tea in it

#Decorators: They give super power to the functions
# In FastAPI, decorators are used to define API routes 
# (endpoints) and associate them with specific HTTP methods like GET, POST, etc.

@app.get("/")
def root():
    return {"message": "MongoDB connection established!"}

@app.get("/teas")
def get_teas():
    return teas

@app.post("/teas")
def add_tea(tea: Tea): # we have pass the tea which we have to add through the function here
    teas.append(tea)
    return tea

@app.put("/teas/{tea_id}")
def update_tea(tea_id: int, updated_tea: Tea):
    for index,tea in enumerate(teas):
        if tea.id == tea_id:
            teas[index] = update_tea
            return update_tea
        else:
            return {"error": "Tea not found"}

@app.delete("/teas/{tea_id}")
def delete_tea(tea_id: int):
    for index,tea in enumerate(teas):
        if tea.id == tea_id:
            deleted = teas.pop(index) # here pop returns the value deleted which can be stored in a variable
            return deleted




