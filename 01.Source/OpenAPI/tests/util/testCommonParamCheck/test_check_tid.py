from fastapi.testclient import TestClient
from fastapi import Request
from app import app
from util.commonParamCheck import checkTransactionId
import util.logUtil as logUtil
from const.systemConst import SystemConstClass

client = TestClient(app)

trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))


# パターン1
# 未入力チェックの確認
def test_check_transacrion_id_case1():
    transacrion_id = ""
    check_transacrion_id = checkTransactionId.CheckTransactionId(trace_logger, transacrion_id)
    assert check_transacrion_id.error_info_list[0]["errorCode"] == "020001"
    assert len(check_transacrion_id.error_info_list) != 0
    assert check_transacrion_id.get_result() == {
        "result": False,
        "errorInfo": check_transacrion_id.error_info_list
    }


# パターン2
# 型チェックの確認
def test_check_transacrion_id_case2():
    transacrion_id = 123456789012345678901234567890123456
    check_transacrion_id = checkTransactionId.CheckTransactionId(trace_logger, transacrion_id)
    assert check_transacrion_id.error_info_list[0]["errorCode"] == "020019"
    assert len(check_transacrion_id.error_info_list) != 0
    assert check_transacrion_id.get_result() == {
        "result": False,
        "errorInfo": check_transacrion_id.error_info_list
    }


# パターン3
# 桁数（閾値超過）チェックの確認
def test_check_transacrion_id_case3():
    transacrion_id = "abcdefghijklmnopqrstuvwxyzabcdefghijk"
    check_transacrion_id = checkTransactionId.CheckTransactionId(trace_logger, transacrion_id)
    assert check_transacrion_id.error_info_list[0]["errorCode"] == "020002"
    assert len(check_transacrion_id.error_info_list) != 0
    assert check_transacrion_id.get_result() == {
        "result": False,
        "errorInfo": check_transacrion_id.error_info_list
    }


# パターン4
# 入力可能文字チェックの確認
def test_check_transacrion_id_case4():
    transacrion_id = "ＡＢＣＤＥＦｇＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺＡＢＣＤＥＦｇＨＩＪ"
    check_transacrion_id = checkTransactionId.CheckTransactionId(trace_logger, transacrion_id)
    assert check_transacrion_id.error_info_list[0]["errorCode"] == "020020"
    assert len(check_transacrion_id.error_info_list) != 0
    assert check_transacrion_id.get_result() == {
        "result": False,
        "errorInfo": check_transacrion_id.error_info_list
    }


# パターン5
# 複合パターン（桁数不正、入力可能文字不正）チェックの確認
def test_check_transacrion_id_case5():
    transacrion_id = "ＡＢＣＤＥＦｇＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺＡＢＣＤＥＦｇＨＩＪｋ"
    check_transacrion_id = checkTransactionId.CheckTransactionId(trace_logger, transacrion_id)
    assert check_transacrion_id.error_info_list[0]["errorCode"] == "020002"
    assert check_transacrion_id.error_info_list[1]["errorCode"] == "020020"
    assert len(check_transacrion_id.error_info_list) != 0
    assert check_transacrion_id.get_result() == {
        "result": False,
        "errorInfo": check_transacrion_id.error_info_list
    }


# パターン6
# 複合パターン（型不正、桁数不正）チェックの確認
def test_check_transacrion_id_case6():
    transacrion_id = 123456789012345678901234567890123456
    check_transacrion_id = checkTransactionId.CheckTransactionId(trace_logger, transacrion_id)
    assert check_transacrion_id.error_info_list[0]["errorCode"] == "020019"
    assert len(check_transacrion_id.error_info_list) != 0
    assert check_transacrion_id.get_result() == {
        "result": False,
        "errorInfo": check_transacrion_id.error_info_list
    }


# パターン7
# 正常系
def test_check_transacrion_id_case7():
    transacrion_id = "tfoperator1"
    check_transacrion_id = checkTransactionId.CheckTransactionId(trace_logger, transacrion_id)
    assert len(check_transacrion_id.error_info_list) == 0
    assert check_transacrion_id.get_result() == {
        "result": True
    }
