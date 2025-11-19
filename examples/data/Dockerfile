FROM python:3.12-slim

RUN mkdir /service
RUN mkdir /service/logs
COPY ./requirements.txt /service/requirements.txt
COPY ./extension /service/extension
WORKDIR /service

RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

CMD ["gunicorn", "-w", "4", "-b", ":8080", "--chdir", "extension", "example_extensions:analytics_service()", "--access-logfile", "../logs/access.log"]
