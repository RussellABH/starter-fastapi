from pydantic import BaseModel

class Batch(BaseModel):
    modelUrl: str
    datasetUrl: str
    indexTuple: tuple[int, int]
    requestID: int

    def __init__(self, modelUrl, datasetUrl, indexTuple, requestID):
        self.modelUrl = modelUrl
        self.datasetUrl = datasetUrl
        self.indexTuple = indexTuple
        self.requestID = requestID

    
class Pipeline():
    #TODO: Actaully implement this
    def __init__(self):
        self.test = 'foo'
    
    def run(self):
        print(self.test)