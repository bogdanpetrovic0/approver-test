FROM python:3.9-slim-buster

WORKDIR /app

COPY app/requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt

COPY app/ /app/

ENV PYTHONUNBUFFERED=1
ENV LANG=en_US.UTF-8

# Run the executable
CMD ["python", "/app/circleci_approver.py"]
