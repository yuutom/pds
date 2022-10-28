import json
from fastapi import Request
from logging import Logger
import traceback

# Exception
from exceptionClass.PDSException import PDSException

# Const
from const.messageConst import MessageConstClass

# Util
import util.commonUtil as commonUtil
from util.commonUtil import CommonUtilClass
from util.postgresDbUtil import PostgresDbUtilClass
from util.callbackExecutorUtil import CallbackExecutor
from const.apitypeConst import apitypeConstClass
import util.logUtil as logUtil

# 定数クラス
from const.sqlConst import SqlConstClass


class deleteModelClass():
    def __init__(self, logger: Logger, request: Request, pds_user_info, tid: str, pds_user_domain_name: str):
        """
        コンストラクタ

        Args:
            logger (Logger): ロガー（TRACE）
        """
        self.logger: Logger = logger
        self.request: Request = request
        self.common_util = CommonUtilClass(logger)
        self.pds_user_info = pds_user_info
        self.tid = tid
        self.pds_user_domain_name = pds_user_domain_name

    def main(self):
        """
        個人情報削除 メイン処理

        """
        try:
            # 02.個人情報削除処理
            # 02-01.以下の引数で個人情報削除処理を実行
            # 02-02.個人情報削除処理からのレスポンスを、「変数．個人情報削除処理実行結果」に格納する
            self.delete_user(
                pds_user_instance_secret_name=self.pds_user_info["pdsUserInstanceSecretName"],
                transaction_id=self.tid,
                pds_user_info=self.pds_user_info
            )

            # 03.個人情報削除バッチキュー発行処理
            # 03-01.以下の引数で個人情報削除バッチキュー発行処理を実行する
            # 03-02.以下の引数で、キューにメッセージを送信する
            self.common_util.transaction_delete_batch_queue_issue(self.tid, self.pds_user_info["pdsUserId"])

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

    def delete_user(self, pds_user_instance_secret_name: str, transaction_id: str, pds_user_info: object):
        """
        個人情報削除処理

        """
        try:
            # 01.PDSユーザDB接続情報取得
            self.pds_user_connection_resource: PostgresDbUtilClass = None
            # 01-01.以下の引数でPDSユーザDBの接続情報をAWSのSecrets Managerから取得する
            # 01-02.取得したPDSユーザDBの接続情報を、「変数．PDSユーザDB接続情報」に格納する
            # 01-03.「変数．PDSユーザDB接続情報」を利用して、PDSユーザDBに対してのコネクションを作成する
            pds_user_db_info_response = self.common_util.get_pds_user_db_info_and_connection(pds_user_instance_secret_name)
            if not pds_user_db_info_response["result"]:
                return pds_user_db_info_response
            else:
                self.pds_user_db_connection_resource = pds_user_db_info_response["pds_user_db_connection_resource"]
                self.pds_user_db_connection = pds_user_db_info_response["pds_user_db_connection"]

            # 02.個人情報取得処理
            pds_user_error_info = None
            # 02-01.個人情報テーブルからデータを取得し、「変数．個人情報取得結果」に1レコードをタプルとして格納する
            pds_user_result = self.pds_user_db_connection_resource.select_tuple_one(
                self.pds_user_db_connection,
                SqlConstClass.USER_PROFILE_DELETE_SELECT_SQL,
                transaction_id
            )
            # 02-02.「変数.個人情報取得結果」が0件の場合、「変数.個人情報取得エラー情報」を作成し、エラー情報をCloudWatchへログ出力する
            if pds_user_result["result"] and pds_user_result["rowcount"] == 0:
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020004"]["logMessage"], transaction_id))
                pds_user_error_info = {
                    "errorCode": "020004",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020004"]["message"], transaction_id)
                }
            # 02-03.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not pds_user_result["result"]:
                pds_user_error_info = self.common_util.create_postgresql_log(
                    pds_user_result["errorObject"],
                    None,
                    None,
                    pds_user_result["stackTrace"]
                ).get("errorInfo")

            # 03.共通エラーチェック処理
            # 03-01 以下の引数で共通エラーチェック処理を実行する
            if pds_user_error_info is not None:
                # API実行履歴登録処理
                api_history_insert = CallbackExecutor(
                    self.common_util.insert_api_history,
                    commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                    pds_user_info["pdsUserId"],
                    apitypeConstClass.API_TYPE["DELETE"],
                    self.pds_user_domain_name,
                    str(self.request.url),
                    json.dumps({"path_param": self.request.path_params, "query_param": self.request.query_params._dict, "header_param": commonUtil.make_headerParam(self.request.headers)}),
                    False,
                    None,
                    commonUtil.get_str_datetime()
                )
                # 03-02 例外が発生した場合、例外処理に遷移
                self.common_util.common_error_check(
                    pds_user_error_info,
                    api_history_insert
                )

            # 04.個人情報バイナリデータ取得処理
            pds_user_binary_data_error_info = None
            # 04-01.個人情報バイナリデータからデータを取得し、「変数．個人情報バイナリデータ取得結果リスト」に全レコードをタプルのリストとして格納する
            pds_user_binary_data_result = self.pds_user_db_connection_resource.select_tuple_list(
                self.pds_user_db_connection,
                SqlConstClass.USER_PROFILE_DELETE_BINARY_DATA_SELECT_SQL,
                transaction_id
            )
            # 04-02.「変数.個人情報バイナリデータ取得結果リスト」が0件の場合、「変数.個人情報バイナリデータ取得エラー情報」を作成し、エラー情報をCloudWatchへログ出力する
            if pds_user_binary_data_result["result"] and pds_user_binary_data_result["rowCount"] == 0:
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020004"]["logMessage"], transaction_id))
                pds_user_binary_data_error_info = {
                    "errorCode": "020004",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020004"]["message"], transaction_id)
                }
            # 04-03.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not pds_user_binary_data_result["result"]:
                pds_user_binary_data_error_info = self.common_util.create_postgresql_log(
                    pds_user_binary_data_result["errorObject"],
                    None,
                    None,
                    pds_user_binary_data_result["stackTrace"]
                ).get("errorInfo")

            # 05.共通エラーチェック処理
            # 05-01 以下の引数で共通エラーチェック処理を実行する
            if pds_user_binary_data_error_info is not None:
                # API実行履歴登録処理
                api_history_insert = CallbackExecutor(
                    self.common_util.insert_api_history,
                    commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                    pds_user_info["pdsUserId"],
                    apitypeConstClass.API_TYPE["DELETE"],
                    self.pds_user_domain_name,
                    str(self.request.url),
                    json.dumps({"path_param": self.request.path_params, "query_param": self.request.query_params._dict, "header_param": commonUtil.make_headerParam(self.request.headers)}),
                    False,
                    None,
                    commonUtil.get_str_datetime()
                )
                # 05-02 例外が発生した場合、例外処理に遷移
                self.common_util.common_error_check(
                    pds_user_binary_data_error_info,
                    api_history_insert
                )

            # 06.トランザクション作成処理
            # 06-01.「個人情報削除トランザクション」を作成する

            # 07.個人情報バイナリデータ論理削除処理
            # 07-01.以下の引数で個人情報バイナリデータ論理削除処理を実行する
            # 07-02.レスポンスを、「変数．個人情報バイナリデータ論理削除処理実行結果」に格納する
            self.delete_user_info_binary_data(transaction_id, pds_user_info["pdsUserId"])

            # 08.個人情報論理削除処理
            # 08-01.以下の引数で個人情報論理削除処理を実行する
            # 08-02.レスポンスを、「変数．個人情報論理削除処理実行結果」に格納する
            self.delete_user_info(transaction_id, pds_user_info["pdsUserId"])

            # 09.トランザクションコミット処理
            # 09-01.「個人情報削除トランザクション」をコミットする
            self.pds_user_db_connection_resource.commit_transaction(self.pds_user_db_connection)
            self.pds_user_db_connection_resource.close_connection(self.pds_user_db_connection)

            # 10.終了処理
            # 10-01.正常終了をCloudWatchへログ出力する
            # 10-02.レスポンス情報整形処理
            # 10-02-01.以下をレスポンスとして返却する
            # 10-03.処理を終了する
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

    def delete_user_info_binary_data(self, transaction_id: str, pds_user_id: str):
        """
        個人情報バイナリデータ論理削除処理

        Args:
            transaction_id (string): トランザクションID
            pds_user_id (string): PDSユーザID

        """
        try:
            # 01.個人情報バイナリデータ更新処理
            pds_user_delete_binary_data_update_error_info = None
            # 01-01.個人情報バイナリデータテーブルを更新する
            pds_user_delete_binary_data_update_result = self.pds_user_db_connection_resource.update(
                self.pds_user_db_connection,
                SqlConstClass.USER_PROFILE_DELETE_BINARY_DATA_UPDATE_SQL,
                transaction_id
            )
            # 01-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not pds_user_delete_binary_data_update_result["result"]:
                pds_user_delete_binary_data_update_error_info = self.common_util.create_postgresql_log(
                    pds_user_delete_binary_data_update_result["errorObject"],
                    None,
                    None,
                    pds_user_delete_binary_data_update_result["stackTrace"]
                ).get("errorInfo")

            # 02.共通エラーチェック処理
            # 02-01.以下の引数で共通エラーチェック処理を実行する
            if pds_user_delete_binary_data_update_error_info is not None:
                # ロールバック処理
                rollback_transaction = CallbackExecutor(
                    self.common_util.common_check_postgres_rollback,
                    self.pds_user_db_connection,
                    self.pds_user_db_connection_resource
                )
                # API実行履歴登録処理
                api_history_insert = CallbackExecutor(
                    self.common_util.insert_api_history,
                    commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                    pds_user_id,
                    apitypeConstClass.API_TYPE["DELETE"],
                    self.pds_user_domain_name,
                    str(self.request.url),
                    json.dumps({"path_param": self.request.path_params, "query_param": self.request.query_params._dict, "header_param": commonUtil.make_headerParam(self.request.headers)}),
                    False,
                    None,
                    commonUtil.get_str_datetime()
                )
                # 02-02.例外が発生した場合、例外処理に遷移
                self.common_util.common_error_check(
                    pds_user_delete_binary_data_update_error_info,
                    rollback_transaction,
                    api_history_insert
                )

            # 03.終了処理
            # 03-01.レスポンス情報を作成し、返却する
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

    def delete_user_info(self, transaction_id, pds_user_id):
        """
        個人情報論理削除処理

        Args:
            transaction_id (string): トランザクションID
            pds_user_id (string): PDSユーザID

        """
        try:
            # 01.個人情報更新処理
            pds_user_delete_data_update_error_info = None
            # 01-01.個人情報テーブルを更新する
            pds_user_delete_data_update_result = self.pds_user_db_connection_resource.update(
                self.pds_user_db_connection,
                SqlConstClass.USER_PROFILE_DELETE_DATA_UPDATE_SQL,
                transaction_id
            )
            # 01-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not pds_user_delete_data_update_result["result"]:
                pds_user_delete_data_update_error_info = self.common_util.create_postgresql_log(
                    pds_user_delete_data_update_result["errorObject"],
                    None,
                    None,
                    pds_user_delete_data_update_result["stackTrace"]
                ).get("errorInfo")

            # 02.共通エラーチェック処理
            # 02-01.以下の引数で共通エラーチェック処理を実行する
            if pds_user_delete_data_update_error_info is not None:
                # ロールバック処理
                rollback_transaction = CallbackExecutor(
                    self.common_util.common_check_postgres_rollback,
                    self.pds_user_db_connection,
                    self.pds_user_db_connection_resource
                )
                # API実行履歴登録処理
                api_history_insert = CallbackExecutor(
                    self.common_util.insert_api_history,
                    commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                    pds_user_id,
                    apitypeConstClass.API_TYPE["DELETE"],
                    self.pds_user_domain_name,
                    str(self.request.url),
                    json.dumps({"path_param": self.request.path_params, "query_param": self.request.query_params._dict, "header_param": commonUtil.make_headerParam(self.request.headers)}),
                    False,
                    None,
                    commonUtil.get_str_datetime()
                )
                # 02-02.例外が発生した場合、例外処理に遷移
                self.common_util.common_error_check(
                    pds_user_delete_data_update_error_info,
                    rollback_transaction,
                    api_history_insert
                )

            # 03.終了処理
            # 03-01.レスポンス情報を作成し、返却する
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
