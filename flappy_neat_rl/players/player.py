from abc import ABC, abstractmethod

class Player(ABC):
    @abstractmethod
    def jump(self, *args, **kwargs):
        pass

    @abstractmethod
    def method(self):
        pass
