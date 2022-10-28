import traceback
import json
# FastApi
from fastapi import APIRouter, Depends, status, Header, Request
from typing import Optional
from fastapi.responses import JSONResponse
# Security
from fastapi.security import OAuth2PasswordBearer
# Logger
from logging import Logger

# 自作クラス
## 業務ロジッククラス
from models.public.deleteModel import deleteModelClass

## コールバック関数
from util.callbackExecutorUtil import CallbackExecutor
## Exception
from exceptionClass.PDSException import PDSException

# utilクラス
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
from util.commonParamCheck import checkTransactionId

# 処理名
EXEC_NAME: str = "delete"
EXEC_NAME_JP: str = "個人情報削除"

# ルータ作成
router = APIRouter()

# Bearerトークン設定
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="bearerToken")


def advance_exec(
    trace_logger: Logger,
    logger_guid: str,
    pds_user_domain_name: str,
    transaction_id: str,
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
        pds_user_domain_name (str): PDSユーザドメイン名（パスパラメータ）
        transaction_id (str): トランザクションID (クエリパラメータ)
        pds_user_id (str): PDSユーザID（ヘッダパラメータ）
        access_token (str): アクセストークン（ヘッダパラメータ）
        time_stamp (str): タイムスタンプ（ヘッダパラメータ）
        jwt (str): JWT
        request (Request): リクエスト情報
    """
    try:
        # 01.PDSユーザドメイン検証処理
        common_util = CommonUtilClass(trace_logger)
        # 01-01.以下の引数でPDSユーザドメイン検証処理実行
        # 01-02.PDSユーザドメイン検証処理からのレスポンスを、「変数．PDSユーザドメイン検証処理実行結果」に格納する
        pds_user_domain_check_result = common_util.check_pds_user_domain(pds_user_domain_name, pds_user_id)

        # 02.共通エラーチェック処理
        # 02-01.以下の引数で共通エラーチェック処理を実行する
        # 02-02.例外が発生した場合、例外処理に遷移
        if pds_user_domain_check_result.get("errorInfo"):
            # API実行履歴登録処理
            api_history_insert = CallbackExecutor(
                common_util.insert_api_history,
                commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                None,
                apitypeConstClass.API_TYPE["DELETE"],
                pds_user_domain_name,
                str(request.url),
                json.dumps({"path_param": request.path_params, "query_param": request.query_params._dict, "header_param": commonUtil.make_headerParam(request.headers), "request_body": ""}),
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
                apitypeConstClass.API_TYPE["DELETE"],
                pds_user_domain_name,
                str(request.url),
                json.dumps({"path_param": request.path_params, "query_param": request.query_params._dict, "header_param": commonUtil.make_headerParam(request.headers)}),
                False,
                None,
                commonUtil.get_str_datetime()
            )
            common_util.common_error_check(
                token_verify_response["errorInfo"],
                api_history_insert
            )

        # JWTペイロード設定済みロガー再作成作成
        trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, logger_guid, json.dumps(token_verify_response["payload"]), "", request)

        # 05.パラメータ検証チェック処理
        # 05-01.以下の引数でパラメータ検証処理を実行する
        # 05-02.パラメータ検証処理のレスポンスを「変数．パラメータ検証処理実行結果」に格納する
        input_check_result = input_check(trace_logger, pds_user_domain_name, transaction_id, pds_user_id, access_token, time_stamp, pds_user_domain_check_result)

        # 06.共通エラーチェック処理
        # 06-01.以下の引数で共通エラーチェック処理を実行する
        # 06-02.例外が発生した場合、例外処理に遷移
        if input_check_result.get("errorInfo"):
            # API実行履歴登録処理
            api_history_insert = CallbackExecutor(
                common_util.insert_api_history,
                commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                pds_user_domain_check_result["pdsUserInfo"]["pdsUserId"],
                apitypeConstClass.API_TYPE["DELETE"],
                pds_user_domain_name,
                str(request.url),
                json.dumps({"path_param": request.path_params, "query_param": request.query_params._dict, "header_param": commonUtil.make_headerParam(request.headers)}),
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


# 入力チェック
def input_check(
    trace_logger: Logger,
    pds_user_domain_name: str,
    transaction_id: str,
    pds_user_id: str,
    access_token: str,
    time_stamp: str,
    pds_user_domain_check_result: dict
):
    """
    パラメータ検証処理

    Args:
        trace_logger (Logger): ロガー(TRACE)
        pds_user_domain_name (str): PDSユーザドメイン名（パスパラメータ）
        transaction_id (str): トランザクションID (クエリパラメータ)
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

        # 01-02.クエリパラメータ検証処理
        # 01-02-01.トランザクションID検証処理
        # 01-02-01-01.以下の引数でトランザクションID検証処理を実行する
        check_transaction_id_result = checkTransactionId.CheckTransactionId(trace_logger, transaction_id).get_result()
        # 01-02-01-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not check_transaction_id_result["result"]:
            [error_info_list.append(error_info) for error_info in check_transaction_id_result["errorInfo"]]

        # 01-03.ヘッダパラメータ検証処理
        # 01-03-01.PDSユーザID検証処理
        # 01-03-01-01.以下の引数でPDSユーザID検証処理を実行する
        check_pds_user_id_result = checkPdsUserId.CheckPdsUserId(trace_logger, pds_user_id).get_result()
        # 01-03-01-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not check_pds_user_id_result["result"]:
            [error_info_list.append(error_info) for error_info in check_pds_user_id_result["errorInfo"]]

        # 01-03-02.タイムスタンプ検証処理
        # 01-03-02-01.以下の引数でタイムスタンプ検証処理を実行する
        check_time_stamp_result = checkTimeStamp.CheckTimeStamp(trace_logger, time_stamp).get_result()
        # 01-03-02-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not check_time_stamp_result["result"]:
            [error_info_list.append(error_info) for error_info in check_time_stamp_result["errorInfo"]]

        # 01-03-03.アクセストークン検証処理
        # 01-03-03-01.以下の引数でアクセストークン検証処理を実行する
        check_access_token_result = checkAccessToken.CheckAccessToken(trace_logger, access_token).get_result()
        # 01-03-03-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not check_access_token_result["result"]:
            [error_info_list.append(error_info) for error_info in check_access_token_result["errorInfo"]]

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


# 個人情報削除API
@router.delete("/api/2.0/{pdsUserDomainName}/transaction")
async def delete(
    request: Request,
    pdsUserDomainName: str,
    tid: str,
    pdsUserId: Optional[str] = Header(""),
    accessToken: Optional[str] = Header(""),
    timeStamp: Optional[str] = Header(""),
    jwt: str = Depends(oauth2_scheme)
):
    """
        個人情報削除API

        Args:
            request (Request): リクエストオブジェクト
            pdsUserDomainName (str): PDSユーザドメイン名
            tid (str): トランザクションID
            pdsUserID (Optional[str]): PDSユーザID
            accessToken (Optional[str]): アクセストークン
            timeStamp (Optional[str]): タイムスタンプ
            jwt (str): JWT

        Returns:
            status: ステータス
            accessToken: アクセストークン
        """
    # ロガー作成
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", request)
    common_util = CommonUtilClass(trace_logger)

    try:
        in_logger.info(logUtil.message_build(MessageConstClass.IN_LOG["000000"]["logMessage"], EXEC_NAME_JP))
        # 01.事前処理
        # 01-01.以下の引数で事前処理を実行
        # 01-02.事前処理からのレスポンスを、「変数．事前処理実行結果」に格納する
        advance_exec_result = advance_exec(trace_logger, guid, pdsUserDomainName, tid, pdsUserId, accessToken, timeStamp, jwt, request)

        # 個人情報削除処理
        delete_model = deleteModelClass(advance_exec_result["traceLogger"], request, advance_exec_result["pdsUserInfo"], tid, pdsUserDomainName)
        delete_model.main()

        # 04.アクセストークン発行処理
        # 04-01.以下の引数でアクセストークン発行処理を実行する
        # 04-02.アクセストークン発行処理のレスポンスを「変数．アクセストークン発行処理結果」に格納する
        token_util = TokenUtilClass(advance_exec_result["traceLogger"])
        token_create_response = token_util.create_token_public(
            advance_exec_result["pdsUserInfo"]["pdsUserId"],
            advance_exec_result["pdsUserInfo"]["pdsUserName"],
            accessToken
        )

        # 05.共通エラーチェック処理
        # 05-01.以下の引数で共通エラーチェック処理を実行する
        # 05-02.例外が発生した場合、例外処理に遷移
        if token_create_response.get("errorInfo"):
            # API実行履歴登録処理
            api_history_insert = CallbackExecutor(
                common_util.insert_api_history,
                commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                pdsUserId,
                apitypeConstClass.API_TYPE["DELETE"],
                pdsUserDomainName,
                str(request.url),
                json.dumps({"path_param": request.path_params, "query_param": request.query_params._dict, "header_param": commonUtil.make_headerParam(request.headers)}),
                False,
                None,
                commonUtil.get_str_datetime()
            )
            common_util.common_error_check(
                token_create_response["errorInfo"],
                api_history_insert
            )

        # 06.API実行履歴登録処理
        # 06-01.以下の引数でAPI実行履歴登録処理を実行する
        try:
            common_util.insert_api_history(
                commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                advance_exec_result["pdsUserInfo"]["pdsUserId"],
                apitypeConstClass.API_TYPE["DELETE"],
                pdsUserDomainName,
                str(request.url),
                json.dumps({"path_param": request.path_params, "query_param": request.query_params._dict, "header_param": commonUtil.make_headerParam(request.headers)}),
                True,
                None,
                commonUtil.get_str_datetime()
            )
        except Exception as e:
            # 06-02.処理に失敗した場合、以下の引数でAPI実行履歴登録処理を実行する
            common_util.insert_api_history(
                commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                pdsUserId,
                apitypeConstClass.API_TYPE["DELETE"],
                pdsUserDomainName,
                str(request.url),
                json.dumps({"path_param": request.path_params, "query_param": request.query_params._dict, "header_param": commonUtil.make_headerParam(request.headers)}),
                False,
                None,
                commonUtil.get_str_datetime()
            )
            raise e

        # 07.終了処理
        # 07-01.返却パラメータを作成し返却する
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
