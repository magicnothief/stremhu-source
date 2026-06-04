from common.schemas.api import SuccessResponse
from fastapi import APIRouter

router = APIRouter()


@router.get(
    "/health",
    response_model=SuccessResponse,
    tags=["Monitoring"],
)
def health() -> SuccessResponse:
    return SuccessResponse(
        success=True,
        message="🚀 StremHU Source fut! 🚀",
    )
