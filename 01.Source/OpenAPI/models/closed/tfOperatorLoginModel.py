import traceback
# Const
from const.messageConst import MessageConstClass
from const.sqlConst import SqlConstClass
# Util
import util.logUtil as logUtil
from util.commonUtil import CommonUtilClass, get_str_date
from util.postgresDbUtil import PostgresDbUtilClass
from util.cryptoUtil import CryptUtilClass
# Exception
from exceptionClass.PDSException import PDSException


# 検索用 水野担当ファイル(完了)
class tfOperatorLoginClass():

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
        TFオペレータログインAPI メイン処理

        Returns:
            dict: 処理結果
        """
        try:
            # 03.パスワードのハッシュ化処理
            # 03-01.「リクエストのリクエストボディ.パスワード」をハッシュ化してハッシュ化済パスワードを作成する
            crypt_util_class = CryptUtilClass(self.logger)
            hashed_password = crypt_util_class.hash_password(request_body.tfOperatorPassword)

            # 04.共通DB接続準備処理
            # 04-01.AWS SecretsManagerから共通DB接続情報を取得して、「変数．共通DB接続情報」に格納する
            common_util = CommonUtilClass(self.logger)
            common_db_connection_resource: PostgresDbUtilClass = None
            # 04-02.「変数．共通DB接続情報」を利用して、共通DBに対してのコネクションを作成する
            common_db_info_response = common_util.get_common_db_info_and_connection()
            if not common_db_info_response["result"]:
                return common_db_info_response
            else:
                common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
                common_db_connection = common_db_info_response["common_db_connection"]

            # 05.TFオペレータ取得処理
            # 05-01.TFオペレータテーブルからデータを取得し、「変数.TFオペレータ取得結果」に1レコードをタプルとして格納する
            tf_operator_select_result = common_db_connection_resource.select_tuple_one(
                common_db_connection,
                SqlConstClass.TF_OPERATOR_LOGIN_SELECT_SQL,
                request_body.tfOperatorId,
                hashed_password,
                get_str_date()
            )
            # 05-02.「変数.TFオペレータ取得結果["rowcount"]」が1以外の場合、「変数.エラー情報」を作成する
            if tf_operator_select_result["result"] and tf_operator_select_result["rowcount"] != 1:
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020004"]["logMessage"], request_body.tfOperatorId))
                self.error_info = {
                    "errorCode": "010006",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["010006"]["message"])
                }
            # 05-03.処理が失敗した場合は「postgresqlエラー処理」からのレスポンスを、「変数．エラー情報」に格納する
            if not tf_operator_select_result["result"]:
                self.error_info = self.common_util.create_postgresql_log(
                    tf_operator_select_result["errorObject"],
                    None,
                    None,
                    tf_operator_select_result["stackTrace"]
                ).get("errorInfo")

            # 06.共通エラーチェック処理
            # 06-01.以下の引数で共通エラーチェック処理を実行する
            if self.error_info is not None:
                self.common_util.common_error_check(
                    self.error_info
                )

            return {
                "tfOperatorInfo": tf_operator_select_result["query_results"]
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
