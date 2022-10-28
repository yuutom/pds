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
from util.commonUtil import CommonUtilClass

# 自作クラス
## 業務ロジッククラス
from models.closed.pdsUserSearchModel import pdsUserSearchModelClass
## utilクラス
from util import checkUtil
from util.tokenUtil import TokenUtilClass
import util.logUtil as logUtil
## 固定値クラス
from const.messageConst import MessageConstClass
from const.systemConst import SystemConstClass
## 共通パラメータチェッククラス
from util.commonParamCheck import checkTimeStamp
from util.commonParamCheck import checkAccessToken

# Bearerトークン設定
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="bearerToken")

# 処理名
EXEC_NAME: str = "pdsUserSearch"
EXEC_NAME_JP: str = "PDSユーザ検索・参照"

# ルータ作成
router = APIRouter()


class requestBody(BaseModel):
    """
    リクエストボディクラス

    Args:
        BaseModel (Object): Pydanticのベースクラス
    """
    pdsUser: Optional[Any] = None
    fromDate: Optional[Any] = None
    toDate: Optional[Any] = None
    pdsUserStatus: Optional[Any] = None


def input_check(trace_logger: Logger, request_body: requestBody, access_token, time_stamp):
    """
    パラメータ検証処理

    Args:
        trace_logger (Logger): ロガー（TRACE）
        request_body (requestBody): リクエストボディ
        access_token(string): アクセストークン
        time_stamp (string): タイムスタンプ

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
        # 01-02-01.「引数．リクエストボディ．PDSユーザ検索テキスト」の型が文字列型ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_type(request_body.pdsUser, str):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "PDSユーザ検索テキスト", "文字列"))
            error_info_list.append(
                {
                    "errorCode": "020019",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "PDSユーザ検索テキスト", "文字列")
                }
            )

        # 01-02-02.「引数．リクエストボディ．PDSユーザ検索テキスト」の値の桁数が64桁を超過する場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_max_length(request_body.pdsUser, 64):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020002"]["logMessage"], "PDSユーザ検索テキスト", "64"))
            error_info_list.append(
                {
                    "errorCode": "020002",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020002"]["message"], "PDSユーザ検索テキスト", "64")
                }
            )

        # 01-02-03.「引数．リクエストボディ．PDSユーザ公開鍵有効期限From」の値が入っている、かつ、
        #           PDSユーザ公開鍵有効期限Fromの値の桁数が10桁以外の場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_length(request_body.fromDate, 10):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020014"]["logMessage"], "PDSユーザ公開鍵有効期限From", "10"))
            error_info_list.append(
                {
                    "errorCode": "020014",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020014"]["message"], "PDSユーザ公開鍵有効期限From", "10")
                }
            )

        # 01-02-04.「引数．リクエストボディ．PDSユーザ公開鍵有効期限From」の値が入力規則に違反している場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_date(request_body.fromDate):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020003"]["logMessage"], "PDSユーザ公開鍵有効期限From"))
            error_info_list.append(
                {
                    "errorCode": "020003",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "PDSユーザ公開鍵有効期限From")
                }
            )

        # 01-02-05.「引数．リクエストボディ．PDSユーザ公開鍵有効期限To」の値が入っている、かつ、
        #           PDSユーザ公開鍵有効期限Toの値の桁数が10桁以外の場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_length(request_body.toDate, 10):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020014"]["logMessage"], "PDSユーザ公開鍵有効期限To", "10"))
            error_info_list.append(
                {
                    "errorCode": "020014",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020014"]["message"], "PDSユーザ公開鍵有効期限To", "10")
                }
            )

        # 01-02-06.「引数．リクエストボディ．PDSユーザ公開鍵有効期限To」の値が入力規則に違反している場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_date(request_body.toDate):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020003"]["logMessage"], "PDSユーザ公開鍵有効期限To"))
            error_info_list.append(
                {
                    "errorCode": "020003",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "PDSユーザ公開鍵有効期限To")
                }
            )

        # 01-02-07.「引数．リクエストボディ．PDSユーザ公開鍵有効状態」の型が論理型ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_type(request_body.pdsUserStatus, bool):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "PDSユーザ公開鍵有効状態", "論理"))
            error_info_list.append(
                {
                    "errorCode": "020019",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "PDSユーザ公開鍵有効状態", "論理")
                }
            )

        # 01-03.相関チェック処理
        # 01-03-01.「引数．リクエストボディ．検索日From」と「引数．リクエストボディ．検索日To」に値が設定されており、
        #          「引数．リクエストボディ．検索日From」が「引数．リクエストボディ．検索日To」の値を超過している場合、
        #          「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.correlation_check_date(request_body.fromDate, request_body.toDate):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["030006"]["logMessage"]))
            error_info_list.append(
                {
                    "errorCode": "030006",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["030006"]["message"])
                }
            )
        # 02. 終了処理
        # 02-01.レスポンス情報を作成し、返却する
        # 02-01-01.「変数．エラー情報リスト」に値が設定されていない場合、下記のレスポンス情報を返却する
        if len(error_info_list) == 0:
            return {
                "result": True
            }
        # 02-01-02.「変数．エラー情報リスト」に値が設定されている場合、下記のレスポンス情報を返却する
        else:
            return {
                "result": False,
                "errorInfo": error_info_list
            }

    # 例外処理(PDSException)
    except PDSException as e:
        # PDSExceptionオブジェクトをエラーとしてスローする
        raise e

    except Exception as e:
        # エラー情報をCloudWatchへログ出力する
        trace_logger.error(logUtil.message_build(MessageConstClass.ERRORS["999999"]["logMessage"], str(e), traceback.format_exc()))
        # 下記のパラメータでPDSExceptionオブジェクトを作成する
        # PDSExceptionオブジェクトをエラーとしてスローする
        raise PDSException(
            {
                "errorCode": "999999",
                "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
            }
        )


# PDSユーザ検索・参照API
@router.post("/api/2.0/pdsuser/search")
async def pds_user_search(
        request: Request,
        request_body: Optional[requestBody],
        accessToken: Optional[str] = Header(""),
        timeStamp: Optional[str] = Header(""),
        jwt: str = Depends(oauth2_scheme)
):
    """
    PDSユーザ検索・参照API

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
        # 共通クラスオブジェクト作成
        common_util = CommonUtilClass(trace_logger)

        # 01.アクセストークン検証処理
        token_util = TokenUtilClass(trace_logger)
        # 01-01.以下の引数でアクセストークン検証処理を実行する
        # 01-02.アクセストークン検証処理からのレスポンスを、「変数．アクセストークン検証処理実行結果」に格納する
        token_verify_response = token_util.verify_token_closed(accessToken, jwt)
        # 02.共通エラーチェック処理
        # 02-01.以下の引数で共通エラーチェック処理を実行する
        # 02-02.例外が発生した場合、例外処理に遷移
        if token_verify_response.get("errorInfo"):
            common_util.common_error_check(token_verify_response["errorInfo"])

        # JWTペイロード設定済みロガー再作成作成
        trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, guid, json.dumps(token_verify_response["payload"]), request_body.dict(), request)

        # 03.パラメータ検証処理
        # 03-01.以下の引数でパラメータ検証処理を実行する
        # 03-02.パラメータ検証処理のレスポンスを「変数．パラメータ検証処理実行結果」に格納する
        input_check_result = input_check(trace_logger, request_body, accessToken, timeStamp)

        # 04.共通エラーチェック処理
        # 04-01.以下の引数で共通エラーチェック処理を実行する
        # 04-02.例外が発生した場合、例外処理に遷移
        if input_check_result.get("errorInfo"):
            common_util.common_error_check(input_check_result["errorInfo"])

        # 業務ロジック実施
        serach_pds_user_model = pdsUserSearchModelClass(trace_logger)
        # main関数実行
        main_result = serach_pds_user_model.main(request_body)

        # 09.アクセストークン発行処理
        # 09-01.アクセストークン発行処理を実行する
        # 09-02.アクセストークン発行処理からのレスポンスを、「変数．アクセストークン発行処理実行結果」に格納する
        token_create_response = token_util.create_token_closed(
            {
                "tfOperatorId": token_verify_response["payload"]["tfOperatorId"],
                "tfOperatorName": token_verify_response["payload"]["tfOperatorName"]
            },
            token_verify_response["payload"]["accessToken"]
        )

        # 10.共通エラーチェック処理
        # 10-01.共通エラーチェック処理を実行する
        # 10-02.例外が発生した場合、例外処理に遷移
        if token_create_response.get("errorInfo"):
            CommonUtilClass.common_error_check(token_create_response["errorInfo"])

        # 11.終了処理
        # 11-01.正常終了をCloudWatchへログ出力する
        # 11-02.レスポンス情報整形処理
        # 11-02-01.以下をレスポンスとして返却する
        # 11-03.処理を終了する
        response_content = {
            "status": "OK",
            "accessToken": token_create_response["accessToken"],
            "pdsUserInfo": main_result["pdsUserInfo"]
        }
        out_logger.info(logUtil.message_build(MessageConstClass.OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP, json.dumps(response_content)))
        response = JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response_content
        )
        response.headers["Authorization"] = "Bearer " + token_create_response["jwt"]

    # 例外処理(PDSException)
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
        # エラー情報をCloudWatchへログ出力する
        trace_logger.error(logUtil.message_build(MessageConstClass.ERRORS["999999"]["logMessage"], str(e), traceback.format_exc()))
        # 以下をレスポンスとして返却する
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
