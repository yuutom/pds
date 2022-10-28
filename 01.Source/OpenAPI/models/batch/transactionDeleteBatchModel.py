import traceback
import asyncio
# util
from util.postgresDbUtil import PostgresDbUtilClass
from util.commonUtil import CommonUtilClass
from util.s3Util import s3UtilClass
import util.logUtil as logUtil
from util.callbackExecutorUtil import CallbackExecutor
from util.mongoDbUtil import MongoDbClass
# const
from const.messageConst import MessageConstClass
from const.sqlConst import SqlConstClass
# Exception
from exceptionClass.PDSException import PDSException


class transactionDeleteBatchModelClass():
    def __init__(self, logger):
        """
        コンストラクタ

        Args:
            logger (Logger): ロガー（TRACE）
        """
        self.logger = logger
        self.common_util = CommonUtilClass(logger)
        self.error_info = None

    async def main(self, pds_user_id, transaction_id):
        """
        個人情報削除バッチ メイン処理

        Args:
            pds_user_id (str): PDSユーザID
            transaction_id (str): トランザクションID

        """
        try:
            # 03.共通DB接続準備処理
            # 03-01.共通DB接続情報取得処理
            # 03-01-01.AWS SecretsManagerから共通DB接続情報を取得して、「変数．共通DB接続情報」に格納する
            common_db_connection_resource: PostgresDbUtilClass = None
            # 03-02.「変数．共通DB接続情報」を利用して、共通DBに対してのコネクションを作成する
            common_db_info_response = self.common_util.get_common_db_info_and_connection()
            if not common_db_info_response["result"]:
                return common_db_info_response
            else:
                common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
                common_db_connection = common_db_info_response["common_db_connection"]

            # 04.PDSユーザデータ取得処理
            # 04-01.PDSユーザテーブルからデータを取得し、「変数．PDSユーザ情報」に1レコードをタプルとして格納する
            pds_user_result = common_db_connection_resource.select_tuple_one(
                common_db_connection,
                SqlConstClass.TRANSACTION_DELETE_PDS_USER_SELECT_SQL,
                pds_user_id
            )
            # 04-02.「変数．PDSユーザ情報」が0件の場合、「変数．エラー情報」を作成する
            if pds_user_result["result"] and pds_user_result["rowcount"] == 0:
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020004"]["logMessage"], pds_user_id))
                self.error_info = {
                    "errorCode": "020004",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020004"]["message"], pds_user_id)
                }
            # 04-03.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not pds_user_result["result"]:
                self.error_info = self.common_util.create_postgresql_log(
                    pds_user_result["errorObject"],
                    None,
                    None,
                    pds_user_result["stackTrace"]
                ).get("errorInfo")

            # 05.共通エラーチェック処理
            # 05-01 以下の引数で共通エラーチェック処理を実行する
            # 05-02 例外が発生した場合、例外処理に遷移
            if self.error_info is not None:
                self.common_util.common_error_check(self.error_info)

            # 06.PDSユーザDB接続準備処理
            # 06-01.以下の引数でPDSユーザDBの接続情報をAWSのSecrets Managerから取得する
            # 06-02.取得したPDSユーザDBの接続情報を、「変数．PDSユーザDB接続情報」に格納する
            # 06-03.「変数．PDSユーザDB接続情報」を利用して、PDSユーザDBに対してのコネクションを作成する
            rds_db_secret_name = pds_user_result["query_results"][0]
            pds_user_db_info_response = self.common_util.get_pds_user_db_info_and_connection(rds_db_secret_name)
            if not pds_user_db_info_response["result"]:
                return pds_user_db_info_response
            else:
                self.pds_user_db_connection_resource = pds_user_db_info_response["pds_user_db_connection_resource"]
                self.pds_user_db_connection = pds_user_db_info_response["pds_user_db_connection"]

            # 07.個人情報削除対象データ一括取得処理
            # 07-01.個人情報テーブル、バイナリデータテーブル、バイナリ分割テーブルを結合したテーブルからデータを取得し、「変数．個人情報削除対象データリスト」に全レコードをタプルのリストとして格納する
            data_to_delete_select_result = self.pds_user_db_connection_resource.select_tuple_list(
                self.pds_user_db_connection,
                SqlConstClass.TRANSACTION_DELETE_DATA_TO_DELETE_SELECT_SQL,
                transaction_id,
                transaction_id
            )
            # 07-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not data_to_delete_select_result["result"]:
                self.error_info = self.common_util.create_postgresql_log(
                    data_to_delete_select_result["errorObject"],
                    None,
                    None,
                    data_to_delete_select_result["stackTrace"]
                ).get("errorInfo")

            # 08.共通エラーチェック処理
            # 08-01.以下の引数で共通エラーチェック処理を実行する
            # 08-02.例外が発生した場合、例外処理に遷移
            if self.error_info is not None:
                self.common_util.common_error_check(self.error_info)

            # 09.削除対象リスト作成処理
            # 09-01.以下の引数で削除対象リスト作成処理を実行する
            data_to_delete_dict = {
                "transaction_id_list": None,
                "user_profile_valid_flg_list": None,
                "json_data_flg_list": None,
                "save_data_mongodb_key_list": None,
                "save_image_idx_list": None,
                "save_image_data_id_list": None,
                "user_profile_binary_valid_flg_list": None,
                "file_save_path_list": None
            }
            transaction_id_list = [t[0] for t in data_to_delete_select_result["query_results"]]
            user_profile_valid_flg_list = [t[1] for t in data_to_delete_select_result["query_results"]]
            json_data_flg_list = [t[2] for t in data_to_delete_select_result["query_results"]]
            save_data_mongodb_key_list = [t[3] for t in data_to_delete_select_result["query_results"]]
            save_image_idx_list = [t[4] for t in data_to_delete_select_result["query_results"]]
            save_image_data_id_list = [t[5] for t in data_to_delete_select_result["query_results"]]
            user_profile_binary_valid_flg_list = [t[6] for t in data_to_delete_select_result["query_results"]]
            file_save_path_list = [t[7] for t in data_to_delete_select_result["query_results"]]

            data_to_delete_dict["transaction_id_list"] = transaction_id_list
            data_to_delete_dict["user_profile_valid_flg_list"] = user_profile_valid_flg_list
            data_to_delete_dict["json_data_flg_list"] = json_data_flg_list
            data_to_delete_dict["save_data_mongodb_key_list"] = save_data_mongodb_key_list
            data_to_delete_dict["save_image_idx_list"] = save_image_idx_list
            data_to_delete_dict["save_image_data_id_list"] = save_image_data_id_list
            data_to_delete_dict["user_profile_binary_valid_flg_list"] = user_profile_binary_valid_flg_list
            data_to_delete_dict["file_save_path_list"] = file_save_path_list

            # 09-02.レスポンスを「変数．削除対象リスト作成処理結果」に格納する
            data_to_delete_list_create_result = self.data_to_delete_list_create(data_to_delete_dict)

            # 10.分割バイナリファイル削除処理リスト初期化処理
            # 10-01.「変数．分割バイナリファイル削除処理リスト」を空のリストで作成する
            split_binary_file_delete_list = []

            for binary_file_delete_loop, user_profile_binary_data_to_delete_element in enumerate(data_to_delete_list_create_result["save_image_idx_list"]):
                # 11.S3ファイル削除処理
                # 11-01.「変数．分割バイナリファイル削除処理リスト」に分割バイナリファイル削除処理を追加する
                split_binary_file_delete_list.append(self.split_binary_file_delete(data_to_delete_list_create_result["file_save_path_list"][binary_file_delete_loop], pds_user_result["query_results"][1]))

            # 12.分割バイナリファイル削除処理実行処理
            # 12-01.「変数．分割バイナリファイル削除処理リスト」もとに、分割バイナリファイル削除処理を並列で実行する
            # 12-02.レスポンスを「変数．分割バイナリファイル削除処理実行結果リスト」に格納する
            split_binary_file_delete_result_list = await asyncio.gather(*split_binary_file_delete_list)

            split_binary_file_delete_error_info = None
            result_list = [d.get("result") for d in split_binary_file_delete_result_list]
            if False in result_list:
                for result_info in split_binary_file_delete_result_list:
                    if result_info.get("errorInfo"):
                        split_binary_file_delete_error_info = result_info.get("errorInfo")

            # 13.共通エラーチェック処理
            # 13-01.以下の引数で共通エラーチェック処理を実行する
            # 13-02.例外が発生した場合、例外処理に遷移
            if split_binary_file_delete_error_info is not None:
                self.common_util.common_error_check(split_binary_file_delete_error_info)

            # 14.トランザクション作成処理
            # 14-01.「個人情報削除トランザクション」を作成する

            # 15.個人情報バイナリ分割データ削除処理
            # 15-01.削除条件を満たすデータを個人情報バイナリ分割データテーブルから削除する
            user_profile_binary_split_delete_result = self.pds_user_db_connection_resource.delete(
                self.pds_user_db_connection,
                SqlConstClass.TRANSACTION_DELETE_BINARY_SPLIT_DELETE_SQL,
                tuple(data_to_delete_dict["save_image_data_id_list"])
            )
            # 15-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not user_profile_binary_split_delete_result["result"]:
                self.error_info = self.common_util.create_postgresql_log(
                    user_profile_binary_split_delete_result["errorObject"],
                    None,
                    None,
                    user_profile_binary_split_delete_result["stackTrace"]
                ).get("errorInfo")

            # 16.共通エラーチェック処理
            # 16-01.以下の引数で共通エラーチェック処理を実行する
            # 16-02.例外が発生した場合、例外処理に遷移
            if self.error_info is not None:
                # ロールバック処理
                rollback_transaction = CallbackExecutor(
                    self.common_util.common_check_postgres_rollback,
                    self.pds_user_db_connection,
                    self.pds_user_db_connection_resource
                )
                self.common_util.common_error_check(
                    self.error_info,
                    rollback_transaction
                )

            # 17.個人情報バイナリデータ削除処理
            # 17-01.削除条件を満たすデータを個人情報バイナリデータテーブルから削除する
            user_profile_binary_delete_result = self.pds_user_db_connection_resource.delete(
                self.pds_user_db_connection,
                SqlConstClass.TRANSACTION_DELETE_BINARY_DELETE_SQL,
                transaction_id,
                tuple(data_to_delete_dict["save_image_idx_list"])
            )
            # 17-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not user_profile_binary_delete_result["result"]:
                self.error_info = self.common_util.create_postgresql_log(
                    user_profile_binary_delete_result["errorObject"],
                    None,
                    None,
                    user_profile_binary_delete_result["stackTrace"]
                ).get("errorInfo")

            # 18.共通エラーチェック処理
            # 18-01.以下の引数で共通エラーチェック処理を実行する
            if self.error_info is not None:
                # ロールバック処理
                rollback_transaction = CallbackExecutor(
                    self.common_util.common_check_postgres_rollback,
                    self.pds_user_db_connection,
                    self.pds_user_db_connection_resource
                )
                self.common_util.common_error_check(
                    self.error_info,
                    rollback_transaction
                )

            # 19.個人情報削除判定処理
            pds_user_column_list = [
                "pds_user_instance_secret_name",
                "s3_image_data_bucket_name",
                "tokyo_a_mongodb_secret_name",
                "tokyo_c_mongodb_secret_name",
                "osaka_a_mongodb_secret_name",
                "osaka_c_mongodb_secret_name"
            ]
            pds_user_dict = {column: data for column, data in zip(pds_user_column_list, pds_user_result["query_results"])}
            # 19-01.「変数．個人情報削除対象データ[個人情報有効フラグ][0]」がfalseの場合、「20.個人情報削除処理」に遷移する
            # 19-02.「変数．個人情報削除対象データ[個人情報有効フラグ][0]」がtrueの場合、「21.トランザクションコミット処理」に遷移する
            if not data_to_delete_dict["user_profile_valid_flg_list"][0]:
                # 20.個人情報削除処理
                # 20-01.以下の引数で個人情報削除処理を実行する
                self.user_profile_delete(transaction_id, data_to_delete_list_create_result["mongo_db_delete_flg"], data_to_delete_list_create_result["mongo_db_delete_data_key"], pds_user_dict)

            # 21.トランザクションコミット処理
            # 21-01.「個人情報削除トランザクション」をコミットする
            self.pds_user_db_connection_resource.commit_transaction(self.pds_user_db_connection)
            self.pds_user_db_connection_resource.close_connection(self.pds_user_db_connection)

            return {
                "result": True
            }

        # 例外処理(PDSException)
        except PDSException as e:
            raise e

        # 例外処理
        except Exception as e:
            self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["999999"]["logMessage"], str(e), traceback.format_exc()))
            raise PDSException(
                {
                    "errorCode": "999999",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
                }
            )

    def data_to_delete_list_create(self, data_to_delete_list: object):
        """
        削除対象リスト作成処理

        Args:
            data_to_delete_list (object): 個人情報削除対象データ
             transaction_id_list (list): 個人情報．トランザクションID
             user_profile_valid_flg_list (list): 個人情報．有効フラグ
             json_data_flg_list (list): 個人情報．Jsonデータフラグ
             save_data_mongodb_key_list (list): 個人情報．データ格納用Mongoデータキー
             save_image_idx_list (list): 個人情報バイナリデータ．保存画像インデックス
             save_image_data_id_list (list): 個人情報バイナリデータ．保存画像データID
             user_profile_binary_valid_flg_list (list): 個人情報バイナリデータ．有効フラグ
             file_save_path_list (list): 個人情報バイナリ分割データ．保存先パス

        Returns:
            result (bool): 処理結果
            file_save_path_list (list): 保存パスリスト
            save_image_data_id_list (list): 保存画像データIDリスト
            user_profile_binary_data_to_delete_list (list): 個人情報バイナリデータ削除対象リスト
            mongo_db_delete_flg (bool): MongoDBデータ削除フラグ
            mongo_db_delete_data_key (string): MongoDBデータ削除対象データキー
        """
        try:
            # 01.個人情報削除情報作成処理
            # 01-01.「引数．個人情報削除対象データ．Jsonデータフラグ[0]」を「変数．MongoDBデータ削除フラグ」に格納する
            mongo_db_delete_flg = data_to_delete_list["json_data_flg_list"][0]
            # 01-02.「引数．個人情報削除対象データ．データ格納用Mongoデータキーリスト[0]」を「変数．MongoDBデータ削除対象データキー」に格納する
            mongo_db_delete_data_key = data_to_delete_list["save_data_mongodb_key_list"][0]

            # 02.削除対象データリスト作成処理
            # 02-01.「引数．個人情報削除対象データ．保存先パスリスト」を、「変数．保存パスリスト」に格納する
            file_save_path_list = data_to_delete_list["file_save_path_list"]
            # 02-02.「引数．個人情報削除対象データ．保存画像データIDリスト」から重複した値を取り除き、「変数．保存画像データIDリスト」に格納する
            save_image_data_id_list = set(data_to_delete_list["save_image_data_id_list"])
            # 02-03.「引数．個人情報削除対象データ．保存画像インデックスリスト」から重複した値を取り除き、「変数．保存画像インデックスリスト」に格納する
            save_image_idx_list = set(data_to_delete_list["save_image_idx_list"])

            # 03.終了処理
            # 03-01.レスポンス情報を作成し、返却する
            return {
                "result": True,
                "file_save_path_list": file_save_path_list,
                "save_image_data_id_list": save_image_data_id_list,
                "save_image_idx_list": save_image_idx_list,
                "mongo_db_delete_flg": mongo_db_delete_flg,
                "mongo_db_delete_data_key": mongo_db_delete_data_key
            }

        # 例外処理(PDSException)
        except PDSException as e:
            raise e

        # 例外処理
        except Exception as e:
            self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["999999"]["logMessage"], str(e), traceback.format_exc()))
            raise PDSException(
                {
                    "errorCode": "999999",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
                }
            )

    async def split_binary_file_delete(self, s3_data_to_delete: str, bucket_name: str):
        """
        分割バイナリファイル削除処理

        Args:
            s3_data_to_delete (str): S3削除対象

        Returns:
            result (bool): 処理結果
            error_info (object); エラー情報

        """
        try:
            s3_util = s3UtilClass(self.logger, bucket_name)
            for delete_count in range(5):
                # 01.S3のファイル削除処理
                # 01-01.キー名に「引数．S3削除対象」を指定してS3（バケット名：引数．バケット名）から削除する
                delete_file_result = s3_util.deleteFile(s3_data_to_delete)
                if delete_file_result:
                    break
            # 01-02.処理が失敗した場合は「変数．エラー情報」を作成し、エラーログをCloudWatchにログ出力する
            delete_file_error_info = None
            if not delete_file_result:
                # 01-02-01.S3のファイル削除に失敗した場合、「変数．エラー情報」にエラー情報を追加する
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990022"]["logMessage"]))
                delete_file_error_info = {
                    "errorCode": "990022",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["990022"]["message"], "990022")
                }

            # 02.S3のファイル削除チェック処理
            # 02-01.「変数．エラー情報」がNullの場合、「03.S3のファイル削除エラー処理」に遷移する
            # 02-02.「変数．エラー情報」がNullの場合、「04.終了処理」に遷移する
            if delete_file_error_info is not None:
                # 03.S3のファイル削除エラー処理
                # 03-01.返却パラメータを作成し、返却する
                return {
                    "result": False,
                    "errorInfo": delete_file_error_info
                }

            # 04.終了処理
            # 04-01.返却パラメータを作成し、返却する
            return {
                "result": True,
                "errorInfo": None
            }

        # 例外処理(PDSException)
        except PDSException as e:
            raise e

        # 例外処理
        except Exception as e:
            self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["999999"]["logMessage"], str(e), traceback.format_exc()))
            raise PDSException(
                {
                    "errorCode": "999999",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
                }
            )

    def user_profile_delete(self, transaction_id: str, mongodb_delete_flg: bool, mongodb_key: str, pds_user_info: object):
        """
        個人情報削除処理

        Args:
            transaction_id (str): トランザクションID
            mongodb_delete_flg (bool): MongoDBデータ削除フラグ
            mongodb_key (str): MongoDBデータ削除対象データキー
            pds_user_info (object): PDSユーザ情報

        Returns:
            result: 処理結果
        """
        try:
            # 01.MongoDB接続準備処理
            # 01-01.プログラムが配置されているリージョンのAZaのMongoDBの接続情報をAWSのSecrets Managerから取得する
            # 01-01-01.下記の引数で、AZaのMongoDB接続情報を取得する
            # 01-01-02.取得したMongoDBの接続情報を、「変数．MongoDB接続情報」に格納する
            # 01-02.プログラムが配置されているリージョンのAZcのMongoDBの接続情報をAWSのSecrets Managerから取得する
            # 01-02-01.下記の引数で、AZcのMongoDB接続情報を取得する
            # 01-02-02.取得したMongoDBの接続情報を、「変数．MongoDB接続情報」に格納する
            # 01-03 .変数．MongoDB接続情報」を利用して、MongoDBに対してのコネクションを作成する
            mongo_info_result = self.common_util.get_mongo_db_info_and_connection(
                pds_user_info["tokyo_a_mongodb_secret_name"],
                pds_user_info["tokyo_c_mongodb_secret_name"],
                pds_user_info["osaka_a_mongodb_secret_name"],
                pds_user_info["osaka_c_mongodb_secret_name"]
            )
            self.mongo_db_util: MongoDbClass = mongo_info_result["mongo_db_util"]

            # 02.MongoDBトランザクション作成処理
            # 02-01.「MongoDB個人情報削除トランザクション」を作成する
            self.mongo_db_util.create_session()
            self.mongo_db_util.create_transaction()

            # 03.MongoDB削除判定処理
            # 03-01.「引数．MongoDBデータ削除フラグ」がtrueの場合、「04.MongoDBデータ削除処理」に遷移する
            # 03-02.「引数．MongoDBデータ削除フラグ」がfalseの場合、「06. 個人情報削除処理」に遷移する

            if mongodb_delete_flg:
                # 04.MongoDBデータ削除処理
                # 04-01.MongoDBからデータを削除する
                mongo_db_delete_result = self.mongo_db_util.delete_object_id(mongodb_key)

                # 04-02.処理が失敗した場合は「変数．エラー情報」を作成し、エラーログをCloudWatchにログ出力する
                if not mongo_db_delete_result["result"]:
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["992001"]["logMessage"], mongo_db_delete_result["errorCode"], mongo_db_delete_result["message"]))
                    self.error_info = {
                        "errorCode": "992001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["992001"]["message"], "992001")
                    }

                # 05.共通エラーチェック処理
                # 05-01.以下の引数で共通エラーチェック処理を実行する
                # 05-02.例外が発生した場合、例外処理に遷移
                if self.error_info is not None:
                    # ロールバック処理
                    rollback_transaction = CallbackExecutor(
                        self.common_util.common_check_postgres_rollback,
                        self.pds_user_db_connection,
                        self.pds_user_db_connection_resource
                    )
                    # MongoDBロールバック処理
                    mongo_db_rollback = CallbackExecutor(
                        self.common_util.common_check_mongo_rollback,
                        self.mongo_db_util
                    )
                    # 02-02.例外が発生した場合、例外処理に遷移
                    self.common_util.common_error_check(
                        self.error_info,
                        rollback_transaction,
                        mongo_db_rollback
                    )

            # 06.個人情報削除処理
            # 06-01.個人情報テーブルからデータを削除する
            user_profile_delete_sql_result = self.pds_user_db_connection_resource.delete(
                self.pds_user_db_connection,
                SqlConstClass.TRANSACTION_DELETE_DATA_DELETE_SQL,
                transaction_id
            )
            # 06-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not user_profile_delete_sql_result["result"]:
                self.error_info = self.common_util.create_postgresql_log(
                    user_profile_delete_sql_result["errorObject"],
                    None,
                    None,
                    user_profile_delete_sql_result["stackTrace"]
                ).get("errorInfo")

            # 07.共通エラーチェック処理
            # 07-01.以下の引数で共通エラーチェック処理を実行する
            # 07-02.例外が発生した場合、例外処理に遷移
            if self.error_info is not None:
                # ロールバック処理
                rollback_transaction = CallbackExecutor(
                    self.common_util.common_check_postgres_rollback,
                    self.pds_user_db_connection,
                    self.pds_user_db_connection_resource
                )
                # MongoDBロールバック処理
                mongo_db_rollback = CallbackExecutor(
                    self.common_util.common_check_mongo_rollback,
                    self.mongo_db_util
                )
                self.common_util.common_error_check(
                    self.error_info,
                    rollback_transaction,
                    mongo_db_rollback
                )

            # 08.MongoDBトランザクションコミット処理
            # 08-01.「MongoDB個人情報削除トランザクション」をコミットする
            self.mongo_db_util.commit_transaction()
            self.mongo_db_util.close_session()
            self.mongo_db_util.close_mongo()

            # 09.終了処理
            # 09-01.レスポンス情報を作成し、返却する
            # 09-01-01.「変数．エラー情報」に値が設定されていない場合、下記のレスポンス情報を返却する
            return {
                "result": True
            }

        # 例外処理(PDSException)
        except PDSException as e:
            raise e

        # 例外処理
        except Exception as e:
            self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["999999"]["logMessage"], str(e), traceback.format_exc()))
            raise PDSException(
                {
                    "errorCode": "999999",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
                }
            )
