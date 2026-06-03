from fastapi import APIRouter, Depends
from modules.attributes.dependencies import get_attributes_service
from modules.attributes.schemas.api import AttributeResponse
from modules.attributes.service import AttributesService

router = APIRouter(
    prefix="/attributes",
    tags=["Attributes"],
)


@router.get(
    "/",
    response_model=list[AttributeResponse],
)
def find_list(
    attributes_service: AttributesService = Depends(get_attributes_service),
):
    return attributes_service.find_list()
