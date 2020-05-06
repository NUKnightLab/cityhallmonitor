FROM python:3.5
ENV PYTHONUNBUFFERED 1
WORKDIR /usr/src/apps/cityhallmonitor
RUN mkdir -p /home/apps/log/cityhallmonitor
COPY . .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
