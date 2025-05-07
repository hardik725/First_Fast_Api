from fastapi import FastAPI
# this is the core framework on which whole api is built
from pydantic import BaseModel,Field
# this is the used for validation the req and res that we send and recieve the structure of it can be 
# modified using pydantic
from typing import List

from bson import ObjectId

from pymongo.mongo_client import MongoClient
#this is a client which helps us to interact with mongodb
from pymongo.server_api import ServerApi
# this helps us to decide the type of server to use to connect to mongo db
#without this it will take a default latest server
from fastapi.responses import JSONResponse
from fastapi import HTTPException

app = FastAPI()

uri = "mongodb+srv://purplescissorsorg:7B6IgeNZKd3hrewl@cluster0.uvaagdj.mongodb.net/?retryWrites=true&w=majority"
# here we have to create a database and a collection to store the teas in it 
DATABASE_NAME = "tea_Database"
COLLECTION_NAME = "tea_Collection"

client = MongoClient(uri, server_api=ServerApi('1'))

def serialize_mongo_doc(doc):
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc

# there was problem in adjusting the Object id in the json format so we have to make a custimized function to handle this issue


# here client is instance object made to interact with mongo db and admin is main database which handle commands and command is 
# req send to db and ping checks for connection has been done or not
try: 
    client.admin.command('ping')
    print("✅ Successfully connected to MongoDB")

    db = client[DATABASE_NAME]
    teas = db[COLLECTION_NAME]

    # here class is formed in the form it should store the data

    class Tea(BaseModel):
        id: int = Field(alias="_id")
        name: str
        origin: str
        class Config:
            populate_by_name = True # Allows using either 'id' or '_id' during model initialization
            json_encoders = {ObjectId: str} # If you use ObjectId and want to serialize it to string
            arbitrary_types_allowed = True # If using ObjectId

        # here sample tea data to be stored in mongo db
    teas_data: List[Tea] = []
    # Convert Pydantic models to dictionaries for MongoDB insertion
    # MongoDB stores data as BSON documents, which are dict-like.
    # Pydantic's model_dump() method (or dict() in Pydantic V1) converts the model to a dictionary.
    teas_to_insert = [tea.model_dump() for tea in teas_data]
    #after we have created funtion to add tea we can remove this default setting to add sample value
    if teas_to_insert:
        try:
            result  = teas.insert_many(teas_to_insert)
            print(f"the teas data has been inserted successfully{result}")
        
        except Exception as e:
            print(f"❌ An unexpected error occurred: {e}")
        
        finally:
               if 'client' in locals() and client:
                   client.close()
            # It's good practice to close the connection when done,
            # # though for simple scripts it might not be strictly necessary
            # # as it often closes when the script ends.
            # # For long-running applications, proper connection management is crucial.
            # # print("ℹ️ MongoDB connection closed.")
        
except Exception as e:
    print("❌ Failed to connect to MongoDB:", e)



# teas: List[Tea] = []
# # this is a list that contain the data structure Tea in it

#Decorators: They give super power to the functions
# In FastAPI, decorators are used to define API routes 
# (endpoints) and associate them with specific HTTP methods like GET, POST, etc.

@app.get("/")
def root():
    return {"message": "MongoDB connection established!"}

@app.get("/getTea/{tea_id}")
def get_teas(tea_id: int):
    req_tea = teas.find_one({"id": tea_id})
    if req_tea is None:
        raise HTTPException(status_code=404, detail="Tea was not found.")
    return serialize_mongo_doc(req_tea)


@app.post("/teas")
def add_tea(tea: Tea): # we have pass the tea which we have to add through the function here
    try:
        #here first we will convert the tea data into a dict
        tea_dict = tea.model_dump()
        result = teas.insert_one(tea_dict)
        return JSONResponse(
            status_code=201,
            content={"message": "Tea added successfully"},
        )
    except Exception as e:
        return JSONResponse(
            status_code=401,
            content={"There was an error while adding the tea"}
        )

@app.put("/teas/{tea_id}")
def update_tea(tea_id: int, updated_tea: Tea):
    update_result = teas.update_one(
        {"id": tea_id},
        {"$set": updated_tea.model_dump()}
    )

    if update_result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Tea not found")

    return JSONResponse(
        status_code=200,
        content={"message": "Tea was updated successfully"}
    )
        

@app.delete("/teas/{tea_id}")
def delete_tea(tea_id: int):
    result = teas.delete_one({"id": tea_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="There is no tea with this id")
    req_tea = teas.find_one({"id": tea_id})
    if req_tea:
        raise HTTPException(status_code=404, detail="Tea was not deleted successfully")
    return JSONResponse(
        status_code=201,
        content={"message": "Tea was deleted Successfully"}
    )




