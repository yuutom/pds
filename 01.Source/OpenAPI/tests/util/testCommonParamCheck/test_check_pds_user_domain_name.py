from fastapi.testclient import TestClient
from fastapi import Request
from app import app
from util.commonParamCheck import checkPdsUserDomainName
import util.logUtil as logUtil
from const.systemConst import SystemConstClass

client = TestClient(app)

trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))


# パターン1
# 未入力チェックの確認
def test_check_pds_user_domain_name_case1():
    pds_user_domain_name = ""
    check_pds_user_domain_name = checkPdsUserDomainName.CheckPdsUserDomainName(trace_logger, pds_user_domain_name)
    assert check_pds_user_domain_name.error_info_list[0]["errorCode"] == "020001"
    assert check_pds_user_domain_name.error_info_list[1]["errorCode"] == "020016"
    assert check_pds_user_domain_name.error_info_list[2]["errorCode"] == "020003"
    assert len(check_pds_user_domain_name.error_info_list) != 0
    assert check_pds_user_domain_name.get_result() == {
        "result": False,
        "errorInfo": check_pds_user_domain_name.error_info_list
    }


# パターン2
# 型チェックの確認
def test_check_pds_user_domain_name_case2():
    pds_user_domain_name = 12345678
    check_pds_user_domain_name = checkPdsUserDomainName.CheckPdsUserDomainName(trace_logger, pds_user_domain_name)
    assert check_pds_user_domain_name.error_info_list[0]["errorCode"] == "020019"
    assert len(check_pds_user_domain_name.error_info_list) != 0
    assert check_pds_user_domain_name.get_result() == {
        "result": False,
        "errorInfo": check_pds_user_domain_name.error_info_list
    }


# パターン3
# 桁数（閾値未満）チェックの確認
def test_check_pds_user_domain_name_case3():
    pds_user_domain_name = "tokn"
    check_pds_user_domain_name = checkPdsUserDomainName.CheckPdsUserDomainName(trace_logger, pds_user_domain_name)
    assert check_pds_user_domain_name.error_info_list[0]["errorCode"] == "020016"
    assert check_pds_user_domain_name.error_info_list[1]["errorCode"] == "020003"
    assert len(check_pds_user_domain_name.error_info_list) != 0
    assert check_pds_user_domain_name.get_result() == {
        "result": False,
        "errorInfo": check_pds_user_domain_name.error_info_list
    }


# パターン4
# 桁数（閾値超過）チェックの確認
def test_check_pds_user_domain_name_case4():
    pds_user_domain_name = "pds_user_create_tf_op"
    check_pds_user_domain_name = checkPdsUserDomainName.CheckPdsUserDomainName(trace_logger, pds_user_domain_name)
    assert check_pds_user_domain_name.error_info_list[0]["errorCode"] == "020002"
    assert check_pds_user_domain_name.error_info_list[1]["errorCode"] == "020003"
    assert len(check_pds_user_domain_name.error_info_list) != 0
    assert check_pds_user_domain_name.get_result() == {
        "result": False,
        "errorInfo": check_pds_user_domain_name.error_info_list
    }


# パターン5
# 入力規則（半角大英字を含む）チェックの確認
def test_check_pds_user_domain_name_case5():
    pds_user_domain_name = "PDS_user_create"
    check_pds_user_domain_name = checkPdsUserDomainName.CheckPdsUserDomainName(trace_logger, pds_user_domain_name)
    assert check_pds_user_domain_name.error_info_list[0]["errorCode"] == "020003"
    assert len(check_pds_user_domain_name.error_info_list) != 0
    assert check_pds_user_domain_name.get_result() == {
        "result": False,
        "errorInfo": check_pds_user_domain_name.error_info_list
    }


# パターン6
# 入力規則（全角を含む）チェックの確認
def test_check_pds_user_domain_name_case6():
    pds_user_domain_name = "１２３４５６７８９０１２３４５６７８９０１"
    check_pds_user_domain_name = checkPdsUserDomainName.CheckPdsUserDomainName(trace_logger, pds_user_domain_name)
    assert check_pds_user_domain_name.error_info_list[0]["errorCode"] == "020002"
    assert check_pds_user_domain_name.error_info_list[1]["errorCode"] == "020003"
    assert len(check_pds_user_domain_name.error_info_list) != 0
    assert check_pds_user_domain_name.get_result() == {
        "result": False,
        "errorInfo": check_pds_user_domain_name.error_info_list
    }


# パターン7
# 入力規則（URL利用可能文字以外を含む）チェックの確認
def test_check_pds_user_domain_name_case7():
    pds_user_domain_name = "ab!#"
    check_pds_user_domain_name = checkPdsUserDomainName.CheckPdsUserDomainName(trace_logger, pds_user_domain_name)
    assert check_pds_user_domain_name.error_info_list[0]["errorCode"] == "020016"
    assert check_pds_user_domain_name.error_info_list[1]["errorCode"] == "020003"
    assert len(check_pds_user_domain_name.error_info_list) != 0
    assert check_pds_user_domain_name.get_result() == {
        "result": False,
        "errorInfo": check_pds_user_domain_name.error_info_list
    }


# パターン8
# 複合パターン（桁不正、型不正）チェックの確認
def test_check_pds_user_domain_name_case8():
    pds_user_domain_name = 1234
    check_pds_user_domain_name = checkPdsUserDomainName.CheckPdsUserDomainName(trace_logger, pds_user_domain_name)
    assert check_pds_user_domain_name.error_info_list[0]["errorCode"] == "020019"
    assert check_pds_user_domain_name.error_info_list[1]["errorCode"] == "020016"
    assert len(check_pds_user_domain_name.error_info_list) != 0
    assert check_pds_user_domain_name.get_result() == {
        "result": False,
        "errorInfo": check_pds_user_domain_name.error_info_list
    }


# パターン9
# 複合パターン（桁不正、型不正）チェックの確認
def test_check_pds_user_domain_name_case9():
    pds_user_domain_name = 123456789012345678901
    check_pds_user_domain_name = checkPdsUserDomainName.CheckPdsUserDomainName(trace_logger, pds_user_domain_name)
    assert check_pds_user_domain_name.error_info_list[0]["errorCode"] == "020019"
    assert check_pds_user_domain_name.error_info_list[1]["errorCode"] == "020002"
    assert len(check_pds_user_domain_name.error_info_list) != 0
    assert check_pds_user_domain_name.get_result() == {
        "result": False,
        "errorInfo": check_pds_user_domain_name.error_info_list
    }


# パターン10
# 正常系
def test_check_pds_user_domain_name_case10():
    pds_user_domain_name = "pds_user_create"
    check_pds_user_domain_name = checkPdsUserDomainName.CheckPdsUserDomainName(trace_logger, pds_user_domain_name)
    assert len(check_pds_user_domain_name.error_info_list) == 0
    assert check_pds_user_domain_name.get_result() == {
        "result": True
    }


# パターン11
# 正常系
def test_check_pds_user_domain_name_case11():
    pds_user_domain_name = "pds_-"
    check_pds_user_domain_name = checkPdsUserDomainName.CheckPdsUserDomainName(trace_logger, pds_user_domain_name)
    assert len(check_pds_user_domain_name.error_info_list) == 0
    assert check_pds_user_domain_name.get_result() == {
        "result": True
    }


# パターン12
# 正常系
def test_check_pds_user_domain_name_case12():
    pds_user_domain_name = "pds_user_create__-__"
    check_pds_user_domain_name = checkPdsUserDomainName.CheckPdsUserDomainName(trace_logger, pds_user_domain_name)
    assert len(check_pds_user_domain_name.error_info_list) == 0
    assert check_pds_user_domain_name.get_result() == {
        "result": True
    }
