from multiprocessing import Process, Manager, Value, get_logger
from time import sleep
import signal
import logging

class AdditionableDict(dict):
    def add(self, key, value):
        if key not in self:
            self[key] = []
        self[key].append(value)

def maLogger(level=logging.WARNING, handler=logging.StreamHandler(), formatter=logging.Formatter("[%(asctime)s.%(msecs)03d] [%(levelname)s/%(processName)s]: %(message)s", "%Y-%m-%d %H:%M:%S"), **kwargs):
    import multiprocessing as mp
    handler.setFormatter(formatter)
    mplogger = mp.get_logger()
    mplogger.setLevel(level)
    mplogger.addHandler(handler)
    return mplogger

class MultiAssist():
    def __init__(self):
        self.processList = []
        self.running = {}
        self.manager = None
        self._logger = get_logger()

    def safeExit(self, *args):
        self.joinAllRunning()
        return True

    def killExit(self, *args):
        self.killAll()
        return True

    def setSignal(self, safe=True):
        if safe:
            signal.signal(signal.SIGINT, self.safeExit)
            signal.signal(signal.SIGTERM, self.safeExit)
        else:
            signal.signal(signal.SIGINT, self.killExit)
            signal.signal(signal.SIGTERM, self.killExit)

    def getManager(self):
        """multiprocessing.Managerを得る。self.managerに保持している場合は以前生成したものを、
           self.manager=Noneの場合は新しく生成する。

        Returns:
            SyncManager : multiprocessing.Manager()
        """
        if self.manager is None:
            self.manager = Manager()
        return self.manager

    def makeDict(self, di={}):
        """Manager.dictを生成する

        Args:
            di (dict, optional): 設定した任意のdictで初期化する

        Returns:
            Manager.dict: dict proxy
        """
        return self.getManager().dict(di)

    def makeList(self, li=[]):
        """Manager.listを生成する

        Args:
            li (list, optional): 設定した任意のlistで初期化する

        Returns:
            Manager.list: list proxy
        """
        return self.getManager().list(li)

    def makeFlag(self, flag=True):
        """multiprocessing.Valueを生成する

        Args:
            flag (bool, optional): 設定した任意のboolで初期化する

        Returns:
            Value : 生成したValue。アクセスする場合はValue.value
        """
        return Value('i', flag)

    def processStarter(self, target, *args, **kwargs):
        """指定した関数を別プロセスで実行する。

        Args:
        ----
            target (function): 実行する関数。
            args (tuple): 実行する関数の引数 (tupleのため引数が1つの場合は必ず","を最後に付ける)。
            kwargs (dict): 実行する関数のキーワード引数。

        Returns:
        -------
            Process: 生成したProcess
        """
        p = Process(target=target, args=args, kwargs=kwargs)
        p.start()
        self.processList.append(p)
        return p

    def joinAll(self):
        """processStarterにて実行したものをすべてjoinする
        """
        for p in self.processList:
            p.join()
        self.processList = []

    def join(self, process):
        """指定したProcessをJoinする

        Args:
            process (multiprocessing.Process): processStarterの返り値のProcess
        """
        for i, p in enumerate(self.processList):
            if p == process:
                p.join()
                del self.processList[i]

    def joinAllRunning(self):
        """autorunさせたものをすべてJoinする
        """
        self.stopAllRunning()
        for p in self.running.keys():
            p.join()
            self.processList.remove(p)
        self.cleanRunning()

    def joinRunning(self, p):
        """autorunさせた指定のプロセスをJoinする

        Args:
            p (multiprocessing.Process): autorunの返り値のProcess
        """
        if p in self.running:
            self.running[p].value = False
            self.join(p)
            self.processList.remove(p)

    def stopAllRunning(self):
        """autorunで実行したすべてのプロセスに停止フラグをセットする
        """
        for v in self.running.values():
            v.value = False

    def killAll(self):
        """管理しているすべてのプロセスをprocess.kill()する
        """
        for k in self.processList:
            k.kill()

    def cleanRunning(self):
        """autorunで実行したプロセスのうち、プロセスがis_aliveでないものを管理リストから除外する
        """
        for k in self.running.copy().keys():
            if not k.is_alive():
                try:
                    del self.running[k]
                except KeyError:
                    pass
                try:
                    self.processList.remove(k)
                except ValueError:
                    pass

    def autorun(self, target, interval, args=(), kwargs={}):
        """任意の関数を別プロセスで指定秒ごとに実行する
        1つ目の返り値を操作することでプロセスを停止できる
        (e.g. flag, process = autorun(hoge, 60)とした場合、f.value=falseで継続停止)

        Args:
        ----
            target (function): 実行する関数
            interval (int): 実行する間隔(秒)
            args (tuple, optional): 関数の引数。省略可
            kwargs (dict, optional): 関数のキーワード引数。省略可

        Returns:
        -------
            (multiprocessing.Value, multiprocessing.Process): Value.valueにはTrueが入った状態で得られる。これをFalseにした時、継続実行を取りやめる。実行終了はProcessの各種メソッドにて確認できる(Join等)
        """
        continueflag = self.makeFlag(True)
        p = self.processStarter(self._run, target, interval, continueflag, args, kwargs)
        self.running[p] = continueflag
        self._logger.info("autorun start (interval=%dsec): %s"%(interval, target))
        return p

    def _run(self, target, interval, continueflag, args, kwargs):
        interval_sec = interval
        interval_dec = 0
        if interval > 1:
            interval_sec = int(interval // 1)
            interval_dec = interval % 1
        interval_sec = range(interval_sec)
        while continueflag.value:
            target(*args, **kwargs)
            for i in interval_sec:
                if not continueflag.value:
                    break
                sleep(1)
            sleep(interval_dec)
        return 0

    def __enter__(self):
        self._logger.debug("[%s] __enter__ is called", self.__class__.__name__)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.safeExit()
        self._logger.debug("[%s] __exit__ is called(%s, %s, %s)"%(self.__class__.__name__, exc_type, exc_val, exc_tb))
        return True

    def __getstate__(self):
        #Process, Managerはpickle化できないため破棄
        rv = self.__dict__.copy()
        rv["processList"] = []
        rv["running"] = {}
        rv["manager"] = None
        return rv

    def __setstate__(self, state):
        self.__dict__.update(state)