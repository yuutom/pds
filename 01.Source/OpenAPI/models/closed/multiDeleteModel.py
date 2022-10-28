from typing import Optional, Union
import json
from pydantic import BaseModel
from fastapi import Request
from logging import Logger
import traceback

## コールバック関数
from util.callbackExecutorUtil import CallbackExecutor
# Exception
from exceptionClass.PDSException import PDSException

# Const
from const.messageConst import MessageConstClass
from const.apitypeConst import apitypeConstClass
from const.sqlConst import SqlConstClass
from const.fileNameConst import FileNameConstClass
from const.wbtConst import wbtConstClass

# Util
import util.logUtil as logUtil
import util.commonUtil as commonUtil
from util.commonUtil import CommonUtilClass
from util.postgresDbUtil import PostgresDbUtilClass
from util.fileUtil import NoHeaderOneItemCsvStringClass, CsvStreamClass
from util.s3Util import s3UtilClass
from util.pdfUtil import PdfUtilClass


class searchCriteriaInfo(BaseModel):
    userIdMatchMode: Optional[str] = None
    userIdStr: Optional[str] = None
    dataJsonKey: Optional[str] = None
    dataMatchMode: Optional[str] = None
    dataStr: Optional[str] = None
    imageHash: Optional[str] = None
    fromDate: Optional[str] = None
    toDate: Optional[str] = None


class requestBody(BaseModel):
    pdsUserId: Optional[str] = None
    searchCriteria: Optional[searchCriteriaInfo] = None
    tidList: Union[Optional[str], Optional[list]] = None
    tidListFileName: Optional[str] = None
    approvalUserId: Optional[str] = None
    approvalUserPassword: Optional[str] = None
    mailAddressTo: Optional[str] = None
    mailAddressCc: Optional[str] = None
    multiDeleteAgreementStr: Optional[str] = None


class multiDeleteModel():

    def __init__(self, logger: Logger, request: Request):
        self.logger: Logger = logger
        self.request: Request = request
        self.common_util = CommonUtilClass(logger)

    def main(self, request_body: requestBody):
        """
        メイン処理

        Args:
            request_body (object): リクエストボディ

        Returns:
            dict: メイン処理実行結果
        """
        try:
            # 02.共通DB接続準備処理
            # 02-01.AWS SecretsManagerから共通DB接続情報を取得して、「変数．共通DB接続情報」に格納する
            common_util = CommonUtilClass(self.logger)
            common_db_connection_resource: PostgresDbUtilClass = None
            # 02-02.「変数．共通DB接続情報」を利用して、共通DBに対してのコネクションを作成する
            common_db_info_response = common_util.get_common_db_info_and_connection()
            if not common_db_info_response["result"]:
                raise PDSException(common_db_info_response["errorInfo"])
            else:
                common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
                common_db_connection = common_db_info_response["common_db_connection"]

            # 03.承認者情報確認処理
            # 03-01.承認者情報確認処理を実行する
            self.common_util.check_approval_user_info(
                approvalUserId=request_body.approvalUserId,
                approvalUserPassword=request_body.approvalUserPassword,
                commonDbInfo=common_db_info_response
            )

            # 04.PDSユーザデータ取得処理
            pds_user_search_error_info = None
            # 04-01.PDSユーザテーブルからPDSユーザデータを取得し、「変数．PDSユーザ情報」に1レコードをタプルとして格納する
            pds_user_search_result = common_db_connection_resource.select_tuple_one(
                common_db_connection,
                SqlConstClass.MONGODB_SECRET_NAME_AND_S3_SELECT_SQL,
                request_body.pdsUserId
            )
            # 04-02.「変数．PDSユーザ取得結果」が0件の場合、「変数.エラー情報」を作成する
            if pds_user_search_result["result"] and pds_user_search_result["rowcount"] == 0:
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020004"]["logMessage"], request_body.pdsUserId))
                pds_user_search_error_info = {
                    "errorCode": "020004",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020004"]["message"], request_body.pdsUserId)
                }
            # 04-03.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not pds_user_search_result["result"]:
                pds_user_search_error_info = self.common_util.create_postgresql_log(
                    pds_user_search_result["errorObject"],
                    None,
                    None,
                    pds_user_search_result["stackTrace"]
                ).get("errorInfo")

            # 05.共通エラーチェック処理
            # 05-01.以下の引数で共通エラーチェック処理を実行する
            # 05-02.例外が発生した場合、例外処理に遷移
            if pds_user_search_error_info is not None:
                # API実行履歴登録処理
                api_history_insert = CallbackExecutor(
                    self.common_util.insert_api_history,
                    commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                    request_body.pdsUserId,
                    apitypeConstClass.API_TYPE["BATCH_DELETE"],
                    None,
                    str(self.request.url),
                    json.dumps({"path_param": self.request.path_params, "query_param": self.request.query_params._dict, "header_param": commonUtil.make_headerParam(self.request.headers), "request_body": request_body.dict()}),
                    False,
                    None,
                    commonUtil.get_str_datetime()
                )
                self.common_util.common_error_check(
                    pds_user_search_error_info,
                    api_history_insert
                )

            # PDSユーザ情報（Dict形式）の作成
            pds_user_info_column_list = [
                'pdsUserInstanceSecretName',
                'tokyo_a_mongodb_secret_name',
                'tokyo_c_mongodb_secret_name',
                'osaka_a_mongodb_secret_name',
                'osaka_c_mongodb_secret_name',
                's3ImageDataBucketName',
                'pdsUserName'
            ]
            pds_user_info_dict = {column: data for column, data in zip(pds_user_info_column_list, pds_user_search_result["query_results"])}

            # 06.tidリスト有無判定
            # 06-01.リクエストの「リクエストボディ．tidリスト」がNullの場合、「07.tidリスト作成処理」に遷移する
            # 06-02.「リクエストのリクエストボディ．tidリスト」がNull以外の場合、「08.PDSユーザDB接続準備処理」に遷移する
            tid_list = request_body.tidList
            if tid_list is None:
                try:
                    # 07.tidリスト作成処理
                    # 07-01.tidリスト作成処理を実行
                    # 07-02.レスポンスを、「変数．tidリスト作成処理実行結果」に格納する
                    tid_list_create_exec_result = self.common_util.tid_list_create_exec(
                        searchCriteria=request_body.searchCriteria.dict(),
                        pdsUserInfo=pds_user_info_dict
                    )
                    # 07-03.「変数．tidリスト」に「変数．tidリスト作成処理実行結果．tidリスト」を格納する
                    tid_list = tid_list_create_exec_result["tidList"]
                except PDSException as e:
                    # 08.共通エラーチェック処理
                    # 08-01.以下の引数で共通エラーチェック処理を実行する
                    # 08-02.例外が発生した場合、例外処理に遷移
                    # API実行履歴登録処理
                    api_history_insert = CallbackExecutor(
                        self.common_util.insert_api_history,
                        commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                        request_body.pdsUserId,
                        apitypeConstClass.API_TYPE["BATCH_DELETE"],
                        None,
                        str(self.request.url),
                        json.dumps({"path_param": self.request.path_params, "query_param": self.request.query_params._dict, "header_param": commonUtil.make_headerParam(self.request.headers), "request_body": request_body.dict()}),
                        False,
                        None,
                        commonUtil.get_str_datetime()
                    )
                    self.common_util.common_error_check(
                        e.error_info_list,
                        api_history_insert
                    )

            # 09.PDSユーザDB接続準備処理
            # 09-01.以下の引数でPDSユーザDBの接続情報をAWSのSecrets Managerから取得する
            # 09-02.取得したPDSユーザDBの接続情報を、「変数．PDSユーザDB接続情報」に格納する
            # 09-03.「変数．PDSユーザDB接続情報」を利用して、PDSユーザDBに対してのコネクションを作成する
            pds_user_db_connection_resource: PostgresDbUtilClass = None
            pds_user_db_info_response = self.common_util.get_pds_user_db_info_and_connection(pds_user_info_dict["pdsUserInstanceSecretName"])
            if not pds_user_db_info_response["result"]:
                raise PDSException(pds_user_db_info_response["errorInfo"])
            else:
                pds_user_db_connection_resource = pds_user_db_info_response["pds_user_db_connection_resource"]
                pds_user_db_connection = pds_user_db_info_response["pds_user_db_connection"]

            # 10.トランザクション作成処理
            # 10-01.「個人情報バイナリデータ論理削除トランザクション」を作成する

            # 11.削除対象tid有無判定
            # 11-01.「変数．tidリスト」に値が存在する場合、「12.PDSユーザDB接続準備処理」へ遷移する
            # 11-02.「変数．tidリスト」に値が存在しない場合、「17.TIDリスト保存処理」へ遷移する
            if len(tid_list) > 0:
                # 12.個人情報取得処理
                user_profile_select_error_info = None
                # 12-01.個人情報テーブルからデータを取得し、「変数．個人情報取得結果リスト」に全レコードをタプルのリストとして格納する
                user_profile_select_result = pds_user_db_connection_resource.select_tuple_list(
                    pds_user_db_connection,
                    SqlConstClass.USER_PROFILE_TRANSACTION_ID_SELECT_SQL,
                    tuple(tid_list)
                )
                # 12-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
                if not user_profile_select_result["result"]:
                    user_profile_select_error_info = self.common_util.create_postgresql_log(
                        user_profile_select_result["errorObject"],
                        None,
                        None,
                        user_profile_select_result["stackTrace"]
                    ).get("errorInfo")

                # 13.共通エラーチェック処理
                # 13-01.以下の引数で共通エラーチェック処理を実行する
                # 13-02.例外が発生した場合、例外処理に遷移
                if user_profile_select_error_info is not None:
                    # API実行履歴登録処理
                    api_history_insert = CallbackExecutor(
                        self.common_util.insert_api_history,
                        commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                        request_body.pdsUserId,
                        apitypeConstClass.API_TYPE["BATCH_DELETE"],
                        None,
                        str(self.request.url),
                        json.dumps({"path_param": self.request.path_params, "query_param": self.request.query_params._dict, "header_param": commonUtil.make_headerParam(self.request.headers), "request_body": request_body.dict()}),
                        False,
                        None,
                        commonUtil.get_str_datetime()
                    )
                    self.common_util.common_error_check(
                        user_profile_select_error_info,
                        api_history_insert
                    )

                # 14.tidリストファイル作成処理
                # 14-01.「変数．個人情報取得結果リスト[][0]」のデータを「変数．削除対象tidリスト」に格納する
                # 14-02.「変数．削除対象tidリスト」をもとにCSVファイルを作成する
                # 14-03.作成したCSVを「変数．tidリストファイル」に格納する
                if len(user_profile_select_result) > 0:
                    delete_tid_list = [record[0] for record in user_profile_select_result["query_results"]]
                else:
                    delete_tid_list = []
                tid_list_file_name = FileNameConstClass.TID_LIST_NOTIFICATION_NAME + commonUtil.get_datetime_str_no_symbol() + FileNameConstClass.TID_LIST_NOTIFICATION_EXTENSION
                tid_list_csv_string = NoHeaderOneItemCsvStringClass(delete_tid_list)
                tid_list_csv_stream = CsvStreamClass(tid_list_csv_string)
                # 14－04.「変数．削除レコード数」に「変数．個人情報取得結果リスト」の要素数を格納する
                delete_count = len(user_profile_select_result["query_results"])

                # 15.削除対象データ有無判定処理
                # 15-01.「変数．削除レコード数」が0の場合、「18.TIDリスト保存処理」へ遷移する
                # 15-02.「変数．削除レコード数」が0以外の場合、「16.個人情報バイナリデータ論理削除処理」へ遷移する
                if delete_count != 0:
                    # 16.個人情報バイナリデータ論理削除処理
                    # 16-01.以下の引数で個人情報バイナリデータ論理削除処理を実行する
                    self.delete_user_info_binary_data(
                        transaction_id_list=delete_tid_list,
                        pds_user_db_info=pds_user_db_info_response,
                        pds_user_id=request_body.pdsUserId
                    )

                    # 17.個人情報論理削除処理
                    # 17-01.以下の引数で個人情報論理削除処理を実行する
                    self.delete_user_info(
                        transaction_id_list=delete_tid_list,
                        pds_user_db_info=pds_user_db_info_response,
                        pds_user_id=request_body.pdsUserId
                    )
            else:
                # 11-02-01.空のCSVファイルを作成する
                # 11-02-02.作成したCSVを「変数．tidリストファイル」に格納する
                tid_list_file_name = FileNameConstClass.TID_LIST_NOTIFICATION_NAME + commonUtil.get_datetime_str_no_symbol() + FileNameConstClass.TID_LIST_NOTIFICATION_EXTENSION
                tid_list_csv_string = NoHeaderOneItemCsvStringClass(tid_list)
                tid_list_csv_stream = CsvStreamClass(tid_list_csv_string)
                # 11-02-03.「変数．削除レコード数」に0を格納する
                delete_count = 0
                # 11-02-04.「変数．削除対象tidリスト」に空のリストを格納する
                delete_tid_list = []

            # 18.TIDリスト保存処理
            file_path_prefix = "multiDelete/" + commonUtil.get_datetime_str_no_symbol() + "/"
            tid_file_save_path = file_path_prefix + tid_list_file_name
            put_tid_list_error_info = None
            # 18-01.「変数．tidリストファイル」をS3（バケット名：変数．PDSユーザ取得結果．S3バイナリデータ格納バケット名）に格納する
            s3_util = s3UtilClass(self.logger, pds_user_info_dict["s3ImageDataBucketName"])
            for exec_count in range(5):
                if s3_util.put_file(file_name=tid_file_save_path, data=tid_list_csv_stream.get_temp_csv()):
                    break
                if exec_count == 4:
                    # 18-02.処理が失敗した場合は「変数．エラー情報」を作成し、エラーログをCloudWatchにログ出力する
                    # 18-02-01.S3へのファイルコピーエラーが発生した場合、「変数．エラー情報」にエラー情報を追加する
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990021"]["logMessage"]))
                    put_tid_list_error_info = {
                        "errorCode": "990021",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["990021"]["message"], "990021")
                    }
                    break

            # 19.共通エラーチェック処理
            # 19-01.以下の引数で共通エラーチェック処理を実行する
            # 19-02.例外が発生した場合、例外処理に遷移
            if put_tid_list_error_info is not None:
                # ロールバック処理
                rollback_transaction = CallbackExecutor(
                    self.common_util.common_check_postgres_rollback,
                    pds_user_db_connection,
                    pds_user_db_connection_resource
                )
                # API実行履歴登録処理
                api_history_insert = CallbackExecutor(
                    self.common_util.insert_api_history,
                    commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                    request_body.pdsUserId,
                    apitypeConstClass.API_TYPE["BATCH_DELETE"],
                    None,
                    str(self.request.url),
                    json.dumps({"path_param": self.request.path_params, "query_param": self.request.query_params._dict, "header_param": commonUtil.make_headerParam(self.request.headers), "request_body": request_body.dict()}),
                    False,
                    None,
                    commonUtil.get_str_datetime()
                )
                self.common_util.common_error_check(
                    put_tid_list_error_info,
                    rollback_transaction,
                    api_history_insert
                )

            # 20.削除レポート用変数作成処理
            # 20-01.トランザクションIDの一覧項目に設定する変数を作成する
            # 20-01-01.格納条件に当てはまる場合に、変数に値を格納する
            if request_body.tidList is None:
                transaction_id_setting_str = "トランザクションIDの指定なし"
                transaction_id_setting_file_str = request_body.tidListFileName
            # 20-01-02.格納条件に当てはまる場合に、変数に値を格納する
            elif request_body.tidList is not None:
                transaction_id_setting_str = str(len(request_body.tidList)) + "件のトランザクションIDの指定あり"
                transaction_id_setting_file_str = request_body.tidListFileName

            # 20-02.保存したいデータ形式に設定する変数を作成する
            # 20-02-01.格納条件に当てはまる場合に、変数に値を格納する
            if request_body.searchCriteria.dataJsonKey is None:
                save_data_format_str = "テキスト"

            # 20-02-02.格納条件に当てはまる場合に、変数に値を格納する
            if request_body.searchCriteria.dataJsonKey is not None:
                save_data_format_str = "JSON"

            # 21.削除レポートファイル作成処理
            # 21-01.「変数．個人情報検索結果．個人情報取得結果．トランザクションID」をもとに格納用ファイルを作成する
            pdf_util = PdfUtilClass(self.logger)
            pdf_util.create_pdf(
                pds_user_name=pds_user_info_dict["pdsUserName"],
                pds_user_id=request_body.pdsUserId,
                transaction_id_setting_str=transaction_id_setting_str,
                transaction_id_setting_file_str=transaction_id_setting_file_str,
                user_id_str=request_body.searchCriteria.userIdStr,
                user_id_match_mode=request_body.searchCriteria.userIdMatchMode,
                data_json_key=request_body.searchCriteria.dataJsonKey,
                data_str=request_body.searchCriteria.dataStr,
                data_match_mode=request_body.searchCriteria.dataMatchMode,
                image_hash=request_body.searchCriteria.imageHash,
                from_date=request_body.searchCriteria.fromDate,
                to_date=request_body.searchCriteria.toDate,
                save_data_format_str=save_data_format_str,
                delete_count=delete_count,
                file_name=tid_list_file_name
            )
            # 21-02.作成したPDFファイルを「変数．削除レポートファイル」に格納する
            delete_report = pdf_util.get_pdf_file()

            # 21-03.「変数．PDSユーザ情報[5]」からバケット名を取得し、「変数．バケット名」に格納する
            bucket_name = pds_user_info_dict["s3ImageDataBucketName"]

            # 21-04.「変数．バケット名」をもとに保存先パスを作成し、「変数．保存先パス」に格納する
            delete_report_file_name = FileNameConstClass.DELETE_REPORT_NAME + FileNameConstClass.DELETE_REPORT_EXTENSION
            delete_report_file_path = file_path_prefix + delete_report_file_name

            # 22.削除レポートファイル保存処理
            put_delete_pdf_error_info = None
            s3_util = s3UtilClass(self.logger, bucket_name)
            for exec_count in range(5):
                # 22-01.「変数．削除レポートファイル」をS3（バケット名：「変数．バケット名」）に格納する
                if s3_util.put_file(file_name=delete_report_file_path, data=delete_report):
                    break
                if exec_count == 4:
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990021"]["logMessage"]))
                    put_delete_pdf_error_info = {
                        "errorCode": "990021",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["990021"]["message"], "990021")
                    }
                    break

            # 23.共通エラーチェック処理
            # 23-01.以下の引数で共通エラーチェック処理を実行する
            # 23-02.例外が発生した場合、例外処理に遷移
            if put_delete_pdf_error_info is not None:
                # S3ファイル削除処理
                tid_list_file_delete = CallbackExecutor(
                    self.delete_s3_file,
                    pds_user_info_dict["s3ImageDataBucketName"],
                    tid_file_save_path
                )
                # ロールバック処理
                rollback_transaction = CallbackExecutor(
                    self.common_util.common_check_postgres_rollback,
                    pds_user_db_connection,
                    pds_user_db_connection_resource
                )
                # API実行履歴登録処理
                api_history_insert = CallbackExecutor(
                    self.common_util.insert_api_history,
                    commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                    request_body.pdsUserId,
                    apitypeConstClass.API_TYPE["BATCH_DELETE"],
                    None,
                    str(self.request.url),
                    json.dumps({"path_param": self.request.path_params, "query_param": self.request.query_params._dict, "header_param": commonUtil.make_headerParam(self.request.headers), "request_body": request_body.dict()}),
                    False,
                    None,
                    commonUtil.get_str_datetime()
                )
                self.common_util.common_error_check(
                    put_delete_pdf_error_info,
                    tid_list_file_delete,
                    rollback_transaction,
                    api_history_insert
                )

            # 24.WBT新規メール情報登録API実行処理
            wbt_mails_add_api_error_info = None
            file_name_list = [
                tid_list_file_name,
                delete_report_file_name
            ]
            try:
                # 24-01.以下の引数でWBT「新規メール情報登録API」を呼び出し処理を実行する
                # 24-02.WBT新規メール情報登録APIからのレスポンスを、「変数．WBT新規メール情報登録API実行結果」に格納する
                wbt_mails_add_api_exec_result = self.common_util.wbt_mails_add_api_exec(
                    wbtConstClass.REPOSITORY_TYPE["RETURN"],
                    file_name_list,
                    commonUtil.get_str_datetime_in_X_days(7),
                    None,
                    wbtConstClass.MESSAGE["USER_PROFILE_MULTI_DELETE"],
                    request_body.mailAddressTo,
                    request_body.mailAddressCc,
                    wbtConstClass.TITLE["USER_PROFILE_MULTI_DELETE"]
                )
            except Exception:
                # 24-03.WebBureauTransferの処理に失敗した場合、「変数．エラー情報」にエラー情報を作成する
                wbt_mails_add_api_error_info = {
                    "errorCode": "990011",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["990011"]["message"], "990011")
                }
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990011"]["logMessage"]))

            # 25.共通エラーチェック処理
            # 25-01.以下の引数で共通エラーチェック処理を実行する
            # 25-02 例外が発生した場合、例外処理に遷移
            if wbt_mails_add_api_error_info is not None:
                # S3ファイル削除処理
                tid_list_file_delete = CallbackExecutor(
                    self.delete_s3_file,
                    pds_user_info_dict["s3ImageDataBucketName"],
                    tid_file_save_path
                )
                # S3ファイル削除処理
                delete_report_file_delete = CallbackExecutor(
                    self.delete_s3_file,
                    pds_user_info_dict["s3ImageDataBucketName"],
                    delete_report_file_path
                )
                # ロールバック処理
                rollback_transaction = CallbackExecutor(
                    self.common_util.common_check_postgres_rollback,
                    pds_user_db_connection,
                    pds_user_db_connection_resource
                )
                # API実行履歴登録処理
                api_history_insert = CallbackExecutor(
                    self.common_util.insert_api_history,
                    commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                    request_body.pdsUserId,
                    apitypeConstClass.API_TYPE["BATCH_DELETE"],
                    None,
                    str(self.request.url),
                    json.dumps({"path_param": self.request.path_params, "query_param": self.request.query_params._dict, "header_param": commonUtil.make_headerParam(self.request.headers), "request_body": request_body.dict()}),
                    False,
                    None,
                    commonUtil.get_str_datetime()
                )
                self.common_util.common_error_check(
                    wbt_mails_add_api_error_info,
                    tid_list_file_delete,
                    delete_report_file_delete,
                    rollback_transaction,
                    api_history_insert
                )

            # 26.WBTのファイル登録API実行処理
            wbt_file_add_api_error_info = None
            try:
                # 26-01.以下のパラメータでWBTファイル登録APIを呼び出し処理を実行する
                self.common_util.wbt_file_add_api_exec(
                    wbt_mails_add_api_exec_result["id"],
                    wbt_mails_add_api_exec_result["attachedFiles"][0]["id"],
                    tid_list_csv_stream.get_temp_csv(),
                    None,
                    None,
                )
            except Exception:
                # 26-02.WBTファイル登録APIからのレスポンスを、「変数．WBTファイル登録API実行結果」に格納する
                # 26-02-01.WebBureauTransferの処理に失敗した場合、「変数．エラー情報」にエラー情報を作成する
                wbt_file_add_api_error_info = {
                    "errorCode": "990013",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["990013"]["message"], "990013")
                }
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990013"]["logMessage"]))

            try:
                # 26-03.以下のパラメータでWBTファイル登録APIを呼び出し処理を実行する
                self.common_util.wbt_file_add_api_exec(
                    wbt_mails_add_api_exec_result["id"],
                    wbt_mails_add_api_exec_result["attachedFiles"][1]["id"],
                    delete_report,
                    None,
                    None,
                )
            except Exception:
                # 26-04.WBTファイル登録APIからのレスポンスを、「変数．WBTファイル登録API実行結果」に格納する
                # 26-04-01.WebBureauTransferの処理に失敗した場合、「変数．エラー情報」にエラー情報を作成する
                wbt_file_add_api_error_info = {
                    "errorCode": "990013",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["990013"]["message"], "990013")
                }
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990013"]["logMessage"]))

            # 27.共通エラーチェック処理
            # 27-01.以下の引数で共通エラーチェック処理を実行する
            # 27-02 例外が発生した場合、例外処理に遷移
            if wbt_file_add_api_error_info is not None:
                # WBT送信取り消しAPI実行
                wbt_send_delete_api_exec = CallbackExecutor(
                    self.common_util.wbt_mail_cancel_exec,
                    wbt_mails_add_api_exec_result["id"]
                )
                # S3ファイル削除処理
                tid_list_file_delete = CallbackExecutor(
                    self.delete_s3_file,
                    pds_user_info_dict["s3ImageDataBucketName"],
                    tid_file_save_path
                )
                # S3ファイル削除処理
                delete_report_file_delete = CallbackExecutor(
                    self.delete_s3_file,
                    pds_user_info_dict["s3ImageDataBucketName"],
                    delete_report_file_path
                )
                # ロールバック処理
                rollback_transaction = CallbackExecutor(
                    self.common_util.common_check_postgres_rollback,
                    pds_user_db_connection,
                    pds_user_db_connection_resource
                )
                # API実行履歴登録処理
                api_history_insert = CallbackExecutor(
                    self.common_util.insert_api_history,
                    commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                    request_body.pdsUserId,
                    apitypeConstClass.API_TYPE["BATCH_DELETE"],
                    None,
                    str(self.request.url),
                    json.dumps({"path_param": self.request.path_params, "query_param": self.request.query_params._dict, "header_param": commonUtil.make_headerParam(self.request.headers), "request_body": request_body.dict()}),
                    False,
                    None,
                    commonUtil.get_str_datetime()
                )
                self.common_util.common_error_check(
                    wbt_file_add_api_error_info,
                    wbt_send_delete_api_exec,
                    tid_list_file_delete,
                    delete_report_file_delete,
                    rollback_transaction,
                    api_history_insert
                )

            # 28.トランザクションコミット処理
            # 28-01.「個人情報削除トランザクション」をコミットする
            pds_user_db_connection_resource.commit_transaction(pds_user_db_connection)
            pds_user_db_connection_resource.close_connection(pds_user_db_connection)

            for tid in delete_tid_list:
                # 28.個人情報一括DLバッチキュー発行処理
                # 28-01.以下の引数で個人情報削除バッチキュー発行処理を実行する
                self.common_util.transaction_delete_batch_queue_issue(transactionId=tid, pdsUserId=request_body.pdsUserId)

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

    def delete_user_info_binary_data(self, transaction_id_list: list, pds_user_db_info: dict, pds_user_id: str):
        """
        個人情報バイナリデータ論理削除処理

        Args:
            transaction_id_list (list): トランザクションIDリスト
            pds_user_db_info (dict): PDSユーザDB接続情報
            pds_user_id (string): PDSユーザID

        """
        try:
            pds_user_db_connection_resource: PostgresDbUtilClass = pds_user_db_info["pds_user_db_connection_resource"]
            pds_user_db_connection = pds_user_db_info["pds_user_db_connection"]
            # 01.個人情報バイナリデータ更新処理
            pds_user_delete_binary_data_update_error_info = None
            # 01-01.個人情報バイナリデータテーブルを更新する
            pds_user_delete_binary_data_update_result = pds_user_db_connection_resource.update(
                pds_user_db_connection,
                SqlConstClass.USER_PROFILE_DELETE_BINARY_DATA_MULTI_UPDATE_SQL,
                tuple(transaction_id_list)
            )
            # 01-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not pds_user_delete_binary_data_update_result["result"]:
                pds_user_delete_binary_data_update_error_info = self.common_util.create_postgresql_log(
                    pds_user_delete_binary_data_update_result["errorObject"],
                    None,
                    None,
                    pds_user_delete_binary_data_update_result["stackTrace"]
                ).get("errorInfo")

            # 02.共通エラーチェック処理
            # 02-01.以下の引数で共通エラーチェック処理を実行する
            if pds_user_delete_binary_data_update_error_info is not None:
                # ロールバック処理
                rollback_transaction = CallbackExecutor(
                    self.common_util.common_check_postgres_rollback,
                    pds_user_db_connection,
                    pds_user_db_connection_resource
                )
                # API実行履歴登録処理
                api_history_insert = CallbackExecutor(
                    self.common_util.insert_api_history,
                    commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                    pds_user_id,
                    apitypeConstClass.API_TYPE["BATCH_DELETE"],
                    None,
                    str(self.request.url),
                    json.dumps({"path_param": self.request.path_params, "query_param": self.request.query_params._dict, "header_param": commonUtil.make_headerParam(self.request.headers)}),
                    False,
                    None,
                    commonUtil.get_str_datetime()
                )
                # 02-02.例外が発生した場合、例外処理に遷移
                self.common_util.common_error_check(
                    pds_user_delete_binary_data_update_error_info,
                    rollback_transaction,
                    api_history_insert
                )

            # 03.終了処理
            # 03-01.レスポンス情報を作成し、返却する
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

    def delete_user_info(self, transaction_id_list: list, pds_user_db_info: dict, pds_user_id: str):
        """
        個人情報論理削除処理

        Args:
            transaction_id_list (list): トランザクションIDリスト
            pds_user_db_info (dict): PDSユーザDB接続情報
            pds_user_id (str): PDSユーザID

        """
        try:
            pds_user_db_connection_resource: PostgresDbUtilClass = pds_user_db_info["pds_user_db_connection_resource"]
            pds_user_db_connection = pds_user_db_info["pds_user_db_connection"]
            # 01.個人情報更新処理
            pds_user_delete_data_update_error_info = None
            # 01-01.個人情報テーブルを更新する
            pds_user_delete_data_update_result = pds_user_db_connection_resource.update(
                pds_user_db_connection,
                SqlConstClass.USER_PROFILE_DELETE_DATA_MULTI_UPDATE_SQL,
                tuple(transaction_id_list)
            )
            # 01-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not pds_user_delete_data_update_result["result"]:
                pds_user_delete_data_update_error_info = self.common_util.create_postgresql_log(
                    pds_user_delete_data_update_result["errorObject"],
                    None,
                    None,
                    pds_user_delete_data_update_result["stackTrace"]
                ).get("errorInfo")

            # 02.共通エラーチェック処理
            # 02-01.以下の引数で共通エラーチェック処理を実行する
            if pds_user_delete_data_update_error_info is not None:
                # ロールバック処理
                rollback_transaction = CallbackExecutor(
                    self.common_util.common_check_postgres_rollback,
                    pds_user_db_connection,
                    pds_user_db_connection_resource
                )
                # API実行履歴登録処理
                api_history_insert = CallbackExecutor(
                    self.common_util.insert_api_history,
                    commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                    pds_user_id,
                    apitypeConstClass.API_TYPE["BATCH_DELETE"],
                    None,
                    str(self.request.url),
                    json.dumps({"path_param": self.request.path_params, "query_param": self.request.query_params._dict, "header_param": commonUtil.make_headerParam(self.request.headers)}),
                    False,
                    None,
                    commonUtil.get_str_datetime()
                )
                # 02-02.例外が発生した場合、例外処理に遷移
                self.common_util.common_error_check(
                    pds_user_delete_data_update_error_info,
                    rollback_transaction,
                    api_history_insert
                )

            # 03.終了処理
            # 03-01.レスポンス情報を作成し、返却する
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

    def delete_s3_file(self, bucket_name: str, key: str):
        """
        S3ファイル削除処理

        Args:
            bucket_name (str): バケット名
            key (str, optional): ファイルパス. Defaults to None.
        """
        try:
            error_info = None
            # 01.S3のファイル削除処理
            s3_util = s3UtilClass(self.logger, bucket_name)
            # 01-01.「引数．ファイルパス」のデータをS3から削除する
            for exec_count in range(5):
                if s3_util.deleteFile(file_name=key):
                    break
                if exec_count == 4:
                    # 01-02.処理が失敗した場合は「変数．エラー情報」を作成し、エラーログをCloudWatchにログ出力する
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990022"]["logMessage"]))
                    error_info = {
                        "errorCode": "990022",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["990022"]["message"], "990022")
                    }
                    break

            # 02.共通エラーチェック処理
            # 02-01.以下の引数で共通エラーチェック処理を実行する
            # 02-02.例外が発生した場合、例外処理に遷移
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
