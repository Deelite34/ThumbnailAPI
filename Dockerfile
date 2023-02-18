FROM python:3

ENV PYTHONDONTWRITEBYTECODE 1 \
    PYTHONUNBUFFERED 1

WORKDIR /code/

COPY requirements.txt .

RUN apt-get -qq update && \
    pip install --upgrade pip \
    pip install -r requirements.txt

COPY . .

CMD gunicorn ThumbnailAPI.wsgi:application --workers=4 --bind 0.0.0.0:8000




