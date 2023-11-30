from __future__ import annotations

from typing import TYPE_CHECKING

from litestar._openapi.schema_generation import SchemaCreator
from litestar.enums import RequestEncodingType
from litestar.openapi.spec.media_type import OpenAPIMediaType
from litestar.openapi.spec.request_body import RequestBody
from litestar.params import BodyKwarg

__all__ = ("RequestBodyFactory",)


if TYPE_CHECKING:
    from litestar._openapi.factory import OpenAPIContext
    from litestar.handlers import BaseRouteHandler
    from litestar.typing import FieldDefinition


class RequestBodyFactory:
    def __init__(self, context: OpenAPIContext) -> None:
        self.context = context
        self.schema_creator = SchemaCreator(
            generate_examples=self.context.openapi_config.create_examples,
            plugins=self.context.plugins,
            schemas=self.context.schemas,
            prefer_alias=True,
        )

    def create_request_body(
        self, route_handler: BaseRouteHandler, field_definition: FieldDefinition
    ) -> RequestBody | None:
        """Create a RequestBody model for the given RouteHandler or return None."""
        media_type: RequestEncodingType | str = RequestEncodingType.JSON
        if isinstance(field_definition.kwarg_definition, BodyKwarg) and field_definition.kwarg_definition.media_type:
            media_type = field_definition.kwarg_definition.media_type

        if dto := route_handler.resolve_data_dto():
            schema = dto.create_openapi_schema(
                field_definition=field_definition,
                handler_id=route_handler.handler_id,
                schema_creator=self.schema_creator,
            )
        else:
            schema = self.schema_creator.for_field_definition(field_definition)

        return RequestBody(required=True, content={media_type: OpenAPIMediaType(schema=schema)})
