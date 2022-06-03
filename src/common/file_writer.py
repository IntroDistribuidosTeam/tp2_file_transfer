import os

class FileWriter:
    ''' Class resposible for writting data in file'''

    def __init__(self, file_path, file_name):
        self.file_path = file_path
        self.file_name = file_name

    def get_filepath(self):
        '''Returns file path'''
        return self.file_path

    def get_filename(self):
        ''' Returns file name'''
        return self.file_name

    def write(self,chunk):
        ''' Writes chunk in file '''
        with open(self.file_path, 'ab') as file:
            file.write(chunk)
    
    def remove_path(self):
        ''''Removes file in file_path'''
        if os.path.exists(self.file_path):
            os.remove(self.file_path)