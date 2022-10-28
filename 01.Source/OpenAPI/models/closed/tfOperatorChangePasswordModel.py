import traceback
from typing import Any, Optional

# RequestBody
from pydantic import BaseModel
from util.callbackExecutorUtil import CallbackExecutor
from util.cryptoUtil import CryptUtilClass

from util.commonUtil import CommonUtilClass
from util.postgresDbUtil import PostgresDbUtilClass
import util.commonUtil as commonUtil
import util.logUtil as logUtil
from const.messageConst import MessageConstClass
from const.sqlConst import SqlConstClass

# Exception
from exceptionClass.PDSException import PDSException


class requestBody(BaseModel):
    """
    リクエストボディクラス

    Args:
        BaseModel (Object): Pydanticのベースクラス
    """
    tfOperatorPassword: Optional[Any] = None
    tfOperatorConfirmPassword: Optional[Any] = None


class tfOperatorChangePasswordClass():
    def __init__(self, logger):
        """
        コンストラクタ

        Args:
            logger (Logger): ロガー（TRACE）
        """
        self.logger = logger
        self.common_util = CommonUtilClass(logger)

    def main(self, request_body: requestBody, tfOperatorId: Any):
        """
            TFオペレータパスワード変更API メイン処理

        Args:
            request_body (requestBody): リクエストボディ
            tfOperatorId (str): TFオペレータID

        Raises:
            e: 例外処理
            PDSException: PDS例外処理

        Returns:
            dict: 処理結果
        """
        try:
            # 05.パスワードのハッシュ化処理
            # 05-01.「リクエストのリクエストボディ.パスワード」をハッシュ化してハッシュ化済パスワードを作成する
            #        ハッシュ化済パスワードを「変数.変更後パスワード」に格納する
            util = CryptUtilClass(self.logger)
            hash_password = util.hash_password(request_body.tfOperatorPassword)

            # 06.共通DB接続準備処理
            # 06-01.AWS SecretsManagerから共通DB接続情報を取得して、「変数．共通DB接続情報」に格納する
            common_util = CommonUtilClass(self.logger)
            common_db_connection_resource: PostgresDbUtilClass = None
            # 06-02.「変数．共通DB接続情報」を利用して、共通DBに対してのコネクションを作成する
            common_db_info_response = common_util.get_common_db_info_and_connection()
            if not common_db_info_response["result"]:
                return common_db_info_response
            else:
                common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
                common_db_connection = common_db_info_response["common_db_connection"]

            # 07.TFオペレータ取得処理
            tf_operator_change_password_error_info = None
            # 07-01.TFオペレータテーブルからデータを取得し、「変数．TFオペレータ取得結果」に1レコードをタプルとして格納する
            tf_operator_select_result = common_db_connection_resource.select_tuple_one(
                common_db_connection,
                SqlConstClass.TF_OPERATOR_CHANGE_PASSWORD_SELECT_SQL,
                tfOperatorId
            )

            # 07-02.「変数.TFオペレータ取得結果["rowcount"]」が1以外の場合、「変数.エラー情報」を作成する
            if tf_operator_select_result["result"] and tf_operator_select_result["rowcount"] != 1:
                tf_operator_change_password_error_info = {
                    "errorCode": "020004",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020004"]["message"], tfOperatorId)
                }
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["020004"]["logMessage"], tfOperatorId))

            # 07-03.「変数.TFオペレータ取得結果[8]」がtrueの場合、「変数.エラー情報」を作成する
            elif tf_operator_select_result["result"] and tf_operator_select_result["query_results"][8]:
                tf_operator_change_password_error_info = {
                    "errorCode": "030009",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["030009"]["message"])
                }
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["030009"]["logMessage"]))

            # 07-04.処理が失敗した場合は「変数．エラー情報」を作成し、エラーログをCloudWatchにログ出力する
            if not tf_operator_select_result["result"]:
                tf_operator_change_password_error_info = self.common_util.create_postgresql_log(
                    tf_operator_select_result["errorObject"],
                    None,
                    None,
                    tf_operator_select_result["stackTrace"]
                ).get("errorInfo")

            # 08.共通エラーチェック処理
            # 08-01.以下の引数で共通エラーチェック処理を実行する
            # 08-02.例外が発生した場合、例外処理に遷移
            if tf_operator_change_password_error_info is not None:
                self.common_util.common_error_check(tf_operator_change_password_error_info)

            # 09.TFオペレータ情報整合性チェック処理
            # 09-01.「変数.TFオペレータ取得結果」で取得した情報と「変数.変更後パスワード」の世代チェックを実施する
            # 09-01-01.「変数.TFオペレータ取得結果[1]」と「変数.変更後パスワード」が一致する場合、「変数．エラー情報」にエラー情報を作成する
            if self.chacktfOperatorValid(hash_password, tf_operator_select_result["query_results"][1]):
                tf_operator_change_password_error_info = {
                    "errorCode": "030014",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["030014"]["message"])
                }
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["030014"]["logMessage"]))

            # 09-01-02.「変数.TFオペレータ取得結果[2]」と「変数.変更後パスワード」が一致する場合、「変数．エラー情報」にエラー情報を作成する
            if self.chacktfOperatorValid(hash_password, tf_operator_select_result["query_results"][2]):
                tf_operator_change_password_error_info = {
                    "errorCode": "030014",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["030014"]["message"])
                }
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["030014"]["logMessage"]))

            # 09-01-03.「変数.TFオペレータ取得結果[3]」と「変数.変更後パスワード」が一致する場合、「変数．エラー情報」にエラー情報を作成する
            if self.chacktfOperatorValid(hash_password, tf_operator_select_result["query_results"][3]):
                tf_operator_change_password_error_info = {
                    "errorCode": "030014",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["030014"]["message"])
                }
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["030014"]["logMessage"]))

            # 09-01-04.「変数.TFオペレータ取得結果[4]」と「変数.変更後パスワード」が一致する場合、「変数．エラー情報」にエラー情報を作成する
            if self.chacktfOperatorValid(hash_password, tf_operator_select_result["query_results"][4]):
                tf_operator_change_password_error_info = {
                    "errorCode": "030014",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["030014"]["message"])
                }
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["030014"]["logMessage"]))

            # 09-01-05.「変数.TFオペレータ取得結果[5]」と「変数.変更後パスワード」が一致する場合、「変数．エラー情報」にエラー情報を作成する
            if self.chacktfOperatorValid(hash_password, tf_operator_select_result["query_results"][5]):
                tf_operator_change_password_error_info = {
                    "errorCode": "030014",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["030014"]["message"])
                }
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["030014"]["logMessage"]))

            # 10.共通エラーチェック処理
            # 10-01.以下の引数で共通エラーチェック処理を実行する
            # 10-02.例外が発生した場合、例外処理に遷移
            if tf_operator_change_password_error_info is not None:
                self.common_util.common_error_check(tf_operator_change_password_error_info)

            # 11.トランザクション作成処理
            # 11-01.「TFオペレータ更新トランザクション」を作成する

            # 12.TFオペレータ更新処理
            # 12-01.TFオペレータテーブルを更新する
            tf_operator_update_result = common_db_connection_resource.update(
                common_db_connection,
                SqlConstClass.TF_OPERATOR_CHANGE_PASSWORD_UPDATE_SQL,
                hash_password,
                tf_operator_select_result["query_results"][1],
                tf_operator_select_result["query_results"][2],
                tf_operator_select_result["query_results"][3],
                tf_operator_select_result["query_results"][4],
                commonUtil.get_str_date_in_X_month(3),
                tfOperatorId
            )

            # 12-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not tf_operator_update_result["result"]:
                tf_operator_change_password_error_info = self.common_util.create_postgresql_log(
                    tf_operator_update_result["errorObject"],
                    None,
                    None,
                    tf_operator_update_result["stackTrace"]
                ).get("errorInfo")

            # 13.共通エラーチェック処理
            # 13-01.以下の引数で共通エラーチェック処理を実行する
            # 13-02.例外が発生した場合、例外処理に遷移
            if tf_operator_change_password_error_info is not None:
                rollback_transaction = CallbackExecutor(
                    self.common_util.common_check_postgres_rollback,
                    common_db_connection,
                    common_db_connection_resource
                )
                self.common_util.common_error_check(
                    tf_operator_change_password_error_info,
                    rollback_transaction
                )

            # 14.トランザクションコミット処理
            # 14-01.「TFオペレータ更新トランザクション」をコミットする
            common_db_connection_resource.commit_transaction(common_db_connection)
            common_db_connection_resource.close_connection(common_db_connection)

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

    def chacktfOperatorValid(self, check_str1: str, check_str2: str):
        """
            比較元文字列が比較対象文字列と同一か判定
            True:同一の場合、False:違う場合
        Args:
            check_str1 (str): 比較元文字列
            check_str2 (str): 比較対象文字列

        Returns:
            bool: 判定結果
        """
        return check_str1 == check_str2
