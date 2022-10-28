from fastapi.testclient import TestClient
from fastapi import Request
from app import app
from util.commonParamCheck import checkTfOperatorMail
import util.logUtil as logUtil
from const.systemConst import SystemConstClass

client = TestClient(app)

trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))


# パターン1
# 未入力チェックの確認
def test_check_tf_operator_mail_case1():
    tf_operator_mail = ""
    check_tf_operator_mail = checkTfOperatorMail.CheckTfOperatorMail(trace_logger, tf_operator_mail)
    assert check_tf_operator_mail.error_info_list[0]["errorCode"] == "020001"
    assert check_tf_operator_mail.error_info_list[1]["errorCode"] == "020016"
    assert check_tf_operator_mail.error_info_list[2]["errorCode"] == "020003"
    assert len(check_tf_operator_mail.error_info_list) != 0
    assert check_tf_operator_mail.get_result() == {
        "result": False,
        "errorInfo": check_tf_operator_mail.error_info_list
    }


# パターン2
# 型チェックの確認
def test_check_tf_operator_mail_case2():
    tf_operator_mail = 12345
    check_tf_operator_mail = checkTfOperatorMail.CheckTfOperatorMail(trace_logger, tf_operator_mail)
    assert check_tf_operator_mail.error_info_list[0]["errorCode"] == "020019"
    assert len(check_tf_operator_mail.error_info_list) != 0
    assert check_tf_operator_mail.get_result() == {
        "result": False,
        "errorInfo": check_tf_operator_mail.error_info_list
    }


# パターン3
# 桁数（閾値未満）チェックの確認
def test_check_tf_operator_mail_case3():
    tf_operator_mail = "abcd"
    check_tf_operator_mail = checkTfOperatorMail.CheckTfOperatorMail(trace_logger, tf_operator_mail)
    assert check_tf_operator_mail.error_info_list[0]["errorCode"] == "020016"
    assert check_tf_operator_mail.error_info_list[1]["errorCode"] == "020003"
    assert len(check_tf_operator_mail.error_info_list) != 0
    assert check_tf_operator_mail.get_result() == {
        "result": False,
        "errorInfo": check_tf_operator_mail.error_info_list
    }


# パターン4
# 桁数（閾値超過）チェックの確認
def test_check_tf_operator_mail_case4():
    tf_operator_mail = "abcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwx@abc.com"
    check_tf_operator_mail = checkTfOperatorMail.CheckTfOperatorMail(trace_logger, tf_operator_mail)
    assert check_tf_operator_mail.error_info_list[0]["errorCode"] == "020002"
    assert len(check_tf_operator_mail.error_info_list) != 0
    assert check_tf_operator_mail.get_result() == {
        "result": False,
        "errorInfo": check_tf_operator_mail.error_info_list
    }


# パターン5
# 入力規則（半角大英字を含む）チェックの確認
def test_check_tf_operator_mail_case5():
    tf_operator_mail = "abcde"
    check_tf_operator_mail = checkTfOperatorMail.CheckTfOperatorMail(trace_logger, tf_operator_mail)
    assert check_tf_operator_mail.error_info_list[0]["errorCode"] == "020003"
    assert len(check_tf_operator_mail.error_info_list) != 0
    assert check_tf_operator_mail.get_result() == {
        "result": False,
        "errorInfo": check_tf_operator_mail.error_info_list
    }


# パターン6
# 入力規則（全角を含む）チェックの確認
def test_check_tf_operator_mail_case6():
    tf_operator_mail = "abcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvxy@abc.ＣＯＭ"
    check_tf_operator_mail = checkTfOperatorMail.CheckTfOperatorMail(trace_logger, tf_operator_mail)
    assert check_tf_operator_mail.error_info_list[0]["errorCode"] == "020002"
    assert check_tf_operator_mail.error_info_list[1]["errorCode"] == "020003"
    assert len(check_tf_operator_mail.error_info_list) != 0
    assert check_tf_operator_mail.get_result() == {
        "result": False,
        "errorInfo": check_tf_operator_mail.error_info_list
    }


# パターン7
# 複合パターン（桁不正、型不正）チェックの確認
def test_check_tf_operator_mail_case7():
    tf_operator_mail = 1234
    check_tf_operator_mail = checkTfOperatorMail.CheckTfOperatorMail(trace_logger, tf_operator_mail)
    assert check_tf_operator_mail.error_info_list[0]["errorCode"] == "020019"
    assert check_tf_operator_mail.error_info_list[1]["errorCode"] == "020016"
    assert len(check_tf_operator_mail.error_info_list) != 0
    assert check_tf_operator_mail.get_result() == {
        "result": False,
        "errorInfo": check_tf_operator_mail.error_info_list
    }


# パターン8
# 正常系
def test_check_tf_operator_mail_case8():
    tf_operator_mail = "a@b.c"
    check_tf_operator_mail = checkTfOperatorMail.CheckTfOperatorMail(trace_logger, tf_operator_mail)
    assert len(check_tf_operator_mail.error_info_list) == 0
    assert check_tf_operator_mail.get_result() == {
        "result": True
    }


# パターン9
# 正常系
def test_check_tf_operator_mail_case9():
    tf_operator_mail = "abcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuvwxyabcdefghijklmnopqrstuv@abc.com"
    check_tf_operator_mail = checkTfOperatorMail.CheckTfOperatorMail(trace_logger, tf_operator_mail)
    assert len(check_tf_operator_mail.error_info_list) == 0
    assert check_tf_operator_mail.get_result() == {
        "result": True
    }
