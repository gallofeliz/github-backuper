from croniter import croniter
import sched, os, time
from github_backup.github_backup import (
    backup_account,
    backup_repositories,
    filter_repositories,
    get_authenticated_user,
    parse_args,
    retrieve_repositories,
    log_warning,
    log_info
)

args = parse_args()
args.token = os.environ['TOKEN']
args.user = os.environ['USER']
args.output_directory = '/backup'
args.include_repository = True
args.private = True
args.fork = True
args.bare_clone = True

schedule = os.environ['SCHEDULE']
scheduler = sched.scheduler(time.time)

def backup():
    scheduler.enterabs(croniter(schedule).get_next(), 1, backup)
    try:
        log_info('Backup start')
        authenticated_user = get_authenticated_user(args)
        repositories = retrieve_repositories(args, authenticated_user)
        repositories = filter_repositories(args, repositories)
        backup_repositories(args, args.output_directory, repositories)
        backup_account(args, args.output_directory)
        log_info('Backup done')
    except Exception as e:
        log_warning('Backup KO')

# github_backup has not a good separation between the logic and the command line
# It can exit() during its job and we want to avoid a "spam" behavior with docker restart policy
log_info('Waiting 10 seconds before starting')
time.sleep(10)
backup()
scheduler.run()
