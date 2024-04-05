from pydantic import BaseModel

class BatchItem(BaseModel):
    modelUrl: str
    datasetUrl: str
    indexTuple: tuple[int, int]
    requestID: int
    
class Pipeline():
    #TODO: Actually implement this
    def __init__(self):
        self.test = 'foo'
    
    def run(self):
        print(self.test)