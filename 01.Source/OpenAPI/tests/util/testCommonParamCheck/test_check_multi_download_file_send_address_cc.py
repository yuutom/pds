from fastapi.testclient import TestClient
from fastapi import Request
from app import app
from util.commonParamCheck import checkMultiDownloadFileSendAddressCc
import util.logUtil as logUtil
from const.systemConst import SystemConstClass

client = TestClient(app)

trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))


# パターン1
# 型チェックの確認
def test_check_multi_download_file_send_address_cc_case1():
    multi_download_file_send_address_cc = 12345
    check_multi_download_file_send_address_cc = checkMultiDownloadFileSendAddressCc.CheckMultiDownloadFileSendAddressCc(trace_logger, multi_download_file_send_address_cc)
    assert check_multi_download_file_send_address_cc.error_info_list[0]["errorCode"] == "020019"
    assert len(check_multi_download_file_send_address_cc.error_info_list) != 0
    assert check_multi_download_file_send_address_cc.get_result() == {
        "result": False,
        "errorInfo": check_multi_download_file_send_address_cc.error_info_list
    }


# パターン2
# 桁数（閾値未満）チェックの確認
def test_check_multi_download_file_send_address_cc_case2():
    multi_download_file_send_address_cc = "abcd"
    check_multi_download_file_send_address_cc = checkMultiDownloadFileSendAddressCc.CheckMultiDownloadFileSendAddressCc(trace_logger, multi_download_file_send_address_cc)
    assert check_multi_download_file_send_address_cc.error_info_list[0]["errorCode"] == "020016"
    assert check_multi_download_file_send_address_cc.error_info_list[1]["errorCode"] == "020003"
    assert len(check_multi_download_file_send_address_cc.error_info_list) != 0
    assert check_multi_download_file_send_address_cc.get_result() == {
        "result": False,
        "errorInfo": check_multi_download_file_send_address_cc.error_info_list
    }


# パターン3
# 桁数（閾値超過）チェックの確認
def test_check_multi_download_file_send_address_cc_case3():
    multi_download_file_send_address_cc = "ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;abcdef@tf.com"
    check_multi_download_file_send_address_cc = checkMultiDownloadFileSendAddressCc.CheckMultiDownloadFileSendAddressCc(trace_logger, multi_download_file_send_address_cc)
    assert check_multi_download_file_send_address_cc.error_info_list[0]["errorCode"] == "020002"
    assert len(check_multi_download_file_send_address_cc.error_info_list) != 0
    assert check_multi_download_file_send_address_cc.get_result() == {
        "result": False,
        "errorInfo": check_multi_download_file_send_address_cc.error_info_list
    }


# パターン4
# 入力規則（@を含まない）チェックの確認
def test_check_multi_download_file_send_address_cc_case4():
    multi_download_file_send_address_cc = "a.com"
    check_multi_download_file_send_address_cc = checkMultiDownloadFileSendAddressCc.CheckMultiDownloadFileSendAddressCc(trace_logger, multi_download_file_send_address_cc)
    assert check_multi_download_file_send_address_cc.error_info_list[0]["errorCode"] == "020003"
    assert len(check_multi_download_file_send_address_cc.error_info_list) != 0
    assert check_multi_download_file_send_address_cc.get_result() == {
        "result": False,
        "errorInfo": check_multi_download_file_send_address_cc.error_info_list
    }


# パターン5
# 複合パターン（桁不正、入力規則不正）チェックの確認
def test_check_multi_download_file_send_address_cc_case5():
    multi_download_file_send_address_cc = "ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢ＠ｔｆ．ＣＯＭ；ＡＢＣＤＥＦ＠ｔｆ．ＣＯＭ"
    check_multi_download_file_send_address_cc = checkMultiDownloadFileSendAddressCc.CheckMultiDownloadFileSendAddressCc(trace_logger, multi_download_file_send_address_cc)
    assert check_multi_download_file_send_address_cc.error_info_list[0]["errorCode"] == "020002"
    assert check_multi_download_file_send_address_cc.error_info_list[1]["errorCode"] == "020003"
    assert len(check_multi_download_file_send_address_cc.error_info_list) != 0
    assert check_multi_download_file_send_address_cc.get_result() == {
        "result": False,
        "errorInfo": check_multi_download_file_send_address_cc.error_info_list
    }


# パターン6
# 複合パターン（桁不正、入力規則不正）チェックの確認
def test_check_multi_download_file_send_address_cc_case6():
    multi_download_file_send_address_cc = "a@!#"
    check_multi_download_file_send_address_cc = checkMultiDownloadFileSendAddressCc.CheckMultiDownloadFileSendAddressCc(trace_logger, multi_download_file_send_address_cc)
    assert check_multi_download_file_send_address_cc.error_info_list[0]["errorCode"] == "020016"
    assert check_multi_download_file_send_address_cc.error_info_list[1]["errorCode"] == "020003"
    assert len(check_multi_download_file_send_address_cc.error_info_list) != 0
    assert check_multi_download_file_send_address_cc.get_result() == {
        "result": False,
        "errorInfo": check_multi_download_file_send_address_cc.error_info_list
    }


# パターン7
# 正常系
def test_check_multi_download_file_send_address_cc_case7():
    multi_download_file_send_address_cc = "a@t.f"
    check_multi_download_file_send_address_cc = checkMultiDownloadFileSendAddressCc.CheckMultiDownloadFileSendAddressCc(trace_logger, multi_download_file_send_address_cc)
    assert len(check_multi_download_file_send_address_cc.error_info_list) == 0
    assert check_multi_download_file_send_address_cc.get_result() == {
        "result": True
    }


# パターン8
# 正常系
def test_check_multi_download_file_send_address_cc_case8():
    multi_download_file_send_address_cc = "ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;ab@tf.com;abcde@tf.com"
    check_multi_download_file_send_address_cc = checkMultiDownloadFileSendAddressCc.CheckMultiDownloadFileSendAddressCc(trace_logger, multi_download_file_send_address_cc)
    assert len(check_multi_download_file_send_address_cc.error_info_list) == 0
    assert check_multi_download_file_send_address_cc.get_result() == {
        "result": True
    }
