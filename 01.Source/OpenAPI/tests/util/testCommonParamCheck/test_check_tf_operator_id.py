from fastapi.testclient import TestClient
from fastapi import Request
from app import app
from util.commonParamCheck import checkTfOperatorId
import util.logUtil as logUtil
from const.systemConst import SystemConstClass

client = TestClient(app)

trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))


# パターン1
# 未入力チェックの確認
def test_check_tf_operator_id_case1():
    tf_operator_id = ""
    check_tf_operator_id = checkTfOperatorId.CheckTfOperatorId(trace_logger, tf_operator_id)
    assert check_tf_operator_id.error_info_list[0]["errorCode"] == "020001"
    assert check_tf_operator_id.error_info_list[1]["errorCode"] == "020016"
    assert len(check_tf_operator_id.error_info_list) != 0
    assert check_tf_operator_id.get_result() == {
        "result": False,
        "errorInfo": check_tf_operator_id.error_info_list
    }


# パターン2
# 型チェックの確認
def test_check_tf_operator_id_case2():
    tf_operator_id = 1234567890123456
    check_tf_operator_id = checkTfOperatorId.CheckTfOperatorId(trace_logger, tf_operator_id)
    assert check_tf_operator_id.error_info_list[0]["errorCode"] == "020019"
    assert len(check_tf_operator_id.error_info_list) != 0
    assert check_tf_operator_id.get_result() == {
        "result": False,
        "errorInfo": check_tf_operator_id.error_info_list
    }


# パターン3
# 桁数（閾値未満）チェックの確認
def test_check_tf_operator_id_case3():
    tf_operator_id = "ab"
    check_tf_operator_id = checkTfOperatorId.CheckTfOperatorId(trace_logger, tf_operator_id)
    assert check_tf_operator_id.error_info_list[0]["errorCode"] == "020016"
    assert len(check_tf_operator_id.error_info_list) != 0
    assert check_tf_operator_id.get_result() == {
        "result": False,
        "errorInfo": check_tf_operator_id.error_info_list
    }


# パターン4
# 桁数（閾値超過）チェックの確認
def test_check_tf_operator_id_case4():
    tf_operator_id = "abcdefghijklmnopq"
    check_tf_operator_id = checkTfOperatorId.CheckTfOperatorId(trace_logger, tf_operator_id)
    assert check_tf_operator_id.error_info_list[0]["errorCode"] == "020002"
    assert len(check_tf_operator_id.error_info_list) != 0
    assert check_tf_operator_id.get_result() == {
        "result": False,
        "errorInfo": check_tf_operator_id.error_info_list
    }


# パターン5
# 入力規則（全角を含む）チェックの確認
def test_check_tf_operator_id_case5():
    tf_operator_id = "abcdefghijklmnｐｑ"
    check_tf_operator_id = checkTfOperatorId.CheckTfOperatorId(trace_logger, tf_operator_id)
    assert check_tf_operator_id.error_info_list[0]["errorCode"] == "020020"
    assert len(check_tf_operator_id.error_info_list) != 0
    assert check_tf_operator_id.get_result() == {
        "result": False,
        "errorInfo": check_tf_operator_id.error_info_list
    }


# パターン6
# 複合パターン（桁不正、入力可能文字不正）チェックの確認
def test_check_tf_operator_id_case6():
    tf_operator_id = "a!"
    check_tf_operator_id = checkTfOperatorId.CheckTfOperatorId(trace_logger, tf_operator_id)
    assert check_tf_operator_id.error_info_list[0]["errorCode"] == "020016"
    assert check_tf_operator_id.error_info_list[1]["errorCode"] == "020020"
    assert len(check_tf_operator_id.error_info_list) != 0
    assert check_tf_operator_id.get_result() == {
        "result": False,
        "errorInfo": check_tf_operator_id.error_info_list
    }


# パターン7
# 複合パターン（桁不正、入力可能文字不正）チェックの確認
def test_check_tf_operator_id_case7():
    tf_operator_id = "abcdefghijklmnoｐｑ"
    check_tf_operator_id = checkTfOperatorId.CheckTfOperatorId(trace_logger, tf_operator_id)
    assert check_tf_operator_id.error_info_list[0]["errorCode"] == "020002"
    assert check_tf_operator_id.error_info_list[1]["errorCode"] == "020020"
    assert len(check_tf_operator_id.error_info_list) != 0
    assert check_tf_operator_id.get_result() == {
        "result": False,
        "errorInfo": check_tf_operator_id.error_info_list
    }


# パターン8
# 複合パターン（型不正、桁不正）チェックの確認
def test_check_tf_operator_id_case8():
    tf_operator_id = 12
    check_tf_operator_id = checkTfOperatorId.CheckTfOperatorId(trace_logger, tf_operator_id)
    assert check_tf_operator_id.error_info_list[0]["errorCode"] == "020019"
    assert check_tf_operator_id.error_info_list[1]["errorCode"] == "020016"
    assert len(check_tf_operator_id.error_info_list) != 0
    assert check_tf_operator_id.get_result() == {
        "result": False,
        "errorInfo": check_tf_operator_id.error_info_list
    }


# パターン9
# 複合パターン（型不正、桁不正）チェックの確認
def test_check_tf_operator_id_case9():
    tf_operator_id = 12345678901234567
    check_tf_operator_id = checkTfOperatorId.CheckTfOperatorId(trace_logger, tf_operator_id)
    assert check_tf_operator_id.error_info_list[0]["errorCode"] == "020019"
    assert check_tf_operator_id.error_info_list[1]["errorCode"] == "020002"
    assert len(check_tf_operator_id.error_info_list) != 0
    assert check_tf_operator_id.get_result() == {
        "result": False,
        "errorInfo": check_tf_operator_id.error_info_list
    }


# パターン10
# 正常系
def test_check_tf_operator_id_case10():
    tf_operator_id = "a-c"
    check_tf_operator_id = checkTfOperatorId.CheckTfOperatorId(trace_logger, tf_operator_id)
    assert len(check_tf_operator_id.error_info_list) == 0
    assert check_tf_operator_id.get_result() == {
        "result": True
    }


# パターン11
# 正常系
def test_check_tf_operator_id_case11():
    tf_operator_id = "abcde-+fghijklmn"
    check_tf_operator_id = checkTfOperatorId.CheckTfOperatorId(trace_logger, tf_operator_id)
    assert len(check_tf_operator_id.error_info_list) == 0
    assert check_tf_operator_id.get_result() == {
        "result": True
    }
