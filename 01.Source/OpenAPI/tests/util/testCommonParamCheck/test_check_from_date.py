from fastapi.testclient import TestClient
from fastapi import Request
from app import app
from util.commonParamCheck import checkFromDate
import util.logUtil as logUtil
from const.systemConst import SystemConstClass

client = TestClient(app)

trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))


# パターン1
# 型チェックの確認
def test_check_from_date_case1():
    from_date = 1234567890
    check_from_date = checkFromDate.CheckFromDate(trace_logger, from_date)
    assert check_from_date.error_info_list[0]["errorCode"] == "020019"
    assert len(check_from_date.error_info_list) != 0
    assert check_from_date.get_result() == {
        "result": False,
        "errorInfo": check_from_date.error_info_list
    }


# パターン2
# 桁数（閾値未満）チェックの確認
def test_check_from_date_case2():
    from_date = "123456789"
    check_from_date = checkFromDate.CheckFromDate(trace_logger, from_date)
    assert check_from_date.error_info_list[0]["errorCode"] == "020014"
    assert check_from_date.error_info_list[1]["errorCode"] == "020003"
    assert len(check_from_date.error_info_list) != 0
    assert check_from_date.get_result() == {
        "result": False,
        "errorInfo": check_from_date.error_info_list
    }


# パターン3
# 桁数（閾値超過）チェックの確認
def test_check_from_date_case3():
    from_date = "12345678901"
    check_from_date = checkFromDate.CheckFromDate(trace_logger, from_date)
    assert check_from_date.error_info_list[0]["errorCode"] == "020014"
    assert check_from_date.error_info_list[1]["errorCode"] == "020003"
    assert len(check_from_date.error_info_list) != 0
    assert check_from_date.get_result() == {
        "result": False,
        "errorInfo": check_from_date.error_info_list
    }


# パターン4
# 入力規則（yyyy/MMがyyy/MMM）チェックの確認
def test_check_from_date_case4():
    from_date = "202/209/13"
    check_from_date = checkFromDate.CheckFromDate(trace_logger, from_date)
    assert check_from_date.error_info_list[0]["errorCode"] == "020003"
    assert len(check_from_date.error_info_list) != 0
    assert check_from_date.get_result() == {
        "result": False,
        "errorInfo": check_from_date.error_info_list
    }


# パターン5
# 入力規則（MM/ddがMMM/d）チェックの確認
def test_check_from_date_case5():
    from_date = "2022/0/913"
    check_from_date = checkFromDate.CheckFromDate(trace_logger, from_date)
    assert check_from_date.error_info_list[0]["errorCode"] == "020003"
    assert len(check_from_date.error_info_list) != 0
    assert check_from_date.get_result() == {
        "result": False,
        "errorInfo": check_from_date.error_info_list
    }


# パターン6
# 複合パターン（型不正、桁数不正、入力規則違反）チェックの確認
def test_check_from_date_case6():
    from_date = 12345678901
    check_from_date = checkFromDate.CheckFromDate(trace_logger, from_date)
    assert check_from_date.error_info_list[0]["errorCode"] == "020019"
    assert check_from_date.error_info_list[1]["errorCode"] == "020014"
    assert len(check_from_date.error_info_list) != 0
    assert check_from_date.get_result() == {
        "result": False,
        "errorInfo": check_from_date.error_info_list
    }


# パターン7
# 複合パターン（型不正、桁数不正、入力規則違反）チェックの確認
def test_check_from_date_case7():
    from_date = 123456789
    check_from_date = checkFromDate.CheckFromDate(trace_logger, from_date)
    assert check_from_date.error_info_list[0]["errorCode"] == "020019"
    assert check_from_date.error_info_list[1]["errorCode"] == "020014"
    assert len(check_from_date.error_info_list) != 0
    assert check_from_date.get_result() == {
        "result": False,
        "errorInfo": check_from_date.error_info_list
    }


# パターン8
# 正常系
def test_check_from_date_case8():
    from_date = "2022/09/13"
    check_from_date = checkFromDate.CheckFromDate(trace_logger, from_date)
    assert len(check_from_date.error_info_list) == 0
    assert check_from_date.get_result() == {
        "result": True
    }
