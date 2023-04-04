FROM python:3.10-bullseye
LABEL maintainer="sigae@protonmail.com"
COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt
ENTRYPOINT ["python", "main.py"]