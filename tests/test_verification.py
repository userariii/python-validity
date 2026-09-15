import unittest

from validitysensor.verification import CaptureRetryNotifier


class CaptureRetryNotifierTests(unittest.TestCase):
    def test_waiting_for_contact_never_self_cancels(self):
        emitted = []
        logged = []
        notify = CaptureRetryNotifier(
            'alice',
            lambda result, done: emitted.append((result, done)),
            lambda message, *args: logged.append((message, args)),
        )

        # Rejected/blank frames do not distinguish a wedged chip from a user
        # who has not made adequate contact. The client owns the timeout.
        for _ in range(100):
            notify(None)

        self.assertEqual(notify.count, 100)
        self.assertEqual(emitted, [('verify-retry-scan', False)] * 100)
        self.assertEqual(len(logged), 100)


if __name__ == '__main__':
    unittest.main()
