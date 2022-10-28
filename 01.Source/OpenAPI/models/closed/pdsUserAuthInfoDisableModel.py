import traceback
from typing import Optional
from pydantic import BaseModel

from util.callbackExecutorUtil import CallbackExecutor

# util
from util.commonUtil import CommonUtilClass
from util.postgresDbUtil import PostgresDbUtilClass
import util.logUtil as logUtil
# const
from const.messageConst import MessageConstClass
# Exception
from exceptionClass.PDSException import PDSException


# 検索用 水野担当ファイル(完了)
class requestBody(BaseModel):
    """
    リクエストボディクラス

    Args:
        BaseModel (Object): Pydanticのベースクラス
    """
    pdsUserId: Optional[str] = None
    pdsUserPublicKeyIdx: Optional[int] = None
    pdsUserPublicKeyEndDate: Optional[str] = None


class pdsUserAuthInfoDisableModelClass():

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
        PDSユーザ認証情報無効化API メイン処理

        Returns:
            dict: 処理結果
        """
        try:
            # 05.共通DB接続準備処理
            # 05-01.AWS SecretsManagerから共通DB接続情報を取得して、「変数．共通DB接続情報」に格納する
            common_util = CommonUtilClass(self.logger)
            common_db_connection_resource: PostgresDbUtilClass = None
            # 05-02.「変数．共通DB接続情報」を利用して、共通DBに対してのコネクションを作成する
            common_db_info_response = common_util.get_common_db_info_and_connection()
            if not common_db_info_response["result"]:
                return common_db_info_response
            else:
                common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
                common_db_connection = common_db_info_response["common_db_connection"]

            # 06.PDSユーザ鍵存在検証処理
            # 06-01.PDSユーザ鍵存在検証処理を実行する
            check_pds_user_key_response = self.common_util.check_pds_user_key(
                pdsUserId=request_body.pdsUserId,
                pdsKeyIdx=request_body.pdsUserPublicKeyIdx,
                common_db_info=common_db_info_response
            )

            # 07.共通エラーチェック処理
            # 07-01.共通エラーチェック処理を実行する
            # 07-02.例外が発生した場合、例外処理に遷移
            if check_pds_user_key_response.get("errorInfo"):
                self.common_util.common_error_check(check_pds_user_key_response["errorInfo"])

            # 08.トランザクション作成処理
            # 08-01.「PDSユーザ認証無効化トランザクション」を作成する

            # 09.PDSユーザ公開鍵更新処理
            # 09-01.PDSユーザ公開鍵更新処理を実行する
            update_pds_user_key_response = self.common_util.update_pds_user_key(
                pdsUserId=request_body.pdsUserId,
                pdsKeyIdx=request_body.pdsUserPublicKeyIdx,
                pdsKey=None,
                endDate=request_body.pdsUserPublicKeyEndDate,
                common_db_info=common_db_info_response
            )

            # 10.共通エラーチェック処理
            # 10-01.共通エラーチェック処理を実行する
            # 10-02.例外が発生した場合、例外処理に遷移
            if update_pds_user_key_response.get("errorInfo"):
                # ロールバック処理
                rollback_transaction = CallbackExecutor(
                    self.common_util.common_check_postgres_rollback,
                    common_db_connection,
                    common_db_connection_resource
                )
                self.common_util.common_error_check(
                    update_pds_user_key_response["errorInfo"],
                    rollback_transaction
                )

            # 11.トランザクションコミット処理
            # 11-01.トランザクションをコミットする
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
