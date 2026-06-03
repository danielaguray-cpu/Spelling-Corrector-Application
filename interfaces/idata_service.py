from abc import ABC, abstractmethod

class IDataService(ABC):
    @abstractmethod
    def add(self, item):
        pass

    @abstractmethod
    def update(self, item):
        pass

    @abstractmethod
    def delete(self, item_id):
        pass

    @abstractmethod
    def get_all(self):
        pass
