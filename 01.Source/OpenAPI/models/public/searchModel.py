from typing import Optional
import json
import math
from pydantic import BaseModel
from fastapi import Request
from logging import Logger
import traceback

# Exception
from exceptionClass.PDSException import PDSException

# Const
from const.messageConst import MessageConstClass
from const.apitypeConst import apitypeConstClass

# Util
import util.commonUtil as commonUtil
from util.commonUtil import CommonUtilClass
from util.callbackExecutorUtil import CallbackExecutor
import util.logUtil as logUtil


class requestBody(BaseModel):
    """
    リクエストボディクラス

    Args:
        BaseModel (Object): Pydanticのベースクラス
    """
    userIdMatchMode: Optional[str] = None
    userIdStr: Optional[str] = None
    dataJson: Optional[str] = None
    dataMatchMode: Optional[list] = None
    dataStr: Optional[list] = None
    imageHash: Optional[str] = None
    fromDate: Optional[str] = None
    toDate: Optional[str] = None


class searchModelClass():
    def __init__(self, logger: Logger, request: Request, pds_user_info, page_no: int, pds_user_domain_name: str):
        """
        コンストラクタ

        Args:
            logger (Logger): ロガー（TRACE）
        """
        self.logger: Logger = logger
        self.request: Request = request
        self.common_util = CommonUtilClass(logger)
        self.pds_user_info = pds_user_info
        self.page_no = page_no
        self.pds_user_domain_name = pds_user_domain_name

    def main(self, request_body: requestBody):
        """
        個人情報検索 メイン処理

        Args:
            requestBody (object): リクエストボディ

        Returns:
            dict: 処理結果
        """
        try:
            try:
                # 02.検索条件作成処理
                # 02-01.検索条件の作成
                search_criteria = {
                    "userIdMatchMode": request_body.userIdMatchMode,
                    "userIdStr": request_body.userIdStr,
                    "dataJsonKey": request_body.dataJson,
                    "dataMatchMode": request_body.dataMatchMode,
                    "dataStr": request_body.dataStr,
                    "imageHash": request_body.imageHash,
                    "fromDate": request_body.fromDate,
                    "toDate": request_body.toDate
                }
                # 03.tidリスト作成処理実行
                # 03-01.以下の引数でtidリスト作成処理を実行する
                tid_list_create_result = self.common_util.tid_list_create_exec(
                    searchCriteria=search_criteria,
                    pdsUserInfo=self.pds_user_info
                )
            except PDSException as e:
                # 04.共通エラーチェック処理
                # 04-01.以下の引数で共通エラーチェック処理を実行する
                # 04-02.例外が発生した場合、例外処理に遷移
                # API実行履歴登録処理
                api_history_insert = CallbackExecutor(
                    self.common_util.insert_api_history,
                    commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                    self.pds_user_info["pdsUserId"],
                    apitypeConstClass.API_TYPE["SEARCH"],
                    self.pds_user_domain_name,
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

            # 05.返却項目成形処理
            # 取得が0件の時にゼロ除算を実施してしまうのでケースを分割
            tid_list = tid_list_create_result["tidList"]
            tid_count = len(tid_list)
            if tid_count == 0:
                max_page_no = 0
                out_tid_list = []
            else:
                max_page_no = math.ceil(tid_count / 1000)
                if max_page_no < self.page_no:
                    out_tid_list = []
                elif max_page_no == self.page_no:
                    out_tid_list = tid_list[(self.page_no - 1) * 1000:]
                else:
                    out_tid_list = tid_list[(self.page_no - 1) * 1000:(self.page_no * 1000)]
            # 05-01.下記の情報を変数に格納する
            return {
                "result": True,
                "max_page_no": max_page_no,
                "max_item_no": tid_count,
                "page_no": self.page_no,
                "tid_list": out_tid_list
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
