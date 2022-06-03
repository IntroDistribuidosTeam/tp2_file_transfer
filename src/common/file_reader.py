import os
from common.constants import  FILE_SIZE

HEADER_SIZE = 5
class FileReader:
    ''' Class resposible for reading data in file'''

    def __init__(self, file_path, filename):
        self.path = file_path
        self.filename = filename
        self.file_size = os.path.getsize(file_path)
        self.seek = 0

    def get_filename(self):
        '''Returns the file name'''
        return self.filename

    def update_seek(self, new_seek):
        self.seek -= new_seek
    
    def eof(self):
        return self.seek >= self.file_size

    def get_packets(self, chunks, seq_num):
        '''Returns a total of packets read from file '''
        payloads = []
        
        with open(self.path, "rb") as file:
            file.seek(self.seek)
            i = 0
            while i < chunks and not self.eof():
                payload = file.read(FILE_SIZE)
                self.seek = file.tell()
                eof = 1 if self.seek >= self.file_size else 0
                length = len(payload) + HEADER_SIZE
                msg = length.to_bytes(2,'big') + (seq_num + i).to_bytes(2,'big') + eof.to_bytes(1,'big') + payload 
                payloads.append(msg)
                i += 1
            
        return payloads
 