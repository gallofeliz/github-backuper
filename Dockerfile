FROM python:3.8-alpine3.12

RUN apk add --no-cache git

RUN pip install github-backup git+https://github.com/gallofeliz/python-gallocloud-utils

VOLUME /backup

WORKDIR /app

ADD app.py .

CMD python -u ./app.py -
