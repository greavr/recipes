from fastapi import APIRouter

#APIRouter creates path operations for abm module
router = APIRouter(
    prefix="/admin/",
    tags=["admin"],
    responses={404: {"description": "Not found"}},
)