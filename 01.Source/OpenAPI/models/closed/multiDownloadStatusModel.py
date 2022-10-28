import traceback
# import requests
# util
from util.commonUtil import CommonUtilClass
from util.postgresDbUtil import PostgresDbUtilClass
from util.commonUtil import get_str_datetime_in_X_month
import util.logUtil as logUtil
# const
from const.messageConst import MessageConstClass
from const.sqlConst import SqlConstClass
from const.multiDownloadStatusConst import multiDownloadStatusConst
# Exception
from exceptionClass.PDSException import PDSException


# 検索用 水野担当ファイル
class multiDownloadStatusClass():
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
        個人情報一括DL状況確認API メイン処理

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

            # 06.個人情報一括DL状態管理取得処理
            # 06-01.個人情報一括DL状態管理テーブルからデータを取得し、「変数．個人情報一括DL状態管理取得結果リスト」に全レコードをタプルのリストとして格納する
            multi_download_status_result_list = common_db_connection_resource.select_tuple_list(
                common_db_connection,
                SqlConstClass.MULTI_DOWUNLOAD_STATUS_UNION_SELECT_SQL,
                request_body.pdsUserId,
                get_str_datetime_in_X_month(-6),
                request_body.pdsUserId
            )
            # 06-02.処理が失敗した場合は「postgresqlエラー処理」からのレスポンスを、「変数．エラー情報」に格納する
            if not multi_download_status_result_list["result"]:
                self.error_info = self.common_util.create_postgresql_log(
                    multi_download_status_result_list["errorObject"],
                    None,
                    None,
                    multi_download_status_result_list["stackTrace"]
                ).get("errorInfo")

            # 07.共通エラーチェック処理
            # 07-01.以下の引数で共通エラーチェック処理を実行する
            if self.error_info is not None:
                self.common_util.common_error_check(self.error_info)

            # 個人情報一括ダウンロード情報リスト定義
            multi_download_info_list = []

            # 「変数．個人情報一括DL状態管理取得結果リスト」の要素数分繰り返す
            for loop, multi_download_status in enumerate(multi_download_status_result_list["query_results"]):

                # 08.実行ステータスチェック処理
                # 08-01.「変数．個人情報一括DL状態管理取得結果リスト[変数．WBTループ数][1]」が2ではない場合、「09. 個人情報一括ダウンロード情報作成処理」に遷移する
                if multi_download_status[1] != multiDownloadStatusConst.MULTI_Download_STATUS["STATUS_CODE"]["WBT_PROCESSING"]:

                    # 09. 個人情報一括ダウンロード情報作成処理
                    # 09-01.「変数．実行ステータス」に格納する
                    if multi_download_status[1] == multiDownloadStatusConst.MULTI_Download_STATUS["STATUS_CODE"]["DATA_EXTRACTION"]:
                        exec_status = multiDownloadStatusConst.MULTI_Download_STATUS["STATUS_NAME"]["DATA_EXTRACTION"]
                    elif multi_download_status[1] == multiDownloadStatusConst.MULTI_Download_STATUS["STATUS_CODE"]["FINISHED"]:
                        exec_status = multiDownloadStatusConst.MULTI_Download_STATUS["STATUS_NAME"]["FINISHED"]
                    elif multi_download_status[1] == multiDownloadStatusConst.MULTI_Download_STATUS["STATUS_CODE"]["ERROR"]:
                        exec_status = multiDownloadStatusConst.MULTI_Download_STATUS["STATUS_NAME"]["ERROR"]
                    # 09-02.「変数．個人情報一括ダウンロード情報」に値を格納する
                    multi_download_info = {
                        'executionStartDate': multi_download_status[3].strftime('%Y/%m/%d'),
                        'inquiryId': multi_download_status[0],
                        'downloadStatus': exec_status,
                        'executionEndDate': multi_download_status[4].strftime('%Y/%m/%d')
                    }

                # 08-02.「変数．個人情報一括DL状態管理取得結果リスト[変数．WBTループ数][1]」が2の場合、「10. WBTのタスク結果取得API実行処理」に遷移する
                elif multi_download_status[1] == multiDownloadStatusConst.MULTI_Download_STATUS["STATUS_CODE"]["WBT_PROCESSING"]:

                    # 10.WBTのタスク結果取得API実行処理
                    # mail_id = multi_download_status[2]
                    # URI = "https://wb-transfer.toppan-f.co.jp/info/ja/api/sdms/mails/history/{}".format(mail_id)
                    # 10-01.WBTのタスク結果取得APIを呼び出し処理を実行する
                    # 10-02.タスク結果取得APIからのレスポンスを、「変数．タスク結果取得API実行結果」に格納する
                    # wbt_get_task_response = requests.get(URI)
                    # TODO: 動作確認 & Flake8に対応するため残しています
                    wbt_get_task_response = {
                        "result": True,
                        "exec_status": "PROCESSING"
                    }
                    # 10-03.処理が失敗した場合は「変数．エラー情報」を作成し、エラーログをCloudWatchにログ出力する
                    if not wbt_get_task_response["result"]:
                        self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990018"]["logMessage"]))
                        self.error_info = {
                            "errorCode": "990018",
                            "message": logUtil.message_build(MessageConstClass.ERRORS["990018"]["message"], "990018")
                        }

                    # 11.共通エラーチェック処理
                    # 11-01.以下の引数で共通エラーチェック処理を実行する
                    if self.error_info is not None:
                        self.common_util.common_error_check(self.error_info)

                    # 12.個人情報一括ダウンロード情報作成処理
                    # 12-01.「変数．実行ステータス」に値を納する
                    if wbt_get_task_response["exec_status"] == multiDownloadStatusConst.WBT_STATUS["STATUS_CODE"]["PROCESSING"]:
                        exec_status = multiDownloadStatusConst.WBT_STATUS["STATUS_NAME"]["PROCESSING"]
                    elif wbt_get_task_response["exec_status"] == multiDownloadStatusConst.WBT_STATUS["STATUS_CODE"]["FINISHED"]:
                        exec_status = multiDownloadStatusConst.WBT_STATUS["STATUS_NAME"]["FINISHED"]
                    elif wbt_get_task_response["exec_status"] == multiDownloadStatusConst.WBT_STATUS["STATUS_CODE"]["ERROR_HAPPEND"]:
                        exec_status = multiDownloadStatusConst.WBT_STATUS["STATUS_NAME"]["ERROR_HAPPEND"]
                    # 12-02.「変数．個人情報一括ダウンロード情報」に値を格納する
                    multi_download_info = {
                        'executionStartDate': multi_download_status[3].strftime('%Y/%m/%d'),
                        'inquiryId': multi_download_status[0],
                        'downloadStatus': exec_status,
                        'executionEndDate': multi_download_status[4].strftime('%Y/%m/%d')
                    }

                # 13.個人情報一括ダウンロード情報リスト追加処理
                # 13-01.「変数．個人情報一括ダウンロード情報リスト」に「変数．個人情報一括ダウンロード情報」を追加する
                multi_download_info_list.append(multi_download_info)

            return {
                "multi_download_info_list": multi_download_info_list
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
