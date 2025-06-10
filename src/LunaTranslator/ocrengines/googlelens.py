import dataclasses
import enum
import inspect
import struct
from abc import ABC
from base64 import b64encode
from datetime import datetime, timedelta, timezone
from typing import (
    Any,
    Collection,
    Dict,
    Generator,
    List,
    Mapping,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    get_type_hints,
)

import enum
import collections


@enum.unique
class Status(enum.Enum):
    """Predefined gRPC status codes represented as enum

    See also: https://github.com/grpc/grpc/blob/master/doc/statuscodes.md
    """

    #: The operation completed successfully
    OK = 0
    #: The operation was cancelled (typically by the caller)
    CANCELLED = 1
    #: Generic status to describe error when it can't be described using
    #: other statuses
    UNKNOWN = 2
    #: Client specified an invalid argument
    INVALID_ARGUMENT = 3
    #: Deadline expired before operation could complete
    DEADLINE_EXCEEDED = 4
    #: Some requested entity was not found
    NOT_FOUND = 5
    #: Some entity that we attempted to create already exists
    ALREADY_EXISTS = 6
    #: The caller does not have permission to execute the specified operation
    PERMISSION_DENIED = 7
    #: Some resource has been exhausted, perhaps a per-user quota, or perhaps
    #: the entire file system is out of space
    RESOURCE_EXHAUSTED = 8
    #: Operation was rejected because the system is not in a state required
    #: for the operation's execution
    FAILED_PRECONDITION = 9
    #: The operation was aborted
    ABORTED = 10
    #: Operation was attempted past the valid range
    OUT_OF_RANGE = 11
    #: Operation is not implemented or not supported/enabled in this service
    UNIMPLEMENTED = 12
    #: Internal errors
    INTERNAL = 13
    #: The service is currently unavailable
    UNAVAILABLE = 14
    #: Unrecoverable data loss or corruption
    DATA_LOSS = 15
    #: The request does not have valid authentication credentials for the
    #: operation
    UNAUTHENTICATED = 16


_Cardinality = collections.namedtuple(
    "_Cardinality",
    "client_streaming, server_streaming",
)


@enum.unique
class Cardinality(_Cardinality, enum.Enum):
    UNARY_UNARY = _Cardinality(False, False)
    UNARY_STREAM = _Cardinality(False, True)
    STREAM_UNARY = _Cardinality(True, False)
    STREAM_STREAM = _Cardinality(True, True)


Handler = collections.namedtuple(
    "Handler",
    "func, cardinality, request_type, reply_type",
)
import re


def lowercase(string):
    """Convert string into lower case.

    Args:
        string: String to convert.

    Returns:
        string: Lowercase case string.

    """

    return str(string).lower()


def snakecase(string):
    """Convert string into snake case.
    Join punctuation with underscore

    Args:
        string: String to convert.

    Returns:
        string: Snake cased string.

    """

    string = re.sub(r"[\-\.\s]", "_", str(string))
    if not string:
        return string
    return lowercase(string[0]) + re.sub(
        r"[A-Z]", lambda matched: "_" + lowercase(matched.group(0)), string[1:]
    )


def uppercase(string):
    """Convert string into upper case.

    Args:
        string: String to convert.

    Returns:
        string: Uppercase case string.

    """

    return str(string).upper()


def camelcase(string):
    """Convert string into camel case.

    Args:
        string: String to convert.

    Returns:
        string: Camel case string.

    """

    string = re.sub(r"\w[\s\W]+\w", "", str(string))
    if not string:
        return string
    return lowercase(string[0]) + re.sub(
        r"[\-_\.\s]([a-z])", lambda matched: uppercase(matched.group(1)), string[1:]
    )


def safe_snake_case(value: str) -> str:
    """Snake case a value taking into account Python keywords."""
    value = snakecase(value)
    if value in [
        "and",
        "as",
        "assert",
        "break",
        "class",
        "continue",
        "def",
        "del",
        "elif",
        "else",
        "except",
        "finally",
        "for",
        "from",
        "global",
        "if",
        "import",
        "in",
        "is",
        "lambda",
        "nonlocal",
        "not",
        "or",
        "pass",
        "raise",
        "return",
        "try",
        "while",
        "with",
        "yield",
    ]:
        # https://www.python.org/dev/peps/pep-0008/#descriptive-naming-styles
        value += "_"
    return value


# Proto 3 data types
TYPE_ENUM = "enum"
TYPE_BOOL = "bool"
TYPE_INT32 = "int32"
TYPE_INT64 = "int64"
TYPE_UINT32 = "uint32"
TYPE_UINT64 = "uint64"
TYPE_SINT32 = "sint32"
TYPE_SINT64 = "sint64"
TYPE_FLOAT = "float"
TYPE_DOUBLE = "double"
TYPE_FIXED32 = "fixed32"
TYPE_SFIXED32 = "sfixed32"
TYPE_FIXED64 = "fixed64"
TYPE_SFIXED64 = "sfixed64"
TYPE_STRING = "string"
TYPE_BYTES = "bytes"
TYPE_MESSAGE = "message"
TYPE_MAP = "map"


# Fields that use a fixed amount of space (4 or 8 bytes)
FIXED_TYPES = [
    TYPE_FLOAT,
    TYPE_DOUBLE,
    TYPE_FIXED32,
    TYPE_SFIXED32,
    TYPE_FIXED64,
    TYPE_SFIXED64,
]

# Fields that are numerical 64-bit types
INT_64_TYPES = [TYPE_INT64, TYPE_UINT64, TYPE_SINT64, TYPE_FIXED64, TYPE_SFIXED64]

# Fields that are efficiently packed when
PACKED_TYPES = [
    TYPE_ENUM,
    TYPE_BOOL,
    TYPE_INT32,
    TYPE_INT64,
    TYPE_UINT32,
    TYPE_UINT64,
    TYPE_SINT32,
    TYPE_SINT64,
    TYPE_FLOAT,
    TYPE_DOUBLE,
    TYPE_FIXED32,
    TYPE_SFIXED32,
    TYPE_FIXED64,
    TYPE_SFIXED64,
]

# Wire types
# https://developers.google.com/protocol-buffers/docs/encoding#structure
WIRE_VARINT = 0
WIRE_FIXED_64 = 1
WIRE_LEN_DELIM = 2
WIRE_FIXED_32 = 5

# Mappings of which Proto 3 types correspond to which wire types.
WIRE_VARINT_TYPES = [
    TYPE_ENUM,
    TYPE_BOOL,
    TYPE_INT32,
    TYPE_INT64,
    TYPE_UINT32,
    TYPE_UINT64,
    TYPE_SINT32,
    TYPE_SINT64,
]

WIRE_FIXED_32_TYPES = [TYPE_FLOAT, TYPE_FIXED32, TYPE_SFIXED32]
WIRE_FIXED_64_TYPES = [TYPE_DOUBLE, TYPE_FIXED64, TYPE_SFIXED64]
WIRE_LEN_DELIM_TYPES = [TYPE_STRING, TYPE_BYTES, TYPE_MESSAGE, TYPE_MAP]


# Protobuf datetimes start at the Unix Epoch in 1970 in UTC.
def datetime_default_gen():
    return datetime(1970, 1, 1, tzinfo=timezone.utc)


DATETIME_ZERO = datetime_default_gen()


class Casing(enum.Enum):
    """Casing constants for serialization."""

    CAMEL = camelcase
    SNAKE = snakecase


class _PLACEHOLDER:
    pass


PLACEHOLDER: Any = _PLACEHOLDER()


@dataclasses.dataclass(frozen=True)
class FieldMetadata:
    """Stores internal metadata used for parsing & serialization."""

    # Protobuf field number
    number: int
    # Protobuf type name
    proto_type: str
    # Map information if the proto_type is a map
    map_types: Optional[Tuple[str, str]] = None
    # Groups several "one-of" fields together
    group: Optional[str] = None
    # Describes the wrapped type (e.g. when using google.protobuf.BoolValue)
    wraps: Optional[str] = None

    @staticmethod
    def get(field: dataclasses.Field) -> "FieldMetadata":
        """Returns the field metadata for a dataclass field."""
        return field.metadata["betterproto"]


def dataclass_field(
    number: int,
    proto_type: str,
    *,
    map_types: Optional[Tuple[str, str]] = None,
    group: Optional[str] = None,
    wraps: Optional[str] = None,
) -> dataclasses.Field:
    """Creates a dataclass field with attached protobuf metadata."""
    return dataclasses.field(
        default=PLACEHOLDER,
        metadata={
            "betterproto": FieldMetadata(number, proto_type, map_types, group, wraps)
        },
    )


# Note: the fields below return `Any` to prevent type errors in the generated
# data classes since the types won't match with `Field` and they get swapped
# out at runtime. The generated dataclass variables are still typed correctly.


def enum_field(number: int, group: Optional[str] = None) -> Any:
    return dataclass_field(number, TYPE_ENUM, group=group)


def bool_field(number: int, group: Optional[str] = None) -> Any:
    return dataclass_field(number, TYPE_BOOL, group=group)


def int32_field(number: int, group: Optional[str] = None) -> Any:
    return dataclass_field(number, TYPE_INT32, group=group)


def int64_field(number: int, group: Optional[str] = None) -> Any:
    return dataclass_field(number, TYPE_INT64, group=group)


def uint32_field(number: int, group: Optional[str] = None) -> Any:
    return dataclass_field(number, TYPE_UINT32, group=group)


def uint64_field(number: int, group: Optional[str] = None) -> Any:
    return dataclass_field(number, TYPE_UINT64, group=group)


def float_field(number: int, group: Optional[str] = None) -> Any:
    return dataclass_field(number, TYPE_FLOAT, group=group)


def double_field(number: int, group: Optional[str] = None) -> Any:
    return dataclass_field(number, TYPE_DOUBLE, group=group)


def string_field(number: int, group: Optional[str] = None) -> Any:
    return dataclass_field(number, TYPE_STRING, group=group)


def bytes_field(number: int, group: Optional[str] = None) -> Any:
    return dataclass_field(number, TYPE_BYTES, group=group)


def message_field(
    number: int, group: Optional[str] = None, wraps: Optional[str] = None
) -> Any:
    return dataclass_field(number, TYPE_MESSAGE, group=group, wraps=wraps)


class Enum(int, enum.Enum):
    """Protocol buffers enumeration base class. Acts like `enum.IntEnum`."""

    @classmethod
    def from_string(cls, name: str) -> int:
        """Return the value which corresponds to the string name."""
        try:
            return cls.__members__[name]
        except KeyError as e:
            raise ValueError(
                "Unknown value {} for enum {}".format(name, cls.__name__)
            ) from e


def _pack_fmt(proto_type: str) -> str:
    """Returns a little-endian format string for reading/writing binary."""
    return {
        TYPE_DOUBLE: "<d",
        TYPE_FLOAT: "<f",
        TYPE_FIXED32: "<I",
        TYPE_FIXED64: "<Q",
        TYPE_SFIXED32: "<i",
        TYPE_SFIXED64: "<q",
    }[proto_type]


def encode_varint(value: int) -> bytes:
    """Encodes a single varint value for serialization."""
    b: List[int] = []

    if value < 0:
        value += 1 << 64

    bits = value & 0x7F
    value >>= 7
    while value:
        b.append(0x80 | bits)
        bits = value & 0x7F
        value >>= 7
    return bytes(b + [bits])


def _preprocess_single(proto_type: str, wraps: str, value: Any) -> bytes:
    """Adjusts values before serialization."""
    if proto_type in [
        TYPE_ENUM,
        TYPE_BOOL,
        TYPE_INT32,
        TYPE_INT64,
        TYPE_UINT32,
        TYPE_UINT64,
    ]:
        return encode_varint(value)
    elif proto_type in [TYPE_SINT32, TYPE_SINT64]:
        # Handle zig-zag encoding.
        if value >= 0:
            value = value << 1
        else:
            value = (value << 1) ^ (~0)
        return encode_varint(value)
    elif proto_type in FIXED_TYPES:
        return struct.pack(_pack_fmt(proto_type), value)
    elif proto_type == TYPE_STRING:
        return value.encode("utf-8")
    elif proto_type == TYPE_MESSAGE:
        if isinstance(value, datetime):
            # Convert the `datetime` to a timestamp message.
            seconds = int(value.timestamp())
            nanos = int(value.microsecond * 1e3)
            value = _Timestamp(seconds=seconds, nanos=nanos)
        elif isinstance(value, timedelta):
            # Convert the `timedelta` to a duration message.
            total_ms = value // timedelta(microseconds=1)
            seconds = int(total_ms / 1e6)
            nanos = int((total_ms % 1e6) * 1e3)
            value = _Duration(seconds=seconds, nanos=nanos)
        elif wraps:
            if value is None:
                return b""
            value = _get_wrapper(wraps)(value=value)

        return bytes(value)

    return value


def _serialize_single(
    field_number: int,
    proto_type: str,
    value: Any,
    *,
    serialize_empty: bool = False,
    wraps: str = "",
) -> bytes:
    """Serializes a single field and value."""
    value = _preprocess_single(proto_type, wraps, value)

    output = b""
    if proto_type in WIRE_VARINT_TYPES:
        key = encode_varint(field_number << 3)
        output += key + value
    elif proto_type in WIRE_FIXED_32_TYPES:
        key = encode_varint((field_number << 3) | 5)
        output += key + value
    elif proto_type in WIRE_FIXED_64_TYPES:
        key = encode_varint((field_number << 3) | 1)
        output += key + value
    elif proto_type in WIRE_LEN_DELIM_TYPES:
        if len(value) or serialize_empty or wraps:
            key = encode_varint((field_number << 3) | 2)
            output += key + encode_varint(len(value)) + value
    else:
        raise NotImplementedError(proto_type)

    return output


def decode_varint(buffer: bytes, pos: int, signed: bool = False) -> Tuple[int, int]:
    """
    Decode a single varint value from a byte buffer. Returns the value and the
    new position in the buffer.
    """
    result = 0
    shift = 0
    while 1:
        b = buffer[pos]
        result |= (b & 0x7F) << shift
        pos += 1
        if not (b & 0x80):
            return (result, pos)
        shift += 7
        if shift >= 64:
            raise ValueError("Too many bytes when decoding varint.")


@dataclasses.dataclass(frozen=True)
class ParsedField:
    number: int
    wire_type: int
    value: Any
    raw: bytes


def parse_fields(value: bytes) -> Generator[ParsedField, None, None]:
    i = 0
    while i < len(value):
        start = i
        num_wire, i = decode_varint(value, i)
        number = num_wire >> 3
        wire_type = num_wire & 0x7

        decoded: Any = None
        if wire_type == 0:
            decoded, i = decode_varint(value, i)
        elif wire_type == 1:
            decoded, i = value[i : i + 8], i + 8
        elif wire_type == 2:
            length, i = decode_varint(value, i)
            decoded = value[i : i + length]
            i += length
        elif wire_type == 5:
            decoded, i = value[i : i + 4], i + 4

        yield ParsedField(
            number=number, wire_type=wire_type, value=decoded, raw=value[start:i]
        )


# Bound type variable to allow methods to return `self` of subclasses
T = TypeVar("T", bound="Message")


class ProtoClassMetadata:
    cls: Type["Message"]

    def __init__(self, cls: Type["Message"]):
        self.cls = cls
        by_field = {}
        by_group = {}

        for field in dataclasses.fields(cls):
            meta = FieldMetadata.get(field)

            if meta.group:
                # This is part of a one-of group.
                by_field[field.name] = meta.group

                by_group.setdefault(meta.group, set()).add(field)

        self.oneof_group_by_field = by_field
        self.oneof_field_by_group = by_group

        self.init_default_gen()
        self.init_cls_by_field()

    def init_default_gen(self):
        default_gen = {}

        for field in dataclasses.fields(self.cls):
            meta = FieldMetadata.get(field)
            default_gen[field.name] = self.cls._get_field_default_gen(field, meta)

        self.default_gen = default_gen

    def init_cls_by_field(self):
        field_cls = {}

        for field in dataclasses.fields(self.cls):
            meta = FieldMetadata.get(field)
            if meta.proto_type == TYPE_MAP:
                assert meta.map_types
                kt = self.cls._cls_for(field, index=0)
                vt = self.cls._cls_for(field, index=1)
                Entry = dataclasses.make_dataclass(
                    "Entry",
                    [
                        ("key", kt, dataclass_field(1, meta.map_types[0])),
                        ("value", vt, dataclass_field(2, meta.map_types[1])),
                    ],
                    bases=(Message,),
                )
                field_cls[field.name] = Entry
                field_cls[field.name + ".value"] = vt
            else:
                field_cls[field.name] = self.cls._cls_for(field)

        self.cls_by_field = field_cls


class Message(ABC):
    """
    A protobuf message base class. Generated code will inherit from this and
    register the message fields which get used by the serializers and parsers
    to go between Python, binary and JSON protobuf message representations.
    """

    _serialized_on_wire: bool
    _unknown_fields: bytes
    _group_map: Dict[str, dict]

    def __post_init__(self) -> None:
        # Keep track of whether every field was default
        all_sentinel = True

        # Set a default value for each field in the class after `__init__` has
        # already been run.
        group_map: Dict[str, dataclasses.Field] = {}
        for field in dataclasses.fields(self):
            meta = FieldMetadata.get(field)

            if meta.group:
                group_map.setdefault(meta.group)

            if getattr(self, field.name) != PLACEHOLDER:
                # Skip anything not set to the sentinel value
                all_sentinel = False

                if meta.group:
                    # This was set, so make it the selected value of the one-of.
                    group_map[meta.group] = field

                continue

            setattr(self, field.name, self._get_field_default(field, meta))

        # Now that all the defaults are set, reset it!
        self.__dict__["_serialized_on_wire"] = not all_sentinel
        self.__dict__["_unknown_fields"] = b""
        self.__dict__["_group_map"] = group_map

    def __setattr__(self, attr: str, value: Any) -> None:
        if attr != "_serialized_on_wire":
            # Track when a field has been set.
            self.__dict__["_serialized_on_wire"] = True

        if hasattr(self, "_group_map"):  # __post_init__ had already run
            if attr in self._betterproto.oneof_group_by_field:
                group = self._betterproto.oneof_group_by_field[attr]
                for field in self._betterproto.oneof_field_by_group[group]:
                    if field.name == attr:
                        self._group_map[group] = field
                    else:
                        super().__setattr__(
                            field.name,
                            self._get_field_default(field, FieldMetadata.get(field)),
                        )

        super().__setattr__(attr, value)

    @property
    def _betterproto(self):
        """
        Lazy initialize metadata for each protobuf class.
        It may be initialized multiple times in a multi-threaded environment,
        but that won't affect the correctness.
        """
        meta = getattr(self.__class__, "_betterproto_meta", None)
        if not meta:
            meta = ProtoClassMetadata(self.__class__)
            self.__class__._betterproto_meta = meta
        return meta

    def __bytes__(self) -> bytes:
        """
        Get the binary encoded Protobuf representation of this instance.
        """
        output = b""
        for field in dataclasses.fields(self):
            meta = FieldMetadata.get(field)
            value = getattr(self, field.name)

            if value is None:
                # Optional items should be skipped. This is used for the Google
                # wrapper types.
                continue

            # Being selected in a a group means this field is the one that is
            # currently set in a `oneof` group, so it must be serialized even
            # if the value is the default zero value.
            selected_in_group = False
            if meta.group and self._group_map[meta.group] == field:
                selected_in_group = True

            serialize_empty = False
            if isinstance(value, Message) and value._serialized_on_wire:
                # Empty messages can still be sent on the wire if they were
                # set (or received empty).
                serialize_empty = True

            if value == self._get_field_default(field, meta) and not (
                selected_in_group or serialize_empty
            ):
                # Default (zero) values are not serialized. Two exceptions are
                # if this is the selected oneof item or if we know we have to
                # serialize an empty message (i.e. zero value was explicitly
                # set by the user).
                continue

            if isinstance(value, list):
                if meta.proto_type in PACKED_TYPES:
                    # Packed lists look like a length-delimited field. First,
                    # preprocess/encode each value into a buffer and then
                    # treat it like a field of raw bytes.
                    buf = b""
                    for item in value:
                        buf += _preprocess_single(meta.proto_type, "", item)
                    output += _serialize_single(meta.number, TYPE_BYTES, buf)
                else:
                    for item in value:
                        output += _serialize_single(
                            meta.number, meta.proto_type, item, wraps=meta.wraps or ""
                        )
            elif isinstance(value, dict):
                for k, v in value.items():
                    assert meta.map_types
                    sk = _serialize_single(1, meta.map_types[0], k)
                    sv = _serialize_single(2, meta.map_types[1], v)
                    output += _serialize_single(meta.number, meta.proto_type, sk + sv)
            else:
                output += _serialize_single(
                    meta.number,
                    meta.proto_type,
                    value,
                    serialize_empty=serialize_empty,
                    wraps=meta.wraps or "",
                )

        return output + self._unknown_fields

    # For compatibility with other libraries
    SerializeToString = __bytes__

    @classmethod
    def _type_hint(cls, field_name: str) -> Type:
        module = inspect.getmodule(cls)
        type_hints = get_type_hints(cls, vars(module))
        return type_hints[field_name]

    @classmethod
    def _cls_for(cls, field: dataclasses.Field, index: int = 0) -> Type:
        """Get the message class for a field from the type hints."""
        field_cls = cls._type_hint(field.name)
        if hasattr(field_cls, "__args__") and index >= 0:
            field_cls = field_cls.__args__[index]
        return field_cls

    def _get_field_default(self, field: dataclasses.Field, meta: FieldMetadata) -> Any:
        return self._betterproto.default_gen[field.name]()

    @classmethod
    def _get_field_default_gen(
        cls, field: dataclasses.Field, meta: FieldMetadata
    ) -> Any:
        t = cls._type_hint(field.name)

        if hasattr(t, "__origin__"):
            if t.__origin__ in (dict, Dict):
                # This is some kind of map (dict in Python).
                return dict
            elif t.__origin__ in (list, List):
                # This is some kind of list (repeated) field.
                return list
            elif t.__origin__ == Union and t.__args__[1] == type(None):
                # This is an optional (wrapped) field. For setting the default we
                # really don't care what kind of field it is.
                return type(None)
            else:
                return t
        elif issubclass(t, Enum):
            # Enums always default to zero.
            return int
        elif t == datetime:
            # Offsets are relative to 1970-01-01T00:00:00Z
            return datetime_default_gen
        else:
            # This is either a primitive scalar or another message type. Calling
            # it should result in its zero value.
            return t

    def _postprocess_single(
        self, wire_type: int, meta: FieldMetadata, field: dataclasses.Field, value: Any
    ) -> Any:
        """Adjusts values after parsing."""
        if wire_type == WIRE_VARINT:
            if meta.proto_type in [TYPE_INT32, TYPE_INT64]:
                bits = int(meta.proto_type[3:])
                value = value & ((1 << bits) - 1)
                signbit = 1 << (bits - 1)
                value = int((value ^ signbit) - signbit)
            elif meta.proto_type in [TYPE_SINT32, TYPE_SINT64]:
                # Undo zig-zag encoding
                value = (value >> 1) ^ (-(value & 1))
            elif meta.proto_type == TYPE_BOOL:
                # Booleans use a varint encoding, so convert it to true/false.
                value = value > 0
        elif wire_type in [WIRE_FIXED_32, WIRE_FIXED_64]:
            fmt = _pack_fmt(meta.proto_type)
            value = struct.unpack(fmt, value)[0]
        elif wire_type == WIRE_LEN_DELIM:
            if meta.proto_type == TYPE_STRING:
                value = value.decode("utf-8")
            elif meta.proto_type == TYPE_MESSAGE:
                cls = self._betterproto.cls_by_field[field.name]

                if cls == datetime:
                    value = _Timestamp().parse(value).to_datetime()
                elif cls == timedelta:
                    value = _Duration().parse(value).to_timedelta()
                elif meta.wraps:
                    # This is a Google wrapper value message around a single
                    # scalar type.
                    value = _get_wrapper(meta.wraps)().parse(value).value
                else:
                    value = cls().parse(value)
                    value._serialized_on_wire = True
            elif meta.proto_type == TYPE_MAP:
                value = self._betterproto.cls_by_field[field.name]().parse(value)

        return value

    def parse(self: T, data: bytes) -> T:
        """
        Parse the binary encoded Protobuf into this message instance. This
        returns the instance itself and is therefore assignable and chainable.
        """
        fields = {f.metadata["betterproto"].number: f for f in dataclasses.fields(self)}
        for parsed in parse_fields(data):
            if parsed.number in fields:
                field = fields[parsed.number]
                meta = FieldMetadata.get(field)

                value: Any
                if (
                    parsed.wire_type == WIRE_LEN_DELIM
                    and meta.proto_type in PACKED_TYPES
                ):
                    # This is a packed repeated field.
                    pos = 0
                    value = []
                    while pos < len(parsed.value):
                        if meta.proto_type in ["float", "fixed32", "sfixed32"]:
                            decoded, pos = parsed.value[pos : pos + 4], pos + 4
                            wire_type = WIRE_FIXED_32
                        elif meta.proto_type in ["double", "fixed64", "sfixed64"]:
                            decoded, pos = parsed.value[pos : pos + 8], pos + 8
                            wire_type = WIRE_FIXED_64
                        else:
                            decoded, pos = decode_varint(parsed.value, pos)
                            wire_type = WIRE_VARINT
                        decoded = self._postprocess_single(
                            wire_type, meta, field, decoded
                        )
                        value.append(decoded)
                else:
                    value = self._postprocess_single(
                        parsed.wire_type, meta, field, parsed.value
                    )

                current = getattr(self, field.name)
                if meta.proto_type == TYPE_MAP:
                    # Value represents a single key/value pair entry in the map.
                    current[value.key] = value.value
                elif isinstance(current, list) and not isinstance(value, list):
                    current.append(value)
                else:
                    setattr(self, field.name, value)
            else:
                self._unknown_fields += parsed.raw

        return self

    # For compatibility with other libraries.
    @classmethod
    def FromString(cls: Type[T], data: bytes) -> T:
        return cls().parse(data)

    def to_dict(
        self, casing: Casing = Casing.CAMEL, include_default_values: bool = False
    ) -> dict:
        """
        Returns a dict representation of this message instance which can be
        used to serialize to e.g. JSON. Defaults to camel casing for
        compatibility but can be set to other modes.

        `include_default_values` can be set to `True` to include default
        values of fields. E.g. an `int32` type field with `0` value will
        not be in returned dict if `include_default_values` is set to
        `False`.
        """
        output: Dict[str, Any] = {}
        for field in dataclasses.fields(self):
            meta = FieldMetadata.get(field)
            v = getattr(self, field.name)
            cased_name = casing(field.name).rstrip("_")  # type: ignore
            if meta.proto_type == "message":
                if isinstance(v, datetime):
                    if v != DATETIME_ZERO or include_default_values:
                        output[cased_name] = _Timestamp.timestamp_to_json(v)
                elif isinstance(v, timedelta):
                    if v != timedelta(0) or include_default_values:
                        output[cased_name] = _Duration.delta_to_json(v)
                elif meta.wraps:
                    if v is not None or include_default_values:
                        output[cased_name] = v
                elif isinstance(v, list):
                    # Convert each item.
                    v = [i.to_dict(casing, include_default_values) for i in v]
                    if v or include_default_values:
                        output[cased_name] = v
                else:
                    if v._serialized_on_wire or include_default_values:
                        output[cased_name] = v.to_dict(casing, include_default_values)
            elif meta.proto_type == "map":
                for k in v:
                    if hasattr(v[k], "to_dict"):
                        v[k] = v[k].to_dict(casing, include_default_values)

                if v or include_default_values:
                    output[cased_name] = v
            elif v != self._get_field_default(field, meta) or include_default_values:
                if meta.proto_type in INT_64_TYPES:
                    if isinstance(v, list):
                        output[cased_name] = [str(n) for n in v]
                    else:
                        output[cased_name] = str(v)
                elif meta.proto_type == TYPE_BYTES:
                    if isinstance(v, list):
                        output[cased_name] = [b64encode(b).decode("utf8") for b in v]
                    else:
                        output[cased_name] = b64encode(v).decode("utf8")
                elif meta.proto_type == TYPE_ENUM:
                    enum_values = list(
                        self._betterproto.cls_by_field[field.name]
                    )  # type: ignore
                    if isinstance(v, list):
                        output[cased_name] = [enum_values[e].name for e in v]
                    else:
                        output[cased_name] = enum_values[v].name
                else:
                    output[cased_name] = v
        return output


@dataclasses.dataclass
class _Duration(Message):
    # Signed seconds of the span of time. Must be from -315,576,000,000 to
    # +315,576,000,000 inclusive. Note: these bounds are computed from: 60
    # sec/min * 60 min/hr * 24 hr/day * 365.25 days/year * 10000 years
    seconds: int = int64_field(1)
    # Signed fractions of a second at nanosecond resolution of the span of time.
    # Durations less than one second are represented with a 0 `seconds` field and
    # a positive or negative `nanos` field. For durations of one second or more,
    # a non-zero value for the `nanos` field must be of the same sign as the
    # `seconds` field. Must be from -999,999,999 to +999,999,999 inclusive.
    nanos: int = int32_field(2)

    def to_timedelta(self) -> timedelta:
        return timedelta(seconds=self.seconds, microseconds=self.nanos / 1e3)

    @staticmethod
    def delta_to_json(delta: timedelta) -> str:
        parts = str(delta.total_seconds()).split(".")
        if len(parts) > 1:
            while len(parts[1]) not in [3, 6, 9]:
                parts[1] = parts[1] + "0"
        return ".".join(parts) + "s"


@dataclasses.dataclass
class _Timestamp(Message):
    # Represents seconds of UTC time since Unix epoch 1970-01-01T00:00:00Z. Must
    # be from 0001-01-01T00:00:00Z to 9999-12-31T23:59:59Z inclusive.
    seconds: int = int64_field(1)
    # Non-negative fractions of a second at nanosecond resolution. Negative
    # second values with fractions must still have non-negative nanos values that
    # count forward in time. Must be from 0 to 999,999,999 inclusive.
    nanos: int = int32_field(2)

    def to_datetime(self) -> datetime:
        ts = self.seconds + (self.nanos / 1e9)
        return datetime.fromtimestamp(ts, tz=timezone.utc)

    @staticmethod
    def timestamp_to_json(dt: datetime) -> str:
        nanos = dt.microsecond * 1e3
        copy = dt.replace(microsecond=0, tzinfo=None)
        result = copy.isoformat()
        if (nanos % 1e9) == 0:
            # If there are 0 fractional digits, the fractional
            # point '.' should be omitted when serializing.
            return result + "Z"
        if (nanos % 1e6) == 0:
            # Serialize 3 fractional digits.
            return result + ".%03dZ" % (nanos / 1e6)
        if (nanos % 1e3) == 0:
            # Serialize 6 fractional digits.
            return result + ".%06dZ" % (nanos / 1e3)
        # Serialize 9 fractional digits.
        return result + ".%09dZ" % nanos


class _WrappedMessage(Message):
    """
    Google protobuf wrapper types base class. JSON representation is just the
    value itself.
    """

    value: Any

    def to_dict(self, casing: Casing = Casing.CAMEL) -> Any:
        return self.value


@dataclasses.dataclass
class _BoolValue(_WrappedMessage):
    value: bool = bool_field(1)


@dataclasses.dataclass
class _Int32Value(_WrappedMessage):
    value: int = int32_field(1)


@dataclasses.dataclass
class _UInt32Value(_WrappedMessage):
    value: int = uint32_field(1)


@dataclasses.dataclass
class _Int64Value(_WrappedMessage):
    value: int = int64_field(1)


@dataclasses.dataclass
class _UInt64Value(_WrappedMessage):
    value: int = uint64_field(1)


@dataclasses.dataclass
class _FloatValue(_WrappedMessage):
    value: float = float_field(1)


@dataclasses.dataclass
class _DoubleValue(_WrappedMessage):
    value: float = double_field(1)


@dataclasses.dataclass
class _StringValue(_WrappedMessage):
    value: str = string_field(1)


@dataclasses.dataclass
class _BytesValue(_WrappedMessage):
    value: bytes = bytes_field(1)


def _get_wrapper(proto_type: str) -> Type:
    """Get the wrapper message class for a wrapped type."""
    return {
        TYPE_BOOL: _BoolValue,
        TYPE_INT32: _Int32Value,
        TYPE_UINT32: _UInt32Value,
        TYPE_INT64: _Int64Value,
        TYPE_UINT64: _UInt64Value,
        TYPE_FLOAT: _FloatValue,
        TYPE_DOUBLE: _DoubleValue,
        TYPE_STRING: _StringValue,
        TYPE_BYTES: _BytesValue,
    }[proto_type]


_Value = Union[str, bytes]
_MetadataLike = Union[Mapping[str, _Value], Collection[Tuple[str, _Value]]]


from dataclasses import dataclass
from typing import (
    List,
    Optional,
)


class LensOverlayFilterType(Enum):
    """Supported filter types."""

    UNKNOWN_FILTER_TYPE = 0
    TRANSLATE = 2
    AUTO_FILTER = 7


class Platform(Enum):
    UNSPECIFIED = 0
    WEB = 3
    LENS_OVERLAY = 6


class Surface(Enum):
    UNSPECIFIED = 0
    CHROMIUM = 4
    LENS_OVERLAY = 42


class LensRenderingEnvironment(Enum):
    """The possible rendering environments."""

    RENDERING_ENV_UNSPECIFIED = 0
    RENDERING_ENV_LENS_OVERLAY = 14


class LensOverlayPhaseLatenciesMetadataImageType(Enum):
    UNKNOWN = 0
    JPEG = 1
    PNG = 2
    WEBP = 3


class LensOverlayClientLogsLensOverlayEntryPoint(Enum):
    UNKNOWN_ENTRY_POINT = 0
    APP_MENU = 1
    PAGE_CONTEXT_MENU = 2
    IMAGE_CONTEXT_MENU = 3
    OMNIBOX_BUTTON = 4
    TOOLBAR_BUTTON = 5
    FIND_IN_PAGE = 6


class ClientPlatform(Enum):
    UNSPECIFIED = 0
    LENS_OVERLAY = 2


class CoordinateType(Enum):
    """Specifies the coordinate system used for geometry protos."""

    UNSPECIFIED = 0
    """Unspecified default value, per proto best practice."""

    NORMALIZED = 1
    """Normalized coordinates."""

    IMAGE = 2
    """Image pixel coordinates."""


class PolygonVertexOrdering(Enum):
    """Specifies the vertex ordering."""

    VERTEX_ORDERING_UNSPECIFIED = 0
    CLOCKWISE = 1
    COUNTER_CLOCKWISE = 2


class WritingDirection(Enum):
    """The text reading order."""

    LEFT_TO_RIGHT = 0
    RIGHT_TO_LEFT = 1
    TOP_TO_BOTTOM = 2


class Alignment(Enum):
    """The text alignment."""

    DEFAULT_LEFT_ALIGNED = 0
    RIGHT_ALIGNED = 1
    CENTER_ALIGNED = 2


class TextLayoutWordType(Enum):
    TEXT = 0
    """Printed text."""

    FORMULA = 1
    """Formula type, including mathematical or chemical formulas."""


class TranslationDataStatusCode(Enum):
    UNKNOWN = 0
    SUCCESS = 1
    SERVER_ERROR = 2
    UNSUPPORTED_LANGUAGE_PAIR = 3
    SAME_LANGUAGE = 4
    UNKNOWN_SOURCE_LANGUAGE = 5
    INVALID_REQUEST = 6
    DEADLINE_EXCEEDED = 7
    EMPTY_TRANSLATION = 8
    NO_OP_TRANSLATION = 9


class TranslationDataBackgroundImageDataFileFormat(Enum):
    """File format of the bytes in background_image."""

    UNKNOWN = 0
    RAW_BYTES_RGBA = 1
    PNG_RGBA = 2
    WEBP_RGBA = 3
    JPEG_RGB_PNG_MASK = 4


class LensOverlayInteractionRequestMetadataType(Enum):
    UNKNOWN = 0
    TAP = 1
    """User's tap on the screen."""

    REGION = 2
    """User's region selection on the screenshot."""

    TEXT_SELECTION = 3
    """User's text selection on the screenshot."""

    REGION_SEARCH = 4
    """User selected a bounding box to region search."""

    OBJECT_FULFILLMENT = 5
    """Requests selection and fulfillment of a specific object."""

    CONTEXTUAL_SEARCH_QUERY = 9
    """User sent a query in the contextual search box."""

    PDF_QUERY = 10
    """User sent a query about a pdf."""

    WEBPAGE_QUERY = 11
    """User sent a query about a website."""


class OverlayObjectRenderingMetadataRenderType(Enum):
    DEFAULT = 0
    GLEAM = 1


class RequestType(Enum):
    """The type of the request the payload is sent in."""

    DEFAULT = 0
    """Unset Request type."""

    PDF = 1
    """Request is for PDF."""

    EARLY_PARTIAL_PDF = 3
    """Request is for partial PDF upload."""

    WEBPAGE = 2
    """Request is for webpage."""


class LensOverlaySelectionType(Enum):
    """Possible selection types for Lens overlay."""

    UNKNOWN_SELECTION_TYPE = 0
    TAP_ON_EMPTY = 1
    SELECT_TEXT_HIGHLIGHT = 3
    REGION_SEARCH = 7
    INJECTED_IMAGE = 10
    TAP_ON_REGION_GLEAM = 15
    MULTIMODAL_SEARCH = 18
    SELECT_TRANSLATED_TEXT = 21
    TAP_ON_OBJECT = 22
    MULTIMODAL_SUGGEST_TYPEAHEAD = 25
    MULTIMODAL_SUGGEST_ZERO_PREFIX = 26
    TRANSLATE_CHIP = 52
    SYMBOLIC_MATH_OBJECT = 53


class CompressionType(Enum):
    """Possible compression types for content_data."""

    UNCOMPRESSED = 0
    """Default value. File is not compressed."""

    ZSTD = 1
    """ZSTD compression."""


class ContentDataContentType(Enum):
    """
    Possible types of the content.
     Next ID: 6
    """

    CONTENT_TYPE_UNSPECIFIED = 0
    """Default value."""

    CONTENT_TYPE_PDF = 1
    """PDF content."""

    CONTENT_TYPE_INNER_TEXT = 2
    """Inner text content."""

    CONTENT_TYPE_INNER_HTML = 3
    """Inner HTML content."""

    CONTENT_TYPE_ANNOTATED_PAGE_CONTENT = 4
    """Annotated page content."""

    CONTENT_TYPE_EARLY_PARTIAL_PDF = 5
    """Early partial PDF content."""


class LensOverlayServerErrorErrorType(Enum):
    UNKNOWN_TYPE = 0
    MISSING_REQUEST = 1


class StickinessSignalsNamespace(Enum):
    UNKNOWN = 0
    TRANSLATE_LITE = 56
    EDUCATION_INPUT = 79


@dataclass(eq=False, repr=False)
class AppliedFilter(Message):
    """Supported filter types."""

    filter_type: "LensOverlayFilterType" = enum_field(1)
    translate: "AppliedFilterTranslate" = message_field(3, group="filter_payload")


@dataclass(eq=False, repr=False)
class AppliedFilterTranslate(Message):
    target_language: str = string_field(1)
    source_language: str = string_field(2)


@dataclass(eq=False, repr=False)
class AppliedFilters(Message):
    """Supported filter types."""

    filter: List["AppliedFilter"] = message_field(1)


@dataclass(eq=False, repr=False)
class LensOverlayClientContext(Message):
    """Context information of the client sending the request."""

    platform: "Platform" = enum_field(1)
    """Required. Client platform."""

    surface: "Surface" = enum_field(2)
    """Optional. Client surface."""

    locale_context: "LocaleContext" = message_field(4)
    """Required. Locale specific context."""

    app_id: str = string_field(6)
    """
    Required. Name of the package which sends the request to Lens Frontend.
    """

    client_filters: "AppliedFilters" = message_field(17)
    """Filters that are enabled on the client side."""

    rendering_context: "RenderingContext" = message_field(20)
    """The rendering context info."""

    client_logging_data: "ClientLoggingData" = message_field(23)
    """Logging data."""


@dataclass(eq=False, repr=False)
class LocaleContext(Message):
    """Describes locale context."""

    language: str = string_field(1)
    """The BCP 47 language tag used to identify the language of the client."""

    region: str = string_field(2)
    """The CLDR region tag used to identify the region of the client."""

    time_zone: str = string_field(3)
    """The CLDR time zone ID used to identify the timezone of the client."""


@dataclass(eq=False, repr=False)
class RenderingContext(Message):
    rendering_environment: "LensRenderingEnvironment" = enum_field(2)
    """The rendering environment."""


@dataclass(eq=False, repr=False)
class ClientLoggingData(Message):
    """Contains data that can be used for logging purposes."""

    is_history_eligible: bool = bool_field(1)
    """Whether history is enabled."""


@dataclass(eq=False, repr=False)
class LensOverlayPhaseLatenciesMetadata(Message):
    """Phase latency metadata for the Lens Overlay."""

    phase: List["LensOverlayPhaseLatenciesMetadataPhase"] = message_field(1)


@dataclass(eq=False, repr=False)
class LensOverlayPhaseLatenciesMetadataPhase(Message):
    """
    Represents a single point in time during the image preprocessing flow.
    """

    image_downscale_data: "LensOverlayPhaseLatenciesMetadataPhaseImageDownscaleData" = (
        message_field(3, group="phase_data")
    )
    """Data specifically only relevant for IMAGE_DOWNSCALE_END PhaseType."""

    image_encode_data: "LensOverlayPhaseLatenciesMetadataPhaseImageEncodeData" = (
        message_field(4, group="phase_data")
    )
    """Data specifically only relevant for IMAGE_ENCODE_END PhaseType."""


@dataclass(eq=False, repr=False)
class LensOverlayPhaseLatenciesMetadataPhaseImageDownscaleData(Message):
    original_image_size: int = int64_field(1)
    """The size of the original image, in pixels."""

    downscaled_image_size: int = int64_field(2)
    """The size of the downscaled image, in pixels."""


@dataclass(eq=False, repr=False)
class LensOverlayPhaseLatenciesMetadataPhaseImageEncodeData(Message):
    original_image_type: "LensOverlayPhaseLatenciesMetadataImageType" = enum_field(1)
    """
    The type of the original Image. This only applies to IMAGE_ENCODE_END
     PhaseTypes
    """

    encoded_image_size_bytes: int = int64_field(2)
    """The bytes size of the encoded image."""


@dataclass(eq=False, repr=False)
class LensOverlayClientLogs(Message):
    phase_latencies_metadata: "LensOverlayPhaseLatenciesMetadata" = message_field(1)
    """
    The phase latency metadata for any image preprocessing required for the
     request.
    """

    lens_overlay_entry_point: "LensOverlayClientLogsLensOverlayEntryPoint" = enum_field(
        2
    )
    """The Lens Overlay entry point used to access lens."""

    paella_id: int = uint64_field(3)
    """
    A unique identifier for associating events logged by lens asynchronously.
    """

    metrics_collection_disabled: bool = bool_field(5)
    """Whether the user has disabled metrics collection."""


@dataclass(eq=False, repr=False)
class LensOverlayRoutingInfo(Message):
    """Information about where to route the request."""

    server_address: str = string_field(1)
    """Address to route the request to."""

    cell_address: str = string_field(3)
    """Cell to route the request to."""

    blade_target: str = string_field(2)
    """Blade target to route the request to."""


@dataclass(eq=False, repr=False)
class LensOverlayClusterInfo(Message):
    """The cluster info for a Lens Overlay session."""

    server_session_id: str = string_field(1)
    """ID for subsequent server requests."""

    search_session_id: str = string_field(2)
    """ID for subsequent search requests."""

    routing_info: "LensOverlayRoutingInfo" = message_field(6)
    """Info used for routing subsequent requests."""


@dataclass(eq=False, repr=False)
class Polygon(Message):
    """Information about a polygon."""

    vertex: List["PolygonVertex"] = message_field(1)
    vertex_ordering: "PolygonVertexOrdering" = enum_field(2)
    coordinate_type: "CoordinateType" = enum_field(3)
    """Specifies the coordinate type of vertices."""


@dataclass(eq=False, repr=False)
class PolygonVertex(Message):
    """Represents a single vertex in the polygon."""

    x: float = float_field(1)
    y: float = float_field(2)


@dataclass(eq=False, repr=False)
class CenterRotatedBox(Message):
    """Information about a center bounding box rotated around its center."""

    center_x: float = float_field(1)
    center_y: float = float_field(2)
    width: float = float_field(3)
    height: float = float_field(4)
    rotation_z: float = float_field(5)
    """
    Clockwise rotation around the center in radians. The rotation angle is
     computed before normalizing the coordinates.
    """

    coordinate_type: "CoordinateType" = enum_field(6)
    """
    Specifies the coordinate type of center and size.
     @note default is COORDINATE_TYPE_UNSPECIFIED, please initialize this value
     to NORMALIZED or IMAGE for Lens detection API usage.
    """


@dataclass(eq=False, repr=False)
class Geometry(Message):
    """Geometric shape(s) used for tracking and detection."""

    bounding_box: "CenterRotatedBox" = message_field(1)
    """Specifies the bounding box for this geometry."""

    segmentation_polygon: List["Polygon"] = message_field(5)
    """
    Specifies the segmentation polygon. The vertices of the outer-boundaries
     are in clockwise, and the ones of inner-boundaries are in counter-clockwise
     ordering.
    """


@dataclass(eq=False, repr=False)
class ZoomedCrop(Message):
    """
    A cropped and potentially re-scaled image region, rectangular subregion of a
     canonical image.
    """

    crop: "CenterRotatedBox" = message_field(1)
    """The cropped region of the parent image in parent coordinates."""

    parent_width: int = int32_field(2)
    """Width of the parent image."""

    parent_height: int = int32_field(3)
    """Height of the parent image."""

    zoom: float = float_field(4)
    """
    The ratio of the pixel dimensions of the child image to the pixel
     dimensions of the 'crop' in parent coordinates.
    """


@dataclass(eq=False, repr=False)
class Text(Message):
    text_layout: "TextLayout" = message_field(1)
    """Optional. Information describing the text."""

    content_language: str = string_field(2)
    """
    Optional. Dominant content language of the text. Language
     code is CLDR/BCP-47.
    """


@dataclass(eq=False, repr=False)
class TextLayout(Message):
    """Nested text structure."""

    paragraphs: List["TextLayoutParagraph"] = message_field(1)
    """Optional. List of paragraphs in natural reading order."""


@dataclass(eq=False, repr=False)
class TextLayoutWord(Message):
    id: "TextEntityIdentifier" = message_field(1)
    """Required. Unique id within TextLayout."""

    plain_text: str = string_field(2)
    """Optional. The text in a plain text."""

    text_separator: Optional[str] = string_field(3)
    """
    Optional. The text separator that should be appended after this word when
     it is concatenated with the subsequent word in the same or next
     line/paragraph into a single-line string. This is specified as optional
     because there is a distinction between the absence of a separator and
     the empty string as a separator.
    """

    geometry: "Geometry" = message_field(4)
    """Optional. The geometry of the word."""

    type: "TextLayoutWordType" = enum_field(5)
    """Optional. The type of this word."""

    formula_metadata: "TextLayoutWordFormulaMetadata" = message_field(6)
    """
    Optional. Metadata for formulas. This is populated for entities of
     `type=FORMULA`.
    """


@dataclass(eq=False, repr=False)
class TextLayoutWordFormulaMetadata(Message):
    latex: str = string_field(1)
    """
    Optional. LaTeX representation of a formula. Can be the same as
     `plain_text`. Example: "\frac{2}{x}=y". The plain text
     representation of this is available in Word.plain_text.
    """


@dataclass(eq=False, repr=False)
class TextLayoutLine(Message):
    words: List["TextLayoutWord"] = message_field(1)
    """Optional. List of words in natural reading order."""

    geometry: "Geometry" = message_field(2)
    """Optional. The geometry of the line."""


@dataclass(eq=False, repr=False)
class TextLayoutParagraph(Message):
    id: "TextEntityIdentifier" = message_field(1)
    """Required. Unique id within TextLayout."""

    lines: List["TextLayoutLine"] = message_field(2)
    """
    Optional. List of lines in natural reading order (see also
     `writing_direction`).
    """

    geometry: "Geometry" = message_field(3)
    """Optional. Geometry of the paragraph."""

    writing_direction: "WritingDirection" = enum_field(4)
    """Optional. The text writing direction (aka reading order)."""

    content_language: str = string_field(5)
    """
    Optional. BCP-47 language code of the dominant language in this
     paragraph.
    """


@dataclass(eq=False, repr=False)
class TextEntityIdentifier(Message):
    id: int = int64_field(1)
    """
    Required. Unique entity id used to reference (and match) text entities and
     ranges.
    """


@dataclass(eq=False, repr=False)
class DeepGleamData(Message):
    translation: "TranslationData" = message_field(10, group="rendering_oneof")
    visual_object_id: List[str] = string_field(11)


@dataclass(eq=False, repr=False)
class TranslationData(Message):
    status: "TranslationDataStatus" = message_field(1)
    target_language: str = string_field(2)
    source_language: str = string_field(3)
    translation: str = string_field(4)
    """The translated text."""

    line: List["TranslationDataLine"] = message_field(5)
    writing_direction: "WritingDirection" = enum_field(7)
    """The original writing direction of the source text."""

    alignment: "Alignment" = enum_field(8)
    justified: bool = bool_field(9)
    """Whether the text is justified."""


@dataclass(eq=False, repr=False)
class TranslationDataStatus(Message):
    code: "TranslationDataStatusCode" = enum_field(1)


@dataclass(eq=False, repr=False)
class TranslationDataTextStyle(Message):
    """
    Style as the aggregation of the styles of the words in the original text.
    """

    text_color: int = uint32_field(1)
    """The foreground color of text in aRGB format."""

    background_primary_color: int = uint32_field(2)
    """The background color of text in aRGB format."""


@dataclass(eq=False, repr=False)
class TranslationDataBackgroundImageData(Message):
    """Properties of the image used to inpaint the source text."""

    background_image: bytes = bytes_field(1)
    """
    Image bytes to inpaint the source text. Contains image bytes in the
     format specified in file_format.
    """

    image_width: int = int32_field(2)
    """Width of background_image in pixels."""

    image_height: int = int32_field(3)
    """Height of background_image in pixels."""

    vertical_padding: float = float_field(4)
    """
    Vertical padding to apply to the text box before drawing the background
     image. Expressed as a fraction of the text box height, i.e. 1.0 means
     that the height should be doubled. Half of the padding should be added on
     the top and half on the bottom.
    """

    horizontal_padding: float = float_field(5)
    """
    Horizontal padding to apply to the text box before drawing the background
     image. Expressed as a fraction of the text box height. Half of the
     padding should be added on the left and half on the right.
    """

    file_format: "TranslationDataBackgroundImageDataFileFormat" = enum_field(6)
    text_mask: bytes = bytes_field(7)
    """Text mask for the generated background image."""


@dataclass(eq=False, repr=False)
class TranslationDataLine(Message):
    start: int = int32_field(1)
    """
    A substring from the translation from start to end (exclusive),
     that needs to be distributed on this line, measured in Unicode
     characters. If not set, the Line doesn't have any translation.
    """

    end: int = int32_field(2)
    style: "TranslationDataTextStyle" = message_field(3)
    word: List["TranslationDataLineWord"] = message_field(5)
    background_image_data: "TranslationDataBackgroundImageData" = message_field(9)
    """Background image data is set only when inpainting is computed."""


@dataclass(eq=False, repr=False)
class TranslationDataLineWord(Message):
    start: int = int32_field(1)
    """
    A substring from the translation from start to end (exclusive),
     representing a word (without separator), measured in Unicode
     characters.
    """

    end: int = int32_field(2)


@dataclass(eq=False, repr=False)
class LensOverlayDocument(Message):
    """
    Top-level PDF representation extracted using Pdfium.
     Next ID: 6
    """

    pages: List["Page"] = message_field(1)
    """Ordered pdf pages."""


@dataclass(eq=False, repr=False)
class Page(Message):
    """
    Represents a single page of the PDF.
     Next ID: 10
    """

    page_number: int = int32_field(1)
    """Page number in the pdf (indexed starting at 1)."""

    text_segments: List[str] = string_field(4)
    """List of text segments of the page."""


@dataclass(eq=False, repr=False)
class ClientImage(Message):
    """Image data from the client."""

    image_content: bytes = bytes_field(1)
    """Required. A byte array encoding an image."""


@dataclass(eq=False, repr=False)
class ImageCrop(Message):
    """User-selected / auto-detected cropped image region."""

    crop_id: str = string_field(1)
    """The ID of the cropped image region."""

    image: "ClientImage" = message_field(2)
    """The image content of the cropped image region."""

    zoomed_crop: "ZoomedCrop" = message_field(3)
    """The zoomed crop properties of the cropped image region."""


@dataclass(eq=False, repr=False)
class ImageData(Message):
    """
    Data representing image. Contains image bytes or image retrieval identifier.
    """

    payload: "ImagePayload" = message_field(1)
    """Image payload to process. This contains image bytes."""

    image_metadata: "ImageMetadata" = message_field(3)
    """Required. Context of the given image."""

    significant_regions: List["Geometry"] = message_field(4)
    """The bounds of significant regions in the image."""


@dataclass(eq=False, repr=False)
class ImagePayload(Message):
    image_bytes: bytes = bytes_field(1)
    """Required. Image byte array."""


@dataclass(eq=False, repr=False)
class ImageMetadata(Message):
    width: int = int32_field(1)
    """
    Required. Image width in pixels. Should reflect the actual size of
     image_bytes.
    """

    height: int = int32_field(2)
    """
    Required. Image height in pixels. Should reflect the actual size of
     image_bytes.
    """


@dataclass(eq=False, repr=False)
class TextQuery(Message):
    """Contains an unstructured text query to add to an image query."""

    query: str = string_field(1)
    """The unstructured text query, such as "blue" or "blouse"."""

    is_primary: bool = bool_field(2)


@dataclass(eq=False, repr=False)
class LensOverlayInteractionRequestMetadata(Message):
    """Metadata associated with an interaction request."""

    type: "LensOverlayInteractionRequestMetadataType" = enum_field(1)
    selection_metadata: "LensOverlayInteractionRequestMetadataSelectionMetadata" = (
        message_field(2)
    )
    query_metadata: "LensOverlayInteractionRequestMetadataQueryMetadata" = (
        message_field(4)
    )


@dataclass(eq=False, repr=False)
class LensOverlayInteractionRequestMetadataSelectionMetadata(Message):
    """
    Metadata related to the selection associated with this interaction request.
    """

    point: "LensOverlayInteractionRequestMetadataSelectionMetadataPoint" = (
        message_field(1, group="selection")
    )
    region: "LensOverlayInteractionRequestMetadataSelectionMetadataRegion" = (
        message_field(2, group="selection")
    )
    object: "LensOverlayInteractionRequestMetadataSelectionMetadataObject" = (
        message_field(3, group="selection")
    )


@dataclass(eq=False, repr=False)
class LensOverlayInteractionRequestMetadataSelectionMetadataPoint(Message):
    x: float = float_field(1)
    y: float = float_field(2)


@dataclass(eq=False, repr=False)
class LensOverlayInteractionRequestMetadataSelectionMetadataRegion(Message):
    region: "CenterRotatedBox" = message_field(1)


@dataclass(eq=False, repr=False)
class LensOverlayInteractionRequestMetadataSelectionMetadataObject(Message):
    object_id: str = string_field(1)
    geometry: "Geometry" = message_field(2)


@dataclass(eq=False, repr=False)
class LensOverlayInteractionRequestMetadataQueryMetadata(Message):
    """Metadata related to query."""

    text_query: "TextQuery" = message_field(2)
    """The text query information."""


@dataclass(eq=False, repr=False)
class TranslateStickinessSignals(Message):
    """
    base specific to queries coming from translate stickiness extension.
    """

    translate_suppress_echo_for_sticky: bool = bool_field(1)


@dataclass(eq=False, repr=False)
class FunctionCall(Message):
    """A message representing the function call of an answers intent query."""

    name: str = string_field(1)
    """Name of this function call."""

    argument: List["Argument"] = message_field(2)
    """A list of arguments of this function call."""

    base: "FunctionCallSignals" = message_field(4)
    """base at the function call level"""


@dataclass(eq=False, repr=False)
class FunctionCallSignals(Message):
    """base at the function call level"""

    translate_stickiness_signals: "TranslateStickinessSignals" = message_field(
        311378150
    )


@dataclass(eq=False, repr=False)
class Argument(Message):
    """A message representing the function argument."""

    name: str = string_field(1)
    """Name of this argument."""

    value: "ArgumentValue" = message_field(2)
    """The value of this argument."""


@dataclass(eq=False, repr=False)
class ArgumentValue(Message):
    """A message representing the value of an argument."""

    simple_value: "SimpleValue" = message_field(3, group="value")


@dataclass(eq=False, repr=False)
class SimpleValue(Message):
    """A message representing a simple literal value."""

    string_value: str = string_field(1, group="value")


@dataclass(eq=False, repr=False)
class Query(Message):
    """A Query is a representation of the meaning of the user query."""

    intent_query: "FunctionCall" = message_field(56249026)


@dataclass(eq=False, repr=False)
class MathSolverQuery(Message):
    math_input_equation: str = string_field(3)


@dataclass(eq=False, repr=False)
class MessageSet(Message):
    """This is proto2's version of MessageSet."""

    message_set_extension: "Query" = message_field(41401449)


@dataclass(eq=False, repr=False)
class OverlayObject(Message):
    """Overlay Object."""

    id: str = string_field(1)
    """The id."""

    geometry: "Geometry" = message_field(2)
    """The object geometry."""

    rendering_metadata: "OverlayObjectRenderingMetadata" = message_field(8)
    """The rendering metadata for the object."""

    interaction_properties: "OverlayObjectInteractionProperties" = message_field(4)
    is_fulfilled: bool = bool_field(9)
    """
    Indicates to the client that this object is eligible to be an object
     fulfillment request.
    """


@dataclass(eq=False, repr=False)
class OverlayObjectRenderingMetadata(Message):
    """Rendering metadata for the object."""

    render_type: "OverlayObjectRenderingMetadataRenderType" = enum_field(1)


@dataclass(eq=False, repr=False)
class OverlayObjectInteractionProperties(Message):
    select_on_tap: bool = bool_field(1)
    """Whether an object can be tapped"""


@dataclass(eq=False, repr=False)
class LensOverlayRequestId(Message):
    """
    Request Id definition to support request sequencing and state lookup.
     Next Id: 10
    """

    uuid: int = uint64_field(1)
    """A unique identifier for a sequence of related Lens requests."""

    sequence_id: int = int32_field(2)
    """
    An id to indicate the order of the current request within a sequence of
     requests sharing the same uuid. Starts from 1, increments by 1 if there is
     a new request with the same uuid.
    """

    image_sequence_id: int = int32_field(3)
    """
    An id to indicate the order of image payload sent within a sequence of
     requests sharing the same uuid. Starts from 1, increments by 1 if there is
     a new request with an image payload with the same uuid.
     Note, region search request does not increment this id.
    """

    analytics_id: bytes = bytes_field(4)
    """
    Analytics ID for the Lens request. Will be updated on the initial request
     and once per interaction request.
    """

    long_context_id: int = int32_field(9)
    """
    An id to indicate the order of contextual document payloads sent within a
     sequence of requests sharing the same uuid. Starts from 1, increments by 1
     if there is a new request with a contextual payload with the same uuid.
    """

    routing_info: "LensOverlayRoutingInfo" = message_field(6)
    """Information about where to route the request."""


@dataclass(eq=False, repr=False)
class LensOverlayRequestContext(Message):
    """Request context for a Lens Overlay request."""

    request_id: "LensOverlayRequestId" = message_field(3)
    """Required. Identifiers for this request."""

    client_context: "LensOverlayClientContext" = message_field(4)
    """The client context for the request."""


@dataclass(eq=False, repr=False)
class LensOverlayObjectsRequest(Message):
    request_context: "LensOverlayRequestContext" = message_field(1)
    """Required. Basic information and context for the request."""

    image_data: "ImageData" = message_field(3)
    """Required. Image Data to process."""

    payload: "Payload" = message_field(4)
    """
    Optional. Data payload of the request.
     TODO(b/359638436): Mark required when clients have migrated to use Payload
     field.
    """


@dataclass(eq=False, repr=False)
class LensOverlayUploadChunkRequest(Message):
    request_context: "LensOverlayRequestContext" = message_field(1)
    """
    Required. Chunks of the same payload should have the same request
     context.
    """

    debug_options: "ChunkDebugOptions" = message_field(6)
    """Optional. Debug options for the request."""

    chunk_id: int = int64_field(3)
    """
    Required. The id of the chunk. This should start from 0 for the first
     chunk and go up to (total_chunks - 1) in sequential chunk order.
    """

    chunk_bytes: bytes = bytes_field(4)
    """Required. The bytes of the payload chunk to upload."""


@dataclass(eq=False, repr=False)
class LensOverlayUploadChunkResponse(Message):
    debug_metadata: "ChunkDebugMetadata" = message_field(2)
    """Debug metadata from the upload chunk response."""


@dataclass(eq=False, repr=False)
class ChunkDebugOptions(Message):
    total_chunks: int = int64_field(1)
    """
    Required in first chunk request of the payload. Optional afterwards.
     Total number of chunks that will be uploaded to Lens server for the given
     payload.
    """

    query_chunks: bool = bool_field(2)
    """
    Optional. When true, Lens server will return a repeated list of remaining
     chunk ids that it expects to receive to complete the payload. Should only
     be used for debugging purposes.
    """


@dataclass(eq=False, repr=False)
class ChunkDebugMetadata(Message):
    remaining_chunks: List[int] = int64_field(1)
    """
    Only populated if ChunkDebugOptions.query_chunks is true in the
     UploadChunk request. List of chunk ids that Lens server is expecting to
     complete the payload. Should only be used for debugging purposes.
    """


@dataclass(eq=False, repr=False)
class LensOverlayObjectsResponse(Message):
    overlay_objects: List["OverlayObject"] = message_field(2)
    """Overlay objects."""

    text: "Text" = message_field(3)
    """Text."""

    deep_gleams: List["DeepGleamData"] = message_field(4)
    """Gleams."""

    cluster_info: "LensOverlayClusterInfo" = message_field(7)
    """The cluster info."""


@dataclass(eq=False, repr=False)
class LensOverlayInteractionRequest(Message):
    request_context: "LensOverlayRequestContext" = message_field(1)
    """Basic information and context for the request."""

    interaction_request_metadata: "LensOverlayInteractionRequestMetadata" = (
        message_field(2)
    )
    """Metadata associated with an interaction request."""

    image_crop: "ImageCrop" = message_field(3)
    """The image crop data."""


@dataclass(eq=False, repr=False)
class LensOverlayInteractionResponse(Message):
    encoded_response: str = string_field(3)
    text: "Text" = message_field(5)


@dataclass(eq=False, repr=False)
class Payload(Message):
    """Next ID: 11"""

    request_type: "RequestType" = enum_field(6)
    """Optional. The type of the request."""

    image_data: "ImageData" = message_field(2)
    """
    Currently unset, use image_data in ObjectsRequest.
     TODO(b/359638436): Move ObjectsRequest clients onto Payload.ImageData.
    """

    content_data: bytes = bytes_field(3)
    """
    Data for non-image payloads. May be sent with or without an image in the
     image_data field. If content_data is set, content_type must also be set.
     TODO(crbug.com/399173540): Deprecate this field in favor of content.
    """

    content_type: str = string_field(4)
    """
    The media type/MIME type of the data represented i content_data, e.g.
     "application/pdf". If content_type is set, content_data should also be set.
     TODO(crbug.com/399173540): Deprecate this field in favor of content.
    """

    page_url: str = string_field(5)
    """
    The page url this request was made on.
     TODO(crbug.com/399173540): Deprecate this field in favor of content.
    """

    partial_pdf_document: "LensOverlayDocument" = message_field(7)
    """
    The partially parsed PDF document. Used to get early suggest base. This
     is only set for REQUEST_TYPE_EARLY_PARTIAL_PDF.
     TODO(crbug.com/399173540): Deprecate this field in favor of content.
    """

    compression_type: "CompressionType" = enum_field(8)
    """
    Compression format of content_data. Currently only used for PDF data.
     TODO(crbug.com/399173540): Deprecate this field in favor of content.
    """

    stored_chunk_options: "StoredChunkOptions" = message_field(9)
    """
    Optional. Options for reading stored chunks from state layer.
     TODO(crbug.com/399173540): Deprecate this field in favor of content.
    """

    content: "Content" = message_field(10)
    """Non-image content to be sent to the Lens server."""


@dataclass(eq=False, repr=False)
class StoredChunkOptions(Message):
    """
    Specifies the options for the server to use when reading stored chunks from
     state layer during a streamed request.
     Next ID: 3
    """

    read_stored_chunks: bool = bool_field(1)
    """
    When set to true, Lens will retrieve payload chunks uploaded to state
     layer via the UploadChunk API and use those to construct
     content_data. If this is set, then content_type and total_stored_chunks
     must also be set.
    """

    total_stored_chunks: int = int64_field(2)
    """
    The total number of chunks the payload was split into. This is used to
     facilitate the reconstruction of content_data.
    """


@dataclass(eq=False, repr=False)
class Content(Message):
    """
    Generic content message for all types of content that can be sent to Lens.
     Next ID: 4
    """

    webpage_url: str = string_field(1)
    """Optional. Page url for the webpage."""

    content_data: List["ContentData"] = message_field(2)
    """Optional. Content items for the request."""

    request_type: "RequestType" = enum_field(3)
    """The type of the request."""


@dataclass(eq=False, repr=False)
class ContentData(Message):
    """
    Generic content data message for all types of content that can be sent to
     Lens.
     Next ID: 5
    """

    content_type: "ContentDataContentType" = enum_field(1)
    """The type of the content."""

    data: bytes = bytes_field(2)
    """The content data."""

    compression_type: "CompressionType" = enum_field(3)
    """Optional. Compression format of content_data."""

    stored_chunk_options: "StoredChunkOptions" = message_field(4)
    """Optional. Options for reading stored chunks from state layer."""


@dataclass(eq=False, repr=False)
class LensOverlayServerClusterInfoRequest(Message):
    """The cluster info request for a Lens Overlay session."""

    enable_search_session_id: bool = bool_field(1)
    """
    Whether to return a search session id alongside the server session id.
    """


@dataclass(eq=False, repr=False)
class LensOverlayServerClusterInfoResponse(Message):
    server_session_id: str = string_field(1)
    """ID for subsequent server requests."""

    search_session_id: str = string_field(2)
    """ID for subsequent search requests."""

    routing_info: "LensOverlayRoutingInfo" = message_field(3)
    """The routing info for the server session."""


@dataclass(eq=False, repr=False)
class LensOverlayServerError(Message):
    """
    An error encountered while handling a request.
     Next ID: 2
    """

    error_type: "LensOverlayServerErrorErrorType" = enum_field(1)
    """The error type."""


@dataclass(eq=False, repr=False)
class LensOverlayServerRequest(Message):
    """Next ID: 4"""

    objects_request: "LensOverlayObjectsRequest" = message_field(1)
    """Options for fetching objects."""

    interaction_request: "LensOverlayInteractionRequest" = message_field(2)
    """Options for fetching interactions."""

    client_logs: "LensOverlayClientLogs" = message_field(3)
    """Client logs for the request."""


@dataclass(eq=False, repr=False)
class LensOverlayServerResponse(Message):
    """
    Response details for an LensOverlay request.
     Next ID: 4
    """

    error: "LensOverlayServerError" = message_field(1)
    """The encountered error."""

    objects_response: "LensOverlayObjectsResponse" = message_field(2)
    """The objects response."""

    interaction_response: "LensOverlayInteractionResponse" = message_field(3)
    """The interaction response."""


@dataclass(eq=False, repr=False)
class StickinessSignals(Message):
    id_namespace: "StickinessSignalsNamespace" = enum_field(1)
    interpretation: "MessageSet" = message_field(28)
    education_input_extension: "EducationInputExtension" = message_field(121)


@dataclass(eq=False, repr=False)
class EducationInputExtension(Message):
    math_solver_query: "MathSolverQuery" = message_field(1)


@dataclass(eq=False, repr=False)
class LensOverlayVideoContextInputParams(Message):
    url: str = string_field(1)
    """Url of the video."""


@dataclass(eq=False, repr=False)
class LensOverlayVideoParams(Message):
    video_context_input_params: "LensOverlayVideoContextInputParams" = message_field(1)
    """Video context params from input."""


@dataclass(eq=False, repr=False)
class LensOverlayVisualSearchInteractionLogData(Message):
    """Log data for a Lens Overlay visual search interaction."""

    filter_data: "FilterData" = message_field(1)
    """Filter related metadata."""

    user_selection_data: "UserSelectionData" = message_field(2)
    """User Selection metadata."""

    is_parent_query: bool = bool_field(3)
    """Whether the query is a parent query."""

    client_platform: "ClientPlatform" = enum_field(4)
    """The client platform this query was originated from."""


@dataclass(eq=False, repr=False)
class FilterData(Message):
    """
    Filter data.
     Next ID: 2
    """

    filter_type: "LensOverlayFilterType" = enum_field(1)
    """
    The filter type associated with this interaction (auto, translate, etc.).
    """


@dataclass(eq=False, repr=False)
class UserSelectionData(Message):
    """
    User selection data.
     Next ID: 2
    """

    selection_type: "LensOverlaySelectionType" = enum_field(1)
    """
    The selection type associated with this interaction (e.g. region search).
    """


@dataclass(eq=False, repr=False)
class LensOverlayVisualSearchInteractionData(Message):
    """Metadata associated with a Lens Visual Search request."""

    interaction_type: "LensOverlayInteractionRequestMetadataType" = enum_field(1)
    """The type of interaction."""

    zoomed_crop: "ZoomedCrop" = message_field(7)
    """The selected region for this interaction, instead of the object id."""

    object_id: str = string_field(3)
    """
    The selected object id for this interaction, instead of the zoomed crop.
     Currently unsupported and should not be populated.
    """

    log_data: "LensOverlayVisualSearchInteractionLogData" = message_field(5)
    """Logging-specific data."""


import random
import requests


def randbytes(n):
    """Generate n random bytes."""
    return random.getrandbits(n * 8).to_bytes(n, "little")


class GoogleLens:
    LENS_ENDPOINT: str = "https://lensfrontend-pa.googleapis.com/v1/crupload"

    HEADERS: "dict[str, str]" = {
        "Host": "lensfrontend-pa.googleapis.com",
        "Connection": "keep-alive",
        "Content-Type": "application/x-protobuf",
        "X-Goog-Api-Key": "AIzaSyDr2UxVnv_U85AbhhY8XSHSIavUW0DC-sY",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Dest": "empty",
    }

    def __init__(self, session: requests.Session):
        self.client = session

    def __call__(self, raw_bytes: str, width: int, height: int):

        request = LensOverlayServerRequest()

        request.objects_request.request_context.request_id.uuid = random.randint(
            0, 2**64 - 1
        )
        request.objects_request.request_context.request_id.sequence_id = 0
        request.objects_request.request_context.request_id.image_sequence_id = 0
        request.objects_request.request_context.request_id.analytics_id = randbytes(
            n=16
        )
        request.objects_request.request_context.request_id.routing_info = (
            LensOverlayRoutingInfo()
        )

        request.objects_request.request_context.client_context.platform = Platform.WEB
        request.objects_request.request_context.client_context.surface = (
            Surface.CHROMIUM
        )

        # request.objects_request.request_context.client_context.locale_context.language = 'vi'
        # request.objects_request.request_context.client_context.locale_context.region = 'Asia/Ho_Chi_Minh'
        request.objects_request.request_context.client_context.locale_context.time_zone = (
            ""  # not set by chromium
        )

        request.objects_request.request_context.client_context.app_id = (
            ""  # not set by chromium
        )

        filter = AppliedFilter()
        filter.filter_type = LensOverlayFilterType.AUTO_FILTER
        request.objects_request.request_context.client_context.client_filters.filter.append(
            filter
        )

        request.objects_request.image_data.payload.image_bytes = raw_bytes
        request.objects_request.image_data.image_metadata.width = width
        request.objects_request.image_data.image_metadata.height = height
        payload = request.SerializeToString()

        res = self.client.post(
            self.LENS_ENDPOINT, data=payload, headers=self.HEADERS, timeout=40
        )

        response_proto = LensOverlayServerResponse().FromString(res.content)
        response_dict = response_proto.to_dict()

        result = []
        boxs = []
        paragraphs = (
            response_dict.get("objectsResponse", {})
            .get("text", {})
            .get("textLayout", {})
            .get("paragraphs", [])
        )
        if not paragraphs:
            return
        for paragraph in paragraphs:
            lines = ""
            for line in paragraph.get("lines", []):
                for word in line.get("words", []):
                    plain_text = word.get("plainText", "")
                    separator_text = word.get("textSeparator", "")
                    lines += plain_text + separator_text
            if lines:
                boundingBox = paragraph["geometry"]["boundingBox"]
                centerX = boundingBox["centerX"] * width
                centerY = boundingBox["centerY"] * height
                _width = boundingBox["width"] * width / 2
                _height = boundingBox["height"] * height / 2
                boxs.append(
                    [
                        centerX - _width,
                        centerY - _height,
                        centerX + _width,
                        centerY + _height,
                    ]
                )
                result.append(lines)
        return OCRResult(boxs=boxs, texts=result)


from qtsymbols import *
from ocrengines.baseocrclass import baseocr, OCRResult
from myutils.utils import qimage2binary


class OCR(baseocr):

    required_image_format = QImage

    def ocr(self, data: QImage):
        return GoogleLens(self.proxysession)(
            qimage2binary(data, "PNG"), data.width(), data.height()
        )
