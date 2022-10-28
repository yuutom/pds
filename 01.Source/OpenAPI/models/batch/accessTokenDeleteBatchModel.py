import traceback

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


class accessTokenDeleteBatchModelClass():

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
        アクセストークン削除バッチ メイン処理

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

            # 02.トランザクション作成処理
            # 02-01.「アクセストークン削除トランザクション」を作成する

            # 03.アクセストークン削除処理
            access_token_delete_info = None
            # 03-01 アクセストークンテーブルからアクセストークンを削除する
            access_token_delete_result = common_db_connection_resource.update(
                common_db_connection,
                SqlConstClass.ACCESS_TOKEN_BATCH_DELETE_SQL,
                commonUtil.get_datetime_jst()
            )
            # 03-02 処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not access_token_delete_result["result"]:
                access_token_delete_info = self.common_util.create_postgresql_log(
                    access_token_delete_result["errorObject"],
                    None,
                    None,
                    access_token_delete_result["stackTrace"]
                ).get("errorInfo")
            # 04.共通エラーチェック処理
            # 04-01 以下の引数で共通エラーチェック処理を実行する
            # 04-02 例外が発生した場合、例外処理に遷移
            if access_token_delete_info is not None:
                # ロールバック処理
                rollback_transaction = CallbackExecutor(
                    self.common_util.common_check_postgres_rollback,
                    common_db_connection,
                    common_db_connection_resource
                )
                self.common_util.common_error_check(
                    access_token_delete_info,
                    rollback_transaction
                )

            # 05.トランザクションコミット処理
            # 05-01 「アクセストークン削除トランザクション」をコミットする
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
