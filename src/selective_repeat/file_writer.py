import os

class FileWriter:

    def __init__(self, file_path, file_name):
        self.file_path = file_path
        self.file_name = file_name


    def write(self,chunk):
        with open(self.file_path, 'w', encoding="utf8") as file:
            file.write(chunk)
        
    def get_filepath(self):
        return self.file_path

    def remove_path(self):
        os.remove(self.file_path)
    