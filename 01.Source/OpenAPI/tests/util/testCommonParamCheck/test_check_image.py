from fastapi.testclient import TestClient
from fastapi import Request
from app import app
from util.commonParamCheck import checkImage
import util.logUtil as logUtil
from const.systemConst import SystemConstClass

client = TestClient(app)

trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))


# パターン1
# 型チェックの確認
def test_check_image_case1():
    image = 1234567890
    check_image = checkImage.CheckImage(trace_logger, image)
    assert check_image.error_info_list[0]["errorCode"] == "020019"
    assert len(check_image.error_info_list) != 0
    assert check_image.get_result() == {
        "result": False,
        "errorInfo": check_image.error_info_list
    }


# パターン2
# 型チェックの確認
def test_check_image_case2():
    image = [1234567890]
    check_image = checkImage.CheckImage(trace_logger, image)
    assert check_image.error_info_list[0]["errorCode"] == "020019"
    assert len(check_image.error_info_list) != 0
    assert check_image.get_result() == {
        "result": False,
        "errorInfo": check_image.error_info_list
    }


# パターン3
# 複合（桁不正、入力可能文字（全角））チェックの確認
def test_check_image_case3():
    f = open('tests/public/14MB.txt', 'r', encoding='UTF-8')
    text = f.read()
    image = "あ" + text
    check_image = checkImage.CheckImage(trace_logger, image)
    assert check_image.error_info_list[0]["errorCode"] == "020020"
    assert check_image.error_info_list[1]["errorCode"] == "030017"
    assert len(check_image.error_info_list) != 0
    assert check_image.get_result() == {
        "result": False,
        "errorInfo": check_image.error_info_list
    }


# パターン4
# 複合（桁不正、入力可能文字（記号））チェックの確認
def test_check_image_case4():
    f = open('tests/public/140MB.txt', 'r', encoding='UTF-8')
    text = f.read()
    image = "$" + text
    check_image = checkImage.CheckImage(trace_logger, image)
    assert check_image.error_info_list[0]["errorCode"] == "020020"
    assert check_image.error_info_list[1]["errorCode"] == "030017"
    assert check_image.error_info_list[2]["errorCode"] == "030018"
    assert len(check_image.error_info_list) != 0
    assert check_image.get_result() == {
        "result": False,
        "errorInfo": check_image.error_info_list
    }


# パターン5
# 複合（桁不正、入力可能文字（全角））チェックの確認
def test_check_image_case5():
    f = open('tests/public/14MB.txt', 'r', encoding='UTF-8')
    text = f.read()
    image = ["あ" + text, "い" + text]
    check_image = checkImage.CheckImage(trace_logger, image)
    assert check_image.error_info_list[0]["errorCode"] == "020020"
    assert check_image.error_info_list[1]["errorCode"] == "030017"
    assert len(check_image.error_info_list) != 0
    assert check_image.get_result() == {
        "result": False,
        "errorInfo": check_image.error_info_list
    }


# パターン6
# 複合（桁不正、入力可能文字（記号））チェックの確認
def test_check_image_case6():
    f = open('tests/public/14MB.txt', 'r', encoding='UTF-8')
    text = f.read()
    image = ["$" + text, text, text, text, text, text, text, text, text, text]
    check_image = checkImage.CheckImage(trace_logger, image)
    assert check_image.error_info_list[0]["errorCode"] == "020020"
    assert check_image.error_info_list[1]["errorCode"] == "030017"
    assert check_image.error_info_list[2]["errorCode"] == "030018"
    assert len(check_image.error_info_list) != 0
    assert check_image.get_result() == {
        "result": False,
        "errorInfo": check_image.error_info_list
    }


# パターン7
# 正常系
def test_check_image_case7():
    f = open('tests/public/14MB.txt', 'r', encoding='UTF-8')
    text = f.read()
    image = text
    check_image = checkImage.CheckImage(trace_logger, image)
    assert len(check_image.error_info_list) == 0
    assert check_image.get_result() == {
        "result": True
    }


# パターン8
# 正常系
def test_check_image_case8():
    f = open('tests/public/14MB.txt', 'r', encoding='UTF-8')
    text = f.read()
    image = [text, text, text, text, text, text, text, text, text, text]
    check_image = checkImage.CheckImage(trace_logger, image)
    assert len(check_image.error_info_list) == 0
    assert check_image.get_result() == {
        "result": True
    }
