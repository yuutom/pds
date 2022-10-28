from fastapi.testclient import TestClient
from fastapi import Request
from app import app
from util.commonParamCheck import checkDataMatchMode
import util.logUtil as logUtil
from const.systemConst import SystemConstClass

client = TestClient(app)

trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))


# パターン1
# 型チェックの確認
def test_check_data_match_mode_case1():
    data_match_mode = 12345
    check_data_match_mode = checkDataMatchMode.CheckDataMatchMode(trace_logger, data_match_mode)
    assert check_data_match_mode.error_info_list[0]["errorCode"] == "020019"
    assert len(check_data_match_mode.error_info_list) != 0
    assert check_data_match_mode.get_result() == {
        "result": False,
        "errorInfo": check_data_match_mode.error_info_list
    }


# パターン2
# 入力可能文字チェックの確認
def test_check_data_match_mode_case2():
    data_match_mode = "あいうえお"
    check_data_match_mode = checkDataMatchMode.CheckDataMatchMode(trace_logger, data_match_mode)
    assert check_data_match_mode.error_info_list[0]["errorCode"] == "020020"
    assert len(check_data_match_mode.error_info_list) != 0
    assert check_data_match_mode.get_result() == {
        "result": False,
        "errorInfo": check_data_match_mode.error_info_list
    }


# パターン3
# 複合パターン（型不正、入力可能文字不正）チェックの確認
def test_check_data_match_mode_case3():
    data_match_mode = 12345
    check_data_match_mode = checkDataMatchMode.CheckDataMatchMode(trace_logger, data_match_mode)
    assert check_data_match_mode.error_info_list[0]["errorCode"] == "020019"
    assert len(check_data_match_mode.error_info_list) != 0
    assert check_data_match_mode.get_result() == {
        "result": False,
        "errorInfo": check_data_match_mode.error_info_list
    }


# パターン4
# 正常系
def test_check_data_match_mode_case4():
    data_match_mode = "前方一致"
    check_data_match_mode = checkDataMatchMode.CheckDataMatchMode(trace_logger, data_match_mode)
    assert len(check_data_match_mode.error_info_list) == 0
    assert check_data_match_mode.get_result() == {
        "result": True
    }
