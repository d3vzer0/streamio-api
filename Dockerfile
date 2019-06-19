FROM python:3.7

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ARG FLASK_PORT=5000
ENV FLASK_PORT="${FLASK_PORT}"

ARG FLASK_SECRET=replace_this_example_first_tho
ENV FLASK_SECRET="${FLASK_SECRET}"

ARG JWT_SECRET_KEY=y08_should_also_r3place_this
ENV JWT_SECRET_KEY="${JWT_SECRET_KEY}"

ARG MONGO_DB=phishyme
ENV MONGO_DB="${MONGO_DB}"

ARG MONGO_IP=mongodb
ENV MONGO_IP="${MONGO_IP}"

ARG MONGO_PORT=27017
ENV MONGO_PORT="${MONGO_PORT}"

ARG MONGO_AUTH=admin
ENV MONGO_AUTH="${MONGO_AUTH}"

WORKDIR phishyme-api
COPY . /phishyme-api
ENTRYPOINT ["python", "./run.py"]
