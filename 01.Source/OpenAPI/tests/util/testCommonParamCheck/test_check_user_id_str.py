from fastapi.testclient import TestClient
from fastapi import Request
from app import app
from util.commonParamCheck import checkUserIdStr
import util.logUtil as logUtil
from const.systemConst import SystemConstClass

client = TestClient(app)

trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))


# パターン1
# 型チェックの確認
def test_check_user_id_str_case1():
    user_id_str = 123456789012345678901234567890123456
    check_user_id_str = checkUserIdStr.CheckUserIdStr(trace_logger, user_id_str)
    assert check_user_id_str.error_info_list[0]["errorCode"] == "020019"
    assert len(check_user_id_str.error_info_list) != 0
    assert check_user_id_str.get_result() == {
        "result": False,
        "errorInfo": check_user_id_str.error_info_list
    }


# パターン2
# 桁数（閾値超過）チェックの確認
def test_check_user_id_str_case2():
    user_id_str = "abcdefghijklmnopqrstuvwxyzabcdefghijk"
    check_user_id_str = checkUserIdStr.CheckUserIdStr(trace_logger, user_id_str)
    assert check_user_id_str.error_info_list[0]["errorCode"] == "020002"
    assert len(check_user_id_str.error_info_list) != 0
    assert check_user_id_str.get_result() == {
        "result": False,
        "errorInfo": check_user_id_str.error_info_list
    }


# パターン3
# 複合パターン（型不正、桁不正）チェックの確認
def test_check_user_id_str_case3():
    user_id_str = 1234567890123456789012345678901234567
    check_user_id_str = checkUserIdStr.CheckUserIdStr(trace_logger, user_id_str)
    assert check_user_id_str.error_info_list[0]["errorCode"] == "020019"
    assert check_user_id_str.error_info_list[1]["errorCode"] == "020002"
    assert len(check_user_id_str.error_info_list) != 0
    assert check_user_id_str.get_result() == {
        "result": False,
        "errorInfo": check_user_id_str.error_info_list
    }


# パターン4
# 正常系
def test_check_user_id_str_case4():
    user_id_str = "abcdefghijklmnopqrstuvwxyzabcdefghij"
    check_user_id_str = checkUserIdStr.CheckUserIdStr(trace_logger, user_id_str)
    assert len(check_user_id_str.error_info_list) == 0
    assert check_user_id_str.get_result() == {
        "result": True
    }
