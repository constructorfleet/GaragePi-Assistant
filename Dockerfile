FROM balenalib/raspberry-pi-debian-python:3-buster


WORKDIR /app

COPY requirements.txt garagepi ./

RUN apt update && \
    apt install -y gcc make libevent-dev python3-dev \
    libffi-dev
RUN pip3 install -r requirements.txt

CMD ["python3", "-m", "garagepi", "-c", "/config.json"]
