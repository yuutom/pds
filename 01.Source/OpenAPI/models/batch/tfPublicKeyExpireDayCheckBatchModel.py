import base64
import traceback
# util
from util.postgresDbUtil import PostgresDbUtilClass
from util.kmsUtil import KmsUtilClass
from util.commonUtil import CommonUtilClass, get_str_date_in_X_days, get_uuid_no_hypen, get_str_datetime_in_X_days, get_str_date_in_one_years
import util.logUtil as logUtil
from util.fileUtil import NoHeaderOneItemCsvStringClass, CsvStreamClass
from util.callbackExecutorUtil import CallbackExecutor
# const
from const.messageConst import MessageConstClass
from const.sqlConst import SqlConstClass
from const.wbtConst import wbtConstClass
from const.fileNameConst import FileNameConstClass
# Exception
from exceptionClass.PDSException import PDSException


# 検索用 水野担当ファイル
class tfPublicKeyExpireDayCheckBatchModelClass():
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
        TF公開鍵有効期限確認バッチ メイン処理

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

            # 02. PDSユーザPDSユーザ公開鍵情報取得処理
            # 02-01. PDSユーザ、PDSユーザ公開鍵テーブルを結合したテーブルからデータを取得し、
            #       「変数．PDSユーザPDSユーザ公開鍵取得結果リスト」に全レコードをタプルのリストとして格納する
            pds_user_pds_user_public_key_get_result_list = common_db_connection_resource.select_tuple_list(
                common_db_connection,
                SqlConstClass.PDS_USER_PDS_USER_PUBLIC_KEY_SELECT_SQL,
                get_str_datetime_in_X_days(15)
            )
            # 02-02.処理が失敗した場合は、postgresqlエラー処理を実行する
            if not pds_user_pds_user_public_key_get_result_list["result"]:
                self.error_info = self.common_util.create_postgresql_log(
                    pds_user_pds_user_public_key_get_result_list["errorObject"],
                    None,
                    None,
                    pds_user_pds_user_public_key_get_result_list["stackTrace"]
                ).get("errorInfo")

            # 03.共通エラーチェック処理
            # 03-01.以下の引数で共通エラーチェック処理を実行する
            # 03-02.例外が発生した場合、例外処理に遷移
            if self.error_info is not None:
                self.common_util.common_error_check(self.error_info)

            # 「変数．PDSユーザ情報取得結果リスト」の要素数分繰り返す
            for loop, pds_user_pds_user_public_key in enumerate(pds_user_pds_user_public_key_get_result_list["query_results"]):

                # kmsUtilクラスオブジェクト作成
                kms_util = KmsUtilClass(self.logger)

                # 04.キーペア作成処理
                kms_error_info = None
                # 04-01.KMSからTF公開鍵、秘密鍵のキーペアを作成し、KMSIDを取得する
                # 04-02.「変数．KMSID」に保持する
                for _ in range(5):
                    kms_id = kms_util.create_pds_user_kms_key(pds_user_pds_user_public_key[1], pds_user_pds_user_public_key[2])
                    if kms_id:
                        break
                # 04-03.KMS登録処理に失敗した場合、「変数．エラー情報」を作成してエラーログをCloudWatchにログ出力する
                if not kms_id:
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990062"]["logMessage"]))
                    kms_error_info = {
                        "errorCode": "990062",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["990062"]["message"], "990062")
                    }

                # 05.共通エラーチェック処理
                # 05-01.以下の引数で共通エラーチェック処理を実行する
                # 05-02.例外が発生した場合、例外処理に遷移
                if kms_error_info is not None:
                    self.common_util.common_error_check(
                        kms_error_info
                    )

                # 06.キーペアレプリケート処理
                # 06-01.現在のリージョンとは別のリージョンにKMSIDをレプリケートする
                for i in range(5):
                    replicate_id = kms_util.replicate_pds_user_kms_key(kms_id, pds_user_pds_user_public_key[1], pds_user_pds_user_public_key[2])
                    if replicate_id:
                        break
                # 06-02.KMSレプリケート処理に失敗した場合、「変数．エラー情報」を作成してエラーログをCloudWatchにログ出力する
                if not replicate_id:
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990063"]["logMessage"]), kms_id)
                    kms_error_info = {
                        "errorCode": "990063",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["990063"]["message"], "990063")
                    }

                # 07.共通エラーチェック処理
                # 07-01.以下の引数で共通エラーチェック処理を実行する
                # 07-02.例外が発生した場合、例外処理に遷移
                if kms_error_info is not None:
                    # KMS削除処理
                    delete_kms_key = CallbackExecutor(
                        kms_util.delete_kms_key,
                        kms_id,
                        False
                    )
                    self.common_util.common_error_check(
                        kms_error_info,
                        delete_kms_key
                    )

                # 08.キーペア取得処理
                # 08-01.作成したキーペアから公開鍵を取得する
                for i in range(5):
                    public_key = kms_util.get_kms_public_key(kms_id)
                    if public_key:
                        break
                # 08-02.KMS公開鍵取得処理に失敗した場合、「変数．エラー情報」を作成してエラーログをCloudWatchにログ出力する
                if not public_key:
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990064"]["logMessage"]), kms_id)
                    kms_error_info = {
                        "errorCode": "990064",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["990064"]["message"], "990064")
                    }

                # 09.共通エラーチェック処理
                # 09-01.以下の引数で共通エラーチェック処理を実行する
                # 09-02.例外が発生した場合、例外処理に遷移
                if kms_error_info is not None:
                    # KMS削除処理
                    delete_kms_key = CallbackExecutor(
                        kms_util.delete_kms_key,
                        kms_id,
                        True
                    )
                    self.common_util.common_error_check(
                        kms_error_info,
                        delete_kms_key
                    )

                # 10.TF公開鍵通知ファイル作成処理
                # 10-01.取得した以下のデータをもとにCSVファイルを作成する
                public_key_string = base64.b64encode(public_key).decode()
                tf_public_key_csv_string = NoHeaderOneItemCsvStringClass([public_key_string])
                # 10-02.作成したCSVファイルを「変数.TF公開鍵通知ファイル」に格納する
                tf_public_key_csv_stream = CsvStreamClass(tf_public_key_csv_string)

                # 11.WBTメール件名作成処理
                # 11-01.UUID ( v4ハイフンなし) を作成する
                uuid = get_uuid_no_hypen()
                # 11-02.メール件名固定文字列と作成したUUIDを結合して、「変数．WBTメール件名」に保持する
                mail_title = wbtConstClass.TITLE["TF_PUBLIC_KEY_EXPIRE_DAY_CHECK"] + "【{}】".format(uuid)

                # 12. トランザクション作成
                # 12-01. 「PDSユーザ公開鍵トランザクション」を作成する

                # 13.PDSユーザ公開鍵テーブル登録処理
                # 13-01 PDSユーザ公開鍵テーブルに以下の登録内容で新規登録する
                pds_user_public_key_update_result = common_db_connection_resource.insert(
                    common_db_connection,
                    SqlConstClass.PDS_USER_KEY_INSERT_SQL,
                    pds_user_pds_user_public_key[1],
                    pds_user_pds_user_public_key[0] + 1,
                    None,
                    kms_id,
                    pds_user_pds_user_public_key[6],
                    get_str_date_in_one_years(),
                    None,
                    get_str_date_in_X_days(30),
                    False,
                    None,
                    mail_title,
                    True
                )
                # 13-02.処理が失敗した場合は、postgresqlエラー処理を実行する
                if not pds_user_public_key_update_result["result"]:
                    self.error_info = self.common_util.create_postgresql_log(
                        pds_user_public_key_update_result["errorObject"],
                        "PDSユーザ公開鍵インデックス",
                        pds_user_pds_user_public_key[0] + 1,
                        pds_user_public_key_update_result["stackTrace"]
                    ).get("errorInfo")

                # 14.共通エラーチェック処理
                # 14-01.以下の引数で共通エラーチェック処理を実行する
                if self.error_info is not None:
                    rollback_transaction = CallbackExecutor(
                        self.common_util.common_check_postgres_rollback,
                        common_db_connection,
                        common_db_connection_resource
                    )
                    delete_kms_key = CallbackExecutor(
                        kms_util.delete_kms_key,
                        kms_id,
                        True
                    )
                    self.common_util.common_error_check(
                        self.error_info,
                        delete_kms_key,
                        rollback_transaction
                    )

                # 15.WBT新規メール情報登録API実行処理
                # 15-01.WBT新規メール情報登録API呼び出し処理を実行する
                # 15-02.「新規メール情報登録API」からのレスポンスを、「変数．WBT新規メール情報登録API実行結果」に格納する
                wbt_mails_add_api_exec_result = common_util.wbt_mails_add_api_exec(
                    repositoryType=wbtConstClass.REPOSITORY_TYPE["ROUND"],
                    fileName=FileNameConstClass.TF_PUBLIC_KEY_NOTIFICATION + FileNameConstClass.TF_PUBLIC_KEY_NOTIFICATION_EXTENSION,
                    downloadDeadline=get_str_datetime_in_X_days(7),
                    replyDeadline=get_str_datetime_in_X_days(30),
                    comment=wbtConstClass.MESSAGE["TF_PUBLIC_KEY_EXPIRE_DAY_CHECK"],
                    mailAddressTo=pds_user_pds_user_public_key[3],
                    mailAddressCc=pds_user_pds_user_public_key[4],
                    title=mail_title
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
                    rollback_transaction = CallbackExecutor(
                        self.common_util.common_check_postgres_rollback,
                        common_db_connection,
                        common_db_connection_resource
                    )
                    delete_kms_key = CallbackExecutor(
                        kms_util.delete_kms_key,
                        kms_id,
                        True
                    )
                    self.common_util.common_error_check(
                        self.error_info,
                        rollback_transaction,
                        delete_kms_key
                    )

                # 17.WBTファイル登録API実行処理
                # 17-01.WBTファイル登録APIを呼び出す
                # 17-02.「ファイル登録API」からのレスポンスを、「変数．WBTファイル登録API実行結果」に格納する
                wbt_file_add_api_exec_result = common_util.wbt_file_add_api_exec(
                    mailId=wbt_mails_add_api_exec_result["id"],
                    fileId=wbt_mails_add_api_exec_result["attachedFiles"][0]["id"],
                    file=tf_public_key_csv_stream.get_temp_csv(),
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
                    rollback_transaction = CallbackExecutor(
                        self.common_util.common_check_postgres_rollback,
                        common_db_connection,
                        common_db_connection_resource
                    )
                    wbt_send_delete_api_exec = CallbackExecutor(
                        self.common_util.wbt_mail_cancel_exec,
                        wbt_mails_add_api_exec_result["id"]
                    )
                    delete_kms_key = CallbackExecutor(
                        kms_util.delete_kms_key,
                        kms_id,
                        True
                    )

                    self.common_util.common_error_check(
                        self.error_info,
                        rollback_transaction,
                        wbt_send_delete_api_exec,
                        delete_kms_key
                    )
                # 19.トランザクションコミット処理
                # 19-01.「PDSユーザ公開鍵トランザクション」をコミットする
                common_db_connection_resource.commit_transaction(common_db_connection)

                # 20.トランザクション作成
                # 20-01.「WBT送信メールIDトランザクション」を作成する

                # 21.WBT送信メールID更新処理
                # 21-01.PDSユーザ公開鍵テーブルを更新する
                pds_user_public_key_update_result = common_db_connection_resource.update(
                    common_db_connection,
                    SqlConstClass.PDS_USER_KEY_UPDATE_SQL,
                    wbt_mails_add_api_exec_result["id"],
                    pds_user_pds_user_public_key[1],
                    pds_user_pds_user_public_key[0] + 1
                )
                # 21-02.処理が失敗した場合は、postgresqlエラー処理を実行する
                if not pds_user_public_key_update_result["result"]:
                    self.error_info = self.common_util.create_postgresql_log(
                        pds_user_public_key_update_result["errorObject"],
                        None,
                        None,
                        pds_user_public_key_update_result["stackTrace"]
                    ).get("errorInfo")

                # 22.共通エラーチェック処理
                # 22-01.以下の引数で共通エラーチェック処理を実行する
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

                # 23.トランザクションコミット処理
                # 23-01.「WBT送信メールIDトランザクション」をコミットする
                common_db_connection_resource.commit_transaction(common_db_connection)

                # 24. TF公開鍵通知ファイル削除処理
                # 24-01.「変数.TF公開鍵通知ファイル」をNullにする
                tf_public_key_csv_string = None
                tf_public_key_csv_stream = None

            # コネクションを切断する
            common_db_connection_resource.close_connection(common_db_connection)

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
