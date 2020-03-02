FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
ENV PYTHONPATH ${PYTHONPATH}:/app
COPY ./requirements.txt /app/requirements.txt
COPY ./prestart.sh /app/prestart.sh
RUN pip install -r /app/requirements.txt
COPY ./app /app/app
