"""
PostgreSQLのSQLクライアント

SQLを入力し、結果をリストビューで表示する
リストビューは、1行おきに背景色を変え、横スクロールバーを持ち、列幅を自動調節する
"""

from typing import Tuple
import psycopg2
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkFont
import csv
import os
import datetime

class ListView(ttk.Frame):
    """
    SQLの結果をリストビューで表示する
    """
    def __init__(self, master):
        """
        画面の作成
        上のFrame: 入力用
        下のFrame: listviewで出力
        """
        super().__init__(master)
        self.postgres = Postgres()
        self.u_frame = tk.Frame(master, bg="blue")     # 背景色を付けて配置を見る
        self.b_frame = tk.Frame(master, bg="green")    # 背景色を付けて配置を見る
        self.u_frame.pack(fill=tk.X)
        self.b_frame.pack(fill=tk.BOTH, expand=True)
        self.create_input_frame(self.u_frame)
        self.create_tree_frame(self.b_frame)

    def fixed_map(self, option):
        # Fix for setting text colour for Tkinter 8.6.9
        # From: https://core.tcl.tk/tk/info/509cafafae
        #
        # Returns the style map for 'option' with any styles starting with
        # ('!disabled', '!selected', ...) filtered out.

        # style.map() returns an empty list for missing options, so this
        # should be future-safe.
        return [elm for elm in self.style.map('Treeview', query_opt=option) if
            elm[:2] != ('!disabled', '!selected')]

    def create_input_frame(self, parent):
        """
        入力項目の画面の作成
        上段：SQL入力ボックス、実行ボタン、CSV出力チェックボックス
        下段：メッセージ
        """
        self.lbl_sql = tk.Label(parent, text="SQL:")
        self.sql = tk.StringVar(value="select * from customer limit 5")
        self.ety_sql = tk.Entry(parent, textvariable=self.sql)
        self.btn_exe = tk.Button(parent, text="実行", command=self.execute_sql)
        self.var_csv = tk.IntVar(value=0)
        self.ckb_csv = tk.Checkbutton(parent, text="CSV出力", variable=self.var_csv)
        self.msg = tk.StringVar(value="msg")
        self.lbl_msg = tk.Label(parent
                                , textvariable=self.msg
                                , justify=tk.LEFT
                                , font=("Fixedsys", 11)
                                , relief=tk.RIDGE
                                , anchor=tk.W)
        self.lbl_msg.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)    #先にpackしないと下に配置されない
        self.lbl_sql.pack(side=tk.LEFT, fill=tk.BOTH)
        self.ety_sql.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.ckb_csv.pack(side=tk.RIGHT, fill=tk.Y)
        self.btn_exe.pack(side=tk.RIGHT)
        self.ety_sql.bind("<Return>", self.execute_sql)     #Enterキーを押しても動作するように

    def create_tree_frame(self, parent):
        """
        Treeviewとスクロールバーをparentに作成する。
        Treeviewは、listview形式、行は縞模様
        Args:
            tk.Frame:   親frame
        """
        # tagを有効にするためstyleを更新 tkinter8.6?以降必要みたい
        # 表の文字色、背景色の設定に必要
        self.style = ttk.Style()
        self.style.map('Treeview', foreground=self.fixed_map('foreground')
                                 , background=self.fixed_map('background'))
        # Treeviewの作成
        self.tree = ttk.Treeview(parent)
        self.tree["show"] = "headings"      # listview形式の指定
        self.tree.tag_configure("odd", background="ivory2")
        # スクロールバーの作成
        self.hscrlbar = tk.Scrollbar(parent, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(xscrollcommand=self.hscrlbar.set)
        # pack 横一杯にする方を先にpackしないと見えなくなる
        self.hscrlbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)

    def update_tree_column(self, columns):
        """
        TreeViewの列定義(見出し)を設定
        見出しの文字長で列幅を初期設定
        Args:
            list:       列名のリスト
        """
        self.tree["columns"] = columns                  # treeviewの列定義を設定
        font1 = tkFont.Font()
        for col_name in columns:
            self.tree.heading(col_name, text=col_name)  # 見出しの設定
            width1 = font1.measure(col_name) + 10       # 見出しの文字幅をピクセルで取得
            self.tree.column(col_name, width=width1)    # 見出し幅の設定

    def update_tree_by_result(self, rows:list):
        """
        rowsをTreeViewに設定
        Args:
            list:    SQL実行結果セット
        """
        # 要素の長さにより列幅を修正
        if not rows:    # 要素が無ければ戻る
            return
        font1 = tkFont.Font()
        for i, _ in enumerate(rows[0]):
            # 同じ列のデータをリストにし列の値の長さを求め、最大となる列のデータを求める。
            # 値は数字もあるので文字に変換し長さを求める。
            max_str = max([x[i] for x in rows], key=lambda x:len(str(x)))
            width1 = font1.measure(max_str) + 10   # 見出しの文字幅をピクセルで取得
            header1 = self.tree.column(self.tree['columns'][i], width=None) # 現在の幅
            if width1 > header1:
                self.tree.column(self.tree['columns'][i], width=width1)    # 見出し幅の再設定
        # treeviewに要素追加。背景はtagを切り替えて設定
        self.tree.delete(*self.tree.get_children())    # Treeviewをクリア
        for i, row in enumerate(rows):
            _tags = []              # tag設定値の初期化
            if i & 1:               # 奇数か? i % 2 == 1:
                _tags.append("odd") # 奇数番目(treeviewは0始まりなので偶数行)だけ背景色を変える(oddタグを設定)
            self.tree.insert("", tk.END, values=row, tags=_tags)

    def execute_sql(self, event=None):
        """
        SQLの実行
        """
        sql1 = self.ety_sql.get()   # SQL文字列を取得
        # SQLの実行。戻り値として、見出し、結果セット、エラーメッセージが返る。
        self.columns, self.rows, _msg = self.postgres.exe_sql(sql1, self.var_csv.get())
        # エラーメッセージを画面に設定
        self.msg.set(_msg)
        # 見出しをtreeviewに追加
        self.update_tree_column(self.columns)
        # 結果セットをtreeviewに追加
        self.update_tree_by_result(self.rows)

class Postgres():
    """
    PostgreSQLにコネクトしてSQLを発行し結果を得る
    """
    KEY_DBNAME = "py_sqlc_dbname"
    KEY_USER = "py_sqlc_user"
    KEY_PASS = "py_sqlc_pass"
    KEY_PORT = "py_sqlc_port"

    def get_auth_info(self) -> Tuple[str, str, str, str]:
        """
        環境変数を読んで値を返す
        Returns:
            str:    データベース名
            str:    ユーザー名
            str:    パスワード
            str:    ポート
        """
        dbname1 = os.getenv(self.KEY_DBNAME)
        user1 = os.getenv(self.KEY_USER)
        pass1 = os.getenv(self.KEY_PASS)
        port1 = os.getenv(self.KEY_PORT)
        return dbname1, user1, pass1, port1

    def get_connection(self):
        """
        PostgreSQLに接続
        Returns:
            psycopg2.connection:    コネクション
        """
        dbname1, user1, pass1, port1 = self.get_auth_info()
        conn = psycopg2.connect(
        dbname=dbname1
        , user=user1
        , password=pass1
        , port=port1)
        return conn

    def exe_sql(self, sql:str, w_csv:bool) -> Tuple[list, list, str]:
        """sqlを実行し、結果を返す
        Args:
            str:    SQL文字列
            bool:   CSV出力する(true:出力、false:未出力)
        Returns:
            list:   カラム定義
            list:   結果セット
            str:    エラーメッセージ(空文はエラーなし)
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    _msg = ""
                    cur.execute(sql)        # SQLの実行
                    rows = cur.fetchall()   # 結果セットの取得。タプルのリストで返る
                    columns = [desc.name for desc in cur.description]   # descriptionのname要素がカラム名
                    if w_csv:
                        CsvManage().write_csv(columns, rows)    # CSV作成
                    return columns, rows, _msg
        except psycopg2.DatabaseError as e:
            print("DB error", e)
            _msg = e
        except Exception as e:
            print("例外エラー", e)
            _msg = e
        return [], [], _msg

class CsvManage():
    """
    CSV出力の管理
    """
    def __init__(self):
        pass

    def write_csv(self, header:list, rows:list):
        """
        csvファイルにrowsを出力
        ファイル名は「sql_月日_時分_秒.csv」
        """
        try:
            csv_path = f'sql_{datetime.datetime.now().strftime("%m%d_%H%M_%S")}.csv'

            with open(csv_path, encoding="utf_8", mode="w", newline="") as f:
                _writer = csv.writer(f)
                _writer.writerow(header)
                _writer.writerows(rows)
        except Exception as e:
            print("CSVエラー", e)

if __name__ == '__main__':
    root = tk.Tk()  #トップレベルウィンドウの作成
    root.title("SQL cilent")    #タイトル
    root.geometry("600x600")    #サイズ
    listview = ListView(root)
    root.mainloop()
