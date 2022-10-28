from fastapi.testclient import TestClient
from fastapi import Request
from app import app
from util.commonParamCheck import checkDataStr
import util.logUtil as logUtil
from const.systemConst import SystemConstClass

client = TestClient(app)

trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))


# パターン1
# 型チェックの確認
def test_check_data_str_case1():
    data_str = 12345
    check_data_str = checkDataStr.CheckDataStr(trace_logger, data_str)
    assert check_data_str.error_info_list[0]["errorCode"] == "020019"
    assert len(check_data_str.error_info_list) != 0
    assert check_data_str.get_result() == {
        "result": False,
        "errorInfo": check_data_str.error_info_list
    }


# パターン2
# 正常系
def test_check_data_str_case2():
    data_str = "abcde"
    check_data_str = checkDataStr.CheckDataStr(trace_logger, data_str)
    assert len(check_data_str.error_info_list) == 0
    assert check_data_str.get_result() == {
        "result": True
    }
