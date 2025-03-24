#!/usr/bin/env python3

import os
import contextlib

import fastapi

import models
import database
import services
import middlewares


DATABASE_URI = os.getenv(
    'DATABASE_URI',
    'postgres://postgres:postgres@postgres/postgres',
)
JWT_SECRET = os.getenv(
    'JWT_SECRET',
    'dQw4w9WgXcQ',
)


@contextlib.asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    db = await database.Database.connect(DATABASE_URI)

    app.state.user_service = services.UserService(db)
    app.state.task_service = services.TaskService(db)

    app.state.secret = JWT_SECRET

    yield


app = fastapi.FastAPI(lifespan = lifespan)
app.middleware('http')(middlewares.error_wrapper_middleware)
app.middleware('http')(middlewares.authenticate_middleware)


@app.get('/')
async def index():
    return 'hello, world'


@app.post('/users/register')
async def register(request: fastapi.Request):
    user_service: services.UserService = app.state.user_service

    obj = await request.json()
    username, password = obj.get('username'), obj.get('password')

    if username is None or not isinstance(username, str):
        raise TypeError('invalid username')
    
    if password is None or not isinstance(password, str):
        raise TypeError('invalid password')

    user = await user_service.register(username, password)
    request.state.username = user.username

    return {}


@app.post('/users/login')
async def login(request: fastapi.Request):
    user_service: services.UserService = app.state.user_service

    obj = await request.json()
    username, password = obj.get('username'), obj.get('password')

    if username is None or not isinstance(username, str):
        raise TypeError('invalid username')
    
    if password is None or not isinstance(password, str):
        raise TypeError('invalid password')

    user = await user_service.login(username, password)
    request.state.username = user.username

    return {}


@app.post('/users/logout')
async def logout(request: fastapi.Request):
    request.state.username = None

    return {}


@app.get('/tasks/list')
async def list_tasks(request: fastapi.Request):
    username = request.state.username

    if username is None:
        raise PermissionError('unauthenticated')
    
    task_service: services.TaskService = app.state.task_service

    count = request.query_params.get('count')

    if count is not None:
        try:
            count = int(count)
        except Exception:
            raise TypeError('invalid count')

    tasks = await task_service.list_tasks(username, count)

    return {'tasks': tasks}


@app.get('/tasks/search')
async def search_tasks(request: fastapi.Request):
    username = request.state.username

    if username is None:
        raise PermissionError('unauthenticated')
    
    task_service: services.TaskService = app.state.task_service

    text = request.query_params.get('text')

    if text is None or not isinstance(text, str):
        raise TypeError('invalid text')

    tasks = await task_service.search_tasks(username, text)

    return {'tasks': tasks}


@app.get('/tasks/get/{task_id}')
async def get_task(request: fastapi.Request, task_id: str):
    username = request.state.username

    if username is None:
        raise PermissionError('unauthenticated')
    
    task_service: services.TaskService = app.state.task_service

    task = await task_service.get_task(task_id, username)

    return {'task': task}


@app.post('/tasks/create')
async def create_task(request: fastapi.Request):
    username = request.state.username

    if username is None:
        raise PermissionError('unauthenticated')
    
    task_service: services.TaskService = app.state.task_service

    obj = await request.json()
    title, description, status, priority = (
        obj.get('title'),
        obj.get('description'),
        obj.get('status'),
        obj.get('priority'),
    )

    if title is None or not isinstance(title, str):
        raise TypeError('invalid title')
    
    if description is None or not isinstance(description, str):
        raise TypeError('invalid description')

    try:
        status = models.TaskStatus(status)
    except Exception:
        raise TypeError('invalid status')

    if priority is None or not isinstance(priority, int):
        raise TypeError('invalid priority')

    task = await task_service.create_task(
        username, title, description, status, priority,
    )

    return {'task_id': task.id}


@app.post('/tasks/update/{task_id}')
async def update_task(request: fastapi.Request, task_id: str):
    username = request.state.username

    if username is None:
        raise PermissionError('unauthenticated')
    
    task_service: services.TaskService = app.state.task_service

    obj = await request.json()
    title, description, status, priority = (
        obj.get('title'),
        obj.get('description'),
        obj.get('status'),
        obj.get('priority'),
    )

    if title is not None:
        if not isinstance(title, str):
            raise TypeError('invalid title')
        
    if description is not None:
        if not isinstance(description, str):
            raise TypeError('invalid description')
        
    if status is not None:
        try:
            status = models.TaskStatus(status)
        except Exception:
            raise TypeError('invalid status')
        
    if priority is not None:
        if not isinstance(priority, int):
            raise TypeError('invalid priority')

    await task_service.update_task(
        task_id, username, title, description, status, priority,
    )

    return {}


@app.post('/tasks/delete/{task_id}')
async def delete_task(request: fastapi.Request, task_id: str):
    username = request.state.username

    if username is None:
        raise PermissionError('unauthenticated')
    
    task_service: services.TaskService = app.state.task_service

    await task_service.delete_task(task_id, username)

    return {}
