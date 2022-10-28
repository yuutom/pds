from fastapi.testclient import TestClient
from const.sqlConst import SqlConstClass
from util.commonUtil import CommonUtilClass
from app import app
from fastapi import Request
import pytest
from pytest_mock.plugin import MockerFixture
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
    "pdsUserId": "C9876543",
    "pdsKeyIdx": "1"
}

trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
token_util = TokenUtilClass(trace_logger)
common_util = CommonUtilClass(trace_logger)
# 共通DB接続準備処理
common_db_info_response = common_util.get_common_db_info_and_connection()


@pytest.fixture
def create_auth():
    token_result = token_util.create_token_public(HEADER["pdsUserId"], HEADER["pdsUserName"], None)
    print(token_result["accessToken"], token_result["jwt"])
    yield {"accessToken": token_result["accessToken"], "jwt": token_result["jwt"]}


# No1.PDSユーザ鍵存在検証処理_01.引数検証処理チェック　異常系　引数．PDSユーザID　値が設定されていない（空値）
def test_check_pds_user_key_case1_1_1():
    data_copy = DATA.copy()
    data_copy["pdsUserId"] = ""
    with pytest.raises(PDSException) as e:
        common_util.check_pds_user_key(
            pdsUserId=data_copy["pdsUserId"],
            pdsKeyIdx=data_copy["pdsKeyIdx"],
            common_db_info=common_db_info_response
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "PDSユーザID")
    }
    print(e)


# No1.PDSユーザ鍵存在検証処理_01.引数検証処理チェック　正常系　引数．PDSユーザID　値が設定されている
def test_check_pds_user_key_case1_1_2():
    data_copy = DATA.copy()
    response = common_util.check_pds_user_key(
        pdsUserId=data_copy["pdsUserId"],
        pdsKeyIdx=data_copy["pdsKeyIdx"],
        common_db_info=common_db_info_response
    )
    assert response == {
        "result": True
    }
    print(response)


# No1.PDSユーザ鍵存在検証処理_01.引数検証処理チェック　異常系　引数．PDSユーザ公開鍵インデックス　値が設定されていない（空値）
def test_check_pds_user_key_case1_2_1():
    data_copy = DATA.copy()
    data_copy["pdsKeyIdx"] = ""
    with pytest.raises(PDSException) as e:
        common_util.check_pds_user_key(
            pdsUserId=data_copy["pdsUserId"],
            pdsKeyIdx=data_copy["pdsKeyIdx"],
            common_db_info=common_db_info_response
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "PDSユーザ公開鍵インデックス")
    }
    print(e)


# No1.PDSユーザ鍵存在検証処理_01.引数検証処理チェック　正常系　引数．PDSユーザ公開鍵インデックス　値が設定されている
def test_check_pds_user_key_case1_2_2():
    data_copy = DATA.copy()
    response = common_util.check_pds_user_key(
        pdsUserId=data_copy["pdsUserId"],
        pdsKeyIdx=data_copy["pdsKeyIdx"],
        common_db_info=common_db_info_response
    )
    assert response == {
        "result": True
    }
    print(response)


# No1.PDSユーザ鍵存在検証処理_02.PDSユーザ取得処理　異常系　変数．PDSユーザ取得結果．カウントの値が1以外
def test_check_pds_user_key_case2():
    data_copy = DATA.copy()
    data_copy["pdsUserId"] = "C1100001"
    response = common_util.check_pds_user_key(
        pdsUserId=data_copy["pdsUserId"],
        pdsKeyIdx=data_copy["pdsKeyIdx"],
        common_db_info=common_db_info_response
    )
    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "030013",
            "message": logUtil.message_build(MessageConstClass.ERRORS["030013"]["message"], "PDSユーザ、PDSユーザ公開鍵", data_copy["pdsUserId"])
        }
    }
    print(response)


# No3.PDSユーザ鍵存在検証処理_02.PDSユーザ取得処理　異常系　postgresqlのエラーが発生
def test_check_pds_user_key_case3(mocker: MockerFixture):
    data_copy = DATA.copy()
    mocker.patch.object(SqlConstClass, "PDS_USER_JOIN_PDS_USER_KEY_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    response = common_util.check_pds_user_key(
        pdsUserId=data_copy["pdsUserId"],
        pdsKeyIdx=data_copy["pdsKeyIdx"],
        common_db_info=common_db_info_response
    )
    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "999999",
            "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
        }
    }
    print(response)


# No4.PDSユーザ鍵存在検証処理_02.PDSユーザ取得処理　正常系　変数．PDSユーザ取得結果．カウントの値が1
def test_check_pds_user_key_case4():
    data_copy = DATA.copy()
    response = common_util.check_pds_user_key(
        pdsUserId=data_copy["pdsUserId"],
        pdsKeyIdx=data_copy["pdsKeyIdx"],
        common_db_info=common_db_info_response
    )
    assert response == {
        "result": True
    }
    print(response)


# No5.PDSユーザ鍵存在検証処理_03.終了処理　正常系　変数．エラー情報がない
def test_check_pds_user_key_case5():
    data_copy = DATA.copy()
    response = common_util.check_pds_user_key(
        pdsUserId=data_copy["pdsUserId"],
        pdsKeyIdx=data_copy["pdsKeyIdx"],
        common_db_info=common_db_info_response
    )
    assert response == {
        "result": True
    }
    print(response)
