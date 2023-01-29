from apscheduler.schedulers.blocking import BlockingScheduler

from app.circleci_approver import CircleciApproverUAB

def main() -> None:
    scheduler = BlockingScheduler()
    approver_uab = CircleciApproverUAB()
    scheduler.add_job(approver_uab.fetch_and_approve_jobs, 'cron', hour='9,13,16', timezone='Europe/Ljubljana')
    scheduler.start()

if __name__ == "__main__":
    main()
