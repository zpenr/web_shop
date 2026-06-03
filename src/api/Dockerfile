FROM python:3.12-alpine
WORKDIR /project
ENV PYTHONPATH=/project/src
COPY . .
RUN pip install -e .
CMD ["uvicorn", "api.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
