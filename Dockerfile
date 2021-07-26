FROM python:3.8-slim-buster

WORKDIR /app

COPY app/requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt

COPY app/ /app/

# Run the executable
CMD ["python", "/app/circleci_approver.py"]
