from abc import ABCMeta, abstractmethod
from typing import Pattern, Match
from ..types import Link


class BaseLinkScanner(metaclass=ABCMeta):
    @abstractmethod
    def pattern(self) -> str:
        pass

    @abstractmethod
    def match(self, match: Match) -> bool:
        pass

    @abstractmethod
    def extract(self, match: Match) -> Link:
        pass
