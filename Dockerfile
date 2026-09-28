FROM python:3.12-slim

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=hello.py

EXPOSE 5000

CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]
