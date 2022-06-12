FROM python:3.9-slim

WORKDIR /opt/classifier

COPY requirements.txt .

RUN apt-get update && \
  apt-get install ffmpeg libsm6 libxext6 --no-install-recommends -y && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/* && \
  pip install -r requirements.txt && \
  rm requirements.txt

COPY src src

ENTRYPOINT ["uvicorn", "--host", "0.0.0.0", "src.api:app"]
