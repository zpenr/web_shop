FROM python:3.12-alpine
WORKDIR /project
COPY pyproject.toml .
RUN pip install -e .
COPY . .