from abc import ABC, abstractmethod


class Field(ABC):
    """Interface abstrata para um corpo algébrico."""

    @abstractmethod
    def normalize(self, value):
        pass

    @abstractmethod
    def add(self, a, b):
        pass

    @abstractmethod
    def multiply(self, a, b):
        pass

    @abstractmethod
    def zero(self):
        pass

    @abstractmethod
    def one(self):
        pass
