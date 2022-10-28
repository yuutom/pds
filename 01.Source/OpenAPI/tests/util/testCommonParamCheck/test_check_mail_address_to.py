from fastapi.testclient import TestClient
from fastapi import Request
from app import app
from util.commonParamCheck import checkMailAddressTo
import util.logUtil as logUtil
from const.systemConst import SystemConstClass

client = TestClient(app)

trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))


# パターン1
# 未入力チェックの確認
def test_check_mail_address_to_case1():
    mail_address_to = ""
    check_mail_address_to = checkMailAddressTo.CheckMailAddressTo(trace_logger, mail_address_to)
    assert check_mail_address_to.error_info_list[0]["errorCode"] == "020001"
    assert check_mail_address_to.error_info_list[1]["errorCode"] == "020016"
    assert check_mail_address_to.error_info_list[2]["errorCode"] == "020003"
    assert len(check_mail_address_to.error_info_list) != 0
    assert check_mail_address_to.get_result() == {
        "result": False,
        "errorInfo": check_mail_address_to.error_info_list
    }


# パターン2
# 型チェックの確認
def test_check_mail_address_to_case2():
    mail_address_to = 12345
    check_mail_address_to = checkMailAddressTo.CheckMailAddressTo(trace_logger, mail_address_to)
    assert check_mail_address_to.error_info_list[0]["errorCode"] == "020019"
    assert len(check_mail_address_to.error_info_list) != 0
    assert check_mail_address_to.get_result() == {
        "result": False,
        "errorInfo": check_mail_address_to.error_info_list
    }


# パターン3
# 桁数（閾値未満）チェックの確認
def test_check_mail_address_to_case3():
    mail_address_to = "abcd"
    check_mail_address_to = checkMailAddressTo.CheckMailAddressTo(trace_logger, mail_address_to)
    assert check_mail_address_to.error_info_list[0]["errorCode"] == "020016"
    assert check_mail_address_to.error_info_list[1]["errorCode"] == "020003"
    assert len(check_mail_address_to.error_info_list) != 0
    assert check_mail_address_to.get_result() == {
        "result": False,
        "errorInfo": check_mail_address_to.error_info_list
    }


# パターン4
# 桁数（閾値超過）チェックの確認
def test_check_mail_address_to_case4():
    mail_address_to = "ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;abcdef@tf.com"
    check_mail_address_to = checkMailAddressTo.CheckMailAddressTo(trace_logger, mail_address_to)
    assert check_mail_address_to.error_info_list[0]["errorCode"] == "020002"
    assert len(check_mail_address_to.error_info_list) != 0
    assert check_mail_address_to.get_result() == {
        "result": False,
        "errorInfo": check_mail_address_to.error_info_list
    }


# パターン5
# 入力規則（@を含まない）チェックの確認
def test_check_mail_address_to_case5():
    mail_address_to = "a.com"
    check_mail_address_to = checkMailAddressTo.CheckMailAddressTo(trace_logger, mail_address_to)
    assert check_mail_address_to.error_info_list[0]["errorCode"] == "020003"
    assert len(check_mail_address_to.error_info_list) != 0
    assert check_mail_address_to.get_result() == {
        "result": False,
        "errorInfo": check_mail_address_to.error_info_list
    }


# パターン6
# 複合パターン（桁不正、入力規則不正）チェックの確認
def test_check_mail_address_to_case6():
    mail_address_to = "ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢＣＤＥＦ＠ｔｆ．ＣＯＭ"
    check_mail_address_to = checkMailAddressTo.CheckMailAddressTo(trace_logger, mail_address_to)
    assert check_mail_address_to.error_info_list[0]["errorCode"] == "020002"
    assert check_mail_address_to.error_info_list[1]["errorCode"] == "020003"
    assert len(check_mail_address_to.error_info_list) != 0
    assert check_mail_address_to.get_result() == {
        "result": False,
        "errorInfo": check_mail_address_to.error_info_list
    }


# パターン7
# 複合パターン（桁不正、入力規則不正）チェックの確認
def test_check_mail_address_to_case7():
    mail_address_to = "a@!#"
    check_mail_address_to = checkMailAddressTo.CheckMailAddressTo(trace_logger, mail_address_to)
    assert check_mail_address_to.error_info_list[0]["errorCode"] == "020016"
    assert check_mail_address_to.error_info_list[1]["errorCode"] == "020003"
    assert len(check_mail_address_to.error_info_list) != 0
    assert check_mail_address_to.get_result() == {
        "result": False,
        "errorInfo": check_mail_address_to.error_info_list
    }


# パターン8
# 正常系
def test_check_mail_address_to_case8():
    mail_address_to = "a@t.f"
    check_mail_address_to = checkMailAddressTo.CheckMailAddressTo(trace_logger, mail_address_to)
    assert len(check_mail_address_to.error_info_list) == 0
    assert check_mail_address_to.get_result() == {
        "result": True
    }


# パターン9
# 正常系
def test_check_mail_address_to_case9():
    mail_address_to = "ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;abcde@tf.com"
    check_mail_address_to = checkMailAddressTo.CheckMailAddressTo(trace_logger, mail_address_to)
    assert len(check_mail_address_to.error_info_list) == 0
    assert check_mail_address_to.get_result() == {
        "result": True
    }
