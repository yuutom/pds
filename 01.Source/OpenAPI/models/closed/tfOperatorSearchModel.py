import traceback

# Const
from const.messageConst import MessageConstClass
from const.sqlConst import SqlConstClass

# Util
import util.logUtil as logUtil
from util.commonUtil import CommonUtilClass
from util.postgresDbUtil import PostgresDbUtilClass

# Exception
from exceptionClass.PDSException import PDSException


class tfOperatorSearchClass():
    def __init__(self, logger):
        """
        コンストラクタ

        Args:
            logger (Logger): ロガー（TRACE）
        """
        self.logger = logger
        self.common_util = CommonUtilClass(logger)

    def main(self):
        """
        TFオペレータ検索・参照API メイン処理

        Returns:
            dict: 処理結果
        """
        try:
            # 05.共通DB接続準備処理
            # 05-01.共通DB接続情報取得処理
            common_util = CommonUtilClass(self.logger)
            common_db_connection_resource: PostgresDbUtilClass = None
            # 05-01-01.AWS SecretsManagerから共通DB接続情報を取得して、「変数．共通DB接続情報」に格納する
            # 05-02.「変数．共通DB接続情報」を利用して、共通DBに対してのコネクションを作成する
            common_db_info_response = common_util.get_common_db_info_and_connection()
            if not common_db_info_response["result"]:
                return common_db_info_response
            else:
                common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
                common_db_connection = common_db_info_response["common_db_connection"]

            # 06.TFオペレータ全件検索処理
            tf_operator_select_error_info = None
            # 06-01.TFオペレータテーブルからデータを取得し、「変数.TFオペレータ取得結果リスト」に全レコードをタプルのリストとして格納する
            tf_operator_select_result = common_db_connection_resource.select_tuple_list(
                common_db_connection,
                SqlConstClass.TF_OPERATOR_SELECT_SQL
            )
            # 06-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not tf_operator_select_result["result"]:
                tf_operator_select_error_info = self.common_util.create_postgresql_log(
                    tf_operator_select_result["errorObject"],
                    None,
                    None,
                    tf_operator_select_result["stackTrace"]
                ).get("errorInfo")

            # 07.共通エラーチェック処理
            # 07-01.以下の引数で共通エラーチェック処理を実行する
            # 07-02 例外が発生した場合、例外処理に遷移
            if tf_operator_select_error_info is not None:
                self.common_util.common_error_check(tf_operator_select_error_info["errorInfo"])

            tf_operator_info_list = []
            tf_operator_column_list = [
                "tfOperatorId",
                "tfOperatorName",
                "tfOperatorStatus",
                "tfOperatorMail"
            ]
            for tf_operator_loop, tf_operator_info in enumerate(tf_operator_select_result["query_results"]):
                tf_operator_dict = {column: data for column, data in zip(tf_operator_column_list, tf_operator_info)}
                tf_operator_info_list.append(tf_operator_dict)

            # 08.TFオペレータ無効化フラグ反転処理
            # 08-01.「変数．TFオペレータ取得結果リスト[2]」のブール値を反転させ、「変数．TFオペレータ有効状態」に格納する
            for tf_operator_valid_loop, tf_operator_select_element in enumerate(tf_operator_select_result["query_results"]):
                tf_operator_valid_flg = not tf_operator_select_element[2]
                # 08-02.「変数．TFオペレータ有効状態」を「変数．TFオペレータ取得結果リスト[2]」に格納する
                tf_operator_info_list[tf_operator_valid_loop]["tfOperatorStatus"] = tf_operator_valid_flg

            return {
                "tfOperatorInfo": tf_operator_info_list
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
