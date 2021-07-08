import os
import sys
import time
import requests
import json

#import re

from typing import List, Dict, Any

circle_token = os.environ['CIRCLE_TOKEN']
circle_project = os.environ['CIRCLE_PROJECT']
circle_branch = os.environ['CIRCLE_BRANCH']
circle_workflow = os.environ['CIRCLE_WORKFLOW']
circle_approval_job = os.environ['CIRCLE_APPROVAL_JOB']
merger_name = os.getenv('MERGER_NAME')

circle_base_url = 'https://circleci.com/api/v2'
circle_auth = (circle_token, '')

sleep_seconds = 60


# Since we deploy regularly, the latest unapproved workflow should be found on the first pipeline page, earlier should be approved already
def fetch_and_approve_jobs() -> None:
    print('Running fetch_and_approve_jobs...')

    # Get pipelines
    pipelines_params = {'branch': circle_branch}
    pipelines_url = f'{circle_base_url}/project/{circle_project}/pipeline'
    pipelines_response = requests.get(pipelines_url, params=pipelines_params, auth=circle_auth).json()
    assert hasattr(pipelines_response, 'items'), f'Error fetching master pipelines from {pipelines_url}, received:\n{pipelines_response}'
    pipelines = [p for p in pipelines_response['items'] if merger_name is None or p['trigger']['actor']['login'] == merger_name]
    for pipeline in pipelines:
        # Get workflows
        workflows_url = f'{circle_base_url}/pipeline/{pipeline["id"]}/workflow'
        workflows_response = requests.get(workflows_url, auth=circle_auth).json()
        assert hasattr(workflows_response, 'items'), f'Error fetching workflows from {workflows_url}, received:\n{workflows_response}'
        workflow_id = [workflow['id'] for workflow in workflows_response['items'] if workflow['name'] == circle_workflow]

        # Get workflow jobs
        if workflow_id:
            jobs_url = f'{circle_base_url}/workflow/{workflow_id[0]}/job'
            jobs_response = requests.get(jobs_url, auth=circle_auth).json()
            assert hasattr(jobs_response, 'items'), f'Error fetching workflows from {workflows_url}, received:\n{jobs_response}'
            approval_id = [job['approval_request_id'] for job in jobs_response['items'] if job['name'] == circle_approval_job][0]

            # Latest request deploy found - approve it - does nothing if already approved
            approval_url = f"{circle_base_url}/workflow/{workflow_id[0]}/approve/{approval_id}"
            approval_response = requests.post(approval_url, auth=circle_auth)
            aproval_response_text = approval_response.json()
            if approval_response.status_code != 202 and (approval_response.status_code != 400 or aproval_response_text['message'] != 'Job already approved.'):
                print(f'Unsuccessful approval, status code: {approval_response.status_code}, message:\n{aproval_response_text}')
                exit(1)
            break


def main() -> None:
    while True:
        fetch_and_approve_jobs()

        print(f"Completed, sleeping {sleep_seconds}")
        time.sleep(sleep_seconds)


if __name__ == "__main__":
    main()
