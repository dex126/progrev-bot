FROM python:3.13-slim AS build

ENV \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 

WORKDIR /app
COPY . .

RUN pip wheel . -w dist

# ---

FROM python:3.13-slim AS production

ENV \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1

ENV \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 

RUN groupadd -r app && useradd -r app -g app 
USER app

WORKDIR /home/app
COPY --from=build /app/dist/*.whl ./

RUN pip install --user ./*.whl

ENTRYPOINT ["python", "-m", "nutrabot"]