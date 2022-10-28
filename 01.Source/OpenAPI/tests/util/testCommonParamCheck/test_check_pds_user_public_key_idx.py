from fastapi.testclient import TestClient
from fastapi import Request
from app import app
from util.commonParamCheck import checkPdsUserPublicKeyIdx
import util.logUtil as logUtil
from const.systemConst import SystemConstClass

client = TestClient(app)

trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))


# パターン1
# 未入力チェックの確認
def test_check_pds_user_public_key_idx_case1():
    pds_user_public_key_idx = ""
    check_pds_user_public_key_idx = checkPdsUserPublicKeyIdx.CheckPdsUserPublicKeyIdx(trace_logger, pds_user_public_key_idx)
    assert check_pds_user_public_key_idx.error_info_list[0]["errorCode"] == "020001"
    assert check_pds_user_public_key_idx.error_info_list[1]["errorCode"] == "020019"
    assert len(check_pds_user_public_key_idx.error_info_list) != 0
    assert check_pds_user_public_key_idx.get_result() == {
        "result": False,
        "errorInfo": check_pds_user_public_key_idx.error_info_list
    }


# パターン2
# 型チェックの確認
def test_check_pds_user_public_key_idx_case2():
    pds_user_public_key_idx = "abcde"
    check_pds_user_public_key_idx = checkPdsUserPublicKeyIdx.CheckPdsUserPublicKeyIdx(trace_logger, pds_user_public_key_idx)
    assert check_pds_user_public_key_idx.error_info_list[0]["errorCode"] == "020019"
    assert check_pds_user_public_key_idx.error_info_list[1]["errorCode"] == "020020"
    assert len(check_pds_user_public_key_idx.error_info_list) != 0
    assert check_pds_user_public_key_idx.get_result() == {
        "result": False,
        "errorInfo": check_pds_user_public_key_idx.error_info_list
    }


# パターン3
# 正常系
def test_check_pds_user_public_key_idx_case3():
    pds_user_public_key_idx = 123
    check_pds_user_public_key_idx = checkPdsUserPublicKeyIdx.CheckPdsUserPublicKeyIdx(trace_logger, pds_user_public_key_idx)
    assert len(check_pds_user_public_key_idx.error_info_list) == 0
    assert check_pds_user_public_key_idx.get_result() == {
        "result": True
    }
