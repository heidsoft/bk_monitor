# coding: utf-8

import time


class TimeStats(object):
    """
    时间诊断
    """
    auto_start = True

    def __init__(self, bucket=""):
        self._bucket = bucket if isinstance(bucket, bytes) else bucket.encode(
            'utf8')
        self.info = []
        self._slug = []
        if self.auto_start:
            self.start()

    def start(self):
        self._start = time.time()
        self._split = [self._start, ]

    def stop(self):
        self._end = time.time()
        if self._slug:
            self.info.append(u"%s.%s: %s" % (
            self._bucket, self._slug[-1], (self._end - self._split[-1])))
        self.info.insert(0, u"%s.total: %s" % (
        self._bucket, (self._end - self._start)))
        self._split.append(self._end)

    def split(self, slug):
        _timing = time.time()
        if slug == "stop":
            return self.stop()
        if self._slug:
            self.info.append(u"%s.%s: %s" % (
            self._bucket, self._slug[-1], (_timing - self._split[-1])))
        self._slug.append(slug)
        self._split.append(_timing)

    def display(self):
        return u"*** time stats ***\n" + "\n".join(self.info)