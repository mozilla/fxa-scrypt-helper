
import os
import random
import binascii
from loads import TestCase

FIXED_PARAMS = {
    "salt": "identity.mozilla.com/picl/v1/scrypt",
    "N": 65536,
    "r": 8,
    "p": 1,
    "buflen": 32,
}


# If we verified the calculation on every request, we wouldn't be able
# to generate much load!  Instead we probabilistically send some known
# passwords and verify that we get known results.

KNOWN_VALUES = {
    "helloworld": "4d9c58e7d8a3f82ba56a5bdc995e5a51"
                  "72551d327eaaaedf88d310a1033da658",
    "yodawgiherdulikescrypt": "da4681e6f0b642b17b6da27ee79fde02"
                              "6d1232d88f86547e37045c203e501f6b",
    "\x01\x02\x03\x04\x05\x06": "4a3880fa82ef3cf80e5cd59b41ae0dce"
                                "07a3d1cab1f5a56f364ba1572f580c99",
}
try:
    import scrypt
except ImportError:
    pass
else:
    for _ in xrange(10):
        pwd = os.urandom(random.randrange(5, 20))
        KNOWN_VALUES[pwd] = scrypt.hash(pwd, **FIXED_PARAMS).encode("hex")


class StressTest(TestCase):

    server_url = "http://scrypt.loadtest.lcip.org"

    def test_scrypt_helper(self):
        # Randomly decide to send a good payload, a known
        # payload so we can verify results, or a bad payload.
        choice = random.randrange(0, 20)
        if choice < 2:
            payload, status, output = self._make_known_payload()
        elif choice < 5:
            payload, status, output = self._make_bad_payload()
        else:
            payload, status, output = self._make_good_payload()
        response = self.app.post_json("/", payload, status=status)
        # Verify the correctness of the result, as much as we can.
        if status == 200:
            result = response.json
            self.assertEqual(result.keys(), ["output"])
            if output is not None:
                self.assertEqual(result["output"], output)

    def _make_good_payload(self):
        payload = {"input": self._make_random_hex_password()}
        payload.update(FIXED_PARAMS)
        return payload, 200, None

    def _make_known_payload(self):
        input, output = random.choice(KNOWN_VALUES.items())
        payload = {"input": input.encode("hex")}
        payload.update(FIXED_PARAMS)
        return payload, 200, output

    def _make_random_hex_password(self):
        pwdlen = random.randrange(8, 60)
        pwd = hex(random.randrange(16**pwdlen)).strip("0xL")
        if len(pwd) % 2 == 1:
            pwd += "0"
        return pwd

    def _make_bad_payload(self):
        payload, _, _ = self._make_good_payload()
        badifier = random.choice(self._badifiers)
        return badifier(self, payload), 400, None

    # A helpful selection of ways to turn
    # a valid payload into an invalid one.

    _badifiers = []

    @_badifiers.append
    def _badify_remove_a_key(self, payload):
        payload.pop(random.choice(payload.keys()))
        return payload

    @_badifiers.append
    def _badify_change_a_param(self, payload):
        key = random.choice(["N", "r", "p", "buflen"])
        goodval = badval = payload[key]
        while badval == goodval:
            badval = random.randrange(0, 2*goodval)
        payload[key] = badval
        return payload

    @_badifiers.append
    def _badify_send_invalid_salt(self, payload):
        payload["salt"] = self._make_random_hex_password()
        return payload

    @_badifiers.append
    def _badify_send_invalid_hex_input(self, payload):
        badinput = binascii.unhexlify(payload["input"])
        badinput = binascii.b2a_base64(badinput).strip()
        try:
            int(badinput, 16)
        except ValueError:
            pass
        else:
            badinput += "J"
        payload["input"] = badinput
        return payload
