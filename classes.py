from pydantic import BaseModel
from ImageLabelConsensus import ImageLabelConsensus
import heapq # for priority queue

MIN_WORKERS = 3 # Minimum number of workers needed to start a request

# Inherit from BaseModel because this will be sent as a body from fastapi (probably)
class Request(BaseModel):
    requestID: int
    datasetSource: str
    numImages: int
    modelSource: str
    requestOwner: str # address
    bid: int # in wei probably
    # participation: dict[str, float] Not used, instead we just save the list of workers in the PipelineRequest object

class BatchItem(BaseModel):
    modelUrl: str
    datasetUrl: str
    requestID: int

# a data structure for labels
class LabelReturnItem(BaseModel):
    requestID: int
    userEthAddress: str
    labels: list # same as result in Request

class Worker():
    def __init__(self, address: str):
        self.address = address
        self.participation = 0 # Currently used to determine if a worker has already sent labels
        self.labels = [] # The labels that the worker sends back

    def __eq__(self, other) -> bool:
        '''
        Used for checking if a worker is already in the list of workers in a PipelineRequest object
        '''
        return self.address == other.address
    
    def __lt__(self, other) -> bool:
        '''
        Not sure if we'll use this but it's here if we need it. No type checking because it shouldn't matter
        '''
        return self.participation < other.participation if self.participation < other.participation else self.address < other.address
    
class PipelineRequest():
    def __init__(self, request: Request):
        '''
        Make a pipeline request from a Request object
        '''
        self.requestID = request.requestID
        self.datasetSource = request.datasetSource
        self.numImages = request.numImages
        self.modelSource = request.modelSource
        self.requestOwner = request.requestOwner
        self.bid = request.bid
        # self.participation = request.participation # TODO: How are we calculating this again?
        self.workers = [] # List of Workers
        self.consensus = ImageLabelConsensus()

    def add_worker(self, worker: Worker):
        '''
        Called by Pipeline when GET /batch is called.
        '''
        self.workers.append(worker)

    def get_batch(self):
        '''
        Get the relevant information that the workers need in a BatchItem object
        '''
        return BatchItem(modelUrl=self.modelSource, datasetUrl=self.datasetSource, requestID=self.requestID)
    
    def add_labels_check_done(self, data: LabelReturnItem):
        '''
        Called by Pipeline when POST /labels is called.

        Returns None if the consensus algorithm is not done, otherwise returns the labels.
        Also, performs input validation.
        '''
        if data.requestID != self.requestID:
            raise ValueError("Request IDs do not match")
        elif len(data.labels) != self.numImages:
            raise ValueError("Number of labels does not match the number of images")
        
        worker = self.workers[self.workers.index(Worker(data.userEthAddress))] # Will raise ValueError if the worker is not in the list of workers
        if worker.participation:
            raise ValueError("Worker has already sent labels")
        
        worker.labels = data.labels
        worker.participation = 1

        # Check if we have enough labels to run the consensus algorithm
        if len([w for w in self.workers if w.participation]) >= MIN_WORKERS:
            self.consensus.receiveData({worker.address: worker.labels for worker in self.workers})
            return self.consensus.responseData()
        
        return None
    
    # Return current labels for debugging
    def get_labels(self):
        return {worker.address: worker.labels for worker in self.workers}

    # Overload comparison operators for priority queue
    def __lt__(self, other):
        return (self.bid * -1) < (other.bid * -1) # negate so it's a max heap

class Pipeline():
    def __init__(self):
        self.reqPQ = [] # priority queue for requests
        self.currentRequest = None # the current PipelineRequest being worked on

    def add_request(self, req: PipelineRequest):
        """
        Add a PipelineRequest to the priority queueq
        """
        if req.requestID in {r.requestID for r in self.reqPQ}:
            raise ValueError("Request ID already in the queue")
        heapq.heappush(self.reqPQ, req)

    def get_curr_req(self) -> PipelineRequest | None:
        '''
        Get the current request
        '''
        if not self.currentRequest:
            self.set_next_req()
            
        return self.currentRequest
    
    def set_next_req(self):
        '''
        Set the next request in the priority queue as the current request
        '''
        if len(self.reqPQ) == 0:
            self.currentRequest = None
        else:
            self.currentRequest = heapq.heappop(self.reqPQ)