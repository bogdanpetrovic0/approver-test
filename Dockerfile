FROM python:3.9-slim-buster AS base

WORKDIR /app

COPY app/requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt

COPY app/ /app/

ENV PYTHONUNBUFFERED=1
ENV LANG=en_US.UTF-8

# Run the executable
FROM base as circleci-job-approver-uab
CMD ["python", "/app/approve_uab.py"]

FROM base as circleci-job-approver-mab
CMD ["python", "/app/approve_mab.py"]
