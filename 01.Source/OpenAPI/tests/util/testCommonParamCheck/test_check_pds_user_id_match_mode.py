from fastapi.testclient import TestClient
from fastapi import Request
from app import app
from util.commonParamCheck import checkUserIdMatchMode
import util.logUtil as logUtil
from const.systemConst import SystemConstClass

client = TestClient(app)

trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))


# パターン1
# 型チェックの確認
def test_check_user_id_match_mode_case1():
    user_id_match_mode = 12345
    check_user_id_match_mode = checkUserIdMatchMode.CheckUserIdMatchMode(trace_logger, user_id_match_mode)
    assert check_user_id_match_mode.error_info_list[0]["errorCode"] == "020019"
    assert len(check_user_id_match_mode.error_info_list) != 0
    assert check_user_id_match_mode.get_result() == {
        "result": False,
        "errorInfo": check_user_id_match_mode.error_info_list
    }


# パターン2
# 入力可能文字チェックの確認
def test_check_user_id_match_mode_case2():
    user_id_match_mode = "abcde"
    check_user_id_match_mode = checkUserIdMatchMode.CheckUserIdMatchMode(trace_logger, user_id_match_mode)
    assert check_user_id_match_mode.error_info_list[0]["errorCode"] == "020020"
    assert len(check_user_id_match_mode.error_info_list) != 0
    assert check_user_id_match_mode.get_result() == {
        "result": False,
        "errorInfo": check_user_id_match_mode.error_info_list
    }


# パターン3
# 正常系
def test_check_user_id_match_mode_case3():
    user_id_match_mode = "前方一致"
    check_user_id_match_mode = checkUserIdMatchMode.CheckUserIdMatchMode(trace_logger, user_id_match_mode)
    assert len(check_user_id_match_mode.error_info_list) == 0
    assert check_user_id_match_mode.get_result() == {
        "result": True
    }
