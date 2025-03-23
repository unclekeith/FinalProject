# routers/call_router.py

from fastapi import APIRouter

from .schemas import CallRequest
from .services import CallService

call_router = APIRouter(prefix="/calls", tags=["Calls"])


@call_router.post(
    "/initiate/{receiver_id}",
    summary="Initiate a call",
    operation_id="post_initiate_call",
)
async def initiate_call(receiver_id: str, call_request: CallRequest):
    return CallService.initiate_call(receiver_id, call_request.caller_id)


@call_router.delete(
    "/end/{receiver_id}", summary="End a call", operation_id="delete_end_call"
)
async def end_call(receiver_id: str):
    return CallService.end_call(receiver_id)
