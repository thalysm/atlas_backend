from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId
from pydantic_core import core_schema
from pydantic import GetCoreSchemaHandler


class PyObjectId(ObjectId):
    """Classe compatível com Pydantic v2 para validar ObjectId."""

    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, _handler: GetCoreSchemaHandler):
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.union_schema([
                core_schema.str_schema(),
                core_schema.is_instance_schema(ObjectId)
            ])
        )

    @classmethod
    def validate(cls, v: Any) -> ObjectId:
        """Aceita tanto string quanto ObjectId e converte corretamente."""
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid ObjectId")

    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema, handler):
        return handler(core_schema.str_schema())


class UserEntity(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    email: EmailStr
    username: str
    password_hash: str
    name: str
    height: Optional[float] = None
    weight: Optional[float] = None
    gender: Optional[str] = None
    birth_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
    }