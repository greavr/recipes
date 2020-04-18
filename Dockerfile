FROM python

MAINTAINER Rick Greaves "rgreaves@google.com"

RUN apt-get update -y
RUN apt-get install -y python-pip python-dev

COPY /code /app

WORKDIR /app
RUN pip3 install -r requirements.txt

EXPOSE 8080

CMD ["python3", "main.py"]