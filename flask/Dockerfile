FROM python:slim

WORKDIR /app

COPY ./app .
COPY ./migrations .
COPY ./entrypoint.sh .
COPY ./project0.py .
COPY ./requirements.txt .

RUN pip install -r requirements.txt

ENV FLASK_APP project0.py
ENV FLASK_DEBUG 1
ENV FLASK_RUN_PORT 5000
ENV FLASK_RUN_HOST 0.0.0.0

EXPOSE 5000

RUN chmod u+x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
