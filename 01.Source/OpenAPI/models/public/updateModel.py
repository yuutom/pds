from typing import Optional, Union
import json
from pydantic import BaseModel
from fastapi import Request
from logging import Logger
import traceback

## コールバック関数
from util.callbackExecutorUtil import CallbackExecutor
# Exception
from exceptionClass.PDSException import PDSException

# Const
from const.systemConst import SystemConstClass
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


class updateModel():

    def __init__(self, logger: Logger, request: Request, pds_user_id: str, pds_user_info, pds_user_domain_name: str, info_item_flg_dict: dict):
        self.logger: Logger = logger
        self.request: Request = request
        self.pds_user_id: str = pds_user_id
        self.common_util = CommonUtilClass(logger)
        self.pds_user_info = pds_user_info
        self.pds_user_domain_name = pds_user_domain_name
        self.info_item_flg_dict = info_item_flg_dict

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
                raise pds_user_db_info_response["errorInfo"]
            else:
                pds_user_db_secret_info = pds_user_db_info_response["pds_user_db_secret_info"]
                pds_user_db_connection_resource = pds_user_db_info_response["pds_user_db_connection_resource"]
                pds_user_db_connection = pds_user_db_info_response["pds_user_db_connection"]

            # 03.個人情報取得処理
            user_profile_search_error_info = None
            # 03-01.個人情報テーブルからデータを取得し、「変数．個人情報取得結果リスト」に全レコードをタプルのリストとして格納する
            user_profile_search_result = pds_user_db_connection_resource.select_tuple_list(
                pds_user_db_connection,
                SqlConstClass.USER_PROFILE_SEARCH_SELECT_SQL,
                request_body.tid
            )
            # 03-02.「変数．個人情報取得結果リスト」の件数が1件以外の場合、「変数．エラー情報」を作成し、エラー情報をCloudWatchへログ出力する
            if user_profile_search_result["result"] and user_profile_search_result["rowCount"] != 1:
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["030015"]["logMessage"], "個人情報", request_body.tid))
                user_profile_search_error_info = {
                    "errorCode": "030015",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["030015"]["message"], "個人情報", request_body.tid)
                }
            # 03-03.「変数．個人情報検索結果リスト[3]」がfalseの場合、「変数．エラー情報」を作成する
            if user_profile_search_result["result"] and user_profile_search_result["rowCount"] != 0 and not user_profile_search_result["query_results"][0][3]:
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020023"]["logMessage"]))
                user_profile_search_error_info = {
                    "errorCode": "020023",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020023"]["message"])
                }
            # 03-04.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not user_profile_search_result["result"]:
                user_profile_search_error_info = self.common_util.create_postgresql_log(
                    user_profile_search_result["errorObject"],
                    None,
                    None,
                    user_profile_search_result["stackTrace"]
                ).get("errorInfo")

            # 04.共通エラーチェック処理
            # 04-01.以下の引数で共通エラーチェック処理を実行する
            if user_profile_search_error_info is not None:
                # API実行履歴登録処理
                api_history_insert = CallbackExecutor(
                    self.common_util.insert_api_history,
                    commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                    self.pds_user_info["pdsUserId"],
                    apitypeConstClass.API_TYPE["UPDATE"],
                    self.pds_user_domain_name,
                    str(self.request.url),
                    json.dumps({"path_param": self.request.path_params, "query_param": self.request.query_params._dict, "header_param": commonUtil.make_headerParam(self.request.headers), "request_body": request_body.dict()}),
                    False,
                    None,
                    commonUtil.get_str_datetime()
                )
                # 04-02.例外が発生した場合、例外処理に遷移
                self.common_util.common_error_check(
                    user_profile_search_error_info,
                    api_history_insert
                )

            # 05.個人情報更新処理
            # 05-01.個人情報更新処理を実行する
            # 05-02.レスポンスを「変数．個人情報更新結果」に格納する
            user_info_update_result = await self.update_user_info(
                request_body=request_body,
                pds_user_info=self.pds_user_info,
                mongodb_key=user_profile_search_result["query_results"][0][1],
                pds_user_db_secret_info=pds_user_db_secret_info,
                request_info=self.request,
                get_user_profile_data_result=user_profile_search_result["query_results"]
            )

            # 06.SQS実行判定処理
            # 06-01.「変数．個人情報更新結果．SQS実行フラグ」がtrueの場合、「07.個人情報削除バッチキュー発行処理」に遷移する
            # 06-02.「変数．個人情報更新結果．SQS実行フラグ」がfalseの場合、「08.アクセストークン発行処理」に遷移する
            if user_info_update_result["sqs_exec_flg"]:
                # 07.個人情報削除バッチキュー発行処理
                # 07-01.以下の引数で個人情報削除バッチキュー発行処理を実行する
                self.common_util.transaction_delete_batch_queue_issue(
                    transactionId=request_body.tid,
                    pdsUserId=self.pds_user_id
                )

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

    async def update_user_info(
        self,
        request_body: requestBody,
        pds_user_info: dict,
        mongodb_key: str,
        pds_user_db_secret_info: dict,
        request_info: Request,
        get_user_profile_data_result: list
    ):
        """
        個人情報更新処理

        Args:
            request_body (object): リクエストボディ
            pds_user_info (object): PDSユーザ情報
            mongodb_key (string): データ格納用MongoDBキー
            pds_user_db_secret_info (dict): PDSユーザDB接続情報,
            request_info(object): リクエスト情報
            pds_user_search_result(list): 個人情報検索結果リスト
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

            # 02.個人情報バイナリ情報取得処理
            get_binary_data_error_info = None
            # 02-01.個人情報バイナリデータを取得し、「変数．個人情報バイナリ情報取得結果リスト」に全レコードをタプルのリストとして格納する
            get_binary_data_result = pds_user_db_connection_resource.select_tuple_list(
                pds_user_db_connection,
                SqlConstClass.USER_PROFILE_BINARY_SEARCH_SELECT_SQL,
                request_body.tid,
                True
            )
            # 02-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not get_binary_data_result["result"]:
                get_binary_data_error_info = self.common_util.create_postgresql_log(
                    get_binary_data_result["errorObject"],
                    None,
                    None,
                    get_binary_data_result["stackTrace"]
                ).get("errorInfo")

            # 03.共通エラーチェック処理
            # 03-01.以下の引数で共通エラーチェック処理を実行する
            if get_binary_data_error_info is not None:
                # API実行履歴登録処理
                api_history_insert = CallbackExecutor(
                    self.common_util.insert_api_history,
                    commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                    pds_user_info["pdsUserId"],
                    apitypeConstClass.API_TYPE["UPDATE"],
                    self.pds_user_domain_name,
                    str(request_info.url),
                    json.dumps({"path_param": request_info.path_params, "query_param": request_info.query_params._dict, "header_param": commonUtil.make_headerParam(request_info.headers), "request_body": request_body.dict()}),
                    False,
                    None,
                    commonUtil.get_str_datetime()
                )
                # 03-02.例外が発生した場合、例外処理に遷移
                self.common_util.common_error_check(
                    get_binary_data_error_info,
                    api_history_insert
                )

            # 04.個人情報バイナリ最大値取得処理
            get_binary_data_max_error_info = None
            # 04-01.個人情報バイナリデータを取得し、「変数．個人情報バイナリ情報取得結果リスト」に1レコードをタプルとして格納する
            get_binary_data_max_result = pds_user_db_connection_resource.select_tuple_one(
                pds_user_db_connection,
                SqlConstClass.USER_PROFILE_BINARY_SEARCH_MAX_SELECT_SQL,
                request_body.tid
            )
            # 04-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not get_binary_data_max_result["result"]:
                get_binary_data_max_error_info = self.common_util.create_postgresql_log(
                    get_binary_data_max_result["errorObject"],
                    None,
                    None,
                    get_binary_data_max_result["stackTrace"]
                ).get("errorInfo")

            # 05.共通エラーチェック処理
            # 05-01.以下の引数で共通エラーチェック処理を実行する
            if get_binary_data_max_error_info is not None:
                # API実行履歴登録処理
                api_history_insert = CallbackExecutor(
                    self.common_util.insert_api_history,
                    commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                    pds_user_info["pdsUserId"],
                    apitypeConstClass.API_TYPE["UPDATE"],
                    self.pds_user_domain_name,
                    str(request_info.url),
                    json.dumps({"path_param": request_info.path_params, "query_param": request_info.query_params._dict, "header_param": commonUtil.make_headerParam(request_info.headers), "request_body": request_body.dict()}),
                    False,
                    None,
                    commonUtil.get_str_datetime()
                )
                # 05-02.例外が発生した場合、例外処理に遷移
                self.common_util.common_error_check(
                    get_binary_data_max_error_info,
                    api_history_insert
                )

            # 06.バイナリデータの配列への変換処理
            if get_binary_data_result["rowCount"] == 0:
                results_column_list = [[], [], [], []]
                # 取得した保存画像インデックスをもとに「変数．保存画像インデックスリスト」を作成する
                save_image_idx_list = []
                # 取得した保存画像データIDをもとに「変数．保存画像データIDリスト」を作成する
                save_image_data_id_list = []
            else:
                results_column_list = [list(tup) for tup in zip(*get_binary_data_result["query_results"])]
                # 取得した保存画像インデックスをもとに「変数．保存画像インデックスリスト」を作成する
                save_image_idx_list = results_column_list[0]
                # 取得した保存画像データIDをもとに「変数．保存画像データIDリスト」を作成する
                save_image_data_id_list = results_column_list[1]
            # 変数初期化
            image_list = []
            image_hash_list = []
            # 06-01.「引数．リクエストボディ．情報．保存したいデータ」が文字列型である場合、要素1の配列型に変換する
            if not self.info_item_flg_dict["image"]:
                image_list = [False]
            elif request_body.info.image is None:
                image_list = [None]
            elif type(request_body.info.image) is str:
                image_list = [request_body.info.image]
            else:
                image_list = request_body.info.image
            update_image_list = image_list
            # 06-02.「引数．リクエストボディ．情報．保存したいデータのハッシュ値」が文字列型である場合、要素1の配列型に変換する
            if not self.info_item_flg_dict["imageHash"]:
                image_hash_list = [False]
            elif request_body.info.imageHash is None:
                image_hash_list = [None]
            elif type(request_body.info.imageHash) is str:
                image_hash_list = [request_body.info.imageHash]
            else:
                image_hash_list = request_body.info.imageHash
            # 06-03.「変数．保存画像データIDリスト」と「引数．リクエストボディ．情報．保存したいデータ」の要素数を比較する
            # 06-03-01.DBから取得したバイナリデータの方が要素数が多い場合、要素数が一致するようリクエストの末尾にfalseを追加する
            if len(save_image_data_id_list) > len(image_list):
                dev = len(save_image_data_id_list) - len(image_list)
                for _ in range(dev):
                    update_image_list.append(False)
            # 06-03-02.「引数．リクエストボディ．情報．保存したいデータ」の方が要素数が多く、DBから取得したバイナリデータの要素を超過する要素番号にNull または 空文字が設定されている場合、Null または 空文字をfalseに置換する
            if len(save_image_data_id_list) < len(image_list):
                data_list_length = len(image_list)
                save_image_data_length = len(save_image_data_id_list)
                for idx in range(save_image_data_length, data_list_length):
                    if image_list[idx] is None or image_list[idx] == "":
                        # 06-03-03.実行結果を「変数．調整後保存したいデータ」に格納する
                        update_image_list[idx] = False

            # 06-04.DBから取得したバイナリデータと調整後リクエストのバイナリデータをもとに、更新用の配列を作成する
            if get_binary_data_max_result["query_results"][0] is None:
                max_save_image_index = -1
            else:
                max_save_image_index = get_binary_data_max_result["query_results"][0]
            # 06-04-01.「変数．調整後保存したいデータ」に対してバイナリデータ配列インデックスを設定し、「変数．調整後配列データ」を作成する
            update_data_list = []
            array_index = 0
            save_image_index_count = 1
            for idx, data in enumerate(update_image_list):
                # 06-04-02.「変数．調整後保存したいデータ」の先頭から順に要素を「変数．調整後配列データ．保存したいバイナリデータ」に格納する
                update_data_list.append({"data": data})
                # 06-04-03.「変数．調整後配列データ．保存したいバイナリデータ」がfalseかつ DBから取得したバイナリデータの要素数を超過している場合、対応するインデックスの「変数．調整後配列データ．バイナリデータ配列インデックス」と「変数．調整後配列データ．保存画像インデックス」をNullとし、連番にカウントしない
                if len(save_image_data_id_list) - 1 < idx and data is False:
                    update_data_list[idx]["array_index"] = None
                    update_data_list[idx]["save_image_index"] = None
                # 06-04-04.「変数．調整後配列データ．保存したいバイナリデータ」がNullまたは空文字の場合、対応するインデックスの「変数．調整後配列データ．バイナリデータ配列インデックス」と「変数．調整後配列データ．保存画像インデックス」をNullとし、連番にカウントしない
                elif data is None or data == "":
                    update_data_list[idx]["array_index"] = None
                    update_data_list[idx]["save_image_index"] = None
                # 06-04-05.「変数．調整後配列データ．保存したいバイナリデータ」がfalse かつDBから取得したバイナリデータの要素数を超過していない場合、対応するインデックスの「変数．調整後配列データ．バイナリデータ配列インデックス」に0からの連番を設定し、「変数．調整後配列データ．保存画像インデックス」に「変数．保存画像インデックスリスト」の値を設定する
                elif data is False:
                    update_data_list[idx]["array_index"] = array_index
                    update_data_list[idx]["save_image_index"] = save_image_idx_list[idx]
                    array_index += 1
                # 06-04-06.上記以外の場合、対応するインデックスの「変数．調整後配列データ．バイナリデータ配列インデックス」に0からの連番を設定し、「変数．調整後配列データ．保存画像インデックス」に「変数．保存画像インデックスリスト」の最大値からの連番を設定する
                else:
                    update_data_list[idx]["array_index"] = array_index
                    update_data_list[idx]["save_image_index"] = max_save_image_index + save_image_index_count
                    array_index += 1
                    save_image_index_count += 1

            # 07.バイナリデータ計算処理
            binary_total_size_error_info = None
            # DBに保存されているバイナリデータのバイト数計算
            db_binary_data_byte_size = 0
            for byte_size in results_column_list[3]:
                if byte_size is not None and type(byte_size) is int:
                    db_binary_data_byte_size += byte_size

            # DBから削除されるバイナリデータのバイト数計算
            delete_binary_data_byte_size = 0
            for idx, update_target in enumerate(update_image_list):
                if update_target is not False and len(results_column_list[3]) > idx:
                    if results_column_list[3][idx] is not None and type(results_column_list[3][idx]) is int:
                        delete_binary_data_byte_size += results_column_list[3][idx]

            # 新規登録されるバイナリデータのバイト数計算
            insert_binary_data_byte_size = 0
            for image_data in image_list:
                if image_data is not None and image_data is not False and type(image_data) is str and image_data != "":
                    insert_binary_data_byte_size += len(image_data)

            # 07-01.バイナリデータの合計が100MBを超過していないか計算する
            total_size = db_binary_data_byte_size + insert_binary_data_byte_size - delete_binary_data_byte_size

            # 07-02.計算結果が140MB（Base64形式でのリクエストのため100MBを1.4倍計算）を超過している場合、エラー情報を作成する
            if total_size > SystemConstClass.USER_PROFILE_BINARY_FILE_BASE64_TOTAL:
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["030018"]["logMessage"]))
                binary_total_size_error_info = {
                    "errorCode": "030018",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["030018"]["message"])
                }

            # 08.共通エラーチェック処理
            # 08-01.以下の引数で共通エラーチェック処理を実行する
            if binary_total_size_error_info is not None:
                # API実行履歴登録処理
                api_history_insert = CallbackExecutor(
                    self.common_util.insert_api_history,
                    commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                    pds_user_info["pdsUserId"],
                    apitypeConstClass.API_TYPE["UPDATE"],
                    self.pds_user_domain_name,
                    str(request_info.url),
                    json.dumps({"path_param": request_info.path_params, "query_param": request_info.query_params._dict, "header_param": commonUtil.make_headerParam(request_info.headers), "request_body": request_body.dict()}),
                    False,
                    None,
                    commonUtil.get_str_datetime()
                )
                # 08-02.例外が発生した場合、例外処理に遷移
                self.common_util.common_error_check(
                    binary_total_size_error_info,
                    api_history_insert
                )

            # 09.SQS実行フラグ定義処理
            # 09-01.SQSを実行するためのフラグを定義する
            sqs_exec_flg = False

            # 10.トランザクション作成処理
            # 10-01.「個人情報更新トランザクション」を作成する

            # 11.個人情報更新実施判定処理
            # 11-01.「変数．調整後保存したいデータ」の内容がすべてfalseの場合、「20.個人情報テーブル更新処理」に遷移する
            # 11-02.「変数．調整後保存したいデータ」の内容にfalse以外を含む場合、「10.保存画像データ更新スキップ判定処理」に遷移する
            binary_update_skip = False
            if all(image is False for image in update_image_list):
                binary_update_skip = True

            inserted_save_image_index_list = []
            if not binary_update_skip:
                for update_data_loop, update_data in enumerate(update_data_list):
                    # 12.保存画像データ更新スキップ判定処理
                    # 12-01.「変数．調整後配列データ[変数．調整後配列データループ数]．保存したいバイナリデータ」がfalseの場合、「11.個人情報バイナリデータスキップ処理」に遷移する
                    # 12-02.「変数．調整後配列データ[変数．調整後配列データループ数]．保存したいバイナリデータ」がfalse以外の場合、「12.保存画像データハッシュ論理削除判定処理」に遷移する
                    if update_data["data"] is False:
                        # 13.個人情報バイナリデータスキップ処理
                        # 13-01.以下の引数で個人情報バイナリデータスキップ処理を実行する
                        # 13-02.レスポンスを「変数．個人情報バイナリデータスキップ処理実行結果」に格納する
                        self.skip_user_profile_binary(
                            request_body=request_body,
                            adjusted_array_data=update_data,
                            save_image_idx=update_data["save_image_index"],
                            pds_user_id=pds_user_info["pdsUserId"],
                            request_info=request_info,
                            pds_user_db_connection_resource=pds_user_db_connection_resource,
                            pds_user_db_connection=pds_user_db_connection
                        )
                    else:
                        # 14.保存画像データハッシュ論理削除判定処理
                        # 14-01.「変数．調整後配列データ[変数．調整後配列データループ数]．保存したいバイナリデータ」がNullか空文字の場合、「13.個人情報バイナリデータ論理削除処理」に遷移する
                        # 14-02.「変数．調整後配列データ[変数．調整後配列データループ数]．保存したいバイナリデータ」がNullか空文字以外の場合、「14.バイナリデータ情報作成処理」に遷移する
                        if update_data["data"] is None or update_data["data"] == "":
                            # 15.個人情報バイナリデータ論理削除処理
                            # 15-01.以下の引数で個人情報バイナリデータ論理削除処理を実行し、「変数．個人情報バイナリデータ論理削除処理実行結果」に格納する
                            # 15-02.レスポンスを「変数．個人情報バイナリデータ論理削除処理実行結果」に格納する
                            self.logical_delete_user_profile_binary(
                                request_body=request_body,
                                save_image_idx=save_image_idx_list[update_data_loop],
                                pds_user_id=pds_user_info["pdsUserId"],
                                request_info=request_info,
                                pds_user_db_connection_resource=pds_user_db_connection_resource,
                                pds_user_db_connection=pds_user_db_connection
                            )
                            # 15-03.「変数．SQS実行フラグ」がfalseの場合、trueに変更する
                            sqs_exec_flg = True
                        else:
                            # 16.バイナリデータ情報作成処理
                            # 16-01.バイナリデータ登録に必要な情報を、「変数．バイナリデータ情報」に格納する
                            binary_data = {
                                "transaction_id": request_body.tid,
                                "save_image_idx": update_data["save_image_index"],
                                "save_image_data": update_data["data"],
                                "save_image_data_hash": image_hash_list[update_data_loop],
                                "valid_flg": False,
                                "save_image_data_array_index": update_data["array_index"],
                            }

                            # 17.個人情報バイナリデータ登録処理
                            userProfileUtil = UserProfileUtilClass(self.logger)
                            # 17-01.以下の引数で個人情報バイナリデータ登録処理を実行する
                            # 17-02.レスポンスを「変数．個人情報バイナリデータ登録処理実行結果」に格納する
                            insert_binary_data_response = await userProfileUtil.insert_binary_data(
                                binaryInsertData=binary_data,
                                userProfileKmsId=pds_user_info["userProfilerKmsId"],
                                bucketName=pds_user_info["s3ImageDataBucketName"],
                                pdsUserDbInfo=pds_user_db_secret_info
                            )
                            # 17-03.「変数．個人情報バイナリデータ登録処理実行結果．保存画像インデックス」を「変数．登録済み保存画像インデックスリスト」の配列に加える
                            if insert_binary_data_response["result"]:
                                inserted_save_image_index_list.append(update_data["save_image_index"])

                            # 18.共通エラーチェック処理
                            # 18-01.以下の引数で共通エラーチェック処理を実行する
                            if not insert_binary_data_response["result"]:
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
                                    pds_user_info["pdsUserId"]
                                )
                                # API実行履歴登録処理
                                api_history_insert = CallbackExecutor(
                                    self.common_util.insert_api_history,
                                    commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                                    self.pds_user_info["pdsUserId"],
                                    apitypeConstClass.API_TYPE["UPDATE"],
                                    self.pds_user_domain_name,
                                    str(request_info.url),
                                    json.dumps({"path_param": request_info.path_params, "query_param": request_info.query_params._dict, "header_param": commonUtil.make_headerParam(request_info.headers), "request_body": request_body.dict()}),
                                    False,
                                    None,
                                    commonUtil.get_str_datetime()
                                )
                                # 18-02.例外が発生した場合、例外処理に遷移
                                self.common_util.common_error_check(
                                    insert_binary_data_response["errorInfo"],
                                    rollback_transaction,
                                    transaction_delete_batch_queue_issue,
                                    api_history_insert
                                )

                            # 19.個人情報バイナリデータ論理削除処理
                            # 19-01.以下の引数で個人情報バイナリデータ論理削除処理を実行し、「変数．個人情報論理削除処理実行結果」に格納する
                            # 19-02.レスポンスを「変数．個人情報バイナリデータ論理削除処理実行結果」に格納する
                            if update_data_loop < len(save_image_data_id_list):
                                self.logical_delete_user_profile_binary(
                                    request_body=request_body,
                                    save_image_idx=save_image_idx_list[update_data_loop],
                                    pds_user_id=pds_user_info["pdsUserId"],
                                    request_info=request_info,
                                    pds_user_db_connection_resource=pds_user_db_connection_resource,
                                    pds_user_db_connection=pds_user_db_connection
                                )
                                # 19-03.「変数．SQS実行フラグ」がfalseの場合、trueに変更する
                                sqs_exec_flg = True

                # 20.個人情報バイナリ情報更新処理
                if len(inserted_save_image_index_list) > 0:
                    update_binary_data_valid_flg_error_info = None
                    # 20-01.個人情報バイナリデータテーブルを更新する
                    update_binary_data_valid_flg_result = pds_user_db_connection_resource.update(
                        pds_user_db_connection,
                        SqlConstClass.UPDATE_USER_PROFILE_BINARY_VALID_FLG_SQL,
                        request_body.tid,
                        tuple(inserted_save_image_index_list),
                        False
                    )
                    # 20-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
                    if not update_binary_data_valid_flg_result["result"]:
                        update_binary_data_valid_flg_error_info = self.common_util.create_postgresql_log(
                            update_binary_data_valid_flg_result["errorObject"],
                            None,
                            None,
                            update_binary_data_valid_flg_result["stackTrace"]
                        ).get("errorInfo")

                    # 21.共通エラーチェック処理
                    # 21-01.以下の引数で共通エラーチェック処理を実行する
                    if update_binary_data_valid_flg_error_info is not None:
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
                            pds_user_info["pdsUserId"]
                        )
                        # API実行履歴登録処理
                        api_history_insert = CallbackExecutor(
                            self.common_util.insert_api_history,
                            commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                            self.pds_user_info["pdsUserId"],
                            apitypeConstClass.API_TYPE["UPDATE"],
                            self.pds_user_domain_name,
                            str(request_info.url),
                            json.dumps({"path_param": request_info.path_params, "query_param": request_info.query_params._dict, "header_param": commonUtil.make_headerParam(request_info.headers), "request_body": request_body.dict()}),
                            False,
                            None,
                            commonUtil.get_str_datetime()
                        )
                        # 21-02.例外が発生した場合、例外処理に遷移
                        self.common_util.common_error_check(
                            update_binary_data_valid_flg_error_info,
                            rollback_transaction,
                            transaction_delete_batch_queue_issue,
                            api_history_insert
                        )

            # 22.MongoDB接続準備処理
            # 22-01.プログラムが配置されているリージョンのAZaのMongoDBの接続情報をAWSのSecrets Managerから取得する
            # 22-01-01.下記の引数で、AZaのMongoDB接続情報を取得する
            # 22-01-02.取得したMongoDBの接続情報を、「変数．MongoDB接続情報」に格納する
            # 22-02.「20-01」の処理に失敗した場合、プログラムが配置されているリージョンのAZcのMongoDBの接続情報をAWSのSecrets Managerから取得する
            # 22-02-01.プログラムが配置されているリージョンのAZcのMongoDBの接続情報をAWSのSecrets Managerから取得する
            # 22-02-02.取得したMongoDBの接続情報を、「変数．MongoDB接続情報」に格納する
            mongo_info_result = self.common_util.get_mongo_db_info_and_connection(
                self.pds_user_info["tokyo_a_mongodb_secret_name"],
                self.pds_user_info["tokyo_c_mongodb_secret_name"],
                self.pds_user_info["osaka_a_mongodb_secret_name"],
                self.pds_user_info["osaka_c_mongodb_secret_name"]
            )
            mongo_db_util: MongoDbClass = mongo_info_result["mongo_db_util"]

            # 23.MongoDBトランザクション作成処理
            # 23-01.「MongoDB個人情報更新トランザクション」を作成する
            mongo_db_util.create_session()
            mongo_db_util.create_transaction()

            # 24.MongoDB登録判定処理
            json_data_flg = False
            # 24-01.「リクエストのリクエストボディ．情報．保存したいデータ」がJson形式か判定する
            # 24-02.「リクエストのリクエストボディ．情報．保存したいデータ」がJson形式でない場合、「変数．Jsonデータフラグ」をfalseにする
            # 24-03.「リクエストのリクエストボディ．情報．保存したいデータ」がJson形式である場合、「変数．Jsonデータフラグ」をtrueにする
            if commonUtil.is_json(request_body.info.data):
                json_data_flg = True
                # 25.MongoDB登録処理
                mongo_db_insert_error_info = None
                # 25-01.保存データテーブルに、「引数．リクエストボディ．情報．保存したいデータ」を登録する
                mongo_db_insert_result = mongo_db_util.insert_document(json.loads(request_body.info.data))
                # 25-02.登録したMongoのObjectidを取得し、「変数．データ格納用MongoDBキー」に格納する
                if mongo_db_insert_result["result"]:
                    insert_object_id = mongo_db_insert_result["objectId"]
                # 25-03.処理が失敗した場合は「変数．エラー情報」を作成し、エラーログをCloudWatchにログ出力する
                if not mongo_db_insert_result["result"]:
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["992001"]["logMessage"], mongo_db_insert_result["errorCode"], mongo_db_insert_result["message"]))
                    mongo_db_insert_error_info = {
                        "errorCode": "992001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["992001"]["message"], "992001")
                    }

                # 26.共通エラーチェック処理
                # 26-01.以下の引数で共通エラーチェック処理を実行する
                if mongo_db_insert_error_info is not None:
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
                    # 個人情報削除バッチキュー発行処理
                    transaction_delete_batch_queue_issue = CallbackExecutor(
                        self.common_util.transaction_delete_batch_queue_issue,
                        request_body.tid,
                        pds_user_info["pdsUserId"]
                    )
                    # API実行履歴登録処理
                    api_history_insert = CallbackExecutor(
                        self.common_util.insert_api_history,
                        commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                        self.pds_user_info["pdsUserId"],
                        apitypeConstClass.API_TYPE["UPDATE"],
                        self.pds_user_domain_name,
                        str(request_info.url),
                        json.dumps({"path_param": request_info.path_params, "query_param": request_info.query_params._dict, "header_param": commonUtil.make_headerParam(request_info.headers), "request_body": request_body.dict()}),
                        False,
                        None,
                        commonUtil.get_str_datetime()
                    )
                    # 26-02.例外が発生した場合、例外処理に遷移
                    self.common_util.common_error_check(
                        mongo_db_insert_error_info,
                        rollback_transaction,
                        mongo_db_rollback,
                        transaction_delete_batch_queue_issue,
                        api_history_insert
                    )
            else:
                json_data_flg = False
                insert_object_id = None

            # 27.MongoDB削除判定処理
            # 27-01.更新前の保存したいデータがJson形式か判定する
            # 27-01-01.「引数．個人情報検索結果リスト[2]」がfalseの場合、「30.個人情報テーブル更新処理」に遷移する
            # 27-01-02.「引数．個人情報検索結果リスト[2]」がtrueの場合、「28.MongoDB削除処理」に遷移する
            if get_user_profile_data_result[0][2]:
                # 28.MongoDB削除処理
                mongo_db_delete_error_info = None
                # 28-01.MongoDB削除処理を実行する
                mongo_db_delete_result = mongo_db_util.delete_object_id(mongodb_key)
                # 28-02.処理が失敗した場合は「変数．エラー情報」を作成し、エラーログをCloudWatchにログ出力する
                if not mongo_db_delete_result["result"]:
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["992001"]["logMessage"], mongo_db_delete_result["errorCode"], mongo_db_delete_result["message"]))
                    mongo_db_delete_error_info = {
                        "errorCode": "992001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["992001"]["message"], "992001")
                    }

                # 29.共通エラーチェック処理
                # 29-01.以下の引数で共通エラーチェック処理を実行する
                if mongo_db_delete_error_info is not None:
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
                    # 個人情報削除バッチキュー発行処理
                    transaction_delete_batch_queue_issue = CallbackExecutor(
                        self.common_util.transaction_delete_batch_queue_issue,
                        request_body.tid,
                        pds_user_info["pdsUserId"]
                    )
                    # API実行履歴登録処理
                    api_history_insert = CallbackExecutor(
                        self.common_util.insert_api_history,
                        commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                        self.pds_user_info["pdsUserId"],
                        apitypeConstClass.API_TYPE["UPDATE"],
                        self.pds_user_domain_name,
                        str(request_info.url),
                        json.dumps({"path_param": request_info.path_params, "query_param": request_info.query_params._dict, "header_param": commonUtil.make_headerParam(request_info.headers), "request_body": request_body.dict()}),
                        False,
                        None,
                        commonUtil.get_str_datetime()
                    )
                    # 29-02.例外が発生した場合、例外処理に遷移
                    self.common_util.common_error_check(
                        mongo_db_delete_error_info,
                        rollback_transaction,
                        mongo_db_rollback,
                        transaction_delete_batch_queue_issue,
                        api_history_insert
                    )

            # 30.個人情報テーブル更新処理
            update_user_profile_error_info = None
            # 30-01.個人情報テーブルを更新する
            param_list = []
            update_items_list = []
            if self.info_item_flg_dict["userId"]:
                update_items_list.append(" user_id = %s")
                param_list.append(request_body.info.userId)
            if self.info_item_flg_dict["saveDate"]:
                update_items_list.append(" save_datetime = %s")
                param_list.append(request_body.info.saveDate)
            if self.info_item_flg_dict["data"]:
                update_items_list.append(" save_data = %s")
                update_items_list.append(" json_data_flg = %s")
                update_items_list.append(" save_data_mongodb_key = %s")
                param_list.append(request_body.info.data)
                param_list.append(json_data_flg)
                param_list.append(insert_object_id)
            if self.info_item_flg_dict["secureLevel"]:
                update_items_list.append(" secure_level = %s")
                param_list.append(request_body.info.secureLevel)

            if len(update_items_list) > 0:
                update_item_sql = ','.join(update_items_list)
                sql = SqlConstClass.UPDATE_USER_PROFILE_SQL_PREFIX + update_item_sql + SqlConstClass.UPDATE_USER_PROFILE_SQL_SUFFIX
                param_list.append(request_body.tid)

                update_user_profile_result = pds_user_db_connection_resource.update(
                    pds_user_db_connection,
                    sql,
                    *param_list
                )
                # 30-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
                if not update_user_profile_result["result"]:
                    update_user_profile_error_info = self.common_util.create_postgresql_log(
                        update_user_profile_result["errorObject"],
                        None,
                        None,
                        update_user_profile_result["stackTrace"]
                    ).get("errorInfo")

                # 31.共通エラーチェック処理
                # 31-01.以下の引数で共通エラーチェック処理を実行する
                if update_user_profile_error_info is not None:
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
                    # 個人情報削除バッチキュー発行処理
                    transaction_delete_batch_queue_issue = CallbackExecutor(
                        self.common_util.transaction_delete_batch_queue_issue,
                        request_body.tid,
                        pds_user_info["pdsUserId"]
                    )
                    # API実行履歴登録処理
                    api_history_insert = CallbackExecutor(
                        self.common_util.insert_api_history,
                        commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                        self.pds_user_info["pdsUserId"],
                        apitypeConstClass.API_TYPE["UPDATE"],
                        self.pds_user_domain_name,
                        str(request_info.url),
                        json.dumps({"path_param": request_info.path_params, "query_param": request_info.query_params._dict, "header_param": commonUtil.make_headerParam(request_info.headers), "request_body": request_body.dict()}),
                        False,
                        None,
                        commonUtil.get_str_datetime()
                    )
                    # 31-02.例外が発生した場合、例外処理に遷移
                    self.common_util.common_error_check(
                        update_user_profile_error_info,
                        rollback_transaction,
                        mongo_db_rollback,
                        transaction_delete_batch_queue_issue,
                        api_history_insert
                    )

            # 32.MongoDBトランザクションコミット処理
            # 32-01.「MongoDB個人情報更新トランザクション」をコミットする
            mongo_db_util.commit_transaction()
            mongo_db_util.close_session()
            mongo_db_util.close_mongo()

            # 33.トランザクションコミット処理
            # 33-01.「個人情報更新トランザクション」をコミットする
            pds_user_db_connection_resource.commit_transaction(pds_user_db_connection)
            pds_user_db_connection_resource.close_connection(pds_user_db_connection)

            # 34. 終了処理
            # 34-01.返却パラメータを作成し、返却する
            return {
                "result": True,
                "sqs_exec_flg": sqs_exec_flg
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

    def skip_user_profile_binary(
        self,
        request_body: requestBody,
        adjusted_array_data: dict,
        save_image_idx: int,
        pds_user_id: str,
        request_info: Request,
        pds_user_db_connection_resource: PostgresDbUtilClass,
        pds_user_db_connection
    ):
        """
        個人情報バイナリデータスキップ処理

        Args:
            requestBody (object): リクエストボディ
            adjusted_array_data (dict): 調整後の配列データ(dict)
            save_image_idx (int): 保存画像インデックス
            pds_user_id (str): PDSユーザID
            request_info (Request): リクエスト情報
            pds_user_db_connection_resource (PostgresDbUtilClass): PDSユーザDB接続情報
            pds_user_db_connection (object): PDSユーザDBコネクション

        Returns:
            dict: 処理結果
        """
        try:
            # 01.個人情報バイナリデータ更新スキップ判定処理
            # 01-01.「引数．調整後の配列データ．バイナリデータ配列インデックス」がNullの場合、「04.終了処理」に遷移する
            # 01-02.「引数．調整後の配列データ．バイナリデータ配列インデックス」がNull以外の場合、「02.個人情報バイナリデータスキップ処理」に遷移する
            if adjusted_array_data["array_index"] is not None:
                # 02.個人情報バイナリデータスキップ処理
                update_binary_data_skip_error_info = None
                # 02-01.保持するデータのバイナリデータ配列インデックスを更新する
                update_binary_data_skip_result = pds_user_db_connection_resource.update(
                    pds_user_db_connection,
                    SqlConstClass.UPDATE_USER_PROFILE_BINARY_SKIP_SQL,
                    adjusted_array_data["array_index"],
                    request_body.tid,
                    save_image_idx
                )
                # 02-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
                if not update_binary_data_skip_result["result"]:
                    update_binary_data_skip_error_info = self.common_util.create_postgresql_log(
                        update_binary_data_skip_result["errorObject"],
                        None,
                        None,
                        update_binary_data_skip_result["stackTrace"]
                    ).get("errorInfo")

                # 03.共通エラーチェック処理
                # 03-01.以下の引数で共通エラーチェック処理を実行する
                if update_binary_data_skip_error_info is not None:
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
                        pds_user_id
                    )
                    # API実行履歴登録処理
                    api_history_insert = CallbackExecutor(
                        self.common_util.insert_api_history,
                        commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                        self.pds_user_info["pdsUserId"],
                        apitypeConstClass.API_TYPE["UPDATE"],
                        self.pds_user_domain_name,
                        str(request_info.url),
                        json.dumps({"path_param": request_info.path_params, "query_param": request_info.query_params._dict, "header_param": commonUtil.make_headerParam(request_info.headers), "request_body": request_body.dict()}),
                        False,
                        None,
                        commonUtil.get_str_datetime()
                    )
                    # 03-02.例外が発生した場合、例外処理に遷移
                    self.common_util.common_error_check(
                        update_binary_data_skip_error_info,
                        rollback_transaction,
                        transaction_delete_batch_queue_issue,
                        api_history_insert
                    )
            # 04.終了処理
            # 04-01.レスポンス情報を作成し、返却する
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

    def logical_delete_user_profile_binary(
        self,
        request_body: requestBody,
        save_image_idx: int,
        pds_user_id: str,
        request_info: Request,
        pds_user_db_connection_resource: PostgresDbUtilClass,
        pds_user_db_connection
    ):
        """
        個人情報バイナリデータ論理削除処理

        Args:
            requestBody (object): リクエストボディ
            save_image_idx (int): 保存画像インデックス
            pds_user_id (str): PDSユーザID
            request_info (Request): リクエスト情報
            pds_user_db_connection_resource (PostgresDbUtilClass): PDSユーザDB接続情報
            pds_user_db_connection (object): PDSユーザDBコネクション

        Returns:
            dict: 処理結果
        """
        try:
            # 01.個人情報バイナリデータ論理削除処理
            update_binary_data_logical_delete_error_info = None
            # 01-01.論理削除するデータの有効フラグを更新する
            update_binary_data_logical_delete_result = pds_user_db_connection_resource.update(
                pds_user_db_connection,
                SqlConstClass.UPDATE_USER_PROFILE_BINARY_LOGICAL_DELETE_SQL,
                request_body.tid,
                save_image_idx
            )
            # 01-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not update_binary_data_logical_delete_result["result"]:
                update_binary_data_logical_delete_error_info = self.common_util.create_postgresql_log(
                    update_binary_data_logical_delete_result["errorObject"],
                    None,
                    None,
                    update_binary_data_logical_delete_result["stackTrace"]
                ).get("errorInfo")

            # 02.共通エラーチェック処理
            # 02-01.以下の引数で共通エラーチェック処理を実行する
            if update_binary_data_logical_delete_error_info is not None:
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
                    pds_user_id
                )
                # API実行履歴登録処理
                api_history_insert = CallbackExecutor(
                    self.common_util.insert_api_history,
                    commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                    self.pds_user_info["pdsUserId"],
                    apitypeConstClass.API_TYPE["UPDATE"],
                    self.pds_user_domain_name,
                    str(request_info.url),
                    json.dumps({"path_param": request_info.path_params, "query_param": request_info.query_params._dict, "header_param": commonUtil.make_headerParam(request_info.headers), "request_body": request_body.dict()}),
                    False,
                    None,
                    commonUtil.get_str_datetime()
                )
                # 02-02.例外が発生した場合、例外処理に遷移
                self.common_util.common_error_check(
                    update_binary_data_logical_delete_error_info,
                    rollback_transaction,
                    transaction_delete_batch_queue_issue,
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
