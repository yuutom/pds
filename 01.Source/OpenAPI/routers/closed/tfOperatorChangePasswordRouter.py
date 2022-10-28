import json
from typing import Any, Optional
import traceback
# FastApi
from fastapi import APIRouter, Depends, status, Header, Request
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
from models.closed.tfOperatorChangePasswordModel import tfOperatorChangePasswordClass
## utilクラス
from util import checkUtil
from util.tokenUtil import TokenUtilClass
from util.commonUtil import CommonUtilClass
import util.logUtil as logUtil
## 固定値クラス
from const.messageConst import MessageConstClass
from const.systemConst import SystemConstClass
## 共通パラメータチェッククラス
from util.commonParamCheck import checkTimeStamp
from util.commonParamCheck import checkAccessToken
from util.commonParamCheck import checkTfOperatorPassword


# Bearerトークン設定
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="bearerToken")

# 処理名
EXEC_NAME: str = "tfOperatorChangePassword"
EXEC_NAME_JP: str = "TFオペレータパスワード変更"

# ルータ作成
router = APIRouter()


class requestBody(BaseModel):
    """
    リクエストボディクラス

    Args:
        BaseModel (Object): Pydanticのベースクラス
    """
    tfOperatorPassword: Optional[Any] = None
    tfOperatorConfirmPassword: Optional[Any] = None


def input_check(trace_logger: Logger, request_body: requestBody, access_token, time_stamp, verify_result: dict):
    """
    パラメータ検証処理

    Args:
        trace_logger (Logger): ロガー（TRACE）
        request_body (requestBody): リクエストボディ
        access_token (_type_): アクセストークン
        time_stamp (_type_): タイムスタンプ
        verify_result (dict): アクセストークン検証処理結果

    Returns:
        dict: パラメータ検証処理結果
    """
    error_info_list = []
    try:
        # 01.パラメータ検証処理（入力チェック）
        # 01-01. ヘッダパラメータ検証処理
        # 01-01-01.タイムスタンプ検証処理
        # 01-01-01-01.以下の引数でタイムスタンプ検証処理を実行する
        check_time_stamp_result = checkTimeStamp.CheckTimeStamp(trace_logger, time_stamp).get_result()
        # 01-01-01-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not check_time_stamp_result["result"]:
            [error_info_list.append(error_info) for error_info in check_time_stamp_result["errorInfo"]]

        # 01-01-02.アクセストークン検証処理
        # 01-01-02-01.以下の引数でアクセストークン検証処理を実行する
        check_access_token_result = checkAccessToken.CheckAccessToken(trace_logger, access_token).get_result()
        # 01-01-02-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not check_access_token_result["result"]:
            [error_info_list.append(error_info) for error_info in check_access_token_result["errorInfo"]]

        # 01-02	リクエストボディ 検証処理
        # 01-02-01.TFオペレータパスワード検証処理
        # 01-02-01-01.以下の引数でTFオペレータパスワード検証処理を実行する
        check_tf_operator_password_result = checkTfOperatorPassword.CheckTfOperatorPassword(trace_logger, request_body.tfOperatorPassword).get_result()
        # 01-02-01-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not check_tf_operator_password_result["result"]:
            [error_info_list.append(error_info) for error_info in check_tf_operator_password_result["errorInfo"]]

        # 01-02-02 「引数．リクエストボディ．TFオペレータパスワード(確認用)」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_require(request_body.tfOperatorConfirmPassword):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "TFオペレータパスワード(確認用)"))
            error_info_list.append(
                {
                    "errorCode": "020001",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "TFオペレータパスワード(確認用)")
                }
            )

        # 01-02-03 「引数．リクエストボディ．TFオペレータパスワード(確認用)」に値が設定されており、型が文字列型ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_type(request_body.tfOperatorConfirmPassword, str):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "TFオペレータパスワード(確認用)", "文字列"))
            error_info_list.append(
                {
                    "errorCode": "020019",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "TFオペレータパスワード(確認用)", "文字列")
                }
            )

        # 01-02-04 「引数．リクエストボディ．TFオペレータパスワード(確認用)」に値が設定されており、値の桁数が8桁未満の場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_min_length(request_body.tfOperatorConfirmPassword, 8):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020016"]["logMessage"], "TFオペレータパスワード(確認用)", "8"))
            error_info_list.append(
                {
                    "errorCode": "020016",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020016"]["message"], "TFオペレータパスワード(確認用)", "8")
                }
            )

        # 01-02-05 「引数．リクエストボディ．TFオペレータパスワード(確認用)」に値が設定されており、値の桁数が617桁を超過する場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_max_length(request_body.tfOperatorConfirmPassword, 617):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020002"]["logMessage"], "TFオペレータパスワード(確認用)", "617"))
            error_info_list.append(
                {
                    "errorCode": "020002",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020002"]["message"], "TFオペレータパスワード(確認用)", "617")
                }
            )

        # 01-02-06 「引数．リクエストボディ．TFオペレータパスワード(確認用)」に値が設定されており、値に入力可能文字以外が含まれている場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_tf_operator_password(request_body.tfOperatorConfirmPassword):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020020"]["logMessage"], "TFオペレータパスワード(確認用)"))
            error_info_list.append(
                {
                    "errorCode": "020020",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020020"]["message"], "TFオペレータパスワード(確認用)")
                }
            )

        # 01-02-07 「引数．リクエストボディ．TFオペレータパスワード(確認用)」に値が設定されており、値が英大文字、英小文字、数字、記号を含んでいない場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_number_of_character_types(request_body.tfOperatorConfirmPassword):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020010"]["logMessage"], "TFオペレータパスワード(確認用)"))
            error_info_list.append(
                {
                    "errorCode": "020010",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020010"]["message"], "TFオペレータパスワード(確認用)")
                }
            )

        # 01-03.相関チェック
        # 01-03-01.「引数．リクエストボディ．TFオペレータパスワード」の値が「引数．リクエストボディ．TFオペレータパスワード(確認用)」と一致しない場合、「変数．エラー情報リスト」にエラー情報を追加する
        if request_body.tfOperatorPassword != request_body.tfOperatorConfirmPassword:
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["030007"]["logMessage"], "TFオペレータパスワード"))
            error_info_list.append(
                {
                    "errorCode": "030007",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["030007"]["message"], "TFオペレータパスワード")
                }
            )

        # 01-03-02.「引数．リクエストボディ．TFオペレータパスワード」の値が「引数．アクセストークン検証処理結果．ペイロード．TFオペレータID」と同一の場合、「変数．エラー情報リスト」にエラー情報を追加する
        if request_body.tfOperatorPassword == verify_result["payload"]["tfOperatorId"]:
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["030012"]["logMessage"]))
            error_info_list.append(
                {
                    "errorCode": "030012",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["030012"]["message"])
                }
            )

        # 01-03-03.「引数．リクエストボディ．TFオペレータパスワード(確認用)」の値が「引数．アクセストークン検証処理結果．ペイロード．TFオペレータID」と同一の場合、「変数．エラー情報リスト」にエラー情報を追加する
        if request_body.tfOperatorConfirmPassword == verify_result["payload"]["tfOperatorId"]:
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["030012"]["logMessage"]))
            error_info_list.append(
                {
                    "errorCode": "030012",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["030012"]["message"])
                }
            )

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


# TFオペレータパスワード変更API
@router.post("/api/2.0/tfoperator/changepassword")
async def tf_operator_change_password(
        request: Request,
        request_body: Optional[requestBody],
        accessToken: Optional[str] = Header(""),
        timeStamp: Optional[str] = Header(""),
        jwt: str = Depends(oauth2_scheme)
):
    """
    TFオペレータパスワード変更API
    tfOperatorChangePasswordRouter
    Args:
        request (Request): リクエストオブジェクト
        request_body (Optional[requestBody]): リクエストボディ
        access_token (Optional[str], optional): アクセストークン. Defaults to Header("").
        time_stamp (Optional[str], optional): タイムスタンプ. Defaults to Header("").
        jwt (str, optional): JWT. Defaults to Depends(oauth2_scheme).

    Returns:
        JSONResponse: 処理結果
    """
    # ロガー作成
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", request_body.dict(), request)
    try:
        in_logger.info(logUtil.message_build(MessageConstClass.IN_LOG["000000"]["logMessage"], EXEC_NAME_JP))
        # 01. アクセストークン検証処理
        token_util = TokenUtilClass(trace_logger)
        # 01-01 以下の引数でアクセストークン検証処理を実行する
        # 01-02 アクセストークン検証処理からのレスポンスを、変数．アクセストークン検証処理実行結果に格納する
        token_verify_response = token_util.verify_token_closed(accessToken, jwt)

        common_util = CommonUtilClass(trace_logger)
        # 02.共通エラーチェック処理
        # 02-01.以下の引数で共通エラーチェック処理を実行する
        # 02-02.例外が発生した場合、例外処理に遷移
        if token_verify_response.get("errorInfo"):
            common_util.common_error_check(token_verify_response["errorInfo"])

        # JWTペイロード設定済みロガー再作成作成
        trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, guid, json.dumps(token_verify_response["payload"]), request_body.dict(), request)

        # 03.パラメータ検証処理
        input_check_result = input_check(trace_logger, request_body, accessToken, timeStamp, token_verify_response)
        # 04.共通エラーチェック処理
        # 04-01.以下の引数で共通エラーチェック処理を実行する
        # 04-02.例外が発生した場合、例外処理に遷移
        if input_check_result.get("errorInfo"):
            common_util.common_error_check(input_check_result["errorInfo"])

        # TFオペレータパスワード変更処理
        tf_operator_change_password_model = tfOperatorChangePasswordClass(trace_logger)
        tf_operator_change_password_model.main(request_body, token_verify_response["payload"]["tfOperatorId"])

        # 15.アクセストークン発行処理
        # 15-01.以下の引数でアクセストークン発行処理を実行する
        # 15-02.アクセストークン発行処理からのレスポンスを、「変数．アクセストークン発行処理実行結果」に格納する
        token_create_response = token_util.create_token_closed(
            {
                "tfOperatorId": token_verify_response["payload"]["tfOperatorId"],
                "tfOperatorName": token_verify_response["payload"]["tfOperatorName"]
            },
            token_verify_response["payload"]["accessToken"]
        )

        # 16.共通エラー処理
        # 16-01.以下の引数で共通エラーチェック処理を実行する
        # 16-02.例外が発生した場合、例外処理に遷移
        if token_create_response.get("errorInfo"):
            common_util.common_error_check(token_create_response["errorInfo"])

        # 17.終了処理
        # 17-01.正常終了をCloudWatchへログ出力する
        # 17-02.レスポンス情報整形処理
        # 17-03.処理を終了する
        response_content = {
            "status": "OK",
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
