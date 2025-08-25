from abc import ABC, abstractmethod


class BaseParser(ABC):
    @abstractmethod
    def parse(self, full_filepath: str):
        pass
