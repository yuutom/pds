import base64
import json
import math
import traceback
import asyncio
from typing import Optional
from fastapi import Request

## コールバック関数
from util.callbackExecutorUtil import CallbackExecutor
# RequestBody
from pydantic import BaseModel
from exceptionClass.PDSException import PDSException
from util.fileUtil import CsvStreamClass, NoHeaderOneItemCsvStringClass

from util.commonUtil import CommonUtilClass
from util.postgresDbUtil import PostgresDbUtilClass
import util.logUtil as logUtil
from const.messageConst import MessageConstClass
from const.apitypeConst import apitypeConstClass
from const.sqlConst import SqlConstClass
import util.commonUtil as commonUtil


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
    """
    リクエストボディクラス

    Args:
        BaseModel (Object): Pydanticのベースクラス
    """
    pdsUserId: Optional[str] = None
    tidListOutputFlg: Optional[bool] = None
    searchCriteria: Optional[searchCriteriaInfo] = None


class searchTfOperatorModelClass():
    def __init__(self, logger, request: Request):
        """
        コンストラクタ

        Args:
            logger (Logger): ロガー（TRACE）
        """
        self.logger = logger
        self.request: Request = request
        self.common_util = CommonUtilClass(logger)

    async def main(self, page_no: int, request_body: requestBody, tf_operator_id: str):
        """
        個人情報検索API メイン処理

        Args:
            page_no (int): ページNo(パスパラメータ)
            request_body (requestBody): リクエストボディ
        Raises:
            e: 例外処理
            PDSException: PDS例外処理

        Returns:
            dict: 処理結果
        """
        try:
            # 02.共通DB接続準備処理
            # 02-01.共通DB接続情報取得処理
            common_db_connection_resource: PostgresDbUtilClass = None
            # 02-01-01.AWS SecretsManagerから共通DB接続情報を取得して、変数．共通DB接続情報に格納する
            # 02-01-02.「変数．共通DB接続情報」を利用して、共通DBに対してのコネクションを作成する
            common_db_info_response = self.common_util.get_common_db_info_and_connection()
            if not common_db_info_response["result"]:
                return common_db_info_response
            else:
                common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
                common_db_connection = common_db_info_response["common_db_connection"]

            # 03.PDSユーザ取得処理
            pds_user_exist_error_info = None
            # 03-01.PDSユーザテーブルからデータを取得し、「変数．PDSユーザ取得結果」に1レコードをタプルとして格納する
            pds_user_search_list = common_db_connection_resource.select_tuple_one(
                common_db_connection,
                SqlConstClass.MONGODB_SECRET_NAME_SELECT_SQL,
                request_body.pdsUserId
            )
            # 03-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not pds_user_search_list["result"]:
                pds_user_exist_error_info = self.common_util.create_postgresql_log(
                    pds_user_search_list["errorObject"],
                    None,
                    None,
                    pds_user_search_list["stackTrace"]
                ).get("errorInfo")

            # 04.共通エラーチェック処理
            # 04-01.以下の引数で共通エラーチェック処理を実行する
            # 04-02.例外が発生した場合、例外処理に遷移
            if pds_user_exist_error_info is not None:
                # API実行履歴登録処理
                api_history_insert = CallbackExecutor(
                    self.common_util.insert_api_history,
                    commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                    request_body.pdsUserId,
                    apitypeConstClass.API_TYPE["SEARCH_CLOSED"],
                    None,
                    str(self.request.url),
                    json.dumps({"path_param": self.request.path_params, "query_param": self.request.query_params._dict, "header_param": commonUtil.make_headerParam(self.request.headers), "request_body": request_body.dict()}),
                    False,
                    tf_operator_id,
                    commonUtil.get_str_datetime()
                )
                self.common_util.common_error_check(
                    pds_user_exist_error_info,
                    api_history_insert
                )

            # 05.MongoDB検索判定処理
            # 05-01.「リクエストのリクエストボディ．保存データJsonキー情報」がNullの場合、「07.個人情報検索処理」に遷移する
            # 05-02.「リクエストのリクエストボディ．保存データJsonキー情報」がNull以外の場合、「06.MongoDB検索処理」に遷移する
            object_id_list = []
            if request_body.searchCriteria.dataJsonKey is not None:
                # 06.MongoDB検索処理
                # 06.以下の引数でMongoDB検索処理を実行
                # 06.レスポンスを、「変数．MongoDB検索処理実行結果」に格納する
                pds_user_column_list = [
                    "pds_user_instance_secret_name",
                    "tokyo_a_mongodb_secret_name",
                    "tokyo_c_mongodb_secret_name",
                    "osaka_a_mongodb_secret_name",
                    "osaka_c_mongodb_secret_name"
                ]
                pds_user_search_dict = {column: data for column, data in zip(pds_user_column_list, pds_user_search_list["query_results"])}
                mongo_search_result = self.common_util.mongodb_search(
                    pds_user_search_dict,
                    request_body.searchCriteria.dataMatchMode,
                    request_body.searchCriteria.dataJsonKey,
                    request_body.searchCriteria.dataStr
                )
                object_id_list = mongo_search_result["objectIdList"]

            # 07.個人情報検索処理
            # 07-01.以下の引数で個人情報検索処理を実行する
            # 07-02.レスポンスを、「変数．個人情報検索結果」に格納する
            profile_search_result = self.common_util.search_user_profile(
                pds_user_search_dict["pds_user_instance_secret_name"],
                request_body.searchCriteria.dict(),
                object_id_list
            )

            # 08.共通エラーチェック処理
            # 08-01.以下の引数で共通エラーチェック処理を実行する
            # 08-02.例外が発生した場合、例外処理に遷移
            if profile_search_result.get("errorInfo"):
                # API実行履歴登録処理
                api_history_insert = CallbackExecutor(
                    self.common_util.insert_api_history,
                    commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                    request_body.pdsUserId,
                    apitypeConstClass.API_TYPE["SEARCH_CLOSED"],
                    None,
                    str(self.request.url),
                    json.dumps({"path_param": self.request.path_params, "query_param": self.request.query_params._dict, "header_param": commonUtil.make_headerParam(self.request.headers), "request_body": request_body.dict()}),
                    False,
                    tf_operator_id,
                    commonUtil.get_str_datetime()
                )
                self.common_util.common_error_check(
                    profile_search_result["errorInfo"],
                    api_history_insert
                )

            # 09.個人情報検索結果絞り込み処理
            # 09-01.「変数．個人情報検索結果」の内、「リクエストのパスパラメータ．ページNo」に応じた要素数のデータを取得する
            #         変数．個人情報検索結果[(リクエストのパスパラメータ．ページNo - 1) * 1000 ： (リクエストのパスパラメータ．ページNo * 1000) - 1]
            profile_count = profile_search_result["count"]
            if profile_count == 0:
                max_page_no = 0
                out_tid_list = []
                out_user_id_list = []
                out_save_date_list = []
                out_data_list = []
                out_image_hash_list = []
            else:
                max_page_no = math.ceil(profile_count / 1000)
                if max_page_no < page_no:
                    out_tid_list = []
                    out_user_id_list = []
                    out_save_date_list = []
                    out_data_list = []
                    out_image_hash_list = []
                elif max_page_no == page_no:
                    out_tid_list = profile_search_result["transactionId"][(page_no - 1) * 1000:]
                    out_user_id_list = profile_search_result["userId"][(page_no - 1) * 1000:]
                    out_save_date_list = profile_search_result["saveDate"][(page_no - 1) * 1000:]
                    out_data_list = profile_search_result["data"][(page_no - 1) * 1000:]
                    out_image_hash_list = profile_search_result["imageHash"][(page_no - 1) * 1000:]
                else:
                    out_tid_list = profile_search_result["transactionId"][(page_no - 1) * 1000:(page_no * 1000) - 1]
                    out_user_id_list = profile_search_result["userId"][(page_no - 1) * 1000:(page_no * 1000) - 1]
                    out_save_date_list = profile_search_result["saveDate"][(page_no - 1) * 1000:(page_no * 1000) - 1]
                    out_data_list = profile_search_result["data"][(page_no - 1) * 1000:(page_no * 1000) - 1]
                    out_image_hash_list = profile_search_result["imageHash"][(page_no - 1) * 1000:(page_no * 1000) - 1]

            # 10.tidリスト出力有無フラグ判定処理
            tid_list = None
            # 10-01.「リクエストのリクエストボディ．tidリスト出力有無フラグ」がtrueの場合、「12. tidリスト作成処理」に遷移する
            # 10-02.「リクエストのリクエストボディ．tidリスト出力有無フラグ」がfalseの場合、「11. tidリスト未作成処理」に遷移する
            if request_body.tidListOutputFlg:
                # 12.tidリスト作成処理
                # TODO コメントアウトをはずす
                # file_name_datetime_str = commonUtil.get_datetime_jst().strftime('%Y%m%d%H%M%S%f')[:-3]
                # 11-01.「変数．個人情報検索結果．トランザクションID」をもとにCSVファイルを作成する
                #       「トランザクションID」の取得方法注記
                #       変数．個人情報検索結果[(リクエストのパスパラメータ．ページNo - 1) * 1000 ： (リクエストのパスパラメータ．ページNo * 1000) - 1]
                #       ※1の場合、0～999　2の場合、1000～1999　3の場合、2000～2999
                # TODO コメントアウトをはずす
                # file_name = SystemConstClass.TID_LIST_FILE_PREFIX + file_name_datetime_str + SystemConstClass.TID_LIST_FILE_EXTENSION
                tid_list_evacuate_csv = NoHeaderOneItemCsvStringClass(out_tid_list)

                # 12-02.作成したCSVを「変数．tidリスト」に格納する
                tid_list = CsvStreamClass(tid_list_evacuate_csv)

                # 12-03.作成したCSVをBase64エンコードした文字列を「変数．tidリスト文字列」に格納する
                tid_list_str = base64.b64encode(tid_list.get_temp_csv().getvalue()).decode()
                # 12-04.「変数．tidリスト」をNullにする
                tid_list = None
            else:
                # 11.tidリスト未作成処理
                # 11-01.「変数．tidリスト文字列」にNullを格納する
                tid_list_str = None

            # 13.参照情報格納リスト作成処理
            # 13-01.参照情報を格納するための空のリストを作成する
            reference_info_list = []

            # 「変数．個人情報検索結果．トランザクションID」の種類数分繰り返す
            save_data_masking_list = []
            for masking_loop_count, profile_data in enumerate(out_data_list):
                # 14.保存したいデータマスキング処理リスト作成処理
                # 14-01.「変数．保存したいデータマスキング処理リスト」に保存したいデータマスキング処理を追加する
                save_data_masking_list.append(self.save_data_masking(profile_data))

            # 15.保存したいデータマスキング処理実行処理
            # 15-01.「変数．保存したいデータマスキング処理リスト」をもとに、保存したいデータマスキング処理を並列で実行する
            # 15-02.レスポンスを「変数．保存したいデータマスキング処理実行結果リスト」に格納する
            binary_save_data_masking_result_list = await asyncio.gather(*save_data_masking_list)

            for transaction_id_loop_count, masking_data in enumerate(binary_save_data_masking_result_list):
                # 16.参照情報作成処理
                # 16-01.「変数．参照情報」に以下の値を格納する
                reference_info = {
                    "transactionId": out_tid_list[transaction_id_loop_count],
                    "userId": len(out_user_id_list[transaction_id_loop_count]),
                    "saveDate": out_save_date_list[transaction_id_loop_count].strftime('%Y/%m/%d %H:%M:%S.%f')[:23],
                    "data": {"key": len(masking_data["saveDataMasking"])},
                    "imageHash": out_image_hash_list[transaction_id_loop_count]
                }
                # 16-02.「変数．参照情報リスト」に「変数．参照情報」を追加する
                reference_info_list.append(reference_info)

            # 不要になったリソースの片付け
            self.common_util = None

            return {
                "maxPageCount": max_page_no,
                "maxItemCount": profile_count,
                "pageNo": page_no,
                "tidList": tid_list_str,
                "infoList": reference_info_list
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

    async def save_data_masking(self, save_data: str):
        """
        保存したいデータマスキング処理

        Args:
            save_data (str): 保存したいデータ(PDSユーザテーブルからの取得情報)

        Raises:
            e: 例外処理
            PDSException: PDS例外処理

        Returns:
            str: マスキングされた保存したいデータ
        """
        try:
            save_data_masking: str = None
            # 01.Json判定処理
            # 01-01.「引数．保存したいデータ」がJson形式への変換が可能な場合、「03.保存したいデータの辞書型変換処理」に遷移する
            # 01-02.「引数．保存したいデータ」がJson形式への変換ができない場合、「02.文字数取得処理」に遷移する
            if commonUtil.is_json(save_data):
                pass
                # 03.保存したいデータの辞書型変換処理
                # 03-01.「引数．保存したいデータ」を辞書型に変換して、「変数．保存したいデータ辞書」を作成する
                save_data_dict = json.loads(save_data)

                # 04.Jsonデータマスキング処理
                # 04-01.以下の引数でJsonデータマスキング処理を実施する
                masking_data_resronce = self.json_data_masking(save_data_dict)["maskingData"]
                # 04-02.レスポンスを「変数．マスキングされたデータ」に格納する
                masking_data = masking_data_resronce

                # 05.Json文字列変換処理
                # 05-01.「変数．マスキングされたデータ」を文字列に変換して、「変数．マスキングされた保存したいデータ」を格納する
                save_data_masking = json.dumps(masking_data)

            else:
                # 02.文字数取得処理
                # 02-01.「引数．保存したいデータ」の文字数を取得し、「変数．マスキングされた保存したいデータ」に格納する
                save_data_masking = str(len(save_data))

            # 06.終了処理
            # 06-01.レスポンス情報を作成し、返却する
            return {
                "saveDataMasking": save_data_masking
            }
        # 例外処理(PDSException)
        except PDSException as e:
            # PDSExceptionオブジェクトをエラーとしてスローする
            raise e

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

    def json_data_masking(self, data: dict):
        """
        Jsonデータマスキング処理

        Args:
            data (object or list): マスキング対象(Json型かリスト型のデータ)

        Raises:
            e: 例外処理
            PDSException: PDS例外処理

        Returns:
            object or list: マスキングされたデータ(マスキング済みのJson型かリスト型のデータ)
        """
        try:
            # 01.マスキング対象コピー取得処理
            # 01-01.「引数．マスキング対象」のコピーを取得して、「変数．マスキング対象コピー」を作成する
            masking_data_copy = data
            # 変数．マスキングデータ
            masking_data: str = None

            # 02.マスキング対象型判定処理
            if commonUtil.is_json(data):
                # 02-01.「引数．マスキング対象」がJson形式の場合、「03.Jsonキー・バリューリスト取得処理」に遷移する
                # 03.Jsonキー・バリューリスト取得処理
                # 03-01.「引数．マスキング対象」からキーを取得し、「変数．Jsonキーリスト」を作成する
                # TODO: キー取得方法とJsonキーリストの設定方法を確認する
                json_key_list = data.keys()

                json_loop_count: int = 0
                # 「変数．Jsonキーリスト」の要素数だけ繰り返す
                for json_key in json_key_list:
                    # 04.Jsonバリュー型判定処理
                    if commonUtil.is_json(data[json_key]):
                        # 04-01.「引数．マスキング対象」から、「変数．Jsonキーリスト[変数．Jsonループ数]」で取得した値の型が、
                        #        Json型 もしくは リスト型だった場合、「05.Jsonデータマスキング処理」に遷移する
                        # 05.Jsonデータマスキング処理
                        # 05-01.以下の引数でJsonデータマスキング処理を実施する
                        # 05-02.レスポンスを「変数．マスキングデータ」に格納する
                        masking_data = self.json_data_masking(data[json_key])["maskingData"]
                    else:
                        # 04-02.「引数．マスキング対象」から、「変数．Jsonキーリスト[変数．Jsonループ数]」で取得した値の型が、
                        #        Json型 もしくは リスト型以外だった場合、「06.文字数取得処理」に遷移する
                        # 06.文字数取得処理
                        # 06-01.「引数．マスキング対象」から、「変数．Jsonキーリスト[変数．Jsonループ数]」で取得した値を文字列型にキャストして、
                        #        文字数を取得し、「変数．マスキングデータ」に格納する
                        masking_data = str(len(data[json_key]))

                    # 07.マスキング対象コピー更新処理
                    # 07-01.「変数．マスキング対象コピー」に、「変数．マスキングデータ」を格納する
                    masking_data_copy[json_key] = masking_data
                json_loop_count += 1
            else:
                list_loop_count: int = 0
                # 「引数．マスキング対象」の要素数だけ繰り返す
                for json_key in data:
                    # 08.リストバリュー型判定処理
                    if commonUtil.is_json(json_key[list_loop_count]):
                        # 08-01.「引数．マスキング対象」から、「変数．リストループ数」で取得した値の型が、
                        #        Json型 もしくは リスト型だった場合、「09.Jsonデータマスキング処理」に遷移する
                        # 09.Jsonデータマスキング処理
                        # 09-01.以下の引数でJsonデータマスキング処理を実施する
                        # 09-02.レスポンスを「変数．マスキングデータ」に格納する
                        masking_data = self.json_data_masking(json_key[list_loop_count])["maskingData"]
                    else:
                        # 08-02.「引数．マスキング対象」から、「変数．リストループ数」で取得した値の型が、
                        #        Json型 もしくは リスト型以外だった場合、「10.文字数取得処理」に遷移する
                        # 10.文字数取得処理
                        # 10-01.「引数．マスキング対象」から、「変数．Jsonキーリスト[変数．Jsonループ数]」で取得した値を文字列型にキャストして、
                        #        文字数を取得し、「変数．マスキングデータ」に格納する
                        masking_data = str(len(json_key[list_loop_count]))

                    # 11.マスキング対象コピー更新処理
                    # 11-01.「変数．マスキング対象コピー」に、「変数．マスキングデータ」を格納する
                    masking_data_copy[list_loop_count] = masking_data

                    list_loop_count += 1
            # 12.終了処理
            # 12-01.レスポンス情報を作成し、返却する
            return {
                "maskingData": masking_data_copy
            }
        # 例外処理(PDSException)
        except PDSException as e:
            # PDSExceptionオブジェクトをエラーとしてスローする
            raise e

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
