# Use an official Python runtime as the parent image
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY api.py /app/api.py

# Install any needed packages specified in requirements.txt
RUN pip install numpy pillow matplotlib
RUN pip install --no-cache-dir fastapi uvicorn

RUN pip install -e git+https://github.com/ArnoSchiller/PackingUtils.git#egg=packutils --ignore-installed 
RUN pip install git+https://github.com/ArnoSchiller/palletier.git#egg=palletier

# Make port 80 available to the world outside this container
EXPOSE 8000

# Define environment variable for uvicorn to run on port 8000
ENV UVICORN_HOST=0.0.0.0 UVICORN_PORT=8000

# Run main.py using uvicorn when the container launches
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
