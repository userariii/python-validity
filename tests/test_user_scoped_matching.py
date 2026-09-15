import unittest
from struct import pack
from unittest.mock import patch

from validitysensor.sensor import FingerNotMatchedException, sensor


def matcher_reply(user_id, subtype, hsh=b'x' * 32):
    # tls.app(0x60) response: status + payload length + TLV dictionary
    payload = (
        pack('<HHI', 1, 4, user_id) +
        pack('<HHH', 3, 2, subtype) +
        pack('<HH', 4, len(hsh)) + hsh
    )
    return b'\x00\x00' + pack('<H', len(payload)) + payload


class UserScopedMatchingTests(unittest.TestCase):
    def setUp(self):
        self.original_type = getattr(sensor, 'real_device_type', None)
        sensor.real_device_type = 0xd51

    def tearDown(self):
        sensor.real_device_type = self.original_type

    def run_match(self, requested_user, returned_user, subtype):
        replies = [b'\x00\x00', matcher_reply(returned_user, subtype), b'\x00\x00']
        with patch('validitysensor.sensor.tls.app', side_effect=replies), \
                patch('validitysensor.sensor.usb.wait_int',
                      return_value=b'\x03\x00\x03\x00\xdb'):
            return sensor.match_finger(requested_user)

    def test_exact_linux_user_matches(self):
        result = self.run_match(11, 11, 2)
        self.assertEqual(result[0:2], (11, 2))

    def test_different_user_is_rejected(self):
        with self.assertRaises(FingerNotMatchedException):
            self.run_match(11, 5, 2)

    def test_windows_private_subtype_is_rejected(self):
        with self.assertRaises(FingerNotMatchedException):
            self.run_match(11, 11, 0xf5)

    def test_verify_retries_wrong_finger_three_times_then_fails(self):
        retries = []

        with patch.object(sensor, 'capture', return_value=(0, 0, 0, 0)), \
                patch.object(sensor, 'match_finger',
                             side_effect=FingerNotMatchedException('wrong finger')), \
                patch('validitysensor.sensor.glow_start_scan'), \
                patch('validitysensor.sensor.glow_end_scan'), \
                patch('validitysensor.sensor.sleep'):
            with self.assertRaises(FingerNotMatchedException):
                sensor.verify(11, lambda e: retries.append(str(e)))

        # First two wrong fingerprints request another scan.
        # The third is terminal and becomes verify-no-match.
        self.assertEqual(len(retries), 2)

    def test_verify_succeeds_if_correct_finger_is_used_on_third_attempt(self):
        retries = []

        with patch.object(sensor, 'capture', return_value=(0, 0, 0, 0)), \
                patch.object(sensor, 'match_finger',
                             side_effect=[
                                 FingerNotMatchedException('wrong finger'),
                                 FingerNotMatchedException('wrong finger'),
                                 (11, 2, b'x' * 32),
                             ]), \
                patch('validitysensor.sensor.glow_start_scan'), \
                patch('validitysensor.sensor.glow_end_scan'), \
                patch('validitysensor.sensor.sleep'):
            result = sensor.verify(11, lambda e: retries.append(str(e)))

        self.assertEqual(result[0:2], (11, 2))
        self.assertEqual(len(retries), 2)


if __name__ == '__main__':
    unittest.main()
