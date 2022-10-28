from typing import Optional, Union
import json
from pydantic import BaseModel
from fastapi import Request
from logging import Logger
import traceback
import asyncio

## コールバック関数
from util.callbackExecutorUtil import CallbackExecutor
# Exception
from exceptionClass.PDSException import PDSException

# Const
from const.messageConst import MessageConstClass
from const.apitypeConst import apitypeConstClass
from const.sqlConst import SqlConstClass

# Util
import util.logUtil as logUtil
import util.commonUtil as commonUtil
from util.commonUtil import CommonUtilClass
from util.mongoDbUtil import MongoDbClass
from util.userProfileUtil import UserProfileUtilClass
from util.postgresDbUtil import PostgresDbUtilClass


class userInfo(BaseModel):
    saveDate: Optional[str] = None
    userId: Optional[str] = None
    data: Optional[str] = None
    image: Union[Optional[str], Optional[list]] = None
    imageHash: Union[Optional[str], Optional[list]] = None
    secureLevel: Optional[str] = None


class requestBody(BaseModel):
    """
    リクエストボディクラス
    """
    tid: Optional[str] = None
    info: Optional[userInfo] = None


class createModel():

    def __init__(self, logger: Logger, request: Request, pds_user_id: str, pds_user_info, pds_user_domain_name: str):
        self.logger: Logger = logger
        self.request: Request = request
        self.pds_user_id: str = pds_user_id
        self.common_util = CommonUtilClass(logger)
        self.pds_user_info = pds_user_info
        self.pds_user_domain_name = pds_user_domain_name

    async def main(self, request_body: requestBody):
        """
        メイン処理

        Args:
            request_body (object): リクエストボディ

        Returns:
            dict: メイン処理実行結果
        """
        try:
            # 02.PDSユーザDB接続準備処理
            # 02-01.以下の引数でPDSユーザDBの接続情報をAWSのSecrets Managerから取得する
            # 02-02.取得したPDSユーザDBの接続情報を、「変数．PDSユーザDB接続情報」に格納する
            # 02-03.「変数．PDSユーザDB接続情報」を利用して、PDSユーザDBに対してのコネクションを作成する
            rds_db_secret_name = self.pds_user_info["pdsUserInstanceSecretName"]
            pds_user_db_connection_resource: PostgresDbUtilClass = None
            pds_user_db_info_response = self.common_util.get_pds_user_db_info_and_connection(rds_db_secret_name)
            if not pds_user_db_info_response["result"]:
                raise PDSException(pds_user_db_info_response.get("errorInfo"))
            else:
                pds_user_db_secret_info = pds_user_db_info_response["pds_user_db_secret_info"]
                pds_user_db_connection_resource = pds_user_db_info_response["pds_user_db_connection_resource"]
                pds_user_db_connection = pds_user_db_info_response["pds_user_db_connection"]

            # 03.個人情報取得処理
            pds_user_check_error_info = None
            # 03-01.個人情報テーブルからデータを取得し、「変数．個人情報取得結果リスト」に全レコードをタプルのリストとして格納する
            pds_user_check_result = pds_user_db_connection_resource.select_tuple_list(
                pds_user_db_connection,
                SqlConstClass.USER_PROFILE_SELECT_CHECK_SQL,
                request_body.tid
            )
            # 03-02.「変数．個人情報取得結果リスト」の件数が0件以外の場合、「変数．エラー情報」を作成し、エラー情報をCloudWatchへログ出力する
            if pds_user_check_result["result"] and pds_user_check_result["rowCount"] != 0:
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["030001"]["logMessage"], "トランザクションID", request_body.tid))
                pds_user_check_error_info = {
                    "errorCode": "030001",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["030001"]["message"], "トランザクションID", request_body.tid)
                }

            # 03-03.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not pds_user_check_result["result"]:
                pds_user_check_error_info = self.common_util.create_postgresql_log(
                    pds_user_check_result["errorObject"],
                    None,
                    None,
                    pds_user_check_result["stackTrace"]
                ).get("errorInfo")

            # 04.共通エラーチェック処理
            # 04-01.以下の引数で共通エラーチェック処理を実行する
            if pds_user_check_error_info is not None:
                # API実行履歴登録処理
                api_history_insert = CallbackExecutor(
                    self.common_util.insert_api_history,
                    commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                    self.pds_user_info["pdsUserId"],
                    apitypeConstClass.API_TYPE["REGISTER"],
                    self.pds_user_domain_name,
                    str(self.request.url),
                    json.dumps({"path_param": self.request.path_params, "query_param": self.request.query_params._dict, "header_param": commonUtil.make_headerParam(self.request.headers), "request_body": request_body.dict()}),
                    False,
                    None,
                    commonUtil.get_str_datetime()
                )
                # 04-02.例外が発生した場合、例外処理に遷移
                self.common_util.common_error_check(
                    pds_user_check_error_info,
                    api_history_insert
                )

            # 05.MongoDB接続準備処理
            # 05-01.プログラムが配置されているリージョンのAZaのMongoDBの接続情報をAWSのSecrets Managerから取得する
            # 05-01-01.下記の引数で、AZaのMongoDB接続情報を取得する
            # 05-01-02.取得したMongoDBの接続情報を、「変数．MongoDB接続情報」に格納する
            # 05-02.「05-01」の処理に失敗した場合、プログラムが配置されているリージョンのAZcのMongoDBの接続情報をAWSのSecrets Managerから取得する
            # 05-02-01.プログラムが配置されているリージョンのAZcのMongoDBの接続情報をAWSのSecrets Managerから取得する
            # 05-02-02.取得したMongoDBの接続情報を、「変数．MongoDB接続情報」に格納する
            mongo_info_result = self.common_util.get_mongo_db_info_and_connection(
                self.pds_user_info["tokyo_a_mongodb_secret_name"],
                self.pds_user_info["tokyo_c_mongodb_secret_name"],
                self.pds_user_info["osaka_a_mongodb_secret_name"],
                self.pds_user_info["osaka_c_mongodb_secret_name"]
            )
            mongo_db_util: MongoDbClass = mongo_info_result["mongo_db_util"]

            # 06.MongoDBトランザクション作成処理
            # 06-01.「MongoDB個人情報登録トランザクション」を作成する
            mongo_db_util.create_session()
            mongo_db_util.create_transaction()

            # 07.保存したいデータ形式判定処理
            # 07-01.「リクエストのリクエストボディ．保存したいデータ」がJson形式の場合、「変数．Jsonデータフラグ」にtrueを格納し、「08.MongoDB接続準備処理」に遷移する
            # 07-02.「リクエストのリクエストボディ．保存したいデータ」がJson形式でない場合、「変数．Jsonデータフラグ」にfalseを格納し、「10.トランザクション作成処理」に遷移する
            if commonUtil.is_json(request_body.info.data):
                json_data_flg = True

                # 08.MongoDB登録処理
                mongo_insert_error_info = None
                # 08-01.保存データテーブルに、「リクエストのリクエストボディ．情報．保存したいデータ」を登録する
                # 08-02.登録したデータのMongoDBのObjectidを取得し、「変数．データ格納用MongoDBキー」に格納する
                if type(request_body.info.data) is str:
                    mongo_insert_result = mongo_db_util.insert_document(json.loads(request_body.info.data))
                if type(request_body.info.data) is dict:
                    mongo_insert_result = mongo_db_util.insert_document(request_body.info.data)
                # 08-03.処理が失敗した場合は「変数．エラー情報」を作成し、エラーログをCloudWatchにログ出力する
                if not mongo_insert_result["result"]:
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["992001"]["logMessage"], mongo_insert_result["errorCode"], mongo_insert_result["message"]))
                    mongo_insert_error_info = {
                        "errorCode": "992001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["992001"]["message"], "992001")
                    }
                # 09.共通エラーチェック処理
                # 09-01.以下の引数で共通エラーチェック処理を実行する
                if mongo_insert_error_info is not None:
                    # MongoDBロールバック処理
                    mongo_db_rollback = CallbackExecutor(
                        self.common_util.common_check_mongo_rollback,
                        mongo_db_util
                    )
                    # API実行履歴登録処理
                    api_history_insert = CallbackExecutor(
                        self.common_util.insert_api_history,
                        commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                        self.pds_user_info["pdsUserId"],
                        apitypeConstClass.API_TYPE["REGISTER"],
                        self.pds_user_domain_name,
                        str(self.request.url),
                        json.dumps({"path_param": self.request.path_params, "query_param": self.request.query_params._dict, "header_param": commonUtil.make_headerParam(self.request.headers), "request_body": request_body.dict()}),
                        False,
                        None,
                        commonUtil.get_str_datetime()
                    )
                    # 09-02.例外が発生した場合、例外処理に遷移
                    self.common_util.common_error_check(
                        mongo_insert_error_info,
                        mongo_db_rollback,
                        api_history_insert
                    )
                # データ登録用変数作成
                insert_object_id = mongo_insert_result["objectId"]
                data_str = request_body.info.data
                if type(request_body.info.data) is str:
                    data_str = request_body.info.data
                if type(request_body.info.data) is dict:
                    data_str = json.dumps(request_body.info.data)
            else:
                # データ登録用変数作成
                json_data_flg = False
                insert_object_id = None
                data_str = request_body.info.data

            # 10.トランザクション作成処理
            # 10-01.「個人情報登録トランザクション」を作成する

            # 11.個人情報登録処理
            pds_user_profile_insert_error_info = None
            # 11-01.個人情報テーブルに登録する
            pds_user_profile_insert_result = pds_user_db_connection_resource.insert(
                pds_user_db_connection,
                SqlConstClass.USER_PROFILE_INSERT_SQL,
                request_body.tid,
                request_body.info.userId,
                request_body.info.saveDate,
                json_data_flg,
                insert_object_id,
                data_str,
                request_body.info.secureLevel,
                False,
                commonUtil.get_datetime_jst()
            )

            # 11-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not pds_user_profile_insert_result["result"]:
                pds_user_profile_insert_error_info = self.common_util.create_postgresql_log(
                    pds_user_profile_insert_result["errorObject"],
                    "トランザクションID",
                    request_body.tid,
                    pds_user_profile_insert_result["stackTrace"]
                ).get("errorInfo")

            # 12.共通エラーチェック処理
            # 12-01.以下の引数で共通エラーチェック処理を実行する
            if pds_user_profile_insert_error_info is not None:
                # ロールバック処理
                rollback_transaction = CallbackExecutor(
                    self.common_util.common_check_postgres_rollback,
                    pds_user_db_connection,
                    pds_user_db_connection_resource
                )
                # MongoDBロールバック処理
                mongo_db_rollback = CallbackExecutor(
                    self.common_util.common_check_mongo_rollback,
                    mongo_db_util
                )
                # API実行履歴登録処理
                api_history_insert = CallbackExecutor(
                    self.common_util.insert_api_history,
                    commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                    self.pds_user_info["pdsUserId"],
                    apitypeConstClass.API_TYPE["REGISTER"],
                    self.pds_user_domain_name,
                    str(self.request.url),
                    json.dumps({"path_param": self.request.path_params, "query_param": self.request.query_params._dict, "header_param": commonUtil.make_headerParam(self.request.headers), "request_body": request_body.dict()}),
                    False,
                    None,
                    commonUtil.get_str_datetime()
                )
                # 12-02.例外が発生した場合、例外処理に遷移
                self.common_util.common_error_check(
                    pds_user_profile_insert_error_info,
                    rollback_transaction,
                    mongo_db_rollback,
                    api_history_insert
                )

            # 13.MongoDBトランザクションコミット処理
            # 13-01.「MongoDB個人情報登録トランザクション」をコミットする
            mongo_db_util.commit_transaction()
            mongo_db_util.close_session()
            mongo_db_util.close_mongo()

            # 14.トランザクションコミット処理
            # 14-01.「個人情報登録トランザクション」をコミットする
            pds_user_db_connection_resource.commit_transaction(pds_user_db_connection)

            # 15.個人情報バイナリデータ取得処理
            # 15-01.以下の引数で個人情報バイナリデータ取得処理を実行する
            # 15-02.個人情報バイナリデータ取得処理からのレスポンスを、「変数．個人情報バイナリデータ取得処理実行結果」に格納する
            binary_data_acquisition_exec_result = await self.user_profile_binary_data_acquisition_exec(
                request_body=request_body,
                kms_id=self.pds_user_info["userProfilerKmsId"],
                bucket_name=self.pds_user_info["s3ImageDataBucketName"],
                pds_user_db_secret_info=pds_user_db_secret_info
            )

            # 16.共通エラーチェック処理
            # 16-01.以下の引数で共通エラーチェック処理を実行する
            if not binary_data_acquisition_exec_result["result"]:
                # 個人情報削除バッチキュー発行処理
                transaction_delete_batch_queue_issue = CallbackExecutor(
                    self.common_util.transaction_delete_batch_queue_issue,
                    request_body.tid,
                    self.pds_user_info["pdsUserId"]
                )
                # API実行履歴登録処理
                api_history_insert = CallbackExecutor(
                    self.common_util.insert_api_history,
                    commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                    self.pds_user_info["pdsUserId"],
                    apitypeConstClass.API_TYPE["REGISTER"],
                    self.pds_user_domain_name,
                    str(self.request.url),
                    json.dumps({"path_param": self.request.path_params, "query_param": self.request.query_params._dict, "header_param": commonUtil.make_headerParam(self.request.headers), "request_body": request_body.dict()}),
                    False,
                    None,
                    commonUtil.get_str_datetime()
                )
                # 16-02.例外が発生した場合、例外処理に遷移
                self.common_util.common_error_check(
                    binary_data_acquisition_exec_result["errorInfo"],
                    transaction_delete_batch_queue_issue,
                    api_history_insert
                )

            # 17.トランザクション作成処理
            # 17-01.「個人情報更新トランザクション」を作成する

            # 18.個人情報更新処理
            pds_user_profile_update_error_info = None
            # 18-01.個人情報テーブルを更新する
            pds_user_profile_update_result = pds_user_db_connection_resource.update(
                pds_user_db_connection,
                SqlConstClass.USER_PROFILE_VALID_FLG_UPDATE_SQL,
                request_body.tid,
                False
            )

            # 18-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not pds_user_profile_update_result["result"]:
                pds_user_profile_update_error_info = self.common_util.create_postgresql_log(
                    pds_user_profile_update_result["errorObject"],
                    None,
                    None,
                    pds_user_profile_update_result["stackTrace"]
                ).get("errorInfo")

            # 19.共通エラーチェック処理
            # 19-01.以下の引数で共通エラーチェック処理を実行する
            if pds_user_profile_update_error_info is not None:
                # ロールバック処理
                rollback_transaction = CallbackExecutor(
                    self.common_util.common_check_postgres_rollback,
                    pds_user_db_connection,
                    pds_user_db_connection_resource
                )
                # 個人情報削除バッチキュー発行処理
                transaction_delete_batch_queue_issue = CallbackExecutor(
                    self.common_util.transaction_delete_batch_queue_issue,
                    request_body.tid,
                    self.pds_user_info["pdsUserId"]
                )
                # API実行履歴登録処理
                api_history_insert = CallbackExecutor(
                    self.common_util.insert_api_history,
                    commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                    self.pds_user_info["pdsUserId"],
                    apitypeConstClass.API_TYPE["REGISTER"],
                    self.pds_user_domain_name,
                    str(self.request.url),
                    json.dumps({"path_param": self.request.path_params, "query_param": self.request.query_params._dict, "header_param": commonUtil.make_headerParam(self.request.headers), "request_body": request_body.dict()}),
                    False,
                    None,
                    commonUtil.get_str_datetime()
                )
                # 19-02.例外が発生した場合、例外処理に遷移
                self.common_util.common_error_check(
                    pds_user_profile_update_error_info,
                    rollback_transaction,
                    transaction_delete_batch_queue_issue,
                    api_history_insert
                )

            # 20.トランザクションコミット処理
            # 20-01.「個人情報更新トランザクション」をコミットする
            pds_user_db_connection_resource.commit_transaction(pds_user_db_connection)
            pds_user_db_connection_resource.close_connection(pds_user_db_connection)

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

    async def user_profile_binary_data_acquisition_exec(
        self,
        request_body: requestBody,
        kms_id: str,
        bucket_name: str,
        pds_user_db_secret_info: dict
    ):
        """
        個人情報バイナリデータ取得処理

        Args:
            request_body (requestBody): リクエストボディ
            kms_id (str): 個人情報暗号・復号化用KMSID
            bucket_name (str): バケット名
            pds_user_db_connection_info (dict): PDSユーザDB接続情報
        """
        try:
            user_profile_binary_insert_task_list = []
            userProfileUtil = UserProfileUtilClass(self.logger)
            # バイナリデータを変換
            if request_body.info.image is None:
                binary_data_list = []
            elif type(request_body.info.image) is not list:
                binary_data_list = [request_body.info.image]
            else:
                binary_data_list = request_body.info.image

            # バイナリデータのハッシュ値を変換
            if request_body.info.imageHash is None:
                hash_list = []
            elif type(request_body.info.imageHash) is not list:
                hash_list = [request_body.info.imageHash]
            else:
                hash_list = request_body.info.imageHash

            for idx, binary_data in enumerate(binary_data_list):
                # 01.バイナリデータ情報取得処理
                # 01-01.バイナリデータ登録に必要な情報を、「変数．バイナリデータ情報」に格納する
                binary_data_info = {}
                binary_data_info["transaction_id"] = request_body.tid
                binary_data_info["save_image_idx"] = idx
                binary_data_info["save_image_data"] = binary_data
                binary_data_info["save_image_data_hash"] = hash_list[idx]
                binary_data_info["valid_flg"] = True
                binary_data_info["save_image_data_array_index"] = idx

                # 02.個人情報バイナリデータ登録処理リスト作成処理
                # 02-01.「変数．個人情報バイナリデータ登録処理リスト」に個人情報バイナリデータ登録処理を追加する
                user_profile_binary_insert_task_list.append(
                    userProfileUtil.insert_binary_data(
                        binaryInsertData=binary_data_info,
                        userProfileKmsId=kms_id,
                        bucketName=bucket_name,
                        pdsUserDbInfo=pds_user_db_secret_info
                    )
                )

            # 03.個人情報バイナリデータ登録処理実行処理
            # 03-01.「変数．個人情報バイナリデータ登録処理リスト」をもとに、個人情報バイナリデータ登録処理を並列で実行する
            # 03-02.レスポンスを「変数．個人情報バイナリデータ登録処理実行結果リスト」に格納する
            insert_binary_data_result_list = await asyncio.gather(*user_profile_binary_insert_task_list)

            # 04.個人情報バイナリデータ登録処理実行チェック処理
            result_list = [d.get("result") for d in insert_binary_data_result_list]
            # 04.個人情報バイナリデータ登録処理実行チェック処理
            # 04-01.「変数．個人情報バイナリデータ登録処理実行結果リスト[]．処理結果」にfalseが存在する場合、「05.個人情報バイナリデータ登録処理実行エラー処理」に遷移する
            # 04-02.「変数．個人情報バイナリデータ登録処理実行結果リスト[]．処理結果」にfalseが存在しない場合、「06.終了処理」に遷移する
            if False in result_list:
                # 05.個人情報バイナリデータ登録処理実行エラー処理
                # 05-01.返却パラメータを作成し、返却する
                errorInfoList = []
                for result_info in insert_binary_data_result_list:
                    if result_info.get("errorInfo"):
                        errorInfoList.append(result_info["errorInfo"])

                return {
                    "result": False,
                    "errorInfo": errorInfoList
                }
            else:
                # 06.終了処理
                # 06-01.返却パラメータを作成し、返却する
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
