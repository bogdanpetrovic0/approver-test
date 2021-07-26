from circleci_approver import CircleciApprover

if __name__ == "__main__":
    approver = CircleciApprover()
    approver.fetch_and_approve_jobs()
