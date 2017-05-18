# このソフトウェアについて

起動引数にSSHのホスト名を指定するとGitHubに設定しDBに登録するようにした。

起動引数`-s`で`~/.ssh/config`に設定したHost値を指定すると、`IdentityFile`キーからファイルパスを取得し、キー値を取得する。それをAPIでGitHubに設定する。念の為DBにも登録する。

# 変更箇所

* `/cui/register/Main.py`に該当処理を追加した
* `./cui/register/github/api/v3/users/SshKeys.py`に取得APIを追加した

# 罠になるかもしれない点

* 秘密鍵と公開鍵は同一ディレクトリに存在する必要がある

`IdentityFile`キーからファイルパスを取得する。公開鍵でも秘密鍵でもいいが、もう一方のファイルパスも同一ディレクトリと仮定してパスを取得する。

# 前回まで

* https://github.com/ytyaru/GitHub.Upload.GetMailAddressForAPI.201704041114
* https://github.com/ytyaru/GitHub.Upload.SSH.Check.201704040709
* https://github.com/ytyaru/GitHub.Upload.SSH.key.gen.201704031547
* https://github.com/ytyaru/GitHub.DB.Accounts.Create.Table.SshKeys.201704031424
* https://github.com/ytyaru/GitHub.Upload.UserRegister.Insert.Token.201704031122
* https://github.com/ytyaru/GitHub.Upload.UserRegister.CUI.201703311858
* https://github.com/ytyaru/GitHub.Upload.CUI.Account.SubCommand.201703302040
* https://github.com/ytyaru/GitHub.Upload.Headers.License.201703301853
* https://github.com/ytyaru/GitHub.Upload.Http.Response.201703301533
* https://github.com/ytyaru/GitHub.Upload.Response.201703291452
* https://github.com/ytyaru/GitHub.Upload.Delete.CommentAndFile.201703281815
* https://github.com/ytyaru/GitHub.Upload.Add.CUI.Directory.201703281703
* https://github.com/ytyaru/GitHub.Upload.ByPython.Add.Database.Create.refactoring.GitHubApi.201703280740
* https://github.com/ytyaru/GitHub.Upload.ByPython.Add.Database.Create.refactoring.Pagenation.201703271311
* https://github.com/ytyaru/GitHub.Upload.ByPython.Add.Database.Create.refactoring.Response.201703270700
* https://github.com/ytyaru/GitHub.Upload.ByPython.Add.Database.Create.refactoring.Data.201703261947
* https://github.com/ytyaru/GitHub.Upload.ByPython.Add.Database.Create.Callable.refactoring.201703261352

# 開発環境

* Linux Mint 17.3 MATE 32bit
* [Python 3.4.3](https://www.python.org/downloads/release/python-343/)
* [SQLite](https://www.sqlite.org/) 3.8.2

## WebService

* [GitHub](https://github.com/)
    * [アカウント](https://github.com/join?source=header-home)
    * [AccessToken](https://github.com/settings/tokens)
    * [Two-Factor認証](https://github.com/settings/two_factor_authentication/intro)
    * [API v3](https://developer.github.com/v3/)

# 準備

## GitHubアカウント登録

1. [GitHubアカウント登録ページ](https://github.com/join)にてアカウントを登録する
1. 指定したメールアドレスにGitHubからメールが届くので確認する
1. リンクをクリックしてメールアドレスを`verified`にする

GitHubアカウント登録と有効なメールアドレスの登録が完了した。

## SSH設定

`~/.ssh/config`に対象アカウントの設定をしておく。たとえば以下のように。

```
Host github.com.user1
  User git
  Port 22
  HostName github.com
  IdentityFile /home/mint/.ssh/github/rsa_4096_user1
  TCPKeepAlive yes
  IdentitiesOnly yes
```

# 実行

```sh
$ python3 GitHubUserRegister.py insert -u user1 -p pass -s github.com.user1
```

# 結果

`~/.ssh/config`ファイルから設定を読み込んで以下を行う。

* [GitHubにSSH公開鍵を登録する](https://developer.github.com/v3/users/keys/#create-a-public-key)
* DBに登録する
    * Host
    * 鍵(ファイルパス、鍵の値)
    * ssh-keygen値
        * bits(4096)
        * type(rsa)

`GitHub.Accounts.sqlite3`DBファイルにはSSH秘密鍵まで保存するのでDBの扱いは要注意。いずれどうするか考える。

# クリアした課題

* 同一Hostが`~/.ssh/config`内に定義済みでも追記されてしまう
    * Hostが既存の場合、追記しないようにしたい
        * SSHのconfigファイル編集ツールを作りたい
            * <strong>`SshConfigurator.py`を作成しHost設定値を読み取れるようにした。</strong>
* 利用中アカウントでもDB登録するときに新規生成してしまう。既存のものを使いたいときはどうするか
    * すでにTokenを生成してあるアカウントの場合でも、TokenがDBに存在しないなら作成されてしまう
        * <strong>管理するためには仕方ない</strong>
    * すでにSSH鍵を生成してあるアカウントの場合でも、SSH鍵がDBに存在しないなら作成されてしまう
        * <strong>`SshConfigurator.py`を作成しHost設定値を読み取れるようにした。</strong>

# 課題

* Tokenが多くて邪魔
    A. 現在のように権限別で複数のTokenを作成する
    B. ツールで1つのTokenにし、権限は適時変更しながら使う
* SSH鍵生成時に、任意の値を指定したい
    * 暗号化方式
    * 暗号化強度
* SSHのconfigを編集したい（定義順などきれいに整形したい）
* `/cui/register/Main.py`が汚すぎる

# ライセンス

このソフトウェアはCC0ライセンスである。

[![CC0](http://i.creativecommons.org/p/zero/1.0/88x31.png "CC0")](http://creativecommons.org/publicdomain/zero/1.0/deed.ja)

Library|License|Copyright
-------|-------|---------
[requests](http://requests-docs-ja.readthedocs.io/en/latest/)|[Apache-2.0](https://opensource.org/licenses/Apache-2.0)|[Copyright 2012 Kenneth Reitz](http://requests-docs-ja.readthedocs.io/en/latest/user/intro/#requests)
[dataset](https://dataset.readthedocs.io/en/latest/)|[MIT](https://opensource.org/licenses/MIT)|[Copyright (c) 2013, Open Knowledge Foundation, Friedrich Lindenberg, Gregor Aisch](https://github.com/pudo/dataset/blob/master/LICENSE.txt)
[bs4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)|[MIT](https://opensource.org/licenses/MIT)|[Copyright © 1996-2011 Leonard Richardson](https://pypi.python.org/pypi/beautifulsoup4),[参考](http://tdoc.info/beautifulsoup/)
[pytz](https://github.com/newvem/pytz)|[MIT](https://opensource.org/licenses/MIT)|[Copyright (c) 2003-2005 Stuart Bishop <stuart@stuartbishop.net>](https://github.com/newvem/pytz/blob/master/LICENSE.txt)
[furl](https://github.com/gruns/furl)|[Unlicense](http://unlicense.org/)|[gruns/furl](https://github.com/gruns/furl/blob/master/LICENSE.md)
[PyYAML](https://github.com/yaml/pyyaml)|[MIT](https://opensource.org/licenses/MIT)|[Copyright (c) 2006 Kirill Simonov](https://github.com/yaml/pyyaml/blob/master/LICENSE)

