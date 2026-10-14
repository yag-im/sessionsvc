from enum import Enum

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema


class EnumByName:
    """Annotated marker to (de)serialize an enum by member name instead of value.

    Usage: `region: t.Annotated[DcRegion, EnumByName()]`
    """

    def __get_pydantic_core_schema__(self, source: type[Enum], _: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        names = list(source.__members__)
        from_name = core_schema.chain_schema(
            [
                core_schema.literal_schema(names),
                core_schema.no_info_plain_validator_function(lambda name: source[name]),
            ]
        )
        return core_schema.json_or_python_schema(
            json_schema=from_name,
            python_schema=core_schema.union_schema([core_schema.is_instance_schema(source), from_name]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda member: member.name, return_schema=core_schema.literal_schema(names)
            ),
        )
