import json
from fastapi import Request
from logging import Logger
import traceback
import hashlib
import base64
import boto3
from Crypto.Util import number
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from datetime import datetime

# Exception
from exceptionClass.PDSException import PDSException

# Const
from const.messageConst import MessageConstClass
from const.sqlConst import SqlConstClass

# Util
import util.commonUtil as commonUtil
from util.commonUtil import CommonUtilClass
from util.callbackExecutorUtil import CallbackExecutor
from const.apitypeConst import apitypeConstClass
from util.postgresDbUtil import PostgresDbUtilClass
import util.logUtil as logUtil


class cipherClass():
    def __init__(self, n):
        self.n = n


class tokenModelClass():
    def __init__(self, logger, request, pds_user_info, pds_user_domain_name, time_stamp):
        """
        コンストラクタ

        Args:
            logger (Logger): ロガー（TRACE）
        """
        self.logger: Logger = logger
        self.request: Request = request
        self.common_util = CommonUtilClass(logger)
        self.pds_user_info = pds_user_info
        self.pds_user_domain_name = pds_user_domain_name
        self.time_stamp = time_stamp
        self.error_info = None
        self.base_api_key = ""
        self.base_time_stamp = ""

    def main(self, request_body):
        """
        アクセストークン発行 メイン処理

        Args:
            request_body (object): リクエストボディ
        """
        try:
            # 05.共通DB接続準備処理
            # 05-01.AWS SecretsManagerから共通DB接続情報を取得して、「変数．共通DB接続情報」に格納する
            common_db_connection_resource: PostgresDbUtilClass = None
            # 05-02.「変数．共通DB接続情報」を利用して、共通DBに対してのコネクションを作成する
            common_db_info_response = self.common_util.get_common_db_info_and_connection()
            if not common_db_info_response["result"]:
                return common_db_info_response
            else:
                common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
                common_db_connection = common_db_info_response["common_db_connection"]

            # 06.PDSユーザPDSユーザ公開鍵情報取得処理
            # 06-01.PDSユーザ、PDSユーザ公開鍵テーブルを結合したテーブルからデータを取得し、「変数．PDSユーザPDSユーザ公開鍵取得結果リスト」に全レコードをタプルのリストとして格納する
            pds_user_pds_user_key_select_result = common_db_connection_resource.select_tuple_list(
                common_db_connection,
                SqlConstClass.PDS_USER_PDS_USER_PUBLIC_KEY_TOKEN_SELECT_SQL,
                self.pds_user_info["pdsUserId"]
            )
            # 06-02.処理が失敗した場合は、postgresqlエラー処理を実行する
            if not pds_user_pds_user_key_select_result["result"]:
                self.error_info = self.common_util.create_postgresql_log(
                    pds_user_pds_user_key_select_result["errorObject"],
                    None,
                    None,
                    pds_user_pds_user_key_select_result["stackTrace"]
                ).get("errorInfo")

            # 07.共通エラーチェック処理
            # 07-01.以下の引数で共通エラーチェック処理を実行する
            # 07-02.例外が発生した場合、例外処理に遷移
            if self.error_info is not None:
                # API実行履歴登録処理
                api_history_insert = CallbackExecutor(
                    self.common_util.insert_api_history,
                    commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                    self.pds_user_info["pdsUserId"],
                    apitypeConstClass.API_TYPE["ACCESS_TOKEN_ISSUE"],
                    self.pds_user_domain_name,
                    str(self.request.url),
                    json.dumps({"path_param": self.request.path_params, "query_param": self.request.query_params._dict, "header_param": commonUtil.make_headerParam(self.request.headers), "request_body": request_body.dict()}),
                    False,
                    None,
                    commonUtil.get_str_datetime()
                )
                self.common_util.common_error_check(
                    self.error_info,
                    api_history_insert
                )

            # 08.アクセストークン検証フラグ作成処理
            # 08-01.「変数．アクセストークン検証フラグ」を初期化する
            access_token_varify_flg = False

            # 変数．PDSユーザPDSユーザ公開鍵取得結果の要素数分繰り返す
            for loop, pds_user_pds_user_key in enumerate(pds_user_pds_user_key_select_result["query_results"]):

                # TODO：コメントの修正
                # 09.暗号化文字列２復号化処理
                # 09-01.リクエストのリクエストボディ．暗号化文字列２を「変数．PDSユーザPDSユーザ公開鍵取得結果リスト[変数．PDSユーザ公開鍵ループ数][2]」で復号化する
                # 09-02.復号化した結果を「変数．暗号化文字列２復号化処理実行結果」に格納する
                try:
                    hashed_code1 = SHA256.new(request_body.code1.encode())
                    code2_long_module = number.bytes_to_long(base64.b64decode(pds_user_pds_user_key[2]))
                    code2_long_exponent = number.bytes_to_long(base64.b64decode("AQAB"))
                    publickey = RSA.construct((code2_long_module, code2_long_exponent))
                    b64decode_code2 = base64.b64decode(request_body.code2)
                    decryptor_code2 = pkcs1_15.new(publickey)
                    decrypted_code2 = decryptor_code2.verify(hashed_code1, b64decode_code2)
                    code2_verify_flg = True
                except Exception:
                    code2_verify_flg = False

                # TODO：検証なのでハッシュ化した値と比べるのではなくverifyでエラーが出なかった場合に条件を変更
                # 10.暗号化文字列２復号化チェック処理
                # 10-01.「変数．暗号化文字列２復号化処理実行結果」とリクエストのリクエストボディ．暗号化文字列１が一致しない場合、繰り返し処理を続行する
                decoded_code1 = base64.b64decode(request_body.code1)
                hashed_code1 = hashlib.sha256(decoded_code1).hexdigest()
                # 10-02.「変数．暗号化文字列２復号化処理実行結果」とリクエストのリクエストボディ．暗号化文字列１が一致する場合、「10.暗号化文字列１復号化処理」に遷移する
                if code2_verify_flg:
                    # 11.暗号化文字列１復号化処理
                    kms = boto3.client(
                        "kms"
                    )
                    try:
                        # 11-01.暗号化文字列１を「変数．PDSユーザPDSユーザ公開鍵取得結果リスト[変数．PDSユーザPDSユーザ公開鍵ループ数][1]」で復号化する
                        dec_result = kms.decrypt(
                            CiphertextBlob=base64.b64decode(request_body.code1.encode()),
                            KeyId=pds_user_pds_user_key[1],
                            EncryptionAlgorithm='RSAES_OAEP_SHA_1'
                        )
                        plain_text = dec_result["Plaintext"].decode("utf-8")
                    except Exception:
                        # 11-02.復号化に失敗した場合、「変数．エラー情報」を作成し、エラーログをCloudWatchにログ出力する
                        self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990001"]["logMessage"]))
                        self.error_info = {
                            "errorCode": "990001",
                            "message": logUtil.message_build(MessageConstClass.ERRORS["990001"]["message"], "990001")
                        }

                    # 共通エラーチェック処理
                    if self.error_info is not None:
                        # API実行履歴登録処理
                        api_history_insert = CallbackExecutor(
                            self.common_util.insert_api_history,
                            commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                            self.pds_user_info["pdsUserId"],
                            apitypeConstClass.API_TYPE["ACCESS_TOKEN_ISSUE"],
                            self.pds_user_domain_name,
                            str(self.request.url),
                            json.dumps({"path_param": self.request.path_params, "query_param": self.request.query_params._dict, "header_param": commonUtil.make_headerParam(self.request.headers), "request_body": request_body.dict()}),
                            False,
                            None,
                            commonUtil.get_str_datetime()
                        )
                        self.common_util.common_error_check(
                            self.error_info,
                            api_history_insert
                        )

                    base_api_key = plain_text[:30]
                    base_time_stamp = plain_text[30:]
                    # 11-03.復号化した結果のAPIKeyと「変数．PDSユーザPDSユーザ公開鍵取得結果リスト[変数．PDSユーザ公開鍵ループ数][0]」が一致することを検証する
                    if base_api_key != pds_user_pds_user_key[0]:
                        # 11-03-01.復号化した結果のAPIKey と一致しなかった場合、「変数．エラー情報」を作成し、エラーログをCloudWatchにログ出力する
                        self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["010004"]["logMessage"]))
                        self.error_info = {
                            "errorCode": "010004",
                            "message": logUtil.message_build(MessageConstClass.ERRORS["010004"]["message"])
                        }
                    base_time_stamp_dt = datetime.strptime(base_time_stamp + "000", '%Y/%m/%d %H:%M:%S.%f')
                    self_time_stamp_dt = datetime.strptime(self.time_stamp + "000", '%Y/%m/%d %H:%M:%S.%f')
                    # 11-04.復号化した結果のタイムスタンプとヘッダパラメータのタイムスタンプが誤差 (1000ミリ秒) 以内であることを検証する
                    if abs((base_time_stamp_dt - self_time_stamp_dt).seconds) > 1:
                        # 11-04-01.誤差 (1000ミリ秒) 以内ではなかった場合、「変数．エラー情報」を作成し、エラーログをCloudWatchにログ出力する
                        self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["010004"]["logMessage"]))
                        self.error_info = {
                            "errorCode": "010004",
                            "message": logUtil.message_build(MessageConstClass.ERRORS["010004"]["message"])
                        }

                    # 12.共通エラーチェック処理
                    # 12-01.以下の引数で共通エラーチェック処理を実行する
                    # 12-02.例外が発生した場合、例外処理に遷移
                    if self.error_info is not None:
                        # API実行履歴登録処理
                        api_history_insert = CallbackExecutor(
                            self.common_util.insert_api_history,
                            commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                            self.pds_user_info["pdsUserId"],
                            apitypeConstClass.API_TYPE["ACCESS_TOKEN_ISSUE"],
                            self.pds_user_domain_name,
                            str(self.request.url),
                            json.dumps({"path_param": self.request.path_params, "query_param": self.request.query_params._dict, "header_param": commonUtil.make_headerParam(self.request.headers), "request_body": request_body.dict()}),
                            False,
                            None,
                            commonUtil.get_str_datetime()
                        )
                        self.common_util.common_error_check(
                            self.error_info,
                            api_history_insert
                        )

                    # 13.アクセストークン検証フラグ更新処理
                    # 13-01.「変数．アクセストークン検証フラグ」をtrueで更新する
                    access_token_varify_flg = True

                    break

            # 14.アクセストークン検証フラグ確認処理
            # 14-01.「変数．アクセストークン検証フラグ」がfalseの場合、「変数．エラー情報」を作成し、エラーログをCloudWatchにログ出力する
            if not access_token_varify_flg:
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990001"]["logMessage"]))
                self.error_info = {
                    "errorCode": "990001",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["990001"]["message"], "990001")
                }

            # 15.共通エラーチェック処理
            # 15-01.以下の引数で共通エラーチェック処理を実行する
            # 15-02.例外が発生した場合、例外処理に遷移
            if self.error_info is not None:
                # API実行履歴登録処理
                api_history_insert = CallbackExecutor(
                    self.common_util.insert_api_history,
                    commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                    self.pds_user_info["pdsUserId"],
                    apitypeConstClass.API_TYPE["ACCESS_TOKEN_ISSUE"],
                    self.pds_user_domain_name,
                    str(self.request.url),
                    json.dumps({"path_param": self.request.path_params, "query_param": self.request.query_params._dict, "header_param": commonUtil.make_headerParam(self.request.headers), "request_body": request_body.dict()}),
                    False,
                    None,
                    commonUtil.get_str_datetime()
                )
                self.common_util.common_error_check(
                    self.error_info,
                    api_history_insert
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
