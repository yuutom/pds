from typing import Optional
import traceback

# RequestBody
from pydantic import BaseModel

# Util
from util.commonUtil import CommonUtilClass
from util.postgresDbUtil import PostgresDbUtilClass
import util.logUtil as logUtil
from const.messageConst import MessageConstClass
from const.sqlConst import SqlConstClass
from const.apitypeConst import apitypeConstClass

# Exception
from exceptionClass.PDSException import PDSException


class requestBody(BaseModel):
    """
    リクエストボディクラス

    Args:
        BaseModel (Object): Pydanticのベースクラス
    """
    pdsUserId: Optional[str] = None
    fromDate: Optional[str] = None
    toDate: Optional[str] = None
    # apiType: Optional[str] = None


class pdsUserGetAccessRecordClass():

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
        PDSユーザアクセス記録閲覧API メイン処理

        Returns:
            dict: 処理結果
        """
        try:
            # 05.共通DB接続準備処理
            # 05-01.共通DB接続情報取得処理
            common_db_connection_resource: PostgresDbUtilClass = None
            # 05-01-01.AWS SecretsManagerから共通DB接続情報を取得して、「変数．共通DB接続情報」に格納する
            # 05-02.「変数．共通DB接続情報」を利用して、共通DBに対してのコネクションを作成する
            common_db_info_response = self.common_util.get_common_db_info_and_connection()
            if not common_db_info_response["result"]:
                return common_db_info_response
            else:
                common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
                common_db_connection = common_db_info_response["common_db_connection"]

            # 06.PDS利用状況取得処理
            pds_user_usage_situation_info = None
            # 06-01.API実行履歴テーブルからデータを取得し、「変数.PDS利用状況取得結果リスト」に全レコードをタプルのリストとして格納する
            pds_user_usage_situation_list = common_db_connection_resource.select_tuple_list(
                common_db_connection,
                SqlConstClass.PDS_USER_USAGE_SITUATION_SQL,
                request_body.pdsUserId,
                request_body.fromDate,
                request_body.toDate
            )
            # 06-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not pds_user_usage_situation_list["result"]:
                pds_user_usage_situation_info = self.common_util.create_postgresql_log(
                    pds_user_usage_situation_list["errorObject"],
                    None,
                    None,
                    pds_user_usage_situation_list["stackTrace"]
                ).get("errorInfo")

            # 07.共通エラーチェック処理
            # 07-01.以下の引数で共通エラーチェック処理を実行する
            # 07-02.例外が発生した場合、例外処理に遷移
            if pds_user_usage_situation_info is not None:
                self.common_util.common_error_check(pds_user_usage_situation_info)

            # 「変数．PDS利用状況情報リスト」の定義
            pds_usage_situation_info_list = []

            # 08.API種別合計カウント初期化処理
            api_type_count = {}
            # 08-01.「変数．API種別合計カウント」を作成する
            api_type_count["token"] = 0
            api_type_count["read"] = 0
            api_type_count["search"] = 0
            api_type_count["create"] = 0
            api_type_count["update"] = 0
            api_type_count["delete"] = 0
            api_type_count["multiDownload"] = 0
            api_type_count["multiDelete"] = 0
            api_type_count["searchClosed"] = 0

            # 「変数．PDS利用状況取得結果リスト」の要素数分繰り返す
            for pds_usage_situation_loop, usage_situation_api_type in enumerate(pds_user_usage_situation_list.get("query_results")):
                # 09.PDS利用状況情報作成処理
                pds_usage_situation = {}
                # 09-01.「変数．PDS利用状況情報」内に以下の値を格納する
                pds_usage_situation["apiUseDate"] = usage_situation_api_type[0].strftime('%Y/%m/%d %H:%M:%S.%f')[:23]
                pds_usage_situation["apiUsePdsUserId"] = usage_situation_api_type[1]
                pds_usage_situation["apiType"] = usage_situation_api_type[2]
                pds_usage_situation["apiParam"] = usage_situation_api_type[3]
                if usage_situation_api_type[4]:
                    pds_usage_situation["apiResult"] = "OK"
                else:
                    pds_usage_situation["apiResult"] = "NG"
                # 09-02.「変数．PDS利用状況情報リスト」に「変数．PDS利用状況情報」を追加する
                pds_usage_situation_info_list.append(pds_usage_situation)

                # 10.API種別合計カウント加算処理
                # 10-01.格納条件に応じたデータの「変数．API種別合計カウント」のそれぞれの値を加算する
                # 10-01-01.格納条件に一致する場合、「変数．API種別合計カウント．アクセストークン発行」への加算
                if usage_situation_api_type[2] == apitypeConstClass.API_TYPE['ACCESS_TOKEN_ISSUE']:
                    api_type_count["token"] += 1
                # 10-01-02.格納条件に一致する場合、「変数．API種別合計カウント．登録」への加算
                elif usage_situation_api_type[2] == apitypeConstClass.API_TYPE['REGISTER']:
                    api_type_count["create"] += 1
                # 10-01-03.格納条件に一致する場合、「変数．API種別合計カウント．更新」への加算
                elif usage_situation_api_type[2] == apitypeConstClass.API_TYPE['UPDATE']:
                    api_type_count["update"] += 1
                # 10-01-04.格納条件に一致する場合、「変数．API種別合計カウント．参照」への加算
                elif usage_situation_api_type[2] == apitypeConstClass.API_TYPE['REFERENCE']:
                    api_type_count["read"] += 1
                # 10-01-05.格納条件に一致する場合、「変数．API種別合計カウント．削除」への加算
                elif usage_situation_api_type[2] == apitypeConstClass.API_TYPE['DELETE']:
                    api_type_count["delete"] += 1
                # 10-01-06.格納条件に一致する場合、「変数．API種別合計カウント．検索」への加算
                elif usage_situation_api_type[2] == apitypeConstClass.API_TYPE['SEARCH']:
                    api_type_count["search"] += 1
                # 10-01-07.格納条件に一致する場合、「変数．API種別合計カウント．一括削除」への加算
                elif usage_situation_api_type[2] == apitypeConstClass.API_TYPE['BATCH_DELETE']:
                    api_type_count["multiDelete"] += 1
                # 10-01-08.格納条件に一致する場合、「変数．API種別合計カウント．一括DL」への加算
                elif usage_situation_api_type[2] == apitypeConstClass.API_TYPE['BATCH_DOWNLOAD']:
                    api_type_count["multiDownload"] += 1
                # 10-01-09.格納条件に一致する場合、「変数．API種別合計カウント．検索 (内部)」への加算
                elif usage_situation_api_type[2] == apitypeConstClass.API_TYPE['SEARCH_CLOSED']:
                    api_type_count["searchClosed"] += 1
            return {
                "result": True,
                "pds_usage_situation_info": pds_usage_situation_info_list,
                "api_type_total_count": api_type_count
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
