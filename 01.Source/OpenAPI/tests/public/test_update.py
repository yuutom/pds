import random
import string
from fastapi.testclient import TestClient
from app import app
from fastapi import Request
import pytest
from pytest_mock.plugin import MockerFixture
from util.tokenUtil import TokenUtilClass
import util.logUtil as logUtil
import json
from const.sqlConst import SqlConstClass
from const.systemConst import SystemConstClass
from util.mongoDbUtil import MongoDbClass
from util.postgresDbUtil import PostgresDbUtilClass
from pymongo.collection import Collection
from pymongo.client_session import ClientSession
from pymongo.errors import PyMongoError
import routers.public.updateRouter as updateRouter
from models.public.updateModel import updateModel
from models.public.updateModel import requestBody as modelRequestBody
from exceptionClass.PDSException import PDSException

client = TestClient(app)
EXEC_NAME: str = "create"

BEARER = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0Zk9wZXJhdG9ySWQiOiJsLXRlc3QiLCJ0Zk9wZXJhdG9yTmFtZSI6Ilx1MzBlZFx1MzBiMFx1MzBhNFx1MzBmM1x1MzBjNlx1MzBiOVx1MzBjOCIsInRmT3BlcmF0b3JQYXNzd29yZFJlc2V0RmxnIjpmYWxzZSwiYWNjZXNzVG9rZW4iOiJiZGE4ZGY3OThiYzViZGZhMWZkODIyNmRiYmQ0OTMyMTY5ZmY5MjAzNWM0YzFlY2FjZjY2OGUyYzk2ZjAwZThlZTUxNTBiNGM0NTc0NjlkN2I4YmY1NzIxZDZlM2NiNzFiY2RiYzA3ODRiYzcyZWVlNjk1OGE3NTBiMWJkMWEzZWFmZWQ0OWFhNWU0ODZjYzQyZmM3OWNhMWY3MGQzZmM3Yzc0YzE5NjM3ODUzMjRhZDRhNGM0NjkxOGE4NjQ1N2ZiODE3NDU1MCIsImV4cCI6MTY2MTc0NjY3MX0.LCRjPEqKMkRQ_phaYnO7S7pd3SU_rgon-wsX14DBsPA"
ACCESS_TOKEN = "bda8df798bc5bdfa1fd8226dbbd4932169ff92035c4c1ecacf668e2c96f00e8ee5150b4c457469d7b8bf5721d6e3cb71bcdbc0784bc72eee6958a750b1bd1a3eafed49aa5e486cc42fc79ca1f70d3fc7c74c1963785324ad4a4c46918a86457fb8174550"
HEADER = {"pdsUserId": "C9876543", "Content-Type": "application/json", "timeStamp": "2022/08/23 15:12:01.690", "accessToken": ACCESS_TOKEN, "Authorization": "Bearer " + BEARER}
DATA = {
    "tid": "transaction1",
    "info": {
        "userId": "transaction10000",
        "saveDate": "2022/09/26 10:00:00.000",
        "data": "{\"aaa\": \"bbb\"}",
        "image": ["abcde", "123456"],
        "imageHash": ["abc", "def"],
        "secureLevel": "2"
    }
}


@pytest.fixture
def create_header():
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_public(pdsUserId="C9876543", pdsUserName="PDSユーザ登録テスト", accessToken=None)
    print("accessToken:" + token_result["accessToken"])
    yield {"header": {"pdsUserId": "C9876543", "Content-Type": "application/json", "timeStamp": "2022/08/23 15:12:01.690", "accessToken": token_result["accessToken"], "Authorization": "Bearer " + token_result["jwt"]}}


# No1.事前処理が失敗する
def test_update_case1(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.commonUtil.CommonUtilClass.check_pds_user_domain").side_effect = Exception('testException')
    # ErrorInfo
    # mocker.patch("util.commonUtil.CommonUtilClass.check_pds_user_domain").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test Exception"}}
    header = create_header["header"]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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
def test_update_case2(create_header):
    header = create_header["header"]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No3.PDSユーザDB接続準備処理に失敗する
def test_update_case3(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SystemConstClass, "PDS_USER_DB_NAME", "pds_user_db_ng")
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No4.PDSユーザDB接続準備処理に成功する
def test_update_case4(create_header):
    header = create_header["header"]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No5.個人情報検索処理の取得件数が1件以外
def test_update_case5(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction0"
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "030015",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No6.「変数．個人情報検索結果リスト[3]」がfalse
def test_update_case6(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction40000"
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020023",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No7.個人情報取得処理が失敗する
# No9.共通エラーチェック処理が成功（エラー情報有り）
def test_update_case7(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "USER_PROFILE_SEARCH_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No.8個人情報取得処理が成功する
def test_update_case8(create_header):
    header = create_header["header"]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No.10個人情報更新処理が失敗する
def test_update_case10(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "USER_PROFILE_BINARY_SEARCH_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No.11個人情報更新処理が成功する
def test_update_case11(create_header):
    header = create_header["header"]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No.12「変数．個人情報更新結果．SQS実行フラグ」がtrue
def test_update_case12(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("models.public.updateModel.updateModel.update_user_info").return_value = {"result": False, "sqs_exec_flg": True}
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No.13「変数．個人情報更新結果．SQS実行フラグ」がfalse
def test_update_case13(create_header):
    header = create_header["header"]
    DATA["info"]["image"] = [False, False]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No.14個人情報削除バッチキュー発行処理が失敗する
def test_update_case14(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("models.public.updateModel.updateModel.update_user_info").return_value = {"result": False, "sqs_exec_flg": True}
    mocker.patch.object(SystemConstClass, "SQS_QUEUE_NAME", "aaaaaa")
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "990051",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No.15個人情報削除バッチキュー発行処理が成功する
def test_update_case15(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("models.public.updateModel.updateModel.update_user_info").return_value = {"result": False, "sqs_exec_flg": True}
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No.16アクセストークン発行処理が失敗する
# No18.共通エラーチェック処理が成功（エラー情報有り）
def test_update_case16(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.tokenUtil.TokenUtilClass.create_token_public").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No.17アクセストークン発行処理が成功する
def test_update_case17(create_header):
    header = create_header["header"]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No19.API実行履歴登録処理が失敗する
def test_update_case19(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.commonUtil.get_datetime_str_no_symbol").side_effect = ["20220927145527512", "20220101000000000"]
    mocker.patch("util.commonUtil.get_random_ascii").side_effect = ["O1MOs01uEKinK", ''.join(random.choices(string.ascii_letters + string.digits, k=13))]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No20.API実行履歴登録処理が成功する
def test_update_case20(create_header):
    header = create_header["header"]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No21.変数．エラー情報がある(No.5でエラー）
def test_update_case21(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction0"
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "030015",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No22.変数．エラー情報がない
def test_update_case22(create_header):
    header = create_header["header"]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No23.PDSユーザドメイン検証処理が失敗する
# No25.共通エラーチェック処理が成功（エラー情報有り）
def test_update_case23(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.commonUtil.CommonUtilClass.check_pds_user_domain").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No24.PDSユーザドメイン検証処理が成功する
def test_update_case24(create_header):
    header = create_header["header"]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No26.アクセストークン検証処理が失敗する
# No28.共通エラーチェック処理が成功（エラー情報有り）
def test_update_case26(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.tokenUtil.TokenUtilClass.verify_token_public").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No27.アクセストークン検証処理が成功する
# No30.パラメータ検証処理が成功する
# No32.変数．エラー情報がない
def test_update_case27(create_header):
    header = create_header["header"]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No29.パラメータ検証処理が失敗する
# No31.共通エラーチェック処理が成功（エラー情報有り）
def test_update_case29(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("routers.public.updateRouter.input_check").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No33-1.PDSユーザドメイン名 値が設定されていない（空値）
def test_update_case33_1(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    response = client.put("/api/2.0//transaction", headers=header, data=json.dumps(DATA))
    # パスパラメータを空にするとURLが不正になるので確認不可であることを確認
    assert response.status_code == 404
    print(response.json())

    # 入力チェックを直接呼び出してエラーになることを確認
    request_body = updateRouter.requestBody(tid=DATA["tid"], info=DATA["info"])
    response = updateRouter.input_check(
        trace_logger,
        None,
        request_body,
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


# No33-2.PDSユーザドメイン名 文字列型以外、21文字
# パスパラメータはURLで絶対に文字列になるので型チェックできない
def test_update_case33_2(create_header):
    # PDSユーザドメイン名に誤りがある場合には、PDSユーザドメイン検証でエラーになってしまうので入力チェックまで到達できないことを確認
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    response = client.put("/api/2.0/[012345678901, 23456]/transaction", headers=header, data=json.dumps(DATA))
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
    request_body = updateRouter.requestBody(tid=DATA["tid"], info=DATA["info"])
    response = updateRouter.input_check(
        trace_logger,
        123456789012345678901,
        request_body,
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


# No33-3.PDSユーザドメイン名 文字列型、4文字、全角を含む
# パスパラメータはURLで絶対に文字列になるので型チェックできない
def test_update_case33_3(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    response = client.put("/api/2.0/あ123/transaction", headers=header, data=json.dumps(DATA))
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
    request_body = updateRouter.requestBody(tid=DATA["tid"], info=DATA["info"])
    response = updateRouter.input_check(
        trace_logger,
        "あ123",
        request_body,
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


# No33-4.PDSユーザドメイン名 文字列型、5文字、入力規則違反していない（URL利用可能文字のみの半角小英数記号５桁）
def test_update_case33_4():
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_public(pdsUserId="C8000000", pdsUserName="PDSユーザドメイン検証成功テスト", accessToken=None)
    print("accessToken:" + token_result["accessToken"])
    header = {"pdsUserId": "C8000000", "Content-Type": "application/json", "timeStamp": "2022/08/23 15:12:01.690", "accessToken": token_result["accessToken"], "Authorization": "Bearer " + token_result["jwt"]}

    response = client.put("/api/2.0/c0123/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No33-4.PDSユーザドメイン名 文字列型、20文字、入力規則違反していない（URL利用可能文字のみの半角小英数記号20桁）
def test_update_case33_5():
    DATA["tid"] = "transaction800031"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_public(pdsUserId="C8000001", pdsUserName="PDSユーザドメイン検証成功テスト", accessToken=None)
    print("accessToken:" + token_result["accessToken"])
    header = {"pdsUserId": "C8000001", "Content-Type": "application/json", "timeStamp": "2022/08/23 15:12:01.690", "accessToken": token_result["accessToken"], "Authorization": "Bearer " + token_result["jwt"]}

    response = client.put("/api/2.0/c0123456789012345678/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No33-6.PDSユーザID 値が設定されていない（空値）
def test_update_case33_6(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["pdsUserId"] = None
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
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

    # PDSユーザIDに誤りがある場合には、PDSユーザドメイン検証でエラーになってしまうので入力チェックまで到達できないことを確認
    # 入力チェックを直接呼び出してエラーになることを確認
    request_body = updateRouter.requestBody(tid=DATA["tid"], info=DATA["info"])
    response = updateRouter.input_check(
        trace_logger,
        "pds-user-create",
        request_body,
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


# No33-7.PDSユーザID 文字列型以外、7桁、C以外の文字で始まる
def test_update_case33_7(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["pdsUserId"] = '1234567'
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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
    request_body = updateRouter.requestBody(tid=DATA["tid"], info=DATA["info"])
    response = updateRouter.input_check(
        trace_logger,
        "pds-user-create",
        request_body,
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
            },
            {
                "errorCode": "020003",
                "message": response["errorInfo"][2]["message"]
            }
        ]
    }
    print(response)


# No33-8.PDSユーザID 文字列型、8桁、入力規則違反していない（C＋数値7桁）
def test_update_case33_8(create_header):
    header = create_header["header"]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No33-9.タイムスタンプ 値が設定されていない（空値）
def test_update_case33_9(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["timeStamp"] = None
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
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


# No33-10.タイムスタンプ 文字列型以外、22桁
def test_update_case33_10(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["timeStamp"] = '1234567890123456789012'
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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
    request_body = updateRouter.requestBody(tid=DATA["tid"], info=DATA["info"])
    response = updateRouter.input_check(
        trace_logger,
        "pds-user-create",
        request_body,
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


# No33-11.タイムスタンプ 文字列型、24桁、入力規則違反している　hh:mmがhhh:mm
def test_update_case33_11(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["timeStamp"] = '2022/09/30 12:000:00.000'
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No33-12.PDSユーザID 文字列型、23桁、入力規則違反していない　「yyyy/MM/dd hh:mm:ss.iii」
def test_update_case33_12(create_header):
    header = create_header["header"]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No33-13.アクセストークン 値が設定されていない（空値）
def test_update_case33_13(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["accessToken"] = None
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
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

    # アクセストークンが不正な場合には、アクセストークン検証処理でエラーが発生して、入力チェックに到達しないため、
    # 入力チェックを直接呼び出してエラーになることを確認
    request_body = updateRouter.requestBody(tid=DATA["tid"], info=DATA["info"])
    response = updateRouter.input_check(
        trace_logger,
        "pds-user-create",
        request_body,
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


# No33-14.アクセストークン 文字列型以外、201桁
def test_update_case33_14(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["accessToken"] = "123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901"
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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
    request_body = updateRouter.requestBody(tid=DATA["tid"], info=DATA["info"])
    response = updateRouter.input_check(
        trace_logger,
        "pds-user-create",
        request_body,
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


# No33-15.アクセストークン 文字列型、199桁、入力可能文字以外が含まれる（全角）
def test_update_case33_15(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["accessToken"] = "あ123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678"
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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
    request_body = updateRouter.requestBody(tid=DATA["tid"], info=DATA["info"])
    response = updateRouter.input_check(
        trace_logger,
        "pds-user-create",
        request_body,
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


# No33-16.アクセストークン 文字列型、200桁、入力可能文字のみ（半角英数字） [a-fA-F0-9]
def test_update_case33_16(create_header):
    header = create_header["header"]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No33-17.トランザクションID 値が設定されていない（空値）
def test_update_case33_17(create_header):
    header = create_header["header"]
    DATA["tid"] = None
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No33-18.トランザクションID 文字列型以外、37桁
def test_update_case33_18(create_header):
    header = create_header["header"]
    DATA["tid"] = 1234567890123456789012345678901234567
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020019",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020002",
                "message": response.json()["errorInfo"][1]["message"]
            }
        ]
    }
    print(response.json())


# No33-19.トランザクションID 文字列型、37桁、入力可能文字以外が含まれる(全角)
def test_update_case33_19(create_header):
    header = create_header["header"]
    DATA["tid"] = "あ1234567890abcdefghijklmnopqrstuvwxyz"
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No33-20.トランザクションID 文字列型、36桁、入力可能文字のみ（半角英数字） [a-zA-Z0-9]
def test_update_case33_20(create_header):
    header = create_header["header"]
    DATA["tid"] = "1234567890aBcDeFgHiJkLmNoPqRsTuVwXyZ"
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No33-21.検索用ユーザID 文字列型以外、37桁
def test_update_case33_21(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["info"]["userId"] = 1234567890123456789012345678901234567
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020019",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020002",
                "message": response.json()["errorInfo"][1]["message"]
            }
        ]
    }
    print(response.json())


# No33-22.検索用ユーザID 文字列型、36桁
def test_update_case33_22(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["info"]["userId"] = "12345aiueoAIUEOあいうえおアイウエオ亜伊宇江御+-*/%$"
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No33-23.検索用日時 文字列型以外、22桁、
def test_update_case33_23(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["info"]["saveDate"] = 1234567890123456789012
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020019",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020014",
                "message": response.json()["errorInfo"][1]["message"]
            }
        ]
    }
    print(response.json())


# No33-24.検索用日時 文字列型、24桁、入力規則違反している（形式は yyyy/MM/dd hh:mm:ss.iii でない　yyyyy/MMがyyyy/MMM）
def test_update_case33_24(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["info"]["saveDate"] = "2022/011/01 10:00:00.000"
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
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


# No33-25.検索用日時 文字列型、23桁、入力規則違反していない（形式は yyyy/MM/dd hh:mm:ss.iii である）　[0-9 :/.]
def test_update_case33_25(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["info"]["saveDate"] = "2022/11/01 10:00:00.000"
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No33-26.保存したいバイナリデータ 文字列型以外
def test_update_case33_26(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    # imageHashの要素数は一致している必要があるので設定
    data_copy["info"]["imageHash"] = "1234567890"
    data_copy["info"]["image"] = 1234567890
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020019",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No33-27.保存したいバイナリデータ 文字列以外の要素を含む配列
def test_update_case33_27(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    # imageHashの要素数は一致している必要があるので設定
    data_copy["info"]["imageHash"] = "1234567890"
    data_copy["info"]["image"] = [1234567890]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020019",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No33-28.保存したいバイナリデータ 文字列、14680065桁、入力可能文字以外が含まれる（全角）
def test_update_case33_28(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    # imageHashの要素数は一致している必要があるので設定
    data_copy["info"]["imageHash"] = "1234567890"
    f = open('tests/public/14MB.txt', 'r', encoding='UTF-8')
    text = f.read()
    data_copy["info"]["image"] = "あ" + text
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020020",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "030017",
                "message": response.json()["errorInfo"][1]["message"]
            }
        ]
    }
    print(response.json())


# No33-29.保存したいバイナリデータ 文字列、146800641桁、入力可能文字以外が含まれる（半角記号 +/=以外）
def test_update_case33_29(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    # imageHashの要素数は一致している必要があるので設定
    data_copy["info"]["imageHash"] = "1234567890"
    f = open('tests/public/140MB.txt', 'r', encoding='UTF-8')
    text = f.read()
    data_copy["info"]["image"] = "$" + text
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020020",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "030017",
                "message": response.json()["errorInfo"][1]["message"]
            },
            {
                "errorCode": "030018",
                "message": response.json()["errorInfo"][2]["message"]
            }
        ]
    }
    print(response.json())


# No33-30.保存したいバイナリデータ 文字列要素のみの配列、１つの要素が14680065桁、入力可能文字以外が含まれる（全角）
def test_update_case33_30(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    # imageHashの要素数は一致している必要があるので設定
    data_copy["info"]["imageHash"] = ["1234567890", "2345678901"]
    f = open('tests/public/14MB.txt', 'r', encoding='UTF-8')
    text = f.read()
    data_copy["info"]["image"] = ["あ" + text, "い" + text]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020020",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "030017",
                "message": response.json()["errorInfo"][1]["message"]
            }
        ]
    }
    print(response.json())


# No33-31.保存したいバイナリデータ 文字列要素のみの配列、全ての要素の合計が146800641桁、入力可能文字以外が含まれる（半角記号 +/=以外）
def test_update_case33_31(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    # imageHashの要素数は一致している必要があるので設定
    data_copy["info"]["imageHash"] = ["1234567890", "2345678901", "3456789012", "4567890123", "5678901234", "6789012345", "7890123456", "8901234567", "9012345678", "0123456789", "1234567890"]
    f = open('tests/public/14MB.txt', 'r', encoding='UTF-8')
    text = f.read()
    data_copy["info"]["image"] = ["$" + text, text, text, text, text, text, text, text, text, text]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020020",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "030017",
                "message": response.json()["errorInfo"][1]["message"]
            }
        ]
    }
    print(response.json())


# No33-32.保存したいバイナリデータ 文字列、14680064桁、入力可能文字のみ　[a-zA-Z0-9+/=]
def test_update_case33_32(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    # imageHashの要素数は一致している必要があるので設定
    data_copy["info"]["imageHash"] = "1234567890"
    f = open('tests/public/14MB.txt', 'r', encoding='UTF-8')
    text = f.read()
    data_copy["info"]["image"] = text
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    out_logger.info("テストリクエスト送信")
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    out_logger.info("テストレスポンス取得")
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No33-33.保存したいバイナリデータ 文字列要素のみの配列、全ての要素の合計が146800640桁、入力可能文字のみ　[a-zA-Z0-9+/=]
def test_update_case33_33(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    # imageHashの要素数は一致している必要があるので設定
    data_copy["info"]["imageHash"] = ["1234567890", "2345678901", "3456789012", "4567890123", "5678901234", "6789012345", "7890123456", "8901234567", "9012345678", "0123456789", "1234567890"]
    f = open('tests/public/14MB.txt', 'r', encoding='UTF-8')
    text = f.read()
    data_copy["info"]["image"] = [text, text, text, text, text, text, text, text, text, text]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No33-34.保存したいバイナリデータのハッシュ値 文字列型以外
def test_update_case33_34(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    # imageの要素数は一致している必要があるので設定
    data_copy["info"]["image"] = "1234567890"
    data_copy["info"]["imageHash"] = 1234567890
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020019",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No33-35.保存したいバイナリデータのハッシュ値 文字列型以外の要素を含む配列
def test_update_case33_35(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    # imageの要素数は一致している必要があるので設定
    data_copy["info"]["image"] = ["1234567890", "2345678901"]
    data_copy["info"]["imageHash"] = [1234567890, 2345678901]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020019",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No33-36.保存したいバイナリデータのハッシュ値 文字列型、入力可能文字以外が含まれる（全角）
def test_update_case33_36(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    # imageの要素数は一致している必要があるので設定
    data_copy["info"]["image"] = "1234567890"
    data_copy["info"]["imageHash"] = "あ" + "1234567890"
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020020",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No33-37.保存したいバイナリデータのハッシュ値 文字列型の要素のみの配列、入力可能文字以外が含まれる（半角記号）
def test_update_case33_37(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    # imageの要素数は一致している必要があるので設定
    data_copy["info"]["image"] = ["1234567890", "2345678901"]
    data_copy["info"]["imageHash"] = ["1234567890", "$" + "2345678901"]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020020",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No33-38.保存したいバイナリデータのハッシュ値 文字列型、入力可能文字のみ　[a-zA-Z0-9]
def test_update_case33_38(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    # imageの要素数は一致している必要があるので設定
    data_copy["info"]["image"] = "abc1234567890"
    data_copy["info"]["imageHash"] = "abc1234567890"
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No33-39.保存したいバイナリデータのハッシュ値 文字列型、入力可能文字のみ　[a-zA-Z0-9]
def test_update_case33_39(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    # imageの要素数は一致している必要があるので設定
    data_copy["info"]["image"] = ["abc1234567890", "abc2345678901"]
    data_copy["info"]["imageHash"] = ["abc1234567890", "abc2345678901"]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020020",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No33-40.セキュリティレベル 文字列型以外、3桁
def test_update_case33_40(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["info"]["secureLevel"] = 123
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020019",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020002",
                "message": response.json()["errorInfo"][1]["message"]
            }
        ]
    }
    print(response.json())


# No33-41.セキュリティレベル 文字列型、3桁、入力可能文字以外を含む（半角スペース）
def test_update_case33_41(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["info"]["secureLevel"] = "1 2"
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
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


# No33-42.セキュリティレベル 文字列型、2桁、入力可能文字以外を含む
def test_update_case33_42(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["info"]["secureLevel"] = "あi"
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No33-43.保存したいデータ 文字列型か辞書型以外、5001桁
def test_update_case33_43(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["info"]["data"] = 123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020019",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020002",
                "message": response.json()["errorInfo"][1]["message"]
            }
        ]
    }
    print(response.json())


# No33-44.保存したいデータ 文字列型、5001桁
def test_update_case33_44(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["info"]["data"] = "123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901"
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
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


# No33-45.保存したいデータ 文字列型、5001桁
def test_update_case33_45(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["info"]["data"] = {"key": "value12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345"}
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
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


# No33-46.保存したいデータ 文字列型、5000桁
def test_update_case33_46(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["info"]["data"] = "12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890"
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No33-47.保存したいデータ 辞書型、5000桁
def test_update_case33_47(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["info"]["data"] = {"key": "value1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234"}
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No34.「引数．ヘッダパラメータ．PDSユーザID」と「引数．PDSユーザドメイン情報．PDSユーザID」の値が一致しない場合、「変数．エラー情報リスト」にエラー情報を追加する
def test_update_case34(mocker: MockerFixture, create_header):
    # 返却値の変更
    mocker.patch("util.commonUtil.CommonUtilClass.check_pds_user_domain").return_value = {"result": True, "pdsUserInfo": {"pdsUserId": "C1234567"}}
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["pdsUserId"] = 'C9876543'
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No35.「引数．リクエストボディ．情報．保存したいバイナリデータ」、「引数．リクエストボディ．情報．保存したいバイナリデータのハッシュ値」の要素数が不一致の場合、「変数．エラー情報リスト」にエラー情報を追加する(「引数．リクエストボディ．情報．保存したいバイナリデータ」、「引数．リクエストボディ．情報．保存したいバイナリデータのハッシュ値」がstringの場合、要素数1のarrayに変換する)
# No37.変数．エラー情報がある
def test_update_case35(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    # imageの要素数は一致している必要があるので設定
    data_copy["info"]["image"] = ["abc1234567890", "abc2345678901"]
    data_copy["info"]["imageHash"] = "abc1234567890"
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "030010",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No36.変数．エラー情報がない
def test_update_case36(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tid"] = "transaction800056"
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No38.PDSユーザDB接続準備処理に失敗する
@pytest.mark.asyncio
async def test_update_case38(mocker: MockerFixture, create_header):
    header = create_header["header"]
    # 必要な情報を作成する
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    request_body = modelRequestBody(tid="transaction1", info=DATA["info"])
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
    mongodb_key = "633598810bb9f9414418f991"
    pds_user_db_secret_info = {
        "host": "pds-c0000000.cluster-ct7qlfhnwver.ap-northeast-1.rds.amazonaws.com",
        "port": "5432",
        "username": "postgres",
        "password": "9qj5LHTj4V6RozYkoDzo",
    }
    request_info = Request({"type": "http", "headers": {}, "method": "post", "path": ""})
    get_user_profile_data_result = [("transaction1", "633598810bb9f9414418f991", True, True)]
    update_model = updateModel(trace_logger, Request({"type": "http", "headers": {}, "method": "post", "path": ""}), header["pdsUserId"], {}, "pds-user-create")
    # モック
    mocker.patch("util.postgresDbUtil.PostgresDbUtilClass.create_connection").side_effect = Exception("test-exception")
    with pytest.raises(PDSException) as e:
        await update_model.update_user_info(
            request_body,
            pds_user_info,
            mongodb_key,
            pds_user_db_secret_info,
            request_info,
            get_user_profile_data_result
        )
    assert e.value.args[0] == {
        "errorCode": "999999",
        "message": e.value.args[0]["message"]
    }
    print(e)


# No39.PDSユーザDB接続準備処理に成功する
# No41.個人情報バイナリ情報取得処理が成功する
def test_update_case39(create_header):
    header = create_header["header"]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No40.個人情報バイナリ情報取得処理が失敗する
# No42.共通エラーチェック処理が成功（エラー情報有り）
def test_update_case40(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "USER_PROFILE_BINARY_SEARCH_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No43-1.パターン１ DBと入力値の要素数が同じ DB3件、入力3件
def test_update_case43_1(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction110001"
    DATA["info"]["image"] = ["image4", "image5", "image6"]
    DATA["info"]["imageHash"] = ["imageHash4", "imageHash5", "imageHash6"]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No43-2.パターン２ DBと入力値の要素数が同じ DB3件、入力3件 None含む
def test_update_case43_2(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction110002"
    DATA["info"]["image"] = ["image4", None, "image6"]
    DATA["info"]["imageHash"] = ["imageHash4", None, "imageHash6"]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No43-3.パターン３ DBと入力値の要素数が同じ DB3件、入力3件 False含む
def test_update_case43_3(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction110003"
    DATA["info"]["image"] = ["image4", False, "image6"]
    DATA["info"]["imageHash"] = ["imageHash4", False, "imageHash6"]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No43-4.パターン４ DBと入力値の要素数が同じ DB3件、入力3件 Null、False含む
def test_update_case43_4(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction110004"
    DATA["info"]["image"] = ["image4", None, False]
    DATA["info"]["imageHash"] = ["imageHash4", None, False]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No43-5.パターン５ DBと入力値の要素数が同じ DB3件、入力3件 Null、False含む
def test_update_case43_5(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction110005"
    DATA["info"]["image"] = [None, None, False]
    DATA["info"]["imageHash"] = [None, None, False]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No43-6.パターン６ DBと入力値の要素数が同じ DB3件、入力3件 Null、False含む
def test_update_case43_6(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction110011"
    DATA["info"]["image"] = ["image4", "image5", "image6"]
    DATA["info"]["imageHash"] = ["imageHash4", "imageHash5", "imageHash6"]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No43-7.パターン７ DBと入力値の要素数が同じ DB3件、入力3件 Null、False含む
def test_update_case43_7(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction110012"
    DATA["info"]["image"] = ["image4", None, "image6"]
    DATA["info"]["imageHash"] = ["imageHash4", None, "imageHash6"]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No43-8.パターン８ DBと入力値の要素数が同じ DB3件、入力3件 Null、False含む
def test_update_case43_8(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction110013"
    DATA["info"]["image"] = ["image4", False, "image6"]
    DATA["info"]["imageHash"] = ["imageHash4", False, "imageHash6"]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No43-9.パターン９ DBと入力値の要素数が同じ DB3件、入力3件 Null、False含む
def test_update_case43_9(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction110014"
    DATA["info"]["image"] = ["image4", None, False]
    DATA["info"]["imageHash"] = ["imageHash4", None, False]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No43-10.パターン１０ DBと入力値の要素数が同じ DB3件、入力3件 Null、False含む
def test_update_case43_10(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction110015"
    DATA["info"]["image"] = [None, None, False]
    DATA["info"]["imageHash"] = [None, None, False]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No43-11.パターン１１ DBと入力値の要素数が同じ DB3件、入力3件 Null、False含む
def test_update_case43_11(create_header):
    header = create_header["header"]
    request_body = {
        "tid": "transaction110021",
        "info": {
            "userId": "transaction10000",
            "saveDate": "2022/09/26 10:00:00.000",
            "data": "{\"aaa\": \"bbb\"}",
            "secureLevel": "2"
        }
    }
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(request_body))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No43-12.パターン１２ DBと入力値の要素数が同じ DB3件、入力3件 Null、False含む
def test_update_case43_12(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction110031"
    DATA["info"]["image"] = ["image4", "image5"]
    DATA["info"]["imageHash"] = ["imageHash4", "imageHash5"]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No43-13.パターン１３ DBと入力値の要素数が同じ DB3件、入力3件 Null、False含む
def test_update_case43_13(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction110032"
    DATA["info"]["image"] = ["image4", None]
    DATA["info"]["imageHash"] = ["imageHash4", None]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No43-14.パターン１４ DBと入力値の要素数が同じ DB3件、入力3件 Null、False含む
def test_update_case43_14(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction110033"
    DATA["info"]["image"] = ["image4", False]
    DATA["info"]["imageHash"] = ["imageHash4", False]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No43-15.パターン１５ DBと入力値の要素数が同じ DB3件、入力3件 Null、False含む
def test_update_case43_15(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction110034"
    DATA["info"]["image"] = [None, False]
    DATA["info"]["imageHash"] = [None, False]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No43-16.パターン１６ DBと入力値の要素数が同じ DB3件、入力3件 Null、False含む
def test_update_case43_16(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction110041"
    DATA["info"]["image"] = ["image4", "image5", "image6"]
    DATA["info"]["imageHash"] = ["imageHash4", "imageHash5", "imageHash6"]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No43-17.パターン１7 DBと入力値の要素数が同じ DB3件、入力3件 Null、False含む
def test_update_case43_17(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction110042"
    DATA["info"]["image"] = ["image4", None, "image6"]
    DATA["info"]["imageHash"] = ["imageHash4", None, "imageHash6"]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No43-18.パターン１８DBと入力値の要素数が同じ DB3件、入力3件 Null、False含む
def test_update_case43_18(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction110043"
    DATA["info"]["image"] = ["image4", False, "image6"]
    DATA["info"]["imageHash"] = ["imageHash4", False, "imageHash6"]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No43-19.パターン１９ DBと入力値の要素数が同じ DB3件、入力3件 Null、False含む
def test_update_case43_19(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction110044"
    DATA["info"]["image"] = [None, False, "image6"]
    DATA["info"]["imageHash"] = [None, False, "imageHash6"]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No43-20.パターン２０ DBと入力値の要素数が同じ DB3件、入力3件 Null、False含む
def test_update_case43_20(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction110045"
    DATA["info"]["image"] = [None, None, False]
    DATA["info"]["imageHash"] = [None, None, False]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No44.SQS実行フラグ定義処理が成功する
# No48.「変数．調整後保存したいデータ」の内容にFalse以外を含む
def test_update_case44(create_header):
    header = create_header["header"]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No45.個人情報更新トランザクションのトランザクション作成処理が失敗する
#      トランザクション作成については、コネクション作成時にライブラリが自動作成するので確認不可


# No46.個人情報更新トランザクションのトランザクション作成処理が成功する
#      トランザクション作成については、コネクション作成時にライブラリが自動作成するので確認不可


# No47.「変数．調整後保存したいデータ」の内容がすべてfalse
# No71MongoDB接続準備処理成功（接続に成功する 東京a）
# No76.MongoDB個人情報登録トランザクションのMongoDBトランザクション作成処理が成功する
def test_update_case47(create_header):
    header = create_header["header"]
    DATA["info"]["image"] = [False, False]
    DATA["info"]["imageHash"] = [False, False]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No49.「変数．調整後配列データ」の要素数が0
def test_update_case49(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction90501"
    DATA["info"]["image"] = None
    DATA["info"]["imageHash"] = None
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No50.「変数．調整後配列データ」の要素数が0以外
# No51.「変数．調整後配列データ[変数．調整後配列データループ数]．保存したいバイナリデータ」がfalse
# No52.「変数．調整後配列データ[変数．調整後配列データループ数]．保存したいバイナリデータ」がfalse以外
# No54.個人情報バイナリデータスキップ処理が成功する
# No55.「変数．調整後配列データ[変数．調整後配列データループ数]．保存したいバイナリデータ」がNullか空文字
# No56.「変数．調整後配列データ[変数．調整後配列データループ数]．保存したいバイナリデータ」がNullか空文字以外
# No58.個人情報バイナリデータ論理削除処理が成功する
# No59.「変数．SQS実行フラグ」がfalseの場合Trueに変更されること
# No60.バイナリデータ情報作成処理が成功する
# No62.個人情報バイナリデータ登録処理が成功する
# No68.個人情報バイナリデータ更新処理が成功する
def test_update_case50(create_header):
    header = create_header["header"]
    DATA["info"]["image"] = [False, "", "aiueo"]
    DATA["info"]["imageHash"] = [False, "", "12345"]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No53.個人情報バイナリデータスキップ処理が失敗する
def test_update_case53(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["info"]["image"] = [False, "aiueo"]
    DATA["info"]["imageHash"] = [False, "12345"]
    mocker.patch.object(SqlConstClass, "UPDATE_USER_PROFILE_BINARY_SKIP_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No57.個人情報バイナリデータ論理削除処理が失敗する
def test_update_case57(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["info"]["image"] = ["", "aiueo"]
    DATA["info"]["imageHash"] = ["", "12345"]
    mocker.patch.object(SqlConstClass, "UPDATE_USER_PROFILE_BINARY_LOGICAL_DELETE_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No61.個人情報バイナリデータ登録処理が失敗する
# No63.共通エラーチェック処理が成功（エラー情報有り）
def test_update_case61(mocker: MockerFixture, create_header):
    header = create_header["header"]
    # 登録済みのUUIDを返却する
    mocker.patch("util.commonUtil.get_uuid_no_hypen").return_value = "597b54455ca245a4ad8c766e58cd21d2"
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": response.json()["errorInfo"]
    }
    print(response.json())


# No64.個人情報バイナリデータ論理削除処理が失敗する
def test_update_case64(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "UPDATE_USER_PROFILE_BINARY_LOGICAL_DELETE_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No65.個人情報バイナリデータ論理削除処理が成功する
# No66.「変数．SQS実行フラグ」がfalse
def test_update_case65(create_header):
    header = create_header["header"]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No67.個人情報バイナリデータ更新処理が失敗する
# No69.共通エラーチェック処理が成功（エラー情報有り）
def test_update_case67(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "UPDATE_USER_PROFILE_BINARY_VALID_FLG_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No70.MongoDB接続準備処理失敗（接続に失敗する）
def test_update_case70(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_public(pdsUserId="C5000005", pdsUserName="MongoユーザDB接続NGテスト", accessToken=None)
    print("accessToken:" + token_result["accessToken"])

    # 存在しないMongoDB接続情報を持ったPDSユーザを設定する
    header = {
        "pdsUserId": "C5000005",
        "Content-Type": "application/json",
        "timeStamp": "2022/08/23 15:12:01.690",
        "accessToken": token_result["accessToken"],
        "Authorization": "Bearer " + token_result["jwt"]
    }
    response = client.put("/api/2.0/mongo-ng/transaction", headers=header, data=json.dumps(DATA))
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


# No.72MongoDB接続準備処理成功（接続に成功する 東京c）
def test_update_case72(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_public(pdsUserId="C5000002", pdsUserName="MongoユーザDB（東京c）接続OKテスト", accessToken=None)
    print("accessToken:" + token_result["accessToken"])

    # 東京cのみ正常な接続情報を持っているPDSユーザIDを設定する
    header = {
        "pdsUserId": "C5000002",
        "Content-Type": "application/json",
        "timeStamp": "2022/08/23 15:12:01.690",
        "accessToken": token_result["accessToken"],
        "Authorization": "Bearer " + token_result["jwt"]
    }

    response = client.put("/api/2.0/mongo-ok-tokyo-c/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No.73MongoDB接続準備処理成功（接続に成功する 大阪a）
def test_update_case73(mocker: MockerFixture, create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_public(pdsUserId="C5000003", pdsUserName="MongoユーザDB（大阪a）接続OKテスト", accessToken=None)
    print("accessToken:" + token_result["accessToken"])

    # 大阪aのみ正常な接続情報を持っているPDSユーザIDを設定する
    header = {
        "pdsUserId": "C5000003",
        "Content-Type": "application/json",
        "timeStamp": "2022/08/23 15:12:01.690",
        "accessToken": token_result["accessToken"],
        "Authorization": "Bearer " + token_result["jwt"]
    }
    # 大阪に配置されてる状態と同じにする
    mocker.patch.object(SystemConstClass, "REGION", {"TOKYO": "ap-northeast-3", "OSAKA": "ap-northeast-1"})
    response = client.put("/api/2.0/mongo-ok-osaka-a/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No.74MongoDB接続準備処理成功（接続に成功する 大阪c）
def test_update_case74(mocker: MockerFixture, create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_public(pdsUserId="C5000004", pdsUserName="MongoユーザDB（大阪c）接続OKテスト", accessToken=None)
    print("accessToken:" + token_result["accessToken"])

    # 大阪cのみ正常な接続情報を持っているPDSユーザIDを設定する
    header = {
        "pdsUserId": "C5000004",
        "Content-Type": "application/json",
        "timeStamp": "2022/08/23 15:12:01.690",
        "accessToken": token_result["accessToken"],
        "Authorization": "Bearer " + token_result["jwt"]
    }
    # 大阪に配置されてる状態と同じにする
    mocker.patch.object(SystemConstClass, "REGION", {"TOKYO": "ap-northeast-3", "OSAKA": "ap-northeast-1"})
    response = client.put("/api/2.0/mongo-ok-osaka-c/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No75.MongoDB個人情報登録トランザクションのMongoDBトランザクション作成処理が失敗する
def test_update_case75(mocker: MockerFixture, create_header):
    header = create_header["header"]
    # ErrorInfo
    mocker.patch.object(MongoDbClass, "create_transaction", side_effect=Exception('testException'))
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No77.「リクエストのリクエストボディ．情報．保存したいデータ」がJson形式でない
def test_update_case77(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["info"]["data"] = "aiueo"
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No78.「リクエストのリクエストボディ．情報．保存したいデータ」がJson形式
def test_update_case78(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No79.MongoDB登録処理が失敗する
# No81.共通エラーチェック処理が成功（エラー情報有り）
def test_create_case79(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(Collection, "insert_one", side_effect=PyMongoError('testException'))
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "992001",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No80.MongoDB登録処理が成功する
def test_create_case80(create_header):
    header = create_header["header"]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No82.「引数．個人情報検索結果リスト[2]」がfalse
def test_create_case82(create_header):
    header = create_header["header"]
    # トランザクションIDでJSONフラグがFalseのものを指定
    data_copy = DATA.copy()
    data_copy["tid"] = "transaction2"
    data_copy["info"]["data"] = "aiueo"
    data_copy["info"]["image"] = [None]
    data_copy["info"]["imageHash"] = [None]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No83.「引数．個人情報検索結果リスト[2]」がTrue
def test_create_case83(create_header):
    header = create_header["header"]
    # トランザクションIDでJSONフラグがTrueのものを指定
    data_copy = DATA.copy()
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No84.MongoDB削除処理が失敗する
# No86.共通エラーチェック処理が成功（エラー情報有り）
def test_create_case84(mocker: MockerFixture, create_header):
    header = create_header["header"]
    # トランザクションIDでJSONフラグがFalseのものを指定
    data_copy = DATA.copy()
    mocker.patch.object(Collection, "delete_one", side_effect=PyMongoError('testException'))
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "992001",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No85.MongoDB削除処理が成功する
def test_create_case85(create_header):
    header = create_header["header"]
    # トランザクションIDでJSONフラグがFalseのものを指定
    data_copy = DATA.copy()
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No87.個人情報テーブル更新処理が失敗する
# No89.共通エラーチェック処理が成功（エラー情報有り）
def test_update_case87(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "UPDATE_USER_PROFILE_SQL_PREFIX", """ SELECT * FROM AAAAAA; """)
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No88.個人情報テーブル更新処理が成功する
# No91.MongoDB個人情報登録トランザクションのコミット処理が成功する
# No93.個人情報登録トランザクションのコミット処理が成功する
# No94.変数．エラー情報がない
def test_update_case88(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["info"]["userId"] = "transaction105"
    data_copy["info"]["saveDate"] = "2022/10/01 10:10:10.100"
    data_copy["info"]["data"] = "{\"aaa\": \"ccc\"}"
    data_copy["info"]["image"] = ["abcdef", "234567"]
    data_copy["info"]["imageHash"] = ["abcd", "1234"]
    data_copy["info"]["secureLevel"] = "3"
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No90.MongoDB個人情報登録トランザクションのコミット処理が失敗する
def test_update_case90(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(ClientSession, "commit_transaction", side_effect=Exception('testException'))
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No92.個人情報登録トランザクションのコミット処理が失敗する
def test_update_case92(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(PostgresDbUtilClass, "commit_transaction", side_effect=[True, True, True, True, True, True, Exception('testException')])
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No95.「引数．調整後の配列データ．バイナリデータ配列インデックス」がNull
# No100.変数．エラー情報がない
def test_update_case95(create_header):
    header = create_header["header"]
    DATA["info"]["image"] = ["aiueo", False]
    DATA["info"]["imageHash"] = ["12345", False]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No96.「引数．調整後の配列データ．バイナリデータ配列インデックス」がNull以外
# No98.個人情報バイナリデータ更新処理が成功する
def test_update_case96(create_header):
    header = create_header["header"]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    DATA["info"]["image"] = [False, "aiueo"]
    DATA["info"]["imageHash"] = [False, "12345"]
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No97.個人情報バイナリデータ更新処理が失敗する
# No99.共通エラーチェック処理が成功（エラー情報有り）
def test_update_case97(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["info"]["image"] = [False, "aiueo"]
    DATA["info"]["imageHash"] = [False, "12345"]
    mocker.patch.object(SqlConstClass, "UPDATE_USER_PROFILE_BINARY_SKIP_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No101.個人情報バイナリデータ論理削除処理が失敗する
# No103.共通エラーチェック処理が成功（エラー情報有り）
def test_update_case101(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "UPDATE_USER_PROFILE_BINARY_LOGICAL_DELETE_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No102.個人情報バイナリデータ論理削除処理が成功する
# No104.変数．エラー情報がない
def test_update_case102(create_header):
    header = create_header["header"]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No105.ロールバック処理が失敗する
# 　　　ロールバック処理の失敗方法が不明


# No106.ロールバック処理が成功する
def test_update_case106(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "UPDATE_USER_PROFILE_BINARY_LOGICAL_DELETE_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No107.共通エラーチェック処理が成功（エラー情報有り）
# 　　　ロールバック処理の失敗方法が不明


# No108.変数．エラー情報がない
def test_update_case108(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "UPDATE_USER_PROFILE_BINARY_LOGICAL_DELETE_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No109.MongoDBロールバック処理が失敗する
def test_update_case109(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tid"] = "transaction3"
    mocker.patch.object(Collection, "delete_object_id", side_effect=Exception('testException'))
    mocker.patch.object(ClientSession, "rollback_transaction", side_effect=Exception('testException'))
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
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


# No110.MongoDBロールバック処理が成功する
def test_update_case110(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tid"] = "transaction3"
    mocker.patch.object(Collection, "delete_object_id", side_effect=Exception('testException'))
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
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


# No111.MongoDBロールバック処理が失敗する
def test_update_case111(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tid"] = "transaction3"
    mocker.patch.object(Collection, "delete_object_id", side_effect=Exception('testException'))
    mocker.patch.object(ClientSession, "rollback_transaction", side_effect=Exception('testException'))
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
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


# No112.MongoDBロールバック処理が成功する
def test_update_case112(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tid"] = "transaction3"
    mocker.patch.object(Collection, "delete_object_id", side_effect=Exception('testException'))
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
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


# No113.更新後のデータが140MBを超過する場合
def test_update_case113(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tid"] = "transaction110101"
    DATA["info"]["image"] = [False, False, False, False, False, False, False, False, False, False, "a"]
    DATA["info"]["imageHash"] = [False, False, False, False, False, False, False, False, False, False, "imageHash11"]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "030018",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No114.更新後のデータが140MBを超過しない場合
def test_update_case114(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tid"] = "transaction110102"
    f = open('tests/public/14MB.txt', 'r', encoding='UTF-8')
    text = f.read()
    DATA["info"]["image"] = [False, False, False, False, False, False, False, False, False, None, text]
    DATA["info"]["imageHash"] = [False, False, False, False, False, False, False, False, False, None, "imageHash11"]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No115.PDSユーザ更新の項目がすべて未入力の場合
def test_update_case115(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body = {
        "tid": "transaction1",
        "info": {}
    }
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(request_body))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No116.PDSユーザ更新の項目に未入力の項目がある場合
def test_update_case116(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body = {
        "tid": "transaction1",
        "info": {
            "userId": "transaction10001",
            "saveDate": "2022/11/11 10:00:00.000",
            "data": "{\"aaa\": \"ccc\"}"
        }
    }
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(request_body))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No117.PDSユーザ更新の項目に未入力の項目がない場合
def test_update_case117(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body = {
        "tid": "transaction1",
        "info": {
            "userId": "transaction10101",
            "saveDate": "2022/12/12 10:00:00.000",
            "data": "{\"aaa\": \"ddd\"}",
            "secureLevel": "5"
        }
    }
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(request_body))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No118.新規登録のバイナリデータが存在しない場合（削除、スキップのみ）
def test_update_case118(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["info"]["image"] = [False, False, None]
    DATA["info"]["imageHash"] = [False, False, None]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No119.新規登録のバイナリデータが存在する場合
def test_update_case119(mocker: MockerFixture, create_header):
    header = create_header["header"]
    response = client.put("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())
