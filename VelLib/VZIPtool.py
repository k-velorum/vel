from cgitb import handler
import io
import requests
import zipfile
from VelLib import MultiAssist
from time import time, sleep
from multiprocessing import Value
import hashlib
import logging

class LiveZIPViewer(MultiAssist):
    def __init__(self, url, interval):
        super().__init__()
        self.url = url
        self.interval = interval
        self.file = None
        self.timestamp = Value('d', 0)
        self.fio = None
        self._di = self.makeDict({"d":None})
        self.rePrepare = Value('i', True)
        self.autoRequest()
        self.prepare()

    def urlRequest(self, url):
        old = self._di["d"] if self._di["d"] is not None else "".encode()
        old_hash = hashlib.sha256(old).hexdigest()
        for i in range(int(self.interval/5)):
            try:
                new = requests.get(url, timeout=self.interval).content
                new_hash = hashlib.sha256(new).hexdigest()
                break
            except Exception as e:
                self._logger.warning("download retry({} times): {}".format(i, e))
                sleep(5)
                continue
        if (old_hash != new_hash):
            self._di["d"] = new
            self.rePrepare.value = True
            self.timestamp.value = time()
            self._logger.info("new zip data is downloaded. md5: {} -> {}".format(old_hash, new_hash))
            return True
        else:
            self._logger.info("same data is downloaded. md5:{}".format(old_hash))
        return False

    def renewNow(self):
        return self.urlRequest(self.url)

    def autoRequest(self):
        self.autorun(self.urlRequest, self.interval, args=(self.url,))

    def prepare(self):
        while self._di["d"] is None:
            sleep(0.1)
        zipdata = self._di["d"]
        self.fio = io.BytesIO()
        self.fio.write(zipdata)
        z = zipfile.ZipFile(self.fio)
        self.file = z
        self.rePrepare.value = False

    def getLoadTime(self):
        return self.timestamp.value

    def getData(self):
        return self.file

    def open(self, name, mode='r', pwd=None, force_zip64=False):
        if type(pwd) is str:
            pwd = pwd.encode()
        if self.rePrepare.value or self.file is None:
            self.prepare()
        if name in self.namelist():
            return self.file.open(name, mode=mode, pwd=pwd, force_zip64=force_zip64)
        raise FileNotFoundError(name, "file not found.")

    def namelist(self):
        return self.file.namelist() if self.file is not None else None

if __name__ == '__main__':
    from VelLib import maLogger
    logger, mplogger = maLogger(logging.INFO)
    mplogger.warning('test')
    logger.warning('test2')

    z = LiveZIPViewer("http://localhost/style.zip", 10)
    while True:
        sleep(5)
        logger.info(z.namelist())