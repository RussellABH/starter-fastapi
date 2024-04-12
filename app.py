from fastapi import FastAPI, status, HTTPException
from fastapi.responses import FileResponse

from classes import *
import re

app = FastAPI()
pipeline = Pipeline()  # initialize pipeline

# TODO: Figure out a testing suite for each endpoint

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse('favicon.ico')



@app.get("/")  # default root
async def root():
    return {"message": "API is working"}


'''
Example request:
{
  "requestID": 1,
  "datasetSource": "https://drive.google.com/file/d/1P6kHVYGYd7xUTa6bW_37rdY4QHb9NDYa/view?usp=sharing",
  "numImages": 1084,
  "modelSource": "https://huggingface.co/spaces/ayaanzaveri/mnist/resolve/c959fe1db8b15ed643b91856cb2db4e2a3125938/mnist-model.h5",
  "requestOwner": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
  "bid": 10
}
'''
@app.post("/newRequest", status_code=status.HTTP_200_OK)
def NewRequest(req: Request):
    '''
    Receive a new Request
    TODO: Some kind of callback back to chainlink and then smart contract
     honestly probably not a callback and instead just some transaction since we have a request id  
    TODO: Test if req has input validation
    '''
    try: # Function can raise ValueError due to bad request id
        pipeline.add_request(PipelineRequest(req))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "Request received"} # Probably won't be used, just look at the status code

'''
Example address:
0xD693853b55b0DACe3eD82B26B36A2F12AE914F8a
'''
@app.get("/batch", status_code=status.HTTP_200_OK)
def GiveBatch(address: str) -> BatchItem:
    '''
    Client GET a new Batch
    Query parameter is the worker's address.

    Adds the worker to the PipelineRequest and gives the information for the "batch"
    '''
    if not re.match(r'^(0x)?[0-9a-fA-F]{40}$', address): # Regex stolen from https://www.geeksforgeeks.org/ethereum-address-validation-using-regular-expressions/
        raise HTTPException(status_code=400, detail="Invalid Ethereum address")
    
    if not (curr_req := pipeline.get_curr_req()):
        raise HTTPException(status_code=404, detail="No requests available")
    
    curr_req.add_worker(Worker(address))
    return curr_req.get_batch()


@app.put("/labels", status_code=status.HTTP_202_ACCEPTED)
def PostLabels(data: LabelReturnItem):
    '''
    Client POST labels
    
    Add labels to the relevant worker in the PipelineRequest object.
    Then, checks if the current request is done. If so:
    1. Send the resulting labels and participation to the smart contract
        Don't know how to do this yet, waiting on Caleb
    2. Set the currentRequest to the next request in the priority queue
    '''
    if not (curr_req := pipeline.get_curr_req()):
        raise HTTPException(status_code=404, detail="No requests available") 

    # Function can raise ValueError 
    try:
        labels = curr_req.add_labels_check_done(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if labels:
        # TODO: Send the labels to the smart contract
        pipeline.set_next_req()
        return {"message": f"Labels received and consensus reached: {labels}"}
    
    return {"message": "Labels received, waiting on consensus"}
