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

ARG DBHOST=mongodb
ENV DBHOST="${DBHOST}"

ARG FAUST_HOST=http://wordmatching:6066
ENV FAUST_HOST="${FAUST_HOST}"

ARG SCRAPER_AGENT=http://scraper:6066
ENV SCRAPER_AGENT="${SCRAPER_AGENT}"

ARG DBPORT=27017
ENV DBPORT="${DBPORT}"

ARG APIHOST=0.0.0.0
ENV APIHOST="${APIHOST}"

ARG MONGO_AUTH=admin
ENV MONGO_AUTH="${MONGO_AUTH}"

WORKDIR phishyme-api
COPY . /phishyme-api
ENTRYPOINT ["python", "./run.py"]
