# pull official base image
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

# cache tensorflow (400 MB)
#RUN pip install tensorflow

COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY ./src /app