FROM phusion/baseimage:latest
RUN apt-get update -y && apt-get install -y \
    python \
    python-pip \
    python-dev \
    ntp \
    build-essential \
COPY . /app
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install certstream
ENV FLASK_APP app.py
CMD [ "python", "app.py"]

