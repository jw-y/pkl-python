# PKLL - PKL Language Python Binding
Python binding for [Apple's Pkl language](https://pkl-lang.org/index.html).

### Status
* Evaluator API: fully functional
* Code Generation: not implemented, yet

## Installation

``` bash
pip install pkll
```

## Usage
### Basic Usage
Here's how you can start using PKLL to load a PKL module:

```python
import pkll

config = pkll.load("file:///path/to/pkl/example_module.pkl")
print(config)
```

## Advanced Features
For details on the parameters, refer [Message Passing API](https://pkl-lang.org/main/current/bindings-specification/message-passing-api.html).

```python
from pkll import load

# Advanced loading with custom environment and properties
result = load(
    "file:///path/to/pkl/example_module.pkl"
    env={"CUSTOM_ENV": "value"},
    properties={"custom.property": "value"}
)
print(result)
```

### Custom Handler
It is possible to add custom resources or module handler:
```python
import pkll
from pkll.handler import (
    ListResponse,
    ReadModuleResponse,
    ReadResourceResponse,
    ResourcesHandler,
)
from pkll.msgapi.outgoing import ClientResourceReader

class CustomModuleHandler(ResourcesHandler):
    def list_response(self, uri: str) -> ListResponse:
        return ListResponse(
            pathElements=[{"name": "foo.pkl", "isDirectory": False}]
        )

    def read_response(self, uri: str) -> ReadResourceResponse:
        return ReadModuleResponse(
            contents="foo = 1",
        )

config = pkll.load(
    "./tests/myModule.pkl",
    allowedModules=["pkl:", "repl:", "file:", "customfs:"],
    clientModuleReaders=[
        {
            "scheme": "customfs",
            "hasHierarchicalUris": True,
            "isGlobbable": True,
            "isLocal": True,
        }
    ],
    debug=True,
    module_handler=CustomModuleHandler(),
)
```

## Contributing
Contributions are welcome! If you'd like to contribute, please fork the repository and submit a pull request. For major changes, please open an issue first to discuss what you would like to change.

## License
PKLL is released under the MIT License. See the LICENSE file for more details.

## Contact
For support or to contribute, please contact jwyang0213@gmail.com or visit our GitHub repository to report issues or submit pull requests.
