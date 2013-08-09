import json, unittest

from pyramid import testing

import scrypt_helper as S


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

    def test_do_scrypt(self):
        # Handle an arbitrary correct request
        request_body = {
            "salt": "identity.mozilla.com/picl/v1/scrypt",
            "N": 65536,
            "r": 8,
            "p": 1,
            "buflen": 32,
            "input": "f84913e3d8e6d624689d0a3e9678ac8dcc79d2c2f3d9641488cd9d6ef6cd83dd"
}
        body = json.dumps(request_body)
        request = testing.DummyRequest(post=body)
        response = S.do_scrypt(request)
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.body)
        self.assertEqual(
            result.get('output'),
            "5b82f146a64126923e4167a0350bb181feba61f63cb1714012b19cb0be0119c5")



if __name__ == '__main__':
    unittest.main()
