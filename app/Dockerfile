FROM python:slim

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

ENV FLASK_APP app.py
ENV FLASK_DEBUG 1
ENV FLASK_RUN_PORT 5000
ENV FLASK_RUN_HOST 0.0.0.0

EXPOSE 5000

CMD [ "flask", "run" ]
