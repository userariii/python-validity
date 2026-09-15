import logging


class CaptureRetryNotifier:
    """Emit one verify-retry-scan for each completed wrong-finger attempt.

    Generic capture-quality/idle errors are filtered inside sensor.verify(),
    so callbacks reaching this notifier represent genuine completed
    wrong/foreign fingerprint matches.
    """

    def __init__(self, user, emit, log=logging.info):
        self.user = user
        self.emit = emit
        self.log = log
        self.count = 0

    def __call__(self, error):
        self.count += 1
        self.log('Fingerprint retry-scan #%d (user=%s): %s',
                 self.count, self.user, error)
        self.emit('verify-retry-scan', False)
