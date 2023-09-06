FROM python:latest

WORKDIR /phys_bot
COPY . .

RUN pip3 install -r requirements.txt