FROM balenalib/raspberry-pi-debian-python:3-buster


WORKDIR /app

RUN apt update && \
    apt install -y gcc make libevent-dev python3-dev \
    libffi-dev

COPY requirements.txt ./
COPY garagepi/ ./garagepi/
RUN pip3 install -r requirements.txt

CMD ["python3", "garagepi", "-c", "/config.json"]
