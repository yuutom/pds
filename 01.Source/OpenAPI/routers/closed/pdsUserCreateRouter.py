import json
from typing import Optional, Any
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

# 自作クラス
## 業務ロジッククラス
from models.closed.pdsUserCreateModel import pdsUserCreateModelClass
## utilクラス
from util import checkUtil
from util.tokenUtil import TokenUtilClass
import util.logUtil as logUtil
from util.commonUtil import CommonUtilClass

from exceptionClass.PDSException import PDSException

## 共通パラメータチェッククラス
from util.commonParamCheck import checkTimeStamp
from util.commonParamCheck import checkAccessToken
from util.commonParamCheck import checkPdsUserId
from util.commonParamCheck import checkPdsUserDomainName
from util.commonParamCheck import checkMultiDownloadFileSendAddressTo
from util.commonParamCheck import checkMultiDownloadFileSendAddressCc
from util.commonParamCheck import checkMultiDeleteFileSendAddressTo
from util.commonParamCheck import checkMultiDeleteFileSendAddressCc
from util.commonParamCheck import checkPublicKeySendAddressTo
from util.commonParamCheck import checkPublicKeySendAddressCc
## 固定値クラス
from const.messageConst import MessageConstClass
from const.systemConst import SystemConstClass

# Bearerトークン設定
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="bearerToken")

# 処理名
EXEC_NAME: str = "pdsUserCreate"
EXEC_NAME_JP: str = "PDSユーザ登録"

# ルータ作成
router = APIRouter()


class requestBody(BaseModel):
    """
    リクエストボディクラス

    Args:
        BaseModel (Object): Pydanticのベースクラス
    """
    pdsUserId: Optional[Any] = None
    pdsUserName: Optional[Any] = None
    pdsUserDomainName: Optional[Any] = None
    pdsUserPublicKeyStartDate: Optional[Any] = None
    pdsUserPublicKeyExpectedDate: Optional[Any] = None
    tfContactAddress: Optional[Any] = None
    multiDownloadFileSendAddressTo: Optional[Any] = None
    multiDownloadFileSendAddressCc: Optional[Any] = None
    multiDeleteFileSendAddressTo: Optional[Any] = None
    multiDeleteFileSendAddressCc: Optional[Any] = None
    publicKeySendAddressTo: Optional[Any] = None
    publicKeySendAddressCc: Optional[Any] = None


def input_check(trace_logger: Logger, request_body: requestBody, access_token, time_stamp):
    """
    パラメータ検証処理

    Args:
        trace_logger (Logger): ロガー（TRACE）
        request_body (requestBody): リクエストボディ
        access_token (_type_): アクセストークン
        time_stamp (_type_): タイムスタンプ

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

        # 01-02.リクエストボディ 検証処理
        # 01-02-01.PDSユーザID検証処理
        # 01-02-01-01.以下の引数でPDSユーザID検証処理を実行する
        check_pds_user_id_result = checkPdsUserId.CheckPdsUserId(trace_logger, request_body.pdsUserId).get_result()
        # 01-02-01-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not check_pds_user_id_result["result"]:
            [error_info_list.append(error_info) for error_info in check_pds_user_id_result["errorInfo"]]

        # 01-02-02.引数．リクエストボディ．PDSユーザ名の値が設定されていない場合、変数．エラー情報リストにエラー情報を追加する。
        if not checkUtil.check_require(request_body.pdsUserName):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "PDSユーザ名"))
            error_info_list.append(
                {
                    "errorCode": "020001",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "PDSユーザ名")
                }
            )

        # 01-02-03.「引数．リクエストボディ．PDSユーザ名」に値が設定されており、型が文字列型ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_type(request_body.pdsUserName, str):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "PDSユーザ名", "文字列"))
            error_info_list.append(
                {
                    "errorCode": "020019",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "PDSユーザ名", "文字列")
                }
            )

        # 01-02-04.「引数．リクエストボディ．PDSユーザ名」に値が設定されており、値の桁数が64桁超過の場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_max_length(request_body.pdsUserName, 64):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020002"]["logMessage"], "PDSユーザ名", "64"))
            error_info_list.append(
                {
                    "errorCode": "020002",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020002"]["message"], "PDSユーザ名", "64")
                }
            )

        # 01-02-05.「引数．リクエストボディ．PDSユーザ名」に値が設定されており、値に入力可能文字以外が含まれている場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_enterable_characters_general_purpose_characters(request_body.pdsUserName):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020020"]["logMessage"], "PDSユーザ名"))
            error_info_list.append(
                {
                    "errorCode": "020020",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020020"]["message"], "PDSユーザ名")
                }
            )

        # 01-02-06.PDSユーザドメイン名検証処理
        # 01-02-06-01.以下の引数でPDSユーザドメイン名検証処理を実行する
        check_pds_user_domain_name_result = checkPdsUserDomainName.CheckPdsUserDomainName(trace_logger, request_body.pdsUserDomainName).get_result()
        # 01-02-06-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not check_pds_user_domain_name_result["result"]:
            [error_info_list.append(error_info) for error_info in check_pds_user_domain_name_result["errorInfo"]]

        # 01-02-07.「引数．リクエストボディ．PDSユーザ公開鍵開始日」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_require(request_body.pdsUserPublicKeyStartDate):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "PDSユーザ公開鍵開始日"))
            error_info_list.append(
                {
                    "errorCode": "020001",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "PDSユーザ公開鍵開始日")
                }
            )

        # 01-02-08.「引数．リクエストボディ．PDSユーザ公開鍵開始日」に値が設定されており、型が文字列型ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_type(request_body.pdsUserPublicKeyStartDate, str):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "PDSユーザ公開鍵開始日", "文字列"))
            error_info_list.append(
                {
                    "errorCode": "020019",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "PDSユーザ公開鍵開始日", "文字列")
                }
            )

        # 01-02-09.「引数．リクエストボディ．PDSユーザ公開鍵開始日」に値が設定されており、値の桁数が10桁ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_length(request_body.pdsUserPublicKeyStartDate, 10):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020014"]["logMessage"], "PDSユーザ公開鍵開始日", "10"))
            error_info_list.append(
                {
                    "errorCode": "020014",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020014"]["message"], "PDSユーザ公開鍵開始日", "10")
                }
            )

        # 01-02-10.「引数．リクエストボディ．PDSユーザ公開鍵開始日」に値が設定されており、値が入力規則に違反している場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_date(request_body.pdsUserPublicKeyStartDate):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020003"]["logMessage"], "PDSユーザ公開鍵開始日"))
            error_info_list.append(
                {
                    "errorCode": "020003",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "PDSユーザ公開鍵開始日")
                }
            )

        # 01-02-11.「引数．リクエストボディ．PDSユーザ公開鍵終了予定日」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_require(request_body.pdsUserPublicKeyExpectedDate):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "PDSユーザ公開鍵終了予定日"))
            error_info_list.append(
                {
                    "errorCode": "020001",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "PDSユーザ公開鍵終了予定日")
                }
            )

        # 01-02-12.「引数．リクエストボディ．PDSユーザ公開鍵終了予定日」に値が設定されており、型が文字列型ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_type(request_body.pdsUserPublicKeyExpectedDate, str):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "PDSユーザ公開鍵終了予定日", "文字列"))
            error_info_list.append(
                {
                    "errorCode": "020019",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "PDSユーザ公開鍵終了予定日", "文字列")
                }
            )

        # 01-02-13.「引数．リクエストボディ．PDSユーザ公開鍵終了予定日」に値が設定されており、値の桁数が10桁ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_length(request_body.pdsUserPublicKeyExpectedDate, 10):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020014"]["logMessage"], "PDSユーザ公開鍵終了予定日", "10"))
            error_info_list.append(
                {
                    "errorCode": "020014",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020014"]["message"], "PDSユーザ公開鍵終了予定日", "10")
                }
            )

        # 01-02-14.「引数．リクエストボディ．PDSユーザ公開鍵終了予定日」に値が設定されており、値が入力規則に違反している場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_date(request_body.pdsUserPublicKeyExpectedDate):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020003"]["logMessage"], "PDSユーザ公開鍵終了予定日"))
            error_info_list.append(
                {
                    "errorCode": "020003",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "PDSユーザ公開鍵終了予定日")
                }
            )

        # 01-02-15.「引数．リクエストボディ．TF担当者メールアドレス」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_require(request_body.tfContactAddress):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "PDSユーザ公開鍵終了予定日"))
            error_info_list.append(
                {
                    "errorCode": "020001",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "PDSユーザ公開鍵終了予定日")
                }
            )

        # 01-02-16.「引数．リクエストボディ．TF担当者メールアドレス」に値が設定されており、型が文字列型ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_type(request_body.tfContactAddress, str):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "PDSユーザ公開鍵終了予定日", "文字列"))
            error_info_list.append(
                {
                    "errorCode": "020019",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "PDSユーザ公開鍵終了予定日", "文字列")
                }
            )

        # 01-02-17.「引数．リクエストボディ．TF担当者メールアドレス」に値が設定されており、値の桁数が512桁超過の場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_max_length(request_body.tfContactAddress, 512):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020002"]["logMessage"], "TF担当者メールアドレス", "512"))
            error_info_list.append(
                {
                    "errorCode": "020002",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020002"]["message"], "TF担当者メールアドレス", "512")
                }
            )

        # 01-02-18.「引数．リクエストボディ．TF担当者メールアドレス」に値が設定されており、値が入力規則に違反している場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not checkUtil.check_multi_mail_address(request_body.tfContactAddress):
            trace_logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020003"]["logMessage"], "TF担当者メールアドレス"))
            error_info_list.append(
                {
                    "errorCode": "020003",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "TF担当者メールアドレス")
                }
            )

        # 01-02-19.一括DL送付先アドレスTo検証処理
        # 01-02-19-01.以下の引数で一括DL送付先アドレスTo検証処理を実行する
        check_multi_download_file_send_address_to_result = checkMultiDownloadFileSendAddressTo.CheckMultiDownloadFileSendAddressTo(trace_logger, request_body.multiDownloadFileSendAddressTo).get_result()
        # 01-02-19-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not check_multi_download_file_send_address_to_result["result"]:
            [error_info_list.append(error_info) for error_info in check_multi_download_file_send_address_to_result["errorInfo"]]

        # 01-02-20.一括DL送付先アドレスCc検証処理
        # 01-02-20-01.以下の引数で一括DL送付先アドレスCc検証処理を実行する
        check_multi_download_file_send_address_cc_result = checkMultiDownloadFileSendAddressCc.CheckMultiDownloadFileSendAddressCc(trace_logger, request_body.multiDownloadFileSendAddressCc).get_result()
        # 01-02-20-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not check_multi_download_file_send_address_cc_result["result"]:
            [error_info_list.append(error_info) for error_info in check_multi_download_file_send_address_cc_result["errorInfo"]]

        # 01-02-21.一括削除送付先アドレスTo検証処理
        # 01-02-21-01.以下の引数で一括削除送付先アドレスTo検証処理を実行する
        check_multi_delete_file_send_address_to_result = checkMultiDeleteFileSendAddressTo.CheckMultiDeleteFileSendAddressTo(trace_logger, request_body.multiDeleteFileSendAddressTo).get_result()
        # 01-02-21-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not check_multi_delete_file_send_address_to_result["result"]:
            [error_info_list.append(error_info) for error_info in check_multi_delete_file_send_address_to_result["errorInfo"]]

        # 01-02-22.一括削除送付先アドレスCc検証処理
        # 01-02-22-01.以下の引数で一括削除送付先アドレスCc検証処理を実行する
        check_multi_delete_file_send_address_cc_result = checkMultiDeleteFileSendAddressCc.CheckMultiDeleteFileSendAddressCc(trace_logger, request_body.multiDeleteFileSendAddressCc).get_result()
        # 01-02-22-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not check_multi_delete_file_send_address_cc_result["result"]:
            [error_info_list.append(error_info) for error_info in check_multi_delete_file_send_address_cc_result["errorInfo"]]

        # 01-02-23.公開鍵送付先アドレスTo検証処理
        # 01-02-23-01.以下の引数で公開鍵送付先アドレスTo検証処理を実行する
        check_public_key_send_address_to_result = checkPublicKeySendAddressTo.CheckPublicKeySendAddressTo(trace_logger, request_body.publicKeySendAddressTo).get_result()
        # 01-02-23-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not check_public_key_send_address_to_result["result"]:
            [error_info_list.append(error_info) for error_info in check_public_key_send_address_to_result["errorInfo"]]

        # 01-02-24.公開鍵送付先アドレスCc検証処理
        # 01-02-24-01.以下の引数で公開鍵送付先アドレスCc検証処理を実行する
        check_public_key_send_address_cc_result = checkPublicKeySendAddressCc.CheckPublicKeySendAddressCc(trace_logger, request_body.publicKeySendAddressCc).get_result()
        # 01-02-24-02.「レスポンスの処理結果」がfalseの場合、「変数．エラー情報リスト」にエラー情報を追加する
        if not check_public_key_send_address_cc_result["result"]:
            [error_info_list.append(error_info) for error_info in check_public_key_send_address_cc_result["errorInfo"]]

        # 02. 終了処理
        # 02-01.レスポンス情報を作成し、返却する
        if len(error_info_list) == 0:
            # 02-01-01.「変数．エラー情報リスト」に値が設定されていない場合、下記のレスポンス情報を返却する
            return {
                "result": True
            }
        else:
            # 02-01-02.「変数．エラー情報リスト」に値が設定されていない場合、下記のレスポンス情報を返却する
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


# PDSユーザ登録API
@router.post("/api/2.0/pdsuser/regist")
async def pds_user_create(
    request: Request,
    request_body: Optional[requestBody],
    accessToken: Optional[str] = Header(""),
    timeStamp: Optional[str] = Header(""),
    jwt: str = Depends(oauth2_scheme)
):
    """
    PDSユーザ登録API

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
        common_util = CommonUtilClass(trace_logger)
        # 01. アクセストークン検証処理
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
        common_util = CommonUtilClass(trace_logger)

        # 03.パラメータ検証処理
        # 03-01.以下の引数でパラメータ検証処理を実行する
        # 03-02.パラメータ検証処理のレスポンスを変数．パラメータ検証処理実行結果に格納する
        input_check_result = input_check(trace_logger, request_body, accessToken, timeStamp)

        # 04.共通エラーチェック処理
        # 04-01.以下の引数で共通エラーチェック処理を実行する
        # 04-02.例外が発生した場合、例外処理に遷移
        if input_check_result.get("errorInfo"):
            common_util.common_error_check(input_check_result["errorInfo"])

        # 業務ロジック実施
        register_pds_user_model = pdsUserCreateModelClass(trace_logger)
        register_pds_user_model.main(request_body)

        # 33.アクセストークン発行処理
        # 33-01 以下の引数でアクセストークン発行処理を実行する
        # 33-02 アクセストークン発行処理からのレスポンスを、「変数．アクセストークン発行処理実行結果」に格納する
        token_create_response = token_util.create_token_closed(
            {
                "tfOperatorId": token_verify_response["payload"]["tfOperatorId"],
                "tfOperatorName": token_verify_response["payload"]["tfOperatorName"]
            },
            token_verify_response["payload"]["accessToken"]
        )

        # 34.共通エラーチェック処理
        # 34-01.以下の引数で共通エラーチェック処理を実行する
        # 34-02.例外が発生した場合、例外処理に遷移
        if token_create_response.get("errorInfo"):
            common_util.common_error_check(token_create_response["errorInfo"])

        # 35.終了処理
        response_content = {
            "status": "OK",
            "accessToken": token_create_response["accessToken"]
        }
        # 35-01 正常終了をCloudWatchへログ出力する
        out_logger.info(logUtil.message_build(MessageConstClass.OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP, json.dumps(response_content)))
        # 35-02 レスポンス情報整形処理
        # 35-03 処理を終了する
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
