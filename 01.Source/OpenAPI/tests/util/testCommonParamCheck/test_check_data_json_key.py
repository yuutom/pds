from fastapi.testclient import TestClient
from fastapi import Request
from app import app
from util.commonParamCheck import checkDataJsonKey
import util.logUtil as logUtil
from const.systemConst import SystemConstClass

client = TestClient(app)

trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))


# パターン1
# 型チェックの確認
def test_check_data_json_key_case1():
    data_json_key = 12345
    check_data_json_key = checkDataJsonKey.CheckDataJsonKey(trace_logger, data_json_key)
    assert check_data_json_key.error_info_list[0]["errorCode"] == "020019"
    assert len(check_data_json_key.error_info_list) != 0
    assert check_data_json_key.get_result() == {
        "result": False,
        "errorInfo": check_data_json_key.error_info_list
    }


# パターン2
# 正常系
def test_check_data_json_key_case2():
    data_json_key = "abcde"
    check_data_json_key = checkDataJsonKey.CheckDataJsonKey(trace_logger, data_json_key)
    assert len(check_data_json_key.error_info_list) == 0
    assert check_data_json_key.get_result() == {
        "result": True
    }
