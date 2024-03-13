# Use an official Python runtime as the parent image
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

# Set the working directory in the container to /app
WORKDIR /app

COPY . /app/

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install -r /app/requirements.txt
RUN pip install git+https://github.com/SWMSConsulting/PackingUtils.git@v1.0.8_dev

EXPOSE 8000

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
