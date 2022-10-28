from fastapi.testclient import TestClient
from fastapi import Request
from app import app
from util.commonParamCheck import checkApprovalUserId
import util.logUtil as logUtil
from const.systemConst import SystemConstClass

client = TestClient(app)

trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))


# パターン1
# 未入力チェックの確認
def test_check_approval_user_id_case1():
    approval_user_id = ""
    check_approval_user_id = checkApprovalUserId.CheckApprovalUserId(trace_logger, approval_user_id)
    assert check_approval_user_id.error_info_list[0]["errorCode"] == "020001"
    assert check_approval_user_id.error_info_list[1]["errorCode"] == "020016"
    assert len(check_approval_user_id.error_info_list) != 0
    assert check_approval_user_id.get_result() == {
        "result": False,
        "errorInfo": check_approval_user_id.error_info_list
    }


# パターン2
# 型チェックの確認
def test_check_approval_user_id_case2():
    approval_user_id = 1234567890123456
    check_approval_user_id = checkApprovalUserId.CheckApprovalUserId(trace_logger, approval_user_id)
    assert check_approval_user_id.error_info_list[0]["errorCode"] == "020019"
    assert len(check_approval_user_id.error_info_list) != 0
    assert check_approval_user_id.get_result() == {
        "result": False,
        "errorInfo": check_approval_user_id.error_info_list
    }


# パターン3
# 桁数（閾値未満）チェックの確認
def test_check_approval_user_id_case3():
    approval_user_id = "ab"
    check_approval_user_id = checkApprovalUserId.CheckApprovalUserId(trace_logger, approval_user_id)
    assert check_approval_user_id.error_info_list[0]["errorCode"] == "020016"
    assert len(check_approval_user_id.error_info_list) != 0
    assert check_approval_user_id.get_result() == {
        "result": False,
        "errorInfo": check_approval_user_id.error_info_list
    }


# パターン4
# 桁数（閾値超過）チェックの確認
def test_check_approval_user_id_case4():
    approval_user_id = "abcdefghijklmnopq"
    check_approval_user_id = checkApprovalUserId.CheckApprovalUserId(trace_logger, approval_user_id)
    assert check_approval_user_id.error_info_list[0]["errorCode"] == "020002"
    assert len(check_approval_user_id.error_info_list) != 0
    assert check_approval_user_id.get_result() == {
        "result": False,
        "errorInfo": check_approval_user_id.error_info_list
    }


# パターン5
# 入力規則（全角を含む）チェックの確認
def test_check_approval_user_id_case5():
    approval_user_id = "abcdefghijklmnｐｑ"
    check_approval_user_id = checkApprovalUserId.CheckApprovalUserId(trace_logger, approval_user_id)
    assert check_approval_user_id.error_info_list[0]["errorCode"] == "020020"
    assert len(check_approval_user_id.error_info_list) != 0
    assert check_approval_user_id.get_result() == {
        "result": False,
        "errorInfo": check_approval_user_id.error_info_list
    }


# パターン6
# 複合パターン（桁不正、入力可能文字不正）チェックの確認
def test_check_approval_user_id_case6():
    approval_user_id = "a!"
    check_approval_user_id = checkApprovalUserId.CheckApprovalUserId(trace_logger, approval_user_id)
    assert check_approval_user_id.error_info_list[0]["errorCode"] == "020016"
    assert check_approval_user_id.error_info_list[1]["errorCode"] == "020020"
    assert len(check_approval_user_id.error_info_list) != 0
    assert check_approval_user_id.get_result() == {
        "result": False,
        "errorInfo": check_approval_user_id.error_info_list
    }


# パターン7
# 複合パターン（桁不正、入力可能文字不正）チェックの確認
def test_check_approval_user_id_case7():
    approval_user_id = "abcdefghijklmnoｐｑ"
    check_approval_user_id = checkApprovalUserId.CheckApprovalUserId(trace_logger, approval_user_id)
    assert check_approval_user_id.error_info_list[0]["errorCode"] == "020002"
    assert check_approval_user_id.error_info_list[1]["errorCode"] == "020020"
    assert len(check_approval_user_id.error_info_list) != 0
    assert check_approval_user_id.get_result() == {
        "result": False,
        "errorInfo": check_approval_user_id.error_info_list
    }


# パターン8
# 複合パターン（型不正、桁不正）チェックの確認
def test_check_approval_user_id_case8():
    approval_user_id = 12
    check_approval_user_id = checkApprovalUserId.CheckApprovalUserId(trace_logger, approval_user_id)
    assert check_approval_user_id.error_info_list[0]["errorCode"] == "020019"
    assert check_approval_user_id.error_info_list[1]["errorCode"] == "020016"
    assert len(check_approval_user_id.error_info_list) != 0
    assert check_approval_user_id.get_result() == {
        "result": False,
        "errorInfo": check_approval_user_id.error_info_list
    }


# パターン9
# 複合パターン（型不正、桁不正）チェックの確認
def test_check_approval_user_id_case9():
    approval_user_id = 12345678901234567
    check_approval_user_id = checkApprovalUserId.CheckApprovalUserId(trace_logger, approval_user_id)
    assert check_approval_user_id.error_info_list[0]["errorCode"] == "020019"
    assert check_approval_user_id.error_info_list[1]["errorCode"] == "020002"
    assert len(check_approval_user_id.error_info_list) != 0
    assert check_approval_user_id.get_result() == {
        "result": False,
        "errorInfo": check_approval_user_id.error_info_list
    }


# パターン10
# 正常系
def test_check_approval_user_id_case10():
    approval_user_id = "a-c"
    check_approval_user_id = checkApprovalUserId.CheckApprovalUserId(trace_logger, approval_user_id)
    assert len(check_approval_user_id.error_info_list) == 0
    assert check_approval_user_id.get_result() == {
        "result": True
    }


# パターン11
# 正常系
def test_check_approval_user_id_case11():
    approval_user_id = "abcde-+fghijklmn"
    check_approval_user_id = checkApprovalUserId.CheckApprovalUserId(trace_logger, approval_user_id)
    assert len(check_approval_user_id.error_info_list) == 0
    assert check_approval_user_id.get_result() == {
        "result": True
    }
