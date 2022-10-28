from fastapi.testclient import TestClient
from fastapi import Request
from app import app
from util.commonParamCheck import checkAccessToken
import util.logUtil as logUtil
from const.systemConst import SystemConstClass

client = TestClient(app)

trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))


# パターン1
# 未入力チェックの確認
def test_check_access_token_case1():
    access_token = ""
    check_access_token = checkAccessToken.CheckAccessToken(trace_logger, access_token)
    assert check_access_token.error_info_list[0]["errorCode"] == "020001"
    assert check_access_token.error_info_list[1]["errorCode"] == "020014"
    assert check_access_token.error_info_list[2]["errorCode"] == "020003"
    assert len(check_access_token.error_info_list) != 0
    assert check_access_token.get_result() == {
        "result": False,
        "errorInfo": check_access_token.error_info_list
    }


# パターン2
# 型チェックの確認
def test_check_access_token_case2():
    access_token = 12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
    check_access_token = checkAccessToken.CheckAccessToken(trace_logger, access_token)
    assert check_access_token.error_info_list[0]["errorCode"] == "020019"
    assert len(check_access_token.error_info_list) != 0
    assert check_access_token.get_result() == {
        "result": False,
        "errorInfo": check_access_token.error_info_list
    }


# パターン3
# 桁数チェックの確認
def test_check_access_token_case3():
    access_token = "abcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwx"
    check_access_token = checkAccessToken.CheckAccessToken(trace_logger, access_token)
    assert check_access_token.error_info_list[0]["errorCode"] == "020014"
    assert check_access_token.error_info_list[1]["errorCode"] == "020003"
    assert len(check_access_token.error_info_list) != 0
    assert check_access_token.get_result() == {
        "result": False,
        "errorInfo": check_access_token.error_info_list
    }


# パターン4
# 桁数チェックの確認
def test_check_access_token_case4():
    access_token = "abcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyz"
    check_access_token = checkAccessToken.CheckAccessToken(trace_logger, access_token)
    assert check_access_token.error_info_list[0]["errorCode"] == "020014"
    assert check_access_token.error_info_list[1]["errorCode"] == "020003"
    assert len(check_access_token.error_info_list) != 0
    assert check_access_token.get_result() == {
        "result": False,
        "errorInfo": check_access_token.error_info_list
    }


# パターン5
# 入力可能文字チェックの確認
def test_check_access_token_case5():
    access_token = "abcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwx/"
    print(len(access_token))
    check_access_token = checkAccessToken.CheckAccessToken(trace_logger, access_token)
    assert check_access_token.error_info_list[0]["errorCode"] == "020003"
    assert len(check_access_token.error_info_list) != 0
    assert check_access_token.get_result() == {
        "result": False,
        "errorInfo": check_access_token.error_info_list
    }


# パターン6
# 複合パターン（桁不正、入力可能文字）チェックの確認
def test_check_access_token_case6():
    access_token = "abcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvw・"
    check_access_token = checkAccessToken.CheckAccessToken(trace_logger, access_token)
    assert check_access_token.error_info_list[0]["errorCode"] == "020014"
    assert check_access_token.error_info_list[1]["errorCode"] == "020003"
    assert len(check_access_token.error_info_list) != 0
    assert check_access_token.get_result() == {
        "result": False,
        "errorInfo": check_access_token.error_info_list
    }


# パターン7
# 複合パターン（型不正、桁不正）チェックの確認
def test_check_access_token_case7():
    access_token = 1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789
    check_access_token = checkAccessToken.CheckAccessToken(trace_logger, access_token)
    assert check_access_token.error_info_list[0]["errorCode"] == "020019"
    assert check_access_token.error_info_list[1]["errorCode"] == "020014"
    assert len(check_access_token.error_info_list) != 0
    assert check_access_token.get_result() == {
        "result": False,
        "errorInfo": check_access_token.error_info_list
    }


# パターン8
# 正常系
def test_check_access_token_case8():
    access_token = "b47c1bd08140b355a2ee408ed05abfd10ef38fdb611e6fd90f4ec8301e145291ec33a9280c818ab09e0a96908a59b8aea16417eeb5d5f6af34903aee732d8e372e9e0114b4c35a028115cdc30531d9ae35b015194c10eae1584f71536f4c1c2c30b66b5a"
    check_access_token = checkAccessToken.CheckAccessToken(trace_logger, access_token)
    assert len(check_access_token.error_info_list) == 0
    assert check_access_token.get_result() == {
        "result": True
    }
