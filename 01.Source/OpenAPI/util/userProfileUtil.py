import base64
from logging import Logger
import traceback
import asyncio
from Crypto.Cipher import AES
import math
import logging
from fastapi import Request

# Exceptionクラス
from exceptionClass.PDSException import PDSException

# Utilクラス
import util.logUtil as logUtil
import util.checkUtil as checkUtil
import util.commonUtil as commonUtil
from util.commonUtil import CommonUtilClass
from util.postgresDbUtil import PostgresDbUtilClass
# from util.s3Util import s3UtilClass
from util.s3AioUtil import s3AioUtilClass
from util.kmsUtil import KmsUtilClass
from util.fileUtil import BinaryStreamClass

# 定数クラス
from const.systemConst import SystemConstClass
from const.messageConst import MessageConstClass
from const.sqlConst import SqlConstClass


class UserProfileUtilClass:

    def __init__(self, logger):
        self.logger: Logger = logger
        self.common_util = CommonUtilClass(self.logger)

    async def insert_binary_data(
        self,
        binaryInsertData: dict,
        userProfileKmsId: str,
        bucketName: str,
        pdsUserDbInfo: dict
    ):
        """
        個人情報バイナリデータ登録処理

        Args:
            binaryInsertData (dict): バイナリ登録データ
            userProfileKmsId (str): 個人情報暗号・復号化用KMSID
            bucketName (str): バケット名
            pdsUserDbInfo (dict): PDSユーザDB接続情報

        Returns:
            result: 処理結果
            errorInfo: エラー情報リスト
        """
        EXEC_NAME_JP = "個人情報バイナリデータ登録処理"
        try:
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_IN_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            error_info_list = []
            # 01.引数検証処理（入力チェック）
            # 01-01.「引数．バイナリ登録データ．トランザクションID」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(binaryInsertData["transaction_id"]):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "バイナリ登録データ．トランザクションID"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "バイナリ登録データ．トランザクションID")
                    }
                )

            # 01-02.「引数．バイナリ登録データ．保存画像インデックス」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報
            if not checkUtil.check_require(binaryInsertData["save_image_idx"]):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "バイナリ登録データ．保存画像インデックス"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "バイナリ登録データ．保存画像インデックス")
                    }
                )

            # 01-03.「引数．バイナリ登録データ．バイナリデータ」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(binaryInsertData["save_image_data"]):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "バイナリ登録データ．バイナリデータ"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "バイナリ登録データ．バイナリデータ")
                    }
                )

            # 01-04.「引数．バイナリ登録データ．ハッシュ値」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(binaryInsertData["save_image_data_hash"]):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "バイナリ登録データ．ハッシュ値"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "バイナリ登録データ．ハッシュ値")
                    }
                )

            # 01-05.「引数．バイナリ登録データ．有効フラグ」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(binaryInsertData["valid_flg"]):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "バイナリ登録データ．有効フラグ"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "バイナリ登録データ．有効フラグ")
                    }
                )

            # 01-06.「引数．バイナリ登録データ．表示順」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(binaryInsertData["save_image_data_array_index"]):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "バイナリ登録データ．表示順"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "バイナリ登録データ．表示順")
                    }
                )

            # 01-07.「引数．個人情報暗号・復号化用KMSID」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(userProfileKmsId):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "個人情報暗号・復号化用KMSID"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "個人情報暗号・復号化用KMSID")
                    }
                )

            # 01-08.「引数．バケット名」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(bucketName):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "バケット名"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "バケット名")
                    }
                )

            # 01-09.「引数．PDSユーザDB接続情報」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(pdsUserDbInfo):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "PDSユーザDB接続情報"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "PDSユーザDB接続情報")
                    }
                )

            # 01-10.「変数．エラー情報リスト」に値が設定されている場合、エラー作成処理を実施する
            if len(error_info_list) != 0:
                # 01-10-01.下記のパラメータでPDSExceptionオブジェクトを作成する
                # 01-10-02.PDSExceptionオブジェクトをエラーとしてスローする
                raise PDSException(*error_info_list)

            # 02.バイナリデータ分割処理
            # 02-01.バイナリデータ容量チェック
            data_byte = binaryInsertData["save_image_data"].encode("utf-8")
            byte_size = len(data_byte)
            # 02-01-01.「変数．バイナリデータ」のデータサイズが2MB以下の場合、「変数．バイナリデータ」のデータサイズの半分の値を、「変数．チャンクサイズ」に格納する
            if byte_size <= SystemConstClass.SPLIT_BYTE_CHUNK_SIZE:
                split_chunk_size = math.ceil(byte_size / 2)
            # 02-01-02.「変数．バイナリデータ」のデータサイズが2MB超過の場合、2MBを「変数．チャンクサイズ」に格納する
            else:
                split_chunk_size = SystemConstClass.SPLIT_BYTE_CHUNK_SIZE

            # 02-02.バイナリデータ分割
            split_binary_list = []
            # 02-02-01.「変数．バイナリデータ」を「変数．チャンクサイズ」ごとに分割する
            # 02-02-02.分割結果を「変数．分割バイナリデータリスト」に格納する
            total_split_count = math.ceil(byte_size / split_chunk_size)
            for split_count in range(total_split_count):
                if split_count == total_split_count - 1:
                    split_binary_list.append(data_byte[split_count * split_chunk_size:])
                else:
                    split_binary_list.append(data_byte[split_count * split_chunk_size:(split_count + 1) * split_chunk_size])

            # 03.PDSユーザDB接続準備処理
            # 03-01.「引数．PDSユーザDB接続情報」を利用して、PDSユーザDBに対してのコネクションを作成する
            pds_user_db_connection_resource: PostgresDbUtilClass = PostgresDbUtilClass(
                logger=self.logger,
                end_point=pdsUserDbInfo["host"],
                port=pdsUserDbInfo["port"],
                user_name=pdsUserDbInfo["username"],
                password=pdsUserDbInfo["password"],
                region=SystemConstClass.AWS_CONST["REGION"]
            )
            pds_user_db_connection = pds_user_db_connection_resource.create_connection(
                SystemConstClass.PDS_USER_DB_NAME
            )

            for save_image_data_unique_check_count in range(5):
                # 04.保存したいバイナリデータID生成処理
                # 04-01.UUID ( v4ハイフンなし) を作成して、「変数．バイナリデータID」に格納する
                binary_data_id = commonUtil.get_uuid_no_hypen()

                # 05.保存したいバイナリデータID一意検証処理
                save_image_data_unique_check_error_info = None
                # 05-01.個人情報バイナリデータテーブルと個人情報バイナリ分割データテーブルからデータを取得し、「変数．保存画像一意検証データリスト」に全レコードをタプルのリストとして格納する
                save_image_data_unique_check_result = pds_user_db_connection_resource.select_tuple_list(
                    pds_user_db_connection,
                    SqlConstClass.USER_PROFILE_BINARY_UNIQUE_CHECK_SAVE_IMAGE_DATA_ID_SQL,
                    binary_data_id,
                    binary_data_id
                )

                # 05-02.「変数．保存画像一意検証データリスト」が0件の場合、処理成功としてループ処理を抜ける
                if save_image_data_unique_check_result["result"] and save_image_data_unique_check_result["rowCount"] == 0:
                    break

                # 05-03.「変数．保存画像一意検証データリスト」が0件以外 かつ 一意検証ループ数が5回目の場合、「変数.エラー情報」を作成して、失敗処理としてループを抜ける
                if save_image_data_unique_check_result["result"] and save_image_data_unique_check_result["rowCount"] != 0:
                    if save_image_data_unique_check_count == 4:
                        self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["030001"]["logMessage"], "保存したいバイナリデータID", binary_data_id))
                        save_image_data_unique_check_error_info = {
                            "errorCode": "030001",
                            "message": logUtil.message_build(MessageConstClass.ERRORS["030001"]["message"], "保存したいバイナリデータID", binary_data_id)
                        }
                        break

                # 05-04.処理が失敗した場合は「postgresqlエラー処理」からのレスポンスを、「変数．エラー情報」に格納し、失敗処理としてループを抜ける
                if not save_image_data_unique_check_result["result"]:
                    save_image_data_unique_check_error_info = self.common_util.create_postgresql_log(
                        save_image_data_unique_check_result["errorObject"],
                        None,
                        None,
                        save_image_data_unique_check_result["stackTrace"]
                    ).get("errorInfo")
                    break

            # 06.保存したいバイナリデータID一意検証チェック処理
            # 06-01.「変数．エラー情報」がNullの場合、「08.トランザクション作成処理」に遷移する
            # 06-02.「変数．エラー情報」がNull以外の場合、「07.保存したいバイナリデータID一意検証エラー処理」に遷移する
            if save_image_data_unique_check_error_info is not None:
                # 07.保存したいバイナリデータID一意検証エラー処理
                # 07-01.レスポンス情報整形処理
                # 07-01-01.以下をレスポンスとして返却する
                if logging.ERROR == logUtil.output_outlog(EXEC_NAME_JP, save_image_data_unique_check_error_info):
                    self.logger.error(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                else:
                    self.logger.warning(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                return {
                    "result": False,
                    "errorInfo": save_image_data_unique_check_error_info
                }

            # 08.トランザクション作成処理
            # 08-01.「個人情報バイナリデータ登録トランザクション」を作成する

            # 09.個人情報バイナリデータ登録処理
            pds_user_profile_binary_insert_error_info = None
            # 09-01.個人情報バイナリデータテーブルに登録する
            pds_user_profile_binary_insert_result = pds_user_db_connection_resource.insert(
                pds_user_db_connection,
                SqlConstClass.USER_PROFILE_BINARY_INSERT_SQL,
                binaryInsertData["transaction_id"],
                binaryInsertData["save_image_idx"],
                binary_data_id,
                binaryInsertData["save_image_data_hash"],
                len(split_binary_list),
                SystemConstClass.CHUNK_SIZE,
                binaryInsertData["valid_flg"],
                binaryInsertData["save_image_data_array_index"],
                byte_size
            )

            # 09-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not pds_user_profile_binary_insert_result["result"]:
                pds_user_profile_binary_insert_error_info = self.common_util.create_postgresql_log(
                    pds_user_profile_binary_insert_result["errorObject"],
                    "トランザクションID",
                    binaryInsertData["transaction_id"],
                    pds_user_profile_binary_insert_result["stackTrace"]
                ).get("errorInfo")

            # 10.個人情報バイナリデータ登録チェック処理
            # 10-01.「変数．エラー情報」がNullの場合、「13.トランザクションコミット処理」に遷移する
            # 10-02.「変数．エラー情報」がNull以外の場合、「11.トランザクションロールバック処理」に遷移する
            if pds_user_profile_binary_insert_error_info is not None:
                # 11.トランザクションロールバック処理
                # 11-01.「個人情報バイナリデータ登録トランザクション」をロールバックする
                self.common_util.common_check_postgres_rollback(pds_user_db_connection, pds_user_db_connection_resource)

                # 12.個人情報バイナリデータ登録エラー処理
                # 12-01.レスポンス情報整形処理
                # 12-01-01.以下をレスポンスとして返却する
                if logging.ERROR == logUtil.output_outlog(EXEC_NAME_JP, pds_user_profile_binary_insert_error_info):
                    self.logger.error(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                else:
                    self.logger.warning(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                return {
                    "result": False,
                    "errorInfo": pds_user_profile_binary_insert_error_info
                }
            # 13.トランザクションコミット処理
            # 13-01.「個人情報バイナリデータ登録トランザクション」をコミットする
            pds_user_db_connection_resource.commit_transaction(pds_user_db_connection)
            pds_user_db_connection_resource.close_connection(pds_user_db_connection)

            binary_separate_data_insert_list = []
            for separate_No, binary_data in enumerate(split_binary_list):
                # 14.個人情報バイナリ分割データ登録処理リスト作成処理
                binary_separate_data_insert_list.append(
                    self.insert_binary_separate_data(
                        transactionId=binaryInsertData["transaction_id"],
                        binaryDataId=binary_data_id,
                        sepNo=separate_No,
                        binarySeparateData=binary_data,
                        userProfileKmsId=userProfileKmsId,
                        bucketName=bucketName,
                        pdsUserDbInfo=pdsUserDbInfo
                    )
                )

            # 15.個人情報バイナリ分割データ登録処理実行処理
            # 15-01.「変数．個人情報バイナリ分割データ登録処理リスト」をもとに、個人情報バイナリ分割データ登録処理を並列で実行する
            # 15-02.レスポンスを「変数．個人情報バイナリ分割データ登録処理実行結果リスト」に格納する
            binary_separate_data_insert_result_list = await asyncio.gather(*binary_separate_data_insert_list)

            # 16.個人情報バイナリ分割データ登録処理実行処理チェック処理
            result_list = [d.get("result") for d in binary_separate_data_insert_result_list]
            # 16-01.「変数．個人情報バイナリ分割データ登録処理実行結果リスト[]．処理結果」にfalseが存在する場合、「17.個人情報バイナリ分割データ登録処理実行処理エラー処理」に遷移する
            # 16-02.「変数．個人情報バイナリ分割データ登録処理実行結果リスト[]．処理結果」にfalseが存在しない場合、「18.終了処理」に遷移する
            if False in result_list:
                # 17.個人情報バイナリ分割データ登録処理実行処理エラー処理
                # 17-01.返却パラメータを作成し、返却する
                errorInfoList = []
                for result_info in binary_separate_data_insert_result_list:
                    if result_info.get("errorInfo"):
                        errorInfoList.append(result_info["errorInfo"])

                if logging.ERROR == logUtil.output_outlog(EXEC_NAME_JP, errorInfoList):
                    self.logger.error(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                else:
                    self.logger.warning(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                return {
                    "result": False,
                    "errorInfo": errorInfoList
                }
            else:
                # 18.終了処理
                # 18-01.返却パラメータを作成し、返却する
                self.logger.info(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                return {
                    "result": True,
                    "errorInfo": None
                }
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

    async def insert_binary_separate_data(
        self,
        transactionId: str,
        binaryDataId: str,
        sepNo: int,
        binarySeparateData: str,
        userProfileKmsId: str,
        bucketName: str,
        pdsUserDbInfo: dict
    ):
        """
        個人情報バイナリ分割データ登録処理

        Args:
            transactionId (str): トランザクションID
            binaryDataId (str): バイナリデータID
            sepNo (int): セパレートNo
            binarySeparateData (dict): 分割バイナリデータ
            userProfileKmsId (str): 個人情報暗号・復号化用KMSID
            bucketName (str): バケット名
            pdsUserDbInfo (dict): PDSユーザDB接続情報

        Returns:
            result: 処理結果
            errorInfo: エラー情報リスト
        """
        EXEC_NAME_JP = "個人情報バイナリ分割データ登録処理"
        try:
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_IN_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            error_info_list = []
            # 01.引数検証処理（入力チェック）
            # 01-01.「引数．トランザクションID」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(transactionId):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "トランザクションID"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "トランザクションID")
                    }
                )
            # 01-02.「引数．バイナリデータID」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(binaryDataId):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "バイナリデータID"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "バイナリデータID")
                    }
                )
            # 01-03.「引数．セパレートNo」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(sepNo):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "セパレートNo"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "セパレートNo")
                    }
                )
            # 01-04.「引数．分割バイナリデータ」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(binarySeparateData):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "分割バイナリデータ"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "分割バイナリデータ")
                    }
                )
            # 01-05.「引数．個人情報暗号・復号化用KMSID」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(userProfileKmsId):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "個人情報暗号・復号化用KMSID"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "個人情報暗号・復号化用KMSID")
                    }
                )
            # 01-06.「引数．バケット名」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(bucketName):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "バケット名"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "バケット名")
                    }
                )
            # 01-07.「引数．PDSユーザDB接続情報」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(pdsUserDbInfo):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "PDSユーザDB接続情報"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "PDSユーザDB接続情報")
                    }
                )

            # 01-08.「変数．エラー情報リスト」に値が設定されている場合、エラー作成処理を実施する
            if len(error_info_list) != 0:
                # 01-08-01.下記のパラメータでPDSExceptionオブジェクトを作成する
                # 01-08-02.PDSExceptionオブジェクトをエラーとしてスローする
                raise PDSException(*error_info_list)

            # 02.分割バイナリファイル情報作成処理
            # 02-01.以下の引数で分割バイナリファイル情報作成処理を実行する
            # 02-02.レスポンスを、「変数．分割バイナリファイル情報作成処理実行結果」に格納する
            create_binary_separate_file_result = self.create_binary_separate_file(
                transactionId=transactionId,
                splitImage=binarySeparateData,
                userProfileKmsId=userProfileKmsId,
                binaryDataId=binaryDataId,
                sepNo=sepNo
            )

            # 03.分割バイナリファイル情報作成チェック処理
            # 03-01.「変数．エラー情報」がNullの場合、「05.PDSユーザDB接続準備処理」に遷移する
            # 03-02.「変数．エラー情報」がNull以外の場合、「04.分割バイナリファイル情報作成エラー処理」に遷移する
            if create_binary_separate_file_result.get("errorInfo"):
                # 04.分割バイナリファイル情報作成エラー処理
                # 04-01.レスポンス情報整形処理
                # 04-01-01.以下をレスポンスとして返却する
                return {
                    "result": False,
                    "errorInfo": create_binary_separate_file_result["errorInfo"]
                }

            # 05.PDSユーザDB接続準備処理
            # 05-01.「引数．PDSユーザDB接続情報」を利用して、PDSユーザDBに対してのコネクションを作成する
            pds_user_db_connection_resource: PostgresDbUtilClass = PostgresDbUtilClass(
                logger=self.logger,
                end_point=pdsUserDbInfo["host"],
                port=pdsUserDbInfo["port"],
                user_name=pdsUserDbInfo["username"],
                password=pdsUserDbInfo["password"],
                region=SystemConstClass.AWS_CONST["REGION"]
            )
            pds_user_db_connection = pds_user_db_connection_resource.create_connection(
                SystemConstClass.PDS_USER_DB_NAME
            )

            # 06.トランザクション作成処理
            # 06-01.「個人情報バイナリ分割データ登録トランザクション」を作成する

            # 07.個人情報バイナリ分割データ登録処理
            pds_user_profile_binary_separate_insert_error_info = None
            # 07-01.個人情報バイナリ分割データテーブルに登録する
            pds_user_profile_binary_separate_insert_result = pds_user_db_connection_resource.insert(
                pds_user_db_connection,
                SqlConstClass.USER_PROFILE_BINARY_SEPARATE_INSERT_SQL,
                binaryDataId,
                sepNo,
                create_binary_separate_file_result["fileSavePath"],
                create_binary_separate_file_result["kmsChiperDataKey"],
                create_binary_separate_file_result["chiperNonce"]
            )

            # 07-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not pds_user_profile_binary_separate_insert_result["result"]:
                pds_user_profile_binary_separate_insert_error_info = self.common_util.create_postgresql_log(
                    pds_user_profile_binary_separate_insert_result["errorObject"],
                    "保存画像データID",
                    binaryDataId,
                    pds_user_profile_binary_separate_insert_result["stackTrace"]
                ).get("errorInfo")

            # 08.個人情報バイナリ分割データ登録チェック処理
            # 08-01.「変数．エラー情報」がNullの場合、「11.トランザクションコミット処理」に遷移する
            # 08-02.「変数．エラー情報」がNull以外の場合、「09.トランザクションロールバック処理」に遷移する
            if pds_user_profile_binary_separate_insert_error_info is not None:
                # 09.トランザクションロールバック処理
                # 09-01.「個人情報バイナリ分割データ登録トランザクション」をロールバックする
                self.common_util.common_check_postgres_rollback(pds_user_db_connection, pds_user_db_connection_resource)

                # 10.個人情報バイナリデータ登録エラー処理
                # 10-01.レスポンス情報整形処理
                # 10-01-01.以下をレスポンスとして返却する
                if logging.ERROR == logUtil.output_outlog(EXEC_NAME_JP, pds_user_profile_binary_separate_insert_error_info):
                    self.logger.error(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                else:
                    self.logger.warning(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                return {
                    "result": False,
                    "errorInfo": pds_user_profile_binary_separate_insert_error_info
                }

            # 11.トランザクションコミット処理
            # 11-01.「個人情報バイナリ分割データ登録トランザクション」をコミットする
            pds_user_db_connection_resource.commit_transaction(pds_user_db_connection)
            pds_user_db_connection_resource.close_connection(pds_user_db_connection)

            # 12.分割バイナリデータ保存処理
            put_file_error_info = None
            # 12-01.「変数．分割バイナリファイル情報作成処理実行結果．保存先パス」をキーに「変数．分割バイナリファイル情報作成処理'実行結果．格納用ファイル」をS3（バケット名：「引数．バケット名」）に格納する
            s3_util = s3AioUtilClass(self.logger, bucketName)
            for put_count in range(5):
                put_result = await s3_util.async_put_file(file_name=create_binary_separate_file_result["fileSavePath"], data=create_binary_separate_file_result["uploadFile"].get_temp_binary())
                if put_result:
                    break
                if put_count == 4:
                    # 12-2.処理が失敗した場合は「変数．エラー情報」を作成し、エラーログをCloudWatchにログ出力する
                    # 12-02-01.S3へのファイルコピーエラーが発生した場合、「変数．エラー情報」にエラー情報を追加する
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990021"]["logMessage"]))
                    put_file_error_info = {
                        "errorCode": "990021",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["990021"]["message"], "990021")
                    }

            # 13.分割バイナリデータ保存チェック処理
            # 13-01.「変数．エラー情報」がNullの場合、「15.終了処理」に遷移する
            # 13-02.「変数．エラー情報」がNull以外の場合、「14.分割バイナリデータ保存エラー処理」に遷移する
            if put_file_error_info is not None:
                # 14.分割バイナリデータ保存エラー処理
                # 14-01.レスポンス情報整形処理
                # 14-01-01.以下をレスポンスとして返却する
                # 14-02.処理を終了する
                if logging.ERROR == logUtil.output_outlog(EXEC_NAME_JP, put_file_error_info):
                    self.logger.error(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                else:
                    self.logger.warning(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
                return {
                    "result": False,
                    "errorInfo": put_file_error_info
                }

            # 15.終了処理
            # 15-01.返却パラメータを作成し、返却する
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            return {
                "result": True,
                "errorInfo": None
            }

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

    def create_binary_separate_file(
        self,
        transactionId: str,
        splitImage: str,
        userProfileKmsId: str,
        binaryDataId: str,
        sepNo: int
    ):
        """
        分割バイナリファイル情報作成処理

        Args:
            transactionId (str): トランザクションID
            splitImage (str): 分割バイナリデータ
            userProfileKmsId (str): 個人情報暗号・復号化用KMSID
            binaryDataId (str): 保存画像ID
            sepNo (int): セパレートNo

        Returns:
            result: 処理結果
            fileSavePath: 保存先パス
            uploadFile: アップロード対象ファイル
            kmsChiperDataKey: 暗号化済データキー
            chiperNonce: ノンス
        """
        EXEC_NAME_JP = "分割バイナリファイル情報作成処理"
        try:
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_IN_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            error_info_list = []
            # 01.引数検証処理（入力チェック）
            # 01-01.「引数．トランザクションID」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(transactionId):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "トランザクションID"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "トランザクションID")
                    }
                )
            # 01-02.「引数．分割バイナリデータ」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(splitImage):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "分割バイナリデータ"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "分割バイナリデータ")
                    }
                )
            # 01-03.「引数．個人情報暗号・復号化用KMSID」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(userProfileKmsId):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "個人情報暗号・復号化用KMSID"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "個人情報暗号・復号化用KMSID")
                    }
                )
            # 01-04.「引数．保存画像ID」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(binaryDataId):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "保存画像ID"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "保存画像ID")
                    }
                )
            # 01-05.「引数．セパレートNo」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(sepNo):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "セパレートNo"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "セパレートNo")
                    }
                )
            # 01-06.「変数．エラー情報リスト」に値が設定されている場合、エラー作成処理を実施する
            if len(error_info_list) != 0:
                # 01-06-01.下記のパラメータでPDSExceptionオブジェクトを作成する
                # 01-06-02.PDSExceptionオブジェクトをエラーとしてスローする
                raise PDSException(*error_info_list)

            # 02.KMSデータキー発行処理
            # 02-01.KMSの「引数．個人情報暗号・復号化用KMSID」からデータキーを作成し、「変数．KMSデータキー」に格納する
            kms_util = KmsUtilClass(self.logger)
            error_info = None
            for error_count in range(5):
                try:
                    data_key = kms_util.generate_kms_data_key(userProfileKmsId)
                    break
                except Exception:
                    if error_count == 4:
                        self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990065"]["logMessage"], userProfileKmsId))
                        error_info = {
                            "errorCode": "990065",
                            "message": logUtil.message_build(MessageConstClass.ERRORS["990065"]["message"], "990065")
                        }
                        break

            # 03.KMSデータキー発行チェック処理
            # 03-01.「変数．エラー情報」がNullの場合、「05.分割バイナリデータ暗号化処理」に遷移する
            # 03-02.「変数．エラー情報」がNull以外の場合、「04.KMSデータキー発行エラー処理」に遷移する
            if error_info is not None:
                # 04.KMSデータキー発行エラー処理
                # 04-01.レスポンス情報整形処理
                # 04-01-01.以下をレスポンスとして返却する
                return {
                    "result": False,
                    "errorInfo": error_info
                }

            # 05.分割バイナリデータ暗号化処理
            # 05-01.「変数．KMSデータキー['Plaintext']」をもとに暗号化モジュール作成し、「変数．暗号化モジュール」に格納する
            aes = AES.new(data_key['Plaintext'], AES.MODE_GCM)
            # 05-02.「引数．分割バイナリデータ」を「変数．暗号化モジュール」で暗号化し、「変数．暗号化分割バイナリデータ」に格納する
            encrypt_data = aes.encrypt(splitImage)

            # 06.分割バイナリデータ格納準備処理
            # 06-01.「変数．暗号化分割バイナリデータ」をもとに「変数．格納用ファイル」を作成する
            upload_file = BinaryStreamClass(encrypt_data)
            # 06-02.「引数．保存したいバイナリデータID」と「引数．セパレートNo」をもとに「変数．格納用ファイル名」を作成する
            file_name = binaryDataId + "_" + str(sepNo)
            # 06-03.「引数．トランザクションID」と「変数．格納用ファイル名」をもとに保存先パスを作成し、「変数．保存先パス」に格納する
            file_path = transactionId + "/" + file_name

            # 07.終了処理
            # 07-01.返却パラメータを作成し、返却する
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            return {
                "result": True,
                "fileSavePath": file_path,
                "uploadFile": upload_file,
                "kmsChiperDataKey": base64.b64encode(data_key['CiphertextBlob']).decode(),
                "chiperNonce": base64.b64encode(aes.nonce).decode()
            }

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

    async def get_binary_data(
        self,
        pdsUserInfo: dict,
        fileSavePathList: list,
        kmsDataKeyList: list,
        chiperNonceList: list,
        apiType: str,
        request: Request,
        requestBody: dict
    ):
        """
        バイナリデータ取得処理

        Args:
            pdsUserInfo (dict): PDSユーザ情報
            fileSavePathList (list): 保存先パスリスト
            kmsDataKeyList (list): KMSデータキーリスト
            chiperNonceList (list): 暗号化ワンタイムパスワードリスト
            apiType (str): API種別
            request (Request): リクエスト情報
            requestBody (dict): リクエストボディ(辞書型)

        Returns:
            result: 処理結果
            binaryData: バイナリデータ
        """
        EXEC_NAME_JP = "バイナリデータ取得処理"
        try:
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_IN_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            error_info_list = []
            # 01.引数検証処理（入力チェック）
            # 01-01.「引数．PDSユーザ情報」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(pdsUserInfo):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "PDSユーザ情報"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "PDSユーザ情報")
                    }
                )

            # 01-02.「引数．保存先パスリスト」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require_list_str(fileSavePathList):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "保存先パスリスト"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "保存先パスリスト")
                    }
                )

            # 01-03.「引数．KMSデータキーリスト」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require_list_str(kmsDataKeyList):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "KMSデータキーリスト"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "KMSデータキーリスト")
                    }
                )

            # 01-04.「引数．暗号化ワンタイムパスワードリスト」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require_list_str(chiperNonceList):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "暗号化ワンタイムパスワードリスト"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "暗号化ワンタイムパスワードリスト")
                    }
                )

            # 01-05.「引数．API種別」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(apiType):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "API種別"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "API種別")
                    }
                )

            # 01-06.「引数．リクエスト情報」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(request):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "リクエスト情報"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "リクエスト情報")
                    }
                )

            # 01-07.「引数．リクエストボディ」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(requestBody):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "リクエストボディ"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "リクエストボディ")
                    }
                )

            # 01-08.「変数．エラー情報リスト」に値が設定されている場合、エラー作成処理を実施する
            if len(error_info_list) != 0:
                # 01-08-01.下記のパラメータでPDSExceptionオブジェクトを作成する
                # 01-08-02.PDSExceptionオブジェクトをエラーとしてスローする
                raise PDSException(*error_info_list)

            # 02.個人バイナリ情報復号処理リスト初期化処理
            # 02-01.「変数．個人バイナリ情報復号処理リスト」を初期化する
            get_binary_decrypt_exec_list = []

            for binary_separete_loop_no, file_save_path in enumerate(fileSavePathList):
                # 03.個人バイナリ情報復号処理リスト作成処理
                # 03-01.「変数．個人バイナリ情報復号処理リスト」に個人バイナリ情報復号処理を追加する
                get_binary_decrypt_exec_list.append(
                    self.get_binary_decrypt(
                        pdsUserInfo=pdsUserInfo,
                        fileSavePath=file_save_path,
                        kmsDataKey=kmsDataKeyList[binary_separete_loop_no],
                        chiperNonce=chiperNonceList[binary_separete_loop_no],
                        apiType=apiType,
                        request=request,
                        requestBody=requestBody
                    )
                )

            # 04.個人バイナリ情報復号処理実行処理
            # 04-01.「変数．個人バイナリ情報復号処理リスト」をもとに、個人バイナリ情報復号処理を並列で実行する
            # 04-02.レスポンスを「変数．個人バイナリ情報復号処理実行結果リスト」に格納する
            get_binary_decrypt_exec_result_list = await asyncio.gather(*get_binary_decrypt_exec_list)

            # 05.共通エラーチェック処理
            result_list = [d.get("result") for d in get_binary_decrypt_exec_result_list]
            if False in result_list:
                # 05-01.以下の引数で共通エラーチェック処理を実行する
                # 05-02.例外が発生した場合、例外処理に遷移
                # エラー情報
                error_info_list = []
                for result_info in get_binary_decrypt_exec_result_list:
                    if result_info.get("errorInfo"):
                        if type(result_info["errorInfo"]) is list:
                            error_info_list.extend(result_info["errorInfo"])
                        else:
                            error_info_list.append(result_info["errorInfo"])
                return {
                    "result": False,
                    "errorInfo": error_info_list
                }

            # 06.データ結合処理
            # 06-01.リスト形式で返却されたレスポンスのバイナリデータを変数に結合していく
            binary_data_list = [d.get("decryptionData") for d in get_binary_decrypt_exec_result_list]
            binary_data = "".join(binary_data_list)

            # 07.終了処理
            # 07-01.返却パラメータを作成し、返却する
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            return {
                "result": True,
                "binaryData": binary_data
            }

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

    async def get_binary_decrypt(
        self,
        pdsUserInfo: dict,
        fileSavePath: str,
        kmsDataKey: str,
        chiperNonce: str,
        apiType: str,
        request: Request,
        requestBody: dict
    ):
        """
        個人バイナリ情報復号処理

        Args:
            pdsUserInfo (dict): PDSユーザ情報
            fileSavePath (list): 保存先パス
            kmsDataKey (list): KMSデータキー
            chiperNonce (list): 暗号化ワンタイムパスワード
            apiType (str): API種別
            request (Request): リクエスト情報
            requestBody (dict): リクエストボディ

        Returns:
            result: 処理結果
            decryptionData: 復号化データ
        """
        EXEC_NAME_JP = "個人バイナリ情報復号処理"
        try:
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_IN_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            # 01.引数検証処理（入力チェック）
            error_info_list = []
            # 01-01.「引数．PDSユーザ情報」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(pdsUserInfo):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "PDSユーザ情報"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "PDSユーザ情報")
                    }
                )

            # 01-02.「引数．保存先パス」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(fileSavePath):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "保存先パス"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "保存先パス")
                    }
                )

            # 01-03.「引数．KMSデータキー」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(kmsDataKey):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "KMSデータキー"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "KMSデータキー")
                    }
                )

            # 01-04.「引数．暗号化ワンタイムパスワード」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(chiperNonce):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "暗号化ワンタイムパスワード"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "暗号化ワンタイムパスワード")
                    }
                )

            # 01-05.「引数．API種別」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(apiType):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "API種別"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "API種別")
                    }
                )

            # 01-06.「引数．リクエスト情報」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(request):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "リクエスト情報"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "リクエスト情報")
                    }
                )

            # 01-07.「引数．リクエストボディ」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(requestBody):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "リクエストボディ"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "リクエストボディ")
                    }
                )

            # 01-08.「変数．エラー情報リスト」に値が設定されている場合、エラー作成処理を実施する
            if len(error_info_list) != 0:
                # 01-08-01.下記のパラメータでPDSExceptionオブジェクトを作成する
                # 01-08-02.PDSExceptionオブジェクトをエラーとしてスローする
                raise PDSException(*error_info_list)

            # 02.S3からファイル取得
            get_file_error_info = None
            s3_util = s3AioUtilClass(logger=self.logger, bucket_name=pdsUserInfo["s3ImageDataBucketName"])
            for error_count in range(5):
                try:
                    # 02-01.「引数．保存先パス」のファイルS3から取得し、「変数．バイナリデータ」に格納する
                    binary_data = await s3_util.get_file(file_name=fileSavePath)
                    break
                except Exception:
                    # 02-02.処理が失敗した場合は「変数．エラー情報」を作成し、エラーログをCloudWatchにログ出力する
                    # 02-02-01.S3のファイル取得に失敗した場合、「変数．エラー情報」にエラー情報を追加する
                    if error_count == 4:
                        self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990024"]["logMessage"], pdsUserInfo["s3ImageDataBucketName"], fileSavePath))
                        get_file_error_info = {
                            "errorCode": "990024",
                            "message": logUtil.message_build(MessageConstClass.ERRORS["990024"]["message"], "990024")
                        }
                        break

            # 03.共通エラーチェック処理
            # 03-01.以下の引数で共通エラーチェック処理を実行する
            # 03-02.例外が発生した場合、例外処理に遷移
            if get_file_error_info is not None:
                return {
                    "result": False,
                    "errorInfo": get_file_error_info
                }

            # 04.データキー復号化処理
            error_info = None
            kms_util = KmsUtilClass(logger=self.logger)
            for error_count in range(5):
                try:
                    # 04-01.暗号化されたデータキーを復号化し、「変数．復号データキー」に格納する
                    decrypt_data_key = kms_util.decrypt_kms_data_key(base64.b64decode(kmsDataKey.encode()))
                    break
                except Exception:
                    if error_count == 4:
                        self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990066"]["logMessage"]))
                        error_info = {
                            "errorCode": "990066",
                            "message": logUtil.message_build(MessageConstClass.ERRORS["990066"]["message"], "990066")
                        }
                        break

            # 05.共通エラーチェック処理
            # 05-01.以下の引数で共通エラーチェック処理を実行する
            # 05-02.例外が発生した場合、例外処理に遷移
            if error_info is not None:
                return {
                    "result": False,
                    "errorInfo": error_info
                }

            # 06.復号化処理
            # 06-01.「変数．バイナリデータ」を「変数．復号データキー」と「引数．暗号化ワンタイムパスワード」を使って復号化し、「変数．復号化データ」に格納する
            aes = AES.new(decrypt_data_key, AES.MODE_GCM, nonce=base64.b64decode(chiperNonce.encode()))
            decrypt_data = aes.decrypt(binary_data)

            # 07.終了処理
            # 07-01.レスポンス情報を作成し、返却する
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            return {
                "result": True,
                "decryptionData": decrypt_data.decode()
            }

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
