from os import path,stat



DELIMETER = '/'
PAYLOAD_SIZE = 1021

class FileReader:

    def __init__(self,path,filename) :
        self.path = path
        self.filename = filename
        self.file_size = 0
        self.seek = 0

        self.file_exist()
    

    def get_filename(self):
        return self.filename

    def file_exist(self):
        if path.exists(self.path):
            self.file_size = stat(self.file_path).st_size

    def open_file(self):
        if self.file_size != 0:
            raise FileExistsError
        return open(self.path, "r", encoding='utf8')

    def get_packets(self, chunks, seq_num):
        payloads = []
        eof = False
        try:
            file = self.open_file()

            file.seek(self.seek)
            for i in range(1, (chunks + 1)):
                payload = file.read(PAYLOAD_SIZE)
                self.seek = file.tell()
                eof = True if self.seek == self.file_size else False
                msg = str((seq_num + i)) + DELIMETER + str(eof) + DELIMETER + payload
                payloads.append(msg)

            file.close()
        except FileExistsError as error:
            eof = True
            msg = str(-1) + DELIMETER + str(eof) + DELIMETER + str(error)
            payloads.append(msg)

        return payloads

    def end_of_file(self):
        return self.seek >= self.file_size

    def get_file_data(self, end_of_file: bool):
        # Muevo hasta el seek donde termine la ultima vez
        try:
            file = self.open_file()
            file.seek(self.seek)
            file_payload = file.read(PAYLOAD_SIZE).strip()
            self.seek = file.tell()

            if len(file_payload) <= PAYLOAD_SIZE:
                end_of_file = True
            return file_payload,end_of_file
        except FileExistsError as error:
            #logging.error("Exception: %s ",file_not_found_e)
            return str(error),True

    def update_seek(self, res):
        self.seek -= res
