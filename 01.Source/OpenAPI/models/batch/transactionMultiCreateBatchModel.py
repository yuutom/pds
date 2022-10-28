import os
import json
from typing import Optional
import traceback
import base64
from logging import Logger
import shutil
import csv
import asyncio
import hashlib
# RequestBody
from pydantic import BaseModel
# util
from util.postgresDbUtil import PostgresDbUtilClass
from util.commonUtil import CommonUtilClass
import util.logUtil as logUtil
from util.callbackExecutorUtil import CallbackExecutor
from util.billUtil import BillUtilClass
from util.s3Util import s3UtilClass
from util.userProfileUtil import UserProfileUtilClass
from util.mongoDbUtil import MongoDbClass
import util.commonUtil as commonUtil
import util.checkUtil as checkUtil

# const
from const.systemConst import SystemConstClass
from const.messageConst import MessageConstClass
from const.sqlConst import SqlConstClass
# Exception
from exceptionClass.PDSException import PDSException


class requestBody(BaseModel):
    pdsUserId: Optional[str] = None


class transactionMultiCreateBatchModelClass():
    def __init__(self, logger):
        """
        コンストラクタ

        Args:
            logger (Logger): ロガー（TRACE）
        """
        self.logger: Logger = logger
        self.common_util = CommonUtilClass(logger)
        self.bill_util = BillUtilClass(logger)
        self.error_info = None

    async def main(self, request_body: requestBody):
        """
        個人情報一括登録バッチ メイン処理

        """
        try:
            # 03.共通DB接続準備処理
            # 03-01.AWS SecretsManagerから共通DB接続情報を取得して、「変数．共通DB接続情報」に格納する
            common_db_connection_resource: PostgresDbUtilClass = None
            # 03-02.「変数．共通DB接続情報」を利用して、共通DBに対してのコネクションを作成する
            common_db_info_response = self.common_util.get_common_db_info_and_connection()
            if not common_db_info_response["result"]:
                raise PDSException(common_db_info_response["errorInfo"])
            else:
                common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
                common_db_connection = common_db_info_response["common_db_connection"]

            # 04.PDSユーザ情報取得処理
            pds_user_select_error_info = None
            # 04-01.PDSユーザテーブルからPDSユーザ情報を取得し、「変数．PDSユーザ情報取得結果」に1レコードをタプルとして格納する
            pds_user_select_result = common_db_connection_resource.select_tuple_one(
                common_db_connection,
                SqlConstClass.MULTI_CREATE_BATCH_PDS_USER_SELECT_SQL,
                request_body.pdsUserId
            )
            # 04-02.「変数．PDSユーザ情報取得結果」が1件以外の場合、「変数.エラー情報」を作成する
            if pds_user_select_result["result"] and pds_user_select_result["rowcount"] != 1:
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020004"]["logMessage"], request_body.pdsUserId))
                pds_user_select_error_info = {
                    "errorCode": "020004",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020004"]["message"], request_body.pdsUserId)
                }
            # 04-03.処理が失敗した場合は、postgresqlエラー処理を実行する
            if not pds_user_select_result["result"]:
                pds_user_select_error_info = self.common_util.create_postgresql_log(
                    pds_user_select_result["errorObject"],
                    None,
                    None,
                    pds_user_select_result["stackTrace"]
                ).get("errorInfo")

            # 05.共通エラーチェック処理
            # 05-01.以下の引数で共通エラーチェック処理を実行する
            # 05-02.例外が発生した場合、例外処理に遷移
            if pds_user_select_error_info is not None:
                self.common_util.common_error_check(pds_user_select_error_info)

            # 返却するpdsUserInfoをtupleからdictに変換する
            pds_user_info_column_list = [
                'pdsUserId',
                'groupId',
                'pdsUserName',
                'pdsUserDomainName',
                'apiKey',
                'pdsUserInstanceSecretName',
                's3ImageDataBucketName',
                'userProfilerKmsId',
                'validFlg',
                'tokyo_a_mongodb_secret_name',
                'tokyo_c_mongodb_secret_name',
                'osaka_a_mongodb_secret_name',
                'osaka_c_mongodb_secret_name',
                'salesAddress',
                'downloadNoticeAddressTo',
                'downloadNoticeAddressCc',
                'deleteNoticeAddressTo',
                'deleteNoticeAddressCc',
                'credentialNoticeAddressTo',
                'credentialNoticeAddressCc'
            ]
            pds_user_info_data_list = pds_user_select_result["query_results"]
            pds_user_info_dict = {column: data for column, data in zip(pds_user_info_column_list, pds_user_info_data_list)}

            # 06.zipファイルチェック処理
            # 06-01.S3のバケット(バケット名：multi_register_bucket)から「パラメータ．PDSユーザID」をプレフィックスにして、配置されたzipファイルの存在を確認する
            # 06-02.レスポンスを「変数．zipファイルチェック処理実行結果」に格納する
            # 06-03.S3のファイル確認に失敗した場合、「変数．エラー情報」を作成する
            s3_util = s3UtilClass(self.logger, bucket_name=SystemConstClass.USER_PROFILE_MULTI_CREATE_BUCKET)
            check_result = s3_util.check_zip_file(file_prefix=request_body.pdsUserId + "/", file_suffix=SystemConstClass.USER_PROFILE_MULTI_CREATE_FILE_REGIX)

            # 07.共通エラーチェック処理
            # 07-01.以下の引数で共通エラーチェック処理を実行する
            # 07-02.例外が発生した場合、例外処理に遷移
            if check_result.get("errorInfo"):
                self.common_util.common_error_check(check_result.get("errorInfo"))

            # 08.zipファイルダウンロード処理
            # 08-01.S3のバケット(バケット名：multi_register_bucket)から「パラメータ．PDSユーザID」をプレフィックスにして、配置されたzipファイルをダウンロードする
            # 08-02.S3のダウンロード処理に失敗した場合、「変数．エラー情報」を作成する
            zip_file_name = check_result["key"].split('/')[-1]
            dir_name = '.'.join(zip_file_name.split('.')[:-1])
            download_result = s3_util.get_zip_file(check_result["key"], 'download/' + zip_file_name)

            # 09.共通エラーチェック処理
            # 09-01.以下の引数で共通エラーチェック処理を実行する
            # 09-02.例外が発生した場合、例外処理に遷移
            if download_result.get("errorInfo"):
                self.common_util.common_error_check(download_result.get("errorInfo"))

            # 10.zipファイル解凍処理
            # 10-01.ダウンロードしたzipファイルを解凍する
            # TODO(t.ii)：未完成。文字化け対応が不要であれば削除する
            # with zipfile.ZipFile('download/' + zip_file_name) as zipf:
            #     for zinfo in zipf.infolist():        # ZipInfoオブジェクトを取得
            #         if not zinfo.flag_bits == 0x800:  # flag_bitsプロパティで文字コードを取得
            #             # 文字コードが(cp437)だった場合はcp932へ変換する
            #             # strオブジェクトのプロパティencode/decodeでcp932に変換
            #             # 変換後のファイル名をfilenameプロパティで再度し直す
            #             zinfo.filename = zinfo.filename.encode('cp437').decode('cp932')
            #         zipf.extract(zinfo, 'out_dir')
            shutil.unpack_archive('download/' + zip_file_name, 'out_dir')

            # 10-02.解凍したファイルのルートフォルダからInsert.csvファイルを取得する
            csv_file = open("out_dir/" + dir_name + "/Insert.csv", "r", encoding="utf_8_sig", errors="", newline="")
            csv_rows = csv.DictReader(csv_file, delimiter=",", doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)
            # 10-03.「変数．ヘッダ情報リスト」にCSVのヘッダ情報を取得して格納する
            csv_header = csv_rows.fieldnames
            # 10-04.「変数．行データリスト」にCSVのヘッダ以降の行データ情報を取得して格納する
            row_list = list(csv_rows)
            csv_file = None
            csv_rows = None

            tid_list = [d.get('TID') for d in row_list]

            # 11.CSVファイル内容チェック処理
            # 11-01.バッチ概要【CSVファイルの内容チェック処理】を実施
            # 11-01-01.【CSVファイルの内容チェック処理】に違反している場合、「変数．エラー情報」にエラー情報を追加する
            input_check_result = self.check_csv(row_list, csv_header, dir_name)

            # 12.共通エラーチェック処理
            # 12-01.以下の引数で共通エラーチェック処理を実行する
            # 12-02.例外が発生した場合、例外処理に遷移
            if input_check_result.get("errorInfo"):
                # zipファイル削除
                delete_zip_file = CallbackExecutor(
                    self.delete_zip_file,
                    'download/' + zip_file_name,
                    True
                )
                # zipファイル解凍フォルダ削除処理
                delete_unzip_zip_folder = CallbackExecutor(
                    self.delete_unzip_folder,
                    'out_dir/' + dir_name,
                    True
                )
                self.common_util.common_error_check(
                    input_check_result.get("errorInfo"),
                    delete_zip_file,
                    delete_unzip_zip_folder
                )

            # 13.PDSユーザDB接続準備処理
            self.pds_user_connection_resource: PostgresDbUtilClass = None
            # 13-01.以下の引数でPDSユーザDBの接続情報をAWSのSecrets Managerから取得する
            # 13-02.取得したPDSユーザDBの接続情報を、「変数．PDSユーザDB接続情報」に格納する
            # 13-03.「変数．PDSユーザDB接続情報」を利用して、PDSユーザDBに対してのコネクションを作成する
            rds_db_secret_name = pds_user_select_result["query_results"][5]
            pds_user_db_connection_resource: PostgresDbUtilClass = None
            pds_user_db_info_response = self.common_util.get_pds_user_db_info_and_connection(rds_db_secret_name)
            if not pds_user_db_info_response["result"]:
                raise PDSException(pds_user_db_info_response["errorInfo"])
            else:
                pds_user_db_secret_info = pds_user_db_info_response["pds_user_db_secret_info"]
                pds_user_db_connection_resource = pds_user_db_info_response["pds_user_db_connection_resource"]
                pds_user_db_connection = pds_user_db_info_response["pds_user_db_connection"]

            # 14.個人情報取得処理
            user_profile_check_error_info = None
            # 14-01.個人情報テーブルからデータを取得し、「変数．個人情報取得結果リスト」に全レコードをタプルのリストとして格納する
            user_profile_check_result = pds_user_db_connection_resource.select_tuple_list(
                pds_user_db_connection,
                SqlConstClass.MULTI_CREATE_BATCH_USER_PROFILE_SELECT_SQL,
                tuple(tid_list)
            )
            # 14-02.「変数．個人情報取得結果リスト」が、0以外の場合、「変数．エラー情報」を作成し、エラーログを出力する
            if user_profile_check_result["result"] and user_profile_check_result["rowCount"] != 0:
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["030111"]["logMessage"], user_profile_check_result["query_results"][0][0], str(user_profile_check_result["rowCount"])))
                user_profile_check_error_info = {
                    "errorCode": "030111",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["030111"]["message"], user_profile_check_result["query_results"][0][0], str(user_profile_check_result["rowCount"]))
                }
            # 14-03.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not user_profile_check_result["result"]:
                user_profile_check_error_info = self.common_util.create_postgresql_log(
                    user_profile_check_result["errorObject"],
                    None,
                    None,
                    user_profile_check_result["stackTrace"]
                ).get("errorInfo")

            # 15.共通エラーチェック処理
            # 15-01.以下の引数で共通エラーチェック処理を実行する
            # 15-02.例外が発生した場合、例外処理に遷移
            if user_profile_check_error_info is not None:
                # zipファイル削除
                delete_zip_file = CallbackExecutor(
                    self.delete_zip_file,
                    'download/' + zip_file_name,
                    True
                )
                # zipファイル解凍フォルダ削除処理
                delete_unzip_zip_folder = CallbackExecutor(
                    self.delete_unzip_folder,
                    'out_dir/' + dir_name,
                    True
                )
                self.common_util.common_error_check(
                    user_profile_check_error_info,
                    delete_zip_file,
                    delete_unzip_zip_folder
                )

            # 16.個人情報登録処理リスト初期化処理
            # 16-01.「変数．個人情報登録処理リスト」を空のリストで作成する
            user_profile_insert_exec_list = []

            for csv_row_loop, row in enumerate(row_list):
                # 17.個人情報登録処理リスト作成処理
                # 17-01.「変数．個人情報登録処理リスト」に個人情報登録処理を追加する
                user_profile_insert_exec_list.append(
                    self.user_profile_insert_exec(
                        transaction_id=row["TID"],
                        csv_header=csv_header,
                        user_profile_row=row,
                        kms_id=pds_user_select_result["query_results"][7],
                        bucket_name=pds_user_select_result["query_results"][6],
                        pds_user_db_secret_info=pds_user_db_secret_info,
                        pds_user_info=pds_user_info_dict,
                        dir_name=dir_name
                    )
                )

            # 18.個人情報登録処理実行処理
            # 18-01.「変数．個人情報登録処理リスト」もとに、個人情報登録処理を並列で実行する
            # 18-02.レスポンスを「変数．個人情報登録処理実行結果リスト」に格納する
            user_profile_insert_exec_result_list = await asyncio.gather(*user_profile_insert_exec_list, return_exceptions=True)

            # 19.個人情報登録処理実行チェック処理
            # 19-01.「変数．個人情報登録処理実行結果リスト」内を検索して、処理結果がfalseのデータが存在する場合、「20.個人情報バッチキュー発行処理」に遷移する
            # 19-02.「変数．個人情報登録処理実行結果リスト」内を検索して、処理結果がfalseのデータが存在しない場合、「21.トランザクション作成処理」に遷移する
            error_info_list = []
            exception_list = [d for d in user_profile_insert_exec_result_list if type(d) is PDSException]
            if len(exception_list) > 0:
                for exception in exception_list:
                    for error in exception.error_info_list:
                        error_info_list.append(error)

            result_list = [d.get("result") for d in user_profile_insert_exec_result_list if type(d) is dict]
            if False in result_list:
                error_info_list = []
                for result_info in user_profile_insert_exec_result_list:
                    if result_info.get("errorInfo"):
                        if type(result_info["errorInfo"]) is list:
                            error_info_list.extend(result_info["errorInfo"])
                        else:
                            error_info_list.append(result_info["errorInfo"])
            transaction_id_list = [d.get("transactionId") for d in user_profile_insert_exec_result_list if type(d) is dict and d.get("transactionId") is not None]
            if len(error_info_list) > 0:
                # zipファイル削除処理
                delete_zip_file = CallbackExecutor(
                    self.delete_zip_file,
                    'download/' + zip_file_name,
                    True
                )
                # zipファイル解凍フォルダ削除処理
                delete_unzip_zip_folder = CallbackExecutor(
                    self.delete_unzip_folder,
                    'out_dir/' + dir_name,
                    True
                )
                # 個人情報削除バッチキュー発行処理
                transaction_delete_batch_queue_issue_loop = CallbackExecutor(
                    self.transaction_delete_batch_queue_issue_loop,
                    transaction_id_list,
                    request_body
                )
                self.common_util.common_error_check(
                    error_info_list,
                    transaction_delete_batch_queue_issue_loop,
                    delete_zip_file,
                    delete_unzip_zip_folder
                )

            else:
                # 21.トランザクション作成処理
                # 21.「個人情報更新トランザクション」を作成する

                # 22.個人情報更新処理
                user_profile_update_error_info = None
                # 22-01.個人情報テーブルを更新する
                user_profile_update_result = pds_user_db_connection_resource.update(
                    pds_user_db_connection,
                    SqlConstClass.MULTI_CREATE_BATCH_USER_PROFILE_UPDATE_SQL,
                    tuple(tid_list),
                    False
                )
                # 22-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
                if not user_profile_update_result["result"]:
                    user_profile_update_error_info = self.common_util.create_postgresql_log(
                        user_profile_update_result["errorObject"],
                        None,
                        None,
                        user_profile_update_result["stackTrace"]
                    ).get("errorInfo")

                # 23.共通エラーチェック処理
                # 23-01.以下の引数で共通エラーチェック処理を実行する
                # 23-02.例外が発生した場合、例外処理に遷移
                if user_profile_update_error_info is not None:
                    # ロールバック処理
                    rollback_transaction = CallbackExecutor(
                        self.common_util.common_check_postgres_rollback,
                        pds_user_db_connection,
                        pds_user_db_connection_resource
                    )
                    # zipファイル削除処理
                    delete_zip_file = CallbackExecutor(
                        self.delete_zip_file,
                        'download/' + zip_file_name,
                        True
                    )
                    # zipファイル解凍フォルダ削除処理
                    delete_unzip_zip_folder = CallbackExecutor(
                        self.delete_unzip_folder,
                        'out_dir/' + dir_name,
                        True
                    )
                    # 個人情報削除バッチキュー発行処理
                    transaction_delete_batch_queue_issue_loop = CallbackExecutor(
                        self.transaction_delete_batch_queue_issue_loop,
                        transaction_id_list,
                        request_body
                    )
                    self.common_util.common_error_check(
                        user_profile_update_error_info,
                        rollback_transaction,
                        transaction_delete_batch_queue_issue_loop,
                        delete_zip_file,
                        delete_unzip_zip_folder
                    )

                # 24.トランザクションコミット処理
                # 24-01.「個人情報更新トランザクション」をコミットする
                pds_user_db_connection_resource.commit_transaction(pds_user_db_connection)
                pds_user_db_connection_resource.close_connection(pds_user_db_connection)

            # 25.zipファイル削除処理
            # 25-01.以下の引数でzipファイル削除処理を実行する
            # 25-02.レスポンスを「変数．zipファイル削除処理実行結果」に格納する
            delete_zip_file_result = self.delete_zip_file('download/' + zip_file_name, False)

            # 26.共通エラーチェック処理
            # 26-01.以下の引数で共通エラーチェック処理を実行する
            # 26-02.例外が発生した場合、例外処理に遷移
            if delete_zip_file_result.get("errorInfo"):
                # zipファイル解凍フォルダ削除処理
                delete_unzip_zip_folder = CallbackExecutor(
                    self.delete_unzip_folder,
                    'out_dir/' + dir_name,
                    True
                )
                self.common_util.common_error_check(
                    delete_zip_file_result.get("errorInfo"),
                    delete_unzip_zip_folder
                )

            # 27.zipファイル解凍フォルダ削除処理
            # 27-01.以下の引数でzipファイル解凍フォルダ削除処理を実行する
            # 27-02.レスポンスを「変数．zipファイル解凍フォルダ削除処理」に格納する
            delete_unzip_folder_result = self.delete_unzip_folder('out_dir/' + dir_name, False)

            # 28.共通エラーチェック処理
            # 28-01.以下の引数で共通エラーチェック処理を実行する
            # 28-02.例外が発生した場合、例外処理に遷移
            if delete_unzip_folder_result.get("errorInfo"):
                self.common_util.common_error_check(delete_unzip_folder_result.get("errorInfo"))

            if len(error_info_list) == 0:
                # 29.zipファイルダウンロード元ファイル削除処理
                s3_zip_delete_error_info = None
                s3_util = s3UtilClass(self.logger, bucket_name=SystemConstClass.USER_PROFILE_MULTI_CREATE_BUCKET)
                for result_count in range(5):
                    # 29-01.S3のバケット(バケット名：multi_register_bucket)から「パラメータ．PDSユーザID」をプレフィックスにして、配置されたzipファイルを削除する
                    if s3_util.deleteFile(file_name=check_result["key"]):
                        break
                    elif result_count == 4:
                        # 29-02.S3の削除処理に失敗した場合、「変数．エラー情報」を作成する
                        self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990022"]["logMessage"]))
                        s3_zip_delete_error_info = {
                            "errorCode": "990022",
                            "message": logUtil.message_build(MessageConstClass.ERRORS["990022"]["message"], "990022")
                        }

                # 30.共通エラーチェック処理
                # 30-01.以下の引数で共通エラーチェック処理を実行する
                # 30-02.例外が発生した場合、例外処理に遷移
                if s3_zip_delete_error_info is not None:
                    self.common_util.common_error_check(
                        s3_zip_delete_error_info
                    )

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

    def delete_zip_file(self, file_path: str, common_error_check_flg: bool):
        """
        zipファイル削除処理

        Args:
            file_path (str): ファイルパス
            common_error_check_flg (bool): 共通エラーチェックフラグ

        Returns:
            dict: 処理結果
        """
        try:
            error_info = None
            for result_count in range(5):
                try:
                    # 01.zipファイル解凍フォルダ削除処理
                    # 01-01.「引数．ファイルパス」に指定されたダウンロードしたzipファイルを削除する
                    os.remove(file_path)
                    break
                except Exception:
                    if result_count == 4:
                        # 01-02.処理が失敗した場合は「変数．エラー情報」を作成し、エラーログをCloudWatchにログ出力する
                        # 01-02-01.zipファイル削除に失敗した場合、「変数．エラー情報」にエラー情報を追加する
                        self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990031"]["logMessage"]))
                        error_info = {
                            "errorCode": "990031",
                            "message": logUtil.message_build(MessageConstClass.ERRORS["990031"]["message"], "990031")
                        }

            # 02.共通エラーチェック実施チェック処理
            # 02-01.「引数．共通エラーチェックフラグ」がtrueの場合、「03.共通エラーチェック処理」に遷移する
            # 02-02.「引数．共通エラーチェックフラグ」がfalseの場合、「04.終了処理」に遷移する
            if common_error_check_flg:
                # 03.共通エラーチェック処理
                # 03-01.以下の引数で共通エラーチェック処理を実行する
                # 03-02.例外が発生した場合、例外処理に遷移
                if error_info is not None:
                    self.common_util.common_error_check(error_info)

            else:
                # 04.終了処理
                # 04-01.レスポンス情報を作成し、返却する
                if error_info is None:
                    # 04-01-01.「変数．エラー情報」に値が設定されていない場合、下記のレスポンス情報を返却する
                    return {
                        "result": True
                    }
                else:
                    # 04-01-02.「変数．エラー情報」に値が設定されている場合、下記のレスポンス情報を返却する
                    return {
                        "result": False,
                        "errorInfo": error_info
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

    def delete_unzip_folder(self, folder_path: str, common_error_check_flg: bool):
        """
        zipファイル解凍フォルダ削除処理

        Args:
            folder_path (str): フォルダパス
            common_error_check_flg (bool): 共通エラーチェックフラグ

        Returns:
            dict: 処理結果
        """
        try:
            error_info = None
            for result_count in range(5):
                try:
                    # 01.zipファイル解凍フォルダ削除処理
                    # 01-01.「引数．フォルダパス」に指定されたzipファイルを解凍したフォルダを削除する
                    shutil.rmtree(folder_path)
                    break
                except Exception:
                    if result_count == 4:
                        # 01-02.処理が失敗した場合は「変数．エラー情報」を作成し、エラーログをCloudWatchにログ出力する
                        # 01-02-01.zipファイル解凍フォルダ削除に失敗した場合、「変数．エラー情報」にエラー情報を追加する
                        self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990032"]["logMessage"]))
                        error_info = {
                            "errorCode": "990032",
                            "message": logUtil.message_build(MessageConstClass.ERRORS["990032"]["message"], "990032")
                        }

            # 02.共通エラーチェック実施チェック処理
            # 02-01.「引数．共通エラーチェックフラグ」がtrueの場合、「03.共通エラーチェック処理」に遷移する
            # 02-02.「引数．共通エラーチェックフラグ」がfalseの場合、「04.終了処理」に遷移する
            if common_error_check_flg:
                # 03.共通エラーチェック処理
                # 03-01.以下の引数で共通エラーチェック処理を実行する
                # 03-02.例外が発生した場合、例外処理に遷移
                if error_info is not None:
                    self.common_util.common_error_check(error_info)

            else:
                # 04.終了処理
                # 04-01.レスポンス情報を作成し、返却する
                if error_info is None:
                    # 04-01-01.「変数．エラー情報」に値が設定されていない場合、下記のレスポンス情報を返却する
                    return {
                        "result": True
                    }
                else:
                    # 04-01-02.「変数．エラー情報」に値が設定されている場合、下記のレスポンス情報を返却する
                    return {
                        "result": False,
                        "errorInfo": error_info
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

    def check_csv(self, row_list: list, csv_header: list, dir_name: str):
        """
        CSV内容チェック

        Args:
            row_list (list): 行データリスト
            csv_header (list): ヘッダ情報リスト

        Returns:
            dict: 処理結果
        """
        try:
            error_info_list = []
            tid_list = [d.get('TID') for d in row_list]
            # TID必須チェック
            if not checkUtil.check_require_list_str(tid_list):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "TID"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "TID")
                    }
                )

            # TID型チェック
            if not checkUtil.check_type_list(tid_list, str):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "TID", "文字列"))
                error_info_list.append(
                    {
                        "errorCode": "020019",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "TID", "文字列")
                    }
                )

            # TID最小桁チェック
            if not checkUtil.check_min_length_list_str(tid_list, 1):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020016"]["logMessage"], "TID", "1"))
                error_info_list.append(
                    {
                        "errorCode": "020016",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020016"]["message"], "TID", "1")
                    }
                )

            # TID最大桁チェック
            if not checkUtil.check_max_length_list_str(tid_list, 36):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020002"]["logMessage"], "TID", "36"))
                error_info_list.append(
                    {
                        "errorCode": "020002",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020002"]["message"], "TID", "36")
                    }
                )

            # TID入力可能文字チェック
            if not checkUtil.check_image_hash(tid_list):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020020"]["logMessage"], "TID"))
                error_info_list.append(
                    {
                        "errorCode": "020020",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020020"]["message"], "TID")
                    }
                )

            # TIDリスト重複チェック
            dup = [x for x in set(tid_list) if tid_list.count(x) > 1]
            if len(dup) > 0:
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["030110"]["logMessage"], str(dup)))
                error_info_list.append(
                    {
                        "errorCode": "030110",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["030110"]["message"], str(dup))
                    }
                )

            user_id_list = [d.get('UserID') for d in row_list]
            # UserID必須チェック
            user_id_check_flg = True
            if not checkUtil.check_require_list_str(user_id_list):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "UserID"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "UserID")
                    }
                )
                user_id_check_flg = False

            # UserID型チェック
            if not checkUtil.check_type_list(user_id_list, str):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "UserID", "文字列"))
                error_info_list.append(
                    {
                        "errorCode": "020019",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "UserID", "文字列")
                    }
                )
                user_id_check_flg = False

            # UserID最小桁チェック
            if not checkUtil.check_min_length_list_str(user_id_list, 1):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020016"]["logMessage"], "UserID", "1"))
                error_info_list.append(
                    {
                        "errorCode": "020016",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020016"]["message"], "UserID", "1")
                    }
                )
                user_id_check_flg = False

            # UserID最大桁チェック
            if not checkUtil.check_max_length_list_str(user_id_list, 36):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020002"]["logMessage"], "UserID", "36"))
                error_info_list.append(
                    {
                        "errorCode": "020002",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020002"]["message"], "UserID", "36")
                    }
                )
                user_id_check_flg = False

            secure_level_list = [d.get('SecureLevel') for d in row_list]
            # SecureLevel型チェック
            if not checkUtil.check_type_list(secure_level_list, str):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "SecureLevel", "文字列"))
                error_info_list.append(
                    {
                        "errorCode": "020019",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "SecureLevel", "文字列")
                    }
                )

            # SecureLevel最大桁チェック
            if not checkUtil.check_max_length_list_str(secure_level_list, 2):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020002"]["logMessage"], "SecureLevel", "2"))
                error_info_list.append(
                    {
                        "errorCode": "020002",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020002"]["message"], "SecureLevel", "2")
                    }
                )

            # SecureLevel入力可能文字
            if not checkUtil.check_secure_level_characters(secure_level_list):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020003"]["logMessage"], "SecureLevel"))
                error_info_list.append(
                    {
                        "errorCode": "020003",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "SecureLevel")
                    }
                )

            data_key_index_list = [str(str_header).replace('DataKey', "") for str_header in csv_header if str(str_header).startswith("DataKey")]
            data_value_index_list = [str(str_header).replace('DataValue', "") for str_header in csv_header if str(str_header).startswith("DataValue")]

            data_key_value_check_flg = True
            # DataKey,DataValueの組み合わせ（ヘッダ）
            list_diff_item = set(data_key_index_list.copy()) ^ set(data_value_index_list.copy())
            if len(list(list_diff_item)) > 0:
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["030101"]["logMessage"], str(list(list_diff_item))))
                error_info_list.append(
                    {
                        "errorCode": "030101",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["030101"]["message"], str(list(list_diff_item)))
                    }
                )
                data_key_value_check_flg = False

            # DataKey,DataValueの順番（ヘッダ）
            if len(data_key_index_list) != len(data_value_index_list):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["030102"]["logMessage"]))
                error_info_list.append(
                    {
                        "errorCode": "030102",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["030102"]["message"])
                    }
                )
                data_key_value_check_flg = False
            else:
                for index, key_index in enumerate(data_key_index_list):
                    if not key_index.isdecimal():
                        self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["030102"]["logMessage"]))
                        error_info_list.append(
                            {
                                "errorCode": "030102",
                                "message": logUtil.message_build(MessageConstClass.ERRORS["030102"]["message"])
                            }
                        )
                        data_key_value_check_flg = False
                        break
                    if not data_value_index_list[index].isdecimal():
                        self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["030102"]["logMessage"]))
                        error_info_list.append(
                            {
                                "errorCode": "030102",
                                "message": logUtil.message_build(MessageConstClass.ERRORS["030102"]["message"])
                            }
                        )
                        data_key_value_check_flg = False
                        break
                    if key_index != data_value_index_list[index]:
                        self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["030102"]["logMessage"]))
                        error_info_list.append(
                            {
                                "errorCode": "030102",
                                "message": logUtil.message_build(MessageConstClass.ERRORS["030102"]["message"])
                            }
                        )
                        data_key_value_check_flg = False
                        break
                    if int(key_index) != index + 1:
                        self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["030102"]["logMessage"]))
                        error_info_list.append(
                            {
                                "errorCode": "030102",
                                "message": logUtil.message_build(MessageConstClass.ERRORS["030102"]["message"])
                            }
                        )
                        data_key_value_check_flg = False
                        break

                for row in row_list:
                    if data_key_value_check_flg:
                        data = {}
                        data_item_check_flg = True
                        for key_index in data_key_index_list:
                            # DataKey, DataValueの組み合わせ（項目）
                            if len(row["DataKey" + key_index]) == 0 and len(row["DataValue" + key_index]):
                                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["030103"]["logMessage"], row["TID"], key_index))
                                error_info_list.append(
                                    {
                                        "errorCode": "030103",
                                        "message": logUtil.message_build(MessageConstClass.ERRORS["030103"]["message"], row["TID"], key_index)
                                    }
                                )
                                data_item_check_flg = False
                            else:
                                data[row["DataKey" + key_index]] = row["DataValue" + key_index]
                        # DataKey,DataValueをJSON変換した後の桁数
                        if data_item_check_flg and len(json.dumps(data)) > 5000:
                            self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["030103"]["logMessage"], row["TID"]))
                            error_info_list.append(
                                {
                                    "errorCode": "030104",
                                    "message": logUtil.message_build(MessageConstClass.ERRORS["030103"]["message"], row["TID"])
                                }
                            )
                    if user_id_check_flg:
                        check_path = "out_dir/" + dir_name + "/" + row["UserID"] + "/"
                        if os.path.exists(check_path):
                            files = os.listdir(check_path)
                            dir_list = [int(f) for f in files if f.isdecimal() and os.path.isdir(os.path.join(check_path, f))]
                            dir_list.sort()
                            image_index_check = True
                            # Imageの順番
                            for idx, dir_index in enumerate(dir_list):
                                if dir_index != idx + 1:
                                    self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["030105"]["logMessage"], row["UserID"]))
                                    error_info_list.append(
                                        {
                                            "errorCode": "030105",
                                            "message": logUtil.message_build(MessageConstClass.ERRORS["030105"]["message"], row["UserID"])
                                        }
                                    )
                                    image_index_check = False
                                    break
                            if image_index_check:
                                total_file_size = 0
                                for dir_index in dir_list:
                                    dir_path = os.path.join(check_path, str(dir_index))
                                    files = os.listdir(dir_path)
                                    files_list = [os.path.join(dir_path, f) for f in files if os.path.isfile(os.path.join(dir_path, f))]
                                    # Imageの存在チェック
                                    if len(files_list) == 0:
                                        self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["030106"]["logMessage"], row["UserID"], str(key_index)))
                                        error_info_list.append(
                                            {
                                                "errorCode": "030106",
                                                "message": logUtil.message_build(MessageConstClass.ERRORS["030106"]["message"], row["UserID"], str(key_index))
                                            }
                                        )
                                    # Imageの複数配置チェック
                                    elif len(files_list) > 1:
                                        self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["030107"]["logMessage"], row["UserID"], str(key_index)))
                                        error_info_list.append(
                                            {
                                                "errorCode": "030107",
                                                "message": logUtil.message_build(MessageConstClass.ERRORS["030107"]["message"], row["UserID"], str(key_index))
                                            }
                                        )
                                    else:
                                        file_size = os.path.getsize(files_list[0])
                                        total_file_size += file_size
                                        # Imageサイズ（単体）チェック
                                        if file_size > SystemConstClass.USER_PROFILE_BINARY_FILE_SOLO:
                                            self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["030108"]["logMessage"], row["UserID"], str(key_index)))
                                            error_info_list.append(
                                                {
                                                    "errorCode": "030108",
                                                    "message": logUtil.message_build(MessageConstClass.ERRORS["030108"]["message"], row["UserID"], str(key_index))
                                                }
                                            )
                                # Imageサイズ（複数）チェック
                                if total_file_size > SystemConstClass.USER_PROFILE_BINARY_FILE_TOTAL:
                                    self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["030109"]["logMessage"], row["UserID"]))
                                    error_info_list.append(
                                        {
                                            "errorCode": "030109",
                                            "message": logUtil.message_build(MessageConstClass.ERRORS["030109"]["message"], row["UserID"])
                                        }
                                    )
            if len(error_info_list) == 0:
                return {
                    "result": True
                }
            else:
                return {
                    "result": False,
                    "errorInfo": error_info_list
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

    async def user_profile_insert_exec(
        self,
        transaction_id: str,
        csv_header: list,
        user_profile_row: dict,
        kms_id: str,
        bucket_name: str,
        pds_user_db_secret_info: dict,
        pds_user_info: dict,
        dir_name: str
    ):
        """
        個人情報登録処理

        Args:
            transaction_id (str): トランザクションID
            csv_header (list): ヘッダレコード
            user_profile_row (dict): 個人情報レコード
            kms_id (str): 個人情報暗号・復号化用KMSID
            bucket_name (str): バケット名
            pds_user_db_secret_info (dict): PDSユーザDB接続情報
            pds_user_info (dict): PDSユーザ情報
            dir_name (str): フォルダ名
        """
        try:
            # 01.JSON生成処理
            data_key_index_list = [int(str(str_header).replace('DataKey', "")) for str_header in csv_header if str(str_header).startswith("DataKey")]
            data_key_index_list.sort()
            transaction_info = {}
            # 01-01.「引数．個人情報レコード」から取得したDataKeyとDataValueをもとに、JSONを生成し「変数．個人情報データ」に格納する
            for data_key_index in data_key_index_list:
                if user_profile_row['DataKey' + str(data_key_index)] != "" and user_profile_row['DataValue' + str(data_key_index)] != "":
                    transaction_info[user_profile_row['DataKey' + str(data_key_index)]] = user_profile_row['DataValue' + str(data_key_index)]

            check_path = "out_dir/" + dir_name + "/" + user_profile_row["UserID"] + "/"
            user_profile_util = UserProfileUtilClass(self.logger)
            # 02.個人情報バイナリデータ登録処理リスト初期化処理
            # 02-01.「変数．個人情報バイナリデータ登録処理リスト」を初期化する
            user_profile_binary_insert_task_list = []
            # 03.フォルダ存在チェック処理
            # 03-01.解凍したファイルの「ルートフォルダ\{引数．個人情報レコード．UserID}」のフォルダが存在する場合、「04.バイナリデータ読込処理」を実施する
            # 03-02.解凍したファイルの「ルートフォルダ\{引数．個人情報レコード．UserID}」のフォルダが存在しない場合、「08.MongoDB接続準備処理」を実施する
            if os.path.exists(check_path):
                files = os.listdir(check_path)
                dir_list = [int(f) for f in files if os.path.isdir(os.path.join(check_path, f))]
                dir_list.sort()
                for binary_data_loop, dir_name in enumerate(dir_list):
                    dir_path = os.path.join(check_path, str(dir_name))
                    # 04.バイナリデータ読込処理
                    # 04-01.解凍したファイルの「ルートフォルダ\{引数．個人情報レコード．UserID}\{変数．バイナリデータループ数}」の配下にあるバイナリデータを読み込みbase64に変換して、「変数．Base64」に追加する
                    files = os.listdir(dir_path)
                    files_list = [os.path.join(dir_path, f) for f in files if os.path.isfile(os.path.join(dir_path, f))]
                    base64_string = self.convert_file_to_b64_string(files_list[0])

                    # 05.Base64ハッシュ化処理
                    # 05-01.「変数．Base64」をsha512形式のハッシュアルゴリズムでハッシュ化して、「変数．バイナリデータハッシュ」に格納する
                    hash = hashlib.sha512(base64_string.encode("utf-8")).hexdigest()

                    # 06.バイナリデータ情報作成処理
                    # 06-01.バイナリデータ登録に必要な情報を、「変数．バイナリデータ情報」に格納する
                    binary_data_info = {}
                    binary_data_info["transaction_id"] = transaction_id
                    binary_data_info["save_image_idx"] = binary_data_loop
                    binary_data_info["save_image_data"] = base64_string
                    binary_data_info["save_image_data_hash"] = hash
                    binary_data_info["valid_flg"] = True
                    binary_data_info["save_image_data_array_index"] = binary_data_loop

                    # 07.個人情報バイナリデータ登録処理リスト作成処理
                    # 07-01.「変数．個人情報バイナリデータ登録処理リスト」に個人情報バイナリデータ登録処理を追加する
                    user_profile_binary_insert_task_list.append(
                        user_profile_util.insert_binary_data(
                            binaryInsertData=binary_data_info,
                            userProfileKmsId=kms_id,
                            bucketName=bucket_name,
                            pdsUserDbInfo=pds_user_db_secret_info
                        )
                    )

            # 08.MongoDB接続準備処理
            # 08-01.プログラムが配置されているリージョンのAZaのMongoDBの接続情報をAWSのSecrets Managerから取得する
            # 08-01-01.下記の引数で、AZaのMongoDB接続情報を取得する
            # 08-01-02.取得したMongoDBの接続情報を、「変数．MongoDB接続情報」に格納する
            # 08-02.「08-01」の処理に失敗した場合、プログラムが配置されているリージョンのAZcのMongoDBの接続情報をAWSのSecrets Managerから取得する
            # 08-02-01.プログラムが配置されているリージョンのAZcのMongoDBの接続情報をAWSのSecrets Managerから取得する
            # 08-02-02.取得したMongoDBの接続情報を、「変数．MongoDB接続情報」に格納する
            # 08-03.「変数．MongoDB接続情報」を利用して、MongoDBに対してのコネクションを作成する
            mongo_info_result = self.common_util.get_mongo_db_info_and_connection(
                pds_user_info["tokyo_a_mongodb_secret_name"],
                pds_user_info["tokyo_c_mongodb_secret_name"],
                pds_user_info["osaka_a_mongodb_secret_name"],
                pds_user_info["osaka_c_mongodb_secret_name"]
            )
            mongo_db_util: MongoDbClass = mongo_info_result["mongo_db_util"]

            # 09.MongoDBトランザクション作成処理
            # 09-01.「MongoDB個人情報登録トランザクション」を作成する
            mongo_db_util.create_session()
            mongo_db_util.create_transaction()

            # 10.個人情報データ存在チェック処理
            # 10-01.「変数．個人情報データ」が存在する場合、「11.MongoDB登録処理」に遷移する
            # 10-02.「変数．個人情報データ」が存在しない場合、「15.PDSユーザDB接続準備処理」に遷移する
            if transaction_info != {}:
                json_data_flg = True
                # 11.MongoDB登録処理
                mongo_db_insert_error_info = None
                # 11-01.保存データテーブルに、「引数．個人情報データ」を登録する
                mongo_db_insert_result = mongo_db_util.insert_document(transaction_info)
                # 11-02.処理が失敗した場合は「変数．エラー情報」を作成し、エラーログをCloudWatchにログ出力する
                if not mongo_db_insert_result["result"]:
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["992001"]["logMessage"], mongo_db_insert_result["errorCode"], mongo_db_insert_result["message"]))
                    mongo_db_insert_error_info = {
                        "errorCode": "992001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["992001"]["message"], "992001")
                    }

                # 12.MongoDB登録チェック処理
                # 12-01.「変数．エラー情報」がNullの場合、「15.PDSユーザDB接続準備処理」に遷移する
                # 12-01.「変数．エラー情報」がNull以外の場合、「13.MongoDBロールバック処理」に遷移する
                if mongo_db_insert_error_info is not None:
                    # 13.MongoDBロールバック処理
                    # 13-01.以下の引数でMongoDBロールバック処理を実行
                    self.common_util.common_check_mongo_rollback(mongo_db_util)
                    mongo_db_util.close_session()
                    mongo_db_util.close_mongo()

                    # 14.MongoDB登録エラー処理
                    # 14-01.レスポンス情報整形処理
                    # 14-01-01.以下をレスポンスとして返却する
                    return {
                        "result": False,
                        "transactionId": None,
                        "errorInfo": mongo_db_insert_error_info
                    }
                insert_object_id = mongo_db_insert_result["objectId"]
                data_str = json.dumps(transaction_info)
            else:
                json_data_flg = False
                insert_object_id = None
                data_str = None

            # 15.PDSユーザDB接続準備処理
            # 15-01.「引数．PDSユーザDB接続情報」を利用して、PDSユーザDBに対してのコネクションを作成する
            pds_user_db_connection_resource: PostgresDbUtilClass = PostgresDbUtilClass(
                logger=self.logger,
                end_point=pds_user_db_secret_info["host"],
                port=pds_user_db_secret_info["port"],
                user_name=pds_user_db_secret_info["username"],
                password=pds_user_db_secret_info["password"],
                region=SystemConstClass.AWS_CONST["REGION"]
            )
            pds_user_db_connection = pds_user_db_connection_resource.create_connection(
                SystemConstClass.PDS_USER_DB_NAME
            )

            # 16.トランザクション作成処理
            # 16-01.「個人情報登録トランザクション」を作成する

            # 17.個人情報登録処理
            pds_user_profile_insert_error_info = None
            # 17-01.個人情報テーブルに以下の登録内容で新規登録する
            pds_user_profile_insert_result = pds_user_db_connection_resource.insert(
                pds_user_db_connection,
                SqlConstClass.USER_PROFILE_INSERT_SQL,
                transaction_id,
                user_profile_row["UserID"],
                commonUtil.get_datetime_jst(),
                json_data_flg,
                insert_object_id,
                data_str,
                user_profile_row["SecureLevel"],
                False,
                commonUtil.get_datetime_jst()
            )

            # 17-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not pds_user_profile_insert_result["result"]:
                pds_user_profile_insert_error_info = self.common_util.create_postgresql_log(
                    pds_user_profile_insert_result["errorObject"],
                    "トランザクションID",
                    transaction_id,
                    pds_user_profile_insert_result["stackTrace"]
                ).get("errorInfo")

            # 18.個人情報登録チェック処理
            # 18-01.「変数．エラー情報」がNullの場合、「22.MongoDBトランザクションコミット処理」に遷移する
            # 18-02.「変数．エラー情報」がNull以外の場合、「19.ロールバック処理」に遷移する
            if pds_user_profile_insert_error_info is not None:
                # 19.ロールバック処理
                # 19-01.以下の引数でロールバック処理を実行
                self.common_util.common_check_postgres_rollback(pds_user_db_connection, pds_user_db_connection_resource)
                pds_user_db_connection_resource.close_connection(pds_user_db_connection)

                # 20.MongoDBロールバック処理
                # 20-01.以下の引数でMongoDBロールバック処理を実行
                self.common_util.common_check_mongo_rollback(mongo_db_util)
                mongo_db_util.close_session()
                mongo_db_util.close_mongo()

                # 21.個人情報登録エラー処理
                # 21-01.レスポンス情報整形処理
                # 21-01-01.以下をレスポンスとして返却する
                return {
                    "result": False,
                    "transactionId": None,
                    "errorInfo": pds_user_profile_insert_error_info
                }

            # 22.MongoDBトランザクションコミット処理
            # 22-01.「MongoDB個人情報登録トランザクション」をコミットする
            mongo_db_util.commit_transaction()
            mongo_db_util.close_session()
            mongo_db_util.close_mongo()

            # 23.トランザクションコミット処理
            # 23-01.「個人情報登録トランザクション」をコミットする
            pds_user_db_connection_resource.commit_transaction(pds_user_db_connection)
            pds_user_db_connection_resource.close_connection(pds_user_db_connection)

            # 24.個人情報バイナリデータ存在チェック処理
            # 24-01.「変数．個人情報バイナリデータ登録処理リスト」が空のリストの場合、「28.終了処理」に遷移する
            # 24-01.「変数．個人情報バイナリデータ登録処理リスト」が空のリスト以外の場合、「25.個人情報バイナリデータ登録処理実行処理」に遷移する
            if len(user_profile_binary_insert_task_list) != 0:
                # 25.個人情報バイナリデータ登録処理実行処理
                # 25-01.「変数．個人情報バイナリデータ登録処理リスト」もとに、個人情報バイナリデータ登録処理を並列で実行する
                # 25-02.レスポンスを「変数．個人情報バイナリデータ登録処理実行結果リスト」に格納する
                insert_binary_data_result_list = await asyncio.gather(*user_profile_binary_insert_task_list, return_exceptions=True)

                # 26.個人情報バイナリデータ登録チェック処理
                # 26-01.「変数．個人情報バイナリデータ登録処理実行結果リスト」内を検索して、処理結果がfalseのデータが存在する場合、「27.個人情報バイナリデータ登録エラー処理」に遷移する
                # 26-02.「変数．個人情報バイナリデータ登録処理実行結果リスト」内を検索して、処理結果がfalseのデータが存在しない場合、「28.終了処理」に遷移する
                error_info_list = []
                exception_list = [d for d in insert_binary_data_result_list if type(d) is PDSException]
                if len(exception_list) > 0:
                    for exception in exception_list:
                        for error in exception.error_info_list:
                            error_info_list.append(error)

                result_list = [d.get("result") for d in insert_binary_data_result_list if type(d) is dict]
                if False in result_list:
                    error_info_list = []
                    for result_info in insert_binary_data_result_list:
                        if result_info.get("errorInfo"):
                            if type(result_info["errorInfo"]) is list:
                                error_info_list.extend(result_info["errorInfo"])
                            else:
                                error_info_list.append(result_info["errorInfo"])
                if len(error_info_list) > 0:
                    # 27-02.レスポンス情報整形処理
                    # 27-02-01.以下をレスポンスとして返却する
                    return {
                        "result": False,
                        "transactionId": transaction_id,
                        "errorInfo": error_info_list
                    }
            # 28.終了処理
            # 28-01.返却パラメータを作成し、返却する
            return {
                "result": True,
                "transactionId": transaction_id
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

    def convert_file_to_b64_string(self, file_path):
        """
        ファイルをBase64エンコードする

        Args:
            file_path (_type_): ファイルパス

        Returns:
            str: Base64文字列
        """
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    def transaction_delete_batch_queue_issue_loop(self, transaction_id_list: list, request_body: requestBody):
        """
        個人情報削除バッチキュー発行処理（ループ処理）

        Args:
            transaction_id_list (list): 登録したトランザクションIDリスト
            request_body (requestBody): リクエストボディ
        """
        try:
            for tid_loop, tid in enumerate(transaction_id_list):
                self.common_util.transaction_delete_batch_queue_issue(tid, request_body.pdsUserId)
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
