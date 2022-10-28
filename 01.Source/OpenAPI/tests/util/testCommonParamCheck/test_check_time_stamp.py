from fastapi.testclient import TestClient
from fastapi import Request
from app import app
from util.commonParamCheck import checkTimeStamp
import util.logUtil as logUtil
from const.systemConst import SystemConstClass

client = TestClient(app)

trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))


# パターン1
# 未入力チェックの確認
def test_check_time_stamp_case1():
    time_stamp = ""
    check_time_stamp = checkTimeStamp.CheckTimeStamp(trace_logger, time_stamp)
    assert check_time_stamp.error_info_list[0]["errorCode"] == "020001"
    assert check_time_stamp.error_info_list[1]["errorCode"] == "020014"
    assert check_time_stamp.error_info_list[2]["errorCode"] == "020003"
    assert len(check_time_stamp.error_info_list) != 0
    assert check_time_stamp.get_result() == {
        "result": False,
        "errorInfo": check_time_stamp.error_info_list
    }


# パターン2
# 型チェックの確認
def test_check_time_stamp_case2():
    time_stamp = 12345678901234567890123
    check_time_stamp = checkTimeStamp.CheckTimeStamp(trace_logger, time_stamp)
    assert check_time_stamp.error_info_list[0]["errorCode"] == "020019"
    assert len(check_time_stamp.error_info_list) != 0
    assert check_time_stamp.get_result() == {
        "result": False,
        "errorInfo": check_time_stamp.error_info_list
    }


# パターン3
# 桁数チェックの確認
def test_check_time_stamp_case3():
    time_stamp = "202/209/12 00:00:00.00"
    check_time_stamp = checkTimeStamp.CheckTimeStamp(trace_logger, time_stamp)
    assert check_time_stamp.error_info_list[0]["errorCode"] == "020014"
    assert check_time_stamp.error_info_list[1]["errorCode"] == "020003"
    assert len(check_time_stamp.error_info_list) != 0
    assert check_time_stamp.get_result() == {
        "result": False,
        "errorInfo": check_time_stamp.error_info_list
    }


# パターン4
# 入力規則チェックの確認
def test_check_time_stamp_case4():
    time_stamp = "2022/09/12 000:0:00.000"
    check_time_stamp = checkTimeStamp.CheckTimeStamp(trace_logger, time_stamp)
    assert check_time_stamp.error_info_list[0]["errorCode"] == "020003"
    assert len(check_time_stamp.error_info_list) != 0
    assert check_time_stamp.get_result() == {
        "result": False,
        "errorInfo": check_time_stamp.error_info_list
    }


# パターン5
# 入力規則チェックの確認
def test_check_time_stamp_case5():
    time_stamp = "2022/09/12  000:0:00.000"
    check_time_stamp = checkTimeStamp.CheckTimeStamp(trace_logger, time_stamp)
    assert check_time_stamp.error_info_list[0]["errorCode"] == "020014"
    assert check_time_stamp.error_info_list[1]["errorCode"] == "020003"
    assert len(check_time_stamp.error_info_list) != 0
    assert check_time_stamp.get_result() == {
        "result": False,
        "errorInfo": check_time_stamp.error_info_list
    }


# パターン6
# 複合パターン（桁不正、型不正）チェックの確認
def test_check_time_stamp_case6():
    time_stamp = 123456789012345678901234
    check_time_stamp = checkTimeStamp.CheckTimeStamp(trace_logger, time_stamp)
    assert check_time_stamp.error_info_list[0]["errorCode"] == "020019"
    assert check_time_stamp.error_info_list[1]["errorCode"] == "020014"
    assert len(check_time_stamp.error_info_list) != 0
    assert check_time_stamp.get_result() == {
        "result": False,
        "errorInfo": check_time_stamp.error_info_list
    }


# パターン7
# 正常系
def test_check_time_stamp_case7():
    time_stamp = "2022/09/12 00:00:00.000"
    check_time_stamp = checkTimeStamp.CheckTimeStamp(trace_logger, time_stamp)
    assert len(check_time_stamp.error_info_list) == 0
    assert check_time_stamp.get_result() == {
        "result": True
    }
