FROM postgres:16.3-alpine AS base
ENV POSTGRES_DB = postgres
ENV POSTGRES_USER = postgres
COPY ./db_init.sql /
COPY ./db_init.sh /docker-entrypoint-initdb.d/