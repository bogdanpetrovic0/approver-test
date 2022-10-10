import os
import sys
import time
import requests
import json

from apscheduler.schedulers.blocking import BlockingScheduler
from typing import List, Dict, Any

class CircleciApprover:

    def __init__(self) -> None:
        self._circle_token = os.environ['CIRCLE_TOKEN']
        self._circle_project = os.environ['CIRCLE_PROJECT']
        self._circle_branch = os.environ['CIRCLE_BRANCH']
        self._circle_workflow = os.environ['CIRCLE_WORKFLOW']
        self._circle_approval_job = os.environ['CIRCLE_APPROVAL_JOB']
        self._merger_name = os.getenv('MERGER_NAME')
        self._job_dependency = os.getenv('JOB_DEPENDENCY')

        self._circle_base_url = 'https://circleci.com/api/v2'
        self._circle_auth = (self._circle_token, '')


    def _get_pipelines(self) -> List[Dict[str, Any]]:
        pipelines_params = {'branch': self._circle_branch}
        pipelines_url = f'{self._circle_base_url}/project/{self._circle_project}/pipeline'
        pipelines_response = requests.get(pipelines_url, params=pipelines_params, auth=self._circle_auth).json()
        assert hasattr(pipelines_response, 'items'), f'Error fetching master pipelines from {pipelines_url}, received:\n{pipelines_response}'
        return [p for p in pipelines_response['items'] if self._merger_name is None or p['trigger']['actor']['login'] == self._merger_name]

    def _get_worklows_for_pipeline(self, pipeline: Dict[str, Any]) -> List[str]:
        workflows_url = f'{self._circle_base_url}/pipeline/{pipeline["id"]}/workflow'
        workflows_response = requests.get(workflows_url, auth=self._circle_auth).json()
        assert hasattr(workflows_response, 'items'), f'Error fetching workflows from {workflows_url}, received:\n{workflows_response}'
        workflow_ids = [workflow['id'] for workflow in workflows_response['items'] if workflow['name'] == self._circle_workflow]
        return workflow_ids

    def _approve_workflow_job(self, workflow_id: str) -> None:
        jobs_url = f'{self._circle_base_url}/workflow/{workflow_id}/job'
        jobs_response = requests.get(jobs_url, auth=self._circle_auth).json()
        assert hasattr(jobs_response, 'items'), f'Error fetching workflows from {workflows_url}, received:\n{jobs_response}'

        # Don't do anything if job dependency is not finished yet - causes broken authorization on circleci - temp solution, hopefully cirlce will fix this
        if self._job_dependency is not None and not [job for job in jobs_response['items'] if job['name'] == self._job_dependency and job['status'] == 'success']:
            return

        approval_id = [job['approval_request_id'] for job in jobs_response['items'] if job['name'] == self._circle_approval_job][0]

        # Latest request deploy found - approve it - does nothing if already approved
        approval_url = f"{self._circle_base_url}/workflow/{workflow_id}/approve/{approval_id}"
        approval_response = requests.post(approval_url, auth=self._circle_auth)
        aproval_response_text = approval_response.json()
        if approval_response.status_code == 202:
            return

        if approval_response.status_code != 400 or aproval_response_text['message'] != 'Job already approved.':
            raise Exception(f'Unsuccessful approval, status code: {approval_response.status_code}, message:\n{aproval_response_text}')

    # Since we deploy regularly, the latest unapproved workflow should be found on the first pipeline page, earlier should be approved already
    def fetch_and_approve_jobs(self) -> None:
        print('Running fetch_and_approve_jobs...')

        pipelines = self._get_pipelines()
        for pipeline in pipelines:
            workflow_ids = self._get_worklows_for_pipeline(pipeline)

            if len(workflow_ids) == 1:
                self._approve_workflow_job(workflow_ids[0])
                break
            elif len(workflow_ids) > 1:
                print(f'Multiple workflows found for pipeline {pipeline}, most likely a rerun, skipping. workflows: {workflow_ids}')
                break


def main() -> None:
    sched = BlockingScheduler()
    approver = CircleciApprover()
    sched.add_job(approver.fetch_and_approve_jobs, 'cron', hour='9,13,16', timezone='Europe/Ljubljana')
    sched.start()

if __name__ == "__main__":
    main()
