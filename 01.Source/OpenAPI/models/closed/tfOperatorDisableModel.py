import traceback
# RequestBody
from pydantic import BaseModel
from typing import Optional

# Const
from const.messageConst import MessageConstClass
from const.sqlConst import SqlConstClass

# Util
import util.logUtil as logUtil
from util.commonUtil import CommonUtilClass
from util.postgresDbUtil import PostgresDbUtilClass
from util.callbackExecutorUtil import CallbackExecutor

# Exception
from exceptionClass.PDSException import PDSException


class requestBody(BaseModel):
    """
    リクエストボディクラス

    Args:
        BaseModel (Object): Pydanticのベースクラス
    """
    tfOperatorId: Optional[str] = None


class tfOperatorDisableModelClass():

    def __init__(self, logger):
        """
        コンストラクタ

        Args:
            logger (Logger): ロガー（TRACE）
        """
        self.logger = logger
        self.common_util = CommonUtilClass(logger)

    def main(self, request_body: requestBody):
        """
        TFオペレータ無効化API メイン処理

        Returns:
            dict: 処理結果
        """
        try:
            # 05.共通DB接続準備処理
            # 05-01 共通DB接続情報取得処理
            common_util = CommonUtilClass(self.logger)
            common_db_connection_resource: PostgresDbUtilClass = None
            # 05-01-01 AWS SecretsManagerから共通DB接続情報を取得して、「変数．共通DB接続情報」に格納する
            # 05-02.「変数．共通DB接続情報」を利用して、共通DBに対してのコネクションを作成する
            common_db_info_response = common_util.get_common_db_info_and_connection()
            if not common_db_info_response["result"]:
                return common_db_info_response
            else:
                common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
                common_db_connection = common_db_info_response["common_db_connection"]

            # 06.TFオペレータ無効化検証処理
            tf_operator_invalid_verif_info = None
            # 06-01 TFオペレータテーブルからデータを取得し、「変数.TFオペレータ取得結果」に1レコードをタプルとして格納する
            tf_operator_invalid_verif_result = common_db_connection_resource.select_tuple_one(
                common_db_connection,
                SqlConstClass.TF_OPERATOR_INVALID_VERIF_SQL,
                request_body.tfOperatorId
            )
            # 06-02 「変数.TFオペレータ取得結果」が1以外の場合、「変数.エラー情報」を作成する
            if tf_operator_invalid_verif_result.get("result") and tf_operator_invalid_verif_result["rowcount"] != 1:
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020004"]["logMessage"], request_body.tfOperatorId))
                tf_operator_invalid_verif_info = {
                    "errorCode": "020004",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020004"]["message"], request_body.tfOperatorId)
                }

            # 06-03 「変数.TFオペレータ取得結果[0]」がtrueの場合、「変数.エラー情報」を作成する
            elif tf_operator_invalid_verif_result.get("result") and tf_operator_invalid_verif_result["query_results"][0]:

                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["030009"]["logMessage"]))
                tf_operator_invalid_verif_info = {
                    "errorCode": "030009",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["030009"]["message"])
                }
            # 06-04 処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            elif not tf_operator_invalid_verif_result["result"]:
                tf_operator_invalid_verif_info = self.common_util.create_postgresql_log(
                    tf_operator_invalid_verif_result["errorObject"],
                    None,
                    None,
                    tf_operator_invalid_verif_result["stackTrace"]
                ).get("errorInfo")
            # 07.共通エラーチェック処理
            # 07-01 以下の引数で共通エラーチェック処理を実行する
            # 07-02 例外が発生した場合、例外処理に遷移
            if tf_operator_invalid_verif_info is not None:
                self.common_util.common_error_check(tf_operator_invalid_verif_info)

            # 08.トランザクション作成処理
            # 08-01 「TFオペレータ更新トランザクション」を作成する

            # 09.TFオペレータ無効化フラグ更新処理
            tf_operator_invalid_update_info = None
            # 09-01 TFオペレータテーブルを更新する
            tf_operator_invalid_update_result = common_db_connection_resource.update(
                common_db_connection,
                SqlConstClass.TF_OPERATOR_INVALID_UPDATE_SQL,
                request_body.tfOperatorId
            )
            # 09-02 処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not tf_operator_invalid_update_result["result"]:
                tf_operator_invalid_update_info = self.common_util.create_postgresql_log(
                    tf_operator_invalid_update_result["errorObject"],
                    None,
                    None,
                    tf_operator_invalid_update_result["stackTrace"]
                ).get("errorInfo")
            # 10.共通エラーチェック処理
            # 10-01 以下の引数で共通エラーチェック処理を実行する
            # 10-02 例外が発生した場合、例外処理に遷移
            if tf_operator_invalid_update_info is not None:
                # ロールバック処理
                rollback_transaction = CallbackExecutor(
                    self.common_util.common_check_postgres_rollback,
                    common_db_connection,
                    common_db_connection_resource
                )
                self.common_util.common_error_check(
                    tf_operator_invalid_update_info,
                    rollback_transaction
                )

            # 11.トランザクションコミット処理
            # 11-01 「TFオペレータ更新トランザクション」をコミットする
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
