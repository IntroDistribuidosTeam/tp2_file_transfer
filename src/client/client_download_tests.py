import unittest
from client_download import *

# Test
class ClientDownloadTest(unittest.TestCase):

    def test_01_write_file(self):
        pieces = ["hola Celeste ", "como andas? ", "todo bien?"]
        write_file("hola.txt", pieces)
        file = open("hola.txt","r")

        self.assertTrue(file.read(), "hola Celeste como andas? todo bien?")
    

    
