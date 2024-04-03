from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Union

from pkl.reader import ModuleReader, ResourceReader


@dataclass
class ClientResourceReader:
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


@dataclass
class ClientModuleReader:
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

    # Tells whether the module is local to the system.
    #
    # A local resource that [hasHierarchicalUris] supports triple-dot imports.
    isLocal: bool


@dataclass
class Checksums:
    # The sha-256 checksum of this dependency's metadata.
    sha256: str


@dataclass
class RemoteDependency:
    type: str = "remote"

    # The canonical URI of this dependency
    packageUri: Optional[str] = None

    # The checksums of this remote dependency
    checksums: Optional[Checksums] = None


@dataclass
class Project:
    # The URI pointing to the location of the project file.
    projectFileUri: str

    type: str = "local"

    # The canonical URI of this project's package
    packageUri: Optional[str] = None

    # The dependencies of this project.
    dependencies: Dict[str, Union[Project, RemoteDependency]] = field(
        default_factory=dict
    )


@dataclass
class EvaluatorOptions:
    # Regex patterns to determine which modules are allowed for import.
    #
    # API version of the CLI's `--allowed-modules` flag
    allowedModules: Optional[List[str]] = None

    # Regex patterns to dettermine which resources are allowed to be read.
    #
    # API version of the CLI's `--allowed-resources` flag
    allowedResources: Optional[List[str]] = None

    # Register client-side module readers.
    moduleReaders: Optional[List[ModuleReader]] = None

    # Register client-side resource readers.
    resourceReaders: Optional[List[ResourceReader]] = None

    # Directories, ZIP archives, or JAR archives
    # to search when resolving `modulepath:` URIs.
    #
    # API version of the CLI's `--module-path` flag.
    modulePaths: Optional[List[str]] = None

    # Environment variable to set.
    #
    # API version of the CLI's `--env-var` flag.
    env: Optional[Dict[str, str]] = None

    # External properties to set.
    #
    # API version of the CLI's `--properties` flag.
    properties: Optional[Dict[str, str]] = None

    # Duration, in seconds, after which evaluation of a source module will be timed out.
    #
    # API version of the CLI's `--timeout` flag.
    timeoutSeconds: Optional[int] = None

    # Restricts access to file-based modules and resources to those located under the root directory.
    rootDir: Optional[str] = None

    # The cache directory for storing packages.
    cacheDir: Optional[str] = None

    # The format to generate.
    #
    # This sets the `pkl.outputFormat` external property.
    outputFormat: Optional[str] = None

    # The project dependency settings.
    # project: Optional[Project] = None


@dataclass
class PreconfiguredOptions(EvaluatorOptions):
    allowedModules: Optional[List[str]] = field(
        default_factory=lambda: [
            "pkl:",
            "repl:",
            "file:",
            "http:",
            "https:",
            "modulepath:",
            "package:",
            "projectpackage:",
        ]
    )
    allowedResources: Optional[List[str]] = field(
        default_factory=lambda: [
            "http:",
            "https:",
            "file:",
            "env:",
            "prop:",
            "modulepath:",
            "package:",
            "projectpackage:",
        ]
    )
    env: Optional[Dict[str, str]] = field(default_factory=lambda: dict(os.environ))

    cacheDir: Optional[str] = str(Path("~/.pkl/cache").expanduser())
