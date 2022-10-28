from typing import Optional, Any
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
from models.closed.multiDeleteModel import multiDeleteModel

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
from util.commonParamCheck import checkPdsUserId
from util.commonParamCheck import checkTimeStamp
from util.commonParamCheck import checkAccessToken
from util.commonParamCheck import checkUserIdMatchMode
from util.commonParamCheck import checkUserIdStr
from util.commonParamCheck import checkDataJsonKey
from util.commonParamCheck import checkDataMatchMode
from util.commonParamCheck import checkDataStr
from util.commonParamCheck import checkFromDate
from util.commonParamCheck import checkToDate
from util.commonParamCheck import checkImageHash
from util.commonParamCheck import checkApprovalUserId
from util.commonParamCheck import checkApprovalUserPassword
from util.commonParamCheck import checkMailAddressTo
from util.commonParamCheck import checkMailAddressCc

# Bearerトークン設定
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="bearerToken")

# 処理名
EXEC_NAME: str = "multiDelete"
EXEC_NAME_JP: str = "個人情報一括削除"

# ルータ作成
router = APIRouter()


class searchCriteriaInfo(BaseModel):
    userIdMatchMode: Optional[Any] = None
    userIdStr: Optional[Any] = None
    dataJsonKey: Optional[Any] = None
    dataMatchMode: Optional[Any] = None
    dataStr: Optional[Any] = None
    imageHash: Optional[Any] = None
    fromDate: Optional[Any] = None
    toDate: Optional[Any] = None


class requestBody(BaseModel):
    pdsUserId: Optional[Any] = None
    searchCriteria: Optional[searchCriteriaInfo] = None
    tidList: Optional[Any] = None
    tidListFileName: Optional[Any] = None
    approvalUserId: Optional[Any] = None
    approvalUserPassword: Optional[Any] = None
    mailAddressTo: Optional[Any] = None
    mailAddressCc: Optional[Any] = None
    multiDeleteAgreementStr: Optional[Any] = None


def advance_exec(
    trace_logger: Logger,
    logger_guid: str,
    request_body: requestBody,
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
        request_body (requestBody): リクエストボディ
        access_token (str): アクセストークン（ヘッダパラメータ）
        time_stamp (str): タイムスタンプ（ヘッダパラメータ）
        jwt (str): JWT
        request (Request): リクエスト情報
    """
    try:
        # 01.アクセストークン検証処理
        token_util = TokenUtilClass(trace_logger)
        # 01-01.以下の引数でアクセストークン検証処理を実行する
        # 01-02.アクセストークン検証処理からのレスポンスを、「変数．アクセストークン検証処理実行結果」に格納する
        token_verify_response = token_util.verify_token_closed(access_token, jwt)

        # 02.共通エラーチェック処理
        common_util = CommonUtilClass(trace_logger)
        # 02-01.以下の引数で共通エラーチェック処理を実行する
        # 02-02.例外が発生した場合、例外処理に遷移
        if token_verify_response.get("errorInfo"):
            # API実行履歴登録処理
            api_history_insert = CallbackExecutor(
                common_util.insert_api_history,
                commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                request_body.pdsUserId,
                apitypeConstClass.API_TYPE["BATCH_DELETE"],
                None,
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

        # 03.パラメータ検証処理
        # 03-01.以下の引数でパラメータ検証処理を実行する
        # 03-02.パラメータ検証処理のレスポンスを「変数．パラメータ検証処理実行結果」に格納する
        input_check_result = input_check(trace_logger, access_token, time_stamp, request_body, token_verify_response)

        # 04.共通エラーチェック処理
        # 04-01.以下の引数で共通エラーチェック処理を実行する
        # 04-02.例外が発生した場合、例外処理に遷移
        if input_check_result.get("errorInfo"):
            # API実行履歴登録処理
            api_history_insert = CallbackExecutor(
                common_util.insert_api_history,
                commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                request_body.pdsUserId,
                apitypeConstClass.API_TYPE["BATCH_DELETE"],
                None,
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

        # 05.終了処理
        # 05-01.レスポンス情報を作成し、返却する
        return {
            "result": True,
            "token_verify_response": token_verify_response,
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


def input_check(trace_logger: Logger, access_token, time_stamp, request_body: requestBody, token_verify_response):
    """
    パラメータ検証処理

    Args:
        trace_logger (Logger): ロガー（TRACE）
        request_body (requestBody): リクエストボディ
        access_token (_type_): アクセストークン
        time_stamp (_type_): タイムスタンプ
        token_verify_response (dict): アクセストークン検証処理結果

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

        # 01-01-02.アクセストークン検証処理
        # 01-01-02-01.以下の引数でアクセストークン検証処理を実行する
        check_access_token_result = checkAccessToken.CheckAccessToken(trace_logger, access_token).get_result()
        # 01-01-02-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not check_access_token_result["result"]:
            [error_info_list.append(error_info) for error_info in check_access_token_result["errorInfo"]]

        # 01-02.リクエストボディ検証処理
        # 01-02-01.PDSユーザID検証処理
        # 01-02-01-01.以下の引数でPDSユーザID検証処理を実行する
        check_pds_user_id = checkPdsUserId.CheckPdsUserId(trace_logger, request_body.pdsUserId).get_result()
        # 01-02-01-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not check_pds_user_id["result"]:
            [error_info_list.append(error_info) for error_info in check_pds_user_id["errorInfo"]]

        # 01-02-02.検索用ユーザID検索モード検証処理
        # 01-02-02-01.以下の引数で検索用ユーザID検索モード検証処理を実行する
        check_user_id_matchmode_result = checkUserIdMatchMode.CheckUserIdMatchMode(trace_logger, request_body.searchCriteria.userIdMatchMode).get_result()
        # 01-02-02-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not check_user_id_matchmode_result["result"]:
            [error_info_list.append(error_info) for error_info in check_user_id_matchmode_result["errorInfo"]]

        # 01-02-03.検索用ユーザID検索文字列検証処理
        # 01-02-03-01.以下の引数で検索用ユーザID検索文字列検証処理を実行する
        check_user_id_str_result = checkUserIdStr.CheckUserIdStr(trace_logger, request_body.searchCriteria.userIdStr).get_result()
        # 01-02-03-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not check_user_id_str_result["result"]:
            [error_info_list.append(error_info) for error_info in check_user_id_str_result["errorInfo"]]

        # 01-02-04.保存データJsonキー情報検証処理
        # 01-02-04-01.以下の引数で保存データJsonキー情報検証処理を実行する
        check_data_json_result = checkDataJsonKey.CheckDataJsonKey(trace_logger, request_body.searchCriteria.dataJsonKey).get_result()
        # 01-02-04-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not check_data_json_result["result"]:
            [error_info_list.append(error_info) for error_info in check_data_json_result["errorInfo"]]

        # 01-02-05.保存データ検索モード検証処理
        # 01-02-05-01.以下の引数で保存データ検索モード検証処理を実行する
        check_data_matchmode_result = checkDataMatchMode.CheckDataMatchMode(trace_logger, request_body.searchCriteria.dataMatchMode).get_result()
        # 01-02-05-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not check_data_matchmode_result["result"]:
            [error_info_list.append(error_info) for error_info in check_data_matchmode_result["errorInfo"]]

        # 01-02-06.保存データ検索文字列検証処理
        # 01-02-06-01.以下の引数で保存データ検索文字列検証処理を実行する
        check_data_str_result = checkDataStr.CheckDataStr(trace_logger, request_body.searchCriteria.dataStr).get_result()
        # 01-02-06-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not check_data_str_result["result"]:
            [error_info_list.append(error_info) for error_info in check_data_str_result["errorInfo"]]

        # 01-02-07.保存したいバイナリデータのハッシュ値検証処理
        # 01-02-07-01.以下の引数で保存されたバイナリデータのハッシュ値検証処理を実行する
        check_image_hash_result = checkImageHash.CheckImageHash(trace_logger, request_body.searchCriteria.imageHash).get_result()
        # 01-02-07-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not check_image_hash_result["result"]:
            [error_info_list.append(error_info) for error_info in check_image_hash_result["errorInfo"]]

        # 01-02-08.検索用日時From検証処理
        # 01-02-08-01.以下の引数で検索用日時From検証処理を実行する
        check_from_date_result = checkFromDate.CheckFromDate(trace_logger, request_body.searchCriteria.fromDate).get_result()
        # 01-02-08-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not check_from_date_result["result"]:
            [error_info_list.append(error_info) for error_info in check_from_date_result["errorInfo"]]

        # 01-02-09.検索用日時To検証処理
        # 01-02-09-01.以下の引数で検索用日時To検証処理を実行する
        check_to_date_result = checkToDate.CheckToDate(trace_logger, request_body.searchCriteria.toDate).get_result()
        # 01-02-09-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not check_to_date_result["result"]:
            [error_info_list.append(error_info) for error_info in check_to_date_result["errorInfo"]]

        # 01-02-10.「引数．リクエストボディ．tidリスト」に値が設定されており、型が文字列型か配列型ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_type(request_body.tidList, str, list):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "tidリスト", "文字列,配列"))
            error_info_list.append(
                {
                    "errorCode": "020019",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "tidリスト", "文字列,配列")
                }
            )

        # 01-02-11.「引数．リクエストボディ．tidリスト」に値が設定されており、値に入力可能文字以外が含まれている場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_image_hash(request_body.tidList):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020020"]["logMessage"], "tidリスト"))
            error_info_list.append(
                {
                    "errorCode": "020020",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020020"]["message"], "tidリスト")
                }
            )

        # 01-02-12.「引数．リクエストボディ．tidリスト」に値が設定されており、値の桁数が36桁を超過する場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_max_length_list_str(request_body.tidList, 36):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020002"]["logMessage"], "tidリスト", "36"))
            error_info_list.append(
                {
                    "errorCode": "020002",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020002"]["message"], "tidリスト", "36")
                }
            )

        # 01-02-13.「引数．リクエストボディ．tidリストファイル名」に値が設定されており、型が文字列型か配列型ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_type(request_body.tidListFileName, str):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "tidリストファイル名", "文字列"))
            error_info_list.append(
                {
                    "errorCode": "020019",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "tidリストファイル名", "文字列")
                }
            )

        # 01-02-14.「引数．リクエストボディ．tidリストファイル名」に値が設定されており、値に入力可能文字以外が含まれている場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_enterable_characters_file_name(request_body.tidListFileName):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020020"]["logMessage"], "tidリストファイル名"))
            error_info_list.append(
                {
                    "errorCode": "020020",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020020"]["message"], "tidリストファイル名")
                }
            )

        # 01-02-15.承認TFオペレータID検証処理
        # 01-02-15-01.以下の引数で承認TFオペレータID検証処理を実行する
        check_approval_user_id_result = checkApprovalUserId.CheckApprovalUserId(trace_logger, request_body.approvalUserId).get_result()
        # 01-02-15-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not check_approval_user_id_result["result"]:
            [error_info_list.append(error_info) for error_info in check_approval_user_id_result["errorInfo"]]

        # 01-02-16.承認TFオペレータパスワード検証処理
        # 01-02-16-01.以下の引数で承認TFオペレータパスワード検証処理を実行する
        check_approval_user_password_result = checkApprovalUserPassword.CheckApprovalUserPassword(trace_logger, request_body.approvalUserPassword).get_result()
        # 01-02-16-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not check_approval_user_password_result["result"]:
            [error_info_list.append(error_info) for error_info in check_approval_user_password_result["errorInfo"]]

        # 01-02-17.宛先To検証処理
        # 01-02-17-01.以下の引数で宛先To検証処理を実行する
        check_mail_addoress_to_result = checkMailAddressTo.CheckMailAddressTo(trace_logger, request_body.mailAddressTo).get_result()
        # 01-02-17-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not check_mail_addoress_to_result["result"]:
            [error_info_list.append(error_info) for error_info in check_mail_addoress_to_result["errorInfo"]]

        # 01-02-18.宛先Cc検証処理
        # 01-02-18-01.以下の引数で宛先Cc検証処理を実行する
        check_mail_addoress_cc_result = checkMailAddressCc.CheckMailAddressCc(trace_logger, request_body.mailAddressCc).get_result()
        # 01-02-18-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not check_mail_addoress_cc_result["result"]:
            [error_info_list.append(error_info) for error_info in check_mail_addoress_cc_result["errorInfo"]]

        # 01-02-19.「引数．リクエストボディ．一括削除同意テキスト」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_require(request_body.multiDeleteAgreementStr):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "一括削除同意テキスト"))
            error_info_list.append(
                {
                    "errorCode": "020001",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "一括削除同意テキスト")
                }
            )

        # 01-02-20.「引数．リクエストボディ．一括削除同意テキスト」に値が設定されており、型が文字列型ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_type(request_body.multiDeleteAgreementStr, str):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "一括削除同意テキスト", "文字列"))
            error_info_list.append(
                {
                    "errorCode": "020019",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "一括削除同意テキスト", "文字列")
                }
            )

        # 01-02-21.「引数．リクエストボディ．一括削除同意テキスト」に値が設定されており、値が入力規則に違反している場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_multi_delete_agreement_str(request_body.multiDeleteAgreementStr):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020003"]["logMessage"], "一括削除同意テキスト"))
            error_info_list.append(
                {
                    "errorCode": "020003",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "一括削除同意テキスト")
                }
            )

        # 01-02-22.「引数．リクエストボディ．一括削除同意テキスト」に値が設定されており、値の桁数が4桁ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_length(request_body.multiDeleteAgreementStr, 4):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020014"]["logMessage"], "一括削除同意テキスト", "4"))
            error_info_list.append(
                {
                    "errorCode": "020014",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020014"]["message"], "一括削除同意テキスト", "4")
                }
            )

        # 01-03.相関チェック処理
        # 01-03-01.「引数．リクエストボディ．検索条件．検索用日時From」と「引数．リクエストボディ．検索条件．検索用日時To」に値が設定されており、
        #          「引数．リクエストボディ．検索条件．検索用日時From」が「引数．リクエストボディ．検索条件．検索用日時To」の値を超過している場合、
        #          「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.correlation_check_date(request_body.searchCriteria.fromDate, request_body.searchCriteria.toDate):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["030006"]["logMessage"]))
            error_info_list.append(
                {
                    "errorCode": "030006",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["030006"]["message"])
                }
            )

        # 01-03-02.「引数．アクセストークン検証処理実行結果．JWT．TFオペレータID」と
        #          「引数．リクエストボディ．承認TFオペレータID」に値が設定されており、
        #          「引数．アクセストークン検証処理実行結果．JWT．TFオペレータID」と
        #          「引数．リクエストボディ．承認TFオペレータID」の値が同一の場合、
        #          「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.correlation_check_tf_operator_id(token_verify_response["payload"]["tfOperatorId"], request_body.approvalUserId):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["030016"]["logMessage"]))
            error_info_list.append(
                {
                    "errorCode": "030016",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["030016"]["message"])
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


# 個人情報一括削除API
@router.post("/api/2.0/transaction/multidelete")
def multi_delete(
    request: Request,
    request_body: Optional[requestBody],
    accessToken: Optional[str] = Header(""),
    timeStamp: Optional[str] = Header(""),
    jwt: str = Depends(oauth2_scheme)
):
    """
    個人情報一括削除API

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
        # 01 事前処理
        # 01-01 以下の引数で事前処理を実行
        # 01-02 事前処理からのレスポンスを、「変数．事前処理実行結果」に格納する
        advance_exec_result = advance_exec(trace_logger, guid, request_body, accessToken, timeStamp, jwt, request)
        trace_logger = advance_exec_result["traceLogger"]
        out_logger = advance_exec_result["outLogger"]

        # 個人情報一括削除処理
        multi_delete_model = multiDeleteModel(advance_exec_result["traceLogger"], request)
        multi_delete_model.main(request_body)

        common_util = CommonUtilClass(trace_logger)
        # 29.アクセストークン発行処理
        token_util = TokenUtilClass(trace_logger)
        # 29-01.アクセストークン発行処理を実行する
        # 29-02.アクセストークン発行処理からのレスポンスを、「変数．アクセストークン発行処理実行結果」に格納する
        token_create_response = token_util.create_token_closed(
            {
                "tfOperatorId": advance_exec_result["token_verify_response"]["payload"]["tfOperatorId"],
                "tfOperatorName": advance_exec_result["token_verify_response"]["payload"]["tfOperatorName"]
            },
            advance_exec_result["token_verify_response"]["payload"]["accessToken"]
        )

        # 30.共通エラーチェック処理
        # 30-01.以下の引数で共通エラーチェック処理を実行する
        # 30-02.例外が発生した場合、例外処理に遷移
        if token_create_response.get("errorInfo"):
            api_history_insert = CallbackExecutor(
                common_util.insert_api_history,
                commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                request_body.pdsUserId,
                apitypeConstClass.API_TYPE["BATCH_DELETE"],
                None,
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

        # 31.API実行履歴登録処理
        # 31-01.以下の引数でAPI実行履歴登録処理を実行する
        try:
            common_util.insert_api_history(
                commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                request_body.pdsUserId,
                apitypeConstClass.API_TYPE["BATCH_DELETE"],
                None,
                str(request.url),
                json.dumps({"path_param": request.path_params, "query_param": request.query_params._dict, "header_param": commonUtil.make_headerParam(request.headers), "request_body": request_body.dict()}),
                True,
                None,
                commonUtil.get_str_datetime()
            )
        except Exception as e:
            # 31-02.処理に失敗した場合、以下の引数でAPI実行履歴登録処理を実行する
            common_util.insert_api_history(
                commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
                request_body.pdsUserId,
                apitypeConstClass.API_TYPE["BATCH_DELETE"],
                None,
                str(request.url),
                json.dumps({"path_param": request.path_params, "query_param": request.query_params._dict, "header_param": commonUtil.make_headerParam(request.headers), "request_body": request_body.dict()}),
                False,
                None,
                commonUtil.get_str_datetime()
            )
            raise e

        # 32.終了処理
        # 32-01.正常終了をCloudWatchへログ出力する
        response_content = {
            "status": "OK",
            "accessToken": token_create_response["accessToken"]
        }
        out_logger.info(logUtil.message_build(MessageConstClass.OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP, json.dumps(response_content)))
        # 32-02.レスポンス情報整形処理
        # 32-02-01.以下をレスポンスとして返却する
        # 32-03.処理を終了する
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
