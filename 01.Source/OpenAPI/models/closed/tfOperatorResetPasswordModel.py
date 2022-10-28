from typing import Optional
import traceback

# RequestBody
from pydantic import BaseModel
from util.cryptoUtil import CryptUtilClass

# Util
from util.commonUtil import CommonUtilClass
from util.postgresDbUtil import PostgresDbUtilClass
import util.commonUtil as commonUtil
import util.logUtil as logUtil
from util.fileUtil import NoHeaderOneItemCsvStringClass, CsvStreamClass
# from const.systemConst import SystemConstClass
# from const.wbtConst import wbtConstClass
from const.messageConst import MessageConstClass
from const.sqlConst import SqlConstClass
from const.fileNameConst import FileNameConstClass
from const.wbtConst import wbtConstClass
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


class tfOperatorResetPasswordClass():

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
        TFオペレータパスワードリセットAPI メイン処理

        Returns:
            dict: 処理結果
        """
        try:
            # 05.仮パスワード生成処理
            # 05-01.UUID(v4ハイフンなし)を作成し、「変数．UUID」に格納する
            uuid = commonUtil.get_uuid_no_hypen()
            # 05-02.「変数．UUID」の文字列中のランダムな英小文字1文字を英大文字に変換して「変数．仮パスワード」に格納する
            temporary_password = commonUtil.random_upper(uuid)
            # TODO(araki): 仮パスワード確認用。WBT実装後に消す
            print(temporary_password)
            # 05-03.「変数．仮パスワード」をハッシュ化してハッシュ化済UUIDを作成する
            util = CryptUtilClass(self.logger)
            hash_password = util.hash_password(temporary_password)

            # 06.CSVファイル作成処理
            # 06-01.取得した以下のデータをもとにCSVファイルを作成する
            password_csv_string = NoHeaderOneItemCsvStringClass([temporary_password])
            # 06-02.作成したCSVを「変数．パスワード通知ファイル」に格納する
            password_csv_stream = CsvStreamClass(password_csv_string)

            # 07.共通DB接続準備処理
            # 07-01.共通DB接続情報取得処理
            common_util = CommonUtilClass(self.logger)
            common_db_connection_resource: PostgresDbUtilClass = None
            # 07-01-01.AWS SecretsManagerから共通DB接続情報を取得して、「変数．共通DB接続情報」に格納する
            # 07-02.「変数．共通DB接続情報」を利用して、共通DBに対してのコネクションを作成する
            common_db_info_response = common_util.get_common_db_info_and_connection()
            if not common_db_info_response["result"]:
                return common_db_info_response
            else:
                common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
                common_db_connection = common_db_info_response["common_db_connection"]

            # 08.TFオペレータパスワードリセット情報取得処理
            tf_operator_password_reset_select_info = None
            # 08-01.TFオペレータテーブルからデータを取得し、「変数.TFオペレータパスワードリセット情報取得結果」に1レコードをタプルとして格納する
            tf_operator_password_reset_select_result = common_db_connection_resource.select_tuple_one(
                common_db_connection,
                SqlConstClass.TF_OPERATOR_RESET_PASSWORD_SELECT_SQL,
                request_body.tfOperatorId
            )
            # 08-02.「変数.TFオペレータパスワードリセット情報取得結果」の件数が1件以外の場合、「変数.エラー情報」を作成する
            if tf_operator_password_reset_select_result.get("result") and tf_operator_password_reset_select_result["rowcount"] != 1:
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020004"]["logMessage"], request_body.tfOperatorId))
                tf_operator_password_reset_select_info = {
                    "errorCode": "020004",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020004"]["message"], request_body.tfOperatorId)
                }
            # 08-03.「変数.TFオペレータ取得結果[0]」がtrueの場合、「変数.エラー情報」を作成する
            elif tf_operator_password_reset_select_result.get("result") and tf_operator_password_reset_select_result["query_results"][0]:
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["030009"]["logMessage"]))
                tf_operator_password_reset_select_info = {
                    "errorCode": "030009",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["030009"]["message"])
                }
            # 08-04.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            elif not tf_operator_password_reset_select_result["result"]:
                tf_operator_password_reset_select_info = self.common_util.create_postgresql_log(
                    tf_operator_password_reset_select_result["errorObject"],
                    None,
                    None,
                    tf_operator_password_reset_select_result["stackTrace"]
                ).get("errorInfo")
            # 09.共通エラーチェック処理
            # 09-01.以下の引数で共通エラーチェック処理を実行する
            # 09-02.例外が発生した場合、例外処理に遷移
            if tf_operator_password_reset_select_info is not None:
                self.common_util.common_error_check(tf_operator_password_reset_select_info)

            # 10.トランザクション作成処理
            # 10-01.「TFオペレータ更新トランザクション」を作成する

            # 11.TFオペレータパスワードリセット処理
            tf_operator_password_reset_update_info = None

            # 11-01.TFオペレータテーブルを更新する
            tf_operator_password_reset_update_result = common_db_connection_resource.update(
                common_db_connection,
                SqlConstClass.TF_OPERATOR_RESET_PASSWORD_UPDATE_SQL,
                hash_password,
                tf_operator_password_reset_select_result["query_results"][1],
                tf_operator_password_reset_select_result["query_results"][2],
                tf_operator_password_reset_select_result["query_results"][3],
                tf_operator_password_reset_select_result["query_results"][4],
                commonUtil.get_str_date_in_X_days(7),
                request_body.tfOperatorId
            )

            # 11-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not tf_operator_password_reset_update_result["result"]:
                tf_operator_password_reset_update_info = self.common_util.create_postgresql_log(
                    tf_operator_password_reset_update_result["errorObject"],
                    None,
                    None,
                    tf_operator_password_reset_update_result["stackTrace"]
                ).get("errorInfo")
            # 12.共通エラーチェック処理
            # 12-01.以下の引数で共通エラーチェック処理を実行する
            # 12-02.例外が発生した場合、例外処理に遷移
            if tf_operator_password_reset_update_info is not None:
                # ロールバック処理
                rollback_transaction = CallbackExecutor(
                    self.common_util.common_check_postgres_rollback,
                    common_db_connection,
                    common_db_connection_resource
                )
                self.common_util.common_error_check(
                    tf_operator_password_reset_update_info,
                    rollback_transaction
                )

            # 13.WBT新規メール情報登録API実行処理
            repositoryType = wbtConstClass.REPOSITORY_TYPE['RETURN']
            fileName = FileNameConstClass.PASSWORD_NOTIFICATION_NAME + FileNameConstClass.PASSWORD_NOTIFICATION_EXTENSION
            downloadDeadline = commonUtil.get_str_datetime_in_X_days(7)
            comment = wbtConstClass.MESSAGE['TF_OPERATOR_PASSWORD_RESET']
            mailAddressTo = tf_operator_password_reset_select_result["query_results"][5]
            title = wbtConstClass.TITLE['TF_OPERATOR_PASSWORD_RESET']
            # 13-01.以下の引数でWBTの新規メール情報登録API呼び出し処理を実行する
            # 13-02.WBT新規メール情報登録API実行処理からのレスポンスを、「変数．WBT新規メール情報登録API実行結果」に格納する
            wbt_mails_add_api_result = common_util.wbt_mails_add_api_exec(
                repositoryType=repositoryType,
                fileName=fileName,
                downloadDeadline=downloadDeadline,
                replyDeadline=None,
                comment=comment,
                mailAddressTo=mailAddressTo,
                mailAddressCc=None,
                title=title
            )
            # 13-03.WebBureauTransferの処理に失敗した場合、「変数．エラー情報」にエラー情報を作成する
            if not wbt_mails_add_api_result["result"]:
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990011"]["logMessage"]))
                self.error_info = {
                    "errorInfo": {
                        "errorCode": "990011",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["990011"]["message"], "990011")
                    }
                }
            # 14.共通エラーチェック処理
            # 14-01.以下の引数で共通エラーチェック処理を実行する
            # 14-02.例外が発生した場合、例外処理に遷移
            if wbt_mails_add_api_result.get("errorInfo"):
                # ロールバック処理
                rollback_transaction = CallbackExecutor(
                    self.common_util.common_check_postgres_rollback,
                    common_db_connection,
                    common_db_connection_resource
                )
                self.common_util.common_error_check(
                    self.error_info["errorInfo"],
                    rollback_transaction
                )

            # 15.WBTファイル登録API実行処理
            # 15-01.以下のパラメータでWBTのファイル登録APIを呼び出す
            mailId = wbt_mails_add_api_result["id"]
            fileId = wbt_mails_add_api_result["attachedFiles"][0]["id"]
            file = password_csv_stream
            chunkNo = '1'
            chunkTotalNumber = '1'
            # 15-02.WBTファイル登録API実行処理からのレスポンスを、「変数．WBTファイル登録API実行処理」に格納する
            wbt_file_add_api_result = self.common_util.wbt_file_add_api_exec(
                mailId,
                fileId,
                file.get_temp_csv(),
                chunkNo,
                chunkTotalNumber
            )
            # 15-03.処理が失敗した場合は「変数．エラー情報」を作成し、エラーログをCloudWatchにログ出力する
            if not wbt_file_add_api_result["result"]:
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990013"]["logMessage"]))
                self.error_info = {
                    "errorInfo": {
                        "errorCode": "990013",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["990013"]["message"], "990013")
                    }
                }

            # 16.共通エラーチェック処理
            # 16-01.以下の引数で共通エラーチェック処理を実行する
            # 16-02.例外が発生した場合、例外処理に遷移
            if wbt_file_add_api_result.get("errorInfo"):
                rollback_transaction = CallbackExecutor(
                    self.common_util.common_check_postgres_rollback,
                    common_db_connection,
                    common_db_connection_resource
                )
                self.common_util.common_error_check(
                    self.error_info["errorInfo"],
                    rollback_transaction,
                    self.common_util.wbt_mail_cancel_exec(mailId)
                )

            # 17.トランザクションコミット処理
            # 17-01.「TFオペレータ更新トランザクション」をコミットする
            common_db_connection_resource.commit_transaction(common_db_connection)
            common_db_connection_resource.close_connection(common_db_connection)

            # 18.パスワード通知CSVの削除処理
            # 18-01.「変数．パスワード通知ファイル」をNullにする
            password_csv_string = None
            password_csv_stream = None

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
