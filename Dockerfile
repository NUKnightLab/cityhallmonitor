FROM python:3.5
WORKDIR /usr/src/app
COPY . .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN ./env.sh
EXPOSE 8000
# RUN gunicorn --workers 1 --bind unix:/usr/src/app/django.sock core.wsgi:application
