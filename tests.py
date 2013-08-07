import unittest

import server as S


class TestInputValidation(unittest.TestCase):

    def test_validate_parameters(self):
        SALT = b'identity.mozilla.com/picl/v1/scrypt'
        self.assert_(S.validate_parameters(
            {'N': 64*1024, 'r': 8, 'p': 1, 'buflen': 32, 'salt': SALT}))
        self.assertRaises(
            ValueError, S.validate_parameters,
            {'N': 32*1024, 'r': 8, 'p': 1, 'buflen': 32, 'salt': SALT})
        self.assertRaises(
            ValueError, S.validate_parameters,
            {'N': 64*1024, 'r': 7, 'p': 1, 'buflen': 32, 'salt': SALT})
        self.assertRaises(
            ValueError, S.validate_parameters,
            {'N': 64*1024, 'r': 8, 'p': 2, 'buflen': 32, 'salt': SALT})
        self.assertRaises(
            ValueError, S.validate_parameters,
            {'N': 64*1024, 'r': 8, 'p': 1, 'buflen': 33, 'salt': SALT})
        self.assertRaises(
            ValueError, S.validate_parameters,
            {'N': 64*1024, 'r': 8, 'p': 1, 'buflen': 32, 'salt': SALT+"not"})


if __name__ == '__main__':
    unittest.main()
