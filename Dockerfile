FROM python:3.5
WORKDIR /usr/src/app
RUN mkdir -p /home/apps/log/cityhallmonitor
COPY . .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 8000
# RUN gunicorn --workers 1 --bind unix:/usr/src/app/django.sock core.wsgi:application
