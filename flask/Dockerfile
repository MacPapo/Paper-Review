FROM python:3.10-slim

RUN useradd moonphase
WORKDIR /home/moonphase/paper_review

COPY requirements.txt .

RUN python3 -m venv venv
RUN pip install -r requirements.txt
# RUN pip install gunicorn

COPY app app
COPY migrations migrations
COPY uploads uploads
COPY paper_review.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP paper_review.py
ENV FLASK_ENV development
ENV FLASK_DEBUG 1
ENV FLASK_RUN_HOST 0.0.0.0

RUN chown -R moonphase:moonphase ./
USER moonphase

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
