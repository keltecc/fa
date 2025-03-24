#!/usr/bin/env python3

import psycopg

import models


class UserAlreadyExistsError(Exception):
    pass


class Database:
    def __init__(self, conn: psycopg.AsyncConnection) -> None:
        self.conn = conn

    @staticmethod
    async def connect(database_uri: str) -> 'Database':
        conn = await psycopg.AsyncConnection.connect(
            database_uri,
            autocommit = True,
        )

        return Database(conn)
    
    async def create_user(self, user: models.User) -> None:
        sql = '''
        INSERT INTO
            users (username, hashed_password)
        VALUES
            (%s, %s)
        '''

        cursor = self.conn.cursor()

        try:
            values = (
                user.username,
                user.hashed_password,
            )
            await cursor.execute(sql, values)
        except psycopg.errors.UniqueViolation:
            raise UserAlreadyExistsError(f'user {user.username} already exists')

    async def find_user_by_username(self, username: str) -> models.User | None:
        sql = '''
        SELECT
            username, hashed_password
        FROM
            users
        WHERE
            username = %s
        '''

        cursor = self.conn.cursor()
        await cursor.execute(sql, (username,))

        row = await cursor.fetchone()

        if row is None:
            return None

        username, hashed_password = row

        return models.User(username, hashed_password)

    async def create_task(self, task: models.Task) -> None:
        sql = '''
        INSERT INTO
            tasks (id, owner, title, description, status, priority, created_at, updated_at)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s)
        '''

        cursor = self.conn.cursor()

        values = (
            task.id,
            task.owner,
            task.title,
            task.description,
            task.status,
            task.priority,
            task.created_at,
            task.updated_at,
        )
        await cursor.execute(sql, values)

    async def find_task_by_id(self, id: str) -> models.Task | None:
        sql = '''
        SELECT
            id, owner, title, description, status, priority, created_at, updated_at
        FROM
            tasks
        WHERE
            id = %s
        '''

        cursor = self.conn.cursor()
        await cursor.execute(sql, (id,))

        row = await cursor.fetchone()

        if row is None:
            return None
        
        id, owner, title, description, status, priority, created_at, updated_at = row
        
        return models.Task(
            id,
            owner,
            title,
            description,
            status,
            priority,
            created_at,
            updated_at,
        )

    async def find_tasks_by_owner(self, owner: str) -> list[models.Task]:
        sql = '''
        SELECT
            id, owner, title, description, status, priority, created_at, updated_at
        FROM
            tasks
        WHERE
            owner = %s
        '''

        cursor = self.conn.cursor()
        await cursor.execute(sql, (owner,))

        rows = await cursor.fetchall()
        tasks = []

        for row in rows:
            id, owner, title, description, status, priority, created_at, updated_at = row
            task = models.Task(
                id,
                owner,
                title,
                description,
                status,
                priority,
                created_at,
                updated_at,
            )
            tasks.append(task)

        return tasks
    
    async def update_task_by_id(self, id: str, task: models.Task) -> None:
        sql = '''
        UPDATE
            tasks
        SET
            owner = %s,
            title = %s,
            description = %s,
            status = %s,
            priority = %s,
            created_at = %s,
            updated_at = %s
        WHERE
            id = %s
        '''

        cursor = self.conn.cursor()

        values = (
            task.owner,
            task.title,
            task.description,
            task.status,
            task.priority,
            task.created_at,
            task.updated_at,
            id,
        )
        await cursor.execute(sql, values)

    async def delete_task_by_id(self, id: str) -> None:
        sql = '''
        DELETE FROM
            tasks
        WHERE
            id = %s
        '''

        cursor = self.conn.cursor()
        await cursor.execute(sql, (id,))
