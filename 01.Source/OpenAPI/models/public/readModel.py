import json
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
from util.postgresDbUtil import PostgresDbUtilClass
from util.userProfileUtil import UserProfileUtilClass


class readModelClass():
    def __init__(self, logger: Logger, request: Request, pds_user_id: str, pds_user_info, pds_user_domain_name: str):
        self.logger: Logger = logger
        self.request: Request = request
        self.pds_user_id: str = pds_user_id
        self.common_util = CommonUtilClass(logger)
        self.pds_user_info = pds_user_info
        self.pds_user_domain_name = pds_user_domain_name

    async def main(self, transaction_id: str):
        """
        メイン処理

        Returns:
            dict: 処理結果
        """
        try:
            # 02.個人情報取得処理
            # 02-01.以下の引数で個人情報取得処理を実行する
            # 02-02.個人情報取得処理のレスポンスを「変数．個人情報取得結果」に格納する
            get_user_profile_result = await self.get_user_profile(
                pds_user_db_secrets_name=self.pds_user_info["pdsUserInstanceSecretName"],
                transaction_id=transaction_id,
                pds_user_info=self.pds_user_info,
                request=self.request
            )
            return {
                "result": True,
                "transactionInfo": get_user_profile_result["transactionInfo"]
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

    async def get_user_profile(
        self,
        pds_user_db_secrets_name: str,
        transaction_id: str,
        pds_user_info: dict,
        request: Request
    ):
        try:
            # 01.PDSユーザDB接続準備処理
            # 01-01.以下の引数でPDSユーザDBの接続情報をAWSのSecrets Managerから取得する
            # 01-02.取得したPDSユーザDBの接続情報を、「変数．PDSユーザDB接続情報」に格納する
            # 01-03.「変数．PDSユーザDB接続情報」を利用して、PDSユーザDBに対してのコネクションを作成する
            pds_user_db_connection_resource: PostgresDbUtilClass = None
            pds_user_db_info_response = self.common_util.get_pds_user_db_info_and_connection(pds_user_db_secrets_name)
            if not pds_user_db_info_response["result"]:
                raise PDSException(pds_user_db_info_response["errorInfo"])
            else:
                pds_user_db_connection_resource = pds_user_db_info_response["pds_user_db_connection_resource"]
                pds_user_db_connection = pds_user_db_info_response["pds_user_db_connection"]

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
                # API実行履歴登録処理
                api_history_insert = CallbackExecutor(
                    self.common_util.insert_api_history,
                    commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                    pds_user_info["pdsUserId"],
                    apitypeConstClass.API_TYPE["REFERENCE"],
                    self.pds_user_domain_name,
                    str(request.url),
                    json.dumps({"path_param": request.path_params, "query_param": request.query_params._dict, "header_param": commonUtil.make_headerParam(request.headers), "request_body": {}}),
                    False,
                    None,
                    commonUtil.get_str_datetime()
                )
                # 03-02.例外が発生した場合、例外処理に遷移
                self.common_util.common_error_check(
                    pds_user_profile_read_error_info,
                    api_history_insert
                )

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
                # API実行履歴登録処理
                api_history_insert = CallbackExecutor(
                    self.common_util.insert_api_history,
                    commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                    pds_user_info["pdsUserId"],
                    apitypeConstClass.API_TYPE["REFERENCE"],
                    self.pds_user_domain_name,
                    str(request.url),
                    json.dumps({"path_param": request.path_params, "query_param": request.query_params._dict, "header_param": commonUtil.make_headerParam(request.headers), "request_body": {}}),
                    False,
                    None,
                    commonUtil.get_str_datetime()
                )
                # 05-02.例外が発生した場合、例外処理に遷移
                self.common_util.common_error_check(
                    pds_user_profile_binary_get_read_target_error_info,
                    api_history_insert
                )

            # 06.保存したいデータ出力情報作成
            if pds_user_profile_read_result["query_results"][0][5]:
                # 06-01.「変数．個人情報取得結果リスト[0][5]」がtrueの場合、「変数．個人情報取得結果リスト[0][3]」をJson形式として読み取り、「変数．保存したいデータ出力」に格納する
                out_data = json.loads(pds_user_profile_read_result["query_results"][0][3])
            else:
                # 06-02.「変数．個人情報取得結果リスト[0][5]」がtrue以外の場合、「変数．個人情報取得結果リスト[0][3]」をそのままの形式で読み取り、「変数．保存したいデータ出力」に格納する
                out_data = pds_user_profile_read_result["query_results"][0][3]

            # 07.個人バイナリ情報取得件数チェック処理
            # 07-01.「変数．個人バイナリ情報取得結果リスト」が0件の場合、「08.終了処理」に遷移する
            # 07-02.「変数．個人バイナリ情報取得結果リスト」が1件以上の場合、「09.バイナリ情報格納変数定義処理」に遷移する
            if pds_user_profile_binary_get_read_target_result["rowCount"] == 0:
                # 08.終了処理
                # 08-01.レスポンス情報を作成し、返却する
                return {
                    "result": True,
                    "transactionInfo": {
                        "saveDate": pds_user_profile_read_result["query_results"][0][2].strftime('%Y/%m/%d %H:%M:%S.%f')[:-3],
                        "userId": pds_user_profile_read_result["query_results"][0][1],
                        "data": out_data,
                        "image": None,
                        "imageHash": None,
                        "secureLevel": pds_user_profile_read_result["query_results"][0][4]
                    }
                }
            else:
                # 09.ループ処理用変数初期化処理
                # 09-01.バイナリ情報格納用の変数を定義する
                get_binary_file_exec_list = []
                file_save_path_list = []
                kms_data_key_list = []
                chiper_nonce_list = []
                image_hash_list = []
                binary_item_count = 0

                userProfileUtil = UserProfileUtilClass(self.logger)
                binary_data_item_exit_count = len(pds_user_profile_binary_get_read_target_result["query_results"]) - 1
                for binary_data_loop_no, binary_data_item in enumerate(pds_user_profile_binary_get_read_target_result["query_results"]):
                    # 10.個人情報バイナリデータ．保存画像インデックス判定処理
                    # 10-01.「変数．個人バイナリ情報取得結果リスト[変数．個人情報バイナリデータループ数][1]」が変わった場合、「10．バイナリデータ取得処理リスト作成処理」に遷移する
                    # 10-02.「変数．個人バイナリ情報取得結果リスト[変数．個人情報バイナリデータループ数][1]」が同じ場合、「14．バイナリデータ取得対象追加処理」に遷移する
                    if binary_data_loop_no != 0 and binary_data_item[1] != pds_user_profile_binary_get_read_target_result["query_results"][binary_data_loop_no - 1][1]:
                        # 11.バイナリデータ取得処理リスト作成処理
                        # 11-01.「変数．バイナリデータ取得処理リスト」にバイナリデータ取得処理を追加する
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
                        # 12.バイナリデータハッシュ値格納リスト追加処理
                        # 12-01.「変数．バイナリデータハッシュ値格納リスト」にハッシュ値を追加する。
                        image_hash_list.append(pds_user_profile_binary_get_read_target_result["query_results"][binary_data_loop_no - 1][3])

                        # 13.バイナリデータ取得対象初期化処理
                        # 13-01.バイナリデータ取得処理の対象を管理している変数を初期化する
                        file_save_path_list = []
                        kms_data_key_list = []
                        chiper_nonce_list = []

                        # 14.バイナリデータ要素数インクリメント処理
                        # 14-01.「変数．バイナリデータ要素数」をインクリメントする
                        binary_item_count += 1

                    # 15.バイナリデータ取得対象追加処理
                    # 15-01.バイナリデータ取得処理の対象を管理している変数に値を追加する
                    file_save_path_list.append(binary_data_item[5])
                    kms_data_key_list.append(binary_data_item[6])
                    chiper_nonce_list.append(binary_data_item[7])

                    # 16.ループ終了判定処理
                    # 16-01.「変数．個人情報バイナリデータループ数」と「変数．個人情報バイナリ情報取得結果リスト」の要素数が一致する場合、「17．バイナリデータ取得処理リスト作成処理」に遷移する
                    # 16-02.「変数．個人情報バイナリデータループ数」と「変数．個人情報バイナリ情報取得結果リスト」の要素数が一致しない場合、繰り返し処理を続行する
                    if binary_data_loop_no == binary_data_item_exit_count:
                        # 17.バイナリデータ取得処理リスト作成処理
                        # 17-01.「変数．バイナリデータ取得処理リスト」にバイナリデータ取得処理を追加する
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

                        # 18.バイナリデータハッシュ値格納リスト追加処理
                        # 18-01.「変数．バイナリデータハッシュ値格納リスト」にハッシュ値を追加する。
                        image_hash_list.append(binary_data_item[3])

                # 19.バイナリデータ取得処理実行処理
                # 19-01.バイナリデータ取得処理実行処理「変数．バイナリデータ取得処理リスト」をもとに、バイナリデータ取得処理を並列で実行する
                # 19-02.レスポンスを「変数．バイナリデータ取得処理実行結果リスト」に格納する
                get_binary_data_result_list = await asyncio.gather(*get_binary_file_exec_list)

                # 20.終了処理
                # 20-01.返却パラメータを作成し、返却する
                binary_data_list = [d.get("binaryData") for d in get_binary_data_result_list]
                return {
                    "result": True,
                    "transactionInfo": {
                        "saveDate": pds_user_profile_read_result["query_results"][0][2].strftime('%Y/%m/%d %H:%M:%S.%f')[:-3],
                        "userId": pds_user_profile_read_result["query_results"][0][1],
                        "data": out_data,
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
