from code.src.models import ingredient
from fastapi import APIRouter, HTTPException
from typing import Dict, List
import json

from models import recipe

#APIRouter creates path operations for abm module
router = APIRouter(
    prefix="/v1/",
    tags=["v1"],
    responses={404: {"description": "Not found"}},
)
