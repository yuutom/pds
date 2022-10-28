import base64
from logging import Logger
from typing import Optional
import boto3
import traceback
import time

# RequestBody
from pydantic import BaseModel
from const.wbtConst import wbtConstClass
from util.callbackExecutorUtil import CallbackExecutor

# Exception
from exceptionClass.PDSException import PDSException

# Const
from const.systemConst import SystemConstClass
from const.messageConst import MessageConstClass
from const.sqlConst import SqlConstClass
from const.fileNameConst import FileNameConstClass

# Util
from util.commonUtil import CommonUtilClass
from util.kmsUtil import KmsUtilClass
import util.commonUtil as commonUtil
import util.logUtil as logUtil
from util.s3Util import s3UtilClass
from util.fileUtil import NoHeaderOneItemCsvStringClass, CsvStreamClass
from util.mongoDbUtil import MongoDbClass


class requestBody(BaseModel):
    """
    リクエストボディクラス

    Args:
        BaseModel (Object): Pydanticのベースクラス
    """
    pdsUserId: Optional[str] = None
    pdsUserName: Optional[str] = None
    pdsUserDomainName: Optional[str] = None
    pdsUserPublicKeyStartDate: Optional[str] = None
    pdsUserPublicKeyExpectedDate: Optional[str] = None
    tfContactAddress: Optional[str] = None
    multiDownloadFileSendAddressTo: Optional[str] = None
    multiDownloadFileSendAddressCc: Optional[str] = None
    multiDeleteFileSendAddressTo: Optional[str] = None
    multiDeleteFileSendAddressCc: Optional[str] = None
    publicKeySendAddressTo: Optional[str] = None
    publicKeySendAddressCc: Optional[str] = None


class pdsUserCreateModelClass():
    def __init__(self, logger):
        """
        コンストラクタ

        Args:
            logger (Logger): ロガー（TRACE）
        """
        self.logger: Logger = logger
        self.common_util = CommonUtilClass(logger)

    def main(self, request_body: requestBody):
        """
        PDSユーザ登録API メイン処理

        Args:
            request_body (requestBody): リクエストボディ

        Returns:
            dict: 処理結果
        """
        try:
            # 05.共通DB接続準備処理
            # 05-01.共通DB接続情報取得処理
            # 05-01-01.AWS SecretsManagerから共通DB接続情報を取得して、「変数．共通DB接続情報」に格納する
            # 05-01-02.「変数．共通DB接続情報」を利用して、共通DBに対してのコネクションを作成する
            common_db_info_response = self.common_util.get_common_db_info_and_connection()
            if not common_db_info_response["result"]:
                raise PDSException(common_db_info_response["errorInfo"])
            else:
                common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
                common_db_connection = common_db_info_response["common_db_connection"]

            # 06.PDSユーザ取得処理
            pds_user_exist_error_info = None
            # 06-01.PDSユーザからデータを取得し、「変数．PDSユーザ検索結果」に1レコードをタプルとして格納する
            pds_user_get_count_result = common_db_connection_resource.select_tuple_one(
                common_db_connection,
                SqlConstClass.PDS_USER_EXIST_SELECT_SQL,
                request_body.pdsUserId
            )
            # 06-02.「変数．PDSユーザ検索結果[0]」が0以外の場合、「変数.エラー情報」を作成する
            if pds_user_get_count_result["result"] and pds_user_get_count_result["query_results"][0] != 0:
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["030001"]["logMessage"], "PDSユーザID", request_body.pdsUserId))
                pds_user_exist_error_info = {
                    "errorCode": "030001",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["030001"]["message"], "PDSユーザID", request_body.pdsUserId)
                }
            # 06-03.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            elif not pds_user_get_count_result["result"]:
                pds_user_exist_error_info = self.common_util.create_postgresql_log(
                    pds_user_get_count_result["errorObject"],
                    None,
                    None,
                    pds_user_get_count_result["stackTrace"]
                ).get("errorInfo")

            # 07.共通エラーチェック処理
            # 07-01.以下の引数で共通エラーチェック処理を実行する
            # 07-02 例外が発生した場合、例外処理に遷移
            if pds_user_exist_error_info is not None:
                self.common_util.common_error_check(pds_user_exist_error_info)

            # 08.PDSユーザリソース作成処理
            # 08-01.以下の引数でPDSユーザリソース作成処理を実行する
            # 08-02.PDSユーザリソース作成処理のレスポンスを変数．PDSユーザリソース作成処理実行結果に格納する
            create_pds_user_resource_result = self.create_pds_user_resource(
                request_body.pdsUserId + "-stack-set",
                SystemConstClass.CFN_TEMPLATE_BUCKET_NAME,
                SystemConstClass.CFN_PREFIX,
                request_body.pdsUserId
            )

            # 09.共通エラーチェック処理
            # 09-01.以下の引数で共通エラーチェック処理を実行する
            # 09-02 例外が発生した場合、例外処理に遷移
            if create_pds_user_resource_result.get("errorInfo"):
                self.common_util.common_error_check(
                    create_pds_user_resource_result["errorInfo"]
                )

            # 10.キーペア作成処理
            kms_util = KmsUtilClass(self.logger)
            kms_error_info = None
            # 10-01.KMSからTF公開鍵、秘密鍵のキーペアを作成し、KMSIDを取得する
            # 10-02.「変数．KMSID」に保持する
            for i in range(5):
                kms_id = kms_util.create_pds_user_kms_key(request_body.pdsUserId, request_body.pdsUserName)
                if kms_id:
                    break
            # 10-03.KMS登録処理に失敗した場合、「変数．エラー情報」を作成してエラーログをCloudWatchにログ出力する
            if not kms_id:
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990062"]["logMessage"]))
                kms_error_info = {
                    "errorCode": "990062",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["990062"]["message"], "990062")
                }

            # 11.共通エラーチェック処理
            # 11-01.以下の引数で共通エラーチェック処理を実行する
            # 11-02.例外が発生した場合、例外処理に遷移
            if kms_error_info is not None:
                # PDSユーザリソース削除処理
                delete_pds_user_resource = CallbackExecutor(
                    self.delete_pds_user_resource,
                    self.create_cfn_client(),
                    request_body.pdsUserId + "-stack-set"
                )
                self.common_util.common_error_check(
                    kms_error_info,
                    delete_pds_user_resource
                )

            # 12.キーペアレプリケート処理
            # 12-01.作成したキーペアを別リージョンにレプリケートする
            for i in range(5):
                replicate_id = kms_util.replicate_pds_user_kms_key(kms_id, request_body.pdsUserId, request_body.pdsUserName)
                if replicate_id:
                    break
            # 12-02.KMSレプリケート処理に失敗した場合、「変数．エラー情報」を作成してエラーログをCloudWatchにログ出力する
            if not replicate_id:
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990063"]["logMessage"], kms_id))
                kms_error_info = {
                    "errorCode": "990063",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["990063"]["message"], "990063")
                }

            # 13.共通エラーチェック処理
            # 13-01.以下の引数で共通エラーチェック処理を実行する
            # 13-02.例外が発生した場合、例外処理に遷移
            if kms_error_info is not None:
                # PDSユーザリソース削除処理
                delete_pds_user_resource = CallbackExecutor(
                    self.delete_pds_user_resource,
                    self.create_cfn_client(),
                    request_body.pdsUserId + "-stack-set"
                )
                # KMS削除処理
                delete_kms_key = CallbackExecutor(
                    kms_util.delete_kms_key,
                    kms_id,
                    False
                )
                self.common_util.common_error_check(
                    kms_error_info,
                    delete_pds_user_resource,
                    delete_kms_key
                )

            # 14.キーペア取得処理
            # 14-01.作成したキーペアから公開鍵を取得する
            for i in range(5):
                public_key = kms_util.get_kms_public_key(kms_id)
                if public_key:
                    break
            # 14-02.KMS公開鍵取得処理に失敗した場合、「変数．エラー情報」を作成してエラーログをCloudWatchにログ出力する
            if not public_key:
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["990064"]["logMessage"], kms_id))
                kms_error_info = {
                    "errorCode": "990064",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["990064"]["message"], "990064")
                }

            # 15.共通エラーチェック処理
            # 15-01.以下の引数で共通エラーチェック処理を実行する
            # 15-02.例外が発生した場合、例外処理に遷移
            if kms_error_info is not None:
                # PDSユーザリソース削除処理
                delete_pds_user_resource = CallbackExecutor(
                    self.delete_pds_user_resource,
                    self.create_cfn_client(),
                    request_body.pdsUserId + "-stack-set"
                )
                # KMS削除処理
                delete_kms_key = CallbackExecutor(
                    kms_util.delete_kms_key,
                    kms_id,
                    True
                )
                self.common_util.common_error_check(
                    kms_error_info,
                    delete_pds_user_resource,
                    delete_kms_key
                )

            # 16.TF公開鍵通知ファイル作成処理
            # 16-01.作成したキーペアから公開鍵を取得する
            public_key_string = base64.b64encode(public_key).decode()
            # 16-02.取得した以下のデータをもとにCSVファイルを作成する
            public_key_csv_string = NoHeaderOneItemCsvStringClass([public_key_string])
            public_key_csv_stream = CsvStreamClass(public_key_csv_string)

            # 17.APIキー通知ファイル作成処理
            # 17-01.取得した以下のデータをもとにCSVファイルを作成する
            # 17-02.作成したCSVファイルを「変数．APIキー通知ファイル」に格納する
            api_key_csv_string = NoHeaderOneItemCsvStringClass([create_pds_user_resource_result["apiKey"]])
            api_key_csv_stream = CsvStreamClass(api_key_csv_string)

            # 18.トランザクション作成処理
            # 18-01.「PDSユーザ登録トランザクション」を作成する

            # 19.PDSユーザ登録処理
            pds_user_insert_error_info = None
            # 19-01.PDSユーザテーブルに登録する
            pds_user_insert_result = common_db_connection_resource.insert(
                common_db_connection,
                SqlConstClass.PDS_USER_INSERT_SQL,
                request_body.pdsUserId,
                SystemConstClass.GROUP_ID,
                request_body.pdsUserName,
                request_body.pdsUserDomainName,
                create_pds_user_resource_result["apiKey"],
                create_pds_user_resource_result["stackOutputInfo"]["PdsUserDbSecretsName"],
                create_pds_user_resource_result["stackOutputInfo"]["BucketName"],
                create_pds_user_resource_result["stackOutputInfo"]["TokyoAzaMongoSecretName"],
                create_pds_user_resource_result["stackOutputInfo"]["TokyoAzcMongoSecretName"],
                create_pds_user_resource_result["stackOutputInfo"]["OsakaAzaMongoSecretName"],
                create_pds_user_resource_result["stackOutputInfo"]["OsakaAzcMongoSecretName"],
                create_pds_user_resource_result["stackOutputInfo"]["KmsId"],
                True,
                request_body.tfContactAddress,
                request_body.multiDownloadFileSendAddressTo,
                request_body.multiDownloadFileSendAddressCc,
                request_body.multiDeleteFileSendAddressTo,
                request_body.multiDeleteFileSendAddressCc,
                request_body.publicKeySendAddressTo,
                request_body.publicKeySendAddressCc
            )
            # 19-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not pds_user_insert_result["result"]:
                pds_user_insert_error_info = self.common_util.create_postgresql_log(
                    pds_user_insert_result["errorObject"],
                    "PDSユーザID",
                    request_body.pdsUserId,
                    pds_user_insert_result["stackTrace"]
                ).get("errorInfo")

            # 20.共通エラーチェック処理
            # 20-01.以下の引数で共通エラーチェック処理を実行する
            # 20-02 例外が発生した場合、例外処理に遷移
            if pds_user_insert_error_info is not None:
                delete_pds_user_resource = CallbackExecutor(
                    self.delete_pds_user_resource,
                    self.create_cfn_client(),
                    request_body.pdsUserId + "-stack-set"
                )
                # ロールバック処理
                rollback_transaction = CallbackExecutor(
                    self.common_util.common_check_postgres_rollback,
                    common_db_connection,
                    common_db_connection_resource
                )
                # KMS削除処理
                delete_kms_key = CallbackExecutor(
                    kms_util.delete_kms_key,
                    kms_id,
                    True
                )
                self.common_util.common_error_check(
                    pds_user_insert_error_info,
                    delete_pds_user_resource,
                    rollback_transaction,
                    delete_kms_key
                )

            # 21.WBTメール件名作成処理
            # 21-01.UUID ( v4ハイフンなし) を作成する
            mail_uuid = commonUtil.get_uuid_no_hypen()
            # 21-02.メール件名固定文字列と作成したUUIDを結合して、「変数．WBTメール件名」に格納する
            wbt_mail_subject = wbtConstClass.TITLE["PDS_USER_CREATE"] + "【{}】".format(mail_uuid)

            # 22.PDSユーザ公開鍵登録処理
            pds_user_key_insert_error_info = None
            # 22-01.PDSユーザ公開鍵テーブルを登録する
            pds_user_key_insert_result = common_db_connection_resource.insert(
                common_db_connection,
                SqlConstClass.PDS_USER_KEY_INSERT_SQL,
                request_body.pdsUserId,
                1,
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
            # 22-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not pds_user_key_insert_result["result"]:
                pds_user_key_insert_error_info = self.common_util.create_postgresql_log(
                    pds_user_key_insert_result["errorObject"],
                    "PDSユーザID",
                    request_body.pdsUserId,
                    pds_user_key_insert_result["stackTrace"]
                ).get("errorInfo")

            # 23.共通エラーチェック処理
            # 23-01.以下の引数で共通エラーチェック処理を実行する
            # 23-02 例外が発生した場合、例外処理に遷移
            if pds_user_key_insert_error_info is not None:
                # PDSユーザリソース削除処理
                delete_pds_user_resource = CallbackExecutor(
                    self.delete_pds_user_resource,
                    self.create_cfn_client(),
                    request_body.pdsUserId + "-stack-set"
                )
                # ロールバック処理
                rollback_transaction = CallbackExecutor(
                    self.common_util.common_check_postgres_rollback,
                    common_db_connection,
                    common_db_connection_resource
                )
                # KMS削除処理
                delete_kms_key = CallbackExecutor(
                    kms_util.delete_kms_key,
                    kms_id,
                    True
                )
                self.common_util.common_error_check(
                    pds_user_key_insert_error_info,
                    delete_pds_user_resource,
                    rollback_transaction,
                    delete_kms_key
                )

            # 24.WBT新規メール情報登録API実行処理
            wbt_mails_add_api_error_info = None
            file_name_list = [
                FileNameConstClass.TF_PUBLIC_KEY_NOTIFICATION + FileNameConstClass.TF_PUBLIC_KEY_NOTIFICATION_EXTENSION,
                FileNameConstClass.APIKEY_NOTIFICATION_NAME + FileNameConstClass.APIKEY_NOTIFICATION_EXTENSION
            ]
            try:
                # 24-01.以下の引数でWBT「新規メール情報登録API」を呼び出し処理を実行する
                # 24-02.WBT新規メール情報登録APIからのレスポンスを、「変数．WBT新規メール情報登録API実行結果」に格納する
                wbt_mails_add_api_exec_result = self.common_util.wbt_mails_add_api_exec(
                    wbtConstClass.REPOSITORY_TYPE["ROUND"],
                    file_name_list,
                    commonUtil.get_str_datetime_in_X_days(7),
                    commonUtil.get_str_datetime_in_X_days(30),
                    wbtConstClass.MESSAGE["PDS_USER_CREATE"],
                    request_body.publicKeySendAddressTo,
                    request_body.publicKeySendAddressCc,
                    wbt_mail_subject
                )
            except Exception:
                # 24-03.WebBureauTransferの処理に失敗した場合、「変数．エラー情報」にエラー情報を作成する
                wbt_mails_add_api_error_info = {
                    "errorCode": "990011",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["990011"]["message"])
                }
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990011"]["logMessage"], "990011"))

            # 25.共通エラーチェック処理
            # 25-01.以下の引数で共通エラーチェック処理を実行する
            # 25-02 例外が発生した場合、例外処理に遷移
            if wbt_mails_add_api_error_info is not None:
                # PDSユーザリソース削除処理
                delete_pds_user_resource = CallbackExecutor(
                    self.delete_pds_user_resource,
                    self.create_cfn_client(),
                    request_body.pdsUserId + "-stack-set"
                )
                # ロールバック処理
                rollback_transaction = CallbackExecutor(
                    self.common_util.common_check_postgres_rollback,
                    common_db_connection,
                    common_db_connection_resource
                )
                # KMS削除処理
                delete_kms_key = CallbackExecutor(
                    kms_util.delete_kms_key,
                    kms_id,
                    True
                )
                self.common_util.common_error_check(
                    wbt_mails_add_api_error_info,
                    delete_pds_user_resource,
                    rollback_transaction,
                    delete_kms_key
                )

            # 26.WBTのファイル登録API実行処理
            wbt_file_add_api_error_info = None
            try:
                # 26-01.以下のパラメータでWBTファイル登録APIを呼び出し処理を実行する
                # 26-02.WBTファイル登録APIからのレスポンスを、「変数．WBTファイル登録API実行結果」に格納する
                self.common_util.wbt_file_add_api_exec(
                    wbt_mails_add_api_exec_result["id"],
                    wbt_mails_add_api_exec_result["attachedFiles"][0]["id"],
                    public_key_csv_stream.get_temp_csv(),
                    None,
                    None,
                )
            except Exception:
                # 26-03.WBTファイル登録APIからのレスポンスを、「変数．WBTファイル登録API実行結果」に格納する
                wbt_file_add_api_error_info = {
                    "errorCode": "990013",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["990013"]["message"])
                }
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990013"]["logMessage"], "990013"))

            try:
                # 26-04.以下のパラメータでWBTファイル登録APIを呼び出し処理を実行する
                # 26-05.WBTファイル登録APIからのレスポンスを、「変数．WBTファイル登録API実行結果」に格納する
                self.common_util.wbt_file_add_api_exec(
                    wbt_mails_add_api_exec_result["id"],
                    wbt_mails_add_api_exec_result["attachedFiles"][1]["id"],
                    api_key_csv_stream.get_temp_csv(),
                    None,
                    None,
                )
            except Exception:
                # 26-06.WBTファイル登録APIからのレスポンスを、「変数．WBTファイル登録API実行結果」に格納する
                wbt_file_add_api_error_info = {
                    "errorCode": "990013",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["990013"]["message"])
                }
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990013"]["logMessage"], "990013"))

            # 27.共通エラーチェック処理
            # 27-01.以下の引数で共通エラーチェック処理を実行する
            # 27-02 例外が発生した場合、例外処理に遷移
            if wbt_file_add_api_error_info is not None:
                # PDSユーザリソース削除処理
                delete_pds_user_resource = CallbackExecutor(
                    self.delete_pds_user_resource,
                    self.create_cfn_client(),
                    request_body.pdsUserId + "-stack-set"
                )
                # ロールバック処理
                rollback_transaction = CallbackExecutor(
                    self.common_util.common_check_postgres_rollback,
                    common_db_connection,
                    common_db_connection_resource
                )
                # WBT送信取り消しAPI実行
                wbt_send_delete_api_exec = CallbackExecutor(
                    self.common_util.wbt_mail_cancel_exec,
                    wbt_mails_add_api_exec_result["id"]
                )
                # KMS削除処理
                delete_kms_key = CallbackExecutor(
                    kms_util.delete_kms_key,
                    kms_id,
                    True
                )
                self.common_util.common_error_check(
                    wbt_file_add_api_error_info,
                    delete_pds_user_resource,
                    rollback_transaction,
                    wbt_send_delete_api_exec,
                    delete_kms_key
                )

            # 28.トランザクションコミット処理
            # 28-01.トランザクションをコミットする
            common_db_connection_resource.commit_transaction(common_db_connection)

            # 29.トランザクション作成処理
            # 29-01.「PDSユーザ公開鍵更新トランザクション」を作成する

            # 30.WBT送信メールID更新処理
            pds_user_key_update_error_info = None
            # 30-01.PDSユーザ公開鍵テーブルを更新する
            pds_user_key_update_result = common_db_connection_resource.insert(
                common_db_connection,
                SqlConstClass.PDS_USER_KEY_UPDATE_SQL,
                wbt_mails_add_api_exec_result["id"],
                request_body.pdsUserId,
                1
            )
            # 30-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not pds_user_key_update_result["result"]:
                pds_user_key_update_error_info = self.common_util.create_postgresql_log(
                    pds_user_key_update_result["errorObject"],
                    None,
                    None,
                    pds_user_key_update_result["stackTrace"]
                ).get("errorInfo")

            # 31.共通エラーチェック処理
            # 31-01.以下の引数で共通エラーチェック処理を実行する
            # 31-02 例外が発生した場合、例外処理に遷移
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

            # 32.トランザクションコミット処理
            # 32.「PDSユーザ公開鍵更新トランザクション」をコミットする
            common_db_connection_resource.commit_transaction(common_db_connection)
            common_db_connection_resource.close_connection(common_db_connection)

            # 不要になったリソースの片付け
            self.common_util = None
            kms_util = None

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

    def create_pds_user_resource(self, stack_name: str, bucket_name: str, cloud_formation_prefix: str, pds_user_id: str):
        """
        PDSユーザリソース作成処理

        Args:
            stack_name (str): スタック名
            bucket_name (str): テンプレート格納バケット名
            cloud_formation_prefix (str): CloudFormationテンプレートプレフィックス
            pds_user_id (str): PDSユーザID

        Returns:
            dict: 処理結果
        """
        try:
            # 01.CloudFormationテンプレート存在検証処理
            s3_util = s3UtilClass(self.logger, bucket_name)
            # 01-01. 下記のパラメータでS3にテンプレートが存在するかを確認する
            # 01-02. CloudFormationテンプレート存在検証処理に失敗した場合、「変数．エラー情報」を作成するエラーログをCloudWatchにログ出力する
            check_result = s3_util.check_file(cloud_formation_prefix, False)

            # 02.共通エラーチェック処理
            # 02-01.以下の引数で共通エラーチェック処理を実行する
            # 02-02 例外が発生した場合、例外処理に遷移
            if not check_result["result"]:
                self.common_util.common_error_check(check_result["errorInfo"])

            # 03.スタックセット作成処理
            stackset_create_error = None
            try:
                client = self.create_cfn_client()
                sts = boto3.client('sts')
                id_info = sts.get_caller_identity()
                # 03-01.下記のパラメータでCloudFormationのネストされたスタックを実行する
                client.create_stack_set(
                    StackSetName=stack_name,
                    TemplateURL="https://" + bucket_name + ".s3.ap-northeast-1.amazonaws.com/" + cloud_formation_prefix,
                    Parameters=[
                        {'ParameterKey': "PdsUserId", 'ParameterValue': pds_user_id.lower()}
                    ]
                )
            except Exception:
                # 03-02.CloudFormationテンプレート実行処理中にエラーが発生した場合、エラー情報を作成する
                stackset_create_error = {
                    "errorCode": "990072",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["990072"]["message"], "990072")
                }
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990072"]["logMessage"]))

            # 04.共通エラーチェック処理
            # 04-01.以下の引数で共通エラーチェック処理を実行する
            # 04-02 例外が発生した場合、例外処理に遷移
            if stackset_create_error is not None:
                self.common_util.common_error_check(
                    stackset_create_error,
                )

            # 05.スタックセットインスタンス作成処理
            cloud_formation_create_error = None
            try:
                # 05-01.下記のパラメータでスタックセットインスタンス作成処理を実行する
                client.create_stack_instances(
                    StackSetName=stack_name,
                    Accounts=[id_info['Account']],
                    Regions=SystemConstClass.CFN_STACK_SET_REGIONS
                )
            except Exception:
                # 05-02.CloudFormationテンプレート実行処理中にエラーが発生した場合、エラー情報を作成する
                cloud_formation_create_error = {
                    "errorCode": "990072",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["990072"]["message"], "990072")
                }
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990072"]["logMessage"]))

            # 06.共通エラーチェック処理
            # 06-01.以下の引数で共通エラーチェック処理を実行する
            # 06-02 例外が発生した場合、例外処理に遷移
            if cloud_formation_create_error is not None:
                # PDSユーザリソース削除処理
                delete_pds_user_resource = CallbackExecutor(
                    self.delete_stack_set,
                    self.create_cfn_client(),
                    stack_name
                )
                self.common_util.common_error_check(
                    cloud_formation_create_error,
                    delete_pds_user_resource
                )

            # 07.CloudFormation終了監視処理
            cloud_formation_wait_error = None
            list_stack_response = None
            try:
                # 07-01.スタックセットインスタンス情報取得
                list_stack_response = client.list_stack_instances(
                    StackSetName=stack_name
                )
                # 07-02.スタック情報監視処理
                # 07-02-01.スタックセットインスタンス情報の要素数だけループする
                for idx, stack in enumerate(list_stack_response["Summaries"]):
                    for i in range(5):
                        # 07-02-01-01.スタックセットインスタンス情報再取得処理
                        list_stack_response = client.list_stack_instances(
                            StackSetName=stack_name
                        )
                        # 07-02-01-02.スタックセットインスタンス情報にスタックIDが含まれる場合、スタックの終了を監視する
                        if list_stack_response["Summaries"][idx].get("StackId"):
                            waiter_client = boto3.client(service_name="cloudformation", region_name=list_stack_response["Summaries"][idx]["Region"])
                            # 07-02-01-02-01.下記のパラメータでCloudFormationのスタック監視オブジェクトを作成して、「変数．スタック監視オブジェクト」に格納する
                            waiter = waiter_client.get_waiter('stack_create_complete')
                            # 07-02-01-02-02.下記のパラメータでスタックの作成状態を監視する
                            waiter.wait(StackName=list_stack_response["Summaries"][idx].get("StackId"))
                            break
                        # 07-02-01-03.スタックセットインスタンス情報にスタックIDが含まれない場合、一定時間待機後に07-02-01-01処理から再実行する（5回まで）
                        else:
                            if i < 4:
                                time.sleep(10)
                            elif i == 4:
                                # 07-02-01-04.スタックセットインスタンス情報にスタックIDが5回とも含まれなかった場合、「変数．エラー情報」にエラー情報を格納する
                                cloud_formation_wait_error = {
                                    "errorCode": "990073",
                                    "message": logUtil.message_build(MessageConstClass.ERRORS["990073"]["message"], "990073")
                                }
                                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990073"]["logMessage"]))
                                break
            except Exception:
                # 07-03.CloudFormationの終了監視処理でエラーが発生した場合、エラー情報を作成する
                cloud_formation_wait_error = {
                    "errorCode": "990073",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["990073"]["message"], "990073")
                }
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990073"]["logMessage"]))

            # 08.CloudFormation終了監視チェック処理
            # 08-01.「変数．エラー情報」がNullの場合、「11. スタック情報取得処理」に遷移する
            # 08-02.「変数．エラー情報」がNull以外の場合、「09.スタックセット削除処理」に遷移する
            if cloud_formation_wait_error is not None:
                # 09.スタックセット削除処理
                # 09-01.下記の引数でスタックセット削除処理を実施する
                # 09-02.レスポンスを「変数．スタックセット削除レスポンス情報」に格納する
                delete_stack_set_response = self.delete_stack_set(client, stack_name)

                stack_rollback_error_info = None
                delete_pds_user_error_info = None
                if delete_stack_set_response["result"]:
                    for stack_info in delete_stack_set_response["stack_list_info"]:
                        # 10.CloudFormationスタック有無判定
                        # 10-01.「変数．スタックセット削除レスポンス情報．スタックインスタンスリスト[スタックインスタンスリストループ数]．スタックID」の要素が存在する場合、「11.CloudFormation状態チェック処理」を実施する
                        # 10-02.「変数．スタックセット削除レスポンス情報．スタックインスタンスリスト[スタックインスタンスリストループ数]．スタックID」の要素が存在しない場合、次のループを実施する
                        if stack_info.get("StackId"):
                            # 11.CloudFormation状態チェック処理
                            # 11-01.スタック情報取得処理を下記のパラメータで実行する
                            # 11-02.「変数．CloudFormation情報取得処理実行結果[0]．StackStatus」がROLLBACK_COMPLETEの場合、「12．スタック削除処理」に遷移する
                            # 11-03.「変数．CloudFormation情報取得処理実行結果[0]．StackStatus」がDELETE_COMPLETEの場合、次のループに遷移する
                            # 11-04.「変数．CloudFormation情報取得処理実行結果[0]．StackStatus」がROLLBACK_COMPLETEとDELETE_COMPLETE以外の場合、「13.スタックロールバックエラー情報作成処理」に遷移する
                            stack_client = boto3.client(service_name="cloudformation", region_name=list_stack_response["Summaries"][idx]["Region"])
                            if stack_client.describe_stacks(StackName=stack_info["StackId"])["Stacks"][0]["StackStatus"] == SystemConstClass.CFN_ROLLBACK_STACK_STATUS:
                                # 12.スタック削除処理
                                # 12-01.以下の引数でスタック削除処理を実行する
                                for delete_count in range(5):
                                    try:
                                        stack_client.delete_stack(
                                            StackName=stack_info["StackId"]
                                        )
                                        break
                                    except Exception:
                                        # 12-02.スタック削除処理でエラーが発生した場合、「変数．スタック削除エラー情報」にエラー情報を作成する
                                        if delete_count == 4:
                                            self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990074"]["logMessage"], str(stack_name)))
                                            delete_pds_user_error_info = {
                                                "errorCode": "990074",
                                                "message": logUtil.message_build(MessageConstClass.ERRORS["990074"]["message"], "990074")
                                            }
                                            break
                                        continue
                            elif stack_client.describe_stacks(StackName=stack_info["StackId"])["Stacks"][0]["StackStatus"] == SystemConstClass.CFN_DELETE_STACK_STATUS:
                                # 削除済みのため何もしない
                                pass
                            else:
                                # 13.スタックロールバックエラー情報作成処理
                                # 13-01.ロールバックに失敗していた場合、ロールバックエラー情報を作成する
                                stack_rollback_error_info = {
                                    "errorCode": "990071",
                                    "message": logUtil.message_build(MessageConstClass.ERRORS["990071"]["message"], "990071")
                                }
                                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990071"]["logMessage"]))

                # 14.CloudFormationテンプレート実行エラー処理
                # 14-01.レスポンス情報を作成し、返却する
                # 14-01-01.「変数．エラー情報」に値が設定されている場合、下記のレスポンス情報を作成する
                response = {
                    "result": False,
                    "errorInfo": [
                        cloud_formation_wait_error
                    ]
                }
                # 14-01-02.「変数．ロールバックエラー情報」に値が設定されている場合、エラー情報リストに「変数．ロールバックエラー情報」を追加する
                if stack_rollback_error_info is not None:
                    response["errorInfo"].append(stack_rollback_error_info)

                # 14-01-03.「変数．スタック削除エラー情報」に値が設定されている場合、エラー情報リストに「変数．スタック削除エラー情報」を追加する
                if delete_pds_user_error_info is not None:
                    response["errorInfo"].append(delete_pds_user_error_info)

                return response

            # 15.スタック情報取得処理
            cloud_formation_get_stack_info_error = None
            my_region_idx = None
            try:
                for idx, stack in enumerate(list_stack_response["Summaries"]):
                    if stack["Region"] == SystemConstClass.AWS_CONST["REGION"]:
                        my_region_idx = idx

                # 15-01.下記のパラメータでCloudFormationの情報を取得する
                # 15-02.処理のレスポンスを「変数．CloudFormation情報取得処理実行結果」に格納する
                cloud_formation_stack_info = client.describe_stacks(StackName=list_stack_response["Summaries"][my_region_idx]["StackId"])
                # 15-03.「変数．CloudFormation情報取得処理実行結果．Outputs」の要素数だけ処理を繰り返して、「変数．スタック出力情報」を作成する
                stack_output_info = {}
                for output in cloud_formation_stack_info["Stacks"][0]["Outputs"]:
                    stack_output_info[output["OutputKey"]] = output["OutputValue"]
            except Exception:
                # 15-04.CloudFormationの終了監視処理でエラーが発生した場合、エラー情報を作成する
                cloud_formation_get_stack_info_error = {
                    "errorCode": "990073",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["990073"]["message"])
                }
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990073"]["logMessage"], "990073"))

            # 16.共通エラーチェック処理
            # 16-01.以下の引数で共通エラーチェック処理を実行する
            # 16-02 例外が発生した場合、例外処理に遷移
            if cloud_formation_get_stack_info_error is not None:
                # PDSユーザリソース削除処理
                delete_pds_user_resource = CallbackExecutor(
                    self.delete_pds_user_resource,
                    client,
                    stack_name
                )
                self.common_util.common_error_check(cloud_formation_get_stack_info_error)

            # 17.APIキー作成処理
            # 17-01.APIキー(ランダム文字列 30桁)を作成し、「変数．APIキー」に格納する
            api_key = commonUtil.get_random_ascii(30)

            # 18.RDSテーブル作成処理
            # 18-01.以下の引数でRDSテーブル作成処理を実行する
            # 18-02.RDSテーブル作成処理のレスポンスを「変数．RDSテーブル作成処理実行結果」に格納する
            crete_rds_table_response = self.create_rds_table(stack_output_info["PdsUserDbSecretsName"], pds_user_id)

            # 19.共通エラーチェック処理
            # 19-01.以下の引数で共通エラーチェック処理を実行する
            # 19-02 例外が発生した場合、例外処理に遷移
            if not crete_rds_table_response["result"]:
                self.common_util.common_error_check(crete_rds_table_response["errorInfo"])

            # 20.MongoDB初期設定処理
            # 20-01.以下の引数でMongoDB初期設定処理を実行する
            # 20-02.MongoDB初期設定処理のレスポンスを「変数．MongoDB初期設定処理実行結果」に格納する
            initial_mongodb_response = self.initial_mongodb(
                stack_output_info["TokyoAzaMongoSecretName"],
                stack_output_info["TokyoAzcMongoSecretName"],
                stack_output_info["OsakaAzaMongoSecretName"],
                stack_output_info["OsakaAzcMongoSecretName"]
            )

            # 21.共通エラーチェック処理
            # 21-01.以下の引数で共通エラーチェック処理を実行する
            # 21-02 例外が発生した場合、例外処理に遷移
            if not initial_mongodb_response["result"]:
                self.common_util.common_error_check(initial_mongodb_response["errorInfo"])

            # 22.終了処理
            # 22-01.レスポンス情報整形処理
            # 22-02.処理を終了する
            return {
                "result": True,
                "apiKey": api_key,
                "stackOutputInfo": stack_output_info
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

    def delete_pds_user_resource(self, client, stack_name: str):
        """
        PDSユーザリソース削除処理

        Args:
            client (object): boto3のCloudFormationのクライアント
            stack_name (str): スタック名
        """
        try:
            error_info = None
            # 01.スタックセット削除処理
            # 01-01.以下の引数でスタックセット削除処理を実行する
            delete_stack_set_response = self.delete_stack_set(client, stack_name)
            if delete_stack_set_response["result"]:
                # スタックセットに紐づけられていたスタックの削除
                for stack_info in delete_stack_set_response["stack_list_info"]:
                    # 02.削除対象スタック有無判定処理
                    # 02-01.「変数．スタックセット削除処理実行結果．スタックセットインスタンス情報[スタックセットループ数]．スタックID」が存在する場合、「03.CloudFormationスタック削除処理」へ遷移する
                    # 02-02.「変数．スタックセット削除処理実行結果．スタックセットインスタンス情報[スタックセットループ数]．スタックID」が存在しない場合、次のループへ遷移する
                    if stack_info.get("StackId"):
                        stack_client = boto3.client('kms', region_name=stack_info["Region"])
                        for delete_count in range(5):
                            try:
                                # 01.CloudFormationスタック削除処理
                                # 01-01.下記のパラメータでCloudFormationのスタックを削除する
                                stack_client.delete_stack(
                                    StackName=["StackId"]
                                )
                                break
                            except Exception:
                                if delete_count == 4:
                                    # 01-02.CloudFormationスタック削除処理中に5回エラーが発生した場合、エラー情報を作成する
                                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990074"]["logMessage"], str(stack_name)))
                                    error_info = {
                                        "errorCode": "990074",
                                        "message": logUtil.message_build(MessageConstClass.ERRORS["990074"]["message"], "990074")
                                    }
                                    break
                                continue

            # 02.共通エラーチェック処理
            # 02-01.以下の引数で共通エラーチェック処理を実行する
            # 02-02 例外が発生した場合、例外処理に遷移
            if error_info is not None:
                self.common_util.common_error_check(error_info)

            # 03.終了処理
            # 03-01.処理を終了する

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

    def delete_stack_set(self, client, stack_name: str):
        """
        スタックセット削除処理

        Args:
            client (object): boto3クライアント（CloudFormation）
            stack_name (str): スタック名

        """
        try:
            error_info = None
            sts = boto3.client('sts')
            id_info = sts.get_caller_identity()
            # 01.スタックインスタンス情報取得処理
            # 01-01.以下のパラメータでスタックインスタンス削除処理を実行する
            list_stack_response = client.list_stack_instances(
                StackSetName=stack_name
            )

            for delete_count in range(5):
                try:
                    # 01.スタックインスタンス削除処理
                    # 01-01.下記のパラメータでCloudFormationのスタックを削除する
                    # 01-02.レスポンスを「変数．オペレーションID」に格納する
                    response = client.delete_stack_instances(
                        StackSetName=stack_name,
                        Accounts=[id_info['Account']],
                        Regions=SystemConstClass.CFN_STACK_SET_REGIONS,
                        RetainStacks=True
                    )
                    operation_id = response["OperationId"]
                    break
                except Exception:
                    if delete_count == 4:
                        # 01-03.CloudFormationスタック削除処理中に5回エラーが発生した場合、エラー情報を作成する
                        self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990074"]["logMessage"], str(stack_name)))
                        error_info = {
                            "errorCode": "990074",
                            "message": logUtil.message_build(MessageConstClass.ERRORS["990074"]["message"], "990074")
                        }
                        break
                    continue

            # 02.共通エラーチェック処理
            # 02-01.以下の引数で共通エラーチェック処理を実行する
            # 02-02 例外が発生した場合、例外処理に遷移
            if error_info is not None:
                self.common_util.common_error_check(error_info)

            for delete_count in range(5):
                try:
                    # 01.スタックインスタンス削除完了待機処理
                    # 01-01.下記のパラメータでCloudFormationのスタックを削除する
                    response = client.describe_stack_set_operation(
                        StackSetName=stack_name,
                        OperationId=operation_id
                    )
                    operation_status = response["StackSetOperation"]["Status"]
                    if operation_status == SystemConstClass.CFN_STACK_SET_SUCCESS:
                        break
                    else:
                        if delete_count == 4:
                            # 01-02.CloudFormationスタック削除処理中に5回エラーが発生した場合、エラー情報を作成する
                            self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990074"]["logMessage"], str(stack_name)))
                            error_info = {
                                "errorCode": "990074",
                                "message": logUtil.message_build(MessageConstClass.ERRORS["990074"]["message"], "990074")
                            }
                            break
                        time.sleep(5)
                except Exception:
                    if delete_count == 4:
                        # 01-02.CloudFormationスタック削除処理中に5回エラーが発生した場合、エラー情報を作成する
                        self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990074"]["logMessage"], str(stack_name)))
                        error_info = {
                            "errorCode": "990074",
                            "message": logUtil.message_build(MessageConstClass.ERRORS["990074"]["message"], "990074")
                        }
                        break
                    continue

            # 02.共通エラーチェック処理
            # 02-01.以下の引数で共通エラーチェック処理を実行する
            # 02-02 例外が発生した場合、例外処理に遷移
            if error_info is not None:
                self.common_util.common_error_check(error_info)

            for delete_count in range(5):
                try:
                    # 01.CloudFormationスタック削除処理
                    # 01-01.下記のパラメータでCloudFormationのスタックを削除する
                    response = client.delete_stack_set(
                        StackSetName=stack_name
                    )
                    break
                except Exception:
                    if delete_count == 4:
                        # 01-02.CloudFormationスタック削除処理中に5回エラーが発生した場合、エラー情報を作成する
                        self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990074"]["logMessage"], str(stack_name)))
                        error_info = {
                            "errorCode": "990074",
                            "message": logUtil.message_build(MessageConstClass.ERRORS["990074"]["message"], "990074")
                        }
                        break
                    continue

            # 02.共通エラーチェック処理
            # 02-01.以下の引数で共通エラーチェック処理を実行する
            # 02-02 例外が発生した場合、例外処理に遷移
            if error_info is not None:
                self.common_util.common_error_check(error_info)

            return {
                "result": True,
                "stack_list_info": list_stack_response["Summaries"]
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

    def create_rds_table(self, rds_db_secret_name: str, pds_user_id: str):
        """
        RDSテーブル作成処理

        Args:
            rdsDbSecretName (str): PDSユーザDBインスタンスシークレット名
            pds_user_id (str): PDSユーザID

        Returns:
            dict: 処理結果
        """
        try:
            # 01.PDSユーザDB接続情報取得処理
            # 01-01.AWS SecretsManagerから「引数．PDSユーザDBインスタンスシークレット名」でPDSユーザDB接続情報を取得して、
            # 01-01-02.「変数．PDSユーザDB接続情報」を利用して、PDSユーザDBに対してのコネクションを作成する
            pds_user_db_info_response = self.common_util.get_pds_user_db_info_and_connection(rds_db_secret_name)
            if not pds_user_db_info_response["result"]:
                raise PDSException(pds_user_db_info_response["errorInfo"])
            else:
                pds_user_db_connection_resource = pds_user_db_info_response["pds_user_db_connection_resource"]
                pds_user_db_connection = pds_user_db_info_response["pds_user_db_connection"]

            # 02.トランザクション作成処理
            # 02-01.「PDSユーザDB作成トランザクション」を作成する

            # 03.PDSユーザごとのテーブル作成処理
            errorInfo = None
            try:
                # 03-01.個人情報テーブルを作成する
                pds_user_db_connection_resource.execute_query(
                    pds_user_db_connection,
                    SqlConstClass.USER_PROFILE_TABLE_CREATE
                )

                # 03-02.個人情報バイナリデータテーブルを作成する
                pds_user_db_connection_resource.execute_query(
                    pds_user_db_connection,
                    SqlConstClass.USER_PROFILE_BINARY_TABLE_CREATE
                )

                # 03-03.個人情報バイナリ分割データテーブルを作成する
                pds_user_db_connection_resource.execute_query(
                    pds_user_db_connection,
                    SqlConstClass.USER_PROFILE_BINARY_SPLIT_TABLE_CREATE
                )
            except Exception as e:
                # 03-04.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
                errorInfo = self.common_util.create_postgresql_log(
                    e,
                    None,
                    None,
                    traceback.format_exc()
                ).get("errorInfo")

            # 04.共通エラーチェック処理
            # 04-01.以下の引数で共通エラーチェック処理を実行する
            # 04-02 例外が発生した場合、例外処理に遷移
            if errorInfo is not None:
                # PDSユーザリソース削除処理
                delete_pds_user_resource = CallbackExecutor(
                    self.delete_pds_user_resource,
                    self.create_cfn_client(),
                    pds_user_id + "-stack-set"
                )
                # ロールバック処理
                rollback_transaction = CallbackExecutor(
                    self.common_util.common_check_postgres_rollback,
                    pds_user_db_connection,
                    pds_user_db_connection_resource
                )
                self.common_util.common_error_check(
                    errorInfo,
                    delete_pds_user_resource,
                    rollback_transaction
                )

            # 05.トランザクションコミット処理
            # 05-01.「PDSユーザ公開鍵更新トランザクション」をコミットする
            pds_user_db_connection_resource.commit_transaction(pds_user_db_connection)
            pds_user_db_connection_resource.close_connection(pds_user_db_connection)

            # 06.終了処理
            return {
                "result": True
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

    def create_cfn_client(self):
        """
        CFN用のBotoクライアント作成

        Returns:
            object: Botoクライアント(CFN用)
        """
        try:
            client = boto3.client(
                service_name="cloudformation"
            )
            return client
        except Exception as e:
            raise e

    def initial_mongodb(self, mongodb_tokyo_a_secret_name, mongodb_tokyo_c_secret_name, mongodb_osaka_a_secret_name, mongodb_osaka_c_secret_name):
        """
        MongoDB初期設定処理

        Args:
            mongodb_tokyo_a_secret_name (str): MongoDBシークレット名（東京a）
            mongodb_tokyo_c_secret_name (str): MongoDBシークレット名（東京c）
            mongodb_osaka_a_secret_name (str): MongoDBシークレット名（大阪a）
            mongodb_osaka_c_secret_name (str): MongoDBシークレット名（大阪c）

        Returns:
            _type_: _description_
        """
        try:
            # 01.接続情報取得処理
            # 01-01.SecretsManagerから東京aの接続情報を取得する
            mongodb_tokyo_a_secret_info = self.common_util.get_secret_info(mongodb_tokyo_a_secret_name)
            # 01-02.SecretsManagerから東京cの接続情報を取得する
            mongodb_tokyo_c_secret_info = self.common_util.get_secret_info(mongodb_tokyo_c_secret_name)
            # 01-03.SecretsManagerから大阪aの接続情報を取得する
            mongodb_osaka_a_secret_info = self.common_util.get_secret_info(mongodb_osaka_a_secret_name)
            # 01-04.SecretsManagerから大阪cの接続情報を取得する
            mongodb_osaka_c_secret_info = self.common_util.get_secret_info(mongodb_osaka_c_secret_name)

            # 02.MongoDBレプリカセット設定処理
            connection_error_info_list = []
            tokyo_a_connection_flg = False
            tokyo_c_connection_flg = False
            osaka_a_connection_flg = False
            osaka_c_connection_flg = False
            try:
                repset_result = None
                # 02-01-01.東京aのMonboDBに接続する
                tokyo_a_connection: MongoDbClass = self.common_util.get_mongo_connection(mongodb_tokyo_a_secret_info)
                # 02-01-02.東京aのMongoDBをプライマリにレプリカセットを設定する
                repset_result = tokyo_a_connection.create_replica_set(
                    mongodb_tokyo_a_secret_info["host"],
                    mongodb_tokyo_a_secret_info["port"],
                    mongodb_tokyo_c_secret_info["host"],
                    mongodb_tokyo_c_secret_info["port"],
                    mongodb_osaka_a_secret_info["host"],
                    mongodb_osaka_a_secret_info["port"],
                    mongodb_osaka_c_secret_info["host"],
                    mongodb_osaka_c_secret_info["port"],
                )
                # 02-01-03.レプリカセットの設定処理に失敗した場合、「変数．エラー情報」にエラー情報を追加する
                if not repset_result["result"]:
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["992001"]["logMessage"], repset_result["errorCode"], repset_result["message"]))
                    connection_error_info_list.append(
                        {
                            "errorCode": "992001",
                            "message": logUtil.message_build(MessageConstClass.ERRORS["992001"]["message"], "992001")
                        }
                    )
                else:
                    # 02-01-04.レプリカセットの設定処理に成功した場合、「変数．東京aレプリカセット実施フラグ」をtrueにする
                    tokyo_a_connection_flg = True
            except Exception as e:
                # 02-01-03.予期せぬエラーが発生した場合、「変数．エラー情報」にエラー情報を追加する
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["999999"]["logMessage"], str(e), traceback.format_exc()))
                connection_error_info_list.append(
                    {
                        "errorCode": "999999",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
                    }
                )

            # 02-02-01.「変数．東京aレプリカセット実施フラグ」をtrueではない場合、
            if not tokyo_a_connection_flg:
                try:
                    repset_result = None
                    # 02-02.東京aのMonboDBに接続できなかった場合、東京cのMongoDBに接続する
                    tokyo_c_connection: MongoDbClass = self.common_util.get_mongo_connection(mongodb_tokyo_c_secret_info)
                    repset_result = tokyo_c_connection.create_replica_set(
                        mongodb_tokyo_c_secret_info["host"],
                        mongodb_tokyo_c_secret_info["port"],
                        mongodb_tokyo_a_secret_info["host"],
                        mongodb_tokyo_a_secret_info["port"],
                        mongodb_osaka_a_secret_info["host"],
                        mongodb_osaka_a_secret_info["port"],
                        mongodb_osaka_c_secret_info["host"],
                        mongodb_osaka_c_secret_info["port"],
                    )
                    if not repset_result["result"]:
                        self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["992001"]["logMessage"], repset_result["errorCode"], repset_result["message"]))
                        connection_error_info_list.append(
                            {
                                "errorCode": "992001",
                                "message": logUtil.message_build(MessageConstClass.ERRORS["992001"]["message"], "992001")
                            }
                        )
                    else:
                        tokyo_c_connection_flg = True
                except Exception as e:
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["999999"]["logMessage"], str(e), traceback.format_exc()))
                    connection_error_info_list.append(
                        {
                            "errorCode": "999999",
                            "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
                        }
                    )

            if not tokyo_a_connection_flg and not tokyo_c_connection_flg:
                try:
                    repset_result = None
                    # 02-03.東京a、東京cのMonboDBに接続できなかった場合、大阪aのMongoDBに接続する
                    osaka_a_connection: MongoDbClass = self.common_util.get_mongo_connection(mongodb_osaka_a_secret_info)
                    repset_result = osaka_a_connection.create_replica_set(
                        mongodb_osaka_a_secret_info["host"],
                        mongodb_osaka_a_secret_info["port"],
                        mongodb_tokyo_a_secret_info["host"],
                        mongodb_tokyo_a_secret_info["port"],
                        mongodb_tokyo_c_secret_info["host"],
                        mongodb_tokyo_c_secret_info["port"],
                        mongodb_osaka_c_secret_info["host"],
                        mongodb_osaka_c_secret_info["port"],
                    )
                    if not repset_result["result"]:
                        self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["992001"]["logMessage"], repset_result["errorCode"], repset_result["message"]))
                        connection_error_info_list.append(
                            {
                                "errorCode": "992001",
                                "message": logUtil.message_build(MessageConstClass.ERRORS["992001"]["message"], "992001")
                            }
                        )
                    else:
                        osaka_a_connection_flg = True
                except Exception as e:
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["999999"]["logMessage"], str(e), traceback.format_exc()))
                    connection_error_info_list.append(
                        {
                            "errorCode": "999999",
                            "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
                        }
                    )

            if not tokyo_a_connection_flg and not tokyo_c_connection_flg and not osaka_a_connection_flg:
                try:
                    repset_result = None
                    # 02-04.東京a、東京c、大阪aのMonboDBに接続できなかった場合、大阪cのMongoDBに接続する
                    osaka_c_connection: MongoDbClass = self.common_util.get_mongo_connection(mongodb_osaka_c_secret_info)
                    repset_result = osaka_c_connection.create_replica_set(
                        mongodb_osaka_c_secret_info["host"],
                        mongodb_osaka_c_secret_info["port"],
                        mongodb_tokyo_a_secret_info["host"],
                        mongodb_tokyo_a_secret_info["port"],
                        mongodb_tokyo_c_secret_info["host"],
                        mongodb_tokyo_c_secret_info["port"],
                        mongodb_osaka_a_secret_info["host"],
                        mongodb_osaka_a_secret_info["port"],
                    )
                    if not repset_result["result"]:
                        self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["992001"]["logMessage"], repset_result["errorCode"], repset_result["message"]))
                        connection_error_info_list.append(
                            {
                                "errorCode": "992001",
                                "message": logUtil.message_build(MessageConstClass.ERRORS["992001"]["message"], "992001")
                            }
                        )
                    else:
                        osaka_c_connection_flg = True
                except Exception as e:
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["999999"]["logMessage"], str(e), traceback.format_exc()))
                    connection_error_info_list.append(
                        {
                            "errorCode": "999999",
                            "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
                        }
                    )

            if not tokyo_a_connection_flg and not tokyo_c_connection_flg and not osaka_a_connection_flg and not osaka_c_connection_flg:
                # 02-05.東京a、東京c、大阪a、大阪cのMonboDBに接続できなかった場合、「変数．エラー情報」にエラー情報を格納する
                return {
                    "result": False,
                    "errorInfo": connection_error_info_list
                }

            # 04.終了処理
            # 04-01.「変数．エラー情報」がNullの場合、レスポンス情報を作成して返却する
            return {
                "result": True
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
