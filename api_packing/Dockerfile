# Use an official Python runtime as the parent image
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

# Set the working directory in the container to /app
WORKDIR /app

COPY . /app/

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install -r /app/requirements.txt
RUN pip install -e pip install git+https://github.com/SWMSConsulting/PackingUtils.git@stage

EXPOSE 8000


# ENV DEFAULT_SELECT_STRATEGY="OPTIONAL item select strategies"
# ENV NEW_LAYER_SELECT_STRATEGY="OPTIONAL item select strategies"
# ENV DIRECTION_CHANGE_VOLUMES="OPTIONAL proportion of direction change volumes"
# ENV ALLOW_ITEM_EXCEEDS_LAYER="OPTIONAL bool(s) to allow item exceeds layer"
# ENV MIRROR_WALLS="OPTIONAL bool(s) to mirror walls"
# ENV BIN_STABILITY_FACTOR="OPTIONAL bin stability factor(s)"
# ENV NUM_VARIANTS="OPTIONAL number of variants"


CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
