from fastapi import FastAPI, status, HTTPException
from fastapi.responses import FileResponse
from web3 import Web3
import os
from dotenv import load_dotenv, dotenv_values 
from fastapi.middleware.cors import CORSMiddleware
load_dotenv() 
 

from classes import *
import re

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

        # # Initialize endpoint URL and create the node connection
        # node_url = os.getenv("NODE_URL")
        # web3 = Web3(Web3.HTTPProvider(node_url))

        # # Initialize the address calling the functions/signing transactions
        # caller = os.getenv("CALLER")
        # private_key = os.getenv("PRIVATE_KEY")
        # os.getenv("NODE_URL")

        # # Initialize contract ABI and address
        # abi = [{"inputs":[{"internalType":"address","name":"_tokenAddress","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[],"name":"claimDividends","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"string","name":"datasetSource","type":"string"},{"internalType":"string","name":"modelSource","type":"string"},{"internalType":"uint256","name":"numImages","type":"uint256"}],"name":"createRequest","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"debugInfo","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"val","type":"uint256"}],"name":"distributeDividends","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"dividends","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"requestID","type":"uint256"}],"name":"getResults","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"nextRequestID","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"nextTokenID","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"requestID","type":"uint256"},{"internalType":"string","name":"_results","type":"string"},{"internalType":"address[]","name":"_participants","type":"address[]"}],"name":"retrieveData","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"sendAllRequests","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"},{"internalType":"uint256","name":"id","type":"uint256"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"testMint","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"token","outputs":[{"internalType":"contract POVToken","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"workers","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"}]
        # contract_address = "0xD50A06b793ee173365A13e8Dae97c48E47C5F9C5"

        # # Create smart contract instance
        # contract = web3.eth.contract(address=contract_address, abi=abi)

        requestID = curr_req.requestID
        results = " ".join([str(n) for n in labels])
        participants = [worker.address for worker in curr_req.workers if worker.participation]
        
        # # Initialize address nonce
        # nonce = web3.eth.get_transaction_count(caller)

        # # initialize the chain id, we need it to build the transaction for replay protection
        # Chain_id = web3.eth.chain_id

        # # Call your function
        # call_function = contract.functions.retrieveData(requestID, results, participants).build_transaction({"chainId": Chain_id, "from": caller, "nonce": nonce})

        # # Sign transaction
        # signed_tx = web3.eth.account.sign_transaction(call_function, private_key=private_key)

        # # Send transaction
        # send_tx = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

        # # Wait for transaction receipt
        # tx_receipt = web3.eth.wait_for_transaction_receipt(send_tx)
        # print(tx_receipt) 


        pipeline.set_next_req()
        return {"message": f"Labels received and consensus reached", "RequestID": requestID, "Results": results, "Participants": participants}
    
    return {"message": "Labels received, waiting on consensus"}


# DEBUGGING 


@app.get("/showlabels", status_code=status.HTTP_200_OK)
def ShowLabels():
    '''
    Debugging endpoint to show the labels of the current request
    '''
    if not (curr_req := pipeline.get_curr_req()):
        raise HTTPException(status_code=404, detail="No requests available") 

    return curr_req.get_labels()

@app.get("/showreq", status_code=status.HTTP_200_OK)
def ShowReq():
    '''
    Debugging endpoint to show the current request
    '''
    if not (curr_req := pipeline.get_curr_req()):
        raise HTTPException(status_code=404, detail="No requests available") 

    return curr_req