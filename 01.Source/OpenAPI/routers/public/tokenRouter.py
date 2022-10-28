from typing import Optional, Any
import traceback
import json
# FastApi
from fastapi import APIRouter, status, Header, Request
from fastapi.responses import JSONResponse
# Security
# RequestBody
from pydantic import BaseModel
# Logger
from logging import Logger

# 自作クラス
## 業務ロジッククラス
from models.public.tokenModel import tokenModelClass

## コールバック関数
from util.callbackExecutorUtil import CallbackExecutor
## Exception
from exceptionClass.PDSException import PDSException

## utilクラス
from util import checkUtil
import util.logUtil as logUtil
from util.commonUtil import CommonUtilClass
import util.commonUtil as commonUtil
from util.tokenUtil import TokenUtilClass

## 固定値クラス
from const.messageConst import MessageConstClass
from const.apitypeConst import apitypeConstClass
from const.systemConst import SystemConstClass
## 共通パラメータ検証クラス
from util.commonParamCheck import checkPdsUserDomainName
from util.commonParamCheck import checkPdsUserId
from util.commonParamCheck import checkTimeStamp


# 処理名
EXEC_NAME: str = "token"
EXEC_NAME_JP: str = "アクセストークン発行"

# ルータ作成
router = APIRouter()


class requestBody(BaseModel):
    """
    リクエストボディクラス

    Args:
        BaseModel (Object): Pydanticのベースクラス
    """
    code1: Optional[Any] = None
    code2: Optional[Any] = None


def input_check(
    trace_logger: Logger,
    pds_user_domain_name: str,
    request_body: requestBody,
    pds_user_id: str,
    time_stamp: str,
    pds_user_domain_check_result: dict
):
    """
    パラメータ検証処理

    Args:
        trace_logger (Logger): ロガー(TRACE)
        pds_user_domain_name (str): PDSユーザドメイン名（パスパラメータ）
        request_body (requestBody): リクエストボディ
        pds_user_id (str): PDSユーザID（ヘッダパラメータ）
        time_stamp (str): タイムスタンプ（ヘッダパラメータ）
        pds_user_domain_check_result (dict): PDSユーザドメイン情報

    Returns:
        dict: パラメータ検証処理結果
    """
    error_info_list = []
    try:
        # 01.パラメータ検証処理（入力チェック）
        # 01-01.パスパラメータ 検証処理
        # 01-01-01.PDSユーザドメイン名検証処理
        # 01-01-01-01.以下の引数でPDSユーザドメイン名検証処理を実行する
        check_pds_user_domain_name_result = checkPdsUserDomainName.CheckPdsUserDomainName(trace_logger, pds_user_domain_name).get_result()
        # 01-01-01-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not check_pds_user_domain_name_result["result"]:
            [error_info_list.append(error_info) for error_info in check_pds_user_domain_name_result["errorInfo"]]

        # 01-02.ヘッダパラメータ検証処理
        # 01-02-01.PDSユーザID検証処理
        # 01-02-01-01.以下の引数でPDSユーザID検証処理を実行する
        check_pds_user_id_result = checkPdsUserId.CheckPdsUserId(trace_logger, pds_user_id).get_result()
        # 01-02-01-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not check_pds_user_id_result["result"]:
            [error_info_list.append(error_info) for error_info in check_pds_user_id_result["errorInfo"]]

        # 01-02-02.タイムスタンプ検証処理
        # 01-02-02-01.以下の引数でタイムスタンプ検証処理を実行する
        check_time_stamp_result = checkTimeStamp.CheckTimeStamp(trace_logger, time_stamp).get_result()
        # 01-02-02-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not check_time_stamp_result["result"]:
            [error_info_list.append(error_info) for error_info in check_time_stamp_result["errorInfo"]]

        # 01-03.リクエストボディ 検証処理
        # 01-03-01.「引数．暗号化文字列1」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_require(request_body.code1):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "暗号化文字列1"))
            error_info_list.append(
                {
                    "errorCode": "020001",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "暗号化文字列1")
                }
            )
        # 01-03-02.「引数．暗号化文字列1」に値が設定されており、型が文字列型ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_type(request_body.code1, str):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "暗号化文字列1", "文字列"))
            error_info_list.append(
                {
                    "errorCode": "020019",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "暗号化文字列1", "文字列")
                }
            )
        # 01-03-03.「引数．暗号化文字列1」に値が設定されており、値の桁数が684桁未満の場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_min_length(request_body.code1, 684):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020016"]["logMessage"], "暗号化文字列1", "684"))
            error_info_list.append(
                {
                    "errorCode": "020016",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020016"]["message"], "暗号化文字列1", "684")
                }
            )
        # 01-03-04.「引数．暗号化文字列1」に値が設定されており、値の桁数が2052桁を超過する場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_max_length(request_body.code1, 2052):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020002"]["logMessage"], "暗号化文字列1", "2052"))
            error_info_list.append(
                {
                    "errorCode": "020002",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020002"]["message"], "暗号化文字列1", "2052")
                }
            )
        # 01-03-05.「引数．暗号化文字列1」に値が設定されており、値に入力可能文字以外が含まれている場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_enterable_characters_code(request_body.code1):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020020"]["logMessage"], "暗号化文字列1"))
            error_info_list.append(
                {
                    "errorCode": "020020",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020020"]["message"], "暗号化文字列1")
                }
            )
        # 01-03-06.「引数．暗号化文字列2」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_require(request_body.code2):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "暗号化文字列2"))
            error_info_list.append(
                {
                    "errorCode": "020001",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "暗号化文字列2")
                }
            )
        # 01-03-07.「引数．暗号化文字列2」に値が設定されており、型が文字列型ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_type(request_body.code2, str):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "暗号化文字列2", "文字列"))
            error_info_list.append(
                {
                    "errorCode": "020019",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "暗号化文字列2", "文字列")
                }
            )
        # 01-03-08.「引数．暗号化文字列2」に値が設定されており、値の桁数が684桁未満の場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_min_length(request_body.code2, 684):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020016"]["logMessage"], "暗号化文字列2", "684"))
            error_info_list.append(
                {
                    "errorCode": "020016",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020016"]["message"], "暗号化文字列2", "684")
                }
            )
        # 01-03-09.「引数．暗号化文字列2」に値が設定されており、値の桁数が2052桁を超過する場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_max_length(request_body.code2, 2052):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020002"]["logMessage"], "暗号化文字列2", "2052"))
            error_info_list.append(
                {
                    "errorCode": "020002",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020002"]["message"], "暗号化文字列2", "2052")
                }
            )
        # 01-03-10.「引数．暗号化文字列2」に値が設定されており、値に入力可能文字以外が含まれている場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_enterable_characters_code(request_body.code2):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020020"]["logMessage"], "暗号化文字列2"))
            error_info_list.append(
                {
                    "errorCode": "020020",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020020"]["message"], "暗号化文字列2")
                }
            )
        # 01-04.相関チェック処理
        # 01-04-01.「引数．ヘッダパラメータ．PDSユーザID」と「引数．PDSユーザドメイン情報．PDSユーザID」の値が一致しない場合、「変数．エラー情報リスト」にエラー情報を追加する
        if pds_user_id != pds_user_domain_check_result["pdsUserInfo"]["pdsUserId"]:
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["010002"]["logMessage"]))
            error_info_list.append(
                {
                    "errorCode": "010002",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["010002"]["message"])
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


@router.post("/api/2.0/{pdsUserDomainName}/token")
async def generate_token(
    request: Request,
    pdsUserDomainName,
    request_body: Optional[requestBody],
    pdsUserId: Optional[str] = Header(""),
    timeStamp: Optional[str] = Header("")
):
    """
    メイン処理

    Args:
        request (object): リクエスト情報
        pdsUserDomainName (str): PDSユーザドメイン名
        request_body (object): リクエストボディ
        pdsUserId (str): PDSユーザID
        timeStamp (str): タイムスタンプ

    Returns:
        dict: レスポンス
    """
    # ロガー作成
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", request_body.dict(), request)
    try:
        in_logger.info(logUtil.message_build(MessageConstClass.IN_LOG["000000"]["logMessage"], EXEC_NAME_JP))
        # 01.PDSユーザドメイン検証処理実行
        common_util = CommonUtilClass(trace_logger)
        # 01-01.以下の引数でPDSユーザドメイン検証処理実行
        # 01-02.PDSユーザドメイン検証処理からのレスポンスを、「変数．PDSユーザドメイン検証処理実行結果」に格納する
        pds_user_domain_check_result = common_util.check_pds_user_domain(
            pdsUserDomainName,
            pdsUserId
        )

        # 02.共通エラーチェック処理
        # 02-01.以下の引数で共通エラーチェック処理を実行する
        # 02-02.例外が発生した場合、例外処理に遷移
        if pds_user_domain_check_result.get("errorInfo"):
            # API実行履歴登録処理
            api_history_insert = CallbackExecutor(
                common_util.insert_api_history,
                commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                None,
                apitypeConstClass.API_TYPE["ACCESS_TOKEN_ISSUE"],
                pdsUserDomainName,
                str(request.url),
                json.dumps({"path_param": request.path_params, "query_param": request.query_params._dict, "header_param": commonUtil.make_headerParam(request.headers), "request_body": request_body.dict()}),
                False,
                None,
                commonUtil.get_str_datetime()
            )
            common_util.common_error_check(
                pds_user_domain_check_result["errorInfo"],
                api_history_insert
            )

        # 03.パラメータ検証処理
        # 03-01.以下の引数でパラメータ検証処理を実行する
        # 03-02.パラメータ検証処理のレスポンスを「変数．パラメータ検証処理実行結果」に格納する
        input_check_result = input_check(trace_logger, pdsUserDomainName, request_body, pdsUserId, timeStamp, pds_user_domain_check_result)

        # 04.共通エラーチェック処理
        # 04-01.以下の引数で共通エラーチェック処理を実行する
        # 04-02.例外が発生した場合、例外処理に遷移
        if input_check_result.get("errorInfo"):
            # API実行履歴登録処理
            api_history_insert = CallbackExecutor(
                common_util.insert_api_history,
                commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                pds_user_domain_check_result["pdsUserInfo"]["pdsUserId"],
                apitypeConstClass.API_TYPE["ACCESS_TOKEN_ISSUE"],
                pdsUserDomainName,
                str(request.url),
                json.dumps({"path_param": request.path_params, "query_param": request.query_params._dict, "header_param": commonUtil.make_headerParam(request.headers), "request_body": request_body.dict()}),
                False,
                None,
                commonUtil.get_str_datetime()
            )
            common_util.common_error_check(
                input_check_result["errorInfo"],
                api_history_insert
            )

        # トークン発行処理
        token_model = tokenModelClass(trace_logger, request, pds_user_domain_check_result["pdsUserInfo"], pdsUserDomainName, timeStamp)
        token_model.main(request_body)

        # 16.アクセストークン発行処理
        # 16-01.以下の引数でアクセストークン発行処理を実行する
        # 16-02.アクセストークン発行処理のレスポンスを「変数．アクセストークン発行処理結果」に格納する
        token_util = TokenUtilClass(trace_logger)
        token_create_response = token_util.create_token_public(
            pds_user_domain_check_result["pdsUserInfo"]["pdsUserId"],
            pds_user_domain_check_result["pdsUserInfo"]["pdsUserName"],
            None
        )

        # 17.共通エラーチェック処理
        # 17-01.以下の引数で共通エラーチェック処理を実行する
        # 17-01.例外が発生した場合、例外処理に遷移
        if token_create_response.get("errorInfo"):
            api_history_insert = CallbackExecutor(
                common_util.insert_api_history,
                commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                pds_user_domain_check_result["pdsUserInfo"]["pdsUserId"],
                apitypeConstClass.API_TYPE["ACCESS_TOKEN_ISSUE"],
                pdsUserDomainName,
                str(request.url),
                json.dumps({"path_param": request.path_params, "query_param": request.query_params._dict, "header_param": commonUtil.make_headerParam(request.headers), "request_body": {}}),
                False,
                None,
                commonUtil.get_str_datetime()
            )
            common_util.common_error_check(
                token_create_response["errorInfo"],
                api_history_insert
            )

        # 18.API実行履歴登録処理
        # 18-01.以下の引数でAPI実行履歴登録処理を実行する
        try:
            insert_api_history_result = common_util.insert_api_history(
                commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                pds_user_domain_check_result["pdsUserInfo"]["pdsUserId"],
                apitypeConstClass.API_TYPE["ACCESS_TOKEN_ISSUE"],
                pdsUserDomainName,
                str(request.url),
                json.dumps({"path_param": request.path_params, "query_param": request.query_params._dict, "header_param": commonUtil.make_headerParam(request.headers), "request_body": request_body.dict()}),
                True,
                None,
                commonUtil.get_str_datetime()
            )
        # 18-02.処理に失敗した場合、以下の引数でAPI実行履歴登録処理を実行する
        # 18-03.API実行履歴登録処理のレスポンスを「変数．API実行履歴登録処理結果」に格納する
        except Exception:
            insert_api_history_result = common_util.insert_api_history(
                commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                pds_user_domain_check_result["pdsUserInfo"]["pdsUserId"],
                apitypeConstClass.API_TYPE["ACCESS_TOKEN_ISSUE"],
                pdsUserDomainName,
                str(request.url),
                json.dumps({"path_param": request.path_params, "query_param": request.query_params._dict, "header_param": commonUtil.make_headerParam(request.headers), "request_body": request_body.dict()}),
                False,
                None,
                commonUtil.get_str_datetime()
            )

        # 19.共通エラーチェック処理
        # 19-01.以下の引数で共通エラーチェック処理を実行する
        # 19-02.例外が発生した場合、例外処理に遷移
        if insert_api_history_result.get("errorInfo"):
            common_util.common_error_check(insert_api_history_result["errorInfo"])

        # 20.終了処理
        # 20-01.返却パラメータを作成し返却する
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

    # 例外処理
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
