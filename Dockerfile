FROM tiangolo/uwsgi-nginx:python2.7

COPY . /app/
WORKDIR /app
COPY pip.conf /root/.pip/
RUN pip install -r requirements.txt \
    && rm -rf /root/.cache/pip/*
RUN python manager.py db upgrade
