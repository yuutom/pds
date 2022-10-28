import traceback
import requests
import json

# from requests import request
from util.commonUtil import CommonUtilClass
from util.postgresDbUtil import PostgresDbUtilClass
import util.logUtil as logUtil
import util.commonUtil as commonUtil
from const.messageConst import MessageConstClass
from const.sqlConst import SqlConstClass
from util.callbackExecutorUtil import CallbackExecutor

# Exception
from exceptionClass.PDSException import PDSException


class pdsUserPublicKeyDownloadSetBatchModelClass():

    def __init__(self, logger):
        """
        コンストラクタ

        Args:
            logger (Logger): ロガー（TRACE）
        """
        self.logger = logger
        self.common_util = CommonUtilClass(logger)
        self.error_info = None

    def main(self):
        """
        PDSユーザ公開鍵ダウンロード格納バッチ メイン処理

        """
        try:
            # 01.共通DB接続準備処理
            # 01-01.共通DB接続情報取得処理
            common_db_connection_resource: PostgresDbUtilClass = None
            # 01-01-01.AWS SecretsManagerから共通DB接続情報を取得して、「変数．共通DB接続情報」に格納する
            # 01-02.「変数．共通DB接続情報」を利用して、共通DBに対してのコネクションを作成する
            common_db_info_response = self.common_util.get_common_db_info_and_connection()
            if not common_db_info_response["result"]:
                return common_db_info_response
            else:
                common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
                common_db_connection = common_db_info_response["common_db_connection"]

            # 02.PDSユーザPDSユーザ公開鍵情報取得処理
            pds_user_public_key_info = None
            # 02-01.PDSユーザ、PDSユーザ公開鍵テーブルを結合したテーブルからデータを取得し、「変数．PDSユーザPDSユーザ公開鍵取得結果リスト」に全レコードをタプルのリストとして格納する
            pds_user_public_key_result = common_db_connection_resource.select_tuple_list(
                common_db_connection,
                SqlConstClass.PDS_USER_PDS_USER_PUBLIC_KEY_SELECT_WBT_SENDER_SQL,
                commonUtil.get_str_date()
            )
            # 02-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not pds_user_public_key_result["result"]:
                pds_user_public_key_info = self.common_util.create_postgresql_log(
                    pds_user_public_key_result["errorObject"],
                    None,
                    None,
                    pds_user_public_key_result["stackTrace"]
                ).get("errorInfo")

            # 03.共通エラーチェック処理
            # 03-01 以下の引数で共通エラーチェック処理を実行する
            # 03-02 例外が発生した場合、例外処理に遷移
            if pds_user_public_key_info is not None:
                self.common_util.common_error_check(
                    pds_user_public_key_info
                )

            # 「変数．PDSユーザPDSユーザ公開鍵取得結果リスト」の要素数分繰り返す
            # 「変数．PDSユーザ公開鍵ループ数」でループ数を管理
            for pds_user_public_key_loop, pds_user_public_key_element in enumerate(pds_user_public_key_result.get("query_results")):
                # 04.WBT送信詳細情報取得API実行処理
                mailId = pds_user_public_key_element[2]
                # wbt_get_sender_info_API_result = self.wbt_get_sender_info_API(mailId)
                # TODO(araki): WBTの送信詳細情報取得APIに置き換える
                wbt_get_sender_info_API_result = {
                    "result": True,
                    "repliedReceiverCount": 1
                }

                # 05.共通エラーチェック処理
                # 05-01.以下の引数で共通エラーチェック処理を実行する
                # 05-02.例外が発生した場合、例外処理に遷移
                if self.error_info is not None:
                    self.common_util.common_error_check(self.error_info)

                # 06.WBT送信詳細情報取得APIレスポンスチェック処理
                # 06-01.「変数．WBT送信詳細情報取得API実行結果．返信人数」が0の場合、繰り返し処理を続行する
                # 06-02.「変数．WBT送信詳細情報取得API実行結果．返信人数」が1以上の場合、「07.WBT受信一覧取得API呼び出し処理」に遷移する
                if wbt_get_sender_info_API_result.get("repliedReceiverCount") >= 1:

                    # 07.WBT受信一覧取得API実行処理
                    # wbt_receive_list_info_API_result  = self.wbt_receive_list_info_API()
                    # TODO(araki): WBTの受信一覧取得APIに置き換える
                    wbt_receive_list_info_API_result = {
                        "result": True,
                        "iwsdWebMail": [
                            {
                                "filesCount": 1,
                                "iwsdreceiver": [
                                    {
                                        "id": 19344
                                    }
                                ],
                                "title": "Reply Test"
                            },
                            {
                                "filesCount": 1,
                                "iwsdreceiver": [
                                    {
                                        "id": 19341
                                    }
                                ],
                                "title": "【VRM/PDS v2.0】TF公開鍵有効期限確認メール【b92a4c0c-4563-4825-aa53-95c7034cdd25】"
                            }
                        ]
                    }

                    if not wbt_receive_list_info_API_result["result"]:
                        self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990015"]["logMessage"]))
                        self.error_info = {
                            "errorCode": "990015",
                            "message": logUtil.message_build(MessageConstClass.ERRORS["990015"]["message"], "990015")
                        }

                    # 08.共通エラーチェック処理
                    # 08-01.以下の引数で共通エラーチェック処理を実行する
                    # 08-02.例外が発生した場合、例外処理に遷移
                    if self.error_info is not None:
                        self.common_util.common_error_check(self.error_info)

                    receiverID = None

                    for receive_info_loop, receive_info_element in enumerate(wbt_receive_list_info_API_result.get("iwsdWebMail")):
                        # 09.受信者ID取得処理
                        # 09-01.格納条件を満たすデータを「変数．受信者ID」に格納する
                        # TODO(t.ii)：TOとCCの確認の処理を追加
                        if receive_info_element["title"] == pds_user_public_key_element[3]:
                            receiverID = receive_info_element["iwsdreceiver"][0]["id"]

                    # 09-02.すべての受信者ID取得処理に失敗した場合、「変数．エラー情報」にエラー情報を作成する
                    if receiverID is None:
                        self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020004"]["logMessage"], receive_info_element["iwsdreceiver"][0]["id"]))
                        self.error_info = {
                            "errorCode": "020004",
                            "message": logUtil.message_build(MessageConstClass.ERRORS["020004"]["message"], receive_info_element["iwsdreceiver"][0]["id"])
                        }

                    # 10.共通エラーチェック処理
                    # 10-01.以下の引数で共通エラーチェック処理を実行する
                    # 10-02.例外が発生した場合、例外処理に遷移
                    if self.error_info is not None:
                        self.common_util.common_error_check(self.error_info)

                    # 11.WBT受信詳細情報取得API実行処理
                    # receiverIDを引数としてAPIを呼び出す
                    # wbt_receive_detail_info_API_result = self.wbt_receive_detail_info_API(receicerID)
                    # TODO(araki): WBTの受信詳細情報取得APIに置き換える
                    wbt_receive_detail_info_API_result = {
                        "result": True,
                        "iwsdfile": [
                            {
                                "id": 9707
                            }
                        ],
                        "filesCount": 1,
                        "iwsdreceiver": [
                            {
                                "id": 21710
                            }
                        ]
                    }

                    # 12.共通エラーチェック処理
                    # 12-01.以下の引数で共通エラーチェック処理を実行する
                    # 12-02.例外が発生した場合、例外処理に遷移
                    if self.error_info is not None:
                        self.common_util.common_error_check(self.error_info)

                    # 13.WBT受信詳細情報取得APIレスポンスチェック処理
                    # 13-01.「変数．WBT受信詳細情報取得API実行結果．受信ファイル情報」にデータが存在しない場合、繰り返し処理を続行する
                    # 13-02.「変数．WBT受信詳細情報取得API実行結果．受信ファイル情報」にデータが1以上存在する場合、「14. WBTダウンロードAPI呼び出し処理」に遷移する
                    if wbt_receive_detail_info_API_result["filesCount"] >= 1:

                        # 14.WBTダウンロードAPI実行処理
                        receiverID = wbt_receive_detail_info_API_result["iwsdreceiver"][0]["id"]
                        fileId = wbt_receive_detail_info_API_result["iwsdfile"][0]["id"]
                        # wbt_download_info_API_result = self.wbt_download_info_API(receiverID, fileId)
                        # TODO(araki): WBTのダウンロードAPIに置き換える
                        # 成功の場合、対象添付ファイルを返す
                        wbt_download_info_API_result = {
                            "pds_public_key": "test20220824"
                        }

                        # 15.共通エラーチェック処理
                        # 15-01.以下の引数で共通エラーチェック処理を実行する
                        # 15-02.例外が発生した場合、例外処理に遷移
                        if self.error_info is not None:
                            self.common_util.common_error_check(self.error_info)

                        # 16.トランザクション作成処理
                        # 16-01.「PDSユーザ公開鍵更新トランザクション」を作成する

                        # 17.PDSユーザ公開鍵テーブル更新処理
                        pds_user_public_key_update_info = None
                        # 17-01.PDSユーザ公開鍵テーブルを更新する
                        pds_user_public_key_update_result = common_db_connection_resource.update(
                            common_db_connection,
                            SqlConstClass.PDS_USER_PUBLIC_KEY_UPDATE_SQL,
                            wbt_download_info_API_result["pds_public_key"],
                            pds_user_public_key_element[0],
                            pds_user_public_key_element[1]
                        )
                        # 17-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
                        if not pds_user_public_key_update_result["result"]:
                            pds_user_public_key_update_info = self.common_util.create_postgresql_log(
                                pds_user_public_key_update_result["errorObject"],
                                None,
                                None,
                                pds_user_public_key_update_result["stackTrace"]
                            ).get("errorInfo")

                        # 18.共通エラーチェック処理
                        # 18-01 以下の引数で共通エラーチェック処理を実行する
                        # 18-02 例外が発生した場合、例外処理に遷移
                        if pds_user_public_key_update_info is not None:
                            # ロールバック処理
                            rollback_transaction = CallbackExecutor(
                                self.common_util.common_check_postgres_rollback,
                                common_db_connection,
                                common_db_connection_resource
                            )
                            self.common_util.common_error_check(
                                pds_user_public_key_update_info,
                                rollback_transaction
                            )

                        # 19.トランザクションコミット処理
                        # 19-01 「PDSユーザ公開鍵更新トランザクション」をコミットする
                        common_db_connection_resource.commit_transaction(common_db_connection)
                        common_db_connection_resource.close_connection(common_db_connection)

                        # 20.ダウンロードファイル削除処理
                        # 20-01.「変数．ダウンロードファイル」をNullにする
                        wbt_download_info_API_result = None

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

    def wbt_get_sender_info_API(self, mailId):
        try:
            # 送信詳細情報取得API実行
            try:
                # 04-01.以下の引数でWBT「送信詳細情報取得API」を呼び出し処理を実行する
                header = {"Content-Type": "application/json", "Ocp-Apim-Subscription-Key": "e7b58ee4695c4621a9de98de48b1aa38"}
                url = "http://localhost:8080/sdms/mails/outbox/" + mailId
                # 04-02.「送信詳細情報取得API」からのレスポンスを、「変数．WBT送信詳細情報取得API実行結果」に格納する
                get_result = self.get_request(url=url, headers=header)
                if get_result["result"]:
                    wbt_get_sender_info_api_result = get_result["response"].json()
                # 04-03.WebBureauTransferの処理に失敗した場合、「変数．エラー情報」にエラー情報を作成する
                else:
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990014"]["logMessage"]))
                    self.error_info = {
                        "errorCode": "990014",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["990014"]["message"], "990014")
                    }
            except Exception:
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990014"]["logMessage"]))
                self.error_info = {
                    "errorCode": "990014",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["990014"]["message"], "990014")
                }

            if self.error_info is None:
                return {
                    "result": True,
                    "repliedReceiverCount": wbt_get_sender_info_api_result["repliedReceiverCount"]
                }
            else:
                return {
                    "result": False
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

    def wbt_receive_list_info_API(self):
        try:
            # 受信一覧取得API実行
            try:
                # 07-01.引数なしでWBT「受信一覧取得API」を呼び出し処理を実行する
                header = {"Content-Type": "application/json", "Ocp-Apim-Subscription-Key": "e7b58ee4695c4621a9de98de48b1aa38"}
                request_body_data = {"sort": {"field": "id"}}
                url = "http://localhost:8080/sdms/mails/inbox"
                # 07-02.「受信一覧取得API」からのレスポンスを、「変数．WBT受信一覧取得API実行結果」に格納する
                post_result = self.post_request(url=url, data=request_body_data, headers=header)
                if post_result["result"]:
                    wbt_receive_list_info_api_result = post_result["response"].json()
                # 07-03.WebBureauTransferの処理に失敗した場合、「変数．エラー情報」にエラー情報を作成する
                else:
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990015"]["logMessage"]))
                    self.error_info = {
                        "errorCode": "990015",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["990015"]["message"], "990015")
                    }
            except Exception:
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990015"]["logMessage"]))
                self.error_info = {
                    "errorCode": "990015",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["990015"]["message"], "990015")
                }

            if self.error_info is None:
                return {
                    "result": True,
                    "repliedReceiverCount": wbt_receive_list_info_api_result["iwsdWebMail"]
                }
            else:
                return {
                    "result": False
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

    def wbt_receive_detail_info_API(self, receiverId):
        try:
            # 受信詳細情報取得API実行処理
            try:
                # 11-01.以下のパラメータでWBT「受信詳細情報取得API」を呼び出し処理を実行する
                header = {"Content-Type": "application/json", "Ocp-Apim-Subscription-Key": "e7b58ee4695c4621a9de98de48b1aa38"}
                url = "http://localhost:8080/sdms/mails/inbox/" + receiverId
                # 11-02.「受信詳細情報取得API」からのレスポンスを、「変数．WBT受信詳細情報取得API実行結果」に格納する
                get_result = self.get_request(url=url, headers=header)
                if get_result["result"]:
                    wbt_receive_detail_info_api_result = get_result["response"].json()
                # 11-03.処理が失敗した場合は「変数．エラー情報」を作成し、エラーログをCloudWatchにログ出力する
                else:
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990016"]["logMessage"]))
                    self.error_info = {
                        "errorCode": "990016",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["990016"]["message"], "990016")
                    }
            except Exception:
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990016"]["logMessage"]))
                self.error_info = {
                    "errorCode": "990016",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["990016"]["message"], "990016")
                }

            if self.error_info is None:
                return {
                    "result": True,
                    "iwsdfile": wbt_receive_detail_info_api_result["iwsdfile"],
                    "filesCount": wbt_receive_detail_info_api_result["filesCount"],
                    "iwsdreceiver": wbt_receive_detail_info_api_result["iwsdreceiver"],
                }
            else:
                return {
                    "result": False
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

    def wbt_download_info_API(self, receiverId, fileId):
        try:
            # ダウンロードAPI実行処理
            try:
                # 14-01.以下のパラメータでWBT「ダウンロードAPI」を呼び出し処理を実行する
                header = {"Content-Type": "application/json", "Ocp-Apim-Subscription-Key": "e7b58ee4695c4621a9de98de48b1aa38"}
                url = "http://localhost:8080/sdms/mails/inbox/" + receiverId + "/attachment/" + fileId
                # 14-02.「ダウンロードAPI」からのレスポンスを、「変数．ダウンロードファイル」に格納する
                get_result = self.get_request(url=url, headers=header)
                if get_result["result"]:
                    wbt_download_info_api_result = get_result["response"].json()
                # 14-03.処理が失敗した場合は「変数．エラー情報」を作成し、エラーログをCloudWatchにログ出力する
                # 14-03-01.WebBureauTransferの処理に失敗した場合、「変数．エラー情報」にエラー情報を作成する
                else:
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990017"]["logMessage"]))
                    self.error_info = {
                        "errorCode": "990017",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["990017"]["message"], "990017")
                    }
            except Exception:
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990017"]["logMessage"]))
                self.error_info = {
                    "errorCode": "990017",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["990017"]["message"], "990017")
                }

            if self.error_info is None:
                return wbt_download_info_api_result
            else:
                return {
                    "result": False
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

    def get_request(self, url: str, header: dict):
        """
        汎用GETリクエスト処理

        Args:
            url (str): リクエスト先URL
            header (dict): リクエストヘッダ

        Returns:
            response: レスポンス
        """
        try:
            # GETリクエスト
            response = requests.get(
                url=url,
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
