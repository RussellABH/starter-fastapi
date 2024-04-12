from abc import ABC, abstractmethod
from collections import Counter

class Consensus(ABC):
    @abstractmethod
    def receiveData(self, data):
        """
        Receive data like different clients' label arrays.
        """
        pass

    @abstractmethod
    def responseData(self):
        """
        Return the new array after consolidating labels.
        """
        pass

class ImageLabelConsensus(Consensus):
    def __init__(self):
        self.received_labels = {}

    def receiveData(self, data):
        """
        Stores the received data. Expected format: {client_id: [labels]}
        """
        self.received_labels = data

    def responseData(self):
        """
        Consolidates the received label data and returns a new array with the most common labels.
        """
        if not self.received_labels:
            return []

        label_length = len(next(iter(self.received_labels.values())))
        consolidated_labels = []

        for i in range(label_length):
            ith_labels = [labels[i] for labels in self.received_labels.values()]
            most_common_label = Counter(ith_labels).most_common(1)[0][0]
            consolidated_labels.append(most_common_label)

        return consolidated_labels

# # Example usage:
# image_label_consensus = ImageLabelConsensus()

# # Simulating the receipt of data from different clients
# image_label_consensus.receiveData({
#     'client_1': batchmaker.received_labels['client_1'],
#     'client_2': batchmaker.received_labels['client_2'],
#     'client_3': batchmaker.received_labels['client_3'],
#     'client_4': batchmaker.received_labels['client_4'],
#     'client_5': batchmaker.received_labels['client_5'],
# })

# consolidated_labels = image_label_consensus.responseData()
# print("Consolidated Labels:", consolidated_labels)
