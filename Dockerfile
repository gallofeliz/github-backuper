FROM python:alpine

RUN pip install croniter github-backup

RUN apk add --no-cache git

VOLUME /backup

WORKDIR /app

ADD app.py .

CMD python -u ./app.py -
