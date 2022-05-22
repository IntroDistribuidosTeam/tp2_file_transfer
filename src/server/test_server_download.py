import unittest
from server_download import *

# Test
class ServerDownloadTest(unittest.TestCase):
    
    def test_01_is_ack_is_true(self):
        payload = "1"

        self.assertTrue(is_ack(payload=payload))

    def test_02_is_ack_is_false(self):
        payload = "0"

        self.assertFalse(is_ack(payload=payload))

    def test_03_is_nack_is_true(self):
        payload = "0"
        
        self.assertTrue(is_nack(payload=payload))

    def test_04_is_nack_is_false(self):
        payload = "1"

        self.assertFalse(is_nack(payload=payload))

    def test_05_file_data_recieves_94_word_text(self):
        file = "/home/alejo/Documentos/IntroDistribuidos/tp2_file_transfer/test/test_file.txt"
        seek = 0
        eof = True
        expected = 94 
        
        p,seek,eof = file_data(seek,file,eof)

        self.assertEquals(expected,len(p))

    def test_06_file_data_seek_updated_to_94(self):
        file = "/home/alejo/Documentos/IntroDistribuidos/tp2_file_transfer/test/test_file.txt"
        seek = 0
        eof = True
        expected = 94 
        
        p,seek,eof = file_data(seek,file,eof)

        self.assertEquals(expected,seek)

    def test_07_file_data_eof_updated_to_true(self):
        file = "/home/alejo/Documentos/IntroDistribuidos/tp2_file_transfer/test/test_file.txt"
        seek = 0
        eof = False # end of file
        
        p,seek,eof = file_data(seek,file,eof)

        self.assertTrue(eof)

    def test_08_end_of_file_is_true(self):
        p = "Hola esto es un texto de prueba donde se testeara y sabremos si anda bien\nbla bla bla bla hola"
        response = make_response(p,True)
        eof = int(response.decode().split(",")[0])
        self.assertTrue(eof)
    
    def test_09_end_of_file_is_false(self):
        p = "Hola esto es un texto de prueba donde se testeara y sabremos si anda bien\nbla bla bla bla hola"
        response = make_response(p,True)
        eof = int(response.decode().split(",")[0])
        self.assertTrue(eof)

    def test_10_default_response_is_nack(self):
        response = default_response()

        self.assertTrue(is_nack(response))

if __name__ == '__main__':
    unittest.main()
