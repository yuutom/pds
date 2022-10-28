from datetime import timedelta
import secrets
from jose import jwt as JWT
from jose.exceptions import JWTError
from pydantic import BaseModel
from typing import Optional
from util.postgresDbUtil import PostgresDbUtilClass
import logging
from logging import Logger
import traceback

from exceptionClass.PDSException import PDSException

from const.messageConst import MessageConstClass
from const.systemConst import SystemConstClass
from const.sqlConst import SqlConstClass


import util.commonUtil as commonUtil
from util.commonUtil import CommonUtilClass
import util.logUtil as logUtil
import util.checkUtil as checkUtil

from util.commonParamCheck import checkAccessToken
from util.commonParamCheck import checkTfOperatorId
from util.commonParamCheck import checkPdsUserId


class ErrorInfo(BaseModel):
    errorCode: Optional[str]
    message: Optional[str]


class InputCheckResult(BaseModel):
    result: bool
    errorInfo: Optional[ErrorInfo]


class TokenUtilClass:
    def __init__(self, logger: Logger):
        self.logger: Logger = logger

    def create_token_closed(self, tfOperatorInfo: dict, accessToken: str):
        """
        アクセストークン発行処理（非公開用）

        Args:
            tfOperatorInfo (dict): TFオペレータ情報
            accessToken (str): アクセストークン

        Returns:
            dict: 処理結果
        """
        error_info_list = []
        EXEC_NAME_JP = "アクセストークン発行処理（非公開用）"
        try:
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_IN_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            # 01.引数検証処理（入力チェック）
            # 01-01.TFオペレータID検証処理
            # 01-01-01.以下の引数でTFオペレータID検証処理を実行する
            check_tf_operator_id_result = checkTfOperatorId.CheckTfOperatorId(self.logger, tfOperatorInfo["tfOperatorId"]).get_result()
            # 01-01-01-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not check_tf_operator_id_result["result"]:
                [error_info_list.append(error_info) for error_info in check_tf_operator_id_result["errorInfo"]]

            # 01-02.「引数．TFオペレータ情報．TFオペレータ名」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(tfOperatorInfo["tfOperatorName"]):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "TFオペレータ名"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "TFオペレータ名")
                    }
                )
            # 01-03.「引数．TFオペレータ情報．TFオペレータ名」に値が設定されており、型が文字列型ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_type(tfOperatorInfo["tfOperatorName"], str):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "TFオペレータ名", "文字列"))
                error_info_list.append(
                    {
                        "errorCode": "020019",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "TFオペレータ名", "文字列")
                    }
                )

            # 01-04.「引数．TFオペレータ情報．TFオペレータ名」に値が設定されており、値の桁数が2桁未満の場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_min_length(tfOperatorInfo["tfOperatorName"], 2):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020016"]["logMessage"], "TFオペレータ名", "2"))
                error_info_list.append(
                    {
                        "errorCode": "020016",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020016"]["message"], "TFオペレータ名", "2")
                    }
                )

            # 01-05.「引数．TFオペレータ情報．TFオペレータ名」に値が設定されており、値の桁数が12桁を超過する場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_max_length(tfOperatorInfo["tfOperatorName"], 12):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020002"]["logMessage"], "TFオペレータ名", "12"))
                error_info_list.append(
                    {
                        "errorCode": "020002",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020002"]["message"], "TFオペレータ名", "12")
                    }
                )

            # 01-06.「引数．TFオペレータ情報．TFオペレータ名」に値が設定されており、値に入力可能文字以外が含まれている場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_enterable_characters_tf_operator_name(tfOperatorInfo["tfOperatorName"]):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020020"]["logMessage"], "TFオペレータ名"))
                error_info_list.append(
                    {
                        "errorCode": "020020",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020020"]["message"], "TFオペレータ名")
                    }
                )

            # 01-07.アクセストークン検証処理
            # 01-07-01.以下の引数でアクセストークン検証処理を実行する
            check_access_token_result = checkAccessToken.CheckAccessToken(self.logger, accessToken, False).get_result()
            # 01-07-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not check_access_token_result["result"]:
                [error_info_list.append(error_info) for error_info in check_access_token_result["errorInfo"]]

            # 01-08.「変数．エラー情報リスト」に値が設定されている場合、エラー作成処理を実施する
            if len(error_info_list) != 0:
                # 01-08-01.下記のパラメータでPDSExceptionオブジェクトを作成する
                # 01-08-02.PDSExceptionオブジェクトをエラーとしてスローする
                raise PDSException(*error_info_list)

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

            # 03.TFオペレータ取得処理
            tf_operator_error_info = None
            # 03-01.TFオペレータテーブルからデータを取得し、1レコードを「変数．TFオペレータ取得結果」にタプルとして格納する
            tf_operator_info = common_db_connection_resource.select_tuple_one(
                common_db_connection,
                SqlConstClass.ACCESS_TOKEN_CLOSED_TF_OPERATOR_VERIF_SQL,
                tfOperatorInfo["tfOperatorId"],
                False
            )

            # 03-02.「変数．TFオペレータ取得結果[0]」が1件以外の場合、「変数.エラー情報」を作成する
            if tf_operator_info.get("result") and tf_operator_info["rowcount"] != 1:
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020004"]["logMessage"], 'TFオペレータ'))
                tf_operator_error_info = {
                    "errorCode": "020004",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020004"]["logMessage"], 'TFオペレータ')
                }

            # 03-03.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not tf_operator_info["result"]:
                tf_operator_error_info = common_util.create_postgresql_log(
                    tf_operator_info["errorObject"],
                    None,
                    None,
                    tf_operator_info["stackTrace"]
                ).get("errorInfo")

            # 04.TFオペレータ取得チェック処理
            # 04-01.「変数．エラー情報」が設定されていない場合、「06.JWT作成処理」に遷移する
            # 04-02.「変数．エラー情報」が設定されている場合、「05.TFオペレータ取得エラー処理」に遷移する
            if tf_operator_error_info is not None:
                # 05.TFオペレータ取得エラー処理
                # 05-01.レスポンス情報を作成し、返却する
                if logging.ERROR == logUtil.output_outlog(EXEC_NAME_JP, tf_operator_error_info):
                    self.logger.error(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                else:
                    self.logger.warning(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                return {
                    "result": False,
                    "errorInfo": tf_operator_error_info
                }

            # 06.JWT作成処理
            # 06-01.JWTの作成を行う
            # 06-01-01.UUID ( v4ハイフンなし)を作成する
            # 06-01-02.「変数．秘密鍵」に作成したUUIDを格納する
            jwt_secret = commonUtil.get_uuid_no_hypen()
            # 06-01-03.「変数．有効期限」に本日日時　＋　30分を格納する
            expires_delta = timedelta(
                minutes=SystemConstClass.ACCESS_TOKEN_CLOSED_EXPIRE_MINUTES
            )
            expire = commonUtil.get_datetime_jst() + expires_delta

            # 06-01-04.「変数．アクセストークン」に16進数の200文字のランダム文字列を格納する
            create_access_token = secrets.token_hex(100)
            # 06-01-05.「変数．ペイロード」を作成する
            to_encode = tfOperatorInfo.copy()
            to_encode.update({"tfOperatorPasswordResetFlg": tf_operator_info["query_results"][0]})
            to_encode.update({"accessToken": create_access_token})
            to_encode.update({"exp": expire})

            # 06-01-06.JWTを作成し、「変数．JWT」に格納する
            encode_jwt = JWT.encode(
                to_encode,
                jwt_secret,
                algorithm=SystemConstClass.ACCESS_TOKEN_ALGORISHMS
            )

            # 07.トランザクション作成処理
            # 07-01.「アクセストークン発行トランザクション」を作成する

            # 08.アクセストークン判定処理
            # 08-01.「引数．アクセストークン」が設定されている場合、「09.アクセストークン無効処理」に遷移する
            # 08-02.「引数．アクセストークン」が設定されていない場合、「13.アクセストークン登録処理」に遷移する
            if accessToken is not None:
                # pass
                # TODO-TEST(t.ii)：アクセストークン無効化処理停止中 FROM
                # 09.アクセストークン無効処理
                access_token_error_info = None
                # 09-01.アクセストークンテーブルを更新する
                access_token_info = common_db_connection_resource.update(
                    common_db_connection,
                    SqlConstClass.ACCESS_TOKEN_CLOSED_UPDATE_SQL,
                    tfOperatorInfo["tfOperatorId"],
                    accessToken,
                    True
                )

                # 09-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
                if not access_token_info["result"]:
                    access_token_error_info = common_util.create_postgresql_log(
                        access_token_info["errorObject"],
                        None,
                        None,
                        access_token_info["stackTrace"]
                    ).get("errorInfo")

                # 10.アクセストークン無効チェック処理
                # 10-01.「変数．エラー情報」が設定されていない場合、「13.アクセストークン登録処理」に遷移する
                # 10-02.「変数．エラー情報」が設定されている場合、「11.トランザクションロールバック処理」に遷移する
                if access_token_error_info is not None:
                    # 11.トランザクションロールバック処理
                    # 11-01.「アクセストークン発行トランザクション」をロールバックする
                    common_db_connection_resource.rollback_transaction(common_db_connection)
                    # 12.アクセストークン無効エラー処理
                    # 12-01.レスポンス情報を作成し、返却する
                    return {
                        "result": False,
                        "errorInfo": access_token_error_info
                    }
                # TODO-TEST(t.ii)：アクセストークン無効化処理停止中 TO

            # 13.アクセストークン登録処理
            access_token_insert_error_info = None
            # 13-01.アクセストークンテーブルに登録する
            access_token_insert_info = common_db_connection_resource.insert(
                common_db_connection,
                SqlConstClass.ACCESS_TOKEN_INSERT_SQL,
                create_access_token,
                tfOperatorInfo["tfOperatorId"],
                None,
                True,
                expire,
                jwt_secret
            )
            # 13-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not access_token_insert_info["result"]:
                access_token_insert_error_info = common_util.create_postgresql_log(
                    access_token_insert_info["errorObject"],
                    "アクセストークン",
                    create_access_token,
                    access_token_insert_info["stackTrace"]
                ).get("errorInfo")
            # 14.アクセストークン登録チェック処理
            # 14-01.「変数．エラー情報」が設定されていない場合、「17.トランザクションコミット処理」に遷移する
            # 14-02.「変数．エラー情報」が設定されている場合、「15.トランザクションロールバック処理」に遷移する
            if access_token_insert_error_info is not None:
                # 15.トランザクションロールバック処理
                # 15-01.「アクセストークン発行トランザクション」をロールバックする
                common_db_connection_resource.rollback_transaction(common_db_connection)
                # 16.アクセストークン登録エラー処理
                # 16-01.レスポンス情報を作成し、返却する
                if logging.ERROR == logUtil.output_outlog(EXEC_NAME_JP, access_token_insert_error_info):
                    self.logger.error(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                else:
                    self.logger.warning(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                return {
                    "result": False,
                    "errorInfo": access_token_insert_error_info
                }

            # 17.トランザクションコミット処理
            # 17-01.「アクセストークン発行トランザクション」をコミットする
            common_db_connection_resource.commit_transaction(common_db_connection)
            common_db_connection_resource.close_connection(common_db_connection)

            # 18.終了処理
            # 18-01.レスポンス情報を作成し、返却する
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            return {
                "result": True,
                "accessToken": create_access_token,
                "jwt": encode_jwt
            }

        # 例外処理(PDSException)
        except PDSException as e:
            # PDSExceptionオブジェクトをエラーとしてスローする
            raise e

        # 例外処理
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

    def create_token_public(self, pdsUserId: str, pdsUserName: str, accessToken: str):
        """
        アクセストークン発行処理（公開用）

        Args:
            pdsUserId (str): PDSユーザID
            pdsUserName (str): PDSユーザ名
            accessToken (str): アクセストークン

        Returns:
            dict: 処理結果
        """
        error_info_list = []
        EXEC_NAME_JP = "アクセストークン発行処理（公開用）"
        try:
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_IN_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            # 01.引数検証処理（入力チェック）
            # 01-01.PDSユーザID検証処理
            # 01-01-01.以下の引数でPDSユーザID検証処理を実行する
            check_pds_user_id_result = checkPdsUserId.CheckPdsUserId(self.logger, pdsUserId).get_result()
            # 01-01-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not check_pds_user_id_result["result"]:
                [error_info_list.append(error_info) for error_info in check_pds_user_id_result["errorInfo"]]

            # 01-02.「引数．PDSユーザ名」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(pdsUserName):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "PDSユーザ名"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "PDSユーザ名")
                    }
                )
            # 01-03.「引数．PDSユーザ名」に値が設定されており、型が文字列型ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_type(pdsUserName, str):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "PDSユーザ名", "文字列"))
                error_info_list.append(
                    {
                        "errorCode": "020019",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "PDSユーザ名", "文字列")
                    }
                )

            # 01-04.「引数．PDSユーザ名」に値が設定されており、値の桁数が64桁超過の場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_max_length(pdsUserName, 64):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020002"]["logMessage"], "PDSユーザ名", "64"))
                error_info_list.append(
                    {
                        "errorCode": "020002",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020002"]["message"], "PDSユーザ名", "64")
                    }
                )

            # 01-05.「引数．PDSユーザ名」に値が設定されており、値に入力可能文字以外が含まれている場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_enterable_characters_general_purpose_characters(pdsUserName):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020020"]["logMessage"], "PDSユーザ名"))
                error_info_list.append(
                    {
                        "errorCode": "020020",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020020"]["message"], "PDSユーザ名")
                    }
                )

            # 01-06.アクセストークン検証処理
            # 01-06-01.以下の引数でアクセストークン検証処理を実行する
            check_access_token_result = checkAccessToken.CheckAccessToken(self.logger, accessToken, False).get_result()
            # 01-06-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not check_access_token_result["result"]:
                [error_info_list.append(error_info) for error_info in check_access_token_result["errorInfo"]]

            # 01-07.「変数．エラー情報リスト」に値が設定されている場合、エラー作成処理を実施する
            if len(error_info_list) != 0:
                # 01-07-01.下記のパラメータでPDSExceptionオブジェクトを作成する
                # 01-07-02.PDSExceptionオブジェクトをエラーとしてスローする
                raise PDSException(*error_info_list)

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

            # 03.PDSユーザ取得処理
            pds_user_error_info = None
            # 03-01.PDSユーザテーブルからデータを取得し、「変数．PDSユーザ取得結果」に1レコードをタプルとして格納する
            pds_user_info = common_db_connection_resource.select_tuple_one(
                common_db_connection,
                SqlConstClass.ACCESS_TOKEN_PUBLIC_PDS_USER_TOKEN_ISSUANCE_SQL,
                pdsUserId,
                pdsUserName,
                True
            )

            # 03-02.「変数．PDSユーザ取得結果」の件数が1以外の場合、「変数.エラー情報」を作成する
            if pds_user_info.get("result") and pds_user_info["rowcount"] != 1:
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020004"]["logMessage"], pdsUserId))
                pds_user_error_info = {
                    "errorCode": "020004",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020004"]["logMessage"], pdsUserId)
                }

            # 03-03.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not pds_user_info["result"]:
                pds_user_error_info = common_util.create_postgresql_log(
                    pds_user_info["errorObject"],
                    None,
                    None,
                    pds_user_info["stackTrace"]
                ).get("errorInfo")

            # 04.PDSユーザ取得チェック処理
            # 04-01.「変数．エラー情報」が設定されていない場合、「06.JWT作成処理」に遷移する
            # 04-02.「変数．エラー情報」が設定されている場合、「05.PDSユーザ取得エラー処理」に遷移する
            if pds_user_error_info is not None:
                # 05.PDSユーザ取得エラー処理
                # 05-01.レスポンス情報を作成し、返却する
                if logging.ERROR == logUtil.output_outlog(EXEC_NAME_JP, pds_user_error_info):
                    self.logger.error(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                else:
                    self.logger.warning(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                return {
                    "result": False,
                    "errorInfo": pds_user_error_info
                }

            # 06.JWT作成処理
            # 06-01.JWTの作成を行う
            # 06-01-01.UUID ( v4ハイフンなし)を作成する
            # 06-01-02.「変数．秘密鍵」に作成したUUIDを格納する
            jwt_secret = commonUtil.get_uuid_no_hypen()
            # 06-01-03.「変数．有効期限」に現在日時　＋　1分を格納する
            expires_delta = timedelta(
                minutes=SystemConstClass.ACCESS_TOKEN_PUBLIC_EXPIRE_MINUTES
            )
            expire = commonUtil.get_datetime_jst() + expires_delta

            # 06-01-04.「変数．アクセストークン」に16進数の200文字のランダム文字列を格納する
            create_access_token = secrets.token_hex(100)
            # 06-01-05.「変数．ペイロード」を作成する
            to_encode = {}
            to_encode.update({"pdsUserId": pdsUserId})
            to_encode.update({"pdsUserName": pdsUserName})
            to_encode.update({"accessToken": create_access_token})
            to_encode.update({"exp": expire})

            # 06-01-06.JWTを作成し、「変数．JWT」に格納する
            encode_jwt = JWT.encode(
                to_encode,
                jwt_secret,
                algorithm=SystemConstClass.ACCESS_TOKEN_ALGORISHMS
            )

            # 07.トランザクション作成処理
            # 07-01.「アクセストークン発行トランザクション」を作成する

            # 08.アクセストークン判定処理
            # 08-01.「引数．アクセストークン」が設定されている場合、「09.アクセストークン無効処理」に遷移する
            # 08-02.「引数．アクセストークン」が設定されていない場合、「13.アクセストークン登録処理」に遷移する
            if accessToken is not None:
                # pass
                # TODO-TEST(t.ii)：アクセストークン無効化処理停止中 From
                # 09.アクセストークン無効処理
                access_token_error_info = None
                # 09-01.アクセストークンテーブルを更新する
                access_token_info = common_db_connection_resource.update(
                    common_db_connection,
                    SqlConstClass.ACCESS_TOKEN_PUBLIC_UPDATE_SQL,
                    pdsUserId,
                    accessToken,
                    True
                )

                # 09-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
                if not access_token_info["result"]:
                    access_token_error_info = common_util.create_postgresql_log(
                        access_token_info["errorObject"],
                        None,
                        None,
                        access_token_info["stackTrace"]
                    ).get("errorInfo")

                # 10.アクセストークン無効チェック処理
                # 10-01.「変数．エラー情報」が設定されていない場合、「13.アクセストークン登録処理」に遷移する
                # 10-02.「変数．エラー情報」が設定されている場合、「11.トランザクションロールバック処理」に遷移する
                if access_token_error_info is not None:
                    # 11.トランザクションロールバック処理
                    # 11-01.「アクセストークン発行トランザクション」をロールバックする
                    common_db_connection_resource.rollback_transaction(common_db_connection)
                    # 12.アクセストークン無効エラー処理
                    # 12-01.レスポンス情報を作成し、返却する
                    if logging.ERROR == logUtil.output_outlog(EXEC_NAME_JP, access_token_error_info):
                        self.logger.error(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                    else:
                        self.logger.warning(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                    return {
                        "result": False,
                        "errorInfo": access_token_error_info
                    }
                # TODO-TEST(t.ii)：アクセストークン無効化処理停止中 TO

            # 13.アクセストークン登録処理
            access_token_insert_error_info = None
            # 13-01.アクセストークンテーブルに登録する
            access_token_insert_info = common_db_connection_resource.insert(
                common_db_connection,
                SqlConstClass.ACCESS_TOKEN_INSERT_SQL,
                create_access_token,
                None,
                pdsUserId,
                True,
                expire,
                jwt_secret
            )
            # 13-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not access_token_insert_info["result"]:
                access_token_insert_error_info = common_util.create_postgresql_log(
                    access_token_insert_info["errorObject"],
                    "アクセストークン",
                    create_access_token,
                    access_token_insert_info["stackTrace"]
                ).get("errorInfo")
            # 14.アクセストークン登録チェック処理
            # 14-01.「変数．エラー情報」が設定されていない場合、「17.トランザクションコミット処理」に遷移する
            # 14-02.「変数．エラー情報」が設定されている場合、「15.トランザクションロールバック処理」に遷移する
            if access_token_insert_error_info is not None:
                # 15.トランザクションロールバック処理
                # 15-01.「アクセストークン発行トランザクション」をロールバックする
                common_db_connection_resource.rollback_transaction(common_db_connection)
                # 16.アクセストークン登録エラー処理
                # 16-01.レスポンス情報を作成し、返却する
                if logging.ERROR == logUtil.output_outlog(EXEC_NAME_JP, access_token_insert_error_info):
                    self.logger.error(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                else:
                    self.logger.warning(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                return {
                    "result": False,
                    "errorInfo": access_token_insert_error_info
                }

            # 17.トランザクションコミット処理
            # 17-01.「アクセストークン発行トランザクション」をコミットする
            common_db_connection_resource.commit_transaction(common_db_connection)
            common_db_connection_resource.close_connection(common_db_connection)

            # 18.終了処理
            # 18-01.レスポンス情報を作成し、返却する
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            return {
                "result": True,
                "accessToken": create_access_token,
                "jwt": encode_jwt
            }

        # 例外処理(PDSException)
        except PDSException as e:
            # PDSExceptionオブジェクトをエラーとしてスローする
            raise e

        # 例外処理
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

    def verify_token_closed(self, accessToken: str, jwt: str):
        """
        アクセストークン検証処理（非公開用）

        Args:
            accessToken (str): アクセストークン
            jwt (str): JWT

        Returns:
            dict: 処理結果
        """
        error_info_list = []
        EXEC_NAME_JP = "アクセストークン検証処理（非公開用）"
        try:
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_IN_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            # 01.引数検証処理（入力チェック）
            # 01-01.アクセストークン検証処理
            # 01-01-01.以下の引数でアクセストークン検証処理を実行する
            check_access_token_result = checkAccessToken.CheckAccessToken(self.logger, accessToken).get_result()
            # 01-01-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not check_access_token_result["result"]:
                [error_info_list.append(error_info) for error_info in check_access_token_result["errorInfo"]]

            # 01-02.「引数．JWT」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(jwt):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "JWT"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "JWT")
                    }
                )
            # 01-03.「引数．JWT」に値が設定されており、型が文字列型ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_type(jwt, str):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "JWT", "文字列"))
                error_info_list.append(
                    {
                        "errorCode": "020019",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "JWT", "文字列")
                    }
                )

            # 01-04.「変数．エラー情報リスト」に値が設定されている場合、エラー作成処理を実施する
            if len(error_info_list) != 0:
                raise PDSException(*error_info_list)

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

            # 03.アクセストークン取得処理
            access_token_info = {}
            access_token_error_info = None
            try:
                # 03-01.アクセストークンテーブルからデータを取得し、1レコードを「変数．アクセストークン取得結果」にタプルとして格納する
                access_token_info = common_db_connection_resource.select_tuple_one(
                    common_db_connection,
                    SqlConstClass.ACCESS_TOKEN_CLOSED_SELECT_SQL,
                    accessToken,
                    commonUtil.get_datetime_jst()
                )
                # 03-02.「変数．アクセストークン取得結果[0]」が0の場合、「変数.エラー情報」を作成する
                if access_token_info["result"] and access_token_info["rowcount"] != 1:
                    self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["010004"]["logMessage"]))
                    access_token_error_info = {
                        "errorCode": "010004",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["010004"]["message"])
                    }

                # 03-03.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
                elif not access_token_info["result"]:
                    access_token_error_info = common_util.create_postgresql_log(
                        access_token_info["errorObject"],
                        None,
                        None,
                        access_token_info["stackTrace"]
                    ).get("errorInfo")

            except Exception as e:
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["999999"]["logMessage"], str(e), traceback.format_exc()))
                access_token_error_info = {
                    "errorCode": "999999",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["logMessage"], "999999")
                }

            # 04.アクセストークン取得チェック処理
            # 04-01.「変数．エラー情報」が設定されていない場合、「06.JWT検証処理」に遷移する
            # 04-02.「変数．エラー情報」が設定されている場合、「05.アクセストークン取得エラー処理」に遷移する
            if access_token_error_info is not None:
                # 05.アクセストークン取得エラー処理
                # 05-01.レスポンス情報を作成し、返却する
                if logging.ERROR == logUtil.output_outlog(EXEC_NAME_JP, access_token_error_info):
                    self.logger.error(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                else:
                    self.logger.warning(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                return {
                    "result": False,
                    "errorInfo": {
                        "errorCode": access_token_error_info["errorCode"],
                        "message": access_token_error_info["message"]
                    }
                }

            # 06.JWT検証処理
            jwt_verify_error = None
            payload_tf_operator_id: str = ""
            payload_tf_operator_name: str = ""
            payload_access_token: str = ""
            try:
                # 06-01.JWTの検証を行う
                # 06-01-01.JWT検証
                payload = JWT.decode(
                    jwt,
                    access_token_info["query_results"][0],
                    algorithms=SystemConstClass.ACCESS_TOKEN_ALGORISHMS,
                    options={"leeway": -32400}
                )
                # 06-01-02.JWT検証結果のレスポンスを、「変数．JWT検証結果」に格納する
                payload_tf_operator_id = payload.get("tfOperatorId")
                payload_tf_operator_name = payload.get("tfOperatorName")
                payload_access_token = payload.get("accessToken")

                # 06-02.「変数．JWT検証結果．アクセストークン」と、「引数．アクセストークン」が一致しなかった場合、「変数．エラー情報」にエラー情報を格納する
                if not payload_access_token == accessToken:
                    self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["010007"]["logMessage"]))
                    jwt_verify_error = {
                        "errorCode": "010007",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["010007"]["message"])
                    }

                # 06-03.「変数．JWT検証結果．TFオペレーターID」と、「変数．アクセストークン取得結果[1]」が一致しなかった場合、「変数．エラー情報」にエラー情報を格納する
                if not payload_tf_operator_id == access_token_info["query_results"][1]:
                    self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["010007"]["logMessage"]))
                    jwt_verify_error = {
                        "errorCode": "010007",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["010007"]["message"])
                    }

            # 06-03.JWTの検証でエラーが発生した場合、「変数．エラー情報」にエラー情報を格納する
            except JWTError:
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["010007"]["logMessage"]))
                jwt_verify_error = {
                    "errorCode": "010007",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["010007"]["message"])
                }

            # 07.JWT検証チェック処理
            # 07-01.「変数．エラー情報」が設定されていない場合、「09.終了処理」に遷移する
            # 07-02.「変数．エラー情報」が設定されている場合、「08.JWT検証エラー処理」に遷移する
            if jwt_verify_error is not None:
                # 08.JWT検証エラー処理
                # 08-01.レスポンス情報を作成し、返却する
                if logging.ERROR == logUtil.output_outlog(EXEC_NAME_JP, jwt_verify_error):
                    self.logger.error(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                else:
                    self.logger.warning(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                return {
                    "result": False,
                    "errorInfo": jwt_verify_error
                }

            # 09.終了処理
            # 09-01.レスポンス情報を作成し、返却する
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            return {
                "result": True,
                "payload": {
                    "tfOperatorId": payload_tf_operator_id,
                    "tfOperatorName": payload_tf_operator_name,
                    "accessToken": payload_access_token
                }
            }

        # 例外処理(PDSException)
        except PDSException as e:
            # PDSExceptionオブジェクトをエラーとしてスローする
            raise e

        # 例外処理
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

    def verify_token_public(self, accessToken: str, jwt: str, pdsUserId: str):
        """
        アクセストークン検証処理（公開用）

        Args:
            accessToken (str): アクセストークン
            jwt (str): JWT
            pdsUserId (str): PDSユーザID

        Returns:
            dict: 処理結果
        """
        error_info_list = []
        EXEC_NAME_JP = "アクセストークン検証処理（公開用）"
        try:
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_IN_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            # 01.引数検証処理（入力チェック）
            # 01-01.アクセストークン検証処理
            # 01-01-01.以下の引数でアクセストークン検証処理を実行する
            check_access_token_result = checkAccessToken.CheckAccessToken(self.logger, accessToken).get_result()
            # 01-01-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not check_access_token_result["result"]:
                [error_info_list.append(error_info) for error_info in check_access_token_result["errorInfo"]]

            # 01-02.「引数．JWT」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(jwt):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "JWT"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "JWT")
                    }
                )
            # 01-03.「引数．JWT」に値が設定されており、型が文字列型ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_type(jwt, str):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "JWT", "文字列"))
                error_info_list.append(
                    {
                        "errorCode": "020019",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "JWT", "文字列")
                    }
                )
            # 01-04.PDSユーザID検証処理
            # 01-04-01.以下の引数でPDSユーザID検証処理を実行する
            check_pds_user_id_result = checkPdsUserId.CheckPdsUserId(self.logger, pdsUserId).get_result()
            # 01-04-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not check_pds_user_id_result["result"]:
                [error_info_list.append(error_info) for error_info in check_pds_user_id_result["errorInfo"]]
            # 01-05.「変数．エラー情報リスト」に値が設定されている場合、エラー作成処理を実施する
            if len(error_info_list) != 0:
                # 01-05-01.下記のパラメータでPDSExceptionオブジェクトを作成する
                # 01-05-02.PDSExceptionオブジェクトをエラーとしてスローする
                raise PDSException(*error_info_list)

            # 02.共通DB接続準備処理
            # 02-01.共通DB接続情報取得処理
            common_util = CommonUtilClass(self.logger)
            common_db_connection_resource: PostgresDbUtilClass = None
            # 02-01-01.AWS SecretsManagerから共通DB接続情報を取得して、「変数．共通DB接続情報」に格納する
            # 02-02.「変数．共通DB接続情報」を利用して、共通DBに対してのコネクションを作成する
            common_db_info_response = common_util.get_common_db_info_and_connection()
            if not common_db_info_response["result"]:
                return common_db_info_response
            else:
                common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
                common_db_connection = common_db_info_response["common_db_connection"]

            # 03.アクセストークン取得処理
            access_token_info = None
            access_token_error_info = None
            # 03-01.アクセストークンテーブルからデータを取得し、1レコードを「変数．アクセストークン取得結果」にタプルとして格納する
            access_token_info = common_db_connection_resource.select_tuple_one(
                common_db_connection,
                SqlConstClass.ACCESS_TOKEN_PUBLIC_SELECT_SQL,
                accessToken,
                pdsUserId,
                commonUtil.get_datetime_jst(),
                True
            )
            # 03-02.「変数．アクセストークン取得結果」の件数が1以外の場合、「変数.エラー情報」を作成する
            if access_token_info["result"] and access_token_info["rowcount"] != 1:
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["010004"]["logMessage"]))
                access_token_error_info = {
                    "errorCode": "010004",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["010004"]["message"])
                }

            # 03-03.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            elif not access_token_info["result"]:
                access_token_error_info = common_util.create_postgresql_log(
                    access_token_info["errorObject"],
                    None,
                    None,
                    access_token_info["stackTrace"]
                ).get("errorInfo")

            # 04.アクセストークン取得チェック処理
            # 04-01.「変数．エラー情報」が設定されていない場合、「06.JWT検証処理」に遷移する
            # 04-02.「変数．エラー情報」が設定されている場合、「05.アクセストークン取得エラー処理」に遷移する
            if access_token_error_info is not None:
                # 05.アクセストークン取得エラー処理
                # 05-01.レスポンス情報を作成し、返却する
                if logging.ERROR == logUtil.output_outlog(EXEC_NAME_JP, access_token_error_info):
                    self.logger.error(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                else:
                    self.logger.warning(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                return {
                    "result": False,
                    "errorInfo": {
                        "errorCode": access_token_error_info["errorCode"],
                        "message": access_token_error_info["message"]
                    }
                }

            # 06.JWT検証処理
            jwt_verify_error = None
            payload_pds_user_id: str = ""
            payload_pds_user_name: str = ""
            payload_access_token: str = ""
            try:
                # 06-01.JWTの検証を行う
                # 06-01-01.JWT検証
                payload = JWT.decode(
                    jwt,
                    access_token_info["query_results"][0],
                    algorithms=SystemConstClass.ACCESS_TOKEN_ALGORISHMS,
                    options={"leeway": -32400}
                )
                # 06-01-02.JWT検証結果のレスポンスを、「変数．JWT検証結果」に格納する
                payload_pds_user_id = payload.get("pdsUserId")
                payload_pds_user_name = payload.get("pdsUserName")
                payload_access_token = payload.get("accessToken")
                # 06-02.「変数．JWT検証結果．アクセストークン」と、「引数．アクセストークン」が一致しなかった場合、「変数．エラー情報」にエラー情報を格納する
                if not payload_access_token == accessToken:
                    self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["010007"]["logMessage"]))
                    jwt_verify_error = {
                        "errorCode": "010007",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["010007"]["message"])
                    }

            # 06-03.JWTの検証でエラーが発生した場合、「変数．エラー情報」にエラー情報を格納する
            except JWTError:
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["010007"]["logMessage"]))
                jwt_verify_error = {
                    "errorCode": "010007",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["010007"]["message"])
                }

            # 07.JWT検証チェック処理
            # 07-01.「変数．エラー情報」が設定されていない場合、「09.終了処理」に遷移する
            # 07-02.「変数．エラー情報」が設定されている場合、「08.JWT検証エラー処理」に遷移する
            if jwt_verify_error is not None:
                # 08.JWT検証エラー処理
                # 08-01.レスポンス情報を作成し、返却する
                if logging.ERROR == logUtil.output_outlog(EXEC_NAME_JP, jwt_verify_error):
                    self.logger.error(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                else:
                    self.logger.warning(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                return {
                    "result": False,
                    "errorInfo": jwt_verify_error
                }

            # 09.終了処理
            # 09-01.レスポンス情報を作成し、返却する
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            return {
                "result": True,
                "payload": {
                    "pdsUserId": payload_pds_user_id,
                    "pdsUserName": payload_pds_user_name,
                    "accessToken": payload_access_token
                }
            }

        # 例外処理(PDSException)
        except PDSException as e:
            # PDSExceptionオブジェクトをエラーとしてスローする
            raise e

        # 例外処理
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
