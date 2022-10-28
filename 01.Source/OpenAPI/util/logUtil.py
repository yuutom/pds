import logging
import sys
import json
from fastapi import Request
import util.commonUtil as commonUtil


def create_logger(logger_name: str):
    root_logger = logging.getLogger()
    logging.addLevelName(30, 'WARN')
    root_logger.setLevel(logging.INFO)
    # ログ出力先設定
    trace_sh = logging.StreamHandler(stream=sys.stdout)
    trace_sh.setLevel(logging.DEBUG)
    in_sh = logging.StreamHandler(stream=sys.stdout)
    in_sh.setLevel(logging.DEBUG)
    out_sh = logging.StreamHandler(stream=sys.stdout)
    out_sh.setLevel(logging.DEBUG)

    # ログフォーマット作成
    trace_formatter_string = '%(asctime)s.%(msecs)03d [%(levelname)s][TRC] GUID:[%(guid)s] ExecName:[%(execName)s] %(module)s:%(lineno)s %(funcName)s URL:[%(requestMethod)s-%(requestUrl)s] Param:[%(resuestParam)s] Header:[%(requestHeader)s] JwtPayload:[%(jwtPayload)s] %(message)s'
    in_formatter_string = '%(asctime)s.%(msecs)03d [%(levelname)s][IN] GUID:[%(guid)s] ExecName:[%(execName)s] %(module)s:%(lineno)s %(funcName)s URL:[%(requestMethod)s-%(requestUrl)s] Param:[%(resuestParam)s] Header:[%(requestHeader)s] JwtPayload:[%(jwtPayload)s] %(message)s'
    out_formatter_string = '%(asctime)s.%(msecs)03d [%(levelname)s][OUT] GUID:[%(guid)s] ExecName:[%(execName)s] %(module)s:%(lineno)s %(funcName)s URL:[%(requestMethod)s-%(requestUrl)s] Param:[%(resuestParam)s] Header:[%(requestHeader)s] JwtPayload:[%(jwtPayload)s] %(message)s'

    trace_fmt = logging.Formatter(trace_formatter_string)
    in_fmt = logging.Formatter(in_formatter_string)
    out_fmt = logging.Formatter(out_formatter_string)

    # ログフォーマットとハンドラの紐づけ
    trace_sh.setFormatter(trace_fmt)
    in_sh.setFormatter(in_fmt)
    out_sh.setFormatter(out_fmt)

    # ロガー作成
    trace_logger = logging.getLogger(logger_name + "Trace")
    in_logger = logging.getLogger(logger_name + "In")
    out_logger = logging.getLogger(logger_name + "Out")

    trace_logger.addHandler(trace_sh)
    in_logger.addHandler(in_sh)
    out_logger.addHandler(out_sh)


def getLogger(logger_name: str, exec_name: str, guid: str, jwt_payload: str, request_body_param: dict, request: Request):
    """
    ロガー作成処理

    Args:
        logger_name (str): ロガー名
        exec_name (str): 処理名
        guid (str): GUID
        jwt_payload (str): JWTのペイロード
        request_body_param (requestBody): リクエストボディ
        request (Request): リクエストオブジェクト

    Returns:
        Logger, Logger, Logger, str: ロガー3種類(TRACE、IN、OUT) ＋ GUID
    """
    if guid == "":
        guid = commonUtil.get_uuid()
    header_param_dict = {
        k.decode("utf-8"): v.decode("utf-8") for (k, v) in request.headers.raw
    }

    trace_logger = logging.getLogger(logger_name + "Trace")
    in_logger = logging.getLogger(logger_name + "In")
    out_logger = logging.getLogger(logger_name + "Out")

    trace_logger = logging.LoggerAdapter(
        trace_logger,
        {
            'guid': guid,
            'execName': exec_name,
            "requestMethod": request.method,
            "requestUrl": request.url._url,
            "resuestParam": json.dumps(request_body_param, ensure_ascii=False),
            "requestHeader": json.dumps(header_param_dict, ensure_ascii=False),
            "jwtPayload": jwt_payload
        }
    )
    in_logger = logging.LoggerAdapter(
        in_logger,
        {
            'guid': guid,
            'execName': exec_name,
            "requestMethod": request.method,
            "requestUrl": request.url._url,
            "resuestParam": json.dumps(request_body_param, ensure_ascii=False),
            "requestHeader": json.dumps(header_param_dict, ensure_ascii=False),
            "jwtPayload": jwt_payload
        }
    )
    out_logger = logging.LoggerAdapter(
        out_logger,
        {
            'guid': guid,
            'execName': exec_name,
            "requestMethod": request.method,
            "requestUrl": request.url._url,
            "resuestParam": json.dumps(request_body_param, ensure_ascii=False),
            "requestHeader": json.dumps(header_param_dict, ensure_ascii=False),
            "jwtPayload": jwt_payload
        }
    )

    return trace_logger, in_logger, out_logger, guid


def message_build(message: str, *args):
    """
    メッセージ作成処理

    Args:
        message (str): メッセージ
        args: 置換パラメータ

    Returns:
        str: メッセージ
    """
    if args:
        for index, item in enumerate(args):
            str_index = str(index)
            message = message.replace(f"%{str_index}", item)
    return message


def output_outlog(exec_name: str, error_info):
    if type(error_info) is list:
        if error_info[0]["errorCode"][0:2] == "99":
            return logging.ERROR
        else:
            return logging.WARNING
    elif type(error_info) is dict:
        if error_info["errorCode"][0:2] == "99":
            return logging.ERROR
        else:
            return logging.WARNING
    else:
        return logging.ERROR
