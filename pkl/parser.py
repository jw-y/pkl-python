import sys
import types
from dataclasses import dataclass, make_dataclass
from datetime import timedelta
from enum import Enum, auto
from typing import Generic, List, Literal, TypeVar

# create module for lookup
_lookup_module = types.ModuleType(__name__ + "._lookup")
sys.modules[_lookup_module.__name__] = _lookup_module


class ResultType(Enum):
    INT = auto()
    FLOAT = auto()
    STRING = auto()
    LIST = auto()
    TUPLE = auto()
    CLASS = auto()
    DICTIONARY = auto()
    RANGE = auto()
    DATACLASS = auto()
    NAMEDTUPLE = auto()
    TIMEDELTA = auto()
    PANDAS_TIMEDELTA = auto()


CODE_TYPED_DYNAMIC = 0x1
CODE_MAP = 0x2
CODE_MAPPING = 0x3
CODE_LIST = 0x4
CODE_LISTING = 0x5
CODE_SET = 0x6
CODE_DURATION = 0x7
CODE_DATASIZE = 0x8
CODE_PAIR = 0x9
CODE_INTSEQ = 0xA
CODE_REGEX = 0xB
CODE_CLASS = 0xC
CODE_TYPEALIAS = 0xD
CODE_PROPERTY = 0x10
CODE_ENTRY = 0x11
CODE_ELEMENT = 0x12


T1 = TypeVar("T1")
T2 = TypeVar("T2")


@dataclass
class Pair(Generic[T1, T2]):
    first: T1
    second: T2


@dataclass
class Duration:
    value: float
    unit: Literal["ns", "us", "ms", "s", "min", "h", "d"]
    _UNIT_MAP = {
        "ns": "nanoseconds",
        "us": "microseconds",
        "ms": "milliseconds",
        "s": "seconds",
        "min": "minutes",
        "h": "hours",
        "d": "days",
    }

    def to_timedelta(self):
        return timedelta(**{self._UNIT_MAP[self.unit]: self.value})

    def to_pandas_timedelta(self):
        import pandas as pd

        return pd.Timedelta(self.value, self._UNIT_MAP[self.unit])


@dataclass
class DataSize:
    value: float
    unit: Literal["b", "kb", "kib", "mb", "mib", "gb", "gib", "tb", "tib", "pb", "pib"]


@dataclass
class IntSeq:
    start: int
    end: int
    step: int


@dataclass
class Regex:
    pattern: str


class Parser:
    def __init__(
        self,
        namespace=None,
        force_render=False,
    ):
        self.type_handlers = {
            CODE_TYPED_DYNAMIC: self.parse_typed_dynamic,
            CODE_MAP: self.parse_map,
            CODE_MAPPING: self.parse_mapping,
            CODE_LIST: self.parse_list,
            CODE_LISTING: self.parse_listing,
            CODE_SET: self.parse_set,
            CODE_DURATION: self.parse_duration,
            CODE_DATASIZE: self.parse_datasize,
            CODE_PAIR: self.parse_pair,
            CODE_INTSEQ: self.parse_intseq,
            CODE_REGEX: self.parse_regex,
            CODE_CLASS: self.parse_class,
            CODE_TYPEALIAS: self.parse_typealias,
            CODE_PROPERTY: self.parse_property,
            CODE_ENTRY: self.parse_entry,
            CODE_ELEMENT: self.parse_element,
        }
        self.namespace = namespace
        self.dataclass_cache = {}
        self.force_render = force_render

    def parse(self, obj):
        return self.handle_type(obj)

    def handle_type(self, obj):
        if isinstance(obj, list):
            type_code = obj[0]
            if type_code in self.type_handlers:
                return self.type_handlers[type_code](obj)
            else:
                # Handle unknown type or implement a default handler
                return {"type": "Unknown", "value": obj}
        elif isinstance(obj, dict):
            return {k: self.handle_type(v) for k, v in obj.items()}
        elif isinstance(obj, (set, tuple)):
            return type(obj)(self.handle_type(v) for v in obj)
        return obj

    def get_dataclass_class(self, class_name: str, keys: List[str]):
        if class_name not in self.dataclass_cache:
            dynamic_class = make_dataclass(class_name, keys)
            dynamic_class.__module__ = _lookup_module.__name__
            setattr(_lookup_module, class_name, dynamic_class)
            self.dataclass_cache[class_name] = dynamic_class
        dynamic_class = self.dataclass_cache[class_name]
        return dynamic_class

    def parse_typed_dynamic(self, obj):
        _, full_class_name, module_uri, members = obj

        member_types = set(m[0] for m in members)
        property_list = list(map(self.handle_type, members))

        if CODE_ELEMENT in member_types:  # has element
            if len(member_types) > 1 and not self.force_render:
                raise ValueError(
                    "Cannot render object with both elements and properties/entries.\n"
                    "\tUse 'force_render=True'"
                )
            # element types
            members = property_list
            return members

        # only properties and entries
        members = {k: v for m in property_list for k, v in m.items()}
        class_name = full_class_name.split("#")[-1].split(".")[-1]

        if self.namespace is not None:
            if class_name not in self.namespace:
                raise ValueError(f"'namespace' provided but '{class_name}' not found")
            clazz = self.namespace[class_name]
        else:
            clazz = self.get_dataclass_class(class_name, members.keys())
        res = clazz(*members.values())
        return res

    def parse_map(self, obj):
        members = obj[1]
        return dict(zip(members.keys(), map(self.handle_type, members.values())))

    def parse_mapping(self, obj):
        return self.parse_map(obj)

    def parse_list(self, obj):
        return list(map(self.handle_type, obj[1]))

    def parse_listing(self, obj):
        return self.parse_list(obj)

    def parse_set(self, obj):
        return set(obj[1])

    def parse_duration(self, obj):
        _, value, unit = obj

        return Duration(value, unit)

    def parse_pair(self, obj):
        return Pair(obj[1], obj[2])

    def parse_datasize(self, obj):
        return DataSize(obj[1], obj[2])

    def parse_intseq(self, obj):
        return IntSeq(obj[1], obj[2], obj[3])

    def parse_regex(self, obj):
        return Regex(obj[1])

    def parse_class(self, obj):
        return

    def parse_typealias(self, obj):
        return

    def parse_property(self, obj):
        _, key, value = obj
        return {key: self.handle_type(value)}

    def parse_entry(self, obj):
        _, key, value = obj
        return {key: self.handle_type(value)}

    def parse_element(self, obj):
        _, index, value = obj
        return {index: self.handle_type(value)}
