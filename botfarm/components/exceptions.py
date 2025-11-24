import fastapi
from fastapi import responses, status

from botfarm.entities import exceptions


async def handle_project_not_exists_error(request: fastapi.Request, exc: exceptions.BotfarmProjectNotExistsError):
    """Возвращает ответ 422, если указанный проект не найден"""
    return responses.JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={'detail': str(exc)},
    )


async def handle_user_not_exists_error(request: fastapi.Request, exc: exceptions.BotfarmUserNotExistsError):
    """Возвращает ответ 422, если указанный пользователь не найден"""
    return responses.JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={'detail': str(exc)},
    )


async def handle_user_locked_error(request: fastapi.Request, exc: exceptions.BotfarmUserLockedError):
    """Возвращает ответ 423, если пользователь уже занят"""
    return responses.JSONResponse(
        status_code=status.HTTP_423_LOCKED,
        content={'detail': str(exc)},
    )
