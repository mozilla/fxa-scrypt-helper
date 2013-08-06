import unittest

import server as S

class TestInputValidation(unittest.TestCase):

    def test_validate_parameters(self):
        valid = S.REQUIRED_PARAMETERS.copy()
        self.assertEqual(S.validate_parameters(valid),
                         (True, S.REQUIRED_PARAMETERS))

if __name__ == '__main__':
    unittest.main()
