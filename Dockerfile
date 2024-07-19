FROM python:3.11-bookworm as requirements

WORKDIR /tmp

RUN pip install poetry

COPY ./pyproject.toml ./poetry.lock* /tmp/

# RUN poetry self add poetry-plugin-export 

RUN poetry export -f requirements.txt --output requirements.txt

FROM python:3.11-bookworm as builder

WORKDIR /app
COPY --from=requirements /tmp/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app

CMD ["fastapi", "run", "chatbot"]
