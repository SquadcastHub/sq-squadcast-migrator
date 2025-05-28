from typing import Generic, TypeVar
from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T")

class ResponseWrapper(GenericModel, Generic[T]):
    data: T

class Meta(BaseModel):
    status: int
    error_message: str

class ErrorResponse(BaseModel):
    meta: Meta
