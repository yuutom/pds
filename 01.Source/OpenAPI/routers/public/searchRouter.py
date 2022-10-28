from typing import Any, Optional
import traceback
import json
# FastApi
from fastapi import APIRouter, Depends, status, Header, Request
from fastapi.responses import JSONResponse
# Security
from fastapi.security import OAuth2PasswordBearer
# RequestBody
from pydantic import BaseModel
# Logger
from logging import Logger

# 自作クラス
## 業務ロジッククラス
from models.public.searchModel import searchModelClass

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
from util.commonParamCheck import checkAccessToken
from util.commonParamCheck import checkUserIdMatchMode
from util.commonParamCheck import checkUserIdStr
from util.commonParamCheck import checkDataJsonKey
from util.commonParamCheck import checkDataMatchMode
from util.commonParamCheck import checkDataStr
from util.commonParamCheck import checkImageHash
from util.commonParamCheck import checkFromDate
from util.commonParamCheck import checkToDate


# 処理名
EXEC_NAME: str = "search"
EXEC_NAME_JP: str = "個人情報検索"

# ルータ作成
router = APIRouter()

# Bearerトークン設定
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="bearerToken")


class requestBody(BaseModel):
    """
    リクエストボディクラス

    Args:
        BaseModel (Object): Pydanticのベースクラス
    """
    userIdMatchMode: Optional[Any] = None
    userIdStr: Optional[Any] = None
    dataJson: Optional[Any] = None
    dataMatchMode: Optional[Any] = None
    dataStr: Optional[Any] = None
    imageHash: Optional[Any] = None
    fromDate: Optional[Any] = None
    toDate: Optional[Any] = None


def advance_exec(
    trace_logger: Logger,
    logger_guid: str,
    page_no: int,
    pds_user_domain_name: str,
    request_body: requestBody,
    pds_user_id: str,
    access_token: str,
    time_stamp: str,
    jwt: str,
    request: Request
):
    """
    事前処理

    Args:
        trace_logger (Logger): ロガー(TRACE)
        logger_guid (str): ロガー発行時のGUID
        page_no (int): ページ数（パスパラメータ）
        pds_user_domain_name (str): PDSユーザドメイン名（パスパラメータ）
        request_body (requestBody): リクエストボディ
        pds_user_id (str): PDSユーザID（ヘッダパラメータ）
        access_token (str): アクセストークン（ヘッダパラメータ）
        time_stamp (str): タイムスタンプ（ヘッダパラメータ）
        jwt (str): JWT
        request (Request): リクエスト情報
    """
    try:
        # 01.PDSユーザドメイン検証処理実行
        common_util = CommonUtilClass(trace_logger)
        # 01-01.以下の引数でPDSユーザドメイン検証処理実行
        # 01-02.PDSユーザドメイン検証処理からのレスポンスを、「変数．PDSユーザドメイン検証処理実行結果」に格納する
        pds_user_domain_check_result = common_util.check_pds_user_domain(
            pds_user_domain_name,
            pds_user_id
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
                apitypeConstClass.API_TYPE["SEARCH"],
                pds_user_domain_name,
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

        # 03.アクセストークン検証処理
        token_util = TokenUtilClass(trace_logger)
        # 03-01.以下の引数でアクセストークン検証処理を実行する
        # 03-02.アクセストークン検証処理からのレスポンスを、「変数．アクセストークン検証処理実行結果」に格納する
        token_verify_response = token_util.verify_token_public(access_token, jwt, pds_user_id)

        # 04.共通エラーチェック処理
        # 04-01.以下の引数で共通エラーチェック処理を実行する
        # 04-02.例外が発生した場合、例外処理に遷移
        if token_verify_response.get("errorInfo"):
            # API実行履歴登録処理
            api_history_insert = CallbackExecutor(
                common_util.insert_api_history,
                commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                pds_user_domain_check_result["pdsUserInfo"]["pdsUserId"],
                apitypeConstClass.API_TYPE["SEARCH"],
                pds_user_domain_name,
                str(request.url),
                json.dumps({"path_param": request.path_params, "query_param": request.query_params._dict, "header_param": commonUtil.make_headerParam(request.headers), "request_body": request_body.dict()}),
                False,
                None,
                commonUtil.get_str_datetime()
            )
            common_util.common_error_check(
                token_verify_response["errorInfo"],
                api_history_insert
            )

        # JWTペイロード設定済みロガー再作成作成
        trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, logger_guid, json.dumps(token_verify_response["payload"]), request_body.dict(), request)

        # 05.パラメータ検証処理
        # 05-01.以下の引数でパラメータ検証処理を実行する
        # 05-02.パラメータ検証処理のレスポンスを「変数．パラメータ検証処理実行結果」に格納する
        input_check_result = input_check(trace_logger, page_no, pds_user_domain_name, request_body, pds_user_id, access_token, time_stamp, pds_user_domain_check_result)

        # 06.共通エラーチェック処理
        # 06-01.以下の引数で共通エラーチェック処理を実行する
        # 06-02.例外が発生した場合、例外処理に遷移
        if input_check_result.get("errorInfo"):
            # API実行履歴登録処理
            api_history_insert = CallbackExecutor(
                common_util.insert_api_history,
                commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                pds_user_domain_check_result["pdsUserInfo"]["pdsUserId"],
                apitypeConstClass.API_TYPE["SEARCH"],
                pds_user_domain_name,
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

        # 07.終了処理
        # 07-01.レスポンス情報を作成し、返却する
        return {
            "result": True,
            "pdsUserInfo": pds_user_domain_check_result["pdsUserInfo"],
            "traceLogger": trace_logger,
            "outLogger": out_logger
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


def input_check(
    trace_logger: Logger,
    page_no: str,
    pds_user_domain_name: str,
    request_body: requestBody,
    pds_user_id: str,
    access_token: str,
    time_stamp: str,
    pds_user_domain_check_result: dict
):
    """
    パラメータ検証処理

    Args:
        trace_logger (Logger): ロガー(TRACE)
        page_no (int): ページ数（パスパラメータ）
        pds_user_domain_name (str): PDSユーザドメイン名（パスパラメータ）
        request_body (requestBody): リクエストボディ
        pds_user_id (str): PDSユーザID（ヘッダパラメータ）
        access_token (str): アクセストークン（ヘッダパラメータ）
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

        # 01-01-02.「引数．パスパラメータ．ページNo」に値が設定されており、型が数値型ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_type(page_no, int):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "ページNo", "数値"))
            error_info_list.append(
                {
                    "errorCode": "020019",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "ページNo", "数値")
                }
            )

        # 01-01-03.「引数．パスパラメータ．ページNo」に値が設定されており、値に入力可能文字以外が含まれている場合、、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_number(str(page_no)):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020020"]["logMessage"], "ページNo"))
            error_info_list.append(
                {
                    "errorCode": "020020",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020020"]["message"], "ページNo")
                }
            )

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

        # 01-02-03.アクセストークン検証処理
        # 01-02-03-01.以下の引数でアクセストークン検証処理を実行する
        check_access_token_result = checkAccessToken.CheckAccessToken(trace_logger, access_token).get_result()
        # 01-02-03-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not check_access_token_result["result"]:
            [error_info_list.append(error_info) for error_info in check_access_token_result["errorInfo"]]

        # 01-03.リクエストボディ 検証処理
        # 01-03-01.検索用ユーザID検索モード検証処理
        # 01-03-01-01.以下の引数で検索用ユーザID検索モード検証処理を実行する
        check_user_id_matchmode_result = checkUserIdMatchMode.CheckUserIdMatchMode(trace_logger, request_body.userIdMatchMode).get_result()
        # 01-03-01-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not check_user_id_matchmode_result["result"]:
            [error_info_list.append(error_info) for error_info in check_user_id_matchmode_result["errorInfo"]]

        # 01-03-02.検索用ユーザID検索文字列検証処理
        # 01-03-02-01.以下の引数で検索用ユーザID検索文字列検証処理を実行する
        check_user_id_str_result = checkUserIdStr.CheckUserIdStr(trace_logger, request_body.userIdStr).get_result()
        # 01-03-02-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not check_user_id_str_result["result"]:
            [error_info_list.append(error_info) for error_info in check_user_id_str_result["errorInfo"]]

        # 01-03-03.保存データJsonキー情報検証処理
        # 01-03-03-01.以下の引数で保存データJsonキー情報検証処理を実行する
        check_data_json_result = checkDataJsonKey.CheckDataJsonKey(trace_logger, request_body.dataJson).get_result()
        # 01-03-03-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not check_data_json_result["result"]:
            [error_info_list.append(error_info) for error_info in check_data_json_result["errorInfo"]]

        # 01-03-04.保存データ検索モード検証処理
        # 01-03-04-01.以下の引数で保存データ検索モード検証処理を実行する
        check_data_matchmode_result = checkDataMatchMode.CheckDataMatchMode(trace_logger, request_body.dataMatchMode).get_result()
        # 01-03-04-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not check_data_matchmode_result["result"]:
            [error_info_list.append(error_info) for error_info in check_data_matchmode_result["errorInfo"]]

        # 01-03-05.保存データ検索文字列検証処理
        # 01-03-05-01.以下の引数で保存データ検索文字列検証処理を実行する
        check_data_str_result = checkDataStr.CheckDataStr(trace_logger, request_body.dataStr).get_result()
        # 01-03-05-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not check_data_str_result["result"]:
            [error_info_list.append(error_info) for error_info in check_data_str_result["errorInfo"]]

        # 01-03-06.保存されたバイナリデータのハッシュ値検証処理
        # 01-03-06-01.以下の引数で保存されたバイナリデータのハッシュ値検証処理を実行する
        check_image_hash_result = checkImageHash.CheckImageHash(trace_logger, request_body.imageHash).get_result()
        # 01-03-06-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not check_image_hash_result["result"]:
            [error_info_list.append(error_info) for error_info in check_image_hash_result["errorInfo"]]

        # 01-03-07.検索用日時From検証処理
        # 01-03-07-01.以下の引数で検索用日時From検証処理を実行する
        check_from_date_result = checkFromDate.CheckFromDate(trace_logger, request_body.fromDate).get_result()
        # 01-03-07-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not check_from_date_result["result"]:
            [error_info_list.append(error_info) for error_info in check_from_date_result["errorInfo"]]

        # 01-03-08.検索用日時To検証処理
        # 01-03-08-01.以下の引数で検索用日時To検証処理を実行する
        check_to_date_result = checkToDate.CheckToDate(trace_logger, request_body.toDate).get_result()
        # 01-03-08-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not check_to_date_result["result"]:
            [error_info_list.append(error_info) for error_info in check_to_date_result["errorInfo"]]

        # 01-04.相関チェック処理
        # 01-04-01.「引数．リクエストボディ．検索用日時From」と「引数．リクエストボディ．検索用日時To」に値が設定されており、
        #          「引数．リクエストボディ．検索用日時From」が「引数．リクエストボディ．検索用日時To」の値を超過している場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.correlation_check_date(request_body.fromDate, request_body.toDate):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["030006"]["logMessage"]))
            error_info_list.append(
                {
                    "errorCode": "030006",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["030006"]["message"])
                }
            )

        # 01-04-02.「引数．ヘッダパラメータ．PDSユーザID」と「引数．PDSユーザドメイン情報．PDSユーザID」の値が一致しない場合、「変数．エラー情報リスト」にエラー情報を追加する
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


async def router_main(
    request: Request,
    pageNo: str,
    pdsUserDomainName,
    request_body: requestBody,
    pdsUserId: str,
    accessToken: str,
    timeStamp: str,
    jwt: str,
    trace_logger: Logger,
    guid: str
):
    try:
        # 01 事前処理
        # 01-01 以下の引数で事前処理を実行
        # 01-02 事前処理からのレスポンスを、「変数．事前処理実行結果」に格納する
        advance_exec_result = advance_exec(trace_logger, guid, pageNo, pdsUserDomainName, request_body, pdsUserId, accessToken, timeStamp, jwt, request)
        trace_logger = advance_exec_result["traceLogger"]
        out_logger = advance_exec_result["outLogger"]

        # 個人情報検索処理
        search_model = searchModelClass(advance_exec_result["traceLogger"], request, advance_exec_result["pdsUserInfo"], pageNo, pdsUserDomainName)
        main_response = search_model.main(request_body)

        common_util = CommonUtilClass(advance_exec_result["traceLogger"])
        # 06.アクセストークン発行処理
        # 06-01.以下の引数でアクセストークン発行処理を実行する
        # 06-02.アクセストークン発行処理のレスポンスを「変数．アクセストークン発行処理結果」に格納する
        token_util = TokenUtilClass(advance_exec_result["traceLogger"])
        token_create_response = token_util.create_token_public(
            advance_exec_result["pdsUserInfo"]["pdsUserId"],
            advance_exec_result["pdsUserInfo"]["pdsUserName"],
            accessToken
        )

        # 07.共通エラーチェック処理
        # 07-01.以下の引数で共通エラーチェック処理を実行する
        # 07-02.例外が発生した場合、例外処理に遷移
        if token_create_response.get("errorInfo"):
            # API実行履歴登録処理
            api_history_insert = CallbackExecutor(
                common_util.insert_api_history,
                commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                advance_exec_result["pdsUserInfo"]["pdsUserId"],
                apitypeConstClass.API_TYPE["SEARCH"],
                pdsUserDomainName,
                str(request.url),
                json.dumps({"path_param": request.path_params, "query_param": request.query_params._dict, "header_param": commonUtil.make_headerParam(request.headers), "request_body": request_body.dict()}),
                False,
                None,
                commonUtil.get_str_datetime()
            )
            common_util.common_error_check(
                token_create_response["errorInfo"],
                api_history_insert
            )

        # 08.API実行履歴登録処理
        # 08-01.以下の引数でAPI実行履歴登録処理を実行する
        # 08-02.API実行履歴登録処理のレスポンスを「変数．API実行履歴登録処理結果」に格納する
        try:
            common_util.insert_api_history(
                commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                advance_exec_result["pdsUserInfo"]["pdsUserId"],
                apitypeConstClass.API_TYPE["SEARCH"],
                pdsUserDomainName,
                str(request.url),
                json.dumps({"path_param": request.path_params, "query_param": request.query_params._dict, "header_param": commonUtil.make_headerParam(request.headers), "request_body": request_body.dict()}),
                True,
                None,
                commonUtil.get_str_datetime()
            )
        except Exception as e:
            common_util.insert_api_history(
                commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                advance_exec_result["pdsUserInfo"]["pdsUserId"],
                apitypeConstClass.API_TYPE["SEARCH"],
                pdsUserDomainName,
                str(request.url),
                json.dumps({"path_param": request.path_params, "query_param": request.query_params._dict, "header_param": commonUtil.make_headerParam(request.headers), "request_body": request_body.dict()}),
                True,
                None,
                commonUtil.get_str_datetime()
            )
            raise e

        return {
            "result": True,
            "accessToken": token_create_response["accessToken"],
            "maxPage": main_response["max_page_no"],
            "maxCount": main_response["max_item_no"],
            "pageNo": main_response["page_no"],
            "tidList": main_response["tid_list"],
            "jwt": token_create_response["jwt"],
            "traceLogger": trace_logger,
            "outLogger": out_logger
        }
    # 例外処理(PDSException)
    except PDSException as e:
        raise e

    # 例外処理
    except Exception as e:
        advance_exec_result["traceLogger"].error(logUtil.message_build(MessageConstClass.ERRORS["999999"]["logMessage"], str(e), traceback.format_exc()))
        raise PDSException(
            {
                "errorCode": "999999",
                "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
            }
        )


# 個人情報検索API(PageNoが存在しない場合はAPIの入口を分割する必要がある)
@router.post("/api/2.0/{pdsUserDomainName}/transaction/search/")
async def search_no_page(
    request: Request,
    pdsUserDomainName,
    request_body: Optional[requestBody],
    pdsUserId: Optional[str] = Header(""),
    accessToken: Optional[str] = Header(""),
    timeStamp: Optional[str] = Header(""),
    jwt: str = Depends(oauth2_scheme)
):
    # ロガー作成
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", request_body.dict(), request)
    pageNo = 1
    try:
        router_main_result = await router_main(
            request,
            pageNo,
            pdsUserDomainName,
            request_body,
            pdsUserId,
            accessToken,
            timeStamp,
            jwt,
            trace_logger,
            guid
        )
        trace_logger = router_main_result["traceLogger"]
        out_logger = router_main_result["outLogger"]

        # 09.終了処理
        response_content = {
            "status": "OK",
            "accessToken": router_main_result["accessToken"],
            "maxPage": router_main_result["maxPage"],
            "maxCount": router_main_result["maxCount"],
            "pageNo": router_main_result["pageNo"],
            "tidList": router_main_result["tidList"]
        }
        out_logger.info(logUtil.message_build(MessageConstClass.OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP, json.dumps(response_content)))
        # 09-01.返却パラメータを作成し返却する
        response = JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response_content
        )
        response.headers["Authorization"] = "Bearer " + router_main_result["jwt"]

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


# 個人情報検索API
@router.post("/api/2.0/{pdsUserDomainName}/transaction/search/{pageNo}")
async def search(
    request: Request,
    pageNo: int,
    pdsUserDomainName,
    request_body: Optional[requestBody],
    pdsUserId: Optional[str] = Header(""),
    accessToken: Optional[str] = Header(""),
    timeStamp: Optional[str] = Header(""),
    jwt: str = Depends(oauth2_scheme)
):
    # ロガー作成
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", request_body.dict(), request)
    try:
        in_logger.info(logUtil.message_build(MessageConstClass.IN_LOG["000000"]["logMessage"], EXEC_NAME_JP))
        router_main_result = await router_main(
            request,
            pageNo,
            pdsUserDomainName,
            request_body,
            pdsUserId,
            accessToken,
            timeStamp,
            jwt,
            trace_logger,
            guid
        )
        trace_logger = router_main_result["traceLogger"]
        out_logger = router_main_result["outLogger"]

        # 09.終了処理
        response_content = {
            "status": "OK",
            "accessToken": router_main_result["accessToken"],
            "maxPage": router_main_result["maxPage"],
            "maxCount": router_main_result["maxCount"],
            "pageNo": router_main_result["pageNo"],
            "tidList": router_main_result["tidList"]
        }
        out_logger.info(logUtil.message_build(MessageConstClass.OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP, json.dumps(response_content)))
        # 09-01.返却パラメータを作成し返却する
        response = JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response_content
        )
        response.headers["Authorization"] = "Bearer " + router_main_result["jwt"]

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
