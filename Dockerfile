# BUILDER #
###########

FROM python:3.8.0-alpine as builder

ENV BUILD_DIR /usr/src/app
WORKDIR $BUILD_DIR

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

# lint
RUN pip install --upgrade pip
RUN pip install flake8
RUN flake8 --ignore=E501,F401 .

# install dependencies
COPY ./requirements/common.txt ./requirements.txt
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt


#########
# FINAL #
#########
FROM python:3.8.0-alpine

ENV HOME=/home/app
ENV APP_HOME=$HOME/web
ENV BUILD_DIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p $HOME
RUN addgroup -S app && adduser -S app -G app

RUN mkdir -p $APP_HOME
RUN mkdir -p $APP_HOME/files/static
RUN mkdir -p $APP_HOME/files/media
RUN mkdir -p $APP_HOME/logs
WORKDIR $APP_HOME

# install dependencies
RUN apk update && apk add libpq
COPY --from=builder $BUILD_DIR/wheels /wheels
COPY --from=builder $BUILD_DIR/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache /wheels/*

# copy project
COPY ./hookah_crm $APP_HOME/hookah_crm
COPY ./src $APP_HOME/src
COPY ./templates $APP_HOME/templates
COPY ./manage.py $APP_HOME/

# copy entrypoint.sh
COPY ./entrypoint.sh $APP_HOME

RUN chown -R app:app $APP_HOME
USER app

ENTRYPOINT ["sh", "/home/app/web/entrypoint.sh"]