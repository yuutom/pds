import traceback
from util.commonUtil import CommonUtilClass
from util.postgresDbUtil import PostgresDbUtilClass
import util.logUtil as logUtil
from util.billUtil import BillUtilClass
from util.checkUtil import check_require
from const.messageConst import MessageConstClass
from const.sqlConst import SqlConstClass
from const.apitypeConst import apitypeConstClass
from exceptionClass.PDSException import PDSException


# 検索用 水野担当ファイル(完了)
class pdsUserGetUseCountModelClass():
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

    def main(self, request_body):
        """
        PDSユーザ利用回数確認API メイン処理

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

            # 空文字判定処理
            from_date_exist_flg = check_require(request_body.fromDate)
            to_date_exist_flg = check_require(request_body.toDate)

            # クエリ編集処理
            select_items_list = []
            param_list = [request_body.pdsUserId]
            if from_date_exist_flg:
                select_items_list.append(" AND t_exec_api_history.register_datetime >= %s")
                param_list.append(request_body.fromDate)
            if to_date_exist_flg:
                select_items_list.append(" AND t_exec_api_history.register_datetime <= %s")
                param_list.append(request_body.toDate)
            select_items_list.append(" GROUP BY")
            select_items_list.append(" t_exec_api_history.api_type")
            select_items_list.append(" , t_exec_api_history.exec_status")
            select_items_list.append(" ORDER BY")
            select_items_list.append(" t_exec_api_history.api_type;")
            select_items_sql = ''.join(select_items_list)
            sql = SqlConstClass.PDS_USER_GET_USE_COUNT_API_HISTORY_SELECT_SQL + select_items_sql

            # 06.API実行履歴取得処理
            # 06-01.API実行履歴テーブルからデータを取得し、「変数．API実行履歴取得結果リスト」に全レコードをタプルのリストとして格納する
            api_history_get_result_list = common_db_connection_resource.select_tuple_list(
                common_db_connection,
                sql,
                *param_list
            )
            # 06-02.処理が失敗した場合は、postgresqlエラー処理を実行する
            if not api_history_get_result_list["result"]:
                self.error_info = self.common_util.create_postgresql_log(
                    api_history_get_result_list["errorObject"],
                    None,
                    None,
                    api_history_get_result_list["stackTrace"]
                ).get("errorInfo")

            # 07.共通エラーチェック処理
            # 07-01.以下の引数で共通エラーチェック処理を実行する
            # 07-02.例外が発生した場合、例外処理に遷移
            if self.error_info is not None:
                self.common_util.common_error_check(self.error_info)

            # 請求金額定義
            billing_amount = 0

            # 利用回数データ定義
            use_count_data = {
                "token": {
                    "successCount": 0,
                    "errorCount": 0,
                },
                "read": {
                    "successCount": 0,
                    "errorCount": 0,
                },
                "search": {
                    "successCount": 0,
                    "errorCount": 0,
                },
                "create": {
                    "successCount": 0,
                    "errorCount": 0,
                },
                "update": {
                    "successCount": 0,
                    "errorCount": 0,
                },
                "delete": {
                    "successCount": 0,
                    "errorCount": 0,
                },
                "multiDownload": {
                    "successCount": 0,
                    "errorCount": 0,
                },
                "multiDelete": {
                    "successCount": 0,
                    "errorCount": 0,
                },
                "searchClosed": {
                    "successCount": 0,
                    "errorCount": 0,
                }
            }

            # 「変数．API実行履歴取得結果リスト」の要素数分繰り返す
            for loop, api_history in enumerate(api_history_get_result_list["query_results"]):

                # 08.請求金額取得処理
                # 08-01.請求金額テーブルからデータを取得し、「変数．請求金額取得結果」に全レコードをタプルのリストとして格納する
                billing_get_result_list = common_db_connection_resource.select_tuple_list(
                    common_db_connection,
                    SqlConstClass.BILLING_SELECT_SQL,
                    api_history[0],
                    api_history[2]
                )
                # 08-02.処理が失敗した場合は、postgresqlエラー処理を実行する
                if not billing_get_result_list["result"]:
                    self.error_info = self.common_util.create_postgresql_log(
                        billing_get_result_list["errorObject"],
                        None,
                        None,
                        billing_get_result_list["stackTrace"]
                    ).get("errorInfo")

                # 09.共通エラーチェック処理
                # 09-01.以下の引数で共通エラーチェック処理を実行する
                # 09-02.例外が発生した場合、例外処理に遷移
                if self.error_info is not None:
                    self.common_util.common_error_check(self.error_info)

                # 10.累進請求金額計算処理
                charge_bill_list = billing_get_result_list["query_results"]
                # 10-01.累進請求金額計算処理を実行する
                # 10-02.レスポンスを、「変数．累進請求金額計算処理結果」に格納する
                progressive_billing_calculation_response = self.bill_util.progressive_billing_exec(api_history[0], api_history[1], api_history[2], charge_bill_list)

                # 11. 請求金額計算処理
                # 11-01. 「変数．請求金額」に「変数．累進請求金額計算処理結果．累進請求金額」を加算する
                billing_amount += progressive_billing_calculation_response["progressiveBilling"]

                # 12.PDS利用状況データ作成処理
                # 12-01	.「変数．PDS利用状況データ」に値を格納する
                # 12-01-01.格納条件に一致する場合、「変数．PDS利用状況データ．アクセストークン発行．成功」へ加算する
                if api_history[0] == apitypeConstClass.API_TYPE["ACCESS_TOKEN_ISSUE"] and api_history[1]:
                    use_count_data["token"]["successCount"] = api_history[2]
                # 12-01-02.格納条件に一致する場合、「変数．PDS利用状況データ．アクセストークン発行．失敗」へ加算する
                if api_history[0] == apitypeConstClass.API_TYPE["ACCESS_TOKEN_ISSUE"] and not api_history[1]:
                    use_count_data["token"]["errorCount"] = api_history[2]
                # 12-01-03.格納条件に一致する場合、「変数．PDS利用状況データ．登録．成功」へ加算する
                if api_history[0] == apitypeConstClass.API_TYPE["REGISTER"] and api_history[1]:
                    use_count_data["create"]["successCount"] = api_history[2]
                # 12-01-04.格納条件に一致する場合、「変数．PDS利用状況データ．登録．失敗」へ加算する
                if api_history[0] == apitypeConstClass.API_TYPE["REGISTER"] and not api_history[1]:
                    use_count_data["create"]["errorCount"] = api_history[2]
                # 12-01-05.格納条件に一致する場合、「変数．PDS利用状況データ．更新．成功」へ加算する
                if api_history[0] == apitypeConstClass.API_TYPE["UPDATE"] and api_history[1]:
                    use_count_data["update"]["successCount"] = api_history[2]
                # 12-01-06.格納条件に一致する場合、「変数．PDS利用状況データ．更新．失敗」へ加算する
                if api_history[0] == apitypeConstClass.API_TYPE["UPDATE"] and not api_history[1]:
                    use_count_data["update"]["errorCount"] = api_history[2]
                # 12-01-07.格納条件に一致する場合、「変数．PDS利用状況データ．参照．成功」へ加算する
                if api_history[0] == apitypeConstClass.API_TYPE["REFERENCE"] and api_history[1]:
                    use_count_data["read"]["successCount"] = api_history[2]
                # 12-01-08.格納条件に一致する場合、「変数．PDS利用状況データ．参照．失敗」へ加算する
                if api_history[0] == apitypeConstClass.API_TYPE["REFERENCE"] and not api_history[1]:
                    use_count_data["read"]["errorCount"] = api_history[2]
                # 12-01-09.格納条件に一致する場合、「変数．PDS利用状況データ．削除．成功」へ加算する
                if api_history[0] == apitypeConstClass.API_TYPE["DELETE"] and api_history[1]:
                    use_count_data["delete"]["successCount"] = api_history[2]
                # 12-01-10.格納条件に一致する場合、「変数．PDS利用状況データ．削除．失敗」へ加算する
                if api_history[0] == apitypeConstClass.API_TYPE["DELETE"] and not api_history[1]:
                    use_count_data["delete"]["errorCount"] = api_history[2]
                # 12-01-11.格納条件に一致する場合、「変数．PDS利用状況データ．検索．成功」へ加算する
                if api_history[0] == apitypeConstClass.API_TYPE["SEARCH"] and api_history[1]:
                    use_count_data["search"]["successCount"] = api_history[2]
                # 12-01-12.格納条件に一致する場合、「変数．PDS利用状況データ．検索．失敗」へ加算する
                if api_history[0] == apitypeConstClass.API_TYPE["SEARCH"] and not api_history[1]:
                    use_count_data["search"]["errorCount"] = api_history[2]
                # 12-01-13.格納条件に一致する場合、「変数．PDS利用状況データ．一括削除．成功」へ加算する
                if api_history[0] == apitypeConstClass.API_TYPE["BATCH_DELETE"] and api_history[1]:
                    use_count_data["multiDelete"]["successCount"] = api_history[2]
                # 12-01-14.格納条件に一致する場合、「変数．PDS利用状況データ．削除．失敗」へ加算する
                if api_history[0] == apitypeConstClass.API_TYPE["BATCH_DELETE"] and not api_history[1]:
                    use_count_data["multiDelete"]["errorCount"] = api_history[2]
                # 12-01-15.格納条件に一致する場合、「変数．PDS利用状況データ．一括DL．成功」へ加算する
                if api_history[0] == apitypeConstClass.API_TYPE["BATCH_DOWNLOAD"] and api_history[1]:
                    use_count_data["multiDownload"]["successCount"] = api_history[2]
                # 12-01-16.格納条件に一致する場合、「変数．PDS利用状況データ．一括DL．失敗」へ加算する
                if api_history[0] == apitypeConstClass.API_TYPE["BATCH_DOWNLOAD"] and not api_history[1]:
                    use_count_data["multiDownload"]["errorCount"] = api_history[2]
                # 12-01-17.格納条件に一致する場合、「変数．PDS利用状況データ．検索 (内部)．成功」へ加算する
                if api_history[0] == apitypeConstClass.API_TYPE["SEARCH_CLOSED"] and api_history[1]:
                    use_count_data["searchClosed"]["successCount"] = api_history[2]
                # 12-01-18.格納条件に一致する場合、「変数．PDS利用状況データ．検索 (内部)．失敗」へ加算する
                if api_history[0] == apitypeConstClass.API_TYPE["SEARCH_CLOSED"] and not api_history[1]:
                    use_count_data["searchClosed"]["errorCount"] = api_history[2]

            # 13.リソース請求金額計算処理
            # 13-01.リソース請求金額計算処理を実行する
            # 13-02.レスポンスを、「変数．リソース請求金額計算処理結果」に格納する
            resource_billing_calculation_response = self.bill_util.resource_billing_exec(request_body.pdsUserId, common_db_info_response)

            # 14.請求金額計算処理
            # 14-01.「変数．請求金額」に「変数．リソース請求金額計算処理結果．リソース請求金額」を加算する
            billing_amount += resource_billing_calculation_response["resourceBilling"]

            return {
                "billing_amount": billing_amount,
                "use_count_data": use_count_data
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
