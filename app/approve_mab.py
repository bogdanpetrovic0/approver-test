from apscheduler.schedulers.blocking import BlockingScheduler

from app.circleci_approver import CircleciApproverMABDeploy
from app.circleci_approver import CircleciApproverMABRTA

def main() -> None:
    scheduler = BlockingScheduler()
    approver_mab_deploy = CircleciApproverMABDeploy()
    approver_mab_rta = CircleciApproverMABRTA()
    scheduler.add_job(approver_mab_deploy.fetch_and_approve_jobs, 'cron', hour='8', minute='30', timezone='Europe/Ljubljana')
    scheduler.add_job(approver_mab_rta.fetch_and_approve_jobs, 'cron', hour='13', timezone='Europe/Ljubljana')
    scheduler.start()

if __name__ == "__main__":
    main()
