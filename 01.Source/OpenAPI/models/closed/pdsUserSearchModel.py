import traceback
from typing import Any, Optional

# RequestBody
from pydantic import BaseModel
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
    pdsUser: Optional[Any] = None
    fromDate: Optional[Any] = None
    toDate: Optional[Any] = None
    pdsUserStatus: Optional[Any] = None


class pdsUserSearchModelClass():
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
        PDSユーザ検索・参照API メイン処理

        Args:
            request_body (requestBody): リクエストボディ
        Raises:
            e: 例外処理
            PDSException: PDS例外処理

        Returns:
            dict: 処理結果
        """
        try:
            # 05.共通DB接続準備処理
            # 05-01.共通DB接続情報取得処理
            common_db_connection_resource: PostgresDbUtilClass = None
            # 05-01-01.AWS SecretsManagerから共通DB接続情報を取得して、変数．共通DB接続情報に格納する
            # 05-01-02.「変数．共通DB接続情報」を利用して、共通DBに対してのコネクションを作成する
            common_db_info_response = self.common_util.get_common_db_info_and_connection()
            if not common_db_info_response["result"]:
                return common_db_info_response
            else:
                common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
                common_db_connection = common_db_info_response["common_db_connection"]

            # 06.PDSユーザ検索処理
            pds_user_exist_error_info = None
            # 06-01.PDSユーザテーブルとPDSユーザ公開鍵テーブルからデータを取得し、「変数．PDSユーザ取得結果リスト」に全レコードをタプルのリストとして格納する
            param_list = []
            select_items_list = []
            is_exist_pds_user: bool = False
            if request_body.pdsUser is not None and request_body.pdsUser != "":
                is_exist_pds_user = True
            is_exist_from_date: bool = False
            if request_body.fromDate is not None and request_body.fromDate != "":
                is_exist_from_date = True
            is_exist_to_date: bool = False
            if request_body.toDate is not None and request_body.toDate != "":
                is_exist_to_date = True
            is_exist_pds_user_status: bool = False
            if request_body.pdsUserStatus is not None and request_body.pdsUserStatus != "":
                is_exist_pds_user_status = True

            if is_exist_pds_user or is_exist_from_date or is_exist_to_date or is_exist_pds_user_status:
                select_items_list.append(" WHERE")

                if is_exist_pds_user:
                    select_items_list.append("     (")
                    select_items_list.append("         m_pds_user.pds_user_id = %s")
                    select_items_list.append("         OR m_pds_user.pds_user_name = %s")
                    select_items_list.append("     )")
                    param_list.append(request_body.pdsUser)
                    param_list.append(request_body.pdsUser)
                    if is_exist_from_date or is_exist_to_date or is_exist_pds_user_status:
                        # 後続の条件が存在する場合、and句を付与
                        select_items_list.append("     AND")

                if is_exist_from_date:
                    select_items_list.append("         m_pds_user_key.start_date <= %s")
                    param_list.append(request_body.fromDate)
                    if is_exist_to_date or is_exist_pds_user_status:
                        # 後続の条件が存在する場合、and句を付与
                        select_items_list.append("     AND")

                if is_exist_to_date:
                    select_items_list.append("         (")
                    select_items_list.append("         (")
                    select_items_list.append("             m_pds_user_key.end_date IS NOT NULL")
                    select_items_list.append("             AND m_pds_user_key.end_date >= %s")
                    select_items_list.append("         )")
                    select_items_list.append("         OR (")
                    select_items_list.append("             m_pds_user_key.end_date IS NULL")
                    select_items_list.append("             AND m_pds_user_key.update_date >= %s")
                    select_items_list.append("         )")
                    select_items_list.append("     )")
                    param_list.append(request_body.toDate)
                    param_list.append(request_body.toDate)
                    if is_exist_pds_user_status:
                        # 後続の条件が存在する場合、and句を付与
                        select_items_list.append("     AND")

                if is_exist_pds_user_status:
                    select_items_list.append("         m_pds_user_key.valid_flg = %s")
                    param_list.append(request_body.pdsUserStatus)

            if len(select_items_list) > 0:
                select_items_sql = ''.join(select_items_list)
                sql = SqlConstClass.PDS_USER_SEARCH_SELECT_SQL + select_items_sql + ";"
            else:
                sql = SqlConstClass.PDS_USER_SEARCH_SELECT_SQL + ";"

            pds_user_search_list = common_db_connection_resource.select_tuple_list(
                common_db_connection,
                sql,
                *param_list
            )
            # 06-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not pds_user_search_list["result"]:
                pds_user_exist_error_info = self.common_util.create_postgresql_log(
                    pds_user_search_list["errorObject"],
                    None,
                    None,
                    pds_user_search_list["stackTrace"]
                ).get("errorInfo")

            # 07.共通エラーチェック処理
            # 07-01.以下の引数で共通エラーチェック処理を実行する
            # 07-02.例外が発生した場合、例外処理に遷移
            if pds_user_exist_error_info is not None:
                self.common_util.common_error_check(pds_user_exist_error_info)

            # 08.PDSユーザ情報作成処理
            # 08-01.「変数．PDSユーザ情報」に「変数．PDSユーザ取得結果リスト」を格納する
            # 返却するpdsUserInfoをtupleからdictに変換する
            pds_user_search_column_list = [
                'pdsUserId',
                'pdsUserName',
                'apiKey',
                'pdsUserPublicKeyIdx',
                'pdsUserStatus',
                'pdsUserPublicKeyStartDate',
                'pdsUserPublicKeyExpectedDate',
                'pdsUserPublicKeyEndDate',
                'tfContactAddress',
                'multiDownloadFileSendAddressTo',
                'multiDownloadFileSendAddressCc',
                'multiDeleteFileSendAddressTo',
                'multiDeleteFileSendAddressCc'
            ]
            pds_user_search_data_list = pds_user_search_list["query_results"]
            # datetime型の要素を文字列型に変換する(データが存在する場合)
            for pds_user_search_data_loop, pds_user_search_element in enumerate(pds_user_search_list["query_results"]):
                pds_user_search_element_list = list(pds_user_search_element)
                if pds_user_search_element[5] is not None:
                    # start_date
                    start_date = str(pds_user_search_element[5])
                    pds_user_search_element_list[5] = start_date
                if pds_user_search_element[6] is not None:
                    # update_date
                    update_date = str(pds_user_search_element[6])
                    pds_user_search_element_list[6] = update_date
                if pds_user_search_element[7] is not None:
                    # end_date
                    end_date = str(pds_user_search_element[7])
                    pds_user_search_element_list[7] = end_date
                pds_user_search_list["query_results"][pds_user_search_data_loop] = tuple(pds_user_search_element_list)

            pds_user_info_dict = [dict(zip(pds_user_search_column_list, data_list)) for data_list in pds_user_search_data_list]

            # 不要になったリソースの片付け
            self.common_util = None

            return {
                "pdsUserInfo": pds_user_info_dict
            }

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
