This is CircleCI job approver, inteded to approve jobs with special contexts and needed credentials from a save and limited environment.

Prepare
create .env file from .env.SAMPLE

Run locally and debug
docker-compose up -d circleci-job-approver
docker exec -it circleci-job-approver /bin/bash
python /app/circleci_approver_test.py

Deploy
Deploy to heroku celtra/circleci-job-approver is automatic on push to master.

Monitor
Heroku cli: heroku logs -t -a circleci-job-approver
