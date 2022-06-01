import logging
from common.constants import DELIMETER,UPLOAD_CODE,ACTION_POS,DONWLOAD_CODE,FILENAME_POS,LOG_FORMAT



def parse_request(msg):
    request = {}
    data = msg.decode().split(DELIMETER)
    if len(data) != 2:
        logging.error('Wrong data format')
        raise Exception
    if data[ACTION_POS] not in [UPLOAD_CODE, DONWLOAD_CODE]:
        logging.error("Command should be %s  or %s",UPLOAD_CODE,DONWLOAD_CODE)
        raise Exception
    request['command'] = data[ACTION_POS]
    request['filename'] = data[FILENAME_POS]

    return request




def set_up_logger():
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)