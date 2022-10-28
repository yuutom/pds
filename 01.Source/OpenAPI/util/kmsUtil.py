import json
import time
import boto3
from logging import Logger
import traceback

# Exceptionクラス
from exceptionClass.PDSException import PDSException

# Utilクラス
import util.logUtil as logUtil
import util.checkUtil as checkUtil
from util.commonUtil import CommonUtilClass

# 定数クラス
from const.systemConst import SystemConstClass
from const.messageConst import MessageConstClass


class KmsUtilClass:
    def __init__(self, logger):
        self.logger: Logger = logger
        self.client = boto3.client(
            service_name="kms"
        )
        self.another_client = boto3.client(
            service_name="kms",
            region_name=SystemConstClass.KMS_REPLICA_REGION
        )

    def create_pds_user_kms_key(self, pds_user_id: str, pds_user_name: str):
        """
        PDSUser認証キー作成

        Args:
            pdsUserId (str): PDSユーザID
            pdsUserName (str): PDSユーザ名

        Returns:
            str: KMSID
        """

        pdsUserKeyResponse = self.client.create_key(
            Policy=json.dumps(SystemConstClass.KMS_POLICY_TEMP),
            Description=pds_user_name + '認証キー',
            KeyUsage='ENCRYPT_DECRYPT',
            CustomerMasterKeySpec='RSA_4096',
            Origin='AWS_KMS',
            BypassPolicyLockoutSafetyCheck=False,
            Tags=[
                {
                    'TagKey': 'NAME',
                    'TagValue': pds_user_id + 'key'
                }
            ],
            MultiRegion=True
        )
        return pdsUserKeyResponse["KeyMetadata"]['KeyId']

    def replicate_pds_user_kms_key(self, key_id: str, pds_user_id: str, pds_user_name: str):
        """
        PDSUser認証キーレプリケート

        Args:
            kms_id (str): KMSキーID
            pdsUserId (str): PDSユーザID
            pdsUserName (str): PDSユーザ名

        Returns:
            str: KMSID
        """

        pdsUserKeyResponse = self.client.replicate_key(
            KeyId=key_id,
            ReplicaRegion=SystemConstClass.KMS_REPLICA_REGION,
            Policy=json.dumps(SystemConstClass.KMS_POLICY_TEMP_REPLICA),
            Description=pds_user_name + '認証キー',
            BypassPolicyLockoutSafetyCheck=False,
            Tags=[
                {
                    'TagKey': 'NAME',
                    'TagValue': pds_user_id + 'key'
                }
            ]
        )
        return pdsUserKeyResponse["ReplicaKeyMetadata"]['KeyId']

    def generate_kms_data_key(self, key_id: str):
        """
        データキー生成

        Args:
            kms_id (str): KMSキーID

        Returns:
            dict: データキー情報
        """

        return self.client.generate_data_key(KeyId=key_id, KeySpec='AES_256')

    def get_kms_public_key(self, kms_id: str):
        """
        公開鍵情報取得

        Args:
            kms_id (str): KMSID

        Returns:
            bytes: 公開鍵情報
        """
        pdsUserKeyResponse = self.client.get_public_key(
            KeyId=kms_id
        )
        return pdsUserKeyResponse["PublicKey"]

    def decrypt_kms_data_key(self, encryptDataKey: str):
        """
        複合処理(データキー)

        Args:
            encryptDataKey (str): 暗号化済みデータキー
            encryptData (str): 暗号化済みデータ

        Returns:
            bytes: 複合データキー
        """
        decrypt_key = self.client.decrypt(CiphertextBlob=bytes(encryptDataKey))
        return decrypt_key['Plaintext']

    # 検索用 水野担当ファイル
    def delete_kms_key(self, kmsKeyId: str, replicate_delete_flg: bool):
        """
        KMS削除処理

        Args:
            kmsKeyId (str): KMSキーID
            replicate_delete_flg(bool): レプリケート削除フラグ

        """
        error_info_list = []
        error_info = None
        EXEC_NAME_JP = "KMS削除処理"
        try:
            common_util = CommonUtilClass(self.logger)

            # 01.引数検証処理（入力チェック）
            # 01-01.「引数．KMSキーID」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(kmsKeyId):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "検索条件"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "検索条件")
                    }
                )
            # 01-02.「変数．エラー情報リスト」に値が設定されている場合、エラー作成処理を実施する
            if len(error_info_list) != 0:
                raise PDSException(*error_info_list)

            # 02.KMSキー情報無効化処理
            # 02-01.KMSのキー情報を無効化する
            for _ in range(5):
                disable_key_response = self.client.disable_key(
                    KeyId=kmsKeyId
                )
                if disable_key_response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                    break
            # 02-02.KMS無効化処理に失敗した場合、「変数．エラー情報」を作成してエラーログをCloudWatchにログ出力する
            if disable_key_response["ResponseMetadata"]["HTTPStatusCode"] != 200:
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990061"]["logMessage"], kmsKeyId))
                error_info = {
                    "errorCode": "990061",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["990061"]["message"], "990061")
                }

            # 03.レプリケート削除フラグチェック処理
            # 03-01.「引数．レプリケート削除フラグ」がtrueの場合、「04.アナザーリージョンKMSキー情報無効化処理」に遷移する
            # 03-02.「引数．レプリケート削除フラグ」がfalseの場合、「05.共通エラーチェック処理」に遷移する
            if replicate_delete_flg:
                # 04.別リージョンKMSキー情報無効化処理
                # 04-01.別のリージョンのKMSのキー情報を無効化する
                for _ in range(5):
                    try:
                        if not self.another_client.describe_key(KeyId=kmsKeyId)["KeyMetadata"]["Enabled"]:
                            time.sleep(0.5)
                        disable_key_response = self.another_client.disable_key(
                            KeyId=kmsKeyId
                        )
                        if disable_key_response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                            break
                    except Exception:
                        continue
                # 04-02.別のリージョンのKMS無効化処理に失敗した場合、「変数．エラー情報」を作成してエラーログをCloudWatchにログ出力する
                if disable_key_response["ResponseMetadata"]["HTTPStatusCode"] != 200:
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990061"]["logMessage"], kmsKeyId))
                    error_info = {
                        "errorCode": "990061",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["990061"]["message"], "990061")
                    }

            # 05.共通エラーチェック処理
            # 05-01.以下の引数で共通エラーチェック処理を実行する
            # 05-02.例外が発生した場合、例外処理に遷移
            if error_info is not None:
                common_util.common_error_check(error_info)

            # 06.KMSキー情報削除予定作成処理
            # 06-01.KMSのキー情報を削除する
            for _ in range(5):
                schedule_key_deletion_response = self.client.schedule_key_deletion(
                    KeyId=kmsKeyId,
                    PendingWindowInDays=7
                )
                if schedule_key_deletion_response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                    break
            # 06-02.KMS削除処理に失敗した場合、「変数．エラー情報」を作成してエラーログをCloudWatchにログ出力する
            if schedule_key_deletion_response["ResponseMetadata"]["HTTPStatusCode"] != 200:
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990061"]["logMessage"], kmsKeyId))
                error_info = {
                    "errorCode": "990061",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["990061"]["message"], "990061")
                }

            # 07.レプリケート削除フラグチェック処理
            # 07-01.「引数．レプリケート削除フラグ」がtrueの場合、「08.別リージョンKMSキー情報無効化処理」に遷移する
            # 07-02.「引数．レプリケート削除フラグ」がfalseの場合、「09.共通エラーチェック処理」に遷移する
            if replicate_delete_flg:
                # 08.別リージョンKMSキー情報削除予定作成処理
                # 08-01.別のリージョンのKMSのキー情報を削除する
                for _ in range(5):
                    schedule_key_deletion_response = self.another_client.schedule_key_deletion(
                        KeyId=kmsKeyId,
                        PendingWindowInDays=7
                    )
                    if schedule_key_deletion_response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                        break
                # 08-02.別のリージョンのKMS削除処理に失敗した場合、「変数．エラー情報」を作成してエラーログをCloudWatchにログ出力する
                if schedule_key_deletion_response["ResponseMetadata"]["HTTPStatusCode"] != 200:
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990061"]["logMessage"], kmsKeyId))
                    error_info = {
                        "errorCode": "990061",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["990061"]["message"], "990061")
                    }

            # 09.共通エラーチェック処理
            # 09-01.以下の引数で共通エラーチェック処理を実行する
            # 09-02.例外が発生した場合、例外処理に遷移
            if error_info is not None:
                common_util.common_error_check(error_info)

            # 10.終了処理
            # 10-01.処理を終了する
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))

        # 例外処理（PDSExceptionクラス）：
        except PDSException as e:
            # PDSExceptionオブジェクトをエラーとしてスローする
            raise e
        # 例外処理：
        except Exception as e:
            # エラー情報をCloudWatchへログ出力する
            self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["999999"]["logMessage"], str(e), traceback.format_exc()))
            # 下記のパラメータでPDSExceptionオブジェクトを作成する
            # PDSExceptionオブジェクトをエラーとしてスローする
            raise PDSException(
                {
                    "errorCode": "999999",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
                }
            )
