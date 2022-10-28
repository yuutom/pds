import traceback
# util
from util.postgresDbUtil import PostgresDbUtilClass
from util.commonUtil import CommonUtilClass, get_beginning_and_end_of_the_last_month, get_str_datetime, get_str_datetime_in_X_days
from util.fileUtil import HeaderDictItemCsvStringClass, HeaderDictItemCsvStreamClass
import util.logUtil as logUtil
from util.callbackExecutorUtil import CallbackExecutor
from util.billUtil import BillUtilClass

# const
from const.messageConst import MessageConstClass
from const.sqlConst import SqlConstClass
from const.wbtConst import wbtConstClass
# Exception
from exceptionClass.PDSException import PDSException


# 検索用 水野担当ファイル
class pdsUserNoticeUseCountBatchModelClass():
    def __init__(self, logger):
        """
        コンストラクタ

        Args:
            logger (Logger): ロガー（TRACE）
        """
        self.logger = logger
        self.common_util = CommonUtilClass(logger)
        self.bill_util = BillUtilClass(logger)
        self.error_info = None

    def main(self):
        """
        PDSユーザ利用回数通知バッチ メイン処理

        """
        try:
            # 01.共通DB接続準備処理
            # 01-01.AWS SecretsManagerから共通DB接続情報を取得して、「変数．共通DB接続情報」に格納する
            common_util = CommonUtilClass(self.logger)
            common_db_connection_resource: PostgresDbUtilClass = None
            # 01-02.「変数．共通DB接続情報」を利用して、共通DBに対してのコネクションを作成する
            common_db_info_response = common_util.get_common_db_info_and_connection()
            if not common_db_info_response["result"]:
                return common_db_info_response
            else:
                common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
                common_db_connection = common_db_info_response["common_db_connection"]

            # 02.PDSユーザ情報取得処理
            # 02-01.PDSユーザテーブルからデータを取得し、「変数．PDSユーザ取得結果リスト」に全レコードをタプルのリストとして格納する
            pds_user_get_result_list = common_db_connection_resource.select_tuple_list(
                common_db_connection,
                SqlConstClass.PDS_USER_VALID_FLG_TRUE_SELECT_SQL
            )
            # 02-02.処理が失敗した場合は、postgresqlエラー処理を実行する
            if not pds_user_get_result_list["result"]:
                self.error_info = self.common_util.create_postgresql_log(
                    pds_user_get_result_list["errorObject"],
                    None,
                    None,
                    pds_user_get_result_list["stackTrace"]
                ).get("errorInfo")

            # 03.共通エラーチェック処理
            # 03-01.以下の引数で共通エラーチェック処理を実行する
            if self.error_info is not None:
                self.common_util.common_error_check(self.error_info)

            # 「変数．PDSユーザ情報取得結果リスト」の要素数分繰り返す
            for pds_user_loop, pds_user in enumerate(pds_user_get_result_list["query_results"]):

                # 請求金額計算用変数
                billing_amount = 0

                # 04.API実行履歴取得処理
                pds_user_id = pds_user[0]
                beginning_of_the_last_month, end_of_the_last_month = get_beginning_and_end_of_the_last_month()
                # 04-01.API実行履歴テーブルからデータを取得し、「変数．API実行履歴取得結果リスト」に全レコードをタプルのリストとして格納する
                api_history_get_result_list = common_db_connection_resource.select_tuple_list(
                    common_db_connection,
                    SqlConstClass.API_HISTORY_SELECT_SQL,
                    pds_user_id,
                    beginning_of_the_last_month,
                    end_of_the_last_month
                )
                # 04-02.処理が失敗した場合は、postgresqlエラー処理を実行する
                if not api_history_get_result_list["result"]:
                    self.error_info = self.common_util.create_postgresql_log(
                        api_history_get_result_list["errorObject"],
                        None,
                        None,
                        api_history_get_result_list["stackTrace"]
                    ).get("errorInfo")

                # 05.共通エラーチェック処理
                # 05-01.以下の引数で共通エラーチェック処理を実行する
                if self.error_info is not None:
                    self.common_util.common_error_check(self.error_info)

                # 06.API種別カウント作成処理
                # 06-01. 「変数．API種別カウント」を作成する
                api_type_count = {
                    "register_success": 0,
                    "register_failure": 0,
                    "update_success": 0,
                    "update_failure": 0,
                    "read_success": 0,
                    "read_failure": 0,
                    "delete_success": 0,
                    "delete_failure": 0
                }

                # 「変数．API実行履歴取得結果リスト」の要素数分繰り返す
                for api_history_loop, api_history in enumerate(api_history_get_result_list["query_results"]):

                    # 07.請求金額取得処理
                    api_type = api_history[0]
                    exec_status = api_history[1]
                    count = api_history[2]
                    # 07-01.請求金額テーブルからデータを取得し、「変数．請求金額取得結果」に全レコードをタプルのリストとして格納する
                    billing_get_result_list = common_db_connection_resource.select_tuple_list(
                        common_db_connection,
                        SqlConstClass.BILLING_SELECT_SQL,
                        api_type,
                        count
                    )
                    # 07-02.処理が失敗した場合は、postgresqlエラー処理を実行する
                    if not billing_get_result_list["result"]:
                        self.error_info = self.common_util.create_postgresql_log(
                            billing_get_result_list["errorObject"],
                            None,
                            None,
                            billing_get_result_list["stackTrace"]
                        ).get("errorInfo")

                    # 08.共通エラーチェック処理
                    # 08-01.以下の引数で共通エラーチェック処理を実行する
                    if self.error_info is not None:
                        self.common_util.common_error_check(self.error_info)

                    # 09.累進請求金額計算処理
                    charge_bill_list = billing_get_result_list["query_results"]
                    # 09-01.累進請求金額計算処理を実行する
                    progressive_billing_calculation_response = self.bill_util.progressive_billing_exec(api_type, exec_status, count, charge_bill_list)

                    # 10. 請求金額計算処理
                    # 10-01. 「変数．請求金額」に「変数．累進請求金額計算処理結果．累進請求金額」を加算する
                    billing_amount += progressive_billing_calculation_response["progressiveBilling"]

                    # 11.API種別カウント加算処理
                    # 11-01.「変数．API種別カウント」のそれぞれの値を加算する
                    if api_history[0] == "2" and api_history[1]:
                        api_type_count["register_success"] = api_history[2]
                    if api_history[0] == "2" and not api_history[1]:
                        api_type_count["register_failure"] = api_history[2]
                    if api_history[0] == "3" and api_history[1]:
                        api_type_count["update_success"] = api_history[2]
                    if api_history[0] == "3" and not api_history[1]:
                        api_type_count["update_failure"] = api_history[2]
                    if api_history[0] == "4" and api_history[1]:
                        api_type_count["read_success"] = api_history[2]
                    if api_history[0] == "4" and not api_history[1]:
                        api_type_count["read_failure"] = api_history[2]
                    if api_history[0] == "5" and api_history[1]:
                        api_type_count["delete_success"] = api_history[2]
                    if api_history[0] == "5" and not api_history[1]:
                        api_type_count["delete_failure"] = api_history[2]

                # 12.リソース請求金額計算処理
                # 12-01.リソース請求金額計算処理を実行する
                resource_billing_calculation_response = self.bill_util.resource_billing_exec(pds_user_id, common_db_info_response)
                # 13.請求金額計算処理
                # 13-01.「変数．請求金額」に「変数．リソース請求金額計算処理結果．リソース請求金額」を加算する
                billing_amount += resource_billing_calculation_response["resourceBilling"]

                # 14.CSVファイル作成処理
                file_name = "UseInfo_" + pds_user[0] + "_" + get_str_datetime() + ".csv"
                header_list = ["PDSユーザID", "PDSユーザ名", "結果", "登録", "更新", "参照", "削除", "金額"]
                dict_list = [
                    {
                        "PDSユーザID": pds_user[0],
                        "PDSユーザ名": pds_user[1],
                        "結果": "成功",
                        "登録": api_type_count["register_success"],
                        "更新": api_type_count["update_success"],
                        "参照": api_type_count["read_success"],
                        "削除": api_type_count["delete_success"],
                        "金額": billing_amount
                    },
                    {
                        "PDSユーザID": pds_user[0],
                        "PDSユーザ名": pds_user[1],
                        "結果": "失敗",
                        "登録": api_type_count["register_failure"],
                        "更新": api_type_count["update_failure"],
                        "参照": api_type_count["read_failure"],
                        "削除": api_type_count["delete_failure"],
                        "金額": billing_amount
                    }
                ]
                # 14-01.取得したデータをもとにCSVファイルを作成する
                pds_user_use_count_string = HeaderDictItemCsvStringClass(header_list, dict_list, "-")
                pds_user_use_count_stream = HeaderDictItemCsvStreamClass(pds_user_use_count_string)

                # 15.WBT新規メール情報登録API実行処理
                type = wbtConstClass.REPOSITORY_TYPE['RETURN']
                file_name = file_name
                download_deadline = get_str_datetime_in_X_days(7)
                message = wbtConstClass.MESSAGE['BILLING_DATA_NOTIFICATION']
                mail_address = pds_user[2]
                title = wbtConstClass.TITLE['BILLING_DATA_NOTIFICATION']
                # 15-01.WBT新規メール情報登録API呼び出し処理を実行する
                # 15-02.「新規メール情報登録API」からのレスポンスを、「変数．WBT新規メール情報登録API実行結果」に格納する
                wbt_mails_add_api_exec_result = common_util.wbt_mails_add_api_exec(
                    repositoryType=type,
                    fileName=file_name,
                    downloadDeadline=download_deadline,
                    replyDeadline=None,
                    comment=message,
                    mailAddressTo=mail_address,
                    mailAddressCc=None,
                    title=title
                )
                # 15-03.処理が失敗した場合は「変数．エラー情報」を作成し、エラーログをCloudWatchにログ出力する
                if not wbt_mails_add_api_exec_result["result"]:
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990011"]["logMessage"]))
                    self.error_info = {
                        "errorCode": "990011",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["990011"]["message"], "990011")
                    }

                # 16.共通エラーチェック処理
                # 16-01.以下の引数で共通エラーチェック処理を実行する
                if self.error_info is not None:
                    self.common_util.common_error_check(self.error_info)

                # 17.WBTファイル登録API実行処理
                mail_id = wbt_mails_add_api_exec_result["id"]
                file_id = wbt_mails_add_api_exec_result["attachedFiles"][0]["id"]
                # 17-01.WBTファイル登録APIを呼び出す
                # 17-02.「ファイル登録API」からのレスポンスを、「変数．WBTファイル登録API実行結果」に格納する
                wbt_file_add_api_exec_result = common_util.wbt_file_add_api_exec(
                    mailId=mail_id,
                    fileId=file_id,
                    file=pds_user_use_count_stream.get_temp_csv(),
                    chunkNo=None,
                    chunkTotalNumber=None
                )
                # 17-03.処理が失敗した場合は「変数．エラー情報」を作成し、エラーログをCloudWatchにログ出力する
                if not wbt_file_add_api_exec_result["result"]:
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990013"]["logMessage"]))
                    self.error_info = {
                        "errorCode": "990013",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["990013"]["message"], "990013")
                    }

                # 18.共通エラーチェック処理
                # 18-01.以下の引数で共通エラーチェック処理を実行する
                if self.error_info is not None:
                    wbt_send_delete_api_exec = CallbackExecutor(
                        self.common_util.wbt_mail_cancel_exec,
                        wbt_mails_add_api_exec_result["id"]
                    )
                    self.common_util.common_error_check(
                        self.error_info,
                        wbt_send_delete_api_exec
                    )

                # 19.PDSユーザ利用回数ファイル削除処理
                # 19-01.「変数．PDSユーザ利用回数ファイル」をNullにする
                pds_user_use_count_string = None
                pds_user_use_count_stream = None

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
