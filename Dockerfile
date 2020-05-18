FROM balenalib/raspberry-pi-debian-python:3-buster

VOLUME /config-file

WORKDIR /app

COPY requirements.txt garagepi ./

RUN apt update && \
    apt install -y gcc make libevent-dev python3-dev
RUN pip3 install -r requirements.txt

CMD ["python3", "-m", "garagepi", "-c", "/config-file"]
