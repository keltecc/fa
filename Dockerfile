FROM python:3.10

WORKDIR /tmp/app

COPY src/requirements.txt .

RUN pip install -r requirements.txt

COPY src /tmp/app

CMD ["uvicorn", "--host", "0.0.0.0", "app:app"]
