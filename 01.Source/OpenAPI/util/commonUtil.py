# 共通処理
# 例：現在日時の取得等
import io
import string
import boto3
import random
import json
import requests
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from logging import Logger
import traceback
import uuid
import re
import logging

# Exceptionクラス
from exceptionClass.PDSException import PDSException

# Utilクラス
import util.logUtil as logUtil
import util.checkUtil as checkUtil
from util.postgresDbUtil import PostgresDbUtilClass
from util.callbackExecutorUtil import CallbackExecutor
from util.cryptoUtil import CryptUtilClass
from util.mongoDbUtil import MongoDbClass

# 定数クラス
from const.systemConst import SystemConstClass
from const.messageConst import MessageConstClass
from const.sqlConst import SqlConstClass

from psycopg2 import Error as postgresql_error

## 共通パラメータチェッククラス
from util.commonParamCheck import checkPdsUserId
from util.commonParamCheck import checkPdsUserDomainName


class CommonUtilClass:

    def __init__(self, logger):
        self.logger: Logger = logger

    def post_request(self, url: str, data: dict, header: dict):
        """
        汎用POSTリクエスト処理

        Args:
            url (str): リクエスト先URL
            data (dict): リクエストデータ
            header (dict): リクエストヘッダ

        Returns:
            response: レスポンス
        """
        try:
            data_param = json.dumps(data)
            # POSTリクエスト
            response = requests.post(
                url=url,
                data=data_param,
                headers=header
            )
            if response.status_code != 200:
                return {
                    "result": False
                }
            else:
                return {
                    "result": True,
                    "response": response
                }
        except Exception as e:
            raise e

    def get_secret_info(self, secret_name: str):
        """
        SecretsManager値取得処理

        Args:
            secretName (str): シークレット名

        Returns:
            dict: シークレットマネージャー出力結果
        """
        client = boto3.client(
            service_name="secretsmanager"
        )

        try:
            get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        except Exception as e:
            raise e

        # SecretsManagerからの情報を取得
        return json.loads(get_secret_value_response["SecretString"])

    def wbt_mails_add_api_exec(
        self,
        repositoryType: str,
        fileName: str,
        downloadDeadline: str,
        replyDeadline: str,
        comment: str,
        mailAddressTo: str,
        mailAddressCc: str,
        title: str
    ):
        """
        WBT新規メール情報登録API実行
        WBTの新規メール情報登録APIを実行する
        Args:
            repositoryType (str): 種別
            fileName (str or list): 送信するファイル名
            downloadDeadline (str): 引き取り期限
            replyDeadline (str): 返信期限
            comment (str): メッセージ
            mailAddressTo (str): Toメールアドレス
            mailAddressCc (str): Ccメールアドレス
            title (str): メール件名

        Raises:
            PDSException: PDS例外処理
            e: 例外処理
            PDSException: PDS例外処理

        Returns:
            result: 処理結果
            attachedFiles: 添付するファイルの情報
            id: 送信メールID
            errorInfo: エラー情報
        """
        error_info_list = []
        EXEC_NAME_JP = "WBT新規メール情報登録API実行"
        try:
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_IN_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            # 01.引数検証処理（入力チェック）
            # 01-01.「引数．種別」が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(repositoryType):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "種別"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "種別")
                    }
                )

            # 01-02.「引数．種別」に値が設定されており、型が文字列型ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_type(repositoryType, str):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "種別", "文字列"))
                error_info_list.append(
                    {
                        "errorCode": "020019",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "種別", "文字列")
                    }
                )

            # 01-03.「引数．種別」に値が設定されており、値の桁数が1桁ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_length(repositoryType, 1):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020014"]["logMessage"], "種別", "1"))
                error_info_list.append(
                    {
                        "errorCode": "020014",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020014"]["message"], "種別", "1")
                    }
                )

            # 01-04.「引数．種別」に値が設定されており、値が入力規則に違反している場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_repository_type(repositoryType):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020003"]["logMessage"], "種別"))
                error_info_list.append(
                    {
                        "errorCode": "020003",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "種別")
                    }
                )

            # 01-05.「引数．送信するファイル名」が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require_list_str(fileName):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "送信するファイル名"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "送信するファイル名")
                    }
                )

            # 01-06.「引数．送信するファイル名」に値が設定されており、型が文字列型ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_type(fileName, str, list):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "送信するファイル名", "文字列"))
                error_info_list.append(
                    {
                        "errorCode": "020019",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "送信するファイル名", "文字列")
                    }
                )

            # 01-07.「引数．送信するファイル名」に値が設定されており、値の桁数が256桁超過の場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_max_length_list_str(fileName, 256):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020002"]["logMessage"], "送信するファイル名", "256"))
                error_info_list.append(
                    {
                        "errorCode": "020002",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020002"]["message"], "送信するファイル名", "256")
                    }
                )

            # 01-08.「引数．送信するファイル名」に値が設定されており、値が入力規則に違反している場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_file_name_characters(fileName):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020003"]["logMessage"], "送信するファイル名"))
                error_info_list.append(
                    {
                        "errorCode": "020003",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "送信するファイル名")
                    }
                )

            # 01-09.「引数．引き取り期限」が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(downloadDeadline):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "引き取り期限"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "引き取り期限")
                    }
                )

            # 01-10.「引数．引き取り期限」に値が設定されており、型が文字列型ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_type(downloadDeadline, str):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "引き取り期限", "文字列"))
                error_info_list.append(
                    {
                        "errorCode": "020019",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "引き取り期限", "文字列")
                    }
                )

            # 01-11.「引数．引き取り期限」に値が設定されており、値の桁数が23桁ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_length(downloadDeadline, 23):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020014"]["logMessage"], "引き取り期限", "23"))
                error_info_list.append(
                    {
                        "errorCode": "020014",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020014"]["message"], "引き取り期限", "23")
                    }
                )

            # 01-12.「引数．引き取り期限」に値が設定されており、値が入力規則に違反している場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_time_stamp(downloadDeadline):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020003"]["logMessage"], "引き取り期限"))
                error_info_list.append(
                    {
                        "errorCode": "020003",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "引き取り期限")
                    }
                )

            # 01-13.「引数．返信期限」に値が設定されており、型が文字列型ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_type(replyDeadline, str):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "返信期限", "文字列"))
                error_info_list.append(
                    {
                        "errorCode": "020019",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "返信期限", "文字列")
                    }
                )

            # 01-14.「引数．返信期限」に値が設定されており、値の桁数が23桁ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_length(replyDeadline, 23):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020014"]["logMessage"], "返信期限", "23"))
                error_info_list.append(
                    {
                        "errorCode": "020014",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020014"]["message"], "返信期限", "23")
                    }
                )

            # 01-15.「引数．返信期限」に値が設定されており、値が入力規則に違反している場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_time_stamp(replyDeadline):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020003"]["logMessage"], "返信期限"))
                error_info_list.append(
                    {
                        "errorCode": "020003",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "返信期限")
                    }
                )

            # 01-16.「引数．メッセージ」に値が設定されており、型が文字列型ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_type(comment, str):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "メッセージ", "文字列"))
                error_info_list.append(
                    {
                        "errorCode": "020019",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "メッセージ", "文字列")
                    }
                )

            # 01-17.「引数．メッセージ」に値が設定されており、値の桁数が4000桁超過の場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_max_length(comment, 4000):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020002"]["logMessage"], "メッセージ", "4000"))
                error_info_list.append(
                    {
                        "errorCode": "020002",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020002"]["message"], "メッセージ", "4000")
                    }
                )

            # 01-18.「引数．メッセージ」に値が設定されており、値が入力規則に違反している場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_enterable_characters_general_purpose_characters(comment):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020003"]["logMessage"], "メッセージ"))
                error_info_list.append(
                    {
                        "errorCode": "020003",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "メッセージ")
                    }
                )

            # 01-19.「引数．Toメールアドレス」が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(mailAddressTo):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "Toメールアドレス"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "Toメールアドレス")
                    }
                )

            # 01-20.「引数．Toメールアドレス」に値が設定されており、型が文字列型ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_type(mailAddressTo, str):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "Toメールアドレス", "文字列"))
                error_info_list.append(
                    {
                        "errorCode": "020019",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "Toメールアドレス", "文字列")
                    }
                )

            # 01-21.「引数．Toメールアドレス」に値が設定されており、値の桁数が5桁未満の場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_min_length(mailAddressTo, 5):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020016"]["logMessage"], "Toメールアドレス", "5"))
                error_info_list.append(
                    {
                        "errorCode": "020016",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020016"]["message"], "Toメールアドレス", "5")
                    }
                )

            # 01-22.「引数．Toメールアドレス」に値が設定されており、値の桁数が512桁を超過する場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_max_length(mailAddressTo, 512):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020002"]["logMessage"], "Toメールアドレス", "512"))
                error_info_list.append(
                    {
                        "errorCode": "020002",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020002"]["message"], "Toメールアドレス", "512")
                    }
                )

            # 01-23.「引数．Toメールアドレス」に値が設定されており、値が入力規則に違反している場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_multi_mail_address(mailAddressTo):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020003"]["logMessage"], "Toメールアドレス"))
                error_info_list.append(
                    {
                        "errorCode": "020003",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "Toメールアドレス")
                    }
                )

            # 01-24.「引数．Ccメールアドレス」に値が設定されており、型が文字列型ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_type(mailAddressCc, str):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "Ccメールアドレス", "文字列"))
                error_info_list.append(
                    {
                        "errorCode": "020019",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "Ccメールアドレス", "文字列")
                    }
                )

            # 01-25.「引数．Ccメールアドレス」に値が設定されており、値の桁数が5桁未満の場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_min_length(mailAddressCc, 5):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020016"]["logMessage"], "Ccメールアドレス", "5"))
                error_info_list.append(
                    {
                        "errorCode": "020016",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020016"]["message"], "Ccメールアドレス", "5")
                    }
                )

            # 01-26.「引数．Ccメールアドレス」に値が設定されており、値の桁数が512桁を超過する場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_max_length(mailAddressCc, 512):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020002"]["logMessage"], "Ccメールアドレス", "512"))
                error_info_list.append(
                    {
                        "errorCode": "020002",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020002"]["message"], "Ccメールアドレス", "512")
                    }
                )

            # 01-27.「引数．Ccメールアドレス」に値が設定されており、値が入力規則に違反している場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_multi_mail_address(mailAddressCc):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020003"]["logMessage"], "Ccメールアドレス"))
                error_info_list.append(
                    {
                        "errorCode": "020003",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "Ccメールアドレス")
                    }
                )

            # 01-28.「引数．メール件名」に値が設定されており、型が文字列型ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_type(title, str):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "メール件名", "文字列"))
                error_info_list.append(
                    {
                        "errorCode": "020019",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "メール件名", "文字列")
                    }
                )

            # 01-29.「引数．メール件名」に値が設定されており、値の桁数が256桁を超過する場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_max_length(title, 256):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020002"]["logMessage"], "メール件名", "256"))
                error_info_list.append(
                    {
                        "errorCode": "020002",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020002"]["message"], "メール件名", "256")
                    }
                )

            # 01-30.「引数．メール件名」に値が設定されており、値が入力規則に違反している場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_enterable_characters_general_purpose_characters(title):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020003"]["logMessage"], "メール件名"))
                error_info_list.append(
                    {
                        "errorCode": "020003",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "メール件名")
                    }
                )

            # 01-31.「変数．エラー情報リスト」に値が設定されている場合、エラー作成処理を実施する
            if len(error_info_list) != 0:
                # 01-31-01.下記のパラメータでPDSExceptionオブジェクトを作成する
                # 01-31-02.PDSExceptionオブジェクトをエラーとしてスローする
                raise PDSException(*error_info_list)

            # TODO(t.ii)：WBTの処理は共通処理側で直値を返却するようにしておく
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            return {
                "result": True,
                "attachedFiles": [
                    {
                        "id": 36980,
                        "fileName": "tf_public_key_notification",
                        "extension": ".csv"
                    },
                    {
                        "id": 36981,
                        "fileName": "ファイル名2",
                        "extension": ".jpg"
                    }
                ],
                "id": 28890
            }
            """
            # エラー返却
            return {
                "result": False,
                "errorInfo": {
                    "errorCode": "990011",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["990011"]["message"], "990011")
                }
            }
            """
            """
            # 02.メールアドレスリスト作成処理
            mail_address_list = []
            # 02-01.Toメールアドレス分割処理
            # 02-01-01.「引数．Toメールアドレス」を";"（半角セミコロン）で文字列分割して、「変数．Toメールアドレスリスト」を作成する
            # 02-01-02.「変数．メールアドレスリスト」にデータを追加する
            mail_address_list.append({"mailAddress1": to, "mailType": "To"} for to in mailAddressTo.split(";"))
            # 02-02.Ccメールアドレス分割処理
            # 02-02-01.「引数．Ccメールアドレス」を";"（半角セミコロン）で文字列分割して、「変数．Toメールアドレスリスト」を作成する
            # 02-02-02.「変数．メールアドレスリスト」にデータを追加する
            if mailAddressCc is not None:
                mail_address_list.append({"mailAddress1": cc, "mailType": "Cc"} for cc in mailAddressCc.split(";"))

            # 03.新規メール情報登録API実行
            error_info = None
            if type(fileName) is list:
                attach_file_list = [{"fileName": file_name_str} for file_name_str in fileName]
            else:
                attach_file_list = [{"fileName": fileName}]
            # 03-01.以下の引数でWBTの新規メール情報登録API呼び出し処理を実行する
            try:
                header = {"Content-Type": "application/json", "Ocp-Apim-Subscription-Key": "e7b58ee4695c4621a9de98de48b1aa38"}
                request_body_data = {
                    "repositoryType": repositoryType,
                    "attachedFiles": attach_file_list,
                    "downloadDeadline": downloadDeadline,
                    "replyDeadline": replyDeadline,
                    "downloadNotifyFlag": True,
                    "language": "JAPANESE",
                    "comment": comment,
                    "receivers": mail_address_list,
                    "title": title,
                    "mailPassword": "Password0",
                    "sendGuestPasswordMailFlag": True,
                    "chunkSize": 500
                }
                url = "http://localhost:8080/sdms/mails/add"
                # 03-02.WBTの新規メール情報登録APIからのレスポンスを、変数．新規メール情報登録API結果に格納する
                post_reslt = self.post_request(url=url, headers=header, data=request_body_data)
                if post_reslt["result"]:
                    wbt_mails_add_api_result = post_reslt["response"].json()
                else:
                    # 03-03.WebBureauTransferの処理に失敗した場合、変数．エラー情報にエラー情報を作成する
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990011"]["logMessage"]))
                    error_info = {
                        "errorCode": "990011",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["990011"]["message"], "990011")
                    }
            except Exception:
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990011"]["logMessage"]))
                error_info = {
                    "errorCode": "990011",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["990011"]["message"], "990011")
                }

            # 04.新規メール情報登録API実行チェック処理
            if error_info is not None:
                # 04-01.「変数．エラー情報」が設定されていない場合、「06.終了処理」に遷移する
                pass
            else:
                # 04-02.「変数．エラー情報」が設定されている場合、「05. 新規メール情報登録API実行チエラー処理」に遷移する
                # 05.新規メール情報登録API実行エラー処理
                # 05-01.レスポンス情報を作成し、返却する
                if logging.ERROR == logUtil.output_outlog(EXEC_NAME_JP, error_info):
                    self.logger.error(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                else:
                    self.logger.warning(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                return {
                    "result": False,
                    "errorInfo": error_info
                }

            # 06.終了処理
            # 06-01.レスポンス情報を作成し、返却する
            # 06-01-01.「変数．エラー情報」に値が設定されていない場合、下記のレスポンス情報を返却する
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            return {
                "result": True,
                "attachedFiles": wbt_mails_add_api_result["attachedFiles"],
                "id": wbt_mails_add_api_result["id"]
            }
            """
        # 例外処理（PDSExceptionクラス）：
        except PDSException as e:
            # PDSExceptionオブジェクトをエラーとしてスローする
            raise e
        # 例外処理：
        except Exception as e:
            # エラー情報をCloudWatchへログ出力する
            self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["999999"]["logMessage"], str(e), traceback.format_exc()))
            # 下記のパラメータでPDSExceptionオブジェクトを作成する
            # PDSExceptionオブジェクトをエラーとしてスローする
            raise PDSException(
                {
                    "errorCode": "999999",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
                }
            )

    def wbt_file_add_api_exec(
        self,
        mailId: int,
        fileId: int,
        file: object,
        chunkNo: str,
        chunkTotalNumber: str
    ):
        """
        WBTファイル登録API実行
        WBTのファイル登録APIを実行する
        Args:
            mailId (int): メールID
            fileId (int): ファイルID
            file (object): 添付ファイル
            chunkNo (str): チャンク番号
            chunkTotalNumber (str): ファイル分割総数

        Raises:
            PDSException: PDS例外処理
            e: 例外処理
            PDSException: PDS例外処理

        Returns:
            result: 処理結果
            errorInfo: エラー情報
        """
        error_info_list = []
        EXEC_NAME_JP = "WBTファイル登録API実行"
        try:
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_IN_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            # 01.引数検証処理（入力チェック）
            # 01-01.「引数．メールID」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(mailId):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "メールID"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "メールID")
                    }
                )

            # 01-02.「引数．メールID」に値が設定されており、型が数値型ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_type(mailId, int):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "メールID", "数値"))
                error_info_list.append(
                    {
                        "errorCode": "020019",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "メールID", "数値")
                    }
                )

            # 01-03.「引数．ファイルID」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(fileId):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "ファイルID"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "ファイルID")
                    }
                )

            # 01-04.「引数．ファイルID」に値が設定されており、型が数値型ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_type(fileId, int):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "ファイルID", "数値"))
                error_info_list.append(
                    {
                        "errorCode": "020019",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "ファイルID", "数値")
                    }
                )

            # 01-05.「引数．添付ファイル」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(file):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "添付ファイル"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "添付ファイル")
                    }
                )

            # 01-06.「引数．添付ファイル」に値が設定されており、型がFile Stream型ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not type(file) is io.BytesIO:
                print(type(file))
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "添付ファイル", "File Stream"))
                error_info_list.append(
                    {
                        "errorCode": "020019",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "添付ファイル", "File Stream")
                    }
                )

            # 01-07.「引数．チャンク番号」に値が設定されており、型が文字列型ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_type(chunkNo, str):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "チャンク番号", "文字列"))
                error_info_list.append(
                    {
                        "errorCode": "020019",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "チャンク番号", "文字列")
                    }
                )

            # 01-08.「引数．チャンク番号」に値が設定されており、値が入力規則に違反している場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_alpha_num(chunkNo):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020003"]["logMessage"], "チャンク番号"))
                error_info_list.append(
                    {
                        "errorCode": "020003",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "チャンク番号")
                    }
                )

            # 01-09.「引数．ファイル分割総数」に値が設定されており、型が文字列型ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_type(chunkTotalNumber, str):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "チャンク分割総数", "文字列"))
                error_info_list.append(
                    {
                        "errorCode": "020019",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "チャンク分割総数", "文字列")
                    }
                )

            # 01-10.「引数．ファイル分割総数」に値が設定されており、値が入力規則に違反している場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_pds_user_public_key_idx(chunkTotalNumber):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020003"]["logMessage"], "チャンク分割総数"))
                error_info_list.append(
                    {
                        "errorCode": "020003",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "チャンク分割総数")
                    }
                )

            # 01-11.「変数．エラー情報リスト」に値が設定されている場合、エラー作成処理を実施する
            # 01-11-01.下記のパラメータでPDSExceptionオブジェクトを作成する
            # 01-11-02.PDSExceptionオブジェクトをエラーとしてスローする
            if len(error_info_list) != 0:
                raise PDSException(*error_info_list)

            # TODO(t.ii)：WBTの処理は共通処理側で直値を返却するようにしておく
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            """
            return {
                "result": True
            }
            """
            # エラー返却
            return {
                "result": False,
                "errorInfo": {
                    "errorCode": "990013",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["990013"]["message"], "990013")
                }
            }
            """
            # 02.ファイル登録API実行
            error_info = None
            # 02-01.以下の引数でWBTのファイル登録API呼び出し処理を実行する
            try:
                header = {"Content-Type": "multipart/form-data", "Ocp-Apim-Subscription-Key": "e7b58ee4695c4621a9de98de48b1aa38"}
                request_body_data = {
                    "file": file,
                    "chunkNo": chunkNo,
                    "chunkTotalNumber": chunkTotalNumber
                }
                url = "http://localhost:8080/sdms/mails/" + mailId + "/resume/" + fileId
                # 02-02.WBTのファイル登録APIからのレスポンスを、「変数．ファイル登録API結果」に格納する
                post_reslt = self.post_request(url=url, headers=header, data=request_body_data)
                if not post_reslt["result"]:
                    # 02-03.WebBureauTransferの処理に失敗した場合、「変数．エラー情報」にエラー情報を作成する
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990013"]["logMessage"]))
                    error_info = {
                        "errorCode": "990013",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["990013"]["message"], "990013")
                    }
            except Exception:
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990013"]["logMessage"]))
                error_info = {
                    "errorCode": "990013",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["990013"]["message"], "990013")
                }

            # 03.ファイル登録API実行チェック処理
            if error_info is not None:
                # 03-01.「変数．エラー情報」が設定されていない場合、「05.終了処理」に遷移する
                pass
            else:
                # 03-02.「変数．エラー情報」が設定されている場合、「04. ファイル登録API実行エラー処理」に遷移する
                # 04.ファイル登録API実行チエラー処理
                # 04-01.レスポンス情報を作成し、返却する
                if logging.ERROR == logUtil.output_outlog(EXEC_NAME_JP, error_info):
                    self.logger.error(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                else:
                    self.logger.warning(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                return {
                    "result": False,
                    "errorInfo": error_info
                }

            # 04.終了処理
            # 04-01.処理を終了する
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            return {
                "result": True
            }
            """
        # 例外処理（PDSExceptionクラス）：
        except PDSException as e:
            # PDSExceptionオブジェクトをエラーとしてスローする
            raise e
        # 例外処理：
        except Exception as e:
            # エラー情報をCloudWatchへログ出力する
            self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["999999"]["logMessage"], str(e), traceback.format_exc()))
            # 下記のパラメータでPDSExceptionオブジェクトを作成する
            # PDSExceptionオブジェクトをエラーとしてスローする
            raise PDSException(
                {
                    "errorCode": "999999",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
                }
            )

    def wbt_mail_cancel_exec(
        self,
        mailId: int
    ):
        """
        WBT送信取り消しAPI実行

        Args:
            mailId (int): メールID

        Raises:
            PDSException: PDS例外処理
            e: 例外処理
            PDSException: PDS例外処理
        """
        error_info_list = []
        EXEC_NAME_JP = "WBT送信取り消しAPI実行"
        try:
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_IN_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            # 01.引数検証処理（入力チェック）
            # 01-01.「引数．メールID」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(mailId):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "メールID"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "メールID")
                    }
                )

            # 01-02.「引数．メールID」に値が設定されており、型が数値型ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_type(mailId, int):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "メールID", "数値"))
                error_info_list.append(
                    {
                        "errorCode": "020019",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "メールID", "数値")
                    }
                )

            # 01-03.「変数．エラー情報リスト」に値が設定されている場合、エラー作成処理を実施する
            # 01-03-01.下記のパラメータでPDSExceptionオブジェクトを作成する
            # 01-03-02.PDSExceptionオブジェクトをエラーとしてスローする
            if len(error_info_list) != 0:
                raise PDSException(*error_info_list)

            # TODO(t.ii)：WBTの処理は共通処理側で直値を返却するようにしておく
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            return {
                "result": True
            }
            """
            # エラー返却
            return {
                "result": False,
                "errorInfo": {
                    "errorCode": "990012",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["990012"]["message"], "990012")
                }
            }
            """
            """
            # 02.送信取り消しAPI実行
            error_info = None
            # 02-01.以下の引数でWBTの送信取り消しAPI呼び出し処理を実行する
            try:
                header = {"Content-Type": "application/json", "Ocp-Apim-Subscription-Key": "e7b58ee4695c4621a9de98de48b1aa38"}
                request_body_data = {}
                url = "http://localhost:8080/sdms/mails/outbox/" + mailId + "/cancel"
                # 02-02.WBTの送信取り消しAPIからのレスポンスを、「変数．送信取り消しAPI結果」に格納する
                post_reslt = self.post_request(url=url, headers=header, data=request_body_data)
                if not post_reslt["result"]:
                    # 02-03.WebBureauTransferの処理に失敗した場合、「変数．エラー情報」にエラー情報を作成する
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990012"]["logMessage"]))
                    error_info = {
                        "errorCode": "990012",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["990012"]["message"], "990012")
                    }
            except Exception:
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990012"]["logMessage"]))
                error_info = {
                    "errorCode": "990012",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["990012"]["message"], "990012")
                }

            # 03.共通エラーチェック処理
            # 03-01.共通エラーチェック処理を実行する
            # 03-02.例外が発生した場合、例外処理に遷移
            if error_info is not None:
                self.common_error_check(error_info)

            # 04.終了処理
            # 04-01.レスポンス情報を作成し、返却する
            # 04-01-01.「変数．エラー情報」に値が設定されていない場合、下記のレスポンス情報を返却する
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            return {
                "result": True
            }
            """
        # 例外処理（PDSExceptionクラス）：
        except PDSException as e:
            # PDSExceptionオブジェクトをエラーとしてスローする
            raise e
        # 例外処理：
        except Exception as e:
            # エラー情報をCloudWatchへログ出力する
            self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["999999"]["logMessage"], str(e), traceback.format_exc()))
            # 下記のパラメータでPDSExceptionオブジェクトを作成する
            # PDSExceptionオブジェクトをエラーとしてスローする
            raise PDSException(
                {
                    "errorCode": "999999",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
                }
            )

    # 検索用 水野担当ファイル
    def create_postgresql_log(self, e, param: str, value: str, stackTrace: str):
        """
        postgresqlエラー処理

        Args:
            e (Object): 例外オブジェクト
            param (str): パラメータ名
            value (str): パラメータ値
            stackTrace (str): スタックトレース

        Returns:
            dict: エラー情報
        """
        EXEC_NAME_JP = "postgresqlエラー処理"
        try:
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_IN_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            # 01.引数検証処理（入力チェック）
            error_info_list = []
            # 01-01.「引数．例外オブジェクト」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(e):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "例外オブジェクト"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "例外オブジェクト")
                    }
                )

            # 01-02.「変数．エラー情報リスト」に値が設定されている場合、エラー作成処理を実施する
            if len(error_info_list) != 0:
                raise PDSException(*error_info_list)

            # 02.postgresql例外処理
            error_info = None
            # 02-01.「引数．例外オブジェクト」が「postgresql_error」の場合、「引数．例外オブジェクト．エラーコード」の前2桁で判定し、「変数．エラー情報」を作成し、エラーログをCloudWatchにログ出力する
            if isinstance(e, postgresql_error):
                # 02-01-01.「引数．例外オブジェクト．エラーコード」の前2桁=03（03クラス — SQL文の未完了）の場合
                if e.pgcode[0:2] == "03":
                    error_info = {
                        "errorCode": "991001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["991001"]["message"], "991001")
                    }
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["991001"]["logMessage"], e.pgcode, e.pgerror))
                # 02-01-02.「引数．例外オブジェクト．エラーコード」の前2桁=08（08 クラス — 接続の例外）の場合
                elif e.pgcode[0:2] == "08":
                    error_info = {
                        "errorCode": "991002",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["991002"]["message"], "991002")
                    }
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["991002"]["logMessage"], e.pgcode, e.pgerror))
                # 02-01-03.「引数．例外オブジェクト．エラーコード」の前2桁=09（09 クラス — トリガによるアクションの例外）の場合
                elif e.pgcode[0:2] == "09":
                    error_info = {
                        "errorCode": "991003",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["991003"]["message"], "991003")
                    }
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["991003"]["logMessage"], e.pgcode, e.pgerror))
                # 02-01-04.「引数．例外オブジェクト．エラーコード」の前2桁=0A（0A クラス — サポートされない機能）の場合
                elif e.pgcode[0:2] == "0A":
                    error_info = {
                        "errorCode": "991004",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["991004"]["message"], "991004")
                    }
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["991004"]["logMessage"], e.pgcode, e.pgerror))
                # 02-01-05.「引数．例外オブジェクト．エラーコード」の前2桁=0B（0Bクラス — 無効なトランザクションの初期）の場合
                elif e.pgcode[0:2] == "0B":
                    error_info = {
                        "errorCode": "991005",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["991005"]["message"], "991005")
                    }
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["991005"]["logMessage"], e.pgcode, e.pgerror))
                # 02-01-06.「引数．例外オブジェクト．エラーコード」の前2桁=0F（0F クラス — ロケータの例外）の場合
                elif e.pgcode[0:2] == "0F":
                    error_info = {
                        "errorCode": "991006",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["991006"]["message"], "991006")
                    }
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["991006"]["logMessage"], e.pgcode, e.pgerror))
                # 02-01-07.「引数．例外オブジェクト．エラーコード」の前2桁=0L（0L クラス — 無効な権限付与）の場合
                elif e.pgcode[0:2] == "0L":
                    error_info = {
                        "errorCode": "991007",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["991007"]["message"], "991007")
                    }
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["991007"]["logMessage"], e.pgcode, e.pgerror))
                # 02-01-08.「引数．例外オブジェクト．エラーコード」の前2桁=0P（0P クラス — 無効なロールの指定）の場合
                elif e.pgcode[0:2] == "0P":
                    error_info = {
                        "errorCode": "991008",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["991008"]["message"], "991008")
                    }
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["991008"]["logMessage"], e.pgcode, e.pgerror))
                # 02-01-09.「引数．例外オブジェクト．エラーコード」の前2桁=20（20 クラス — Caseが存在しない）の場合
                elif e.pgcode[0:2] == "20":
                    error_info = {
                        "errorCode": "991009",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["991009"]["message"], "991009")
                    }
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["991009"]["logMessage"], e.pgcode, e.pgerror))
                # 02-01-10.「引数．例外オブジェクト．エラーコード」の前2桁=21（21クラス — 次数違反）の場合
                elif e.pgcode[0:2] == "21":
                    error_info = {
                        "errorCode": "991010",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["991010"]["message"], "991010")
                    }
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["991010"]["logMessage"], e.pgcode, e.pgerror))
                # 02-01-11.「引数．例外オブジェクト．エラーコード」の前2桁=22（22 クラス — データ例外）の場合
                elif e.pgcode[0:2] == "22":
                    error_info = {
                        "errorCode": "991011",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["991011"]["message"], "991011")
                    }
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["991011"]["logMessage"], e.pgcode, e.pgerror))
                # 02-01-12.「引数．例外オブジェクト．エラーコード」の前2桁=23（23 クラス — 整合性制約違反）の場合
                elif e.pgcode[0:2] == "23":
                    if e.pgcode == "23505":
                        error_info = {
                            "errorCode": "030001",
                            "message": logUtil.message_build(MessageConstClass.ERRORS["030001"]["message"], param, value)
                        }
                        self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["030001"]["logMessage"], param, value))
                    else:
                        error_info = {
                            "errorCode": "991012",
                            "message": logUtil.message_build(MessageConstClass.ERRORS["991012"]["message"], "991012")
                        }
                        self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["991012"]["logMessage"], e.pgcode, e.pgerror))
                # 02-01-13.「引数．例外オブジェクト．エラーコード」の前2桁=24（24 クラス — 無効なカーソル状態）の場合
                elif e.pgcode[0:2] == "24":
                    error_info = {
                        "errorCode": "991013",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["991013"]["message"], "991013")
                    }
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["991013"]["logMessage"], e.pgcode, e.pgerror))
                # 02-01-14.「引数．例外オブジェクト．エラーコード」の前2桁=25（25 クラス — 無効なトランザクション状態）の場合
                elif e.pgcode[0:2] == "25":
                    error_info = {
                        "errorCode": "991014",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["991014"]["message"], "991014")
                    }
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["991014"]["logMessage"], e.pgcode, e.pgerror))
                # 02-01-15.「引数．例外オブジェクト．エラーコード」の前2桁=26（26 クラス — 無効なSQL文の名前）の場合
                elif e.pgcode[0:2] == "26":
                    error_info = {
                        "errorCode": "991015",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["991015"]["message"], "991015")
                    }
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["991015"]["logMessage"], e.pgcode, e.pgerror))
                # 02-01-16.「引数．例外オブジェクト．エラーコード」の前2桁=27（27クラス — トリガによるデータ変更違反）の場合
                elif e.pgcode[0:2] == "27":
                    error_info = {
                        "errorCode": "991016",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["991016"]["message"], "991016")
                    }
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["991016"]["logMessage"], e.pgcode, e.pgerror))
                # 02-01-17.「引数．例外オブジェクト．エラーコード」の前2桁=28（28 クラス — 無効な認証指定）の場合
                elif e.pgcode[0:2] == "28":
                    error_info = {
                        "errorCode": "991017",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["991017"]["message"], "991017")
                    }
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["991017"]["logMessage"], e.pgcode, e.pgerror))
                # 02-01-18.「引数．例外オブジェクト．エラーコード」の前2桁=2B（2B クラス — 依存する権限記述子がまだ存在する）の場合
                elif e.pgcode[0:2] == "2B":
                    error_info = {
                        "errorCode": "991018",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["991018"]["message"], "991018")
                    }
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["991018"]["logMessage"], e.pgcode, e.pgerror))
                # 02-01-19.「引数．例外オブジェクト．エラーコード」の前2桁=2D（2D クラス — 無効なトランザクションの終了）の場合
                elif e.pgcode[0:2] == "2D":
                    error_info = {
                        "errorCode": "991019",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["991019"]["message"], "991019")
                    }
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["991019"]["logMessage"], e.pgcode, e.pgerror))
                # 02-01-20.「引数．例外オブジェクト．エラーコード」の前2桁=2F（2F クラス — SQL関数例外）の場合
                elif e.pgcode[0:2] == "2F":
                    error_info = {
                        "errorCode": "991020",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["991020"]["message"], "991020")
                    }
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["991020"]["logMessage"], e.pgcode, e.pgerror))
                # 02-01-21.「引数．例外オブジェクト．エラーコード」の前2桁=34（34クラス — 無効なカーソル名称）の場合
                elif e.pgcode[0:2] == "34":
                    error_info = {
                        "errorCode": "991021",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["991021"]["message"], "991021")
                    }
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["991021"]["logMessage"], e.pgcode, e.pgerror))
                # 02-01-22.「引数．例外オブジェクト．エラーコード」の前2桁=38（38 クラス — 外部関数例外）の場合
                elif e.pgcode[0:2] == "38":
                    error_info = {
                        "errorCode": "991022",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["991022"]["message"], "991022")
                    }
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["991022"]["logMessage"], e.pgcode, e.pgerror))
                # 02-01-23.「引数．例外オブジェクト．エラーコード」の前2桁=39（39 クラス — 外部関数呼び出し例外）の場合
                elif e.pgcode[0:2] == "39":
                    error_info = {
                        "errorCode": "991023",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["991023"]["message"], "991023")
                    }
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["991023"]["logMessage"], e.pgcode, e.pgerror))
                # 02-01-24.「引数．例外オブジェクト．エラーコード」の前2桁=3B（3B クラス — セーブポイント例外）の場合
                elif e.pgcode[0:2] == "3B":
                    error_info = {
                        "errorCode": "991024",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["991024"]["message"], "991024")
                    }
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["991024"]["logMessage"], e.pgcode, e.pgerror))
                # 02-01-25.「引数．例外オブジェクト．エラーコード」の前2桁=3D（3Dクラス — 無効なカタログ名称）の場合
                elif e.pgcode[0:2] == "3D":
                    error_info = {
                        "errorCode": "991025",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["991025"]["message"], "991025")
                    }
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["991025"]["logMessage"], e.pgcode, e.pgerror))
                # 02-01-26.「引数．例外オブジェクト．エラーコード」の前2桁=3F（3F クラス — 無効なスキーマ名称）の場合
                elif e.pgcode[0:2] == "3F":
                    error_info = {
                        "errorCode": "991026",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["991026"]["message"], "991026")
                    }
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["991026"]["logMessage"], e.pgcode, e.pgerror))
                # 02-01-27.「引数．例外オブジェクト．エラーコード」の前2桁=40（40 クラス — トランザクションロールバック）の場合
                elif e.pgcode[0:2] == "40":
                    error_info = {
                        "errorCode": "991027",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["991027"]["message"], "991027")
                    }
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["991027"]["logMessage"], e.pgcode, e.pgerror))
                # 02-01-28.「引数．例外オブジェクト．エラーコード」の前2桁=42（42 クラス — 構文エラー、もしくはアクセスロール違反）の場合
                elif e.pgcode[0:2] == "42":
                    error_info = {
                        "errorCode": "991028",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["991028"]["message"], "991028")
                    }
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["991028"]["logMessage"], e.pgcode, e.pgerror))
                # 02-01-29.「引数．例外オブジェクト．エラーコード」の前2桁=44（44 クラス — 検査オプションに伴う違反）の場合
                elif e.pgcode[0:2] == "44":
                    error_info = {
                        "errorCode": "991029",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["991029"]["message"], "991029")
                    }
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["991029"]["logMessage"], e.pgcode, e.pgerror))
                # 02-01-30.「引数．例外オブジェクト．エラーコード」の前2桁=53（53クラス — リソース不足）の場合
                elif e.pgcode[0:2] == "53":
                    error_info = {
                        "errorCode": "991030",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["991030"]["message"], "991030")
                    }
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["991030"]["logMessage"], e.pgcode, e.pgerror))
                # 02-01-31.「引数．例外オブジェクト．エラーコード」の前2桁=54（54 クラス — プログラム制限の超過）の場合
                elif e.pgcode[0:2] == "54":
                    error_info = {
                        "errorCode": "991031",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["991031"]["message"], "991031")
                    }
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["991031"]["logMessage"], e.pgcode, e.pgerror))
                # 02-01-32.「引数．例外オブジェクト．エラーコード」の前2桁=55（55 クラス — 必要条件を満たさないオブジェクト）の場合
                elif e.pgcode[0:2] == "55":
                    error_info = {
                        "errorCode": "991032",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["991032"]["message"], "991032")
                    }
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["991032"]["logMessage"], e.pgcode, e.pgerror))
                # 02-01-33.「引数．例外オブジェクト．エラーコード」の前2桁=57（57 クラス — 操作の介入）の場合
                elif e.pgcode[0:2] == "57":
                    if e.pgcode == "57014":
                        error_info = {
                            "errorCode": "991101",
                            "message": logUtil.message_build(MessageConstClass.ERRORS["991101"]["message"], "991101")
                        }
                        self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["991101"]["logMessage"], e.pgcode, e.pgerror))
                    else:
                        error_info = {
                            "errorCode": "991033",
                            "message": logUtil.message_build(MessageConstClass.ERRORS["991033"]["message"], "991033")
                        }
                        self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["991033"]["logMessage"], e.pgcode, e.pgerror))
                # 02-01-34.「引数．例外オブジェクト．エラーコード」の前2桁=58（58 クラス — システムエラー（外部原因によるPostgreSQL自体のエラー））の場合
                elif e.pgcode[0:2] == "58":
                    error_info = {
                        "errorCode": "991034",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["991034"]["message"], "991034")
                    }
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["991034"]["logMessage"], e.pgcode, e.pgerror))
                # 02-01-35.「引数．例外オブジェクト．エラーコード」の前2桁=F0（F0クラス — 設定ファイルエラー）の場合
                elif e.pgcode[0:2] == "F0":
                    error_info = {
                        "errorCode": "991035",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["991035"]["message"], "991035")
                    }
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["991035"]["logMessage"], e.pgcode, e.pgerror))
                # 02-01-36.「引数．例外オブジェクト．エラーコード」の前2桁=P0（P0 クラス — PL/pgSQLエラー）の場合
                elif e.pgcode[0:2] == "P0":
                    error_info = {
                        "errorCode": "991036",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["991036"]["message"], "991036")
                    }
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["991036"]["logMessage"], e.pgcode, e.pgerror))
                # 02-01-37「引数．例外オブジェクト．エラーコード」の前2桁=XX（XX クラス — 内部エラー）の場合
                elif e.pgcode[0:2] == "XX":
                    error_info = {
                        "errorCode": "991037",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["991037"]["message"], "991037")
                    }
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["991037"]["logMessage"], e.pgcode, e.pgerror))
                # 02-01-38.上記のすべてに当てはまらない場合
                else:
                    error_info = {
                        "errorCode": "999999",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
                    }
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["999999"]["logMessage"], str(e), stackTrace))
            else:
                # 02-02.「引数．例外オブジェクト」が「postgresql_error」以外の場合、「変数．エラー情報」を作成し、エラーログをCloudWatchにログ出力する
                error_info = {
                    "errorCode": "999999",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
                }
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["999999"]["logMessage"], str(e), stackTrace))

            # 03.終了処理
            # 03-01.レスポンス情報を作成し、返却する
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            return {"errorInfo": error_info}

        # 例外処理（PDSExceptionクラス）：
        except PDSException as e:
            raise e

        # 例外処理：
        except Exception as e:
            self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["999999"]["logMessage"], str(e), traceback.format_exc()))
            raise PDSException(
                {
                    "errorCode": "999999",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
                }
            )

    def common_error_check(self, error_info: dict, *callback_exec: CallbackExecutor) -> None:
        """
        共通エラーチェック処理

        Args:
            error_info (dict): エラー情報
            *callback_exec(tuple(CallbackExecutor)): コールバック関数

        """
        EXEC_NAME_JP = "共通エラーチェック処理"
        try:
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_IN_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            # 01.エラー情報有無判定処理
            # 01-01.「引数．エラー情報」がNullの場合、「05.終了処理」に遷移する
            # 01-02.「引数．エラー情報」がNull以外の場合、「02.コールバック関数実行判定処理」に遷移する
            if error_info is not None:
                # 02.コールバック関数実行判定処理
                # 02-01.「引数．コールバック関数」の要素数が0の場合、「04.例外オブジェクト作成処理」に遷移する
                # 02-02.「引数．コールバック関数」が要素数が0以外の場合、「03.コールバック関数実行処理」に遷移する
                if len(callback_exec) != 0:
                    # 03.コールバック関数実行処理
                    for callback in callback_exec:
                        # 03-01.「引数．コールバック関数」に指定された内容を実施する
                        callback.execute()
                # 04.例外オブジェクト作成処理
                # 04-01.「引数．エラー情報」がリスト型の場合、下記のパラメータでPDSExceptionオブジェクトを作成する
                if type(error_info) is list:
                    raise PDSException(*error_info)
                # 04-02.「引数．エラー情報」が辞書型の場合、下記のパラメータでPDSExceptionオブジェクトを作成する
                if type(error_info) is dict:
                    raise PDSException(error_info)
            # 05.終了処理
            # 05.処理を終了する
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))

        # 例外処理（PDSExceptionクラス）
        except PDSException as e:
            # PDSExceptionオブジェクトをエラーとしてスローする
            raise e
        # 例外処理
        except Exception as e:
            # エラー情報をCloudWatchへログ出力する
            self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["999999"]["logMessage"], str(e), traceback.format_exc()))
            # 下記のパラメータでPDSExceptionオブジェクトを作成する
            raise PDSException(
                {
                    "errorCode": "999999",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
                }
            )

    # 検索用 水野担当ファイル
    def insert_api_history(
        self,
        execId: str,
        pdsUserId: str,
        apiType: str,
        pathParamPdsUserDomainName: str,
        execPath: str,
        execParam: str,
        execStatus: bool,
        execUserId: str,
        registerDatetime: str
    ):
        """
        API実行履歴登録処理

        Args:
            execId (str): 実行ID
            pdsUserId (str): PDSユーザID
            apiType (str): API種別
            pathParamPdsUserDomainName (str): パスパラメータPDSユーザドメイン
            execPath (str): 実行パス
            execParam (str): 実行パラメータ
            execStatus (bool): 実行ステータス
            execUserId (str): 実行ユーザID
            registerDatetime (str): 実行日時

        Returns:
            dict: 処理結果
        """
        error_info_list = []
        EXEC_NAME_JP = "API実行履歴登録処理"
        try:
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_IN_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            # 01.引数検証処理（入力チェック）
            # 01-01.「引数．実行ID」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(execId):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "実行ID"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "実行ID")
                    }
                )
            # 01-02.「引数．実行ID」に値が設定されており、値の型が文字列型ではない場合、「変数．エラー情報リスト」にエラー情報を追加
            if not checkUtil.check_type(execId, str):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "実行ID", "文字列"))
                error_info_list.append(
                    {
                        "errorCode": "020019",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "実行ID", "文字列")
                    }
                )
            # 01-03.PDSユーザID検証処理
            # 01-03-01.PDSユーザID検証処理を実行する
            check_pds_user_id_result = checkPdsUserId.CheckPdsUserId(self.logger, pdsUserId, False).get_result()
            # 01-03-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not check_pds_user_id_result["result"]:
                [error_info_list.append(error_info) for error_info in check_pds_user_id_result["errorInfo"]]

            # 01-04.「引数．API種別」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(apiType):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "API種別"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "API種別")
                    }
                )
            # 01-05.「引数．API種別」に値が設定されており、型が文字列型ではない場合、エラー情報リストにエラー情報を追加する
            if not checkUtil.check_type(apiType, str):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "API種別", "文字列"))
                error_info_list.append(
                    {
                        "errorCode": "020019",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "API種別", "文字列")
                    }
                )

            # 01-06.「引数．API種別」に値が設定されており、値に入力可能文字以外が含まれている場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_api_type(apiType):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020020"]["logMessage"], "API種別"))
                error_info_list.append(
                    {
                        "errorCode": "020020",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020020"]["message"], "API種別")
                    }
                )

            # 01-07.「引数．パスパラメータPDSユーザドメイン」に値が設定されており、型が文字列型ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_type(pathParamPdsUserDomainName, str):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "パスパラメータPDSユーザドメイン", "文字列"))
                error_info_list.append(
                    {
                        "errorCode": "020019",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "パスパラメータPDSユーザドメイン", "文字列")
                    }
                )

            # 01-08.「引数．パスパラメータPDSユーザドメイン」に値が設定されており、値の桁数が5桁未満の場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_min_length(pathParamPdsUserDomainName, 5):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020016"]["logMessage"], "パスパラメータPDSユーザドメイン", "5"))
                error_info_list.append(
                    {
                        "errorCode": "020016",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020016"]["message"], "パスパラメータPDSユーザドメイン", "5")
                    }
                )

            # 01-09.「引数．パスパラメータPDSユーザドメイン」に値が設定されており、値の桁数が20桁を超過する場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_max_length(pathParamPdsUserDomainName, 20):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020002"]["logMessage"], "パスパラメータPDSユーザドメイン", "20"))
                error_info_list.append(
                    {
                        "errorCode": "020002",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020002"]["message"], "パスパラメータPDSユーザドメイン", "20")
                    }
                )
            # 01-10.「引数．パスパラメータPDSユーザドメイン」に値が設定されており、値が入力規則に違反している場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_pds_user_domain_name(pathParamPdsUserDomainName):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020003"]["logMessage"], "パスパラメータPDSユーザドメイン"))
                error_info_list.append(
                    {
                        "errorCode": "020003",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "パスパラメータPDSユーザドメイン")
                    }
                )

            # 01-11.「引数．実行パス」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(execPath):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "実行パス"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "実行パス")
                    }
                )
            # 01-12.「引数．実行パス」に値が設定されており、値の型が文字列型ではない場合、「変数．エラー情報リスト」にエラー情報を追加
            if not checkUtil.check_type(execPath, str):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "実行パス", "文字列"))
                error_info_list.append(
                    {
                        "errorCode": "020019",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "実行パス", "文字列")
                    }
                )

            # 01-13.「引数．実行パラメータ」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(execParam):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "実行パラメータ"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "実行パラメータ")
                    }
                )
            # 01-14.「引数．実行パラメータ」に値が設定されており、値の型が文字列型ではない場合、「変数．エラー情報リスト」にエラー情報を追加
            if not checkUtil.check_type(execParam, str):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "実行パラメータ", "文字列"))
                error_info_list.append(
                    {
                        "errorCode": "020019",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "実行パラメータ", "文字列")
                    }
                )

            # 01-15.「引数．実行ステータス」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(execStatus):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "実行ステータス"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "実行ステータス")
                    }
                )
            # 01-16.「引数．実行ステータス」に値が設定されており、値の型が文字列型ではない場合、「変数．エラー情報リスト」にエラー情報を追加
            if not checkUtil.check_type(execStatus, bool):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "実行ステータス", "論理"))
                error_info_list.append(
                    {
                        "errorCode": "020019",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "実行ステータス", "論理")
                    }
                )

            # 01-17.「引数．実行ユーザID」に値が設定されており、型が文字列型ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_type(execUserId, str):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "実行ユーザID", "文字列"))
                error_info_list.append(
                    {
                        "errorCode": "020019",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "実行ユーザID", "文字列")
                    }
                )

            # 01-18.「引数．実行ユーザID」に値が設定されており、値の桁数が3桁未満の場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_min_length(execUserId, 3):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020016"]["logMessage"], "実行ユーザID", "3"))
                error_info_list.append(
                    {
                        "errorCode": "020016",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020016"]["message"], "実行ユーザID", "3")
                    }
                )

            # 01-19.「引数．実行ユーザID」に値が設定されており、値の桁数が16桁を超過する場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_max_length(execUserId, 16):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020002"]["logMessage"], "実行ユーザID", "16"))
                error_info_list.append(
                    {
                        "errorCode": "020002",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020002"]["message"], "実行ユーザID", "16")
                    }
                )

            # 01-20.「引数．実行日時」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(registerDatetime):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "実行日時"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "実行日時")
                    }
                )
            # 01-21.「引数．実行日時」に値が設定されており、型が文字列型ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_type(registerDatetime, str):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "実行日時", "文字列"))
                error_info_list.append(
                    {
                        "errorCode": "020019",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "実行日時", "文字列")
                    }
                )

            # 01-22.「引数．実行日時」に値が設定されており、値の桁数が23桁ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_length(registerDatetime, 23):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020014"]["logMessage"], "実行日時", "23"))
                error_info_list.append(
                    {
                        "errorCode": "020014",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020014"]["message"], "実行日時", "23")
                    }
                )

            # 01-23.「引数．実行日時」に値が設定されており、値が入力規則に違反している場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_time_stamp(registerDatetime):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020003"]["logMessage"], "実行日時"))
                error_info_list.append(
                    {
                        "errorCode": "020003",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "実行日時")
                    }
                )

            # 01-24.「変数．エラー情報リスト」に値が設定されている場合、エラー作成処理を実施する
            if len(error_info_list) != 0:
                raise PDSException(*error_info_list)

            # 02.共通DB接続準備処理
            common_db_connection_resource: PostgresDbUtilClass = None
            # 02-01.AWS SecretsManagerから共通DB接続情報を取得して、「変数．共通DB接続情報」に格納する
            # 02-02.「変数．共通DB接続情報」を利用して、共通DBに対してのコネクションを作成する
            common_db_info_response = self.get_common_db_info_and_connection()
            if not common_db_info_response["result"]:
                if logging.ERROR == logUtil.output_outlog(EXEC_NAME_JP, common_db_info_response["errorInfo"]):
                    self.logger.error(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                else:
                    self.logger.warning(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                return common_db_info_response
            else:
                common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
                common_db_connection = common_db_info_response["common_db_connection"]

            # 03.トランザクション作成処理
            # 03-01.「API実行履歴登録トランザクション」を作成する

            # 04.API実行履歴登録処理
            api_history_insert_error_info = None
            # 04-01.API実行履歴テーブルに登録する
            api_history_insert_result = common_db_connection_resource.insert(
                common_db_connection,
                SqlConstClass.API_HISTORY_INSERT_SQL,
                execId,
                pdsUserId,
                apiType,
                pathParamPdsUserDomainName,
                execPath,
                execParam,
                execStatus,
                execUserId,
                registerDatetime
            )
            # 04-03.処理が失敗した場合は「postgresqlエラー処理」からのレスポンスを、「変数．エラー情報」に格納する
            if not api_history_insert_result["result"]:
                api_history_insert_error_info = self.create_postgresql_log(
                    api_history_insert_result["errorObject"],
                    "実行ID",
                    execId,
                    api_history_insert_result["stackTrace"]
                ).get("errorInfo")

            # 05.共通エラーチェック処理
            # 05-01.共通エラーチェック処理を実行する
            if api_history_insert_error_info is not None:
                rollback_transaction = CallbackExecutor(
                    self.common_check_postgres_rollback,
                    common_db_connection,
                    common_db_connection_resource
                )
                self.common_error_check(
                    api_history_insert_error_info,
                    rollback_transaction
                )

            # 06.トランザクションコミット処理
            # 06-01.「API実行履歴登録トランザクション」をコミットする
            common_db_connection_resource.commit_transaction(common_db_connection)
            common_db_connection_resource.close_connection(common_db_connection)

            # 07.終了処理
            # 07-01.レスポンス情報を作成し、返却する
            if len(error_info_list) == 0:
                self.logger.info(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                return {
                    "result": True
                }
            # 07-02.「変数．エラー情報」に値が設定されている場合、下記のレスポンス情報を返却する
            else:
                if logging.ERROR == logUtil.output_outlog(EXEC_NAME_JP, error_info_list):
                    self.logger.error(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                else:
                    self.logger.warning(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                return {
                    "result": False,
                    "errorInfo": api_history_insert_error_info
                }

        # 例外処理（PDSExceptionクラス）：
        except PDSException as e:
            raise e

        # 例外処理：
        except Exception as e:
            self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["999999"]["logMessage"], str(e), traceback.format_exc()))
            raise PDSException(
                {
                    "errorCode": "999999",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
                }
            )

    # 検索用 水野担当ファイル
    def check_approval_user_info(self, approvalUserId: str, approvalUserPassword: str, commonDbInfo: object):
        """
        承認者情報確認処理

        Args:
            approval_user_id (str): 承認者TFオペレータID
            approval_user_password (str): 承認者TFオペレータパスワード
            common_db_secret_info (object): 共通DB接続情報
        """
        error_info_list = []
        error_info = None
        EXEC_NAME_JP = "承認者情報確認処理"
        try:
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_IN_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            # 01.引数検証処理（入力チェック）
            # 01-01.「引数．承認者TFオペレータID」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(approvalUserId):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "承認者TFオペレータID"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "承認者TFオペレータID")
                    }
                )
            # 01-02.「引数．承認者TFオペレータパスワード」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(approvalUserPassword):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "承認者TFオペレータパスワード"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "承認者TFオペレータパスワード")
                    }
                )
            # 01-03.「引数．共通DB接続情報」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(commonDbInfo):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "共通DB接続情報"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "共通DB接続情報")
                    }
                )
            # 01-04.「変数．エラー情報リスト」に値が設定されている場合、エラー作成処理を実施する
            if len(error_info_list) != 0:
                raise PDSException(*error_info_list)

            # 02.パスワードのハッシュ化処理
            # 02-01.「引数．承認TFオペレータパスワード」をハッシュ化してハッシュ化済パスワードを作成する
            crypt_util_class = CryptUtilClass(self.logger)
            hashed_password = crypt_util_class.hash_password(approvalUserPassword)

            # 02.共通DB接続準備処理
            # 02-01.共通DB接続情報取得処理
            common_util = CommonUtilClass(self.logger)
            common_db_connection_resource: PostgresDbUtilClass = None
            # 02-01-01.AWS SecretsManagerから共通DB接続情報を取得して、「変数．共通DB接続情報」に格納する
            # 02-02.「変数．共通DB接続情報」を利用して、共通DBに対してのコネクションを作成する
            common_db_info_response = common_util.get_common_db_info_and_connection()
            if not common_db_info_response["result"]:
                if logging.ERROR == logUtil.output_outlog(EXEC_NAME_JP, common_db_info_response["errorInfo"]):
                    self.logger.error(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                else:
                    self.logger.warning(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                return common_db_info_response
            else:
                common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
                common_db_connection = common_db_info_response["common_db_connection"]

            # 04.TFオペレータ取得処理
            # 04-01.TFオペレータテーブルからデータを取得し、「変数.TFオペレータ取得結果」に1レコードをタプルとして格納する
            tf_operator_select_result = common_db_connection_resource.select_tuple_one(
                common_db_connection,
                SqlConstClass.CHECK_APPROVAL_USER_SELECT_SQL,
                approvalUserId,
                hashed_password,
                get_str_date()
            )
            # 04-02.「変数.TFオペレータ取得結果[0]」が1以外の場合、「変数.エラー情報」を作成し、エラー情報をCloudWatchへログ出力する
            if tf_operator_select_result.get("query_results") and tf_operator_select_result["query_results"][0] != 1:
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020004"]["logMessage"], approvalUserId))
                error_info = {
                    "errorCode": "020004",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020004"]["message"], approvalUserId)
                }
            # 04-03.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not tf_operator_select_result["result"]:
                error_info = self.create_postgresql_log(
                    tf_operator_select_result["errorObject"],
                    None,
                    None,
                    tf_operator_select_result["stackTrace"]
                ).get("errorInfo")

            # 05.共通エラーチェック処理
            # 05-01.共通エラーチェック処理を実行する
            # 05-02.例外が発生した場合、例外処理に遷移
            if error_info is not None:
                self.common_error_check(error_info)

            # 06.終了処理
            # 06-01.返却パラメータを作成し、返却する
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            return {
                "result": True
            }

        # 例外処理（PDSExceptionクラス）：
        except PDSException as e:
            raise e

        # 例外処理：
        except Exception as e:
            self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["999999"]["logMessage"], str(e), traceback.format_exc()))
            raise PDSException(
                {
                    "errorCode": "999999",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
                }
            )

    def check_pds_user_domain(
        self,
        pdsUserDomainName: str,
        headerParamPdsUserId: str
    ):
        """
        PDSユーザドメイン検証処理
        Args:
            pdsUserDomainName (str): PDSユーザドメイン
            headerParamPdsUserId (str): ヘッダパラメータPDSユーザID

        Raises:
            PDSException: PDS例外処理
            e: 例外処理
            PDSException: PDS例外処理

        Returns:
            result: 処理結果
            pdsUserInfo: PDSユーザ情報
            errorInfo: エラー情報
        """
        error_info_list = []
        EXEC_NAME_JP = "PDSユーザドメイン検証処理"
        try:
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_IN_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            # 01.引数検証処理（入力チェック）
            # 01-01.PDSユーザドメイン検証処理
            # 01-01-01.以下の引数でPDSユーザドメイン名検証処理を実行する
            check_pds_user_domain_result = checkPdsUserDomainName.CheckPdsUserDomainName(self.logger, pdsUserDomainName).get_result()
            # 01-01-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not check_pds_user_domain_result["result"]:
                [error_info_list.append(error_info) for error_info in check_pds_user_domain_result["errorInfo"]]

            # 01-02.ヘッダパラメータPDSユーザID検証処理
            # 01-02-01.以下の引数でヘッダパラメータPDSユーザID検証処理を実行する
            check_header_pds_user_id_result = checkPdsUserId.CheckPdsUserId(self.logger, headerParamPdsUserId).get_result()
            # 01-02-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not check_header_pds_user_id_result["result"]:
                [error_info_list.append(error_info) for error_info in check_header_pds_user_id_result["errorInfo"]]

            # 01-03.「変数．エラー情報リスト」に値が設定されている場合、エラー作成処理を実施する
            # 01-03-01.下記のパラメータでPDSExceptionオブジェクトを作成する
            if len(error_info_list) > 0:
                # 01-03-02.PDSExceptionオブジェクトをエラーとしてスローする
                raise PDSException(*error_info_list)

            # 02.共通DB接続準備処理
            # 02-01.共通DB接続情報取得処理
            common_db_connection_resource: PostgresDbUtilClass = None
            # 02-01-01.AWS SecretsManagerから共通DB接続情報を取得して、「変数．共通DB接続情報」に格納する
            # 02-02.「変数．共通DB接続情報」を利用して、共通DBに対してのコネクションを作成する
            common_db_info_response = self.get_common_db_info_and_connection()
            if not common_db_info_response["result"]:
                return common_db_info_response
            else:
                common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
                common_db_connection = common_db_info_response["common_db_connection"]

            # 03.PDSユーザ取得処理
            pds_user_select_error_info = {}
            # 03-01.PDSユーザテーブルからデータを取得し、「変数．PDSユーザ取得結果」に1レコードをタプルとして格納する
            pds_user_select_result = common_db_connection_resource.select_tuple_one(
                common_db_connection,
                SqlConstClass.PDS_USER_DOMAIN_NAME_SELECT_SQL,
                pdsUserDomainName,
                headerParamPdsUserId
            )

            # 03-02.「変数．PDSユーザ取得結果」が0件の場合、「変数．エラー情報」を作成し、エラーログを出力する
            if pds_user_select_result["result"] and pds_user_select_result["rowcount"] == 0:
                pds_user_select_error_info = {
                    "errorCode": "020004",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020004"]["message"], pdsUserDomainName)
                }
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["020004"]["logMessage"], pdsUserDomainName))

            # 03-03.処理が失敗した場合は「変数．エラー情報」を作成し、エラーログをCloudWatchにログ出力する
            #       postgresqlエラー処理からのレスポンスを、「変数．エラー情報」に格納する
            if not pds_user_select_result["result"]:
                pds_user_select_error_info = self.create_postgresql_log(
                    pds_user_select_result["errorObject"],
                    None,
                    None,
                    pds_user_select_result["stackTrace"]
                ).get("errorInfo")

            # 04.終了処理
            # 04-01.レスポンス情報を作成し、返却する
            if len(pds_user_select_error_info) == 0:
                # 返却するpdsUserInfoをtupleからdictに変換する
                pds_user_info_column_list = [
                    'pdsUserId',
                    'groupId',
                    'pdsUserName',
                    'pdsUserDomainName',
                    'apiKey',
                    'pdsUserInstanceSecretName',
                    's3ImageDataBucketName',
                    'userProfilerKmsId',
                    'validFlg',
                    'tokyo_a_mongodb_secret_name',
                    'tokyo_c_mongodb_secret_name',
                    'osaka_a_mongodb_secret_name',
                    'osaka_c_mongodb_secret_name',
                    'salesAddress',
                    'downloadNoticeAddressTo',
                    'downloadNoticeAddressCc',
                    'deleteNoticeAddressTo',
                    'deleteNoticeAddressCc',
                    'credentialNoticeAddressTo',
                    'credentialNoticeAddressCc'
                ]
                pds_user_info_data_list = pds_user_select_result["query_results"]
                pds_user_info_dict = {column: data for column, data in zip(pds_user_info_column_list, pds_user_info_data_list)}

                # 04-01-01.「変数．エラー情報」に値が設定されていない場合、下記のレスポンス情報を返却する
                self.logger.info(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                return {
                    "result": True,
                    "pdsUserInfo": pds_user_info_dict
                }
            else:
                # 04-01-02.「変数．エラー情報」に値が設定されている場合、下記のレスポンス情報を返却する
                if logging.ERROR == logUtil.output_outlog(EXEC_NAME_JP, pds_user_select_error_info):
                    self.logger.error(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                else:
                    self.logger.warning(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                return {
                    "result": False,
                    "errorInfo": pds_user_select_error_info
                }

        # 例外処理（PDSExceptionクラス）：
        except PDSException as e:
            # PDSExceptionオブジェクトをエラーとしてスローする
            raise e
        # 例外処理：
        except Exception as e:
            # エラー情報をCloudWatchへログ出力する
            self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["999999"]["logMessage"], str(e), traceback.format_exc()))
            # 下記のパラメータでPDSExceptionオブジェクトを作成する
            # PDSExceptionオブジェクトをエラーとしてスローする
            raise PDSException(
                {
                    "errorCode": "999999",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
                }
            )

    def update_pds_user_key(
        self,
        pdsUserId: str,
        pdsKeyIdx: int,
        pdsKey: str,
        endDate: str,
        common_db_info: object
    ):
        """
        PDSユーザ公開鍵更新処理
        PDSユーザ公開鍵テーブルのデータを更新する
        Args:
            pdsUserId (str): PDSユーザID
            pdsKeyIdx (int): PDSユーザ公開鍵インデックス
            pdsKey (str): PDSユーザ公開鍵
            endDate (str): PDSユーザ公開鍵終了日
            common_db_info (object): 共通DB接続情報

        Raises:
            e: 例外処理
            PDSException: PDS例外処理

        Returns:
            result: 処理結果
            errorInfo: エラー情報
        """
        error_info_list = []
        EXEC_NAME_JP = "PDSユーザ公開鍵更新処理"
        try:
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_IN_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            # 01.引数検証処理（入力チェック）
            # 01-01.「引数．PDSユーザID」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(pdsUserId):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "PDSユーザID"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "PDSユーザID")
                    }
                )

            # 01-02.「引数．PDSユーザ公開鍵インデックス」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(pdsKeyIdx):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "PDSユーザ公開鍵インデックス"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "PDSユーザ公開鍵インデックス")
                    }
                )

            # 01-03.「変数．エラー情報リスト」に値が設定されている場合、エラー作成処理を実施する
            if len(error_info_list) > 0:
                # 01-03-01.下記のパラメータでPDSExceptionオブジェクトを作成する
                # 01-03-02.PDSExceptionオブジェクトをエラーとしてスローする
                raise PDSException(*error_info_list)

            # 共通DB接続情報
            common_db_connection_resource: PostgresDbUtilClass = None
            common_db_connection_resource = common_db_info["common_db_connection_resource"]
            common_db_connection = common_db_info["common_db_connection"]

            # 02.PDSユーザ公開鍵更新処理
            pds_user_key_update_result = None
            # 02-01.PDSユーザ公開鍵テーブルを更新する
            if pdsKey is not None:
                # 更新内容(引数.PDSユーザ公開鍵がNull以外の場合)
                pds_user_key_update_result = common_db_connection_resource.update(
                    common_db_connection,
                    SqlConstClass.PDS_USER_UPDATE_SQL_PDS_USER_KEY_CONDITION,
                    pdsKey,
                    pdsUserId,
                    pdsKeyIdx
                )
            elif endDate is not None:
                # 更新内容(引数.PDSユーザ公開鍵終了日がNull以外の場合)
                pds_user_key_update_result = common_db_connection_resource.update(
                    common_db_connection,
                    SqlConstClass.PDS_USER_UPDATE_SQL_END_DATE_CONDITION,
                    endDate,
                    pdsUserId,
                    pdsKeyIdx
                )

            pds_user_key_error_info = None
            # 02-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            #       postgresqlエラー処理からのレスポンスを、「変数．エラー情報」に格納する
            if not pds_user_key_update_result["result"]:
                pds_user_key_error_info = self.create_postgresql_log(
                    pds_user_key_update_result["errorObject"],
                    None,
                    None,
                    pds_user_key_update_result["stackTrace"]
                ).get("errorInfo")

            # 03.終了処理
            # 03-01.レスポンス情報を作成し、返却する
            if pds_user_key_error_info is None:
                # 03-01-01.「変数．エラー情報」に値が設定されていない場合、下記のレスポンス情報を返却する
                self.logger.info(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                return {
                    "result": True
                }
            else:
                # 03-01-02.「変数．エラー情報」に値が設定されている場合、下記のレスポンス情報を返却する
                if logging.ERROR == logUtil.output_outlog(EXEC_NAME_JP, pds_user_key_error_info):
                    self.logger.error(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                else:
                    self.logger.warning(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                return {
                    "result": False,
                    "errorInfo": pds_user_key_error_info
                }

        # 例外処理（PDSExceptionクラス）：
        except PDSException as e:
            # PDSExceptionオブジェクトをエラーとしてスローする
            raise e
        # 例外処理：
        except Exception as e:
            # エラー情報をCloudWatchへログ出力する
            self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["999999"]["logMessage"], str(e), traceback.format_exc()))
            # 下記のパラメータでPDSExceptionオブジェクトを作成する
            # PDSExceptionオブジェクトをエラーとしてスローする
            raise PDSException(
                {
                    "errorCode": "999999",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
                }
            )

    def check_pds_user_key(
        self,
        pdsUserId: str,
        pdsKeyIdx: int,
        common_db_info: object
    ):
        """
        PDSユーザ鍵存在検証処理
        PDSユーザテーブルとPDSユーザ公開鍵テーブルからデータを取得し、PDSユーザ公開鍵が存在するかを検証する
        Args:
            pdsUserId (str): PDSユーザID
            pdsKeyIdx (int): PDSユーザ公開鍵インデックス
            common_db_info (object): 共通DB接続情報

        Raises:
            e: 例外処理
            PDSException: PDS例外処理

        Returns:
            result: 処理結果
            errorInfo: エラー情報
        """
        error_info_list = []
        EXEC_NAME_JP = "PDSユーザ鍵存在検証処理"
        try:
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_IN_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            # 01.引数検証処理（入力チェック）
            # 01-01.「引数．PDSユーザID」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(pdsUserId):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "PDSユーザID"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "PDSユーザID")
                    }
                )

            # 01-02.「引数．PDSユーザ公開鍵インデックス」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(pdsKeyIdx):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "PDSユーザ公開鍵インデックス"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "PDSユーザ公開鍵インデックス")
                    }
                )

            # 01-03.「変数．エラー情報リスト」に値が設定されている場合、エラー作成処理を実施する
            if len(error_info_list) > 0:
                # 01-03-01.下記のパラメータでPDSExceptionオブジェクトを作成する
                # 01-03-02.PDSExceptionオブジェクトをエラーとしてスローする
                raise PDSException(*error_info_list)

            # 共通DB接続情報
            common_db_connection_resource: PostgresDbUtilClass = None
            common_db_connection_resource = common_db_info["common_db_connection_resource"]
            common_db_connection = common_db_info["common_db_connection"]

            # 02.PDSユーザ取得処理
            # 02-01.PDSユーザテーブルとPDSユーザ公開鍵テーブルからデータを取得し、「変数.PDSユーザ取得結果」に1レコードをタプルとして格納する
            pds_user_result = common_db_connection_resource.select_tuple_one(
                common_db_connection,
                SqlConstClass.PDS_USER_JOIN_PDS_USER_KEY_SELECT_SQL,
                pdsUserId,
                pdsUserId,
                pdsKeyIdx
            )

            pds_user_error_info = None
            if pds_user_result["result"] and pds_user_result["query_results"][0] == 1:
                # 02-02.「変数．PDSユーザ取得結果．カウント」が1の場合、「05.終了処理」に遷移する
                pass
            elif pds_user_result["result"] and pds_user_result["query_results"][0] != 1:
                # 02-03.「変数．PDSユーザ取得結果．カウント」が1以外の場合、「変数．エラー情報」にエラー情報を作成する
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["030013"]["logMessage"], "PDSユーザ、PDSユーザ公開鍵", pdsUserId))
                pds_user_error_info = {
                    "errorCode": "030013",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["030013"]["message"], "PDSユーザ、PDSユーザ公開鍵", pdsUserId)
                }
            elif not pds_user_result["result"]:
                # 02-04.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
                #       postgresqlエラー処理からのレスポンスを、「変数．エラー情報」に格納する
                pds_user_error_info = self.create_postgresql_log(
                    pds_user_result["errorObject"],
                    None,
                    None,
                    pds_user_result["stackTrace"]
                ).get("errorInfo")

            # 03.終了処理
            # 03-01.レスポンス情報を作成し、返却する
            if pds_user_error_info is None:
                # 03-01-01.「変数．エラー情報」に値が設定されていない場合、下記のレスポンス情報を返却する
                self.logger.info(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                return {
                    "result": True
                }
            else:
                # 03-01-02.「変数．エラー情報」に値が設定されている場合、下記のレスポンス情報を返却する
                if logging.ERROR == logUtil.output_outlog(EXEC_NAME_JP, pds_user_error_info):
                    self.logger.error(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                else:
                    self.logger.warning(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                return {
                    "result": False,
                    "errorInfo": pds_user_error_info
                }

        # 例外処理（PDSExceptionクラス）：
        except PDSException as e:
            # PDSExceptionオブジェクトをエラーとしてスローする
            raise e
        # 例外処理：
        except Exception as e:
            # エラー情報をCloudWatchへログ出力する
            self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["999999"]["logMessage"], str(e), traceback.format_exc()))
            # 下記のパラメータでPDSExceptionオブジェクトを作成する
            # PDSExceptionオブジェクトをエラーとしてスローする
            raise PDSException(
                {
                    "errorCode": "999999",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
                }
            )

    def search_user_profile(
        self,
        pdsUserInstanceSecretName: str,
        searchCriteria,
        objectIdList: list
    ):
        """
        個人情報検索処理
        個人情報の検索を行う
        Args:
            pdsUserInstanceSecretName (str): PDSユーザDBインスタンスシークレット名
            searchCriteria (object): 検索条件
            objectIdList (list): objectidリスト

        Raises:
            e: 例外処理
            PDSException: PDS例外処理

        Returns:
            result: 処理結果
            count: カウント
            transactionId: トランザクションID
            userId: 検索用ユーザID
            saveDate: 検索用日時
            data: 保存されたデータ
            imageHash: 保存されたバイナリデータハッシュ値
        """
        error_info_list = []
        EXEC_NAME_JP = "個人情報検索処理"
        try:
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_IN_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            # 01.引数検証処理（入力チェック）
            # 01-01.「引数．PDSユーザDBインスタンスシークレット名」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(pdsUserInstanceSecretName):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "PDSユーザDBインスタンスシークレット名"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "PDSユーザDBインスタンスシークレット名")
                    }
                )

            # 01-02.「変数．エラー情報リスト」に値が設定されている場合、エラー作成処理を実施する
            if len(error_info_list) > 0:
                # 01-02-01.下記のパラメータでPDSExceptionオブジェクトを作成する
                # 01-02-02.PDSExceptionオブジェクトをエラーとしてスローする
                raise PDSException(*error_info_list)

            # 02.PDSユーザDB接続情報取得処理
            # 02-01.以下の引数でPDSユーザDBの接続情報をAWSのSecrets Managerから取得する
            # 02-02.取得したPDSユーザDBの接続情報を、「変数．PDSユーザDB接続情報」に格納する
            # 02-03.「変数．PDSユーザDB接続情報」を利用して、PDSユーザDBに対してのコネクションを作成する
            pds_user_db_info_response = self.get_pds_user_db_info_and_connection(pdsUserInstanceSecretName)
            if not pds_user_db_info_response["result"]:
                if logging.ERROR == logUtil.output_outlog(EXEC_NAME_JP, pds_user_db_info_response["errorInfo"]):
                    self.logger.error(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                else:
                    self.logger.warning(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                return pds_user_db_info_response
            else:
                pds_user_db_connection_resource = pds_user_db_info_response["pds_user_db_connection_resource"]
                pds_user_db_connection = pds_user_db_info_response["pds_user_db_connection"]

            # 03.検索条件作成処理
            # 03-01.下記の条件で「変数．検索条件」に設定する
            select_items_list = []
            param_list = []
            # 「引数．検索条件．検索用日時From」がNull以外の場合
            if searchCriteria.get("fromDate") is not None:
                select_items_list.append(" AND t_user_profile.save_datetime >= %s")
                param_list.append(searchCriteria.get("fromDate"))

            # 「引数．検索条件．検索用日時To」がNull以外の場合
            if searchCriteria.get("toDate") is not None:
                select_items_list.append(" AND t_user_profile.save_datetime <= %s")
                param_list.append(searchCriteria.get("toDate"))

            # 「引数．検索条件．保存されたバイナリデータハッシュ値」がNull以外の場合
            if searchCriteria.get("imageHash") is not None:
                select_items_list.append(" AND t_user_profile_binary.save_image_data_hash = %s")
                param_list.append(searchCriteria.get("imageHash"))

            # 「引数．検索条件．検索用ユーザID検索文字列」がNull以外の場合
            if searchCriteria.get("userIdStr") is not None:
                # 「引数．検索条件．検索用ユーザID検索モード」が "前方一致"の場合
                if searchCriteria["userIdMatchMode"] == SystemConstClass.MATCH_MODE["PREFIX"]:
                    select_items_list.append(" AND t_user_profile.user_id LIKE %s")
                    param_list.append(searchCriteria.get("userIdStr") + '%')
                # 「引数．検索条件．検索用ユーザID検索モード」が"後方一致"の場合
                if searchCriteria["userIdMatchMode"] == SystemConstClass.MATCH_MODE["BACKWARD"]:
                    select_items_list.append(" AND t_user_profile.user_id LIKE %s")
                    param_list.append('%' + searchCriteria.get("userIdStr"))
                # 「引数．検索条件．検索用ユーザID検索モード」が"部分一致"の場合
                if searchCriteria["userIdMatchMode"] == SystemConstClass.MATCH_MODE["PARTIAL"]:
                    select_items_list.append(" AND t_user_profile.user_id LIKE %s")
                    param_list.append('%' + searchCriteria.get("userIdStr") + '%')

            # 「引数．objectidリスト」がNull以外の場合
            if len(objectIdList) > 0:
                select_items_list.append(" AND t_user_profile.save_data_mongodb_key IN %s")
                select_items_list.append(" AND t_user_profile.json_data_flg = true")
                param_list.append(tuple(objectIdList))

            # 「引数．objectid」リストがNullの場合
            if len(objectIdList) == 0:
                # Modify(t.ii)：if文と検索条件が逆になっていたので修正した。設計書は問題なし
                if searchCriteria.get("dataStr") is not None:
                    # 「引数．検索条件．保存データ検索文字列」がNull以外の場合
                    select_items_list.append(" AND t_user_profile.json_data_flg = false")
                    # 「引数．検索条件．保存データ検索モード」が "前方一致"の場合
                    if searchCriteria.get("dataMatchMode") == SystemConstClass.MATCH_MODE["PREFIX"]:
                        select_items_list.append(" AND t_user_profile.save_data LIKE %s")
                        param_list.append(searchCriteria.get("dataStr") + '%')
                    # 「引数．検索条件．保存データ検索モード」が"後方一致"の場合
                    if searchCriteria.get("dataMatchMode") == SystemConstClass.MATCH_MODE["BACKWARD"]:
                        select_items_list.append(" AND t_user_profile.save_data LIKE %s")
                        param_list.append('%' + searchCriteria.get("dataStr"))
                    # 「引数．検索条件．保存データ検索モード」が"部分一致"の場合
                    if searchCriteria.get("dataMatchMode") == SystemConstClass.MATCH_MODE["PARTIAL"]:
                        select_items_list.append(" AND t_user_profile.save_data LIKE %s")
                        param_list.append('%' + searchCriteria.get("dataStr") + '%')

            if len(select_items_list) > 0:
                select_items_sql = ''.join(select_items_list)
                sql = SqlConstClass.USER_PROFILE_SELECT_SQL + select_items_sql + ";"

            # 03.個人情報取得処理
            pds_user_error_info = None
            # 03-01.個人情報テーブルからデータを取得し、「変数．個人情報取得結果リスト」に全レコードをタプルのリストとして格納する
            pds_user_result = pds_user_db_connection_resource.select_tuple_list(
                pds_user_db_connection,
                sql,
                *param_list
            )

            # 03-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            #       postgresqlエラー処理からのレスポンスを、「変数．エラー情報」に格納する
            if not pds_user_result["result"]:
                pds_user_error_info = self.create_postgresql_log(
                    pds_user_result["errorObject"],
                    None,
                    None,
                    pds_user_result["stackTrace"]
                ).get("errorInfo")

            # 04.共通エラーチェック処理
            # 04-01.以下の引数で共通エラーチェック処理を実行する
            if pds_user_error_info is not None:
                # 04-02.例外が発生した場合、例外処理に遷移
                self.common_error_check(pds_user_error_info)

            # 05.終了処理
            # 05-01.レスポンス情報を作成し、返却する
            if pds_user_result["query_results"] == []:
                result_list = [[] for tup in range(5)]
            else:
                result_list = [list(tup) for tup in zip(*pds_user_result["query_results"])]
            # 05-01-01.「変数．エラー情報」に値が設定されていない場合、下記のレスポンス情報を返却する
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            return {
                "result": True,
                "count": pds_user_result["rowCount"],
                "transactionId": result_list[0],
                "userId": result_list[1],
                "saveDate": result_list[2],
                "data": result_list[3],
                "imageHash": result_list[4]
            }
        # 例外処理（PDSExceptionクラス）：
        except PDSException as e:
            # PDSExceptionオブジェクトをエラーとしてスローする
            raise e
        # 例外処理：
        except Exception as e:
            # エラー情報をCloudWatchへログ出力する
            self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["999999"]["logMessage"], str(e), traceback.format_exc()))
            # 下記のパラメータでPDSExceptionオブジェクトを作成する
            # PDSExceptionオブジェクトをエラーとしてスローする
            raise PDSException(
                {
                    "errorCode": "999999",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
                }
            )

    # 検索用 水野担当ファイル
    def mongodb_search(self, pdsUserInfo: dict, dataMatchMode: str, dataJsonKey: str, dataStr: str):
        """
        MongoDB検索処理

        Args:
            pdsUserInfo (dict): PDSユーザ情報
            dataMatchMode (str): 保存データ検索モード
            dataJsonKey (str): 保存データJsonキー情報
            dataStr (str): 保存データ検索文字列
        Returns:
            result: 処理結果
            objectIdList: objectIdリスト
        """
        error_info_list = []
        error_info = None
        EXEC_NAME_JP = "MongoDB検索処理"
        try:
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_IN_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            # 01.引数検証処理（入力チェック）
            # 01-01.「引数．PDSユーザ情報」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(pdsUserInfo):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "PDSユーザ情報"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "PDSユーザ情報")
                    }
                )
            # 01-02.「引数．保存データ検索モード」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(dataMatchMode):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "保存データ検索モード"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "保存データ検索モード")
                    }
                )
            # 01-03.「引数．保存データJsonキー情報」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(dataJsonKey):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "保存データJsonキー情報"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "保存データJsonキー情報")
                    }
                )
            # 01-04.「引数．保存データ検索文字列」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(dataStr):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "保存データ検索文字列"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "保存データ検索文字列")
                    }
                )
            # 01-05.「変数．エラー情報リスト」に値が設定されている場合、エラー作成処理を実施する
            if len(error_info_list) != 0:
                raise PDSException(*error_info_list)

            # 02.MongoDB接続準備処理
            # 02-01.プログラムが配置されているリージョンのAZaのMongoDBの接続情報をAWSのSecrets Managerから取得する
            # 02-01-01.AZaのMongoDB接続情報を取得する
            # 02-01-02.取得したMongoDBの接続情報を、「変数．MongoDB接続情報」に格納する
            # 02-02.「02-01」が失敗した場合、プログラムが配置されているリージョンのAZcのMongoDBの接続情報をAWSのSecrets Managerから取得する
            # 02-02-01.AZcのMongoDB接続情報を取得する
            # 02-02-02.取得したMongoDBの接続情報を、「変数．MongoDB接続情報」に格納する
            # 02-03.「変数．MongoDB接続情報」を利用して、MongoDBに対してのコネクションを作成する
            mongo_info_result = self.get_mongo_db_info_and_connection(
                pdsUserInfo["tokyo_a_mongodb_secret_name"],
                pdsUserInfo["tokyo_c_mongodb_secret_name"],
                pdsUserInfo["osaka_a_mongodb_secret_name"],
                pdsUserInfo["osaka_c_mongodb_secret_name"]
            )
            mongo_db_util: MongoDbClass = mongo_info_result["mongo_db_util"]

            # 03.MongoDB検索処理
            # 03-01.保存データテーブルからデータを取得し、「変数．保存データ取得結果リスト」に全レコードをリストとして格納する
            find_filter_result = mongo_db_util.find_filter(dataJsonKey, dataStr, dataMatchMode)
            # 03-02.処理が失敗した場合は「変数．エラー情報」を作成し、エラーログをCloudWatchにログ出力する
            if not find_filter_result["result"]:
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["992001"]["logMessage"], find_filter_result["errorCode"], find_filter_result["message"]))
                error_info = {
                    "errorCode": "992001",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["992001"]["message"], "992001")
                }

            # 04.共通エラーチェック処理
            # 04-01.以下の引数で共通エラーチェック処理を実行する
            # 04-02.例外が発生した場合、例外処理に遷移
            if error_info is not None:
                self.common_error_check(error_info)

            # 05.終了処理
            # 05-01.レスポンス情報を作成し、返却する
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            return {
                "result": True,
                "objectIdList": find_filter_result["objectIdList"]
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

    # 検索用 水野担当ファイル
    def tid_list_create_exec(self, searchCriteria: object, pdsUserInfo: dict):
        """
        tidリスト作成処理

        Args:
            searchCriteria (object): 検索条件
            pdsUserInfo (dict): PDSユーザ情報

        Returns:
            result: 処理結果
            tidList: tidリスト
        """
        error_info_list = []
        object_id_list = None
        EXEC_NAME_JP = "tidリスト作成処理"
        try:
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_IN_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            # 01.引数検証処理（入力チェック）
            # 01-01.「引数．検索条件」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(searchCriteria):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "検索条件"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "検索条件")
                    }
                )
            # 01-02.「引数．PDSユーザ情報」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(pdsUserInfo):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "PDSユーザ情報"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "PDSユーザ情報")
                    }
                )
            # 01-03.「変数．エラー情報リスト」に値が設定されている場合、エラー作成処理を実施する
            if len(error_info_list) != 0:
                raise PDSException(*error_info_list)

            # 02.MongoDB検索判定処理
            # 02-01.「引数．検索条件．保存データJsonキー情報」がNullの場合、「04.個人情報検索処理」に遷移する
            # 02-02.「引数．検索条件．保存データJsonキー情報」がNull以外の場合、「03.MongoDB検索処理」に遷移する
            if searchCriteria["dataJsonKey"] is not None:
                # 03.MongoDB検索処理
                # 03-01.MongoDB検索処理を実行
                # 03-02.レスポンスを、「変数．MongoDB検索処理実行結果」に格納する
                mongodb_search_exec_response = self.mongodb_search(pdsUserInfo, searchCriteria["dataMatchMode"], searchCriteria["dataJsonKey"], searchCriteria["dataStr"])
                object_id_list = mongodb_search_exec_response["objectIdList"]

            # 04.個人情報検索処理
            # 04-01.個人情報検索処理を実行し、「変数．個人情報検索結果」に格納する
            # 04-02.レスポンスを、「変数．個人情報検索結果」に格納する
            search_user_profile_respone = self.search_user_profile(
                pdsUserInfo["pdsUserInstanceSecretName"],
                searchCriteria,
                object_id_list
            )

            # 05. TID重複除外処理
            # 05-01.「変数．個人情報検索結果．トランザクションID」から重複するトランザクションIDを除外する
            # 05-02.重複を除外したリストを「変数．一意トランザクションIDリスト」に格納する
            tid_list = list(dict.fromkeys(search_user_profile_respone["transactionId"]))

            # 06.終了処理
            # 06-01.レスポンス情報を作成し、返却する
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            return {
                "result": True,
                "tidList": tid_list
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

    def get_common_db_info_and_connection(self):
        """
        共通DB接続準備処理

        Returns:
            dict: 処理結果
        """
        try:
            common_db_secret_info = self.get_secret_info(SystemConstClass.PDS_COMMON_DB_SECRET_INFO["SECRET_NAME"])
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
            return {
                "result": True,
                "common_db_secret_info": common_db_secret_info,
                "common_db_connection": common_db_connection,
                "common_db_connection_resource": common_db_connection_resource
            }

        except Exception as e:
            connection_error_info = self.create_postgresql_log(
                e,
                None,
                None,
                traceback.format_exc()
            ).get("errorInfo")
            return {
                "result": False,
                "errorInfo": connection_error_info
            }

    def get_pds_user_db_info_and_connection(self, rds_db_secret_name: str):
        """
        PDSユーザDB接続準備処理

        Returns:
            dict: 処理結果
        """
        try:
            pds_user_db_secret_info = self.get_secret_info(rds_db_secret_name)
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
            return {
                "result": True,
                "pds_user_db_secret_info": pds_user_db_secret_info,
                "pds_user_db_connection": pds_user_db_connection,
                "pds_user_db_connection_resource": pds_user_db_connection_resource
            }

        except Exception as e:
            connection_error_info = self.create_postgresql_log(
                e,
                None,
                None,
                traceback.format_exc()
            ).get("errorInfo")
            return {
                "result": False,
                "errorInfo": connection_error_info
            }

    def get_mongo_db_info_and_connection(
        self,
        mongo_db_secret_name_tokyo_a: str,
        mongo_db_secret_name_tokyo_c: str,
        mongo_db_secret_name_osaka_a: str,
        mongo_db_secret_name_osaka_c: str
    ):
        """
        MongoDB接続準備処理

        Args:
            mongo_db_secret_name_tokyo_a (str): MongoDBシークレット名(東京a）
            mongo_db_secret_name_tokyo_c (str): MongoDBシークレット名(東京c）
            mongo_db_secret_name_osaka_a (str): MongoDBシークレット名(大阪a）
            mongo_db_secret_name_osaka_c (str): MongoDBシークレット名(大阪c）

        Returns:
            dict: 処理結果
        """
        try:
            mongo_db_util = None
            mongo_db_secret_info_tokyo_a = None
            mongo_db_secret_info_tokyo_c = None
            mongo_db_secret_info_osaka_a = None
            mongo_db_secret_info_osaka_c = None
            try:
                if SystemConstClass.AWS_CONST["REGION"] == SystemConstClass.REGION["TOKYO"]:
                    mongo_db_secret_info_tokyo_a = self.get_secret_info(mongo_db_secret_name_tokyo_a)
                    mongo_db_secret_info = mongo_db_secret_info_tokyo_a
                    mongo_db_util = self.get_mongo_connection(mongo_db_secret_info)
                elif SystemConstClass.AWS_CONST["REGION"] == SystemConstClass.REGION["OSAKA"]:
                    mongo_db_secret_info_osaka_a = self.get_secret_info(mongo_db_secret_name_osaka_a)
                    mongo_db_secret_info = mongo_db_secret_info_osaka_a
                    mongo_db_util = self.get_mongo_connection(mongo_db_secret_info)
            except Exception:
                pass

            if mongo_db_util is None:
                try:
                    if SystemConstClass.AWS_CONST["REGION"] == SystemConstClass.REGION["TOKYO"]:
                        mongo_db_secret_info_tokyo_c = self.get_secret_info(mongo_db_secret_name_tokyo_c)
                        mongo_db_secret_info = mongo_db_secret_info_tokyo_c
                        mongo_db_util = self.get_mongo_connection(mongo_db_secret_info)
                    elif SystemConstClass.AWS_CONST["REGION"] == SystemConstClass.REGION["OSAKA"]:
                        mongo_db_secret_info_osaka_c = self.get_secret_info(mongo_db_secret_name_osaka_c)
                        mongo_db_secret_info = mongo_db_secret_info_osaka_c
                        mongo_db_util = self.get_mongo_connection(mongo_db_secret_info)
                except Exception as e:
                    raise e

            # MongoDBの状態取得
            status = mongo_db_util.get_status()
            # 接続しているMongoDBがプライマリではない場合、MongoDBの再接続
            if status["myState"] != 1:
                mongo_db_util = None
                mongo_db_secret_info = None
                check_host = ""
                for member in status["members"]:
                    if member["state"] == 1:
                        check_host = member["name"]
                        break
                if check_host != "":
                    # 東京aのプライマリチェック
                    try:
                        if mongo_db_secret_info_tokyo_a is None:
                            mongo_db_secret_info_tokyo_a = self.get_secret_info(mongo_db_secret_name_tokyo_a)
                    except Exception:
                        pass
                    try:
                        if mongo_db_secret_info_tokyo_a is not None and mongo_db_secret_info_tokyo_a["host"] == check_host:
                            mongo_db_secret_info = mongo_db_secret_info_tokyo_a
                            mongo_db_util = self.get_mongo_connection(mongo_db_secret_info_tokyo_a)
                    except Exception as e:
                        raise e

                    # 東京cのプライマリチェック
                    try:
                        if mongo_db_secret_info_tokyo_c is None:
                            mongo_db_secret_info_tokyo_c = self.get_secret_info(mongo_db_secret_name_tokyo_c)
                    except Exception:
                        pass
                    try:
                        if mongo_db_secret_info_tokyo_c is not None and mongo_db_secret_info_tokyo_c["host"] == check_host:
                            mongo_db_secret_info = mongo_db_secret_info_tokyo_c
                            mongo_db_util = self.get_mongo_connection(mongo_db_secret_info_tokyo_c)
                    except Exception as e:
                        raise e

                    # 大阪aのプライマリチェック
                    try:
                        if mongo_db_secret_info_osaka_a is None:
                            mongo_db_secret_info_osaka_a = self.get_secret_info(mongo_db_secret_name_osaka_a)
                    except Exception:
                        pass
                    try:
                        if mongo_db_secret_info_osaka_a is not None and mongo_db_secret_info_osaka_a["host"] == check_host:
                            mongo_db_secret_info = mongo_db_secret_info_osaka_a
                            mongo_db_util = self.get_mongo_connection(mongo_db_secret_info_osaka_a)
                    except Exception as e:
                        raise e

                    # 大阪cのプライマリチェック
                    try:
                        if mongo_db_secret_info_osaka_c is None:
                            mongo_db_secret_info_osaka_c = self.get_secret_info(mongo_db_secret_name_osaka_c)
                    except Exception:
                        pass
                    try:
                        if mongo_db_secret_info_osaka_c is not None and mongo_db_secret_info_osaka_c["host"] == check_host:
                            mongo_db_secret_info = mongo_db_secret_info_osaka_c
                            mongo_db_util = self.get_mongo_connection(mongo_db_secret_info_osaka_c)
                    except Exception as e:
                        raise e

                # プライマリチェックが全て失敗した場合
                if mongo_db_util is None:
                    # エラー情報をCloudWatchへログ出力する
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["992101"]["logMessage"]))
                    raise PDSException(
                        {
                            "errorCode": "999999",
                            "message": logUtil.message_build(MessageConstClass.ERRORS["992101"]["message"], "992101")
                        }
                    )

            return {
                "result": True,
                "mongo_db_secret_info": mongo_db_secret_info,
                "mongo_db_util": mongo_db_util
            }

        # 例外処理（PDSExceptionクラス）：
        except PDSException as e:
            # PDSExceptionオブジェクトをエラーとしてスローする
            raise e
        # 例外処理：
        except Exception as e:
            # エラー情報をCloudWatchへログ出力する
            self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["999999"]["logMessage"], str(e), traceback.format_exc()))
            # 下記のパラメータでPDSExceptionオブジェクトを作成する
            # PDSExceptionオブジェクトをエラーとしてスローする
            raise PDSException(
                {
                    "errorCode": "999999",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
                }
            )

    def get_mongo_connection(self, mongo_db_secret_info: dict):
        try:
            mongo_db_util = MongoDbClass(self.logger)
            mongo_db_util.connect_mongo(host=mongo_db_secret_info["host"], port=int(mongo_db_secret_info["port"]))
            mongo_db_util.connect_db("pdsuserdb")
            mongo_db_util.connect_collection("pdsuserdata")
            return mongo_db_util
        except Exception as e:
            raise e

    def transaction_delete_batch_queue_issue(
        self,
        transactionId: str,
        pdsUserId: str
    ):
        """
        個人情報削除バッチキュー発行処理

        Args:
            transactionId (str): トランザクションID
            pdsUserId (str): PDSユーザID

        """
        EXEC_NAME_JP = "個人情報削除バッチキュー発行処理"
        client = boto3.client(
            service_name="sqs"
        )
        try:
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_IN_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            error_info_list = []
            # 01.引数検証処理（入力チェック）
            # 01-01.「引数．トランザクションID」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(transactionId):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "トランザクションID"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "トランザクションID")
                    }
                )

            # 01-02.「引数．PDSユーザID」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(pdsUserId):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "PDSユーザID"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "PDSユーザID")
                    }
                )

            # 01-03.「変数．エラー情報リスト」に値が設定されている場合、エラー作成処理を実施する
            if len(error_info_list) != 0:
                # 01-03-01.下記のパラメータでPDSExceptionオブジェクトを作成する
                # 01-03-02.PDSExceptionオブジェクトをエラーとしてスローする
                raise PDSException(*error_info_list)

            # 02.個人情報削除バッチキュー発行処理
            queue_issue_error_info = None
            for result_count in range(5):
                try:
                    # 02-01.以下の引数でキュー発行するためのインスタンス情報を取得して、「変数．個人情報削除バッチキュー情報」に格納する
                    queue_info = client.get_queue_url(QueueName=SystemConstClass.SQS_QUEUE_NAME)
                    # 02-02.以下の引数で、キューにメッセージを送信する
                    message = {
                        "transactionId": transactionId,
                        "pdsUserId": pdsUserId
                    }
                    data = {
                        "MessageBody": json.dumps(message),
                        "QueueUrl": queue_info["QueueUrl"]
                    }
                    client.send_message(**data)
                    break
                except Exception:
                    if result_count == 4:
                        # 02-03.処理が失敗した場合は「変数．エラー情報」を作成し、エラーログをCloudWatchにログ出力する
                        self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990051"]["logMessage"], transactionId, pdsUserId))
                        queue_issue_error_info = {
                            "errorCode": "990051",
                            "message": logUtil.message_build(MessageConstClass.ERRORS["990051"]["message"], "990051")
                        }

            # 03.共通エラーチェック処理
            # 03-01.以下の引数で共通エラーチェック処理を実行する
            if queue_issue_error_info is not None:
                # 03-02.例外が発生した場合、例外処理に遷移
                self.common_error_check(
                    queue_issue_error_info
                )

            # 04.終了処理
            # 04-01.処理を終了する
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))

        # 例外処理（PDSExceptionクラス）：
        except PDSException as e:
            # PDSExceptionオブジェクトをエラーとしてスローする
            raise e
        # 例外処理：
        except Exception as e:
            # エラー情報をCloudWatchへログ出力する
            self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["999999"]["logMessage"], str(e), traceback.format_exc()))
            # 下記のパラメータでPDSExceptionオブジェクトを作成する
            # PDSExceptionオブジェクトをエラーとしてスローする
            raise PDSException(
                {
                    "errorCode": "999999",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
                }
            )

    def common_check_postgres_rollback(self, con, resource: PostgresDbUtilClass):
        """
        PostgreSQLロールバック処理（汎用）

        Args:
            con (object): PostgreSQLコネクション
            resource (PostgresDbUtilClass): PostgreSQL実行リソース

        """
        try:
            error_info = None
            # 01.ロールバック処理
            # 01－01.トランザクションをロールバックする
            result = resource.rollback_transaction(con)
            # 01－02.処理が失敗した場合は、以下の引数でpostgresqlエラーを実行する
            if not result["result"]:
                error_info = self.create_postgresql_log(
                    result["errorObject"],
                    None,
                    None,
                    result["stackTrace"]
                ).get("errorInfo")
            # 02.共通エラーチェック処理
            # 02-01.以下のh奇数で共通エラーチェック処理を実行する
            # 02-02.例外が発生した場合、例外処理に遷移
            if error_info is not None:
                self.common_error_check(error_info)

            # 03.終了処理
            # 03-01.処理を終了する

        except PDSException as e:
            # PDSExceptionオブジェクトをエラーとしてスローする
            raise e
        # 例外処理：
        except Exception as e:
            # エラー情報をCloudWatchへログ出力する
            self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["999999"]["logMessage"], str(e), traceback.format_exc()))
            # 下記のパラメータでPDSExceptionオブジェクトを作成する
            # PDSExceptionオブジェクトをエラーとしてスローする
            raise PDSException(
                {
                    "errorCode": "999999",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
                }
            )

    def common_check_mongo_rollback(self, mongo_db_util: MongoDbClass):
        """
        MongoDBロールバック処理（汎用）

        Args:
            mongo_db_util (MongoDbClass): MongoDB利用リソース

        """
        try:
            error_info = None
            # 01.ロールバック処理
            # 01－01.トランザクションをロールバックする
            result = mongo_db_util.rollback_transaction()
            # 01－02.処理が失敗した場合は、以下の引数でpostgresqlエラーを実行する
            if not result["result"]:
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["992001"]["logMessage"], result["errorCode"], result["message"]))
                error_info = {
                    "errorCode": "992001",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["992001"]["message"], "992001")
                }

            # 02.共通エラーチェック処理
            # 02-01.以下のh奇数で共通エラーチェック処理を実行する
            # 02-02.例外が発生した場合、例外処理に遷移
            if error_info is not None:
                self.common_error_check(error_info)

            # 03.終了処理
            # 03-01.処理を終了する

        except PDSException as e:
            # PDSExceptionオブジェクトをエラーとしてスローする
            raise e
        # 例外処理：
        except Exception as e:
            # エラー情報をCloudWatchへログ出力する
            self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["999999"]["logMessage"], str(e), traceback.format_exc()))
            # 下記のパラメータでPDSExceptionオブジェクトを作成する
            # PDSExceptionオブジェクトをエラーとしてスローする
            raise PDSException(
                {
                    "errorCode": "999999",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
                }
            )


### クラス外関数(ロガーを必要としない簡易な関数)
def get_datetime_jst():
    """
    現在時刻(JST)を取得する

    Retusns:
        datetime: 現在時刻(JST)
    """
    return datetime.utcnow() + timedelta(hours=9)


def get_str_date():
    """
    現在日付(JST)を取得する

    Retusns:
        str: 現在日付(JST)
    """
    return get_datetime_jst().strftime('%Y/%m/%d')


def get_str_date_in_X_days(x: int):
    """
    現在からX日後の日付(JST)を取得する

    Args:
        x (int): 現在からX日後

    Returns:
        str: 現在からX日後の日付(JST)
    """
    return (get_datetime_jst() + timedelta(days=x)).strftime('%Y/%m/%d')


def get_str_date_in_X_month(x: int):
    """
    現在からXか月後の日付(JST)を取得する

    Args:
        x (int): 現在からXか月後

    Returns:
        str: 現在からXか月後の日付(JST)
    """
    return (get_datetime_jst() + relativedelta(months=x)).strftime('%Y/%m/%d')


def get_str_date_in_one_years():
    """
    現在から1年後の日付(JST)を取得する

    Returns:
        str: 現在から1年後の日付(JST)
    """
    return (get_datetime_jst() + relativedelta(years=1)).strftime('%Y/%m/%d')


def get_str_datetime():
    """
    現在日時(JST)を取得する

    Returns:
        str: 現在日時(JST)
    """
    return str(get_datetime_jst()).replace("-", "/")[:23]


def get_str_datetime_in_X_days(x: int):
    """
    現在からX日後の日付(JST)を取得する

    Args:
        x (int): 現在からX日後

    Returns:
        str: 現在からX日後の日付(JST)
    """
    return str(get_datetime_jst() + relativedelta(days=x)).replace("-", "/")[:23]


def get_str_datetime_in_X_month(x: int):
    """
    現在からXか月後の日時(JST)を取得する

    Args:
        x (int): 現在からXか月後

    Returns:
        str: 現在からXか月後の日時(JST)
    """
    return str(get_datetime_jst() + relativedelta(months=x)).replace("-", "/")[:23]


def get_str_datetime_in_one_years():
    """
    現在から1年後の日付(JST)を取得する

    Returns:
        str: 現在から1年後の日付(JST)
    """
    return str(get_datetime_jst() + relativedelta(years=1)).replace("-", "/")[:23]


def get_beginning_and_end_of_the_last_month():
    """
    先月初、先月末日時を取得する

    Returns:
        str: 先月初日時
        str: 先月末日時
    """
    today = datetime.today()
    beginning_of_the_last_month = today + relativedelta(months=-1, day=1)
    end_of_the_last_month = today + relativedelta(day=1, days=-1)
    beginning_of_the_last_month = str(beginning_of_the_last_month.strftime("%Y/%m/%d")) + " " + "00:00:00.000"
    end_of_the_last_month = str(end_of_the_last_month.strftime("%Y/%m/%d")) + " " + "23:59:59.999"
    return beginning_of_the_last_month, end_of_the_last_month


def get_datetime_str_no_symbol():
    """
    現在日付文字列取得(YYYYMMDDhhmmssiii形式)

    Returns:
        str: 現在日付文字列(YYYYMMDDhhmmssiii形式)
    """
    return get_datetime_jst().strftime('%Y%m%d%H%M%S%f')[:-3]


def get_random_int(digit: int):
    """
    乱数作成

    Args:
        digit (int): 取得したい乱数の桁数(1以上の整数)

    Returns:
        int: 指定した桁の乱数
    """
    return random.randrange(10**(digit - 1), 10**digit)


def get_uuid():
    """
    UUID作成（ハイフンあり）

    Returns:
        str: UUID(ハイフンあり)
    """
    return str(uuid.uuid4())


def get_uuid_no_hypen():
    """
    UUID作成（ハイフンなし）

    Returns:
        str: UUID(ハイフンなし)
    """
    return get_uuid().replace('-', '')


def get_random_ascii(digit: int):
    """
    ランダム文字列(ascii)作成

    Args:
        digits (int): 桁数

    Returns:
        str: ランダム文字列
    """
    return ''.join(random.choices(string.ascii_letters + string.digits, k=digit))


def random_upper(target_str: str):
    """
    文字列中のランダムな英小文字を英大文字に変換する

    Args:
        target_str (str): 変換対象の文字列

    Returns:
        str: 変換後の文字列
    """
    # 文字列内のアルファベットの位置を特定
    moji_list = [m.span() for m in re.finditer('[a-z]', target_str)]
    str_list = list(target_str)
    for idx in moji_list:
        # 乱数でBool値を作成
        random_bool = bool(random.choice([True, False]))
        if random_bool:
            # 文字列内の1文字を大文字に変換
            str_list[idx[0]] = str_list[idx[0]].upper()
    return "".join(str_list)


def make_headerParam(header):
    return {
        k.decode("utf-8"): v.decode("utf-8") for (k, v) in header.raw
    }


def is_json(check_str: str):
    try:
        if type(check_str) is dict:
            result = True
        elif type(check_str) is str:
            json_obj = json.loads(check_str)
            if type(json_obj) in (dict, list):
                result = True
            else:
                result = False
        else:
            result = False
    except Exception:
        result = False
    return result
