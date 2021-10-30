# Python-SQL-Client
PostgreSQLのSQL Client

## 概要 Description
PostgreSQLのSQLクライアント  
SQL client for PostgreSQL

SQLを入力し、結果をリストビューで表示する  
Enter SQL and display the result in list view 

## 特徴 Features

- TkinterのTreeviewを使用  
	Use Treeview in Tkinter 
- １行おきに背景色を変える  
	Change the background color every other line  
- 列の幅を自動調整  
	Automatically adjust column width  
- 横スクロールバーを表示  
	Show horizontal scroll bar  

## 依存関係 Requirement

- Python 3.8.5  
- psycopg2 2.8.6  
- PostgreSQL 11.8  

## 使い方 Usage

- 環境変数に接続情報を登録してください  
	- py_sqlc_dbname=データベース名  
	- py_sqlc_user=ユーザー名  
	- py_sqlc_pass=パスワード  
	- py_sqlc_port=ポート  

```dosbatch
	postgreSQL_client.exe
```

## インストール方法 Installation

- pip install psycopg2  
- PostgreSQLについては、[日本PostgreSQLユーザ会 | 日本PostgreSQLユーザ会](https://www.postgresql.jp/)を参照  

## プログラムの説明サイト Program description site

[SQLクライアントアプリの作り方(Tkinter-Treeview)【Python】 - プログラムでおかえしできるかな](https://juu7g.hatenablog.com/entry/Python/sql/client)  

## 作者 Authors
juu7g

## ライセンス License
このソフトウェアは、MITライセンスのもとで公開されています。LICENSE.txtを確認してください。  
This software is released under the MIT License, see LICENSE.txt.

