FROM python:3.10

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

EXPOSE 5000

WORKDIR /app

RUN pip install flask flask_cors flask_mail bcrypt psycopg2

COPY . .

CMD ["flask", "run"]
