from fastapi.testclient import TestClient
from util.commonUtil import CommonUtilClass
from app import app
from fastapi import Request
import pytest
# from pytest_mock.plugin import MockerFixture
from util.tokenUtil import TokenUtilClass
import util.logUtil as logUtil
# import json
from exceptionClass.PDSException import PDSException
from const.messageConst import MessageConstClass
from const.systemConst import SystemConstClass

client = TestClient(app)

BEARER = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0Zk9wZXJhdG9ySWQiOiJsLXRlc3QiLCJ0Zk9wZXJhdG9yTmFtZSI6Ilx1MzBlZFx1MzBiMFx1MzBhNFx1MzBmM1x1MzBjNlx1MzBiOVx1MzBjOCIsInRmT3BlcmF0b3JQYXNzd29yZFJlc2V0RmxnIjpmYWxzZSwiYWNjZXNzVG9rZW4iOiJiZGE4ZGY3OThiYzViZGZhMWZkODIyNmRiYmQ0OTMyMTY5ZmY5MjAzNWM0YzFlY2FjZjY2OGUyYzk2ZjAwZThlZTUxNTBiNGM0NTc0NjlkN2I4YmY1NzIxZDZlM2NiNzFiY2RiYzA3ODRiYzcyZWVlNjk1OGE3NTBiMWJkMWEzZWFmZWQ0OWFhNWU0ODZjYzQyZmM3OWNhMWY3MGQzZmM3Yzc0YzE5NjM3ODUzMjRhZDRhNGM0NjkxOGE4NjQ1N2ZiODE3NDU1MCIsImV4cCI6MTY2MTc0NjY3MX0.LCRjPEqKMkRQ_phaYnO7S7pd3SU_rgon-wsX14DBsPA"
ACCESS_TOKEN = "bda8df798bc5bdfa1fd8226dbbd4932169ff92035c4c1ecacf668e2c96f00e8ee5150b4c457469d7b8bf5721d6e3cb71bcdbc0784bc72eee6958a750b1bd1a3eafed49aa5e486cc42fc79ca1f70d3fc7c74c1963785324ad4a4c46918a86457fb8174550"
HEADER = {"pdsUserId": "C9876543", "pdsUserDomainName": "pds-user-create", "Content-Type": "application/json", "timeStamp": "2022/08/23 15:12:01.690", "accessToken": ACCESS_TOKEN, "Authorization": "Bearer " + BEARER}
DATA = {
    "mailId": 1
}

trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
token_util = TokenUtilClass(trace_logger)
common_util = CommonUtilClass(trace_logger)


@pytest.fixture
def create_auth():
    token_result = token_util.create_token_public(HEADER["pdsUserId"], HEADER["pdsUserName"], None)
    print(token_result["accessToken"], token_result["jwt"])
    yield {"accessToken": token_result["accessToken"], "jwt": token_result["jwt"]}


# No1.WBT送信取り消しAPI実行_01.引数検証処理チェック　異常系　引数．メールID　値が設定されていない（空値）
def test_wbt_mail_cancel_exec_case1_1():
    data_copy = DATA.copy()
    data_copy["mailId"] = ""
    with pytest.raises(PDSException) as e:
        common_util.wbt_mail_cancel_exec(
            mailId=data_copy["mailId"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "メールID")
    }
    assert e.value.args[1] == {
        "errorCode": "020019",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "メールID", "数値")
    }
    print(e)


# No1.WBT送信取り消しAPI実行_01.引数検証処理チェック　異常系　引数．メールID　数値型ではない
def test_wbt_mail_cancel_exec_case1_2():
    data_copy = DATA.copy()
    data_copy["mailId"] = "12"
    with pytest.raises(PDSException) as e:
        common_util.wbt_mail_cancel_exec(
            mailId=data_copy["mailId"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020019",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "メールID", "数値")
    }
    print(e)


# No1.WBT送信取り消しAPI実行_01.引数検証処理チェック　正常系　引数．メールID　値が設定されている　数値型である
def test_wbt_mail_cancel_exec_case1_3():
    data_copy = DATA.copy()
    response = common_util.wbt_mail_cancel_exec(
        mailId=data_copy["mailId"]
    )
    assert response == {
        "result": True
    }
    print(response)


# No2.WBT送信取り消しAPI実行_02.送信取り消しAPI実行　異常系　送信取り消し実行に失敗する　パラメータ不正
# TODO:パラメータ不正の設定をする
def test_wbt_mail_cancel_exec_case2():
    data_copy = DATA.copy()
    data_copy["mailId"] = "1"
    with pytest.raises(PDSException) as e:
        common_util.wbt_mail_cancel_exec(
            mailId=data_copy["mailId"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020019",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "メールID", "数値")
    }
    print(e)


# No3.WBT送信取り消しAPI実行_02.送信取り消しAPI実行　正常系　送信取り消し実行に成功する
def test_wbt_mail_cancel_exec_case3():
    data_copy = DATA.copy()
    response = common_util.wbt_mail_cancel_exec(
        mailId=data_copy["mailId"]
    )
    assert response == {
        "result": True
    }
    print(response)


# No4.WBT送信取り消しAPI実行_03.共通エラーチェック処理　正常系　共通エラーチェック処理が成功（エラー情報有り）
# TODO:エラー情報ありで共通エラーチェック処理を通す
def test_wbt_mail_cancel_exec_case4():
    data_copy = DATA.copy()
    response = common_util.wbt_mail_cancel_exec(
        mailId=data_copy["mailId"]
    )
    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "990012",
            "message": logUtil.message_build(MessageConstClass.ERRORS["990012"]["message"], "990012")
        }
    }
    print(response)


# No5.WBT送信取り消しAPI実行_04.終了処理　正常系　変数．エラー情報がない
def test_wbt_mail_cancel_exec_case5():
    data_copy = DATA.copy()
    response = common_util.wbt_mail_cancel_exec(
        mailId=data_copy["mailId"]
    )
    assert response == {
        "result": True
    }
    print(response)
