FROM python:3.6-slim
WORKDIR /app
ADD . /app
RUN mkdir -p /app/crawler/screenshots
RUN pip install -r requirements.txt
ENTRYPOINT [ "bash" ]