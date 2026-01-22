from ninja import Schema
from typing import List


class CreateRegionalRequest(Schema):
    name: str


class UpdateRegionalRequest(Schema):
    name: str


class RegionalResponse(Schema):
    id: int
    name: str


class RegionalCreateResponse(Schema):
    """Response schema for regional creation"""

    message: str
    regional: RegionalResponse


class RegionalUpdateResponse(Schema):
    """Response schema for regional update"""

    message: str
    regional: RegionalResponse


class RegionalListResponse(Schema):
    """Response schema for listing regionals"""

    regionals: List[RegionalResponse]


class MessageResponse(Schema):
    message: str
