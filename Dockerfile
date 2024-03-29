FROM python:3.9-alpine

RUN pip install --upgrade pip && pip install \
    flake8 \
    autopep8 \
    requests

RUN apk add --no-cache git

COPY ./app /app
WORKDIR /app

CMD ["python", "-u", "app.py"]
