import unittest

import server as S

class TestInputValidation(unittest.TestCase):

    def test_validate_parameters(self):
        valid = S.REQUIRED_PARAMETERS.copy()
        self.assertEqual(S.validate_parameters(valid),
                         (True, S.REQUIRED_PARAMETERS))

        # extra params OK, ignored
        valid['nonsense'] = 'nonsense'
        self.assertEqual(S.validate_parameters(valid),
                         (True, S.REQUIRED_PARAMETERS))
        del valid['nonsense']

        # case-insensitive N parameter
        valid['n'] = valid['N']
        del valid['N']
        self.assertEqual(S.validate_parameters(valid),
                         (True, S.REQUIRED_PARAMETERS))
        valid['N'] = valid['n']
        del valid['n']

        # Test verification of hard-coded values
        invalid = S.REQUIRED_PARAMETERS.copy()
        for parameter in invalid:
            invalid[parameter] = object()
            self.assertEquals(S.validate_parameters(invalid)[0],
                              False)
            invalid[parameter] = valid[parameter]
            self.assertEqual(S.validate_parameters(valid),
                             (True, S.REQUIRED_PARAMETERS))


if __name__ == '__main__':
    unittest.main()
