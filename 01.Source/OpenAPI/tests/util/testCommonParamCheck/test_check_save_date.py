from fastapi.testclient import TestClient
from fastapi import Request
from app import app
from util.commonParamCheck import checkSaveDate
import util.logUtil as logUtil
from const.systemConst import SystemConstClass

client = TestClient(app)

trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))


# パターン1
# 型チェックの確認
def test_check_save_date_case1():
    save_date = 12345678901234567890123
    check_save_date = checkSaveDate.CheckSaveDate(trace_logger, save_date)
    assert check_save_date.error_info_list[0]["errorCode"] == "020019"
    assert len(check_save_date.error_info_list) != 0
    assert check_save_date.get_result() == {
        "result": False,
        "errorInfo": check_save_date.error_info_list
    }


# パターン2
# 桁数チェックの確認
def test_check_save_date_case2():
    save_date = "2022/09/13 00:00:00.00"
    check_save_date = checkSaveDate.CheckSaveDate(trace_logger, save_date)
    assert check_save_date.error_info_list[0]["errorCode"] == "020014"
    assert check_save_date.error_info_list[1]["errorCode"] == "020003"
    assert len(check_save_date.error_info_list) != 0
    assert check_save_date.get_result() == {
        "result": False,
        "errorInfo": check_save_date.error_info_list
    }


# パターン3
# 桁数チェックの確認
def test_check_save_date_case3():
    save_date = "2022/09/13 000:0:00.0000"
    check_save_date = checkSaveDate.CheckSaveDate(trace_logger, save_date)
    assert check_save_date.error_info_list[0]["errorCode"] == "020014"
    assert check_save_date.error_info_list[1]["errorCode"] == "020003"
    assert len(check_save_date.error_info_list) != 0
    assert check_save_date.get_result() == {
        "result": False,
        "errorInfo": check_save_date.error_info_list
    }


# パターン4
# 入力規則チェックの確認
def test_check_save_date_case4():
    save_date = "202/209/13 00:00:00.000"
    check_save_date = checkSaveDate.CheckSaveDate(trace_logger, save_date)
    assert check_save_date.error_info_list[0]["errorCode"] == "020003"
    assert len(check_save_date.error_info_list) != 0
    assert check_save_date.get_result() == {
        "result": False,
        "errorInfo": check_save_date.error_info_list
    }


# パターン5
# 入力規則チェックの確認
def test_check_save_date_case5():
    save_date = "202/209/13 00:00:000.00"
    check_save_date = checkSaveDate.CheckSaveDate(trace_logger, save_date)
    assert check_save_date.error_info_list[0]["errorCode"] == "020003"
    assert len(check_save_date.error_info_list) != 0
    assert check_save_date.get_result() == {
        "result": False,
        "errorInfo": check_save_date.error_info_list
    }


# パターン6
# 複合パターン（型不正、桁不正、入力規則）チェックの確認
def test_check_save_date_case6():
    save_date = 123456789012345678901234
    check_save_date = checkSaveDate.CheckSaveDate(trace_logger, save_date)
    assert check_save_date.error_info_list[0]["errorCode"] == "020019"
    assert check_save_date.error_info_list[1]["errorCode"] == "020014"
    assert len(check_save_date.error_info_list) != 0
    assert check_save_date.get_result() == {
        "result": False,
        "errorInfo": check_save_date.error_info_list
    }


# パターン7
# 複合パターン（型不正、桁不正、入力規則）チェックの確認
def test_check_save_date_case7():
    save_date = 1234567890123456789012
    check_save_date = checkSaveDate.CheckSaveDate(trace_logger, save_date)
    assert check_save_date.error_info_list[0]["errorCode"] == "020019"
    assert check_save_date.error_info_list[1]["errorCode"] == "020014"
    assert len(check_save_date.error_info_list) != 0
    assert check_save_date.get_result() == {
        "result": False,
        "errorInfo": check_save_date.error_info_list
    }


# パターン8
# 正常系
def test_check_save_date_case8():
    save_date = "2022/09/12 00:00:00.000"
    check_save_date = checkSaveDate.CheckSaveDate(trace_logger, save_date)
    assert len(check_save_date.error_info_list) == 0
    assert check_save_date.get_result() == {
        "result": True
    }
