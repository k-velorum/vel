import configparser

class ConfigReader:
    """iniファイルを読み込む。主にconfigparserの拡張。
    """
    def __init__(self, file):
        self.parser = configparser.ConfigParser()
        self.parser.optionxform = str
        self.parser.read(file)
        self.trueSet = {'true', 'on', 'yes'}
        self.falseSet = {'false', 'off', 'no'}

    def readConfigs(self, section):
        """指定したターゲットのコンフィグをすべて読む

        Args:

            section (str): iniファイルのセクションを指定する。

        Returns:

            dict: 指定したセクション内にあるすべてのパラメータを辞書型で返す。
        """
        di = {}
        for k, v in self.parser[section].items():
            di[k] = v
        return di

    def readConfigsCasted(self, section:str):
        """指定したターゲットのコンフィグをキャストしてすべて読む。boolean > int > float > strの順でキャストを試みる。
            booleanに適応する値は true/false, yes/no, on/off(大文字小文字は問わない)

        Args:

            section (str): iniファイルの[ここ]を指定する。

        Returns:

            dict:  指定したセクション内にあるすべてのパラメータを上記のルールでキャストした上、辞書型で返す。
        """
        di = {}
        for k, v in self.parser[section].items():
            di[k] = self.autoCaster(v)
        return di

    def readCasted(self, section:str, parameter:str):
        """指定したセクションの指定した内容をbool(true/false, on/off, yes/no) > int > float > strにキャストした上で単体で読む

        Args:

            section (str): iniファイルのセクションを指定する
            parameter (str): iniファイルのパラメータを指定する

        Returns:

            object : 得られたコンフィグ
        """

        return self.autoCaster(self.parser[section][parameter])

    def autoCaster(self, value):
        if value.lower() in self.trueSet:
            return True
        if value.lower() in self.falseSet:
            return False
        try:
            return int(value)
        except ValueError:
            pass
        try:
            return float(value)
        except ValueError:
            pass
        return value