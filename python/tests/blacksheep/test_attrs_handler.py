from typing import Optional, Union

import pytest
from attrs import frozen
from blacksheep import Application, Response
from blacksheep.server.openapi.common import ContentInfo, ResponseInfo
from blacksheep.server.openapi.v3 import FieldInfo, OpenAPIHandler
from cattrs.preconf.orjson import make_converter
from oes.util import is_attrs_instance
from oes.util.blacksheep import JSONResponseFunc
from oes.util.blacksheep.attrs_handler import (
    AttrsTypeHandler,
    FromAttrs,
    _get_field_type,
)
from openapidocs.v3 import Info, Reference, Schema, ValueFormat, ValueType

app = Application()

app_docs = OpenAPIHandler(
    info=Info(
        title="Test",
        version="0.1.0",
    )
)

app_docs.object_types_handlers.append(AttrsTypeHandler(app_docs))

app_docs.bind_app(app)

converter = make_converter()


def _default(obj):
    if is_attrs_instance(obj):
        return converter.unstructure(obj)
    else:
        raise TypeError


json_response = JSONResponseFunc(default=_default)


@frozen
class MyClass1:
    a: int
    b: Optional[str] = None


@frozen
class MyClass2:
    c: int


@frozen
class MyClass3:
    val: int
    obj: Union[MyClass1, MyClass2]


@frozen
class MyClass4:
    val: Optional[list[Union[MyClass2, str]]]
    val2: tuple[Union[str, MyClass2, None]]
    val3: dict[str, int]


@app.router.post("/")
@app_docs(
    summary="Test endpoint",
    responses={
        200: ResponseInfo(
            "Example response",
            content=[
                ContentInfo(
                    type=MyClass4,
                )
            ],
        )
    },
)
def view(body: FromAttrs[MyClass4]) -> Response:
    """Example view."""
    return json_response(body.value)


@pytest.fixture
def docs():
    docs_obj = OpenAPIHandler(
        info=Info(
            title="Test",
            version="0.1.0",
        )
    )
    docs_obj.object_types_handlers.append(AttrsTypeHandler(docs_obj))
    return docs_obj


@pytest.mark.parametrize(
    "typ, expected",
    (
        (
            MyClass1,
            [
                FieldInfo(
                    "a",
                    Schema(
                        type=ValueType.INTEGER,
                        format=ValueFormat.INT64,
                        nullable=False,
                    ),
                ),
                FieldInfo(
                    "b",
                    Schema(
                        type=ValueType.STRING,
                        nullable=True,
                    ),
                ),
            ],
        ),
        (
            MyClass2,
            [
                FieldInfo(
                    "c",
                    Schema(
                        type=ValueType.INTEGER,
                        format=ValueFormat.INT64,
                        nullable=False,
                    ),
                )
            ],
        ),
        (
            MyClass3,
            [
                FieldInfo(
                    "val",
                    Schema(
                        type=ValueType.INTEGER,
                        format=ValueFormat.INT64,
                        nullable=False,
                    ),
                ),
                FieldInfo(
                    "obj",
                    Schema(
                        one_of=[
                            Reference("#/components/schemas/MyClass1"),
                            Reference("#/components/schemas/MyClass2"),
                        ],
                        nullable=False,
                    ),
                ),
            ],
        ),
        (
            MyClass4,
            [
                FieldInfo(
                    "val",
                    Schema(
                        type=ValueType.ARRAY,
                        items=Schema(
                            one_of=[
                                Reference("#/components/schemas/MyClass2"),
                                Schema(type=ValueType.STRING, nullable=False),
                            ],
                            nullable=False,
                        ),
                        nullable=True,
                    ),
                ),
                FieldInfo(
                    "val2",
                    Schema(
                        type=ValueType.ARRAY,
                        items=Schema(
                            one_of=[
                                Schema(type=ValueType.STRING, nullable=False),
                                Reference("#/components/schemas/MyClass2"),
                            ],
                            nullable=True,
                        ),
                        nullable=False,
                    ),
                ),
                FieldInfo(
                    "val3",
                    Schema(
                        type=ValueType.OBJECT,
                        nullable=False,
                    ),
                ),
            ],
        ),
    ),
)
def test_get_field_type(docs, typ, expected):
    ref = _get_field_type(docs, typ)
    assert isinstance(ref, Reference)
    fields = docs.get_fields(typ)
    assert fields == expected


def test_attrs_handler(docs: OpenAPIHandler):
    ref = docs.get_schema_by_type(MyClass3)
    assert isinstance(ref, Reference)

    assert docs.get_fields(MyClass3) == [
        FieldInfo(
            "val",
            Schema(
                type=ValueType.INTEGER,
                format=ValueFormat.INT64,
                nullable=False,
            ),
        ),
        FieldInfo(
            "obj",
            Schema(
                one_of=[
                    Reference("#/components/schemas/MyClass1"),
                    Reference("#/components/schemas/MyClass2"),
                ],
                nullable=False,
            ),
        ),
    ]
