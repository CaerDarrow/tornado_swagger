from typing import Generic, TypeVar, Optional
from pydantic.generics import GenericModel

DataT = TypeVar('DataT')


class BaseResponse(GenericModel, Generic[DataT]):
    status_code: int
    reason: Optional[str]
    data: Optional[DataT]
