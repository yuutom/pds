from fastapi.testclient import TestClient
from fastapi import Request
from app import app
from util.commonParamCheck import checkImageHash
import util.logUtil as logUtil
from const.systemConst import SystemConstClass

client = TestClient(app)

trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))


# パターン1
# 型チェックの確認
def test_check_image_hash_case1():
    image_hash = 12345
    check_image_hash = checkImageHash.CheckImageHash(trace_logger, image_hash)
    assert check_image_hash.error_info_list[0]["errorCode"] == "020019"
    assert check_image_hash.error_info_list[1]["errorCode"] == "020020"
    assert len(check_image_hash.error_info_list) != 0
    assert check_image_hash.get_result() == {
        "result": False,
        "errorInfo": check_image_hash.error_info_list
    }


# パターン2
# 入力可能文字チェックの確認
def test_check_image_hash_case2():
    image_hash = "ＡＢＣＤＥ"
    check_image_hash = checkImageHash.CheckImageHash(trace_logger, image_hash)
    assert check_image_hash.error_info_list[0]["errorCode"] == "020020"
    assert len(check_image_hash.error_info_list) != 0
    assert check_image_hash.get_result() == {
        "result": False,
        "errorInfo": check_image_hash.error_info_list
    }


# パターン3
# 入力可能文字チェックの確認
def test_check_image_hash_case3():
    image_hash = "abc/%"
    check_image_hash = checkImageHash.CheckImageHash(trace_logger, image_hash)
    assert check_image_hash.error_info_list[0]["errorCode"] == "020020"
    assert len(check_image_hash.error_info_list) != 0
    assert check_image_hash.get_result() == {
        "result": False,
        "errorInfo": check_image_hash.error_info_list
    }


# パターン4
# 正常系
def test_check_image_hash_case4():
    image_hash = "abc123"
    check_image_hash = checkImageHash.CheckImageHash(trace_logger, image_hash)
    assert len(check_image_hash.error_info_list) == 0
    assert check_image_hash.get_result() == {
        "result": True
    }
