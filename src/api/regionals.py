from django_ratelimit.decorators import ratelimit
from ninja import Router

from src.api.dependencies import (
    get_create_regional_use_case,
    get_get_regional_use_case,
    get_get_regionals_use_case,
    get_update_regional_use_case,
    get_delete_regional_use_case,
)
from src.application.schemas.result_enums import RegionalErrorCode
from src.api.schemas.regional_dto import (
    CreateRegionalRequest,
    UpdateRegionalRequest,
    RegionalResponse,
    RegionalCreateResponse,
    RegionalUpdateResponse,
    RegionalListResponse,
    MessageResponse,
)


router = Router(tags=["Regional"])


@router.post(
    "",
    response={201: RegionalCreateResponse, 400: MessageResponse, 409: MessageResponse},
)
@ratelimit(key="ip", rate="10/m", method="POST")
def create_regional(request, payload: CreateRegionalRequest):
    """Create a new regional

    Rate limited to 10 requests per minute per IP address.
    """
    use_case = get_create_regional_use_case()
    result = use_case.execute(payload.name)

    if result.success:
        return 201, {
            "message": result.message,
            "regional": {
                "id": result.regional.id,
                "name": result.regional.name,
            },
        }
    elif result.error_code == RegionalErrorCode.ALREADY_EXISTS:
        return 409, {"message": result.message}
    else:
        return 400, {"message": result.message}


@router.get(
    "",
    response={200: RegionalListResponse},
)
def get_regionals(request):
    """Get all regionals

    Returns a list of all regionals.
    """
    use_case = get_get_regionals_use_case()
    result = use_case.execute()

    return 200, {
        "regionals": [
            {"id": regional.id, "name": regional.name} for regional in result.regionals
        ]
    }


@router.get(
    "/{regional_id}",
    response={200: RegionalResponse, 404: MessageResponse},
)
def get_regional_by_id(request, regional_id: int):
    """Get regional by ID

    Returns a single regional by its ID.
    """
    use_case = get_get_regional_use_case()
    result = use_case.execute(regional_id)

    if result.success:
        return 200, {
            "id": result.regional.id,
            "name": result.regional.name,
        }
    else:
        return 404, {"message": result.message}


@router.put(
    "/{regional_id}",
    response={200: RegionalUpdateResponse, 400: MessageResponse, 404: MessageResponse},
)
@ratelimit(key="ip", rate="10/m", method="PUT")
def update_regional(request, regional_id: int, payload: UpdateRegionalRequest):
    """Update a regional

    Updates an existing regional in the system.
    Rate limited to 10 requests per minute per IP address.
    """
    use_case = get_update_regional_use_case()
    result = use_case.execute(regional_id, payload.name)

    if result.success:
        return 200, {
            "message": result.message,
            "regional": {
                "id": result.regional.id,
                "name": result.regional.name,
            },
        }
    elif result.error_code == RegionalErrorCode.NOT_FOUND:
        return 404, {"message": result.message}
    else:
        return 400, {"message": result.message}


@router.delete(
    "/{regional_id}",
    response={200: MessageResponse, 404: MessageResponse},
)
@ratelimit(key="ip", rate="10/m", method="DELETE")
def delete_regional(request, regional_id: int):
    """Delete a regional

    Deletes an existing regional from the system.
    Rate limited to 10 requests per minute per IP address.
    """
    use_case = get_delete_regional_use_case()
    result = use_case.execute(regional_id)

    if result.success:
        return 200, {"message": result.message}
    else:
        return 404, {"message": result.message}
