FROM python:2.7.12
MAINTAINER jiaming


ADD project /project

RUN pip install -r /project/requirement.txt

WORKDIR /project/src

EXPOSE 8080

CMD python main.py

