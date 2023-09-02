FROM python:3.11.4-slim

WORKDIR /usr/src

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y libpq-dev gcc

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .