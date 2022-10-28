import base64
import traceback
from typing import Optional

# RequestBody
from pydantic import BaseModel
from util.callbackExecutorUtil import CallbackExecutor

# Util
from util.commonUtil import CommonUtilClass
from util.postgresDbUtil import PostgresDbUtilClass
from util.kmsUtil import KmsUtilClass
import util.commonUtil as commonUtil
import util.logUtil as logUtil
from util.fileUtil import NoHeaderOneItemCsvStringClass, CsvStreamClass
from const.wbtConst import wbtConstClass
from const.messageConst import MessageConstClass
from const.sqlConst import SqlConstClass
from const.fileNameConst import FileNameConstClass

# Exception
from exceptionClass.PDSException import PDSException


class requestBody(BaseModel):
    """
    リクエストボディクラス

    Args:
        BaseModel (Object): Pydanticのベースクラス
    """
    pdsUserId: Optional[str] = None
    pdsUserPublicKeyIdx: Optional[int] = None
    pdsUserPublicKeyEndDate: Optional[str] = None


class pdsUserAuthInfoCreateModelClass():

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
        PDSユーザ認証情報発行API メイン処理

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

            # 06.PDSユーザ取得処理
            pds_user_info = None
            # 06-01.PDSユーザテーブルからデータを取得し、「変数．PDSユーザ取得結果」に1レコードをタプルとして格納する
            pds_user_result = common_db_connection_resource.select_tuple_one(
                common_db_connection,
                SqlConstClass.PDS_USER_AUTH_CREATE_SELECT_SQL,
                request_body.pdsUserId
            )
            # 06-02.「変数．PDSユーザ取得結果」が0件の場合、「変数．エラー情報」を作成する
            if pds_user_result["result"] and pds_user_result["rowcount"] == 0:
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020004"]["logMessage"], request_body.pdsUserId))
                pds_user_info = {
                    "errorCode": "020004",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020004"]["message"], request_body.pdsUserId)
                }
            # 06-03.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not pds_user_result["result"]:
                pds_user_info = self.common_util.create_postgresql_log(
                    pds_user_result["errorObject"],
                    None,
                    None,
                    pds_user_result["stackTrace"]
                ).get("errorInfo")

            # 07.PDSユーザ整合性検証処理
            # 07-01.「変数．PDSユーザ取得結果」で取得した情報のデータチェックを実施する
            # 07-01-01.「変数．PDSユーザ取得結果」が0件以外で「変数PDSユーザ取得結果[1]」が無効の場合、「変数．エラー情報」にエラー情報を作成し、エラー情報をCloudWatchへログ出力する
            if pds_user_result["result"] and pds_user_result["rowcount"] != 0 and not pds_user_result["query_results"][1]:
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["030009"]["logMessage"]))
                pds_user_info = {
                    "errorCode": "030009",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["030009"]["message"])
                }

            # 08.共通エラーチェック処理
            # 08-01.以下の引数で共通エラーチェック処理を実行する
            # 08-02.例外が発生した場合、例外処理に遷移
            if pds_user_info is not None:
                self.common_util.common_error_check(pds_user_info)

            # 09.PDSユーザ公開鍵インデックス最大値取得処理
            pds_auth_max_index_info = None
            # 09-01.PDSユーザ公開鍵テーブルからデータを取得し、「変数．PDSユーザ公開鍵取得結果」に1レコードをタプルとして格納する
            pds_auth_max_index_result = common_db_connection_resource.select_tuple_one(
                common_db_connection,
                SqlConstClass.PDS_USER_AUTH_CREATE_MAX_INDEX_SELECT_SQL,
                request_body.pdsUserId
            )
            # 09-02.「変数．PDSユーザ公開鍵取得結果」が0件の場合、「変数．エラー情報」にエラー情報を作成する
            if pds_auth_max_index_result["result"] and pds_auth_max_index_result["query_results"][0] is None:
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020004"]["logMessage"], request_body.pdsUserId))
                pds_auth_max_index_info = {
                    "errorCode": "020004",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020004"]["message"], request_body.pdsUserId)
                }
            # 09-03.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not pds_auth_max_index_result["result"]:
                pds_auth_max_index_info = self.common_util.create_postgresql_log(
                    pds_auth_max_index_result["errorObject"],
                    None,
                    None,
                    pds_auth_max_index_result["stackTrace"]
                ).get("errorInfo")

            # 10.共通エラーチェック処理
            # 10-01.以下の引数で共通エラーチェック処理を実行する
            # 10-02.例外が発生した場合、例外処理に遷移
            if pds_auth_max_index_info is not None:
                self.common_util.common_error_check(pds_auth_max_index_info)

            # 11.キーペア作成処理
            kms_util = KmsUtilClass(self.logger)
            kms_error_info = None
            # 11-01.KMSからTF公開鍵、秘密鍵のキーペアを作成し、KMSIDを取得する
            # 11-02.「変数．KMSID」に保持する
            for i in range(5):
                kms_id = kms_util.create_pds_user_kms_key(request_body.pdsUserId, pds_user_result["query_results"][0])
                if kms_id:
                    break
            # 11-03.KMS登録処理に失敗した場合、「変数．エラー情報」を作成してエラーログをCloudWatchにログ出力する
            if not kms_id:
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990062"]["logMessage"]))
                kms_error_info = {
                    "errorCode": "990062",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["990062"]["message"], "990062")
                }

            # 12.共通エラーチェック処理
            # 12-01.以下の引数で共通エラーチェック処理を実行する
            # 12-02.例外が発生した場合、例外処理に遷移
            if kms_error_info is not None:
                self.common_util.common_error_check(
                    kms_error_info
                )

            # 13.キーペアレプリケート処理
            # 13-01.現在のリージョンとは別のリージョンにKMSIDをレプリケートする
            for i in range(5):
                replicate_id = kms_util.replicate_pds_user_kms_key(kms_id, request_body.pdsUserId, pds_user_result["query_results"][0])
                if replicate_id:
                    break
            # 13-02.KMSレプリケート処理に失敗した場合、「変数．エラー情報」を作成してエラーログをCloudWatchにログ出力する
            if not replicate_id:
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990063"]["logMessage"], kms_id))
                kms_error_info = {
                    "errorCode": "990063",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["990063"]["message"], "990063")
                }

            # 14.共通エラーチェック処理
            # 14-01.以下の引数で共通エラーチェック処理を実行する
            # 14-02.例外が発生した場合、例外処理に遷移
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

            # 15.キーペア取得処理
            # 15-01.作成したキーペアから公開鍵を取得する
            for i in range(5):
                public_key = kms_util.get_kms_public_key(kms_id)
                if public_key:
                    break
            # 15-02.KMS公開鍵取得処理に失敗した場合、「変数．エラー情報」を作成してエラーログをCloudWatchにログ出力する
            if not public_key:
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["990064"]["logMessage"], kms_id))
                kms_error_info = {
                    "errorCode": "990064",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["990064"]["message"], "990064")
                }

            # 16.共通エラーチェック処理
            # 16-01.以下の引数で共通エラーチェック処理を実行する
            # 16-02.例外が発生した場合、例外処理に遷移
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

            # 17.TF公開鍵通知ファイル作成処理
            # 17-01.取得した以下のデータをもとにCSVファイルを作成する
            public_key_string = base64.b64encode(public_key).decode()
            tf_public_key_csv_string = NoHeaderOneItemCsvStringClass([public_key_string])
            # 17-02.作成したCSVファイルを「変数.TF公開鍵通知ファイル」に格納する
            tf_public_key_csv_stream = CsvStreamClass(tf_public_key_csv_string)

            # 18.WBTメール件名作成処理
            # 18-01.UUID ( v4ハイフンなし) を作成する
            mail_uuid = commonUtil.get_uuid_no_hypen()
            # 18-02.メール件名固定文字列と作成したUUIDを結合して、「変数．WBTメール件名」に保持する
            wbt_mail_subject = wbtConstClass.TITLE['PDS_USER_CREATE'] + "【{}】".format(mail_uuid)

            # 19.トランザクション作成処理
            # 19-01.「PDSユーザ認証情報発行トランザクション」を作成する

            # 20.PDSユーザ公開鍵登録処理
            pds_user_key_insert_error_info = None
            # 20-01.PDSユーザ公開鍵テーブルに登録する
            pds_user_key_insert_result = common_db_connection_resource.insert(
                common_db_connection,
                SqlConstClass.PDS_USER_KEY_INSERT_SQL,
                request_body.pdsUserId,
                pds_auth_max_index_result["query_results"][0] + 1,
                None,
                kms_id,
                commonUtil.get_str_date(),
                commonUtil.get_str_date_in_one_years(),
                None,
                commonUtil.get_str_date_in_X_days(30),
                False,
                None,
                wbt_mail_subject,
                True
            )
            # 20-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not pds_user_key_insert_result["result"]:
                pds_user_key_insert_error_info = self.common_util.create_postgresql_log(
                    pds_user_key_insert_result["errorObject"],
                    "PDSユーザID",
                    request_body.pdsUserId,
                    pds_user_key_insert_result["stackTrace"]
                ).get("errorInfo")

            # 21.共通エラーチェック処理
            # 21-01.以下の引数で共通エラーチェック処理を実行する
            # 21-02.例外が発生した場合、例外処理に遷移
            if pds_user_key_insert_error_info is not None:
                # ロールバック処理
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
                    pds_user_key_insert_error_info,
                    rollback_transaction,
                    delete_kms_key
                )

            # 22.WBT新規メール情報登録API実行処理
            # 22-01.以下の引数でWBT新規メール情報登録API呼び出し処理を実行する
            repositoryType = wbtConstClass.REPOSITORY_TYPE['ROUND']
            fileName = FileNameConstClass.TF_PUBLIC_KEY_NOTIFICATION + FileNameConstClass.TF_PUBLIC_KEY_NOTIFICATION_EXTENSION
            downloadDeadline = commonUtil.get_str_datetime_in_X_days(7)
            replyDeadline = commonUtil.get_str_datetime_in_X_days(30)
            comment = wbtConstClass.MESSAGE['PDS_USER_AUTH_INFO_CREATE']
            mailAddressTo = pds_user_result["query_results"][2]
            mailAddressCc = pds_user_result["query_results"][3]
            title = wbt_mail_subject

            # 22-02.WBT新規メール情報登録APIからのレスポンスを、「変数．WBT新規メール情報登録API実行結果」に格納する
            wbt_mails_add_api_result = self.common_util.wbt_mails_add_api_exec(
                repositoryType,
                fileName,
                downloadDeadline,
                replyDeadline,
                comment,
                mailAddressTo,
                mailAddressCc,
                title
            )
            # 22-03.WebBureauTransferの処理に失敗した場合、「変数．エラー情報」にエラー情報を作成する
            if not wbt_mails_add_api_result["result"]:
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990011"]["logMessage"]))
                self.error_info = {
                    "errorInfo": {
                        "errorCode": "990011",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["990011"]["message"], "990011")
                    }
                }

            # 23.共通エラーチェック処理
            # 23-01.以下の引数で共通エラーチェック処理を実行する
            # 23-02.例外が発生した場合、例外処理に遷移
            if wbt_mails_add_api_result.get("errorInfo"):
                # ロールバック処理
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
                    self.error_info["errorInfo"],
                    rollback_transaction,
                    delete_kms_key
                )

            # 24.WBTファイル登録API実行処理
            # 24-01.以下のパラメータでWBTファイル登録APIを呼び出す
            mailId = wbt_mails_add_api_result["id"]
            fileId = wbt_mails_add_api_result["attachedFiles"][0]["id"]
            file = tf_public_key_csv_stream
            chunkNo = '1'
            chunkTotalNumber = '1'

            # 24-02.WBTファイル登録APIからのレスポンスを、「変数．WBTファイル登録API実行結果」に格納する
            wbt_file_add_api_result = self.common_util.wbt_file_add_api_exec(
                mailId,
                fileId,
                file.get_temp_csv(),
                chunkNo,
                chunkTotalNumber
            )

            # 24-03.処理が失敗した場合は「変数．エラー情報」を作成し、エラー情報をCloudWatchにログ出力する
            if not wbt_file_add_api_result["result"]:
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990013"]["logMessage"]))
                self.error_info = {
                    "errorInfo": {
                        "errorCode": "990013",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["990013"]["message"], "990013")
                    }
                }

            # 25.共通エラーチェック処理
            # 25-01.以下の引数で共通エラーチェック処理を実行する
            # 25-02.例外が発生した場合、例外処理に遷移
            if wbt_file_add_api_result.get("errorInfo"):
                # ロールバック処理
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
                wbt_mail_cancel_exec = CallbackExecutor(
                    self.common_util.wbt_mail_cancel_exec,
                    mailId
                )
                self.common_util.common_error_check(
                    self.error_info["errorInfo"],
                    rollback_transaction,
                    wbt_mail_cancel_exec,
                    delete_kms_key
                )

            # 26.トランザクションコミット処理
            # 26-01.「PDSユーザ認証情報発行トランザクション」をコミットする
            common_db_connection_resource.commit_transaction(common_db_connection)

            # 27.トランザクション作成処理
            # 27-01.「WBT送信メールID更新トランザクション」を作成する

            # 28.WBT送信メールID更新処理
            pds_user_key_update_error_info = None
            # 28-01.PDSユーザ公開鍵テーブルを更新する
            pds_user_key_update_result = common_db_connection_resource.update(
                common_db_connection,
                SqlConstClass.PDS_USER_KEY_UPDATE_SQL,
                wbt_mails_add_api_result["id"],
                request_body.pdsUserId,
                pds_auth_max_index_result["query_results"][0] + 1
            )
            # 28-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not pds_user_key_update_result["result"]:
                pds_user_key_update_error_info = self.common_util.create_postgresql_log(
                    pds_user_key_update_result["errorObject"],
                    None,
                    None,
                    pds_user_key_update_result["stackTrace"]
                ).get("errorInfo")

            # 29.共通エラーチェック処理
            # 29-01.以下の引数で共通エラーチェック処理を実行する
            # 29-02.例外が発生した場合、例外処理に遷移
            if pds_user_key_update_error_info is not None:
                # ロールバック処理
                rollback_transaction = CallbackExecutor(
                    self.common_util.common_check_postgres_rollback,
                    common_db_connection,
                    common_db_connection_resource
                )
                self.common_util.common_error_check(
                    pds_user_key_update_error_info,
                    rollback_transaction
                )

            # 30.トランザクションコミット処理
            # 30-01.「WBT送信メールID更新トランザクション」をコミットする
            common_db_connection_resource.commit_transaction(common_db_connection)
            common_db_connection_resource.close_connection(common_db_connection)

            # 31.TF公開鍵通知ファイル削除処理
            # 31-01.「変数．TF公開鍵通知ファイル」をNullにする
            tf_public_key_csv_stream = None

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
