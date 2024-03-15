from collections import namedtuple
from datetime import timedelta
from enum import Enum, auto


class ResultType(Enum):
    INT = auto()
    FLOAT = auto()
    STRING = auto()
    LIST = auto()
    TUPLE = auto()
    CLASS = auto()
    DICTIONARY = auto()
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


class Parser:
    def __init__(
        self,
        force_render=False,
        *,
        typed_dynamic_result_type=ResultType.NAMEDTUPLE,
        pair_result_type=ResultType.NAMEDTUPLE,
        duration_result_type=ResultType.TIMEDELTA,
        datasize_result_type=ResultType.NAMEDTUPLE,
        regex_result_type=ResultType.NAMEDTUPLE,
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
        self._namedtuple_cache = {
            "__Pair__": namedtuple("Pair", ["first", "second"]),
            "__DataSize__": namedtuple("DataSize", ["value", "unit"]),
            "__Regex__": namedtuple("Regex", ["pattern"]),
        }
        self._force_render = force_render
        self._typed_dynamic_result_type = typed_dynamic_result_type
        self._pair_result_type = pair_result_type
        self._duration_result_type = duration_result_type
        self._datasize_result_type = datasize_result_type
        self._regex_result_type = regex_result_type

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

    def parse_typed_dynamic(self, obj):
        _, full_class_name, module_uri, members = obj

        member_types = set(m[0] for m in members)
        property_list = list(map(self.handle_type, members))

        if CODE_ELEMENT in member_types:  # has element
            if len(member_types) > 1 and not self._force_render:
                raise ValueError(
                    "Cannot render object with both elements and properties/entries.\n"
                    "\tUse 'force_render=True'"
                )
            # element types
            members = property_list
            return members

        # only properties and entries
        members = {k: v for m in property_list for k, v in m.items()}
        result_type = self._typed_dynamic_result_type
        if result_type == ResultType.NAMEDTUPLE:
            class_name = full_class_name.split("#")[-1].split(".")[-1]

            res = namedtuple(class_name, members.keys())(*members.values())
            return res
        elif result_type == ResultType.DICTIONARY:
            return {full_class_name: members}
        else:
            raise ValueError(f"invalid result_type: '{result_type}'")

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
        unit_map = {
            "ns": "nanoseconds",
            "us": "microseconds",
            "ms": "milliseconds",
            "s": "seconds",
            "min": "minutes",
            "h": "hours",
            "d": "days",
        }
        result_type = self._duration_result_type
        if result_type == ResultType.TIMEDELTA and unit == "ns":
            if not self._force_render:
                raise ValueError(
                    "Unit 'ns' not supported for 'datetime.timedelta'\n"
                    "\tTry using 'PANDAS_TIMEDELTA' or 'force_render'"
                )
            result_type = ResultType.PANDAS_TIMEDELTA

        if result_type == ResultType.TIMEDELTA:
            return timedelta(**{unit_map[unit]: value})
        elif result_type == ResultType.PANDAS_TIMEDELTA:
            from pandas import Timedelta

            return Timedelta(**{unit_map[unit]: value})
        else:
            raise ValueError(f"ResultType '{self._pair_result_type}' not supported")

    def parse_pair(self, obj):
        if self._pair_result_type == ResultType.NAMEDTUPLE:
            return self._namedtuple_cache["__Pair__"](obj[1], obj[2])
        elif self._pair_result_type == ResultType.LIST:
            return [obj[1], obj[2]]
        elif self._pair_result_type == ResultType.TUPLE:
            return (obj[1], obj[2])
        else:
            raise ValueError(f"ResultType '{self._pair_result_type}' not supported")

    def parse_datasize(self, obj):
        if self._datasize_result_type == ResultType.NAMEDTUPLE:
            return self._namedtuple_cache["__DataSize__"](obj[1], obj[2])
        elif self._datasize_result_type == ResultType.TUPLE:
            return (obj[1], obj[2])
        else:
            raise ValueError(f"ResultType '{self._datasize_result_type}' not supported")

    def parse_intseq(self, obj):
        return range(obj[1], obj[2], obj[2])

    def parse_regex(self, obj):
        if self._datasize_result_type == ResultType.NAMEDTUPLE:
            return self._namedtuple_cache["__Regex__"](obj[1])
        else:
            raise ValueError(f"ResultType '{self._datasize_result_type}' not supported")

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
