import os
import sys
import time
import requests
import json


from typing import List, Dict, Any

sleep_seconds = 60


class CircleciApprover:

    def __init__(self, jiraApiEmail: str, jiraApiToken: str) -> None:
        self.circle_token = os.environ['CIRCLE_TOKEN']
        self.circle_project = os.environ['CIRCLE_PROJECT']
        self.circle_branch = os.environ['CIRCLE_BRANCH']
        self.circle_workflow = os.environ['CIRCLE_WORKFLOW']
        self.circle_approval_job = os.environ['CIRCLE_APPROVAL_JOB']
        self.merger_name = os.getenv('MERGER_NAME')

        self.circle_base_url = 'https://circleci.com/api/v2'
        self.circle_auth = (self.circle_token, '')


    def get_pipelines(self) -> List[Dict[str, Any]]:
        pipelines_params = {'branch': self.circle_branch}
        pipelines_url = f'{self.circle_base_url}/project/{self.circle_project}/pipeline'
        pipelines_response = requests.get(pipelines_url, params=pipelines_params, auth=self.circle_auth).json()
        assert hasattr(pipelines_response, 'items'), f'Error fetching master pipelines from {pipelines_url}, received:\n{pipelines_response}'
        return [p for p in pipelines_response['items'] if self.merger_name is None or p['trigger']['actor']['login'] == self.merger_name]

    def get_worklows_for_pipeline(self, pipeline: Dict[str, Any]) -> List[str]:
        workflows_url = f'{self.circle_base_url}/pipeline/{pipeline["id"]}/workflow'
        workflows_response = requests.get(workflows_url, auth=self.circle_auth).json()
        assert hasattr(workflows_response, 'items'), f'Error fetching workflows from {workflows_url}, received:\n{workflows_response}'
        workflow_ids = [workflow['id'] for workflow in workflows_response['items'] if workflow['name'] == self.circle_workflow]
        assert len(workflow_ids) < 2, f'Multiple workflows found for pipeline {pipeline}, workflows: {workflow_ids}'
        return workflow_ids

    def approve_workflow_job(self, workflow_id):
        jobs_url = f'{self.circle_base_url}/workflow/{workflow_id}/job'
        jobs_response = requests.get(jobs_url, auth=self.circle_auth).json()
        assert hasattr(jobs_response, 'items'), f'Error fetching workflows from {workflows_url}, received:\n{jobs_response}'
        approval_id = [job['approval_request_id'] for job in jobs_response['items'] if job['name'] == self.circle_approval_job][0]

        # Latest request deploy found - approve it - does nothing if already approved
        approval_url = f"{self.circle_base_url}/workflow/{workflow_id}/approve/{approval_id}"
        approval_response = requests.post(approval_url, auth=self.circle_auth)
        aproval_response_text = approval_response.json()
        if approval_response.status_code == 202:
            return

        if approval_response.status_code != 400 or aproval_response_text['message'] != 'Job already approved.':
            raise Exception(f'Unsuccessful approval, status code: {approval_response.status_code}, message:\n{aproval_response_text}')

    # Since we deploy regularly, the latest unapproved workflow should be found on the first pipeline page, earlier should be approved already
    def fetch_and_approve_jobs() -> None:
        print('Running fetch_and_approve_jobs...')

        pipelines = self.get_pipelines()
        for pipeline in pipelines:
            workflow_ids = self.get_worklows_for_pipeline(pipeline)

            if workflow_ids:
                self.approve_workflow_job(workflow_ids[0])
                break


def main() -> None:
    approver = CircleciApprover()

    while True:
        approver.fetch_and_approve_jobs()

        print(f"Completed, sleeping {sleep_seconds}")
        time.sleep(sleep_seconds)


if __name__ == "__main__":
    main()
