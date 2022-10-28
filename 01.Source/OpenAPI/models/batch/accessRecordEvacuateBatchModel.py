import traceback
from dateutil.relativedelta import relativedelta
from const.systemConst import SystemConstClass

from util.commonUtil import CommonUtilClass
from util.postgresDbUtil import PostgresDbUtilClass
import util.logUtil as logUtil
import util.commonUtil as commonUtil
from util.s3Util import s3UtilClass
from const.messageConst import MessageConstClass
from const.sqlConst import SqlConstClass
from util.fileUtil import HeaderListItemCsvStringClass, HeaderListItemCsvStreamClass
from util.callbackExecutorUtil import CallbackExecutor

# Exception
from exceptionClass.PDSException import PDSException


class AccessRecordEvacuateBatchModel():
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
        アクセス記録退避バッチ メイン処理

        """

        try:
            # 01.共通DB接続準備処理
            # 01-01.共通DB接続情報取得処理
            common_util = CommonUtilClass(self.logger)
            common_db_connection_resource: PostgresDbUtilClass = None
            # 01-01-01.AWS SecretsManagerから共通DB接続情報を取得して、「変数．共通DB接続情報」に格納する
            # 01-02.「変数．共通DB接続情報」を利用して、共通DBに対してのコネクションを作成する
            common_db_info_response = common_util.get_common_db_info_and_connection()
            if not common_db_info_response["result"]:
                return common_db_info_response
            else:
                common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
                common_db_connection = common_db_info_response["common_db_connection"]

            # 02.アクセス記録取得処理
            access_record_evacuate_search_error_info = None
            batch_start_datetime = commonUtil.get_datetime_jst() - relativedelta(months=6)
            batch_start_datetime_str = batch_start_datetime.strftime('%Y/%m/%d %H:%M:%S.%f')[:-3]
            file_name_datetime_str = batch_start_datetime.strftime('%Y%m%d%H%M%S%f')[:-3]
            # 02-01.API実行履歴テーブルからデータを取得し、「変数．API実行履歴取得結果リスト」に全レコードをタプルのリストとして格納する
            access_record_evacuate_search_result = common_db_connection_resource.select_tuple_list(
                common_db_connection,
                SqlConstClass.API_HISTORY_EVACUTATE_SELECT_SQL,
                batch_start_datetime_str
            )
            # 02-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not access_record_evacuate_search_result["result"]:
                access_record_evacuate_search_error_info = self.common_util.create_postgresql_log(
                    access_record_evacuate_search_result["errorObject"],
                    None,
                    None,
                    access_record_evacuate_search_result["stackTrace"]
                ).get("errorInfo")

            # 03.共通エラーチェック処理
            # 03-01.以下の引数で共通エラーチェック処理を実行する
            # 03-02.例外が発生した場合、例外処理に遷移
            if access_record_evacuate_search_error_info is not None:
                self.common_util.common_error_check(
                    access_record_evacuate_search_error_info
                )

            # 04.CSVファイル作成処理
            # 04-01.「変数．API実行履歴取得結果リスト」をもとにCSVファイルを作成する
            # 04-02.作成したCSVファイルを「変数．アクセス記録退避ファイル」に格納する
            header_list = ["exec_id", "pds_user_id", "api_type", "path_param_pds_user_domain_name", "exec_path", "exec_param", "exec_status", "exec_user_id", "register_datetime"]
            access_record_evacuate_csv = HeaderListItemCsvStringClass(header_list=header_list, tuple_list=access_record_evacuate_search_result["query_results"])
            access_record_evacuate_stream = HeaderListItemCsvStreamClass(access_record_evacuate_csv)
            file_name = SystemConstClass.ACCESS_RECORD_EVACUATE_FILE_PREFIX + file_name_datetime_str + SystemConstClass.ACCESS_RECORD_EVACUATE_FILE_EXTENSION

            # 05.アクセス記録退避処理
            s3_util = s3UtilClass(self.logger, SystemConstClass.ACCESS_RECORD_EVACUATE_BUCKET)
            put_file_result = False
            put_file_error_info = None
            for i in range(5):
                # 05-01.「変数．アクセス記録退避ファイル」のデータをS3に格納する
                if s3_util.put_file(file_name=file_name, data=access_record_evacuate_stream.get_temp_csv()):
                    put_file_result = True
                    break

            # 05-02.処理が失敗した場合は「変数．エラー情報」を作成し、エラーログをCloudWatchにログ出力する
            if not put_file_result:
                # 05-02-01.S3へのファイルコピーエラーが発生した場合、「変数．エラー情報」にエラー情報を追加する
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990021"]["logMessage"]))
                put_file_error_info = {
                    "errorCode": "990021",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["990021"]["message"], "990021")
                }

            # 06.共通エラーチェック処理
            # 06-01.以下の引数で共通エラーチェック処理を実行する
            # 06-02.例外が発生した場合、例外処理に遷移
            if put_file_error_info is not None:
                self.common_util.common_error_check(
                    put_file_error_info
                )

            # 07.トランザクション作成処理
            # 07-01.「アクセス記録削除トランザクション」を作成する

            # 08.API実行履歴削除処理
            access_record_evacuate_delete_error_info = None
            # 08-01.API実行履歴テーブルからデータを削除する
            access_record_delete_search_result = common_db_connection_resource.delete(
                common_db_connection,
                SqlConstClass.API_HISTORY_EVACUTATE_DELETE_SQL,
                batch_start_datetime_str
            )
            # 08-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not access_record_delete_search_result["result"]:
                access_record_evacuate_delete_error_info = self.common_util.create_postgresql_log(
                    access_record_delete_search_result["errorObject"],
                    None,
                    None,
                    access_record_delete_search_result["stackTrace"]
                ).get("errorInfo")

            # 09.共通エラーチェック処理
            # 09-01.以下の引数で共通エラーチェック処理を実行する
            # 09-02.例外が発生した場合、例外処理に遷移
            if access_record_evacuate_delete_error_info is not None:
                # ロールバック処理
                rollback_transaction = CallbackExecutor(
                    self.common_util.common_check_postgres_rollback,
                    common_db_connection,
                    common_db_connection_resource
                )
                # S3ファイル削除処理
                s3_file_delete = CallbackExecutor(
                    s3_util.deleteFile,
                    file_name
                )
                self.common_util.common_error_check(
                    access_record_evacuate_delete_error_info,
                    rollback_transaction,
                    s3_file_delete
                )

            # 10.トランザクションコミット処理
            # 10-01.「アクセス記録削除トランザクション」をコミットする
            common_db_connection_resource.commit_transaction(common_db_connection)
            common_db_connection_resource.close_connection(common_db_connection)

            # 11.アクセス記録退避ファイル削除処理
            # 11-01.「変数．アクセス記録退避ファイル」をNullにする
            access_record_evacuate_csv = None
            access_record_evacuate_stream = None

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
