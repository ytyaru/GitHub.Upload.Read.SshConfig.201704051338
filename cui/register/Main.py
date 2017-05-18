#!/usr/bin/python3
#!python3
#encoding:utf-8
import os.path
import subprocess
import shlex
import dataset
import database.src.Database
import database.src.account.Main
import cui.register.github.api.v3.authorizations.Authorizations
import cui.register.github.api.v3.users.SshKeys
import cui.register.github.api.v3.users.Emails
import web.sqlite.Json2Sqlite
import cui.register.SshConfigurator
import re
class Main:
    def __init__(self, path_dir_db):
        self.path_dir_db = path_dir_db
        self.j2s = web.sqlite.Json2Sqlite.Json2Sqlite()
        self.__db = None
    def Insert(self, args):
        print('Account.Insert')
        print(args)
        print('-u: {0}'.format(args.username))
        print('-p: {0}'.format(args.password))
        print('-m: {0}'.format(args.mailaddress))
        print('-s: {0}'.format(args.ssh_host))
        print('-t: {0}'.format(args.two_factor_secret_key))
        print('-r: {0}'.format(args.two_factor_recovery_code_file_path))
        print('--auto: {0}'.format(args.auto))

        self.__db = database.src.Database.Database()
        self.__db.Initialize()
        
        account = self.__db.account['Accounts'].find_one(Username=args.username)
        print(account)
        
        sshconf = cui.register.SshConfigurator.SshConfigurator()
        # テスト用SSH configファイル
#        sshconf.Load('/tmp/SshConfigurator.201704041335/ssh_conf_dup')
        sshconf.Load()
        if None is account:
            # 1. Tokenの新規作成
            auth = cui.register.github.api.v3.authorizations.Authorizations.Authorizations(args.username, args.password)
            token_repo = auth.Create(args.username, args.password, scopes=['repo'])
            token_delete_repo = auth.Create(args.username, args.password, scopes=['delete_repo'])
            token_user = auth.Create(args.username, args.password, scopes=['user'])
            token_public_key = auth.Create(args.username, args.password, scopes=['admin:public_key'])
            # 2. APIでメールアドレスを習得する。https://developer.github.com/v3/users/emails/
            if None is args.mailaddress:
                emails = cui.register.github.api.v3.users.Emails.Emails()
                mails = emails.Gets(token_user['token'])
                print(mails)
                for mail in mails:
                    if mail['primary']:
                        args.mailaddress = mail['email']
                        break
            # 3. SSHの生成と設定
            # 起動引数`-s`がないなら
            if None is args.ssh_host:
                # 3-1. SSH鍵の新規作成
                ssh_key_gen_params = self.__SshKeyGen(args.username, args.mailaddress)
                host = self.__SshConfig(args.username, ssh_key_gen_params['path_file_key_private'])
                # 3-2. SSH鍵をGitHubに登録してDBに挿入する
                api_ssh = cui.register.github.api.v3.users.SshKeys.SshKeys()
                j_ssh = api_ssh.Create(token_public_key['token'], args.mailaddress, ssh_key_gen_params['public_key'])
                # 3-3. SSH接続確認
                self.__SshConnectCheck(host, 'git', ssh_key_gen_params['path_file_key_private'])
            else:
                if not(args.ssh_host in sshconf.Hosts.keys()):
                    raise Exception('存在しないSSH Host名が指定されました。-s引数を指定しなければSSH鍵を新規作成して設定します。既存のSSH鍵を使用するなら~/.ssh/configファイルに設定すると自動で読み取ります。configファイルに設定済みのHost名は次の通りです。 {0}'.format(sshconf.Hosts.keys()))
                
                host = args.ssh_host
                ssh_key_gen_params = {
                    'type': None,
                    'bits': None,
                    'passphrase': None,
                    'path_file_key_private': None,
                    'path_file_key_public': None,
                    'private_key': None,
                    'public_key': None,
                }
                # SSH configファイルから設定値を読み取る
                if re.compile('.+\.pub$', re.IGNORECASE).match(sshconf.Hosts[args.ssh_host]['IdentityFile']):
#                    if re.compile('.pub\Z', re.IGNORECASE).match(sshconf.Hosts[args.ssh_host]['IdentityFile']):
#                    if sshconf.Hosts[args.ssh_host]['IdentityFile'].endswith('.pub'):
                    ssh_key_gen_params.update({'path_file_key_public': sshconf.Hosts[args.ssh_host]['IdentityFile']})
                    ssh_key_gen_params.update({'path_file_key_private': sshconf.Hosts[args.ssh_host]['IdentityFile'][:-4]})
                else:
                    ssh_key_gen_params.update({'path_file_key_private': sshconf.Hosts[args.ssh_host]['IdentityFile']})
                    ssh_key_gen_params.update({'path_file_key_public': sshconf.Hosts[args.ssh_host]['IdentityFile'] + '.pub'})
                print(ssh_key_gen_params['path_file_key_private'])
                print(ssh_key_gen_params['path_file_key_public'])
                # キーファイルから内容を読み取る
                with open(ssh_key_gen_params['path_file_key_private']) as f:
                    ssh_key_gen_params['private_key'] = f.read()
                with open(ssh_key_gen_params['path_file_key_public']) as f:
                    # 公開鍵ファイルはスペース区切りで`{ssh-rsa} {公開鍵} {コメント}`の形式になっている。
                    # GitHubではコメント値は保持しない。
                    # 末尾はスペース+comment(メールアドレス)。必要なのは前半のみ
                    pub_keys = f.read().split()
                    ssh_key_gen_params['public_key'] = pub_keys[0] + ' ' + pub_keys[1]
#                print(ssh_key_gen_params)
                
                # 暗号化強度の情報を取得する
                # ssh-keygen -l -f {秘密鍵ファイルパス}
                # {bits} {AA:BB:CC...}  {comment} ({type})
                # type=`(RSA)`、bits=`2048` comment=`メアド@mail.com`
                cmd = 'ssh-keygen -l -f "{0}"'.format(ssh_key_gen_params['path_file_key_public'])
                print(cmd)
                p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout_data, stderr_data = p.communicate()
                print(stdout_data.decode('utf-8'))
                print(stdout_data.decode('utf-8').split())
                elements = stdout_data.decode('utf-8').split()
                ssh_key_gen_params['bits'] = elements[0]
                elements[3] = elements[3][1:] # '(' 削除
                elements[3] = elements[3][:-1] # ')' 削除
                ssh_key_gen_params['type'] = elements[3].lower()
                print(ssh_key_gen_params)
                
                # GitHubのSSHにすでに設定されているか確認する
                api_ssh = cui.register.github.api.v3.users.SshKeys.SshKeys()
                j_sshs = api_ssh.Gets(args.username, token_public_key['token'])
                print(j_sshs)
                j_sshkey = None
                for j in j_sshs:
                    if j['key'] == ssh_key_gen_params['public_key']:
                        j_sshkey = j
                        print('一致一致一致一致一致一致一致一致一致一致一致一致一致')
                        break
                j_ssh = None
                if None is j_sshkey:
                    # 新規作成
                    print('新規作成新規作成新規作成新規作成新規作成新規作成新規作成新規作成新規作成新規作成')
                    j_ssh = api_ssh.Create(token_public_key['token'], args.mailaddress, ssh_key_gen_params['public_key'])
                else:
                    # 詳細情報取得
                    print('詳細情報取得詳細情報取得詳細情報取得詳細情報取得詳細情報取得詳細情報取得')
                    j_ssh = api_ssh.Get(token_public_key['token'], j_sshkey['id'])
                
            # 4. 全部成功したらDBにアカウントを登録する
            self.__db.account['Accounts'].insert(self.__CreateRecordAccount(args))
            account = self.__db.account['Accounts'].find_one(Username=args.username)
            if None is not args.two_factor_secret_key:
                self.__db.account['AccessTokens'].insert(self.__CreateRecordTwoFactor(account['Id'], args))
            self.__db.account['AccessTokens'].insert(self.__CreateRecordToken(account['Id'], token_repo))
            self.__db.account['AccessTokens'].insert(self.__CreateRecordToken(account['Id'], token_delete_repo))
            self.__db.account['AccessTokens'].insert(self.__CreateRecordToken(account['Id'], token_user))
            self.__db.account['AccessTokens'].insert(self.__CreateRecordToken(account['Id'], token_public_key))
            self.__db.account['SshConfigures'].insert(self.__CreateRecordSshConfigures(account['Id'], host, ssh_key_gen_params))
            self.__db.account['SshKeys'].insert(self.__CreateRecordSshKeys(account['Id'], ssh_key_gen_params['private_key'], ssh_key_gen_params['public_key'], j_ssh))
        # 作成したアカウントのリポジトリDB作成や、作成にTokenが必要なライセンスDBの作成
        self.__db.Initialize()
        return self.__db

    def __CreateRecordAccount(self, args):
        return dict(
            Username=args.username,
            MailAddress=args.mailaddress,
            Password=args.password,
            CreateAt="1970-01-01T00:00:00Z"
        )
        # 作成日時はAPIのuser情報取得によって得られる。
        
    def __CreateRecordToken(self, account_id, j):
        return dict(
            AccountId=account_id,
            IdOnGitHub=j['id'],
            Note=j['note'],
            AccessToken=j['token'],
            Scopes=self.j2s.ArrayToString(j['scopes'])
        )

    def __CreateRecordTwoFactor(self, account_id, args):
        return dict(
            AccountId=account_id,
            Secret=args.args.two_factor_secret_key
        )
        
    def __SshKeyGen(self, username, mailaddress):
        # SSH鍵の生成
        path_dir_ssh = os.path.join(os.path.expanduser('~'), '.ssh/')
#        path_dir_ssh = "/tmp/.ssh/" # テスト用
        path_dir_ssh_keys = os.path.join(path_dir_ssh, 'github/')
        if not(os.path.isdir(path_dir_ssh_keys)):
            os.makedirs(path_dir_ssh_keys)
        protocol_type = "rsa" # ["rsa", "dsa", "ecdsa", "ed25519"]
        bits = 4096 # 2048以上推奨
        passphrase = '' # パスフレーズはあったほうが安全らしい。忘れるだろうから今回はパスフレーズなし。
        path_file_key_private = os.path.join(path_dir_ssh_keys, 'rsa_{0}_{1}'.format(bits, username))
        print(path_dir_ssh)
        print(path_dir_ssh_keys)
        print(path_file_key_private)
        command = 'ssh-keygen -t {p_type} -b {bits} -P "{passphrase}" -C "{mail}" -f "{path}"'.format(p_type=protocol_type, bits=bits, passphrase=passphrase, mail=mailaddress, path=path_file_key_private)
        print(command)
        subprocess.call(shlex.split(command))
        
        private_key = None
        with open(path_file_key_private, 'r') as f:
            private_key = f.read()
        public_key = None
        with open(path_file_key_private + '.pub', 'r') as f:
            public_key = f.read()
        
        ssh_key_gen_params = {
            'type': protocol_type,
            'bits': bits,
            'passphrase': passphrase,
            'path_file_key_private': path_file_key_private,
            'path_file_key_public': path_file_key_private + '.pub',
            'private_key': private_key,
            'public_key': public_key,
        }
        return ssh_key_gen_params
#        return path_file_key_private

    def __SshConfig(self, username, IdentityFile, Port=22):
        host = 'github.com.{username}'.format(username=username)
        append = '''\
Host {Host}
  User git
  Port {Port}
  HostName github.com
  IdentityFile {IdentityFile}
  TCPKeepAlive yes
  IdentitiesOnly yes
'''
        append = append.format(Host=host, Port=Port, IdentityFile=IdentityFile)
        print(append)
        path_dir_ssh = os.path.join(os.path.expanduser('~'), '.ssh/')
#        path_dir_ssh = "/tmp/.ssh/" # テスト用
        path_file_config = os.path.join(path_dir_ssh, 'config')
        if not(os.path.isfile(path_file_config)):
            with open(path_file_config, 'w') as f:
                pass        
        # configファイルの末尾に追記する
        with open(path_file_config, 'a') as f:
            f.write(append)
        
        return host

    def __SshConnectCheck(self, host, config_user, path_file_key_private):
        """
    def __SshConnectCheck(self, host, config_user, path_file_key_private):
        command = 'ssh -i "{path_file_key_private}" -T {config_user}@{config_host}'.format(
            path_file_key_private=path_file_key_private,
            config_user='git',
            config_host=host)
        print(command)
        print(subprocess.check_output(command, shell=True, universal_newlines=True))
        """
        command = "ssh -T git@{host}".format(host=host)
        print(command)
        # check_output()だと例外発生する
        # subprocess.CalledProcessError: Command 'ssh -T git@github.com.{user}' returned non-zero exit status 1
#        subprocess.check_output(command, shell=True, universal_newlines=True)
        subprocess.call(command, shell=True, universal_newlines=True)
        # Hi {user}! You've successfully authenticated, but GitHub does not provide shell access.

    def __CreateRecordSshConfigures(self, account_id, host, ssh_key_gen_params):
        return dict(
            AccountId=account_id,
            HostName=host,
            PrivateKeyFilePath=ssh_key_gen_params['path_file_key_private'],
            PublicKeyFilePath=ssh_key_gen_params['path_file_key_public'],
            Type=ssh_key_gen_params['type'],
            Bits=ssh_key_gen_params['bits'],
            Passphrase=ssh_key_gen_params['passphrase'],
        )

    def __CreateRecordSshKeys(self, account_id, private_key, public_key, j):
        return dict(
            AccountId=account_id,
            Title=j['title'],
            Key=j['key'],
            PrivateKey=private_key,
            PublicKey=public_key,
            Verified=self.j2s.BoolToInt(j['verified']),
            ReadOnly=self.j2s.BoolToInt(j['read_only']),
            CreatedAt=j['created_at'],
        )

    def Update(self, args):
        print('Account.Update')
        print(args)
        print('-u: {0}'.format(args.username))
        print('-p: {0}'.format(args.password))
        print('-m: {0}'.format(args.mailaddress))
        print('-s: {0}'.format(args.ssh_host))
        print('-t: {0}'.format(args.two_factor_secret_key))
        print('-r: {0}'.format(args.two_factor_recovery_code_file_path))
        print('--auto: {0}'.format(args.auto))

    def Delete(self, args):
        print('Account.Delete')
        print(args)
        print('-u: {0}'.format(args.username))
        print('--auto: {0}'.format(args.auto))

    def Tsv(self, args):
        print('Account.Tsv')
        print(args)
        print('path_file_tsv: {0}'.format(args.path_file_tsv))
        print('--method: {0}'.format(args.method))

