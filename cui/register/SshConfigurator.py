import os.path
import re
from requests.structures import CaseInsensitiveDict

class SshConfigurator(object):
    def __init__(self):
        self.__re_host = re.compile('host ', re.IGNORECASE)
        self.__re_indent = re.compile('[ \t]+', re.IGNORECASE)
        self.__text = None
        self.__hosts = {}

    def __GetHosts(self):
        return self.__hosts
    Hosts = property(__GetHosts)

    def Load(self, path=None):
        if None is path:
            path_dir_ssh = os.path.join(os.path.expanduser('~'), '.ssh/')
            path_file_config = os.path.join(path_dir_ssh, 'config')
        else:
            path_file_config = path
        with open(path_file_config) as f:
            self.__text = f.read()
            self.__Parse()

    def __Parse(self):
        nowHost = None
        for line in self.__text.split('\n'):
            # Host定義行なら
            if self.__re_host.match(line):
                nowHost = re.sub(self.__re_host, '', line).strip()
                # すでに存在する場合無視する（同一Host定義のうち、最初に見つかった定義を使う。後に見つかった定義は無視する）
                if nowHost in self.__hosts.keys():
                    nowHost = None
                    continue
                self.__hosts[nowHost] = CaseInsensitiveDict()
                self.__AppendHostStatus(nowHost, line)
            # 行頭がインデントされているならnowHost内の定義行と解釈する
            elif self.__re_indent.match(line):
                self.__AppendHostStatus(nowHost, line)
            else:
                # コメント行と空行は無視する
                if '#' == line[0:1] or 0 == len(line.strip()):
                    continue
                # Host外の設定ならHost内定義フラグを折る
                else:
                    nowHost = None

    def __AppendHostStatus(self, nowHost, line):
        # Host内定義行なら
        if None is not nowHost:
            elements = line.split()
            if 2 == len(elements):
                self.__hosts[nowHost].update({elements[0]: elements[1]})
