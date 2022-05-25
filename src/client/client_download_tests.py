import unittest
from client_download import *

# Test
class ClientDownloadTest(unittest.TestCase):

    def test_01_write_file(self):
        piece = "hola Celeste como andas? todo bien?"
        write_piece("hola.txt", "w", piece)
        file = open("hola.txt","r")

        self.assertTrue(file.read(), "hola Celeste como andas? todo bien?")
    
    
