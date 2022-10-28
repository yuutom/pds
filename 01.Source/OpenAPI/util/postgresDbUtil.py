from logging import Logger
import psycopg2
import psycopg2.extras
import boto3
import traceback


class PostgresDbUtilClass():
    def __init__(self, logger, end_point: str, port: int, user_name: str, password: str, region: str):
        """
        初期処理

        Args:
            endPoint (str): DBエンドポイント
            port (int): DBポート番号
            userName (str): DBユーザ名
            region (str): リージョン
        """
        self.logger: Logger = logger

        self.client = boto3.client(
            service_name='rds'
        )
        self.end_point = end_point
        self.port = port
        self.user_name = user_name
        self.region = region
        self.password = password
        self.token = self.client.generate_db_auth_token(DBHostname=end_point, Port=port, DBUsername=user_name, Region=region)

    ### ベース関数
    def create_connection(self, db_name: str):
        """
        DBコネクション作成

        Args:
            dbName (str): 接続先DB名

        Returns:
            Object: DBコネクションオブジェクト
        """
        return psycopg2.connect(host=self.end_point, port=self.port, database=db_name, user=self.user_name, password=self.password, sslrootcert="SSLCERTIFICATE")

    def close_connection(self, conn):
        """
        DBコネクション削除

        Args:
            conn (Object): DBコネクションオブジェクト
        """
        conn.close()

    def commit_transaction(self, conn):
        """
        トランザクションコミット処理

        Args:
            conn (Object): DBコネクションオブジェクト
        """
        conn.commit()

    def rollback_transaction(self, conn):
        """
        トランザクションロールバック処理

        Args:
            conn (Object): DBコネクションオブジェクト
        """
        try:
            conn.rollback()
            return {
                "result": True
            }
        except psycopg2.Error as e:
            return {
                "result": False,
                "errorObject": e,
                "stackTrace": traceback.format_exc()
            }
        except Exception as e:
            return {
                "result": False,
                "errorObject": e,
                "stackTrace": traceback.format_exc()
            }

    def execute_query(self, conn, query: str, *param: tuple):
        """
        クエリ実行

        Args:
            conn (Object): DBコネクションオブジェクト
            query (str): クエリ
        """
        cur = conn.cursor()
        cur.execute(query, param)
        cur.close()

    def execute_many_query(self, conn, query: str, param_list: list):
        """
        クエリ実行(複数)

        Args:
            conn (Object): DBコネクションオブジェクト
            query (str): クエリ
        """
        cur = conn.cursor()
        cur.executemany(query, param_list)
        cur.close()

    def select_tuple_list(self, conn, query: str, *param: tuple):
        """
        検索処理

        クエリ実行結果はタプルのリストで返却

        Args:
            dbName (str): 接続先DB名
            query (str): クエリ

        Returns:
            dict: 検索結果（タプルのリスト）
        """
        try:
            cur = conn.cursor()
            cur.execute(query, param)
            row_count = cur.rowcount
            query_results = cur.fetchall()
            cur.close()
            return {
                "result": True,
                "rowCount": row_count,
                "query_results": query_results
            }

        except Exception as e:
            return {
                "result": False,
                "errorObject": e,
                "stackTrace": traceback.format_exc()
            }

    def select_tuple_one(self, conn, query: str, *param: tuple):
        """
        検索処理

        検索結果はタプルで返却

        Args:
            dbName (str): 接続先DB名
            query (str): クエリ

        Returns:
            dict: 検索結果（タプル）
        """
        try:
            cur = conn.cursor()
            cur.execute(query, param)
            row_count = cur.rowcount
            query_results = cur.fetchone()
            cur.close()
            return {
                "result": True,
                "rowcount": row_count,
                "query_results": query_results
            }

        except Exception as e:
            return {
                "result": False,
                "errorObject": e,
                "stackTrace": traceback.format_exc()
            }

    def insert(self, conn, query: str, *param: tuple):
        """
        登録処理

        Args:
            dbName (str): 接続先DB名
            query (str): クエリ
        """
        try:
            self.execute_query(conn, query, *param)
            return {
                "result": True
            }
        except psycopg2.Error as e:
            return {
                "result": False,
                "errorObject": e,
                "stackTrace": traceback.format_exc()
            }
        except Exception as e:
            return {
                "result": False,
                "errorObject": e,
                "stackTrace": traceback.format_exc()
            }

    def bulk_insert(self, conn, query: str, param_list: list):
        """
        バルクインサート処理

        Args:
            dbName (str): 接続先DB名
            query (str): クエリ
        """
        try:
            self.execute_many_query(conn, query, param_list)
            return {
                "result": True
            }
        except psycopg2.Error as e:
            return {
                "result": False,
                "errorObject": e,
                "stackTrace": traceback.format_exc()
            }
        except Exception as e:
            return {
                "result": False,
                "errorObject": e,
                "stackTrace": traceback.format_exc()
            }

    def update(self, conn, query: str, *param: tuple):
        """
        更新処理

        Args:
            dbName (str): 接続先DB名
            query (str): クエリ
        """
        try:
            self.execute_query(conn, query, *param)
            return {
                "result": True
            }

        except psycopg2.Error as e:
            return {
                "result": False,
                "errorObject": e,
                "stackTrace": traceback.format_exc()
            }
        except Exception as e:
            return {
                "result": False,
                "errorObject": e,
                "stackTrace": traceback.format_exc()
            }

    def delete(self, conn, query: str, *param: tuple):
        """
        削除処理

        Args:
            dbName (str): 接続先DB名
            query (str): クエリ
        """
        try:
            self.execute_query(conn, query, *param)
            return {
                "result": True
            }
        except psycopg2.Error as e:
            return {
                "result": False,
                "errorObject": e,
                "stackTrace": traceback.format_exc()
            }
        except Exception as e:
            return {
                "result": False,
                "errorObject": e,
                "stackTrace": traceback.format_exc()
            }
