from github_backup.github_backup import (
    backup_account,
    backup_repositories,
    filter_repositories,
    get_authenticated_user,
    parse_args,
    retrieve_repositories
)

from gallocloud_utils.scheduling import schedule_in_thread
from gallocloud_utils.jsonlogging import configure_logger
from gallocloud_utils.config import load_config_from_env
import socketserver, http.server

config = load_config_from_env()
logger = configure_logger(config.get('log', {}).get('level', 'info'))

def backup(raise_on_error=False):
    logger.info('Starting backup', extra={'action': 'backup', 'status': 'starting'})
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
        logger.info('Backup succeeded', extra={'action': 'backup', 'status': 'success'})
    except Exception as e:
        logger.exception('Backup failed', extra={'action': 'backup', 'status': 'failure'})

        if raise_on_error:
            raise e

def listen_trigger(port):
    class Handler(http.server.SimpleHTTPRequestHandler):
        def trigger(self):
            try:
                backup(raise_on_error=True)
                self.send_response(200)
                self.end_headers()
            except Exception as inst:
                self.send_response(500)
                self.end_headers()

        def do_GET(self):
            if (self.path == '/favicon.ico'):
                return

            self.trigger()

        def do_POST(self):
            self.trigger()

        def do_PUT(self):
            self.trigger()

    httpd = socketserver.TCPServer(('', port), Handler)
    try:
       httpd.serve_forever()
    except KeyboardInterrupt:
       pass
    httpd.server_close()

if config.get('schedule'):
    logger.info('Configure schedule')
    schedule_in_thread(config['schedule'], backup, runAtBegin=True)

if config.get('trigger', {}).get('port'):
    logger.info('Configure trigger')
    listen_trigger(int(config['trigger']['port']))

# Use TaskManager to avoid collision ?

