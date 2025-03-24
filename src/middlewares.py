#!/usr/bin/env python3

from typing import Callable, Awaitable
import fastapi

import utils


JWT_COOKIE_NAME = 'jwt'


async def authenticate_middleware(
        request: fastapi.Request,
        next: Callable[[fastapi.Request], Awaitable[fastapi.Response]],
) -> fastapi.Response:
    token = request.cookies.get(JWT_COOKIE_NAME)

    has_cookie = False
    request.state.username = None

    if token is not None:
        has_cookie = True

        try:
            obj = utils.validate_jwt_token(request.app.state.secret, token)
            request.state.username = obj.get('username')
        except Exception:
            # игнорируем _вообще все_ ошибки жесть
            pass

    response = await next(request)
    username = getattr(request.state, 'username', None)

    if username is not None:
        obj = {
            'username': username,
        }
        token = utils.create_jwt_token(request.app.state.secret, obj)

        response.set_cookie(JWT_COOKIE_NAME, token)
    elif has_cookie:
        response.set_cookie(JWT_COOKIE_NAME, '')

    return response


async def error_wrapper_middleware(
        request: fastapi.Request,
        next: Callable[[fastapi.Request], Awaitable[fastapi.Response]],
) -> fastapi.Response:
    try:
        return await next(request)
    except Exception as e:
        # да-да возвращаем всегда 400

        return fastapi.responses.JSONResponse(
            content = {'error': str(e)},
            status_code = 400,
        )
