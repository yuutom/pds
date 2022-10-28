import traceback

# RequestBody
from util.commonUtil import CommonUtilClass
from util.postgresDbUtil import PostgresDbUtilClass
from util.cryptoUtil import CryptUtilClass
from util.commonUtil import get_str_date_in_X_days, get_str_datetime_in_X_days, get_uuid_no_hypen, random_upper
import util.logUtil as logUtil
from util.fileUtil import NoHeaderOneItemCsvStringClass, CsvStreamClass
from util.callbackExecutorUtil import CallbackExecutor
from const.messageConst import MessageConstClass
from const.sqlConst import SqlConstClass
from const.wbtConst import wbtConstClass
from const.fileNameConst import FileNameConstClass
# Exception
from exceptionClass.PDSException import PDSException


# 検索用 水野担当ファイル(完了)
class tfOperatorCreateClass():

    def __init__(self, logger):
        """
        コンストラクタ

        Args:
            logger (Logger): ロガー（TRACE）
        """
        self.logger = logger
        self.common_util = CommonUtilClass(logger)
        self.error_info = None

    def main(self, request_body):
        """
        TFオペレータ登録API メイン処理

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

            # 06.TFオペレータ取得処理
            # 06-01.TFオペレータテーブルからデータを取得し、「変数.TFオペレータ取得結果」に1レコードをタプルとして格納する
            tf_operator_select_result = common_db_connection_resource.select_tuple_one(
                common_db_connection,
                SqlConstClass.TF_OPERATOR_REGISTER_SELECT_SQL,
                request_body.tfOperatorId
            )

            # 06-02.「変数.TFオペレータ取得結果["rowcount"]」が0以外の場合、「変数.エラー情報」を作成する
            # Modify(t.ii)：取得したカウントを参照すること。設計書の修正も必要と思われる
            if tf_operator_select_result.get("result") and tf_operator_select_result["query_results"][0] != 0:
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["030001"]["logMessage"], "TFオペレータID", request_body.tfOperatorId))
                self.error_info = {
                    "errorCode": "030001",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["030001"]["message"], "TFオペレータID", request_body.tfOperatorId)
                }

            # 06-03.処理が失敗した場合は「postgresqlエラー処理」からのレスポンスを、「変数．エラー情報」に格納する
            if not tf_operator_select_result["result"]:
                self.error_info = self.common_util.create_postgresql_log(
                    tf_operator_select_result["errorObject"],
                    None,
                    None,
                    tf_operator_select_result["stackTrace"]
                ).get("errorInfo")

            # 07.共通エラーチェック処理
            # 07-01.以下の引数で共通エラーチェック処理を実行する
            # 07-02.例外が発生した場合、例外処理に遷移
            if self.error_info is not None:
                self.common_util.common_error_check(
                    self.error_info
                )

            # 08.仮パスワード生成処理
            # 08-01.UUID(v4ハイフンなし)を作成し、「変数．UUID」に格納する
            uuid = get_uuid_no_hypen()
            # 08-02.「変数．UUID」の文字列中のランダムな英小文字1文字を英大文字に変換して「変数．仮パスワード」に格納する
            temporary_password = random_upper(uuid)
            # TODO(araki): 仮パスワード確認用。WBT実装後に消す
            print(temporary_password)
            # 08-03.「変数．仮パスワード」をハッシュ化してハッシュ化済UUIDを作成する
            util = CryptUtilClass(self.logger)
            hash_password = util.hash_password(temporary_password)

            # 09. CSVファイル作成処理
            # 09-01.取得した以下のデータをもとにCSVファイルを作成する
            temporary_password_csv_string = NoHeaderOneItemCsvStringClass([temporary_password])
            # 09-02.作成したCSVを「変数．パスワード通知ファイル」に格納する
            temporary_password_csv_stream = CsvStreamClass(temporary_password_csv_string)

            # 10.トランザクション作成処理
            # 10-01.「TFオペレータ登録トランザクション」を作成する

            # 11.TFオペレータ登録処理
            # 11-01.TFオペレータテーブルに登録する
            pds_user_public_key_insert_result = common_db_connection_resource.insert(
                common_db_connection,
                SqlConstClass.TF_OPERATOR_REGISTER_INSERT_SQL,
                request_body.tfOperatorId,
                request_body.tfOperatorName,
                request_body.tfOperatorMail,
                hash_password,
                True,
                False,
                get_str_date_in_X_days(7),
                None,
                None,
                None,
                None,
            )
            # 11-02.処理が失敗した場合は、postgresqlエラー処理を実行する
            if not pds_user_public_key_insert_result["result"]:
                self.error_info = self.common_util.create_postgresql_log(
                    pds_user_public_key_insert_result["errorObject"],
                    "TFオペレータID",
                    request_body.tfOperatorId,
                    pds_user_public_key_insert_result["stackTrace"]
                ).get("errorInfo")

            # 12.共通エラーチェック処理
            # 12-01.以下の引数で共通エラーチェック処理を実行する
            # 12-02.例外が発生した場合、例外処理に遷移
            if self.error_info is not None:
                rollback_transaction = CallbackExecutor(
                    self.common_util.common_check_postgres_rollback,
                    common_db_connection,
                    common_db_connection_resource
                )
                self.common_util.common_error_check(
                    self.error_info,
                    rollback_transaction
                )

            # 13.WBT新規メール情報登録API実行処理
            # 13-01.WBT新規メール情報登録API呼び出し処理を実行する
            # 13-02.「新規メール情報登録API」からのレスポンスを、「変数．WBT新規メール情報登録API実行結果」に格納する
            # Modify(t.ii)：ダウンロード期日はdatetime型なので変更した。設計書の修正が必要
            wbt_mails_add_api_exec_result = common_util.wbt_mails_add_api_exec(
                repositoryType=wbtConstClass.REPOSITORY_TYPE["RETURN"],
                fileName=FileNameConstClass.PASSWORD_NOTIFICATION,
                downloadDeadline=get_str_datetime_in_X_days(7),
                replyDeadline=None,
                comment=wbtConstClass.MESSAGE["TF_OPERATOR_CREATE"],
                mailAddressTo=request_body.tfOperatorMail,
                mailAddressCc=None,
                title=wbtConstClass.TITLE["TF_OPERATOR_CREATE"]
            )
            # 13-03.処理が失敗した場合は「変数．エラー情報」を作成し、エラーログをCloudWatchにログ出力する
            if not wbt_mails_add_api_exec_result["result"]:
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990011"]["logMessage"]))
                self.error_info = {
                    "errorCode": "990011",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["990011"]["message"], "990011")
                }

            # 14.共通エラーチェック処理
            # 14-01.以下の引数で共通エラーチェック処理を実行する
            if self.error_info is not None:
                rollback_transaction = CallbackExecutor(
                    self.common_util.common_check_postgres_rollback,
                    common_db_connection,
                    common_db_connection_resource
                )
                self.common_util.common_error_check(
                    self.error_info,
                    rollback_transaction
                )

            # 15.WBTファイル登録API実行処理
            # 15-01.WBTファイル登録APIを呼び出す
            # 15-02.「ファイル登録API」からのレスポンスを、「変数．WBTファイル登録API実行結果」に格納する
            wbt_file_add_api_exec_result = common_util.wbt_file_add_api_exec(
                mailId=wbt_mails_add_api_exec_result["id"],
                fileId=wbt_mails_add_api_exec_result["attachedFiles"][0]["id"],
                file=temporary_password_csv_stream.get_temp_csv(),
                chunkNo=None,
                chunkTotalNumber=None
            )
            # 15-03.処理が失敗した場合は「変数．エラー情報」を作成し、エラーログをCloudWatchにログ出力する
            if not wbt_file_add_api_exec_result["result"]:
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990013"]["logMessage"]))
                self.error_info = {
                    "errorCode": "990013",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["990013"]["message"], "990013")
                }

            # 16.共通エラーチェック処理
            # 16-01.以下の引数で共通エラーチェック処理を実行する
            # 16-02.例外が発生した場合、例外処理に遷移
            if self.error_info is not None:
                rollback_transaction = CallbackExecutor(
                    self.common_util.common_check_postgres_rollback,
                    common_db_connection,
                    common_db_connection_resource
                )
                wbt_send_delete_api_exec = CallbackExecutor(
                    self.common_util.wbt_mail_cancel_exec,
                    wbt_mails_add_api_exec_result["id"]
                )
                self.common_util.common_error_check(
                    self.error_info,
                    rollback_transaction,
                    wbt_send_delete_api_exec
                )

            # 17.トランザクションコミット処理
            # 17-01.「PDSユーザ公開鍵トランザクション」をコミットする
            common_db_connection_resource.commit_transaction(common_db_connection)
            common_db_connection_resource.close_connection(common_db_connection)

            # 18.パスワード通知CSVの削除処理
            # 18-01.「変数.パスワード通知ファイル」をNullにする
            temporary_password_csv_string = None
            temporary_password_csv_stream = None

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
