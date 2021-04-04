from github_backup.github_backup import (
    backup_account,
    backup_repositories,
    filter_repositories,
    get_authenticated_user,
    parse_args,
    retrieve_repositories
)

from gallocloud_utils.scheduling import schedule
from gallocloud_utils.jsonlogging import configure_logger
from gallocloud_utils.config import load_config_from_env
from datetime import datetime

config = load_config_from_env()
logger = configure_logger(config.get('log', {}).get('level', 'info'))

def backup():
    logger.info('Starting backup', extra={'status': 'starting'})
    try:
        args = parse_args()
        args.token = config['github']['token']
        args.user = config['github']['user']
        args.output_directory = '/backup'
        args.include_repository = True
        args.private = True
        args.fork = True
        args.bare_clone = True
        authenticated_user = get_authenticated_user(args)
        repositories = retrieve_repositories(args, authenticated_user)
        repositories = filter_repositories(args, repositories)
        backup_repositories(args, args.output_directory, repositories)
        backup_account(args, args.output_directory)
        logger.info('Backup succeeded', extra={'status': 'success'})
    except Exception as e:
        logger.exception('Backup failed', extra={'status': 'failure'})


schedule(config['schedule'], backup, runAtBegin=True)
