from typing import Optional, Union
import json
from pydantic import BaseModel
from fastapi import Request
from logging import Logger
import traceback
import boto3
import asyncio
import io

## コールバック関数
from util.callbackExecutorUtil import CallbackExecutor
# Exception
from exceptionClass.PDSException import PDSException

# Const
from const.messageConst import MessageConstClass
from const.apitypeConst import apitypeConstClass
from const.sqlConst import SqlConstClass
from const.systemConst import SystemConstClass
from const.fileNameConst import FileNameConstClass
from const.wbtConst import wbtConstClass

# Util
import util.logUtil as logUtil
import util.commonUtil as commonUtil
from util.commonUtil import CommonUtilClass
from util.postgresDbUtil import PostgresDbUtilClass
from util.userProfileUtil import UserProfileUtilClass


class searchCriteriaInfo(BaseModel):
    userIdMatchMode: Optional[str] = None
    userIdStr: Optional[str] = None
    dataJsonKey: Optional[str] = None
    dataMatchMode: Optional[str] = None
    dataStr: Optional[str] = None
    imageHash: Optional[str] = None
    fromDate: Optional[str] = None
    toDate: Optional[str] = None


class requestBody(BaseModel):
    pdsUserId: Optional[str] = None
    searchCriteria: Optional[searchCriteriaInfo] = None
    tidList: Union[Optional[str], Optional[list]] = None
    approvalUserId: Optional[str] = None
    approvalUserPassword: Optional[str] = None
    mailAddressTo: Optional[str] = None
    mailAddressCc: Optional[str] = None


class requestBodyTask(BaseModel):
    requestNo: Optional[str] = None
    pdsUserId: Optional[str] = None


class multiDownloadModel():

    def __init__(self, logger: Logger, request: Request):
        self.logger: Logger = logger
        self.request: Request = request
        self.common_util = CommonUtilClass(logger)

    def main(self, request_body: requestBody, tf_operator_id: str):
        """
        メイン処理

        Args:
            request_body (object): リクエストボディ

        Returns:
            dict: メイン処理実行結果
        """
        try:
            # 02.共通DB接続準備処理
            # 02-01.AWS SecretsManagerから共通DB接続情報を取得して、「変数．共通DB接続情報」に格納する
            common_util = CommonUtilClass(self.logger)
            common_db_connection_resource: PostgresDbUtilClass = None
            # 02-02.「変数．共通DB接続情報」を利用して、共通DBに対してのコネクションを作成する
            common_db_info_response = common_util.get_common_db_info_and_connection()
            if not common_db_info_response["result"]:
                raise PDSException(common_db_info_response["errorInfo"])
            else:
                common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
                common_db_connection = common_db_info_response["common_db_connection"]

            # 03.承認者情報確認処理
            # 03-01.承認者情報確認処理を実行する
            self.common_util.check_approval_user_info(
                approvalUserId=request_body.approvalUserId,
                approvalUserPassword=request_body.approvalUserPassword,
                commonDbInfo=common_db_info_response["common_db_secret_info"]
            )

            # 04.PDSユーザデータ取得処理
            pds_user_search_error_info = None
            # 04-01.PDSユーザテーブルからPDSユーザデータを取得し、「変数．PDSユーザ情報」に1レコードをタプルとして格納する
            pds_user_search_result = common_db_connection_resource.select_tuple_one(
                common_db_connection,
                SqlConstClass.MONGODB_SECRET_NAME_SELECT_SQL,
                request_body.pdsUserId
            )

            # 04-02.「変数．PDSユーザ取得結果」が0件の場合、「変数.エラー情報」を作成する
            if pds_user_search_result["result"] and pds_user_search_result["rowcount"] == 0:
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020004"]["logMessage"], request_body.pdsUserId))
                pds_user_search_error_info = {
                    "errorCode": "020004",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020004"]["message"], request_body.pdsUserId)
                }

            # 04-03.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not pds_user_search_result["result"]:
                pds_user_search_error_info = self.common_util.create_postgresql_log(
                    pds_user_search_result["errorObject"],
                    None,
                    None,
                    pds_user_search_result["stackTrace"]
                ).get("errorInfo")

            # 05.共通エラーチェック処理
            # 05-01.以下の引数で共通エラーチェック処理を実行する
            # 05-02.例外が発生した場合、例外処理に遷移
            if pds_user_search_error_info is not None:
                # API実行履歴登録処理
                api_history_insert = CallbackExecutor(
                    self.common_util.insert_api_history,
                    commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                    request_body.pdsUserId,
                    apitypeConstClass.API_TYPE["BATCH_DOWNLOAD"],
                    None,
                    str(self.request.url),
                    json.dumps({"path_param": self.request.path_params, "query_param": self.request.query_params._dict, "header_param": commonUtil.make_headerParam(self.request.headers), "request_body": request_body.dict()}),
                    False,
                    tf_operator_id,
                    commonUtil.get_str_datetime()
                )
                self.common_util.common_error_check(
                    pds_user_search_error_info,
                    api_history_insert
                )

            # PDSユーザ情報（Dict形式）の作成
            pds_user_info_column_list = [
                'pdsUserInstanceSecretName',
                'tokyo_a_mongodb_secret_name',
                'tokyo_c_mongodb_secret_name',
                'osaka_a_mongodb_secret_name',
                'osaka_c_mongodb_secret_name',
            ]
            pds_user_info_dict = {column: data for column, data in zip(pds_user_info_column_list, pds_user_search_result["query_results"])}

            # 06.tidリスト有無判定
            # 06-01.リクエストの「リクエストボディ．tidリスト」がNullの場合、「07.tidリスト作成処理」に遷移する
            # 06-02.リクエストの「リクエストボディ．tidリスト」がNull以外の場合、「変数．tidリスト」にリクエストの「リクエストボディ．tidリスト」を格納し、「08.問い合わせID発行処理」に遷移する
            tidList = request_body.tidList
            if tidList is None:
                # 07.tidリスト作成処理
                # 07-01.tidリスト作成処理を実行
                # 07-02.レスポンスを、「変数．tidリスト作成処理実行結果」に格納する
                tid_list_create_exec_result = self.common_util.tid_list_create_exec(
                    searchCriteria=request_body.searchCriteria.dict(),
                    pdsUserInfo=pds_user_info_dict
                )
                # 07-03.「変数．tidリスト」に「変数．tidリスト作成処理実行結果．tidリスト」を格納する
                tidList = tid_list_create_exec_result["tidList"]

            # 08.問い合わせID発行処理
            # 08-01.問い合わせID（UUID）を発行し、「変数．問い合わせID」に格納する
            uuid = commonUtil.get_uuid_no_hypen()

            # 09.トランザクション作成処理
            # 09-01.「個人情報一括DL状態管理テーブル登録トランザクション」を作成する

            # 10.個人情報一括DL状態管理テーブル登録処理
            multi_download_status_manage_insert_error_info = None
            # 10-01.個人情報一括DL状態管理テーブルに登録する
            multi_download_status_manage_insert_result = common_db_connection_resource.insert(
                common_db_connection,
                SqlConstClass.MULTI_DOWUNLOAD_STATUS_MANAGE_INSERT_SQL,
                uuid,
                request_body.pdsUserId,
                SystemConstClass.USER_PROFILE_DL_EXEC_TYPE,
                request_body.mailAddressTo,
                request_body.mailAddressCc,
                SystemConstClass.USER_PROFILE_DL_EXEC_GET_DATA_STATUS,
                None,
                commonUtil.get_datetime_jst(),
                None,
                tf_operator_id
            )
            # 10-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not multi_download_status_manage_insert_result["result"]:
                multi_download_status_manage_insert_error_info = self.common_util.create_postgresql_log(
                    multi_download_status_manage_insert_result["errorObject"],
                    "問い合わせNo",
                    uuid,
                    multi_download_status_manage_insert_result["stackTrace"]
                ).get("errorInfo")

            # 11.共通エラーチェック処理
            # 11-01.以下の引数で共通エラーチェック処理を実行する
            # 11-02.例外が発生した場合、例外処理に遷移。設計書も修正する
            if multi_download_status_manage_insert_error_info is not None:
                # ロールバック処理
                rollback_transaction = CallbackExecutor(
                    self.common_util.common_check_postgres_rollback,
                    common_db_connection,
                    common_db_connection_resource
                )
                # API実行履歴登録処理
                api_history_insert = CallbackExecutor(
                    self.common_util.insert_api_history,
                    commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                    request_body.pdsUserId,
                    apitypeConstClass.API_TYPE["BATCH_DOWNLOAD"],
                    None,
                    str(self.request.url),
                    json.dumps({"path_param": self.request.path_params, "query_param": self.request.query_params._dict, "header_param": commonUtil.make_headerParam(self.request.headers), "request_body": request_body.dict()}),
                    False,
                    tf_operator_id,
                    commonUtil.get_str_datetime()
                )
                self.common_util.common_error_check(
                    multi_download_status_manage_insert_error_info,
                    rollback_transaction,
                    api_history_insert
                )

            # 12.個人情報一括DL対象個人情報IDテーブル登録処理
            insert_data = []
            for tid in tidList:
                insert_data.append((uuid, request_body.pdsUserId, tid))
            multi_download_target_transaction_id_bulk_insert_error_info = None
            # 12-01.個人情報一括DL対象個人情報IDテーブルに登録する（バルクインサート）
            multi_download_target_transaction_id_bulk_insert_result = common_db_connection_resource.bulk_insert(
                common_db_connection,
                SqlConstClass.MULTI_DOWUNLOAD_TARGET_TRANSACTION_ID_BULK_INSERT_SQL,
                insert_data
            )
            # 12-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not multi_download_target_transaction_id_bulk_insert_result["result"]:
                multi_download_target_transaction_id_bulk_insert_error_info = self.common_util.create_postgresql_log(
                    multi_download_target_transaction_id_bulk_insert_result["errorObject"],
                    "問い合わせNo",
                    uuid,
                    multi_download_target_transaction_id_bulk_insert_result["stackTrace"]
                ).get("errorInfo")

            # 13.共通エラーチェック処理
            # 13-01.以下の引数で共通エラーチェック処理を実行する
            # 13-02.例外が発生した場合、例外処理に遷移
            if multi_download_target_transaction_id_bulk_insert_error_info is not None:
                # ロールバック処理
                rollback_transaction = CallbackExecutor(
                    self.common_util.common_check_postgres_rollback,
                    common_db_connection,
                    common_db_connection_resource
                )
                # API実行履歴登録
                api_history_insert = CallbackExecutor(
                    self.common_util.insert_api_history,
                    commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                    request_body.pdsUserId,
                    apitypeConstClass.API_TYPE["BATCH_DOWNLOAD"],
                    None,
                    str(self.request.url),
                    json.dumps({"path_param": self.request.path_params, "query_param": self.request.query_params._dict, "header_param": commonUtil.make_headerParam(self.request.headers), "request_body": request_body.dict()}),
                    False,
                    tf_operator_id,
                    commonUtil.get_str_datetime()
                )
                self.common_util.common_error_check(
                    multi_download_target_transaction_id_bulk_insert_error_info,
                    rollback_transaction,
                    api_history_insert
                )

            # 14.トランザクションコミット処理
            # 14-01.「WBT状態管理登録トランザクション」をコミットする
            common_db_connection_resource.commit_transaction(common_db_connection)
            common_db_connection_resource.close_connection(common_db_connection)

            # 15.個人情報一括DLバッチキュー発行処理
            client = boto3.client(
                service_name="sqs"
            )
            multi_download_queue_error_info = None
            for result_count in range(5):
                try:
                    # 15-01.キュー発行するためのインスタンスを取得して、「変数．個人情報一括DLバッチキューインスタンス」に格納する
                    queue_info = client.get_queue_url(QueueName=SystemConstClass.SQS_MULTI_DOWNLOAD_QUEUE_NAME)
                    # 15-02.キューにメッセージを送信する
                    message = {
                        "requestNo": uuid,
                        "pdsUserId": request_body.pdsUserId
                    }
                    data = {
                        "MessageBody": json.dumps(message),
                        "QueueUrl": queue_info["QueueUrl"]
                    }
                    client.send_message(**data)
                    break
                except Exception:
                    if result_count == 4:
                        self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990052"]["logMessage"], uuid, request_body.pdsUserId))
                        multi_download_queue_error_info = {
                            "errorCode": "990052",
                            "message": logUtil.message_build(MessageConstClass.ERRORS["990052"]["message"], "990052")
                        }
            # 16.共通エラーチェック処理
            # 16-01.以下の引数で共通エラーチェック処理を実行する
            # 16-02.例外が発生した場合、例外処理に遷移
            if multi_download_queue_error_info is not None:
                # API実行履歴登録
                api_history_insert = CallbackExecutor(
                    self.common_util.insert_api_history,
                    commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                    request_body.pdsUserId,
                    apitypeConstClass.API_TYPE["BATCH_DOWNLOAD"],
                    None,
                    str(self.request.url),
                    json.dumps({"path_param": self.request.path_params, "query_param": self.request.query_params._dict, "header_param": commonUtil.make_headerParam(self.request.headers), "request_body": request_body.dict()}),
                    False,
                    tf_operator_id,
                    commonUtil.get_str_datetime()
                )
                common_util.common_error_check(
                    multi_download_queue_error_info,
                    api_history_insert
                )

            return {
                "result": True,
                "inquiry_id": uuid
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

    async def multi_download_exec(self, request_body: dict):
        """
        個人情報一括DL処理 メイン処理

        Args:
            request_body (dict): リクエストボディ

        Returns:
            dict: 処理結果
        """
        try:
            # 02.共通DB接続準備処理
            # 02-01.AWS SecretsManagerから共通DB接続情報を取得して、「変数．共通DB接続情報」に格納する
            common_util = CommonUtilClass(self.logger)
            common_db_connection_resource: PostgresDbUtilClass = None
            # 02-02.「変数．共通DB接続情報」を利用して、共通DBに対してのコネクションを作成する
            common_db_info_response = common_util.get_common_db_info_and_connection()
            if not common_db_info_response["result"]:
                raise PDSException(common_db_info_response["errorInfo"])
            else:
                common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
                common_db_connection = common_db_info_response["common_db_connection"]

            # 03.PDSユーザデータ取得処理
            pds_user_search_error_info = None
            # 03-01.PDSユーザテーブルからPDSユーザデータを取得し、「変数．PDSユーザ情報」に1レコードをタプルとして
            pds_user_search_result = common_db_connection_resource.select_tuple_one(
                common_db_connection,
                SqlConstClass.MONGODB_SECRET_NAME_BUCKET_NAME_SELECT_SQL,
                request_body["pdsUserId"]
            )

            # 03-02.「変数．PDSユーザ情報」が0件の場合、「変数.エラー情報」を作成する
            if pds_user_search_result["result"] and pds_user_search_result["rowcount"] == 0:
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020004"]["logMessage"], request_body["pdsUserId"]))
                pds_user_search_error_info = {
                    "errorCode": "020004",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020004"]["message"], request_body["pdsUserId"])
                }

            # 03-03.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not pds_user_search_result["result"]:
                pds_user_search_error_info = self.common_util.create_postgresql_log(
                    pds_user_search_result["errorObject"],
                    None,
                    None,
                    pds_user_search_result["stackTrace"]
                ).get("errorInfo")

            # 04.共通エラーチェック処理
            # 04-01.以下の引数で共通エラーチェック処理を実行する
            # 04-02.例外が発生した場合、例外処理に遷移
            if pds_user_search_error_info is not None:
                # API実行履歴登録処理
                api_history_insert = CallbackExecutor(
                    self.common_util.insert_api_history,
                    commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                    request_body["pdsUserId"],
                    apitypeConstClass.API_TYPE["BATCH_DOWNLOAD"],
                    None,
                    str(self.request.url),
                    json.dumps({"path_param": self.request.path_params, "query_param": self.request.query_params._dict, "header_param": commonUtil.make_headerParam(self.request.headers), "request_body": request_body}),
                    False,
                    None,
                    commonUtil.get_str_datetime()
                )
                # WBT状態管理更新処理
                update_multi_download_status = CallbackExecutor(
                    self.update_multi_download_status_manage,
                    request_body["requestNo"],
                    common_db_info_response
                )
                self.common_util.common_error_check(
                    pds_user_search_error_info,
                    api_history_insert,
                    update_multi_download_status
                )

            # PDSユーザ情報（Dict形式）の作成
            pds_user_info_column_list = [
                'pdsUserInstanceSecretName',
                'tokyo_a_mongodb_secret_name',
                'tokyo_c_mongodb_secret_name',
                'osaka_a_mongodb_secret_name',
                'osaka_c_mongodb_secret_name',
                's3ImageDataBucketName'
            ]
            pds_user_info_dict = {column: data for column, data in zip(pds_user_info_column_list, pds_user_search_result["query_results"])}

            # 05.個人情報一括DL状態管理取得処理
            multi_download_manage_search_error_info = None
            # 05-01.個人情報一括DL状態管理、個人情報一括DL対象個人情報IDからデータを取得し、「変数．個人情報一括DL状態管理取得結果リスト」に全レコードをタプルのリストとして格納する
            multi_download_manage_search_result = common_db_connection_resource.select_tuple_list(
                common_db_connection,
                SqlConstClass.MULTI_DOWUNLOAD_TARGET_TRANSACTION_ID_SELECT_SQL,
                request_body["requestNo"],
                request_body["pdsUserId"]
            )
            # 05-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not multi_download_manage_search_result["result"]:
                multi_download_manage_search_error_info = self.common_util.create_postgresql_log(
                    multi_download_manage_search_result["errorObject"],
                    None,
                    None,
                    multi_download_manage_search_result["stackTrace"]
                ).get("errorInfo")

            # 06.共通エラーチェック処理
            # 06-01.以下の引数で共通エラーチェック処理を実行する
            # 06-02.例外が発生した場合、例外処理に遷移
            if multi_download_manage_search_error_info is not None:
                # API実行履歴登録処理
                api_history_insert = CallbackExecutor(
                    self.common_util.insert_api_history,
                    commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                    request_body["pdsUserId"],
                    apitypeConstClass.API_TYPE["BATCH_DOWNLOAD"],
                    None,
                    str(self.request.url),
                    json.dumps({"path_param": self.request.path_params, "query_param": self.request.query_params._dict, "header_param": commonUtil.make_headerParam(self.request.headers), "request_body": request_body}),
                    False,
                    None,
                    commonUtil.get_str_datetime()
                )
                # WBT状態管理更新処理
                update_multi_download_status = CallbackExecutor(
                    self.update_multi_download_status_manage,
                    request_body["requestNo"],
                    common_db_info_response
                )
                self.common_util.common_error_check(
                    multi_download_manage_search_error_info,
                    api_history_insert,
                    update_multi_download_status
                )

            results_column_list = [list(tup) for tup in zip(*multi_download_manage_search_result["query_results"])]
            if results_column_list == []:
                tid_list = []
            else:
                tid_list = results_column_list[2]

            # 07.PDSユーザDB接続準備処理
            # 07-01.以下の引数でPDSユーザDBの接続情報をAWSのSecrets Managerから取得する
            # 07-02.取得したPDSユーザDBの接続情報を、「変数．PDSユーザDB接続情報」に格納する
            # 07-03.「変数．PDSユーザDB接続情報」を利用して、PDSユーザDBに対してのコネクションを作成する
            pds_user_db_connection_resource: PostgresDbUtilClass = None
            pds_user_db_info_response = self.common_util.get_pds_user_db_info_and_connection(pds_user_info_dict["pdsUserInstanceSecretName"])
            if not pds_user_db_info_response["result"]:
                raise PDSException(pds_user_db_info_response["errorInfo"])
            else:
                pds_user_db_secret_info = pds_user_db_info_response["pds_user_db_secret_info"]
                pds_user_db_connection_resource = pds_user_db_info_response["pds_user_db_connection_resource"]
                pds_user_db_connection = pds_user_db_info_response["pds_user_db_connection"]

            # 08.個人情報取得処理
            user_profile_select_error_info = None
            # 08-01.個人情報テーブルからデータを取得し、「変数．個人情報取得結果リスト」に全レコードをタプルのリストとして格納する
            user_profile_select_result = pds_user_db_connection_resource.select_tuple_list(
                pds_user_db_connection,
                SqlConstClass.USER_PROFILE_MULTI_DOWNLOAD_SELECT_SQL,
                tuple(tid_list),
                True
            )
            # 08-02.「変数.個人情報取得結果」が0件の場合、「変数.個人情報一意検証エラー情報」を作成し、エラー情報をCloudWatchへログ出力する
            if user_profile_select_result["result"] and user_profile_select_result["rowCount"] == 0:
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020004"]["logMessage"], str(tid_list)))
                user_profile_select_error_info = {
                    "errorCode": "020004",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020004"]["message"], str(tid_list))
                }
            # 08-03.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not user_profile_select_result["result"]:
                user_profile_select_error_info = self.common_util.create_postgresql_log(
                    user_profile_select_result["errorObject"],
                    None,
                    None,
                    user_profile_select_result["stackTrace"]
                ).get("errorInfo")

            # 09.共通エラーチェック処理
            # 09-01.以下の引数で共通エラーチェック処理を実行する
            # 09-02.例外が発生した場合、例外処理に遷移
            if user_profile_select_error_info is not None:
                # API実行履歴登録処理
                api_history_insert = CallbackExecutor(
                    self.common_util.insert_api_history,
                    commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                    request_body["pdsUserId"],
                    apitypeConstClass.API_TYPE["BATCH_DOWNLOAD"],
                    None,
                    str(self.request.url),
                    json.dumps({"path_param": self.request.path_params, "query_param": self.request.query_params._dict, "header_param": commonUtil.make_headerParam(self.request.headers), "request_body": request_body}),
                    False,
                    multi_download_manage_search_result["query_results"][0][0],
                    commonUtil.get_str_datetime()
                )
                # WBT状態管理更新処理
                update_multi_download_status = CallbackExecutor(
                    self.update_multi_download_status_manage,
                    request_body["requestNo"],
                    common_db_info_response
                )
                self.common_util.common_error_check(
                    user_profile_select_error_info,
                    api_history_insert,
                    update_multi_download_status
                )

            # 10.個人情報取得処理リスト初期化処理
            # 10-01.「変数．個人情報取得処理リスト」を初期化する
            get_user_profile_info_exec_list = []

            for transaction_id_loop, user_profile in enumerate(user_profile_select_result["query_results"]):
                # 11.個人情報取得処理リスト作成処理
                # 11-01.「変数．個人情報取得処理リスト」に個人情報取得処理を追加する
                get_user_profile_info_exec_list.append(
                    self.get_user_profile_info_exec(
                        pds_user_db_secret_info=pds_user_db_secret_info,
                        transaction_id=user_profile[0],
                        pds_user_info=pds_user_info_dict,
                        request_id=request_body["requestNo"],
                        common_db_info_response=common_db_info_response,
                        request_body=request_body,
                        request=self.request,
                        tf_operator_id=multi_download_manage_search_result["query_results"][0][0]
                    )
                )

            # 12.個人情報取得処理実行処理
            # 12-01.「変数．個人情報取得処理リスト」をもとに、個人情報取得処理を並列で実行する
            # 12-02.レスポンスを「変数．個人情報取得処理実行結果リスト」に格納する
            get_user_profile_info_exec_result_list = await asyncio.gather(*get_user_profile_info_exec_list, return_exceptions=True)

            error_info_list = []
            exception_list = [d for d in get_user_profile_info_exec_result_list if type(d) is PDSException]
            if len(exception_list) > 0:
                for exception in exception_list:
                    for error in exception.error_info_list:
                        error_info_list.append(error)

            result_list = [d.get("result") for d in get_user_profile_info_exec_result_list if type(d) is dict]
            if False in result_list:
                error_info_list = []
                for result_info in get_user_profile_info_exec_result_list:
                    if result_info.get("errorInfo"):
                        if type(result_info["errorInfo"]) is list:
                            error_info_list.extend(result_info["errorInfo"])
                        else:
                            error_info_list.append(result_info["errorInfo"])
            # 13.共通エラーチェック処理
            # 13-01.以下の引数で共通エラーチェック処理を実行する
            if len(error_info_list) > 0:
                # API実行履歴登録処理
                api_history_insert = CallbackExecutor(
                    self.common_util.insert_api_history,
                    commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                    request_body["pdsUserId"],
                    apitypeConstClass.API_TYPE["BATCH_DOWNLOAD"],
                    None,
                    str(self.request.url),
                    json.dumps({"path_param": self.request.path_params, "query_param": self.request.query_params._dict, "header_param": commonUtil.make_headerParam(self.request.headers), "request_body": request_body}),
                    False,
                    multi_download_manage_search_result["query_results"][0][0],
                    commonUtil.get_str_datetime()
                )
                # WBT状態管理更新処理
                update_multi_download_status = CallbackExecutor(
                    self.update_multi_download_status_manage,
                    request_body["requestNo"],
                    common_db_info_response
                )
                # 13-02.例外が発生した場合、例外処理に遷移
                self.common_util.common_error_check(
                    error_info_list,
                    api_history_insert,
                    update_multi_download_status
                )

            # 14.個人情報一括DLファイル分割リスト初期化処理
            # 14-01.「変数．分割ファイルリスト」を初期化する
            # 14-02.「変数．個人情報リスト」を初期化する
            split_file_list = []
            transaction_info_list = []
            for transaction_id_loop, get_user_profile_info in enumerate(get_user_profile_info_exec_result_list):
                # 15.個人情報作成処理
                # 15-01.「変数．個人情報」に以下の値を格納する
                transaction_info = {
                    "transactionId": get_user_profile_info["transactionId"],
                    "info": {
                        "userId": get_user_profile_info["transactionInfo"]["userId"],
                        "saveDate": get_user_profile_info["transactionInfo"]["saveDate"],
                        "data": get_user_profile_info["transactionInfo"]["data"],
                        "image": get_user_profile_info["transactionInfo"]["image"],
                        "imageHash": get_user_profile_info["transactionInfo"]["imageHash"],
                        "secureLevel": get_user_profile_info["transactionInfo"]["secureLevel"]
                    }
                }
                # 15-02.「変数．個人情報リスト」に「変数．個人情報」を追加する
                transaction_info_list.append(transaction_info)

                # 15-03.「変数．個人情報リスト」のバイト数が2GBを超過する場合には、ファイルを分割する
                if len(json.dumps(transaction_info_list, indent=4).encode("utf-8")) > SystemConstClass.USER_PROFILE_DL_FILE_CHUNK_SIZE:
                    # 15-03-01.「変数．個人情報リスト」の最後の要素を削除する
                    del transaction_info_list[-1]
                    # 15-03-02.「変数．分割ファイルリスト」に「変数．個人情報リスト」を追加する
                    split_file_list.append(transaction_info_list)
                    # 15-03-03.「変数．個人情報リスト」を初期化する
                    transaction_info_list = []
                    # 15-03-04.「変数．個人情報リスト」に「変数．個人情報」を追加する
                    transaction_info_list.append(transaction_info)

            # 16.分割ファイルリスト情報作成
            # 16-01.「変数．分割ファイルリスト」に「変数．個人情報リスト」を追加する
            split_file_list.append(transaction_info_list)

            # 17.個人情報一括DL通知ファイルリスト初期化処理
            # 17-01.「変数．個人情報一括DL通知ファイルリスト」を初期化する
            json_file_list = []
            for split_file_loop, split_file in enumerate(split_file_list):
                # 18.jsonファイル作成処理
                # 18-01.取得した以下のデータをもとにjsonファイルを作成する
                # 18-02.作成したjsonを「変数．個人情報一括DL通知ファイル」に格納する
                json_file = io.BytesIO(json.dumps(split_file, indent=4).encode("utf-8"))
                file_name = FileNameConstClass.MULTI_DOWNLOAD_JSON_NAME + "_" + str(split_file_loop) + FileNameConstClass.MULTI_DOWNLOAD_JSON_EXTENSION
                # 18-03.「変数．個人情報一括DL通知ファイルリスト」に「変数．個人情報一括DL通知ファイル」を追加する
                json_file_list.append({"json_file": json_file, "file_name": file_name})

            # 不要なリソースの削除
            split_file_list = None
            transaction_info_list = None

            # 19.トランザクション作成処理
            # 19-01.「個人情報一括DL状態管理更新トランザクション」を作成する

            # 20.個人情報一括DL状態管理更新処理
            multi_download_manage_wbt_exec_update_error_info = None
            # 20-01.個人情報一括DL状態管理テーブルを更新する
            multi_download_manage_wbt_exec_update_result = common_db_connection_resource.update(
                common_db_connection,
                SqlConstClass.MULTI_DOWUNLOAD_STATUS_MANAGE_WBT_EXEC_UPDATE_SQL,
                SystemConstClass.USER_PROFILE_DL_EXEC_WBT_EXEC_STATUS,
                request_body["requestNo"],
                request_body["pdsUserId"]
            )
            # 20-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not multi_download_manage_wbt_exec_update_result["result"]:
                multi_download_manage_wbt_exec_update_error_info = self.common_util.create_postgresql_log(
                    multi_download_manage_wbt_exec_update_result["errorObject"],
                    None,
                    None,
                    multi_download_manage_wbt_exec_update_result["stackTrace"]
                ).get("errorInfo")

            # 21.共通エラーチェック処理
            # 21-01.以下の引数で共通エラーチェック処理を実行する
            # 21-02.例外が発生した場合、例外処理に遷移
            if multi_download_manage_wbt_exec_update_error_info is not None:
                # API実行履歴登録処理
                api_history_insert = CallbackExecutor(
                    self.common_util.insert_api_history,
                    commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                    request_body["pdsUserId"],
                    apitypeConstClass.API_TYPE["BATCH_DOWNLOAD"],
                    None,
                    str(self.request.url),
                    json.dumps({"path_param": self.request.path_params, "query_param": self.request.query_params._dict, "header_param": commonUtil.make_headerParam(self.request.headers), "request_body": request_body}),
                    False,
                    multi_download_manage_search_result["query_results"][0][0],
                    commonUtil.get_str_datetime()
                )
                # ロールバック処理
                rollback_transaction = CallbackExecutor(
                    self.common_util.common_check_postgres_rollback,
                    common_db_connection,
                    common_db_connection_resource
                )
                # WBT状態管理更新処理
                update_multi_download_status = CallbackExecutor(
                    self.update_multi_download_status_manage,
                    request_body["requestNo"],
                    common_db_info_response
                )
                self.common_util.common_error_check(
                    multi_download_manage_wbt_exec_update_error_info,
                    rollback_transaction,
                    api_history_insert,
                    update_multi_download_status
                )

            # 22.トランザクションコミット処理
            # 22-01.「WBT状態管理更新トランザクション」をコミットする
            common_db_connection_resource.commit_transaction(common_db_connection)

            join_mail_id = ""
            for multi_download_loop, multi_download_file in enumerate(json_file_list):
                # 23.WBT新規メール情報登録API実行処理
                wbt_mails_add_api_error_info = None
                try:
                    # 23-01.以下の引数でWBTの新規メール情報登録API呼び出し処理を実行する
                    wbt_mails_add_api_exec_result = self.common_util.wbt_mails_add_api_exec(
                        wbtConstClass.REPOSITORY_TYPE["RETURN"],
                        multi_download_file["file_name"],
                        commonUtil.get_str_datetime_in_X_days(7),
                        None,
                        wbtConstClass.MESSAGE["USER_PROFILE_MULTI_DOWNLOAD"],
                        multi_download_manage_search_result["query_results"][0][3],
                        multi_download_manage_search_result["query_results"][0][4],
                        wbtConstClass.TITLE["USER_PROFILE_MULTI_DOWNLOAD"]
                    )
                except Exception:
                    # 23-02.WebBureauTransferの処理に失敗した場合、「変数．エラー情報」にエラー情報を作成する
                    wbt_mails_add_api_error_info = {
                        "errorCode": "990011",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["990011"]["message"])
                    }
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990011"]["logMessage"], "990011"))

                # 24.共通エラーチェック処理
                # 24-01.以下の引数で共通エラーチェック処理を実行する
                # 24-02 例外が発生した場合、例外処理に遷移
                if wbt_mails_add_api_error_info is not None:
                    # API実行履歴登録処理
                    api_history_insert = CallbackExecutor(
                        self.common_util.insert_api_history,
                        commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                        request_body["pdsUserId"],
                        apitypeConstClass.API_TYPE["BATCH_DOWNLOAD"],
                        None,
                        str(self.request.url),
                        json.dumps({"path_param": self.request.path_params, "query_param": self.request.query_params._dict, "header_param": commonUtil.make_headerParam(self.request.headers), "request_body": request_body}),
                        False,
                        multi_download_manage_search_result["query_results"][0][0],
                        commonUtil.get_str_datetime()
                    )
                    # WBT状態管理更新処理
                    update_multi_download_status = CallbackExecutor(
                        self.update_multi_download_status_manage,
                        request_body["requestNo"],
                        common_db_info_response
                    )
                    self.common_util.common_error_check(
                        wbt_mails_add_api_error_info,
                        api_history_insert,
                        update_multi_download_status
                    )

                # 25.WBTのファイル登録API実行処理
                wbt_file_add_api_error_info = None
                try:
                    # 25-01.以下のパラメータでWBTファイル登録APIを呼び出し処理を実行する
                    self.common_util.wbt_file_add_api_exec(
                        wbt_mails_add_api_exec_result["id"],
                        wbt_mails_add_api_exec_result["attachedFiles"][0]["id"],
                        multi_download_file["json_file"],
                        None,
                        None,
                    )
                except Exception:
                    # 25-02.WBTファイル登録APIからのレスポンスを、「変数．WBTファイル登録API実行結果」に格納する
                    # 25-02-01.WebBureauTransferの処理に失敗した場合、「変数．エラー情報」にエラー情報を作成する
                    wbt_file_add_api_error_info = {
                        "errorCode": "990013",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["990013"]["message"])
                    }
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990013"]["logMessage"], "990013"))

                # 26.共通エラーチェック処理
                # 26-01.以下の引数で共通エラーチェック処理を実行する
                # 26-02 例外が発生した場合、例外処理に遷移
                if wbt_file_add_api_error_info is not None:
                    # WBT送信取り消しAPI実行
                    wbt_send_delete_api_exec = CallbackExecutor(
                        self.common_util.wbt_mail_cancel_exec,
                        wbt_mails_add_api_exec_result["id"]
                    )
                    # API実行履歴登録処理
                    api_history_insert = CallbackExecutor(
                        self.common_util.insert_api_history,
                        commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                        request_body["pdsUserId"],
                        apitypeConstClass.API_TYPE["BATCH_DOWNLOAD"],
                        None,
                        str(self.request.url),
                        json.dumps({"path_param": self.request.path_params, "query_param": self.request.query_params._dict, "header_param": commonUtil.make_headerParam(self.request.headers), "request_body": request_body}),
                        False,
                        multi_download_manage_search_result["query_results"][0][0],
                        commonUtil.get_str_datetime()
                    )
                    # WBT状態管理更新処理
                    update_multi_download_status = CallbackExecutor(
                        self.update_multi_download_status_manage,
                        request_body["requestNo"],
                        common_db_info_response
                    )
                    self.common_util.common_error_check(
                        wbt_file_add_api_error_info,
                        wbt_send_delete_api_exec,
                        api_history_insert,
                        update_multi_download_status
                    )

                # 27.個人情報一括DL通知ファイル削除処理
                # 27-01.「変数．個人情報一括DL通知ファイル」をNullにする
                multi_download_file["json_file"] = None

                # 28.トランザクション作成処理
                # 28-01.「WBT状態管理更新トランザクション」を作成する

                # 29.個人情報一括DL状態管理テーブル更新処理
                # 29-01.メールID結合処理
                if multi_download_loop == 0:
                    join_mail_id = str(wbt_mails_add_api_exec_result["id"])
                else:
                    join_mail_id += (";" + str(wbt_mails_add_api_exec_result["id"]))

                multi_download_manage_mail_id_update_error_info = None
                # 29-02.個人情報一括DL状態管理テーブルを更新する
                multi_download_manage_mail_id_update_result = common_db_connection_resource.update(
                    common_db_connection,
                    SqlConstClass.MULTI_DOWUNLOAD_STATUS_MANAGE_MAIL_ID_UPDATE_SQL,
                    join_mail_id,
                    request_body["requestNo"],
                    request_body["pdsUserId"]
                )
                # 29-03.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
                if not multi_download_manage_mail_id_update_result["result"]:
                    multi_download_manage_mail_id_update_error_info = self.common_util.create_postgresql_log(
                        multi_download_manage_mail_id_update_result["errorObject"],
                        None,
                        None,
                        multi_download_manage_mail_id_update_result["stackTrace"]
                    ).get("errorInfo")

                # 30.共通エラーチェック処理
                # 30-01.以下の引数で共通エラーチェック処理を実行する
                # 30-02 例外が発生した場合、例外処理に遷移
                if multi_download_manage_mail_id_update_error_info is not None:
                    # ロールバック処理
                    rollback_transaction = CallbackExecutor(
                        self.common_util.common_check_postgres_rollback,
                        common_db_connection,
                        common_db_connection_resource
                    )
                    # API実行履歴登録処理
                    api_history_insert = CallbackExecutor(
                        self.common_util.insert_api_history,
                        commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                        request_body["pdsUserId"],
                        apitypeConstClass.API_TYPE["BATCH_DOWNLOAD"],
                        None,
                        str(self.request.url),
                        json.dumps({"path_param": self.request.path_params, "query_param": self.request.query_params._dict, "header_param": commonUtil.make_headerParam(self.request.headers), "request_body": request_body}),
                        False,
                        multi_download_manage_search_result["query_results"][0][0],
                        commonUtil.get_str_datetime()
                    )
                    # WBT状態管理更新処理
                    update_multi_download_status = CallbackExecutor(
                        self.update_multi_download_status_manage,
                        request_body["requestNo"],
                        common_db_info_response
                    )
                    self.common_util.common_error_check(
                        multi_download_manage_mail_id_update_error_info,
                        rollback_transaction,
                        api_history_insert,
                        update_multi_download_status
                    )

                # 31.トランザクションコミット処理
                # 31-01.「WBT状態管理更新トランザクション」をコミットする
                common_db_connection_resource.commit_transaction(common_db_connection)

            # 32.トランザクション作成処理
            # 32-01.「WBT状態管理更新トランザクション」を作成する

            # 33.個人情報一括DL状態管理更新処理
            multi_download_manage_end_update_error_info = None
            # 33-01.個人情報一括DL状態管理テーブルを更新する
            multi_download_manage_end_update_result = common_db_connection_resource.update(
                common_db_connection,
                SqlConstClass.MULTI_DOWUNLOAD_STATUS_MANAGE_EXIT_UPDATE_SQL,
                SystemConstClass.USER_PROFILE_DL_EXEC_END_STATUS,
                commonUtil.get_str_datetime(),
                request_body["requestNo"]
            )
            # 33-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not multi_download_manage_end_update_result["result"]:
                multi_download_manage_end_update_error_info = self.common_util.create_postgresql_log(
                    multi_download_manage_end_update_result["errorObject"],
                    None,
                    None,
                    multi_download_manage_end_update_result["stackTrace"]
                ).get("errorInfo")

            # 34.共通エラーチェック処理
            # 34-01.以下の引数で共通エラーチェック処理を実行する
            # 34-02.例外が発生した場合、例外処理に遷移
            if multi_download_manage_end_update_error_info is not None:
                # API実行履歴登録処理
                api_history_insert = CallbackExecutor(
                    self.common_util.insert_api_history,
                    commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                    request_body["pdsUserId"],
                    apitypeConstClass.API_TYPE["BATCH_DOWNLOAD"],
                    None,
                    str(self.request.url),
                    json.dumps({"path_param": self.request.path_params, "query_param": self.request.query_params._dict, "header_param": commonUtil.make_headerParam(self.request.headers), "request_body": request_body}),
                    False,
                    multi_download_manage_search_result["query_results"][0][0],
                    commonUtil.get_str_datetime()
                )
                # WBT状態管理更新処理
                update_multi_download_status = CallbackExecutor(
                    self.update_multi_download_status_manage,
                    request_body["requestNo"],
                    common_db_info_response
                )
                # ロールバック処理
                rollback_transaction = CallbackExecutor(
                    self.common_util.common_check_postgres_rollback,
                    common_db_connection,
                    common_db_connection_resource
                )
                self.common_util.common_error_check(
                    multi_download_manage_end_update_error_info,
                    rollback_transaction,
                    api_history_insert,
                    update_multi_download_status
                )

            # 35.トランザクションコミット処理
            # 35-01.「WBT状態管理更新トランザクション」をコミットする
            common_db_connection_resource.commit_transaction(common_db_connection)
            common_db_connection_resource.close_connection(common_db_connection)

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

    def update_multi_download_status_manage(
        self,
        inquiry_id: str,
        common_db_info_response: dict,
    ):
        """
        WBT状態管理更新処理

        Args:
            inquiry_id (str): 問い合わせID
            common_db_info_response (dict): 共通DB接続情報
        """
        try:
            # 01.トランザクション作成処理
            # 01-01.「個人情報一括DL状態管理更新処理トランザクション」を作成する
            common_db_secret_info = common_db_info_response["common_db_secret_info"]
            common_db_connection_resource: PostgresDbUtilClass = PostgresDbUtilClass(
                logger=self.logger,
                end_point=common_db_secret_info["host"],
                port=common_db_secret_info["port"],
                user_name=common_db_secret_info["username"],
                password=common_db_secret_info["password"],
                region=SystemConstClass.AWS_CONST["REGION"]
            )
            common_db_connection = common_db_connection_resource.create_connection(
                SystemConstClass.PDS_COMMON_DB_NAME
            )

            # 02.個人情報更新処理
            multi_download_status_manage_update_error_info = None
            # 02-01.個人情報一括DL状態管理テーブルに登録する
            multi_download_status_manage_update_result = common_db_connection_resource.update(
                common_db_connection,
                SqlConstClass.MULTI_DOWUNLOAD_STATUS_MANAGE_EXIT_UPDATE_SQL,
                SystemConstClass.USER_PROFILE_DL_EXEC_ERROR_STATUS,
                commonUtil.get_str_datetime(),
                inquiry_id
            )
            # 02-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not multi_download_status_manage_update_result["result"]:
                multi_download_status_manage_update_error_info = self.common_util.create_postgresql_log(
                    multi_download_status_manage_update_result["errorObject"],
                    None,
                    None,
                    multi_download_status_manage_update_result["stackTrace"]
                ).get("errorInfo")

            # 03.共通エラーチェック処理
            # 03-01.以下の引数で共通エラーチェック処理を実行する
            # 03-02.例外が発生した場合、例外処理に遷移
            if multi_download_status_manage_update_error_info is not None:
                rollback_transaction = CallbackExecutor(
                    self.common_util.common_check_postgres_rollback,
                    common_db_connection,
                    common_db_connection_resource
                )
                self.common_util.common_error_check(
                    multi_download_status_manage_update_error_info,
                    rollback_transaction
                )

            # 04.トランザクションコミット処理
            # 04-01.「個人情報一括DL状態管理更新処理トランザクション」をコミットする
            common_db_connection_resource.commit_transaction(common_db_connection)
            common_db_connection_resource.close_connection(common_db_connection)

            # 05.終了処理
            # 05-01.処理を終了する

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

    async def get_user_profile_info_exec(
        self,
        pds_user_db_secret_info: dict,
        transaction_id: str,
        pds_user_info: dict,
        request_id: str,
        common_db_info_response: dict,
        request_body: dict,
        request: Request,
        tf_operator_id: str
    ):
        """
        個人情報取得処理

        Args:
            pds_user_db_secret_info (dict): PDSユーザDB接続情報
            transaction_id (str): トランザクションID
            pds_user_info (dict): PDSユーザ情報
            request_id (str): 問い合わせNo
            common_db_info_response (dict): 共通DB接続情報
            request_body (dict): リクエストボディ
            request (Request): リクエスト情報
            tf_operator_id (str): TFオペレータID

        Returns:
            dict: 処理結果
        """
        try:
            # 01.PDSユーザDB接続準備処理
            # 01-01.「引数．PDSユーザDB接続情報」を利用して、PDSユーザDBに対してのコネクションを作成する
            pds_user_db_connection_resource: PostgresDbUtilClass = PostgresDbUtilClass(
                logger=self.logger,
                end_point=pds_user_db_secret_info["host"],
                port=pds_user_db_secret_info["port"],
                user_name=pds_user_db_secret_info["username"],
                password=pds_user_db_secret_info["password"],
                region=SystemConstClass.AWS_CONST["REGION"]
            )
            pds_user_db_connection = pds_user_db_connection_resource.create_connection(
                SystemConstClass.PDS_USER_DB_NAME
            )

            # 02.個人情報取得処理
            pds_user_profile_read_error_info = None
            # 02-01.個人情報テーブルからデータを取得し、「変数．個人情報取得結果リスト」に全レコードをタプルのリストとして格納する
            pds_user_profile_read_result = pds_user_db_connection_resource.select_tuple_list(
                pds_user_db_connection,
                SqlConstClass.USER_PROFILE_READ_SQL,
                transaction_id,
                True
            )
            # 02-02.「変数.個人情報取得結果リスト」が1件以外の場合、「変数.個人情報一意検証エラー情報」を作成し、エラー情報をCloudWatchへログ出力する
            if pds_user_profile_read_result["result"] and pds_user_profile_read_result["rowCount"] != 1:
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020004"]["logMessage"], transaction_id))
                pds_user_profile_read_error_info = {
                    "errorCode": "020004",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020004"]["message"], transaction_id)
                }

            # 02-03.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not pds_user_profile_read_result["result"]:
                pds_user_profile_read_error_info = self.common_util.create_postgresql_log(
                    pds_user_profile_read_result["errorObject"],
                    None,
                    None,
                    pds_user_profile_read_result["stackTrace"]
                ).get("errorInfo")

            # 03.共通エラーチェック処理
            # 03-01.以下の引数で共通エラーチェック処理を実行する
            if pds_user_profile_read_error_info is not None:
                return {
                    "result": False,
                    "errorInfo": pds_user_profile_read_error_info
                }

            # 04.個人バイナリ情報取得処理
            # 04-01.個人情報バイナリデータ、個人情報バイナリ分割データからデータを取得し、「変数．個人バイナリ情報取得結果リスト」に全レコードをタプルのリストとして格納する
            pds_user_profile_binary_get_read_target_error_info = None
            pds_user_profile_binary_get_read_target_result = pds_user_db_connection_resource.select_tuple_list(
                pds_user_db_connection,
                SqlConstClass.USER_PROFILE_BINARY_GET_READ_TARGET_SQL,
                transaction_id,
                True
            )

            # 04-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not pds_user_profile_binary_get_read_target_result["result"]:
                pds_user_profile_binary_get_read_target_error_info = self.common_util.create_postgresql_log(
                    pds_user_profile_binary_get_read_target_result["errorObject"],
                    None,
                    None,
                    pds_user_profile_binary_get_read_target_result["stackTrace"]
                ).get("errorInfo")

            # 05.共通エラーチェック処理
            # 05-01.以下の引数で共通エラーチェック処理を実行する
            if pds_user_profile_binary_get_read_target_error_info is not None:
                return {
                    "result": False,
                    "errorInfo": pds_user_profile_binary_get_read_target_error_info
                }

            if commonUtil.is_json(pds_user_profile_read_result["query_results"][0][3]):
                data_out = json.loads(pds_user_profile_read_result["query_results"][0][3])
            else:
                data_out = pds_user_profile_read_result["query_results"][0][3]

            # 06.個人バイナリ情報取得件数チェック処理
            # 06-01.「変数．個人バイナリ情報取得結果リスト」が0件の場合、「07.終了処理」に遷移する
            # 06-02.「変数．個人バイナリ情報取得結果リスト」が1件以上の場合、「08.バイナリ情報格納変数定義処理」に遷移する
            if pds_user_profile_binary_get_read_target_result["rowCount"] == 0:
                # 07.終了処理
                # 07-01.レスポンス情報を作成し、返却する
                return {
                    "result": True,
                    "transactionId": pds_user_profile_read_result["query_results"][0][0],
                    "transactionInfo": {
                        "saveDate": pds_user_profile_read_result["query_results"][0][2].strftime('%Y/%m/%d %H:%M:%S.%f')[:-3],
                        "userId": pds_user_profile_read_result["query_results"][0][1],
                        "data": data_out,
                        "image": None,
                        "imageHash": None,
                        "secureLevel": pds_user_profile_read_result["query_results"][0][4]
                    }
                }
            else:
                # 08.ループ処理用変数初期化処理
                # 08-01.バイナリ情報格納用の変数を定義する
                get_binary_file_exec_list = []
                file_save_path_list = []
                kms_data_key_list = []
                chiper_nonce_list = []
                image_hash_list = []
                binary_item_count = 0

                userProfileUtil = UserProfileUtilClass(self.logger)
                binary_data_item_exit_count = len(pds_user_profile_binary_get_read_target_result["query_results"]) - 1
                for binary_data_loop_no, binary_data_item in enumerate(pds_user_profile_binary_get_read_target_result["query_results"]):
                    # 09.個人情報バイナリデータ．保存画像インデックス判定処理
                    # 09-01.「変数．個人バイナリ情報取得結果リスト[変数．個人情報バイナリデータループ数][1]」が変わった場合、「10．バイナリデータ取得処理リスト作成処理」に遷移する
                    # 09-02.「変数．個人バイナリ情報取得結果リスト[変数．個人情報バイナリデータループ数][1]」が同じ場合、「14．バイナリデータ取得対象追加処理」に遷移する
                    if binary_data_loop_no != 0 and binary_data_item[1] != pds_user_profile_binary_get_read_target_result["query_results"][binary_data_loop_no - 1][1]:
                        # 10.バイナリデータ取得処理リスト作成処理
                        # 10-01.「変数．バイナリデータ取得処理リスト」にバイナリデータ取得処理を追加する
                        get_binary_file_exec_list.append(
                            userProfileUtil.get_binary_data(
                                pdsUserInfo=pds_user_info,
                                fileSavePathList=file_save_path_list,
                                kmsDataKeyList=kms_data_key_list,
                                chiperNonceList=chiper_nonce_list,
                                apiType=apitypeConstClass.API_TYPE["REFERENCE"],
                                request=request,
                                requestBody={}
                            )
                        )
                        # 11.バイナリデータハッシュ値格納リスト追加処理
                        # 11-01.「変数．バイナリデータハッシュ値格納リスト」にハッシュ値を追加する。
                        image_hash_list.append(pds_user_profile_binary_get_read_target_result["query_results"][binary_data_loop_no - 1][3])

                        # 12.バイナリデータ取得対象初期化処理
                        # 12-01.バイナリデータ取得処理の対象を管理している変数を初期化する
                        file_save_path_list = []
                        kms_data_key_list = []
                        chiper_nonce_list = []

                        # 13.バイナリデータ要素数インクリメント処理
                        # 13-01.「変数．バイナリデータ要素数」をインクリメントする
                        binary_item_count += 1

                    # 14.バイナリデータ取得対象追加処理
                    # 14-01.バイナリデータ取得処理の対象を管理している変数に値を追加する
                    file_save_path_list.append(binary_data_item[5])
                    kms_data_key_list.append(binary_data_item[6])
                    chiper_nonce_list.append(binary_data_item[7])

                    # 15.ループ終了判定処理
                    # 15-01.「変数．個人情報バイナリデータループ数」と「変数．個人情報バイナリ情報取得結果リスト」の要素数が一致する場合、「16．バイナリデータ取得処理リスト作成処理」に遷移する
                    # 15-02.「変数．個人情報バイナリデータループ数」と「変数．個人情報バイナリ情報取得結果リスト」の要素数が一致しない場合、繰り返し処理を続行する
                    if binary_data_loop_no == binary_data_item_exit_count:
                        # 16.バイナリデータ取得処理リスト作成処理
                        # 16-01.「変数．バイナリデータ取得処理リスト」にバイナリデータ取得処理を追加する
                        get_binary_file_exec_list.append(
                            userProfileUtil.get_binary_data(
                                pdsUserInfo=pds_user_info,
                                fileSavePathList=file_save_path_list,
                                kmsDataKeyList=kms_data_key_list,
                                chiperNonceList=chiper_nonce_list,
                                apiType=apitypeConstClass.API_TYPE["REFERENCE"],
                                request=request,
                                requestBody={}
                            )
                        )

                        # 17.バイナリデータハッシュ値格納リスト追加処理
                        # 17-01.「変数．バイナリデータハッシュ値格納リスト」にハッシュ値を追加する。
                        image_hash_list.append(binary_data_item[3])

                # 18.バイナリデータ取得処理実行処理
                # 18-01.バイナリデータ取得処理実行処理「変数．バイナリデータ取得処理リスト」をもとに、バイナリデータ取得処理を並列で実行する
                # 18-02.レスポンスを「変数．バイナリデータ取得処理実行結果リスト」に格納する
                get_binary_data_result_list = await asyncio.gather(*get_binary_file_exec_list, return_exceptions=True)

                # 19.バイナリデータ取得処理実行チェック処理
                error_info_list = []
                exception_list = [d for d in get_binary_data_result_list if type(d) is PDSException]
                if len(exception_list) > 0:
                    for exception in exception_list:
                        for error in exception.error_info_list:
                            error_info_list.append(error)

                result_list = [d.get("result") for d in get_binary_data_result_list if type(d) is dict]
                if False in result_list:
                    for result_info in get_binary_data_result_list:
                        if result_info.get("errorInfo"):
                            if type(result_info["errorInfo"]) is list:
                                error_info_list.extend(result_info["errorInfo"])
                            else:
                                error_info_list.append(result_info["errorInfo"])
                if len(error_info_list) > 0:
                    # 19.バイナリデータ取得処理実行エラー処理
                    return {
                        "result": False,
                        "errorInfo": error_info_list
                    }

                # 19.終了処理
                # 19-01.返却パラメータを作成し、返却する
                binary_data_list = [d.get("binaryData") for d in get_binary_data_result_list]
                return {
                    "result": True,
                    "transactionId": pds_user_profile_read_result["query_results"][0][0],
                    "transactionInfo": {
                        "saveDate": pds_user_profile_read_result["query_results"][0][2].strftime('%Y/%m/%d %H:%M:%S.%f')[:-3],
                        "userId": pds_user_profile_read_result["query_results"][0][1],
                        "data": data_out,
                        "image": binary_data_list,
                        "imageHash": image_hash_list,
                        "secureLevel": pds_user_profile_read_result["query_results"][0][4]
                    }
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
