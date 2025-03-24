#!/usr/bin/env python3

import uuid
import datetime

import utils
import models
import database


class InvalidCredentialsError(Exception):
    pass


class NotFoundError(Exception):
    pass


class UserService:
    def __init__(self, db: database.Database) -> None:
        self.db = db

    async def register(self, username: str, password: str) -> models.User:
        if len(username) == 0:
            raise ValueError('username is empty')
        
        if len(password) == 0:
            raise ValueError('password is empty')

        user = models.User(username, utils.hash_password(password))

        await self.db.create_user(user)

        return user
    
    async def login(self, username: str, password: str) -> models.User:
        if len(username) == 0:
            raise ValueError('username is empty')
        
        if len(password) == 0:
            raise ValueError('password is empty')

        user = await self.db.find_user_by_username(username)

        if user is None or utils.hash_password(password) != user.hashed_password:
            raise InvalidCredentialsError(f'invalid credentials')

        return user


class TaskService:
    def __init__(self, db: database.Database) -> None:
        self.db = db
        self.cache = set()

    async def create_task(
            self,
            owner: str,
            title: str,
            description: str,
            status: models.TaskStatus,
            priority: int,
    ) -> models.Task:
        id = str(uuid.uuid4())
        created = datetime.datetime.now()
        updated = created

        task = models.Task(
            id,
            owner,
            title,
            description,
            status,
            priority,
            created,
            updated,
        )

        await self.db.create_task(task)

        return task
    
    async def get_task(self, id: str, username: str) -> models.Task:
        task = await self.db.find_task_by_id(id)

        if task is None or task.owner != username:
            raise NotFoundError(f'task {id} not found')

        return task
    
    async def list_tasks(self, username: str, count: int = None) -> list[models.Task]:
        # к сожалению фильтрация происходит в питоне, а не в базе

        if count is not None and count < 0:
            raise ValueError('count is negative')

        tasks = await self.db.find_tasks_by_owner(username)

        tasks.sort(
            key = lambda task: task.priority,
            reverse = True,
        )

        if count is not None:
            tasks = tasks[:count]

        return tasks
    
    async def search_tasks(self, username: str, text: str) -> list[models.Task]:
        # к сожалению поиск тоже происходит в питоне, а не в базе

        if len(text) == 0:
            raise ValueError('text is empty')

        tasks = await self.db.find_tasks_by_owner(username)
        filtered = []

        for task in tasks:
            if text in task.title or text in task.description:
                filtered.append(task)

        return filtered
    
    async def update_task(
            self,
            id: str,
            username: str,
            title: str = None,
            description: str = None,
            status: models.TaskStatus = None,
            priority: int = None,
    ) -> None:
        # тут возможна гонка но что поделать...

        task = await self.db.find_task_by_id(id)

        if task is None or task.owner != username:
            raise NotFoundError(f'task {id} not found')
        
        if title is not None:
            task.title = title

        if description is not None:
            task.description = description

        if status is not None:
            task.status = status

        if priority is not None:
            task.priority = priority

        task.updated_at = datetime.datetime.now()

        await self.db.update_task_by_id(id, task)

    async def delete_task(self, id: str, username: str) -> None:
        # тут возможна гонка но что поделать...
        # обратите внимание что здесь присутствует кэширование

        cache_key = (id, username)

        if cache_key in self.cache:
            return
        
        task = await self.db.find_task_by_id(id)

        if task is None or task.owner != username:
            return
        
        await self.db.delete_task_by_id(id)

        self.cache.add(cache_key)
