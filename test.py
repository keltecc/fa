#!/usr/bin/env python3

import os
import secrets

import requests


IP = os.getenv('IP', '0.0.0.0')
PORT = os.getenv('PORT', '8000')


class Client:
    def __init__(self) -> None:
        self.session = requests.Session()

    def register(self, username: str, password: str) -> None:
        url = f'http://{IP}:{PORT}/users/register'

        response = self.session.post(
            url,
            json = {
                'username': username,
                'password': password,
            },
        )
        response.raise_for_status()

    def login(self, username: str, password: str) -> None:
        url = f'http://{IP}:{PORT}/users/login'

        response = self.session.post(
            url,
            json = {
                'username': username,
                'password': password,
            },
        )
        response.raise_for_status()

    def create_task(
            self, title: str, description: str, status: str, priority: int,
    ) -> str:
        url = f'http://{IP}:{PORT}/tasks/create'

        response = self.session.post(
            url,
            json = {
                'title': title,
                'description': description,
                'status': status,
                'priority': priority,
            },
        )

        obj = response.json()

        if 'error' in obj:
            raise Exception(obj['error'])

        task_id = obj['task_id']

        return task_id
    
    def get_task(self, task_id: str) -> dict:
        url = f'http://{IP}:{PORT}/tasks/get/{task_id}'

        response = self.session.get(url)

        obj = response.json()

        if 'error' in obj:
            raise Exception(obj['error'])

        task = obj['task']

        return task
    
    def update_task(
            self, task_id: str, title: str, description: str, status: str, priority: int,
    ) -> dict:
        url = f'http://{IP}:{PORT}/tasks/update/{task_id}'

        response = self.session.post(
            url,
            json = {
                'title': title,
                'description': description,
                'status': status,
                'priority': priority,
            },
        )
        
        obj = response.json()

        if 'error' in obj:
            raise Exception(obj['error'])
    
    def delete_task(self, task_id: str) -> None:
        url = f'http://{IP}:{PORT}/tasks/delete/{task_id}'

        response = self.session.post(url)

        obj = response.json()

        if 'error' in obj:
            raise Exception(obj['error'])

    def list_tasks(self, count: int = None) -> list[dict]:
        url = f'http://{IP}:{PORT}/tasks/list'

        response = self.session.get(
            url,
            params = {
                'count': count,
            },
        )

        obj = response.json()

        if 'error' in obj:
            raise Exception(obj['error'])

        tasks = obj['tasks']

        return tasks
    
    def search_tasks(self, text: str) -> list[dict]:
        url = f'http://{IP}:{PORT}/tasks/search'

        response = self.session.get(
            url,
            params = {
                'text': text,
            },
        )

        obj = response.json()

        if 'error' in obj:
            raise Exception(obj['error'])

        tasks = obj['tasks']

        return tasks


def test_CRUD() -> None:
    print('=== testing CRUD ===')

    username = secrets.token_hex(8)
    password = secrets.token_hex(8)

    client = Client()
    client.register(username, password)
    client.login(username, password)

    # CREATE

    task_id = client.create_task('title1', 'description1', 'Waiting', 1)
    print(f'- created task:')
    print(task_id)

    # READ

    task = client.get_task(task_id)
    print(f'- read task:')
    print(task)

    # UPDATE

    client.update_task(task_id, 'title2', 'description2', 'InProgress', 2)

    updated = client.get_task(task_id)
    print(f'- updated task:')
    print(updated)

    # DELETE

    client.delete_task(task_id)

    try:
        client.get_task(task_id)
    except Exception as e:
        print(f'- failed to delete:')
        print(str(e))


def test_listing() -> None:
    print('=== testing listing ===')

    username = secrets.token_hex(8)
    password = secrets.token_hex(8)

    client = Client()
    client.register(username, password)
    client.login(username, password)

    # create some tasks

    client.create_task('title1', 'description1', 'InProgress', 1)
    client.create_task('title3', 'description3', 'InProgress', 3)
    client.create_task('title2', 'description2', 'InProgress', 2)

    # list all without filter
    # note that tasks are sorted by priority

    tasks1 = client.list_tasks()
    print(f'- list all:')
    print(tasks1)

    # list only top-2 tasks sorted by priority

    tasks2 = client.list_tasks(2)
    print(f'- list top-2:')
    print(tasks2)


def test_searching() -> None:
    print('=== testing searching ===')

    username = secrets.token_hex(8)
    password = secrets.token_hex(8)

    client = Client()
    client.register(username, password)
    client.login(username, password)

    # create some tasks

    client.create_task('x_aaa_x', 'x_bbb_x', 'Done', 1)
    client.create_task('x_bbb_x', 'x_ccc_x', 'Done', 2)
    client.create_task('x_aaa_x', 'x_ccc_x', 'Done', 3)

    # search by 'bbb'

    tasks = client.search_tasks('bbb')
    print(f'- search by bbb')
    print(tasks)


def test_users() -> None:
    print('=== testing users ===')

    username1 = secrets.token_hex(8)
    password1 = secrets.token_hex(8)

    client1 = Client()
    client1.register(username1, password1)
    client1.login(username1, password1)

    # create task

    task_id = client1.create_task('x', 'y', 'Waiting', 1)
    print(f'- created task:')
    print(task_id)

    # failed to access unauthenticated

    client2 = Client()

    try:
        client2.get_task(task_id)
    except Exception as e:
        print(f'- failed to get:')
        print(str(e))

    # failed to access from another user

    username3 = secrets.token_hex(8)
    password3 = secrets.token_hex(8)

    client3 = Client()
    client3.register(username3, password3)
    client3.login(username3, password3)

    try:
        client3.get_task(task_id)
    except Exception as e:
        print(f'- failed to get:')
        print(str(e))


def main() -> None:
    test_CRUD()
    test_listing()
    test_searching()
    test_users()


if __name__ == '__main__':
    main()
