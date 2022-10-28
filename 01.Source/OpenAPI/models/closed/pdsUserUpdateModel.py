from typing import Optional
import traceback

# RequestBody
from pydantic import BaseModel
from util.callbackExecutorUtil import CallbackExecutor

# Exception
from exceptionClass.PDSException import PDSException

from util.commonUtil import CommonUtilClass
from util.postgresDbUtil import PostgresDbUtilClass
import util.logUtil as logUtil
from const.messageConst import MessageConstClass
from const.sqlConst import SqlConstClass


class requestBody(BaseModel):
    """
    リクエストボディクラス

    Args:
        BaseModel (Object): Pydanticのベースクラス
    """
    pdsUserId: Optional[str] = None
    tfContactAddress: Optional[str] = None
    pdsUserPublicKey: Optional[str] = None
    pdsUserPublicKeyIdx: Optional[int] = None
    multiDownloadFileSendAddressTo: Optional[str] = None
    multiDownloadFileSendAddressCc: Optional[str] = None
    multiDeleteFileSendAddressTo: Optional[str] = None
    multiDeleteFileSendAddressCc: Optional[str] = None
    publicKeySendAddressTo: Optional[str] = None
    publicKeySendAddressCc: Optional[str] = None


class pdsUserUpdateModelClass():
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
        PDSユーザ更新API メイン処理

        Returns:
            dict: 処理結果
        """
        try:
            # 05.共通DB接続準備処理
            # 05-01.共通DB接続情報取得処理
            common_db_connection_resource: PostgresDbUtilClass = None
            # 05-01-01.AWS SecretsManagerから共通DB接続情報を取得して、「変数．共通DB接続情報」に格納する
            # 05-01-02.「変数．共通DB接続情報」を利用して、共通DBに対してのコネクションを作成する
            common_db_info_response = self.common_util.get_common_db_info_and_connection()
            if not common_db_info_response["result"]:
                return common_db_info_response
            else:
                common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
                common_db_connection = common_db_info_response["common_db_connection"]

            # 06.PDSユーザ鍵存在検証処理
            # 06-01.以下の引数でPDSユーザ取得処理を実行する
            # 06-02.PDSユーザ取得処理からのレスポンスを、「変数．PDSユーザ取得処理実行結果」に格納する
            pds_user_get_result = self.common_util.check_pds_user_key(request_body.pdsUserId, request_body.pdsUserPublicKeyIdx, common_db_info_response)

            # 07.共通エラーチェック処理
            # 07-01.以下の引数で共通エラーチェック処理を実行する
            # 07-02.例外が発生した場合、例外処理に遷移
            if pds_user_get_result is not None:
                self.common_util.common_error_check(pds_user_get_result.get("errorInfo"))

            # 08.トランザクション作成処理
            # 08-01.「PDSユーザ更新トランザクション」を作成する

            # 09.PDSユーザ更新処理
            pds_user_update_result = None
            pds_user_update_error_info = None
            # 09-01.PDSユーザテーブルを更新する
            pds_user_update_result = common_db_connection_resource.update(
                common_db_connection,
                SqlConstClass.PDS_USER_UPDATE_SQL,
                request_body.tfContactAddress,
                request_body.multiDownloadFileSendAddressTo,
                request_body.multiDownloadFileSendAddressCc,
                request_body.multiDeleteFileSendAddressTo,
                request_body.multiDeleteFileSendAddressCc,
                request_body.publicKeySendAddressTo,
                request_body.publicKeySendAddressCc,
                request_body.pdsUserId
            )
            # 09-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            #       postgresqlエラー処理からのレスポンスを、「変数．エラー情報」に格納する
            if not pds_user_update_result["result"]:
                pds_user_update_error_info = self.common_util.create_postgresql_log(
                    pds_user_update_result["errorObject"],
                    None,
                    None,
                    pds_user_update_result["stackTrace"]
                ).get("errorInfo")

            # 10.共通エラーチェック処理
            # 10-01.以下の引数で共通エラーチェック処理を実行する
            # 10-02.例外が発生した場合、例外処理に遷移
            if pds_user_update_error_info is not None:
                rollback_transaction = CallbackExecutor(
                    self.common_util.common_check_postgres_rollback,
                    common_db_connection,
                    common_db_connection_resource
                )
                self.common_util.common_error_check(
                    pds_user_update_error_info,
                    rollback_transaction
                )

            # 11.PDSユーザ公開鍵更新処理
            # 11-01.以下の引数でPDSユーザ公開鍵更新処理を実行する
            # 11-02.PDSユーザ公開鍵更新処理からのレスポンスを、「変数．PDSユーザ公開鍵更新処理実行結果」に格納する
            pds_user_key_update_result = self.common_util.update_pds_user_key(
                request_body.pdsUserId,
                request_body.pdsUserPublicKeyIdx,
                request_body.pdsUserPublicKey,
                None,
                common_db_info_response
            )

            # 12.共通エラーチェック処理
            # 12-01.以下の引数で共通エラーチェック処理を実行する
            # 12-02.例外が発生した場合、例外処理に遷移
            if not pds_user_key_update_result["result"]:
                # ロールバック処理
                rollback_transaction = CallbackExecutor(
                    self.common_util.common_check_postgres_rollback,
                    common_db_connection,
                    common_db_connection_resource
                )
                self.common_util.common_error_check(
                    pds_user_key_update_result["errorInfo"],
                    rollback_transaction
                )

            # 13.トランザクションコミット処理
            # 13-01.「PDSユーザ更新トランザクション」をコミットする
            common_db_connection_resource.commit_transaction(common_db_connection)
            common_db_connection_resource.close_connection(common_db_connection)

            # 不要になったリソースの片付け
            self.common_util = None
        # 例外処理(PDSException)
        except PDSException as e:
            # PDSExceptionオブジェクトをエラーとしてスローする
            raise e

        # 例外処理
        except Exception as e:
            # エラー情報をCloudWatchへログ出力する
            self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["999999"]["logMessage"], str(e), traceback.format_exc()))
            # 以下をレスポンスとして返却する
            raise PDSException(
                {
                    "errorCode": "999999",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
                }
            )
