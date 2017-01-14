import time
import ts3
import logging.config
import logging
import logging.handlers

# General settings:
BOT_NAME = ''
USER = ''
PASS = ''
HOST = ''
PORT = ''
SID = ''                    # virtual server ID, usually 1

# Promotion bot settings:
CONNECTIONS_REQUIRED = 10   # the amount of total reconnect required
DAYS_REQUIRED = 30          # the amount of required days between first and current connect
PROMOTION_MESSAGE = 'You have been automatically promoted'
PROMOTE_FROM = '8'          # server group number (8 is guest by default)
PROMOTE_TO = '7'            # server group number (7 is member by default)
CHECKING_INTERVAL = 10      # checking interval in seconds

def ts3_bot(server):
    while True:
        # Process to promote clients
        for client in server.clientlist():
            if client["client_type"] != '1' :
                try:
                    client_info = server.clientinfo(clid=client['clid'])[0]
                    server_group = client_info['client_servergroups']
                    database_id = client_info['client_database_id']
                    connections = int(client_info['client_totalconnections'])
                    seconds_required = DAYS_REQUIRED * 86400
                    first_connected = int(client_info['client_created'])
                    last_connected = int(client_info['client_lastconnected'])
                    seconds_current = last_connected - first_connected

                    if server_group == PROMOTE_FROM and connections >= CONNECTIONS_REQUIRED and seconds_current >= seconds_required:
                        server.servergroupaddclient(sgid=PROMOTE_TO, cldbid=database_id)
                        logmessage = 'Client ' + database_id + ' was promoted from servergroup id ' + PROMOTE_FROM + ' to server group ID ' +  PROMOTE_TO
                        logging.info(logmessage)
                        server.sendtextmessage(targetmode=1, target=client['clid'], msg=PROMOTION_MESSAGE)
                except ts3.query.TS3QueryError:
                    pass
        time.sleep(CHECKING_INTERVAL)


if __name__ == '__main__':
    # Connect to server
    with ts3.query.TS3Connection(HOST, PORT) as ts3conn:
        ts3conn.login(client_login_name=USER, client_login_password=PASS)
        ts3conn.use(sid=SID)
        ts3conn.clientupdate(client_nickname=BOT_NAME)

        # Logging
        f = logging.Formatter(fmt='%(levelname)s:%(name)s: %(message)s (%(asctime)s; %(filename)s:%(lineno)d)', datefmt="%Y-%m-%d %H:%M:%S")
        handlers = [
            logging.handlers.RotatingFileHandler('promotion_bot.log', encoding='utf8', maxBytes=100000, backupCount=5),
            logging.StreamHandler()
        ]
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        for h in handlers:
            h.setFormatter(f)
            h.setLevel(logging.DEBUG)
            root_logger.addHandler(h)
        logging.info(BOT_NAME + ' started')

        # Run bot
        ts3_bot(ts3conn)
