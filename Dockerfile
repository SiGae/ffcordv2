FROM python:3.8
LABEL maintainer="sigae@protonmail.com"
COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt
ENTRYPOINT ["python", "main.py"]