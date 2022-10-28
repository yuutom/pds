from typing import Optional
import traceback
import json
from logging import Logger
# FastApi
from fastapi import APIRouter, Request
# RequestBody
from pydantic import BaseModel
# Security
from fastapi.security import OAuth2PasswordBearer

# 自作クラス
## 業務ロジッククラス
from models.batch.transactionMultiCreateBatchModel import transactionMultiCreateBatchModelClass
## utilクラス
import util.logUtil as logUtil
from util.commonUtil import CommonUtilClass
## 固定値クラス
from const.messageConst import MessageConstClass
from const.systemConst import SystemConstClass
## 共通パラメータ検証クラス
from util.commonParamCheck import checkPdsUserId
# Exception
from exceptionClass.PDSException import PDSException

# Bearerトークン設定
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="bearerToken")

# 処理名
EXEC_NAME: str = "transactionMultiCreateBatch"
EXEC_NAME_JP: str = "個人情報一括登録バッチ"

# ルータ作成
router = APIRouter()


class requestBody(BaseModel):
    pdsUserId: Optional[str] = None


def input_check(trace_logger: Logger, request_body: requestBody):
    """
    パラメータ検証処理

    Args:
        trace_logger (Logger): ロガー（TRACE）
        request_body (requestBody): リクエストボディ

    Returns:
        dict: パラメータ検証処理結果
    """
    error_info_list = []
    try:
        # 01-01.リクエストボディ検証処理
        # 01-01-01.PDSユーザID検証処理
        # 01-01-01-01.以下の引数でPDSユーザID検証処理を実行する
        check_pds_user_id = checkPdsUserId.CheckPdsUserId(trace_logger, request_body.pdsUserId).get_result()
        # 01-01-01-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not check_pds_user_id["result"]:
            [error_info_list.append(error_info) for error_info in check_pds_user_id["errorInfo"]]

        # 02. 終了処理
        # 02-01.レスポンス情報を作成し、返却する
        if len(error_info_list) == 0:
            # 02-01-01.「変数．エラー情報リスト」に値が設定されていない場合、下記のレスポンス情報を返却する
            return {
                "result": True
            }
        else:
            # 02-01-02.「変数．エラー情報リスト」に値が設定されている場合、下記のレスポンス情報を返却する
            return {
                "result": False,
                "errorInfo": error_info_list
            }

    # 例外処理(PDSException)
    except PDSException as e:
        raise e

    # 例外処理
    except Exception as e:
        trace_logger.error(logUtil.message_build(MessageConstClass.ERRORS["999999"]["logMessage"], str(e), traceback.format_exc()))
        raise PDSException(
            {
                "errorCode": "999999",
                "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
            }
        )


# 個人情報一括登録バッチ
@router.post("/api/2.0/batch/transactionMultiCreateBatch")
async def transaction_multi_create_batch(
    request_body: requestBody,
    request: Request
):
    """
    個人情報一括登録バッチ

    """
    # ロガー作成
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", request)
    try:
        in_logger.info(logUtil.message_build(MessageConstClass.IN_LOG["000000"]["logMessage"], EXEC_NAME_JP))

        common_util = CommonUtilClass(trace_logger)

        # 01.パラメータ取得処理
        # 01-01.AWS SQSから以下のパラメータを取得し、変数に格納する
        # 01-02.バッチ概要【入力パラメータチェック処理】を実施
        # 01-02-01.【入力パラメータチェック処理】に違反している場合、「変数．エラー情報」にエラー情報を追加する
        input_check_result = input_check(trace_logger, request_body)

        # 02.共通エラーチェック処理
        # 02-01.以下の引数で共通エラーチェック処理を実行する
        # 02-02.例外が発生した場合、例外処理に遷移
        if input_check_result.get("errorInfo"):
            common_util.common_error_check(
                input_check_result["errorInfo"],
            )

        # モデルオブジェクト作成
        transaction_multi_create_batch_model = transactionMultiCreateBatchModelClass(trace_logger)
        # main関数実行
        await transaction_multi_create_batch_model.main(request_body)

        # 31.終了処理
        # 31-01. 正常終了をCloudWatchへログ出力する
        out_logger.info(logUtil.message_build(MessageConstClass.OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP, json.dumps({})))
        # 31-02. 処理を終了する

    # 例外処理(PDSException)
    except PDSException:
        pass

    # 例外処理
    except Exception as e:
        trace_logger.error(logUtil.message_build(MessageConstClass.ERRORS["999999"]["logMessage"], str(e), traceback.format_exc()))
