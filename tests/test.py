import unittest


class TestingTest(unittest.TestCase):
    
    def test_test(self):
        i = 1
        i = i + 1
        self.assertEqual(i, 2)
        

if __name__ == '__main__':
    unittest.main()