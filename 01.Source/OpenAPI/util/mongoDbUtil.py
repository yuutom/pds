from logging import Logger
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.client_session import ClientSession
from bson.objectid import ObjectId

from const.systemConst import SystemConstClass


class MongoDbClass():
    def __init__(self, logger):
        self.logger: Logger = logger
        self.session: ClientSession = None
        self.db: ClientSession

    def connect_mongo(self, host: str, port: int):
        """
        MongoDB接続

        Args:
            host (str): 接続ホスト名
            port (int): ポート番号
        """
        self.client = MongoClient(host, port, serverSelectionTimeoutMS=5000, socketTimeoutMS=None, connect=False, maxPoolsize=1, directConnection=True)

    def connect_db(self, db_name: str):
        """
        指定データベース接続
        ※指定のDBがない場合は作成する

        Args:
            db_name (str): DB名
        """
        self.db = self.client[db_name]

    def connect_collection(self, collection_name: str):
        """
        指定コレクション接続
        ※指定のコレクションがない場合は作成する

        Args:
            collection_name (str): コレクション名
        """
        self.collection = self.db[collection_name]

    def close_mongo(self):
        self.client.close()

    def create_session(self):
        self.session = self.client.start_session()

    def close_session(self):
        self.session.end_session()

    def create_transaction(self):
        self.session.start_transaction()

    def commit_transaction(self):
        if self.session is not None:
            self.session.commit_transaction()

    def rollback_transaction(self):
        try:
            self.session.abort_transaction()
            return {
                "result": True
            }
        except PyMongoError as e:
            if hasattr(e, "code"):
                return {
                    "result": False,
                    "errorCode": e.code,
                    "message": e._message
                }
            else:
                return {
                    "result": False,
                    "errorCode": "",
                    "message": e._message
                }
        except Exception as e:
            raise e

    def get_status(self):
        return self.client.admin.command("replSetGetStatus")

    def find_one_object_id(self, object_id: str):
        """
        オブジェクトID検索

        Args:
            object_id (str): オブジェクトID

        Returns:
            dict: 処理結果
        """
        try:
            search_result = self.collection.find_one({"_id": ObjectId(object_id)})
            return {
                "result": True,
                "search_result": search_result
            }
        except PyMongoError as e:
            if hasattr(e, "code"):
                return {
                    "result": False,
                    "errorCode": e.code,
                    "message": e._message
                }
            else:
                return {
                    "result": False,
                    "errorCode": "",
                    "message": e._message
                }
        except Exception as e:
            raise e

    def find_filter(
        self,
        key: str,
        value: str,
        match_mode: str
    ):
        """
        検索

        Args:
            key (str): 検索キー
            value (str): 検索値
            match_mode (str): 検索条件

        Returns:
            list: objectIDリスト
        """
        try:
            objectIdList = []
            if match_mode == SystemConstClass.MATCH_MODE["PREFIX"]:
                docs = self.collection.find(filter={key: {'$regex': '^' + value}})
            elif match_mode == SystemConstClass.MATCH_MODE["BACKWARD"]:
                docs = self.collection.find(filter={key: {'$regex': value + '$'}})
            elif match_mode == SystemConstClass.MATCH_MODE["PARTIAL"]:
                docs = self.collection.find(filter={key: {'$regex': value}})

            for doc in docs:
                objectIdList.append(str(doc["_id"]))
            return {
                "result": True,
                "objectIdList": objectIdList
            }
        except PyMongoError as e:
            if hasattr(e, "code"):
                return {
                    "result": False,
                    "errorCode": e.code,
                    "message": e._message
                }
            else:
                return {
                    "result": False,
                    "errorCode": "",
                    "message": e._message
                }
        except Exception as e:
            raise e

    def find_all(self):
        """
        ドキュメント全件取得
        """
        try:
            return self.collection.find()
        except PyMongoError as e:
            if hasattr(e, "code"):
                return {
                    "result": False,
                    "errorCode": e.code,
                    "message": e._message
                }
            else:
                return {
                    "result": False,
                    "errorCode": "",
                    "message": e._message
                }
        except Exception as e:
            raise e

    def insert_document(self, data: dict):
        try:
            insert_data = data.copy()
            result = self.collection.insert_one(insert_data, session=self.session)
            return {
                "result": True,
                "objectId": str(result.inserted_id)
            }
        except PyMongoError as e:
            if hasattr(e, "code"):
                return {
                    "result": False,
                    "errorCode": e.code,
                    "message": e._message
                }
            else:
                return {
                    "result": False,
                    "errorCode": "",
                    "message": e._message
                }
        except Exception as e:
            raise e

    def delete_object_id(self, object_id: str):
        """
        MongoDB削除処理

        Args:
            object_id (str): オブジェクトID

        Returns:
            処理結果
        """
        try:
            self.collection.delete_one({"_id": ObjectId(object_id)})
            return {
                "result": True
            }
        except PyMongoError as e:
            if hasattr(e, "code"):
                return {
                    "result": False,
                    "errorCode": e.code,
                    "message": e._message
                }
            else:
                return {
                    "result": False,
                    "errorCode": "",
                    "message": e._message
                }
        except Exception as e:
            raise e

    def create_replica_set(
        self,
        rep0_host,
        rep0_port,
        rep1_host,
        rep1_port,
        rep2_host,
        rep2_port,
        rep3_host,
        rep3_port
    ):
        """
        レプリカセット作成

        Args:
            rep0_host (str): レプリカセット登録ホスト
            rep0_port (str): レプリカセット登録ポート
            rep1_host (str): レプリカセット登録ホスト
            rep1_port (str): レプリカセット登録ポート
            rep2_host (str): レプリカセット登録ホスト
            rep2_port (str): レプリカセット登録ポート
            rep3_host (str): レプリカセット登録ホスト
            rep3_port (str): レプリカセット登録ポート

        Returns:
            _type_: _description_
        """
        try:
            # 01.レプリカセットコンフィグ作成
            config = {
                '_id': 'rs0',
                'version': 1,
                'members': [
                    {'_id': 0, 'host': rep0_host + ":" + str(rep0_port)},
                    {'_id': 1, 'host': rep1_host + ":" + str(rep1_port)},
                    {'_id': 2, 'host': rep2_host + ":" + str(rep2_port)},
                    {'_id': 3, 'host': rep3_host + ":" + str(rep3_port)}
                ]
            }
            # 02.レプリカセットコード実行
            self.client.admin.command("replSetInitiate", config)
            return {
                "result": True
            }
        except PyMongoError as e:
            if hasattr(e, "code"):
                return {
                    "result": False,
                    "errorCode": e.code,
                    "message": e._message
                }
            else:
                return {
                    "result": False,
                    "errorCode": "",
                    "message": e._message
                }
        except Exception as e:
            raise e
