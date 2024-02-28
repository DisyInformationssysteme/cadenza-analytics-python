FROM registry.disy.net/docker-hub-proxy/library/python:3.11.0-slim 

RUN mkdir /service
RUN mkdir /service/logs
COPY ./requirements.txt /service/requirements.txt
COPY ./extension /service/extension
WORKDIR /service

RUN apt-get update && apt-get -y upgrade
RUN pip install -r requirements.txt

CMD ["gunicorn", "-w", "4", "-b", ":8080", "--chdir", "extension", "example_extensions:analytics_service()", "--access-logfile", "../logs/access.log"]
