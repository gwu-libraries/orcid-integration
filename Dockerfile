FROM python:3.9-slim

WORKDIR /opt/orcid_integration

RUN apt-get update && apt-get install -y
RUN apt-get install -y libxml2-dev libxmlsec1-dev libxmlsec1-openssl build-essential pkg-config 

COPY *.py ./
COPY requirements.txt .
COPY migrations ./migrations
COPY orcidflask/*.py ./orcidflask/
COPY orcidflask/templates ./orcidflask/templates/

RUN pip install -r requirements.txt

ENV FLASK_APP=orcidflask
ENV ORCIDFLASK_SETTINGS=/opt/orcid_integration/config.py

CMD [ "gunicorn", "-b", "0.0.0.0:8080", "orcidflask:app" ]