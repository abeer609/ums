FROM python:3
WORKDIR /app
RUN apt-get update
RUN apt-get install python3-dev default-libmysqlclient-dev build-essential pkg-config -y

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY . .


EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000" ]