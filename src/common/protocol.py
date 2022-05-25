import logging




def parse_request(msg):
    request = {}
    data = msg.decode().split(DELIMETER)
    if len(data) != 2:
        logging.error('Wrong data format')
        raise Exception
    if data[ACTION_POS] not in [UPLOAD_CODE, DONWLOAD_CODE]:
        logging.error(f'Command should be {UPLOAD_CODE} or {DONWLOAD_CODE}')
        raise Exception
    request['command'] = data[ACTION_POS]
    request['filename'] = data[FILENAME_POS]

    return request
