from typing import Optional, Any
import traceback
import json
# FastApi
from fastapi import APIRouter, status, Header, Request
from fastapi.responses import JSONResponse
# Security
from fastapi.security import OAuth2PasswordBearer
# RequestBody
from pydantic import BaseModel
# Logger
from logging import Logger
from exceptionClass.PDSException import PDSException

# 自作クラス
## 業務ロジッククラス
from models.closed.tfOperatorLoginModel import tfOperatorLoginClass
## utilクラス
from util.tokenUtil import TokenUtilClass
from util.commonUtil import CommonUtilClass
import util.logUtil as logUtil
## 固定値クラス
from const.messageConst import MessageConstClass
from const.systemConst import SystemConstClass
## 共通パラメータチェッククラス
from util.commonParamCheck import checkTimeStamp
from util.commonParamCheck import checkTfOperatorId
from util.commonParamCheck import checkTfOperatorPassword

# Bearerトークン設定
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="bearerToken")

# 処理名
EXEC_NAME: str = "tfOperatorLogin"
EXEC_NAME_JP: str = "TFオペレータログイン"

# ルータ作成
router = APIRouter()


# 検索用 水野担当ファイル(完了)
class requestBody(BaseModel):
    """
    リクエストボディクラス

    Args:
        BaseModel (Object): Pydanticのベースクラス
    """
    tfOperatorId: Optional[Any] = None
    tfOperatorPassword: Optional[Any] = None


def input_check(trace_logger: Logger, time_stamp, request_body: requestBody):
    """
    パラメータ検証処理

    Args:
        trace_logger (Logger): ロガー（TRACE）
        time_stamp (_type_): タイムスタンプ
        request_body (requestBody): リクエストボディ

    Returns:
        dict: パラメータ検証処理結果
    """
    error_info_list = []
    try:
        # 01.パラメータ検証処理（入力チェック）
        # 01-01.ヘッダパラメータ検証処理
        # 01-01-01.タイムスタンプ検証処理
        # 01-01-01-01.以下の引数でタイムスタンプ検証処理を実行する
        check_time_stamp_result = checkTimeStamp.CheckTimeStamp(trace_logger, time_stamp).get_result()
        # 01-01-01-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not check_time_stamp_result["result"]:
            [error_info_list.append(error_info) for error_info in check_time_stamp_result["errorInfo"]]

        # 01-02.リクエストボディ検証処理
        # 01-02-01.TFオペレータID検証処理
        # 01-02-01-01.以下の引数でTFオペレータID検証処理を実行する
        check_tf_operator_id_result = checkTfOperatorId.CheckTfOperatorId(trace_logger, request_body.tfOperatorId).get_result()
        # 01-02-01-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not check_tf_operator_id_result["result"]:
            [error_info_list.append(error_info) for error_info in check_tf_operator_id_result["errorInfo"]]

        # 01-02-02.TFオペレータパスワード検証処理
        # 01-02-02-01.以下の引数でTFオペレータパスワード検証処理を実行する
        check_tf_operator_password_result = checkTfOperatorPassword.CheckTfOperatorPassword(trace_logger, request_body.tfOperatorPassword).get_result()
        # 01-02-02-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not check_tf_operator_password_result["result"]:
            [error_info_list.append(error_info) for error_info in check_tf_operator_password_result["errorInfo"]]

        # 02. 終了処理
        # 02-01.レスポンス情報を作成し、返却する
        # 02-01-01.「変数．エラー情報リスト」に値が設定されていない場合、下記のレスポンス情報を返却する
        if len(error_info_list) == 0:
            return {
                "result": True
            }
        # 02-01-02.「変数．エラー情報リスト」に値が設定されている場合
        # 02-01-02-01.レスポンス用のエラー情報リストを作成する
        # 02-01-02-02.レスポンス情報を返却する
        else:
            return {
                "result": False,
                "errorInfo": {
                    "errorCode": "010006",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["010006"]["message"])
                }
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


@router.post("/api/2.0/tfoperator/login")
async def tf_operator_login(
    request: Request,
    request_body: Optional[requestBody],
    timeStamp: Optional[str] = Header("")
):
    """
    TFオペレータログインAPI

    Args:
        request (Request): リクエストオブジェクト
        request_body (Optional[requestBody]): リクエストボディ
        time_stamp (Optional[str], optional): タイムスタンプ. Defaults to Header("").

    Returns:
        JSONResponse: 処理結果
    """
    # ロガー作成
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", request_body.dict(), request)
    try:
        in_logger.info(logUtil.message_build(MessageConstClass.IN_LOG["000000"]["logMessage"], EXEC_NAME_JP))
        # 共通クラスオブジェクト作成
        common_util = CommonUtilClass(trace_logger)

        # トークンクラスオブジェクト作成
        token_util = TokenUtilClass(trace_logger)

        # 01.パラメータ検証処理
        # 01-01.以下の引数でパラメータ検証処理を実行する
        # 01-02.パラメータ検証処理のレスポンスを「変数．パラメータ検証処理実行結果」に格納する
        input_check_result = input_check(trace_logger, timeStamp, request_body)

        # 02.共通エラーチェック処理
        # 02-01.共通エラーチェック処理を実行する
        # 02-02.例外が発生した場合、例外処理に遷移
        if input_check_result.get("errorInfo"):
            common_util.common_error_check(input_check_result["errorInfo"])

        # モデルオブジェクト作成
        tf_operator_login_model = tfOperatorLoginClass(trace_logger)

        # main関数実行
        main_result = tf_operator_login_model.main(request_body)

        # 07.アクセストークン発行処理
        # 07-01.アクセストークン発行処理を実行する
        # 07-02.アクセストークン発行処理からのレスポンスを、「変数．アクセストークン発行処理実行結果」に格納する
        token_create_response = token_util.create_token_closed(
            {
                "tfOperatorId": request_body.tfOperatorId,
                "tfOperatorName": main_result["tfOperatorInfo"][0]
            },
            None
        )

        # 08.共通エラーチェック処理
        # 08-01.共通エラーチェック処理を実行する
        # 08-02.例外が発生した場合、例外処理に遷移
        if token_create_response.get("errorInfo"):
            common_util.common_error_check(token_create_response["errorInfo"])

        # 09.終了処理
        # 09-01.正常終了をCloudWatchへログ出力する
        # 09-02.レスポンス情報整形処理
        # 09-03.処理を終了する
        response_content = {
            "status": "OK",
            "tfOperatorId": request_body.tfOperatorId,
            "tfOperatorName": main_result["tfOperatorInfo"][0],
            "tfOperatorPasswordResetFlg": main_result["tfOperatorInfo"][1],
            "accessToken": token_create_response["accessToken"]
        }
        out_logger.info(logUtil.message_build(MessageConstClass.OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP, json.dumps(response_content)))
        response = JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response_content
        )
        response.headers["Authorization"] = "Bearer " + token_create_response["jwt"]

    # 例外処理（PDSExceptionクラス）
    except PDSException as e:
        response_content = {
            "status": "NG",
            "errorInfo": e.error_info_list
        }
        if e.error_info_list[0]["errorCode"][0:2] == "99":
            response = JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=response_content
            )
        else:
            response = JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=response_content
            )

    # 例外処理
    except Exception as e:
        trace_logger.error(logUtil.message_build(MessageConstClass.ERRORS["999999"]["logMessage"], str(e), traceback.format_exc()))
        response_content = {
            "status": "NG",
            "errorInfo": [
                {
                    "errorCode": "999999",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
                }
            ]
        }

        response = JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=response_content
        )

    return response
