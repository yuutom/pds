import random
import string
import asyncio
from fastapi.testclient import TestClient
from app import app
from fastapi import Request
import pytest
from pytest_mock.plugin import MockerFixture
from util.tokenUtil import TokenUtilClass
import util.logUtil as logUtil
from const.sqlConst import SqlConstClass
from const.systemConst import SystemConstClass
from exceptionClass.PDSException import PDSException
import routers.public.readRouter as readRouter
from models.public.readModel import readModelClass

client = TestClient(app)
EXEC_NAME: str = "create"

BEARER = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0Zk9wZXJhdG9ySWQiOiJsLXRlc3QiLCJ0Zk9wZXJhdG9yTmFtZSI6Ilx1MzBlZFx1MzBiMFx1MzBhNFx1MzBmM1x1MzBjNlx1MzBiOVx1MzBjOCIsInRmT3BlcmF0b3JQYXNzd29yZFJlc2V0RmxnIjpmYWxzZSwiYWNjZXNzVG9rZW4iOiJiZGE4ZGY3OThiYzViZGZhMWZkODIyNmRiYmQ0OTMyMTY5ZmY5MjAzNWM0YzFlY2FjZjY2OGUyYzk2ZjAwZThlZTUxNTBiNGM0NTc0NjlkN2I4YmY1NzIxZDZlM2NiNzFiY2RiYzA3ODRiYzcyZWVlNjk1OGE3NTBiMWJkMWEzZWFmZWQ0OWFhNWU0ODZjYzQyZmM3OWNhMWY3MGQzZmM3Yzc0YzE5NjM3ODUzMjRhZDRhNGM0NjkxOGE4NjQ1N2ZiODE3NDU1MCIsImV4cCI6MTY2MTc0NjY3MX0.LCRjPEqKMkRQ_phaYnO7S7pd3SU_rgon-wsX14DBsPA"
ACCESS_TOKEN = "bda8df798bc5bdfa1fd8226dbbd4932169ff92035c4c1ecacf668e2c96f00e8ee5150b4c457469d7b8bf5721d6e3cb71bcdbc0784bc72eee6958a750b1bd1a3eafed49aa5e486cc42fc79ca1f70d3fc7c74c1963785324ad4a4c46918a86457fb8174550"
HEADER = {"pdsUserId": "C9876543", "Content-Type": "application/json", "timeStamp": "2022/08/23 15:12:01.690", "accessToken": ACCESS_TOKEN, "Authorization": "Bearer " + BEARER}
TID = "transaction1"


@pytest.fixture
def create_header():
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_public(pdsUserId="C9876543", pdsUserName="PDSユーザ登録テスト", accessToken=None)
    print("accessToken:" + token_result["accessToken"])
    yield {"header": {"pdsUserId": "C9876543", "Content-Type": "application/json", "timeStamp": "2022/08/23 15:12:01.690", "accessToken": token_result["accessToken"], "Authorization": "Bearer " + token_result["jwt"]}}


# No1.事前処理が失敗する
def test_read_case1(mocker: MockerFixture, create_header):
    mocker.patch("util.commonUtil.CommonUtilClass.check_pds_user_domain").side_effect = Exception('testException')
    header = create_header["header"]
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "999999",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No2.事前処理が成功する
def test_read_case2(create_header):
    header = create_header["header"]
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tid": TID,
        "transactionInfo": {
            "saveDate": "2022/09/26 10:00:00.000",
            "userId": "transaction10000",
            "data": {"aaa": "bbb"},
            "image": ["abcde", "123456"],
            "imageHash": ["abc", "def"],
            "secureLevel": "2"
        }
    }
    print(response.json())


# No3.個人情報取得処理が失敗する
def test_read_case3(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "USER_PROFILE_READ_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "991028",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No4.個人情報取得処理が成功する
def test_read_case4(create_header):
    header = create_header["header"]
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tid": TID,
        "transactionInfo": {
            "saveDate": "2022/09/26 10:00:00.000",
            "userId": "transaction10000",
            "data": {"aaa": "bbb"},
            "image": ["abcde", "123456"],
            "imageHash": ["abc", "def"],
            "secureLevel": "2"
        }
    }
    print(response.json())


# No5.アクセストークン発行処理が失敗する
def test_read_case5(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.tokenUtil.TokenUtilClass.create_token_public").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "999999",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No6.アクセストークン発行処理が成功する
def test_read_case6(create_header):
    header = create_header["header"]
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tid": TID,
        "transactionInfo": {
            "saveDate": "2022/09/26 10:00:00.000",
            "userId": "transaction10000",
            "data": {"aaa": "bbb"},
            "image": ["abcde", "123456"],
            "imageHash": ["abc", "def"],
            "secureLevel": "2"
        }
    }
    print(response.json())


# No7.共通エラーチェック処理が成功（エラー情報有り）
def test_read_case7(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.tokenUtil.TokenUtilClass.create_token_public").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "999999",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No8.API実行履歴登録処理が失敗する
def test_read_case8(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.commonUtil.get_datetime_str_no_symbol").side_effect = ["20220927145527512", "20220101000000000"]
    mocker.patch("util.commonUtil.get_random_ascii").side_effect = ["O1MOs01uEKinK", ''.join(random.choices(string.ascii_letters + string.digits, k=13))]
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "030001",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No9.API実行履歴登録処理が成功する
def test_read_case9(create_header):
    header = create_header["header"]
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tid": TID,
        "transactionInfo": {
            "saveDate": "2022/09/26 10:00:00.000",
            "userId": "transaction10000",
            "data": {"aaa": "bbb"},
            "image": ["abcde", "123456"],
            "imageHash": ["abc", "def"],
            "secureLevel": "2"
        }
    }
    print(response.json())


# No10.返却パラメータを作成し返却する
def test_read_case10(create_header):
    header = create_header["header"]
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tid": TID,
        "transactionInfo": {
            "saveDate": "2022/09/26 10:00:00.000",
            "userId": "transaction10000",
            "data": {"aaa": "bbb"},
            "image": ["abcde", "123456"],
            "imageHash": ["abc", "def"],
            "secureLevel": "2"
        }
    }
    print(response.json())


# No11.PDSユーザドメイン検証処理が失敗する
def test_read_case11(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.commonUtil.CommonUtilClass.check_pds_user_domain").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "999999",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No12.PDSユーザドメイン検証処理が成功する
def test_read_case12(create_header):
    header = create_header["header"]
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tid": TID,
        "transactionInfo": {
            "saveDate": "2022/09/26 10:00:00.000",
            "userId": "transaction10000",
            "data": {"aaa": "bbb"},
            "image": ["abcde", "123456"],
            "imageHash": ["abc", "def"],
            "secureLevel": "2"
        }
    }
    print(response.json())


# No13.共通エラーチェック処理が成功（エラー情報有り）
def test_read_case13(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.commonUtil.CommonUtilClass.check_pds_user_domain").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "999999",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No14.アクセストークン検証処理が失敗する
def test_read_case14(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.tokenUtil.TokenUtilClass.verify_token_public").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "999999",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No15.アクセストークン検証処理が成功する
def test_read_case15(create_header):
    header = create_header["header"]
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tid": TID,
        "transactionInfo": {
            "saveDate": "2022/09/26 10:00:00.000",
            "userId": "transaction10000",
            "data": {"aaa": "bbb"},
            "image": ["abcde", "123456"],
            "imageHash": ["abc", "def"],
            "secureLevel": "2"
        }
    }
    print(response.json())


# No16.アクセストークン検証処理が失敗する
def test_read_case16(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.tokenUtil.TokenUtilClass.verify_token_public").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "999999",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No17.パラメータ検証処理が失敗する
def test_read_case17(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("routers.public.readRouter.input_check").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "999999",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No18.パラメータ検証処理が成功する
def test_read_case18(create_header):
    header = create_header["header"]
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tid": TID,
        "transactionInfo": {
            "saveDate": "2022/09/26 10:00:00.000",
            "userId": "transaction10000",
            "data": {"aaa": "bbb"},
            "image": ["abcde", "123456"],
            "imageHash": ["abc", "def"],
            "secureLevel": "2"
        }
    }
    print(response.json())


# No19.共通エラーチェック処理が成功（エラー情報有り）
def test_read_case19(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("routers.public.readRouter.input_check").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "999999",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No20.終了処理
def test_read_case20(create_header):
    header = create_header["header"]
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tid": TID,
        "transactionInfo": {
            "saveDate": "2022/09/26 10:00:00.000",
            "userId": "transaction10000",
            "data": {"aaa": "bbb"},
            "image": ["abcde", "123456"],
            "imageHash": ["abc", "def"],
            "secureLevel": "2"
        }
    }
    print(response.json())


# No21-1.PDSユーザドメイン名 値が設定されていない（空値）
def test_read_case21_1(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    response = client.get("/api/2.0//transaction?tid=" + TID, headers=header)
    # パスパラメータを空にするとURLが不正になるので確認不可であることを確認
    assert response.status_code == 404
    print(response.json())

    # 入力チェックを直接呼び出してエラーになることを確認
    response = readRouter.input_check(
        trace_logger,
        None,
        TID,
        header["pdsUserId"],
        header["accessToken"],
        header["timeStamp"],
        {
            "result": True,
            "pdsUserInfo": {"pdsUserId": header["pdsUserId"]}
        }
    )
    assert response == {
        "result": False,
        "errorInfo": [
            {
                "errorCode": "020001",
                "message": response["errorInfo"][0]["message"]
            }
        ]
    }
    print(response)


# No21-2.PDSユーザドメイン名 文字列型以外、21文字
# パスパラメータはURLで絶対に文字列になるので型チェックできない
def test_read_case21_2(create_header):
    # PDSユーザドメイン名に誤りがある場合には、PDSユーザドメイン検証でエラーになってしまうので入力チェックまで到達できないことを確認
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    response = client.get("/api/2.0/[012345678901, 23456]/transaction?tid=" + TID, headers=header)
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020002",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020003",
                "message": response.json()["errorInfo"][1]["message"]
            }
        ]
    }
    print(response.json())

    # PDSユーザドメイン名に誤りがある場合には、PDSユーザドメイン検証でエラーになってしまうので入力チェックまで到達できないことを確認
    # 入力チェックを直接呼び出してエラーになることを確認
    response = readRouter.input_check(
        trace_logger,
        [123456789012, 23456],
        TID,
        header["pdsUserId"],
        header["accessToken"],
        header["timeStamp"],
        {
            "result": True,
            "pdsUserInfo": {"pdsUserId": header["pdsUserId"]}
        }
    )
    assert response == {
        "result": False,
        "errorInfo": [
            {
                "errorCode": "020019",
                "message": response["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020002",
                "message": response["errorInfo"][1]["message"]
            },
        ]
    }
    print(response)


# No21-3.PDSユーザドメイン名 文字列型、4文字、全角を含む
# パスパラメータはURLで絶対に文字列になるので型チェックできない
def test_read_case21_3(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    response = client.get("/api/2.0/あ123/transaction?tid=" + TID, headers=header)
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020016",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020003",
                "message": response.json()["errorInfo"][1]["message"]
            }
        ]
    }
    print(response.json())

    # PDSユーザドメイン名に誤りがある場合には、PDSユーザドメイン検証でエラーになってしまうので入力チェックまで到達できないことを確認
    # 入力チェックを直接呼び出してエラーになることを確認
    response = readRouter.input_check(
        trace_logger,
        "あ123",
        TID,
        header["pdsUserId"],
        header["accessToken"],
        header["timeStamp"],
        {
            "result": True,
            "pdsUserInfo": {"pdsUserId": header["pdsUserId"]}
        }
    )
    assert response == {
        "result": False,
        "errorInfo": [
            {
                "errorCode": "020016",
                "message": response["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020003",
                "message": response["errorInfo"][1]["message"]
            }
        ]
    }
    print(response)


# No21-4.PDSユーザドメイン名 文字列型、5文字、入力規則違反していない（URL利用可能文字のみの半角小英数記号５桁）
def test_read_case21_4():
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_public(pdsUserId="C8000000", pdsUserName="PDSユーザドメイン検証成功テスト", accessToken=None)
    print("accessToken:" + token_result["accessToken"])
    header = {"pdsUserId": "C8000000", "Content-Type": "application/json", "timeStamp": "2022/08/23 15:12:01.690", "accessToken": token_result["accessToken"], "Authorization": "Bearer " + token_result["jwt"]}

    response = client.get("/api/2.0/c0123/transaction?tid=" + TID, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tid": TID,
        "transactionInfo": {
            "saveDate": "2022/09/26 10:00:00.000",
            "userId": "transaction10000",
            "data": {"aaa": "bbb"},
            "image": ["abcde", "123456"],
            "imageHash": ["abc", "def"],
            "secureLevel": "2"
        }
    }
    print(response.json())


# No21-5.PDSユーザドメイン名 文字列型、20文字、入力規則違反していない（URL利用可能文字のみの半角小英数記号20桁）
def test_read_case21_5():
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_public(pdsUserId="C8000001", pdsUserName="PDSユーザドメイン検証成功テスト", accessToken=None)
    print("accessToken:" + token_result["accessToken"])
    header = {"pdsUserId": "C8000001", "Content-Type": "application/json", "timeStamp": "2022/08/23 15:12:01.690", "accessToken": token_result["accessToken"], "Authorization": "Bearer " + token_result["jwt"]}

    response = client.get("/api/2.0/c0123456789012345678/transaction?tid=" + TID, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tid": TID,
        "transactionInfo": {
            "saveDate": "2022/09/26 10:00:00.000",
            "userId": "transaction10000",
            "data": {"aaa": "bbb"},
            "image": ["abcde", "123456"],
            "imageHash": ["abc", "def"],
            "secureLevel": "2"
        }
    }
    print(response.json())


# No21-6.PDSユーザID 値が設定されていない（空値）
def test_read_case21_6(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["pdsUserId"] = None
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020001",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020014",
                "message": response.json()["errorInfo"][1]["message"]
            },
            {
                "errorCode": "020003",
                "message": response.json()["errorInfo"][2]["message"]
            }
        ]
    }
    print(response.json())

    # PDSユーザIDに誤りがある場合には、PDSユーザドメイン検証でエラーになってしまうので入力チェックまで到達できないことを確認
    # 入力チェックを直接呼び出してエラーになることを確認
    response = readRouter.input_check(
        trace_logger,
        "pds-user-create",
        TID,
        header["pdsUserId"],
        header["accessToken"],
        header["timeStamp"],
        {
            "result": True,
            "pdsUserInfo": {"pdsUserId": header["pdsUserId"]}
        }
    )
    assert response == {
        "result": False,
        "errorInfo": [
            {
                "errorCode": "020001",
                "message": response["errorInfo"][0]["message"]
            }
        ]
    }
    print(response)


# No57-7.PDSユーザID 文字列型以外、7桁、C以外の文字で始まる
def test_read_case57_7(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["pdsUserId"] = '1234567'
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020014",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020003",
                "message": response.json()["errorInfo"][1]["message"]
            }
        ]
    }
    print(response.json())

    # PDSユーザIDに誤りがある場合には、PDSユーザドメイン検証でエラーになってしまうので入力チェックまで到達できないことを確認
    # 入力チェックを直接呼び出してエラーになることを確認
    response = readRouter.input_check(
        trace_logger,
        "pds-user-create",
        TID,
        int(header["pdsUserId"]),
        header["accessToken"],
        header["timeStamp"],
        {
            "result": True,
            "pdsUserInfo": {"pdsUserId": int(header["pdsUserId"])}
        }
    )
    assert response == {
        "result": False,
        "errorInfo": [
            {
                "errorCode": "020019",
                "message": response["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020014",
                "message": response["errorInfo"][1]["message"]
            }
        ]
    }
    print(response)


# No21-8.PDSユーザID 文字列型、8桁、入力規則違反していない（C＋数値7桁）
def test_read_case21_8(create_header):
    header = create_header["header"]
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tid": TID,
        "transactionInfo": {
            "saveDate": "2022/09/26 10:00:00.000",
            "userId": "transaction10000",
            "data": {"aaa": "bbb"},
            "image": ["abcde", "123456"],
            "imageHash": ["abc", "def"],
            "secureLevel": "2"
        }
    }
    print(response.json())


# No21-9.タイムスタンプ 値が設定されていない（空値）
def test_read_case21_9(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["timeStamp"] = None
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020001",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020014",
                "message": response.json()["errorInfo"][1]["message"]
            },
            {
                "errorCode": "020003",
                "message": response.json()["errorInfo"][2]["message"]
            }
        ]
    }
    print(response.json())


# No21-10.タイムスタンプ 文字列型以外、22桁
def test_read_case21_10(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["timeStamp"] = '1234567890123456789012'
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020014",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020003",
                "message": response.json()["errorInfo"][1]["message"]
            }
        ]
    }
    print(response.json())

    # ヘッダパラメータは文字列型以外を許容しないので、
    # 入力チェックを直接呼び出してエラーになることを確認
    response = readRouter.input_check(
        trace_logger,
        "pds-user-create",
        TID,
        header["pdsUserId"],
        header["accessToken"],
        int(header["timeStamp"]),
        {
            "result": True,
            "pdsUserInfo": {"pdsUserId": header["pdsUserId"]}
        }
    )
    assert response == {
        "result": False,
        "errorInfo": [
            {
                "errorCode": "020019",
                "message": response["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020014",
                "message": response["errorInfo"][1]["message"]
            }
        ]
    }
    print(response)


# No21-11.タイムスタンプ 文字列型、24桁、入力規則違反している　hh:mmがhhh:mm
def test_read_case21_11(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["timeStamp"] = '2022/09/30 12:000:00.000'
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020014",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020003",
                "message": response.json()["errorInfo"][1]["message"]
            }
        ]
    }
    print(response.json())


# No21-12.タイムスタンプ 文字列型、23桁、入力規則違反していない　「yyyy/MM/dd hh:mm:ss.iii」
def test_read_case21_12(create_header):
    header = create_header["header"]
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tid": TID,
        "transactionInfo": {
            "saveDate": "2022/09/26 10:00:00.000",
            "userId": "transaction10000",
            "data": {"aaa": "bbb"},
            "image": ["abcde", "123456"],
            "imageHash": ["abc", "def"],
            "secureLevel": "2"
        }
    }
    print(response.json())


# No21-13.アクセストークン 値が設定されていない（空値）
def test_read_case21_13(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["accessToken"] = None
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020001",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020014",
                "message": response.json()["errorInfo"][1]["message"]
            },
            {
                "errorCode": "020003",
                "message": response.json()["errorInfo"][2]["message"]
            }
        ]
    }
    print(response.json())

    # アクセストークンが不正な場合には、アクセストークン検証処理でエラーが発生して、入力チェックに到達しないため、
    # 入力チェックを直接呼び出してエラーになることを確認
    response = readRouter.input_check(
        trace_logger,
        "pds-user-create",
        TID,
        header["pdsUserId"],
        header["accessToken"],
        header["timeStamp"],
        {
            "result": True,
            "pdsUserInfo": {"pdsUserId": header["pdsUserId"]}
        }
    )
    assert response == {
        "result": False,
        "errorInfo": [
            {
                "errorCode": "020001",
                "message": response["errorInfo"][0]["message"]
            }
        ]
    }
    print(response)


# No21-14.アクセストークン 文字列型以外、201桁
def test_read_case21_14(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["accessToken"] = "123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901"
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020014",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())

    # アクセストークンが不正な場合には、アクセストークン検証処理でエラーが発生して、入力チェックに到達しないため、
    # 入力チェックを直接呼び出してエラーになることを確認
    response = readRouter.input_check(
        trace_logger,
        "pds-user-create",
        TID,
        header["pdsUserId"],
        int(header["accessToken"]),
        header["timeStamp"],
        {
            "result": True,
            "pdsUserInfo": {"pdsUserId": header["pdsUserId"]}
        }
    )
    assert response == {
        "result": False,
        "errorInfo": [
            {
                "errorCode": "020019",
                "message": response["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020014",
                "message": response["errorInfo"][1]["message"]
            }
        ]
    }
    print(response)


# No21-15.アクセストークン 文字列型、199桁、入力可能文字以外が含まれる（全角）
def test_read_case21_15(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["accessToken"] = "あ123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678"
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020014",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020003",
                "message": response.json()["errorInfo"][1]["message"]
            }
        ]
    }
    print(response.json())

    # アクセストークンが不正な場合には、アクセストークン検証処理でエラーが発生して、入力チェックに到達しないため、
    # 入力チェックを直接呼び出してエラーになることを確認
    response = readRouter.input_check(
        trace_logger,
        "pds-user-create",
        TID,
        header["pdsUserId"],
        header["accessToken"],
        header["timeStamp"],
        {
            "result": True,
            "pdsUserInfo": {"pdsUserId": header["pdsUserId"]}
        }
    )
    assert response == {
        "result": False,
        "errorInfo": [
            {
                "errorCode": "020014",
                "message": response["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020003",
                "message": response["errorInfo"][1]["message"]
            }
        ]
    }
    print(response)


# No21-16.アクセストークン 文字列型、200桁、入力可能文字のみ（半角英数字） [a-fA-F0-9]
def test_read_case21_16(create_header):
    header = create_header["header"]
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tid": TID,
        "transactionInfo": {
            "saveDate": "2022/09/26 10:00:00.000",
            "userId": "transaction10000",
            "data": {"aaa": "bbb"},
            "image": ["abcde", "123456"],
            "imageHash": ["abc", "def"],
            "secureLevel": "2"
        }
    }
    print(response.json())


# No21-17.トランザクションID 値が設定されていない（空値）
def test_read_case21_17(create_header):
    header = create_header["header"]
    response = client.get("/api/2.0/pds-user-create/transaction?tid=", headers=header)
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020001",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No21-18.トランザクションID 文字列型以外、37桁
def test_read_case21_18(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + "1234567890123456789012345678901234567", headers=header)
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020002",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())

    # URLのクエリパラメータは文字列以外を許容しないので、
    # 入力チェックを直接呼び出してエラーになることを確認
    response = readRouter.input_check(
        trace_logger,
        "pds-user-create",
        1234567890123456789012345678901234567,
        header["pdsUserId"],
        header["accessToken"],
        header["timeStamp"],
        {
            "result": True,
            "pdsUserInfo": {"pdsUserId": header["pdsUserId"]}
        }
    )
    assert response == {
        "result": False,
        "errorInfo": [
            {
                "errorCode": "020019",
                "message": response["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020002",
                "message": response["errorInfo"][1]["message"]
            }
        ]
    }
    print(response)


# No21-19.トランザクションID 文字列型、37桁、入力可能文字以外が含まれる(全角)
def test_read_case21_19(create_header):
    header = create_header["header"]
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + "あ1234567890abcdefghijklmnopqrstuvwxyz", headers=header)
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020002",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020020",
                "message": response.json()["errorInfo"][1]["message"]
            }
        ]
    }
    print(response.json())


# No21-20.トランザクションID 文字列型、36桁、入力可能文字のみ（半角英数字） [a-zA-Z0-9]
def test_read_case21_20(create_header):
    header = create_header["header"]
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + "1234567890aBcDeFgHiJkLmNoPqRsTuVwXyZ", headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tid": "1234567890aBcDeFgHiJkLmNoPqRsTuVwXyZ",
        "transactionInfo": {
            "saveDate": "2022/09/26 10:00:00.000",
            "userId": "transaction10000",
            "data": {"aaa": "bbb"},
            "image": ["abcde", "123456"],
            "imageHash": ["abc", "def"],
            "secureLevel": "2"
        }
    }
    print(response.json())


# No21-21.「引数．ヘッダパラメータ．PDSユーザID」と「引数．PDSユーザドメイン情報．PDSユーザID」の値が一致しない場合、「変数．エラー情報リスト」にエラー情報を追加する
def test_read_case21_21(mocker: MockerFixture, create_header):
    # 返却値の変更
    mocker.patch("util.commonUtil.CommonUtilClass.check_pds_user_domain").return_value = {"result": True, "pdsUserInfo": {"pdsUserId": "C1234567"}}
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["pdsUserId"] = 'C9876543'
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "010002",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No22.変数．エラー情報がない
def test_read_case22(create_header):
    header = create_header["header"]
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tid": TID,
        "transactionInfo": {
            "saveDate": "2022/09/26 10:00:00.000",
            "userId": "transaction10000",
            "data": {"aaa": "bbb"},
            "image": ["abcde", "123456"],
            "imageHash": ["abc", "def"],
            "secureLevel": "2"
        }
    }
    print(response.json())


# No23.変数．エラー情報がある
def test_read_case23(mocker: MockerFixture, create_header):
    header = create_header["header"]
    response = client.get("/api/2.0/pds-user-create/transaction?tid=", headers=header)
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020001",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No24.接続に失敗する
@pytest.mark.asyncio
async def test_read_case24(mocker: MockerFixture, create_header):
    header = create_header["header"]
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    pds_user_info = {
        'pdsUserId': "C9876543",
        'pdsUserInstanceSecretName': "pds-c0000000-sm",
        's3ImageDataBucketName': "pds-c0000000-bucket",
        'userProfilerKmsId': "fdb4c6aa-50b0-4ed1-bdad-32c21e0a0387",
        'tokyo_a_mongodb_secret_name': "pds-c0000000-mongo-tokyo-a-sm",
        'tokyo_c_mongodb_secret_name': "pds-c0000000-mongo-tokyo-c-sm",
        'osaka_a_mongodb_secret_name': "pds-c0000000-mongo-osaka-a-sm",
        'osaka_c_mongodb_secret_name': "pds-c0000000-mongo-osaka-c-sm"
    }
    request_info = Request({"type": "http", "headers": {}, "method": "post", "path": ""})
    mocker.patch.object(SystemConstClass, "PDS_USER_DB_NAME", "pds_user_db-ng")
    read_model = readModelClass(trace_logger, request_info, header["pdsUserId"], pds_user_info, "pds-user-create")
    with pytest.raises(PDSException) as e:
        await read_model.get_user_profile(
            pds_user_info["pdsUserInstanceSecretName"],
            TID,
            pds_user_info,
            request_info
        )

    assert e.value.args[0] == {
        "errorCode": "999999",
        "message": e.value.args[0]["message"]
    }
    print(e)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No25.接続に成功する
def test_read_case25(create_header):
    header = create_header["header"]
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tid": TID,
        "transactionInfo": {
            "saveDate": "2022/09/26 10:00:00.000",
            "userId": "transaction10000",
            "data": {"aaa": "bbb"},
            "image": ["abcde", "123456"],
            "imageHash": ["abc", "def"],
            "secureLevel": "2"
        }
    }
    print(response.json())


# No26.個人情報取得処理が失敗する
def test_read_case26(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "USER_PROFILE_READ_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "991028",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No27.個人情報取得処理に成功する（0件の場合）
def test_read_case27(create_header):
    header = create_header["header"]
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + "transaction0", headers=header)
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020004",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No28.個人情報取得処理に成功する（1件の場合）
def test_read_case28(create_header):
    header = create_header["header"]
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tid": TID,
        "transactionInfo": {
            "saveDate": "2022/09/26 10:00:00.000",
            "userId": "transaction10000",
            "data": {"aaa": "bbb"},
            "image": ["abcde", "123456"],
            "imageHash": ["abc", "def"],
            "secureLevel": "2"
        }
    }
    print(response.json())


# No29.個人情報取得処理が失敗する
def test_read_case29(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "USER_PROFILE_READ_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "991028",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No30.個人バイナリ情報取得処理に失敗する
def test_read_case30(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "USER_PROFILE_BINARY_GET_READ_TARGET_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "991028",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No31.個人バイナリ情報取得処理に成功する
def test_read_case31(create_header):
    header = create_header["header"]
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tid": TID,
        "transactionInfo": {
            "saveDate": "2022/09/26 10:00:00.000",
            "userId": "transaction10000",
            "data": {"aaa": "bbb"},
            "image": ["abcde", "123456"],
            "imageHash": ["abc", "def"],
            "secureLevel": "2"
        }
    }
    print(response.json())


# No32.共通エラーチェック処理が成功する（エラー情報有り）
def test_read_case32(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "USER_PROFILE_BINARY_GET_READ_TARGET_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "991028",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No33.「変数．個人バイナリ情報取得結果リスト」が0件の場合、「07.終了処理」に遷移する
def test_read_case33(create_header):
    header = create_header["header"]
    # 個人バイナリ情報がないデータを選択する
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + "transaction2", headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tid": "transaction2",
        "transactionInfo": {
            "saveDate": "2023/09/01 21:32:18.181",
            "userId": "C0123456",
            "data": "taroaaaa",
            "image": None,
            "imageHash": None,
            "secureLevel": "2"
        }
    }
    print(response.json())


# No34.「変数．個人バイナリ情報取得結果リスト」が1件以上の場合、「08.バイナリ情報格納変数定義処理」に遷移する
def test_read_case34(create_header):
    header = create_header["header"]
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tid": TID,
        "transactionInfo": {
            "saveDate": "2022/09/26 10:00:00.000",
            "userId": "transaction10000",
            "data": {"aaa": "bbb"},
            "image": ["abcde", "123456"],
            "imageHash": ["abc", "def"],
            "secureLevel": "2"
        }
    }
    print(response.json())


# No35.終了処理を実行する
def test_read_case35(create_header):
    header = create_header["header"]
    # 個人バイナリ情報がないデータを選択する
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + "transaction2", headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tid": "transaction2",
        "transactionInfo": {
            "saveDate": "2023/09/01 21:32:18.181",
            "userId": "C0123456",
            "data": "taroaaaa",
            "image": None,
            "imageHash": None,
            "secureLevel": "2"
        }
    }
    print(response.json())


# No36.バイナリ情報格納用の変数を定義する
def test_read_case36(create_header):
    header = create_header["header"]
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tid": TID,
        "transactionInfo": {
            "saveDate": "2022/09/26 10:00:00.000",
            "userId": "transaction10000",
            "data": {"aaa": "bbb"},
            "image": ["abcde", "123456"],
            "imageHash": ["abc", "def"],
            "secureLevel": "2"
        }
    }
    print(response.json())


# No37.「変数．個人バイナリ情報取得結果リスト[変数．個人情報バイナリデータループ数][1]」が変わった場合、「10．バイナリデータ取得処理リスト作成処理」に遷移する
def test_read_case37(create_header):
    header = create_header["header"]
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tid": TID,
        "transactionInfo": {
            "saveDate": "2022/09/26 10:00:00.000",
            "userId": "transaction10000",
            "data": {"aaa": "bbb"},
            "image": ["abcde", "123456"],
            "imageHash": ["abc", "def"],
            "secureLevel": "2"
        }
    }
    print(response.json())


# No38.「変数．個人バイナリ情報取得結果リスト[変数．個人情報バイナリデータループ数][1]」が同じ場合、「14．バイナリデータ取得対象追加処理」に遷移する
def test_read_case38(create_header):
    header = create_header["header"]
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tid": TID,
        "transactionInfo": {
            "saveDate": "2022/09/26 10:00:00.000",
            "userId": "transaction10000",
            "data": {"aaa": "bbb"},
            "image": ["abcde", "123456"],
            "imageHash": ["abc", "def"],
            "secureLevel": "2"
        }
    }
    print(response.json())


# No39.「変数．バイナリデータ取得処理リスト」にバイナリデータ取得処理を追加する
def test_read_case39(create_header):
    header = create_header["header"]
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tid": TID,
        "transactionInfo": {
            "saveDate": "2022/09/26 10:00:00.000",
            "userId": "transaction10000",
            "data": {"aaa": "bbb"},
            "image": ["abcde", "123456"],
            "imageHash": ["abc", "def"],
            "secureLevel": "2"
        }
    }
    print(response.json())


# No40.「変数．バイナリデータハッシュ値格納リスト」にハッシュ値を追加する。
def test_read_case40(create_header):
    header = create_header["header"]
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tid": TID,
        "transactionInfo": {
            "saveDate": "2022/09/26 10:00:00.000",
            "userId": "transaction10000",
            "data": {"aaa": "bbb"},
            "image": ["abcde", "123456"],
            "imageHash": ["abc", "def"],
            "secureLevel": "2"
        }
    }
    print(response.json())


# No41.バイナリデータ取得処理の対象を管理している変数を初期化する
def test_read_case41(create_header):
    header = create_header["header"]
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tid": TID,
        "transactionInfo": {
            "saveDate": "2022/09/26 10:00:00.000",
            "userId": "transaction10000",
            "data": {"aaa": "bbb"},
            "image": ["abcde", "123456"],
            "imageHash": ["abc", "def"],
            "secureLevel": "2"
        }
    }
    print(response.json())


# No42.「変数．バイナリデータ要素数」をインクリメントする
def test_read_case42(create_header):
    header = create_header["header"]
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tid": TID,
        "transactionInfo": {
            "saveDate": "2022/09/26 10:00:00.000",
            "userId": "transaction10000",
            "data": {"aaa": "bbb"},
            "image": ["abcde", "123456"],
            "imageHash": ["abc", "def"],
            "secureLevel": "2"
        }
    }
    print(response.json())


# No43.バイナリデータ取得処理の対象を管理している変数に値を追加する
def test_read_case43(create_header):
    header = create_header["header"]
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tid": TID,
        "transactionInfo": {
            "saveDate": "2022/09/26 10:00:00.000",
            "userId": "transaction10000",
            "data": {"aaa": "bbb"},
            "image": ["abcde", "123456"],
            "imageHash": ["abc", "def"],
            "secureLevel": "2"
        }
    }
    print(response.json())


# No44.「変数．個人情報バイナリデータループ数」と「変数．個人情報バイナリ情報取得結果リスト」の要素数が一致する場合、「16．バイナリデータ取得処理リスト作成処理」に遷移する
def test_read_case44(create_header):
    header = create_header["header"]
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tid": TID,
        "transactionInfo": {
            "saveDate": "2022/09/26 10:00:00.000",
            "userId": "transaction10000",
            "data": {"aaa": "bbb"},
            "image": ["abcde", "123456"],
            "imageHash": ["abc", "def"],
            "secureLevel": "2"
        }
    }
    print(response.json())


# No45.「変数．個人情報バイナリデータループ数」と「変数．個人情報バイナリ情報取得結果リスト」の要素数が一致しない場合、繰り返し処理を続行する
def test_read_case45(create_header):
    header = create_header["header"]
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tid": TID,
        "transactionInfo": {
            "saveDate": "2022/09/26 10:00:00.000",
            "userId": "transaction10000",
            "data": {"aaa": "bbb"},
            "image": ["abcde", "123456"],
            "imageHash": ["abc", "def"],
            "secureLevel": "2"
        }
    }
    print(response.json())


# No46.「変数．バイナリデータ取得処理リスト」にバイナリデータ取得処理を追加する
def test_read_case46(create_header):
    header = create_header["header"]
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tid": TID,
        "transactionInfo": {
            "saveDate": "2022/09/26 10:00:00.000",
            "userId": "transaction10000",
            "data": {"aaa": "bbb"},
            "image": ["abcde", "123456"],
            "imageHash": ["abc", "def"],
            "secureLevel": "2"
        }
    }
    print(response.json())


# No47.「変数．バイナリデータハッシュ値格納リスト」にハッシュ値を追加する。
def test_read_case47(create_header):
    header = create_header["header"]
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tid": TID,
        "transactionInfo": {
            "saveDate": "2022/09/26 10:00:00.000",
            "userId": "transaction10000",
            "data": {"aaa": "bbb"},
            "image": ["abcde", "123456"],
            "imageHash": ["abc", "def"],
            "secureLevel": "2"
        }
    }
    print(response.json())


# No48.バイナリデータ取得処理実行処理が失敗する
def test_read_case48(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.s3AioUtil.s3AioUtilClass.get_file").side_effect = Exception("test-exception")
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "990024",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No49.「変数．バイナリデータハッシュ値格納リスト」にハッシュ値を追加する。
def test_read_case49(create_header):
    header = create_header["header"]
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tid": TID,
        "transactionInfo": {
            "saveDate": "2022/09/26 10:00:00.000",
            "userId": "transaction10000",
            "data": {"aaa": "bbb"},
            "image": ["abcde", "123456"],
            "imageHash": ["abc", "def"],
            "secureLevel": "2"
        }
    }
    print(response.json())


# No50.返却パラメータを作成し返却する
def test_read_case50(create_header):
    header = create_header["header"]
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tid": TID,
        "transactionInfo": {
            "saveDate": "2022/09/26 10:00:00.000",
            "userId": "transaction10000",
            "data": {"aaa": "bbb"},
            "image": ["abcde", "123456"],
            "imageHash": ["abc", "def"],
            "secureLevel": "2"
        }
    }
    print(response.json())


# No51.「変数．個人情報取得結果リスト[0][5]」がtrueの場合、「変数．個人情報取得結果リスト[0][3]」をJson形式として読み取り、「変数．保存したいデータ出力」に格納する
def test_read_case51(create_header):
    header = create_header["header"]
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + TID, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tid": TID,
        "transactionInfo": {
            "saveDate": "2022/09/26 10:00:00.000",
            "userId": "transaction10000",
            "data": {"aaa": "bbb"},
            "image": ["abcde", "123456"],
            "imageHash": ["abc", "def"],
            "secureLevel": "2"
        }
    }
    print(response.json())


# No52.「変数．個人情報取得結果リスト[0][5]」がtrue以外の場合、「変数．個人情報取得結果リスト[0][3]」をそのままの形式で、「変数．保存したいデータ出力」に格納する
def test_read_case52(create_header):
    header = create_header["header"]
    # 個人バイナリ情報がないデータを選択する
    response = client.get("/api/2.0/pds-user-create/transaction?tid=" + "transaction2", headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tid": "transaction2",
        "transactionInfo": {
            "saveDate": "2023/09/01 21:32:18.181",
            "userId": "C0123456",
            "data": "taroaaaa",
            "image": None,
            "imageHash": None,
            "secureLevel": "2"
        }
    }
    print(response.json())
