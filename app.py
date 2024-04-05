from fastapi import FastAPI, status
from fastapi.responses import FileResponse
from pydantic import BaseModel

from classes import *

app = FastAPI()
pipeline = Pipeline()  # initialize pipeline

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse('favicon.ico')

# Inherit from BaseModel because this will be sent as a body from fastapi (probably)
class Request(BaseModel):
    requestID: int
    datasetSource: str
    modelSource: str
    requestOwner: str # address
    bid: int # in wei probably
    consensusType: str # unsure if relevant still
    result: list # the labels
    participation: dict[str, float]

# a data structure for labels
class Labels(BaseModel):
    requestID: int
    userAddress: str
    labels: list # same as result in Request

@app.get("/")  # default root
async def root():
    return {"message": "API is working"}

# Receive a new Request
# TODO: Some kind of callback back to chainlink and then smart contract
#  honestly probably not a callback and instead just some transaction since we have a request id
@app.post("/newRequest", status_code=status.HTTP_200_OK)
async def newRequest(req: Request):
    # TODO: turn Request into PipelineRequest and add to pipeline's priority queue
    return {"message": "Request received"} # Probably won't be used, just look at the status code

# Client GET a new Batch
@app.get("/batch", status_code=status.HTTP_200_OK)
async def giveBatch() -> BatchItem:
    # TODO: don't return dummy data
    return BatchItem(modelUrl="https://example.com/model", 
                 datasetUrl="https://example.com/dataset", 
                 indexTuple=(0, 100), requestID=1)

# Client POST labels
@app.put("/labels", status_code=status.HTTP_202_ACCEPTED)
async def postLabels(labels: Labels):
    # TODO: Give the labels to the consensus 
    return {"message": "Labels received"} # again probably won't be used