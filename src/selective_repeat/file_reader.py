from os import path, stat
from common.constants import PAYLOAD_SIZE


DELIMETER = '/'
HEADER = 5
class FileReader:
    ''' Class resposible for reading data in file'''

    def __init__(self, file_path, filename):
        self.path = file_path
        self.filename = filename
        self.file_size = 0
        self.seek = 0

    def get_filename(self):
        '''Returns the file name'''
        return self.filename

    def get_packets(self, chunks, seq_num):
        '''Returns a total of packets read from file '''
        payloads = []
        
        with open(self.path, "r", encoding='utf8') as file:
            file.seek(self.seek)
            for _ in range(1, (chunks + 1)):
                payload = file.read(PAYLOAD_SIZE)
                self.seek = file.tell()
                eof = 1 if self.seek == self.file_size else 0
                length = len(payload) + HEADER
                msg = length.to_bytes(2,'big') + seq_num.to_bytes(2,'big') + eof.to_bytes(1,'big') + payload.encode() 
                payloads.append(msg)

        return payloads
 