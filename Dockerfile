FROM python:3.9
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN apt-get update
RUN apt-get -y install build-essential && apt-get -y install apt-utils
RUN pip3 install Cython
RUN pip install -r requirements.txt

COPY . /code/
