from fastapi import responses
from fastapi import status
from botfarm.entities import exceptions
import fastapi


async def handle_project_not_exists_error(request: fastapi.Request, exc: exceptions.BotfarmProjectNotExistsError):
    return responses.JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={'detail': str(exc)},
    )


async def handle_user_not_exists_error(request: fastapi.Request, exc: exceptions.BotfarmUserNotExistsError):
    return responses.JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={'detail': str(exc)},
    )


async def handle_user_locked_error(request: fastapi.Request, exc: exceptions.BotfarmUserLockedError):
    return responses.JSONResponse(
        status_code=status.HTTP_423_LOCKED,
        content={'detail': str(exc)},
    )
