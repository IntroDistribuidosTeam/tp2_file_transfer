import unittest

from setuptools import setup

class EjemploTest(unittest.TestCase):
    
    def test_one(self):
        self.assertEquals(1,1)
    


# Esto sirve para decir que si se llama por comando a test.py se ejecutan las pruebas
if __name__ == '__main__':
    unittest.main()