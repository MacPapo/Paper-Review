FROM python:3.10-slim

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
RUN useradd moonphase
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /home/moonphase

COPY requirements.txt .
RUN pip install -r requirements.txt
# RUN pip install gunicorn
#RUN pip uninstall -y requests_toolbelt && pip install requests_toolbelt==0.9.1

COPY app app
COPY migrations migrations
COPY uploads uploads
COPY project0.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP project0.py
ENV FLASK_ENV development
ENV FLASK_DEBUG 1
ENV FLASK_RUN_HOST 0.0.0.0

RUN chown -R moonphase:moonphase ./
USER moonphase

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
