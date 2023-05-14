FROM python:3.11.1-buster
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ENV PIP_ROOT_USER_ACTION=ignore
RUN pip install --upgrade pip
ADD requirements.txt /code/
RUN pip install -r requirements.txt
