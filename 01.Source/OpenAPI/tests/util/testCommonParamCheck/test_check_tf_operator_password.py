from fastapi.testclient import TestClient
from fastapi import Request
from app import app
from util.commonParamCheck import checkTfOperatorPassword
import util.logUtil as logUtil
from const.systemConst import SystemConstClass

client = TestClient(app)

trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))


# パターン1
# 未入力チェックの確認
def test_check_tf_operator_password_case1():
    tf_operator_password = ""
    check_tf_operator_password = checkTfOperatorPassword.CheckTfOperatorPassword(trace_logger, tf_operator_password)
    assert check_tf_operator_password.error_info_list[0]["errorCode"] == "020001"
    assert check_tf_operator_password.error_info_list[1]["errorCode"] == "020016"
    assert check_tf_operator_password.error_info_list[2]["errorCode"] == "020010"
    assert len(check_tf_operator_password.error_info_list) != 0
    assert check_tf_operator_password.get_result() == {
        "result": False,
        "errorInfo": check_tf_operator_password.error_info_list
    }


# パターン2
# 型チェックの確認
def test_check_tf_operator_password_case2():
    tf_operator_password = 12345678
    check_tf_operator_password = checkTfOperatorPassword.CheckTfOperatorPassword(trace_logger, tf_operator_password)
    assert check_tf_operator_password.error_info_list[0]["errorCode"] == "020019"
    assert len(check_tf_operator_password.error_info_list) != 0
    assert check_tf_operator_password.get_result() == {
        "result": False,
        "errorInfo": check_tf_operator_password.error_info_list
    }


# パターン3
# 桁数（閾値未満）チェックの確認
def test_check_tf_operator_password_case3():
    tf_operator_password = "pa5swo!"
    check_tf_operator_password = checkTfOperatorPassword.CheckTfOperatorPassword(trace_logger, tf_operator_password)
    assert check_tf_operator_password.error_info_list[0]["errorCode"] == "020016"
    assert len(check_tf_operator_password.error_info_list) != 0
    assert check_tf_operator_password.get_result() == {
        "result": False,
        "errorInfo": check_tf_operator_password.error_info_list
    }


# パターン4
# 桁数（閾値超過）チェックの確認
def test_check_tf_operator_password_case4():
    tf_operator_password = "Ab0defghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrst"
    check_tf_operator_password = checkTfOperatorPassword.CheckTfOperatorPassword(trace_logger, tf_operator_password)
    assert check_tf_operator_password.error_info_list[0]["errorCode"] == "020002"
    assert len(check_tf_operator_password.error_info_list) != 0
    assert check_tf_operator_password.get_result() == {
        "result": False,
        "errorInfo": check_tf_operator_password.error_info_list
    }


# パターン5
# 入力規則（全角を含む）チェックの確認
def test_check_tf_operator_password_case5():
    tf_operator_password = "Ab0defghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqｒｓ"
    check_tf_operator_password = checkTfOperatorPassword.CheckTfOperatorPassword(trace_logger, tf_operator_password)
    assert check_tf_operator_password.error_info_list[0]["errorCode"] == "020020"
    assert len(check_tf_operator_password.error_info_list) != 0
    assert check_tf_operator_password.get_result() == {
        "result": False,
        "errorInfo": check_tf_operator_password.error_info_list
    }


# パターン6
# 入力規則（入力可能文字以外が含まれる）チェックの確認
def test_check_tf_operator_password_case6():
    tf_operator_password = "pA5swo?%"
    check_tf_operator_password = checkTfOperatorPassword.CheckTfOperatorPassword(trace_logger, tf_operator_password)
    assert check_tf_operator_password.error_info_list[0]["errorCode"] == "020020"
    assert len(check_tf_operator_password.error_info_list) != 0
    assert check_tf_operator_password.get_result() == {
        "result": False,
        "errorInfo": check_tf_operator_password.error_info_list
    }


# パターン7
# 英大文字、英小文字、数字、記号のうち３種類以上チェックの確認
def test_check_tf_operator_password_case7():
    tf_operator_password = "abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrs"
    check_tf_operator_password = checkTfOperatorPassword.CheckTfOperatorPassword(trace_logger, tf_operator_password)
    assert check_tf_operator_password.error_info_list[0]["errorCode"] == "020010"
    assert len(check_tf_operator_password.error_info_list) != 0
    assert check_tf_operator_password.get_result() == {
        "result": False,
        "errorInfo": check_tf_operator_password.error_info_list
    }


# パターン8
# 複合パターン（入力可能文字不正、種類数不正）チェックの確認
def test_check_tf_operator_password_case8():
    tf_operator_password = "?bcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrs"
    check_tf_operator_password = checkTfOperatorPassword.CheckTfOperatorPassword(trace_logger, tf_operator_password)
    assert check_tf_operator_password.error_info_list[0]["errorCode"] == "020020"
    assert check_tf_operator_password.error_info_list[1]["errorCode"] == "020010"
    assert len(check_tf_operator_password.error_info_list) != 0
    assert check_tf_operator_password.get_result() == {
        "result": False,
        "errorInfo": check_tf_operator_password.error_info_list
    }


# パターン9
# 複合パターン（型不正、桁不正）チェックの確認
def test_check_tf_operator_password_case9():
    tf_operator_password = 123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678
    check_tf_operator_password = checkTfOperatorPassword.CheckTfOperatorPassword(trace_logger, tf_operator_password)
    assert check_tf_operator_password.error_info_list[0]["errorCode"] == "020019"
    assert check_tf_operator_password.error_info_list[1]["errorCode"] == "020002"
    assert len(check_tf_operator_password.error_info_list) != 0
    assert check_tf_operator_password.get_result() == {
        "result": False,
        "errorInfo": check_tf_operator_password.error_info_list
    }


# パターン10
# 複合パターン（型不正、桁不正）チェックの確認
def test_check_tf_operator_password_case10():
    tf_operator_password = 1234567
    check_tf_operator_password = checkTfOperatorPassword.CheckTfOperatorPassword(trace_logger, tf_operator_password)
    assert check_tf_operator_password.error_info_list[0]["errorCode"] == "020019"
    assert check_tf_operator_password.error_info_list[1]["errorCode"] == "020016"
    assert len(check_tf_operator_password.error_info_list) != 0
    assert check_tf_operator_password.get_result() == {
        "result": False,
        "errorInfo": check_tf_operator_password.error_info_list
    }


# パターン11
# 複合パターン（桁不正、入力可能文字不正、種類数不正）チェックの確認
def test_check_tf_operator_password_case11():
    tf_operator_password = "abcd?<g"
    check_tf_operator_password = checkTfOperatorPassword.CheckTfOperatorPassword(trace_logger, tf_operator_password)
    assert check_tf_operator_password.error_info_list[0]["errorCode"] == "020016"
    assert check_tf_operator_password.error_info_list[1]["errorCode"] == "020020"
    assert check_tf_operator_password.error_info_list[2]["errorCode"] == "020010"
    assert len(check_tf_operator_password.error_info_list) != 0
    assert check_tf_operator_password.get_result() == {
        "result": False,
        "errorInfo": check_tf_operator_password.error_info_list
    }


# パターン12
# 複合パターン（桁不正、入力可能文字不正、種類数不正）チェックの確認
def test_check_tf_operator_password_case12():
    tf_operator_password = "?b>defghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrst"
    check_tf_operator_password = checkTfOperatorPassword.CheckTfOperatorPassword(trace_logger, tf_operator_password)
    assert check_tf_operator_password.error_info_list[0]["errorCode"] == "020002"
    assert check_tf_operator_password.error_info_list[1]["errorCode"] == "020020"
    assert check_tf_operator_password.error_info_list[2]["errorCode"] == "020010"
    assert len(check_tf_operator_password.error_info_list) != 0
    assert check_tf_operator_password.get_result() == {
        "result": False,
        "errorInfo": check_tf_operator_password.error_info_list
    }


# パターン13
# 正常系
def test_check_tf_operator_password_case13():
    tf_operator_password = "A5-defghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrs"
    check_tf_operator_password = checkTfOperatorPassword.CheckTfOperatorPassword(trace_logger, tf_operator_password)
    assert len(check_tf_operator_password.error_info_list) == 0
    assert check_tf_operator_password.get_result() == {
        "result": True
    }


# パターン14
# 正常系
def test_check_tf_operator_password_case14():
    tf_operator_password = "ab@D4fgh"
    check_tf_operator_password = checkTfOperatorPassword.CheckTfOperatorPassword(trace_logger, tf_operator_password)
    assert len(check_tf_operator_password.error_info_list) == 0
    assert check_tf_operator_password.get_result() == {
        "result": True
    }
