from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass
class PathElement:
    # name is the name of the path element.
    name: str

    # isDirectory tells if the path element is a directory.
    isDirectory: bool


@dataclass
class Reader(ABC):
    # The URI scheme this reader is responsible for reading.
    scheme: str

    # Tells whether the path part of ths URI has a
    # [hier-part](https://datatracker.ietf.org/doc/html/rfc3986#section-3).
    #
    # An example of a hierarchical URI is `file:///path/to/my/file`, where
    # `/path/to/my/file` designates a nested path through the `/` character.
    #
    # An example of a non-hierarchical URI is `pkl.base`, where the `base` does not denote
    # any form of hierarchy.
    hasHierarchicalUris: bool

    # Tells whether this reader supports globbing.
    isGlobbable: bool

    # listElements returns the list of elements at a specified path.
    # If HasHierarchicalUris is false, path will be empty and ListElements should return all
    # available values.
    #
    # This method is only called if it is hierarchical and local, or if it is globbable.
    def list_elements(self, url: str) -> List[PathElement]:
        raise NotImplementedError(
            f"Must implement 'list_elements' for {self.__class__}"
        )

    @abstractmethod
    def read(self, url):
        pass


@dataclass
class ModuleReader(Reader):
    # Tells whether the module is local to the system.
    #
    # A local resource that [hasHierarchicalUris] supports triple-dot imports.
    isLocal: bool

    @abstractmethod
    def read(self, url) -> str:
        pass


@dataclass
class ResourceReader(Reader):
    @abstractmethod
    def read(self, url) -> bytes:
        pass
