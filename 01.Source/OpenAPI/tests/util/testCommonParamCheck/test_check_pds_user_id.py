from fastapi.testclient import TestClient
from fastapi import Request
from app import app
from util.commonParamCheck import checkPdsUserId
import util.logUtil as logUtil
from const.systemConst import SystemConstClass

client = TestClient(app)

trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))


# パターン1
# 未入力チェックの確認
def test_check_pds_user_id_case1():
    pds_user_id = ""
    check_pds_user_id = checkPdsUserId.CheckPdsUserId(trace_logger, pds_user_id)
    assert check_pds_user_id.error_info_list[0]["errorCode"] == "020001"
    assert len(check_pds_user_id.error_info_list) != 0
    assert check_pds_user_id.get_result() == {
        "result": False,
        "errorInfo": check_pds_user_id.error_info_list
    }


# パターン2
# 型チェックの確認
def test_check_pds_user_id_case2():
    pds_user_id = 12345678
    check_pds_user_id = checkPdsUserId.CheckPdsUserId(trace_logger, pds_user_id)
    assert check_pds_user_id.error_info_list[0]["errorCode"] == "020019"
    assert len(check_pds_user_id.error_info_list) != 0
    assert check_pds_user_id.get_result() == {
        "result": False,
        "errorInfo": check_pds_user_id.error_info_list
    }


# TODO: 020003も出る
# ANS：020003も出てよい。テスト仕様書の結果不備
# パターン3
# 桁数（閾値未満）チェックの確認
def test_check_pds_user_id_case3():
    pds_user_id = "abcdefg"
    check_pds_user_id = checkPdsUserId.CheckPdsUserId(trace_logger, pds_user_id)
    assert check_pds_user_id.error_info_list[0]["errorCode"] == "020014"
    assert check_pds_user_id.error_info_list[1]["errorCode"] == "020003"
    assert len(check_pds_user_id.error_info_list) != 0
    assert check_pds_user_id.get_result() == {
        "result": False,
        "errorInfo": check_pds_user_id.error_info_list
    }


# TODO: 020003も出る
# ANS：020003も出てよい。テスト仕様書の結果不備
# パターン4
# 桁数（閾値超過）チェックの確認
def test_check_pds_user_id_case4():
    pds_user_id = "abcdefghi"
    check_pds_user_id = checkPdsUserId.CheckPdsUserId(trace_logger, pds_user_id)
    assert check_pds_user_id.error_info_list[0]["errorCode"] == "020014"
    assert check_pds_user_id.error_info_list[1]["errorCode"] == "020003"
    assert len(check_pds_user_id.error_info_list) != 0
    assert check_pds_user_id.get_result() == {
        "result": False,
        "errorInfo": check_pds_user_id.error_info_list
    }


# パターン5
# 入力規則（頭文字）チェックの確認
def test_check_pds_user_id_case5():
    pds_user_id = "X1234567"
    check_pds_user_id = checkPdsUserId.CheckPdsUserId(trace_logger, pds_user_id)
    assert check_pds_user_id.error_info_list[0]["errorCode"] == "020003"
    assert len(check_pds_user_id.error_info_list) != 0
    assert check_pds_user_id.get_result() == {
        "result": False,
        "errorInfo": check_pds_user_id.error_info_list
    }


# TODO: 020014も出る
# ANS：020014も出てよい。テスト仕様書の結果不備
# TODO: 8桁であることと両立不可
# ANS：7桁にする。テスト仕様書の条件不備
# パターン6
# 入力規則（数値個数未満）チェックの確認
def test_check_pds_user_id_case6():
    pds_user_id = "C123456"
    check_pds_user_id = checkPdsUserId.CheckPdsUserId(trace_logger, pds_user_id)
    assert check_pds_user_id.error_info_list[0]["errorCode"] == "020014"
    assert check_pds_user_id.error_info_list[1]["errorCode"] == "020003"
    assert len(check_pds_user_id.error_info_list) != 0
    assert check_pds_user_id.get_result() == {
        "result": False,
        "errorInfo": check_pds_user_id.error_info_list
    }


# TODO: 020014も出る
# ANS：020014も出てよい。テスト仕様書の結果不備
# TODO: 8桁であることと両立不可
# ANS：9桁にする。テスト仕様書の条件不備
# パターン7
# 入力規則（数値個数超過）チェックの確認
def test_check_pds_user_id_case7():
    pds_user_id = "C12345678"
    check_pds_user_id = checkPdsUserId.CheckPdsUserId(trace_logger, pds_user_id)
    assert check_pds_user_id.error_info_list[0]["errorCode"] == "020014"
    assert check_pds_user_id.error_info_list[1]["errorCode"] == "020003"
    assert len(check_pds_user_id.error_info_list) != 0
    assert check_pds_user_id.get_result() == {
        "result": False,
        "errorInfo": check_pds_user_id.error_info_list
    }


# パターン8
# 入力規則（数値なし）チェックの確認
def test_check_pds_user_id_case8():
    pds_user_id = "Cabcsefg"
    check_pds_user_id = checkPdsUserId.CheckPdsUserId(trace_logger, pds_user_id)
    assert check_pds_user_id.error_info_list[0]["errorCode"] == "020003"
    assert len(check_pds_user_id.error_info_list) != 0
    assert check_pds_user_id.get_result() == {
        "result": False,
        "errorInfo": check_pds_user_id.error_info_list
    }


# パターン9
# 複合パターン（桁不正、入力規則不正）チェックの確認
# ※複合パターンは、エラー情報リストがappendされており、置換になっていないことも確認すること
def test_check_pds_user_id_case9():
    pds_user_id = "Cabcsef"
    check_pds_user_id = checkPdsUserId.CheckPdsUserId(trace_logger, pds_user_id)
    assert check_pds_user_id.error_info_list[0]["errorCode"] == "020014"
    assert check_pds_user_id.error_info_list[1]["errorCode"] == "020003"
    assert len(check_pds_user_id.error_info_list) != 0
    assert check_pds_user_id.get_result() == {
        "result": False,
        "errorInfo": check_pds_user_id.error_info_list
    }


# パターン10
# 複合パターン（型不正、桁不正）チェックの確認
# ※複合パターンは、エラー情報リストがappendされており、置換になっていないことも確認すること
def test_check_pds_user_id_case10():
    pds_user_id = 1234567
    check_pds_user_id = checkPdsUserId.CheckPdsUserId(trace_logger, pds_user_id)
    assert check_pds_user_id.error_info_list[0]["errorCode"] == "020019"
    assert check_pds_user_id.error_info_list[1]["errorCode"] == "020014"
    assert len(check_pds_user_id.error_info_list) != 0
    assert check_pds_user_id.get_result() == {
        "result": False,
        "errorInfo": check_pds_user_id.error_info_list
    }


# パターン11
# 正常系
def test_check_pds_user_id_case11():
    pds_user_id = "C1234567"
    check_pds_user_id = checkPdsUserId.CheckPdsUserId(trace_logger, pds_user_id)
    assert len(check_pds_user_id.error_info_list) == 0
    assert check_pds_user_id.get_result() == {
        "result": True
    }
