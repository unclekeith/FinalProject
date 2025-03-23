# services/call_service.py

import logging

from fastapi import HTTPException

active_calls = {}
logger = logging.getLogger(__name__)


class CallService:
    @staticmethod
    def initiate_call(receiver_id: str, caller_id: str):
        if receiver_id in active_calls:
            raise HTTPException(
                status_code=400, detail="Receiver is already in a call."
            )

        active_calls[receiver_id] = caller_id
        logger.info(f"Call initiated from {caller_id} to {receiver_id}.")
        return {"message": "Call initiated successfully."}

    @staticmethod
    def end_call(receiver_id: str):
        if receiver_id not in active_calls:
            raise HTTPException(status_code=404, detail="No active call found.")

        del active_calls[receiver_id]
        logger.info(f"Call ended for {receiver_id}.")
        return {"message": "Call ended successfully."}
