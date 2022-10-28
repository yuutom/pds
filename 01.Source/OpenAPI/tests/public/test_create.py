import random
import string
from fastapi.testclient import TestClient
from util.commonUtil import CommonUtilClass
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
from pymongo.errors import PyMongoError
from util.postgresDbUtil import PostgresDbUtilClass
from pymongo.collection import Collection
from pymongo.client_session import ClientSession
import routers.public.createRouter as createRouter
from models.public.createModel import createModel
from models.public.createModel import requestBody as modelRequestBody

client = TestClient(app)
EXEC_NAME: str = "create"

BEARER = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0Zk9wZXJhdG9ySWQiOiJsLXRlc3QiLCJ0Zk9wZXJhdG9yTmFtZSI6Ilx1MzBlZFx1MzBiMFx1MzBhNFx1MzBmM1x1MzBjNlx1MzBiOVx1MzBjOCIsInRmT3BlcmF0b3JQYXNzd29yZFJlc2V0RmxnIjpmYWxzZSwiYWNjZXNzVG9rZW4iOiJiZGE4ZGY3OThiYzViZGZhMWZkODIyNmRiYmQ0OTMyMTY5ZmY5MjAzNWM0YzFlY2FjZjY2OGUyYzk2ZjAwZThlZTUxNTBiNGM0NTc0NjlkN2I4YmY1NzIxZDZlM2NiNzFiY2RiYzA3ODRiYzcyZWVlNjk1OGE3NTBiMWJkMWEzZWFmZWQ0OWFhNWU0ODZjYzQyZmM3OWNhMWY3MGQzZmM3Yzc0YzE5NjM3ODUzMjRhZDRhNGM0NjkxOGE4NjQ1N2ZiODE3NDU1MCIsImV4cCI6MTY2MTc0NjY3MX0.LCRjPEqKMkRQ_phaYnO7S7pd3SU_rgon-wsX14DBsPA"
ACCESS_TOKEN = "bda8df798bc5bdfa1fd8226dbbd4932169ff92035c4c1ecacf668e2c96f00e8ee5150b4c457469d7b8bf5721d6e3cb71bcdbc0784bc72eee6958a750b1bd1a3eafed49aa5e486cc42fc79ca1f70d3fc7c74c1963785324ad4a4c46918a86457fb8174550"
HEADER = {"pdsUserId": "C9876543", "Content-Type": "application/json", "timeStamp": "2022/08/23 15:12:01.690", "accessToken": ACCESS_TOKEN, "Authorization": "Bearer " + BEARER}
DATA = {
    "tid": "transaction10000",
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
    yield {
        "header": {
            "pdsUserId": "C9876543",
            "Content-Type": "application/json",
            "timeStamp": "2022/08/23 15:12:01.690",
            "accessToken": token_result["accessToken"],
            "Authorization": "Bearer " + token_result["jwt"]
        }
    }


# No1.事前処理が失敗する
def test_create_case1(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.commonUtil.CommonUtilClass.check_pds_user_domain").side_effect = Exception('testException')
    header = create_header["header"]
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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
def test_create_case2(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No3.PDSユーザDB接続準備処理に失敗する
def test_create_case3(mocker: MockerFixture, create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_public(pdsUserId="C5000000", pdsUserName="PDSユーザDB接続NGテスト", accessToken=None)
    print("accessToken:" + token_result["accessToken"])

    header = {
        "pdsUserId": "C5000000",
        "Content-Type": "application/json",
        "timeStamp": "2022/08/23 15:12:01.690",
        "accessToken": token_result["accessToken"],
        "Authorization": "Bearer " + token_result["jwt"]
    }

    response = client.post("/api/2.0/pds-user-create-ng/transaction", headers=header, data=json.dumps(DATA))

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
def test_create_case4(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10004"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No5.個人情報取得処理の取得件数が0件以外
def test_create_case5(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction1"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No6.個人情報取得処理が失敗する
def test_create_case6(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "USER_PROFILE_SELECT_CHECK_SQL", """ SELECT * FROM AAAAAA; """)
    DATA["tid"] = "transaction10006"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No.7個人情報取得処理が成功する
def test_create_case7(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10007"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No8.共通エラーチェック処理が成功（エラー情報有り）
def test_create_case8(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "USER_PROFILE_SELECT_CHECK_SQL", """ SELECT * FROM AAAAAA; """)
    DATA["tid"] = "transaction10008"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No.9「リクエストのリクエストボディ．保存したいデータ」がJson形式である
def test_create_case9(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10009"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No.10「リクエストのリクエストボディ．保存したいデータ」がJson形式ではない
def test_create_case10(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10010"
    DATA["info"]["data"] = "aiueo"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No.11MongoDB接続準備処理失敗（接続に失敗する）
def test_create_case11(create_header):
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

    DATA["tid"] = "transaction10011"
    response = client.post("/api/2.0/mongo-ng/transaction", headers=header, data=json.dumps(DATA))
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


# No.12MongoDB接続準備処理成功（接続に成功する 東京a）
def test_create_case12(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_public(pdsUserId="C5000001", pdsUserName="MongoユーザDB（東京a）接続OKテスト", accessToken=None)
    print("accessToken:" + token_result["accessToken"])

    # 東京aのみ正常な接続情報を持っているPDSユーザIDを設定する
    header = {
        "pdsUserId": "C5000001",
        "Content-Type": "application/json",
        "timeStamp": "2022/08/23 15:12:01.690",
        "accessToken": token_result["accessToken"],
        "Authorization": "Bearer " + token_result["jwt"]
    }

    DATA["tid"] = "transaction10012"
    response = client.post("/api/2.0/mongo-ok-tokyo-a/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No.13MongoDB接続準備処理成功（接続に成功する 大阪a）
def test_create_case13(mocker: MockerFixture, create_header):
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
    DATA["tid"] = "transaction10013"
    response = client.post("/api/2.0/mongo-ok-osaka-a/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No.14MongoDB接続準備処理成功（接続に成功する 東京c）
def test_create_case14(create_header):
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

    DATA["tid"] = "transaction10014"
    response = client.post("/api/2.0/mongo-ok-tokyo-c/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No.15MongoDB接続準備処理成功（接続に成功する 大阪c）
def test_create_case15(mocker: MockerFixture, create_header):
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
    DATA["tid"] = "transaction10015"
    # 大阪に配置されてる状態と同じにする
    mocker.patch.object(SystemConstClass, "REGION", {"TOKYO": "ap-northeast-3", "OSAKA": "ap-northeast-1"})
    response = client.post("/api/2.0/mongo-ok-osaka-c/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No.16MongoDB個人情報登録トランザクションのMongoDBトランザクション作成処理が失敗する
def test_create_case16(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10016"
    # ErrorInfo
    mocker.patch.object(MongoDbClass, "create_transaction", side_effect=Exception('testException'))
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No17.MongoDB個人情報登録トランザクションのMongoDBトランザクション作成処理が成功する
def test_create_case17(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10017"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No18.MongoDB登録処理が失敗する
def test_create_case18(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10018"
    mocker.patch.object(Collection, "insert_one", side_effect=PyMongoError('testException'))
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No19.MongoDB登録処理が成功する
def test_create_case19(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10019"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No20.共通エラーチェック処理が成功（エラー情報有り）
def test_create_case20(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10020"
    mocker.patch.object(Collection, "insert_one", side_effect=PyMongoError('testException'))
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No21.個人情報登録トランザクションのトランザクション作成処理が失敗する
# コネクション作成時に自動作成のためテストケースなし

# No22.個人情報登録トランザクションのトランザクション作成処理が成功する
# コネクション作成時に自動作成のためテストケースなし


# No23.個人情報登録処理が失敗する
def test_create_case23(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10023"
    mocker.patch.object(SqlConstClass, "USER_PROFILE_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No24.個人情報登録処理が成功する
def test_create_case24(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10024"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No25.共通エラーチェック処理が成功（エラー情報有り）
def test_create_case25(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10025"
    mocker.patch.object(SqlConstClass, "USER_PROFILE_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No26.MongoDB個人情報登録トランザクションのコミット処理が失敗する
def test_create_case26(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10026"
    mocker.patch.object(ClientSession, "commit_transaction", side_effect=Exception('testException'))
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No27.MongoDB個人情報登録トランザクションのコミット処理が成功する
def test_create_case27(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10027"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No28.個人情報登録トランザクションのコミット処理が失敗する
def test_create_case28(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10028"
    mocker.patch.object(PostgresDbUtilClass, "commit_transaction", side_effect=Exception('testException'))
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No29.個人情報登録トランザクションのコミット処理が成功する
def test_create_case29(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10029"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No30.個人情報バイナリデータ取得処理が失敗する
def test_create_case30(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10030"
    mocker.patch("models.public.createModel.createModel.user_profile_binary_data_acquisition_exec").return_value = {
        "result": False,
        "errorInfo": {"errorCode": "999999", "message": "test-exception"}
    }
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No31.個人情報バイナリデータ取得処理が失敗する
def test_create_case31(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10031"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No32.共通エラーチェック処理が成功（エラー情報有り）
def test_create_case32(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10032"
    mocker.patch("models.public.createModel.createModel.user_profile_binary_data_acquisition_exec").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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

# No33.個人情報更新トランザクションのトランザクション作成処理が失敗する
# トランザクションコミット時に自動で作成されるのでケースなし


# No34.個人情報更新トランザクションのトランザクション作成処理が成功する
# トランザクションコミット時に自動で作成されるのでケースなし


# No35.個人情報更新処理が失敗する
def test_create_case35(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10035"
    mocker.patch.object(SqlConstClass, "USER_PROFILE_VALID_FLG_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No36.個人情報更新処理が成功する
def test_create_case36(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10036"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No37.共通エラーチェック処理が成功（エラー情報有り）
def test_create_case37(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10037"
    mocker.patch.object(SqlConstClass, "USER_PROFILE_VALID_FLG_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No38.個人情報更新トランザクションのコミット処理が失敗する
def test_create_case38(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10038"
    # 全ての関数がモック化されるので、エラーは出ないがコミットもされない状態になっている
    mocker.patch.object(PostgresDbUtilClass, "commit_transaction", side_effect=[None, None, None, None, None, None, None, Exception('testException')])
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No39.個人情報更新トランザクションのコミット処理が成功する
def test_create_case39(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10039"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No40.アクセストークン発行処理が失敗する
def test_create_case40(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10040"
    mocker.patch("util.tokenUtil.TokenUtilClass.create_token_public").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No41.アクセストークン発行処理が成功する
def test_create_case41(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10041"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No42.共通エラーチェック処理が成功（エラー情報有り）
def test_create_case42(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10042"
    mocker.patch("util.tokenUtil.TokenUtilClass.create_token_public").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No43.API実行履歴登録処理が失敗する
def test_create_case43(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10043"
    mocker.patch("util.commonUtil.get_datetime_str_no_symbol").side_effect = ["20220927145527512", "20220101000000000"]
    mocker.patch("util.commonUtil.get_random_ascii").side_effect = ["O1MOs01uEKinK", ''.join(random.choices(string.ascii_letters + string.digits, k=13))]
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No44.API実行履歴登録処理が成功する
def test_create_case44(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10044"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No45.変数．エラー情報がある(No.5でエラー）
def test_create_case45(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction1"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No46.変数．エラー情報がない
def test_create_case46(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10046"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No47.PDSユーザドメイン検証処理が失敗する
def test_create_case47(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10047"
    mocker.patch("util.commonUtil.CommonUtilClass.check_pds_user_domain").return_value = {
        "result": False,
        "errorInfo": {
            "errorCode": "999999",
            "message": "test-exception"
        }
    }
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No48.PDSユーザドメイン検証処理が成功する
def test_create_case48(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10048"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No49.共通エラーチェック処理が成功（エラー情報有り）
def test_create_case49(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10049"
    mocker.patch("util.commonUtil.CommonUtilClass.check_pds_user_domain").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No50.アクセストークン検証処理が失敗する
def test_create_case50(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10050"
    mocker.patch("util.tokenUtil.TokenUtilClass.verify_token_public").return_value = {
        "result": False,
        "errorInfo": {
            "errorCode": "999999",
            "message": "test-exception"
        }
    }
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No51.アクセストークン検証処理が成功する
def test_create_case51(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10051"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No52.アクセストークン検証処理が失敗する
def test_create_case52(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10052"
    mocker.patch("util.tokenUtil.TokenUtilClass.verify_token_public").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No53.パラメータ検証処理が失敗する
def test_create_case53(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10053"
    mocker.patch("routers.public.createRouter.input_check").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No54.パラメータ検証処理が成功する
def test_create_case54(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10054"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No55.共通エラーチェック処理が成功（エラー情報有り）
def test_create_case55(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10055"
    mocker.patch("routers.public.createRouter.input_check").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No56.パラメータ検証処理が成功する
def test_create_case56(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10056"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No57-1.PDSユーザドメイン名 値が設定されていない（空値）
def test_create_case57_1(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    DATA["tid"] = "transaction10057"
    response = client.post("/api/2.0//transaction", headers=header, data=json.dumps(DATA))
    # パスパラメータを空にするとURLが不正になるので確認不可であることを確認
    assert response.status_code == 404
    print(response.json())

    # 入力チェックを直接呼び出してエラーになることを確認
    request_body = createRouter.requestBody(tid=DATA["tid"], info=DATA["info"])
    response = createRouter.input_check(
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


# No57-2.PDSユーザドメイン名 文字列型以外、21文字
# パスパラメータはURLで絶対に文字列になるので型チェックできない
def test_create_case57_2(create_header):
    # PDSユーザドメイン名に誤りがある場合には、PDSユーザドメイン検証でエラーになってしまうので入力チェックまで到達できないことを確認
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    DATA["tid"] = "transaction10058"
    response = client.post("/api/2.0/[012345678901, 23456]/transaction", headers=header, data=json.dumps(DATA))
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
    request_body = createRouter.requestBody(tid=DATA["tid"], info=DATA["info"])
    response = createRouter.input_check(
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


# No57-3.PDSユーザドメイン名 文字列型、4文字、全角を含む
# パスパラメータはURLで絶対に文字列になるので型チェックできない
def test_create_case57_3(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    DATA["tid"] = "transaction10059"
    response = client.post("/api/2.0/あ123/transaction", headers=header, data=json.dumps(DATA))
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
    request_body = createRouter.requestBody(tid=DATA["tid"], info=DATA["info"])
    response = createRouter.input_check(
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


# No57-4.PDSユーザドメイン名 文字列型、5文字、入力規則違反していない（URL利用可能文字のみの半角小英数記号５桁）
def test_create_case57_4():
    DATA["tid"] = "transaction10060"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_public(pdsUserId="C8000000", pdsUserName="PDSユーザドメイン検証成功テスト", accessToken=None)
    print("accessToken:" + token_result["accessToken"])
    header = {"pdsUserId": "C8000000", "Content-Type": "application/json", "timeStamp": "2022/08/23 15:12:01.690", "accessToken": token_result["accessToken"], "Authorization": "Bearer " + token_result["jwt"]}

    response = client.post("/api/2.0/c0123/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No57-5.PDSユーザドメイン名 文字列型、20文字、入力規則違反していない（URL利用可能文字のみの半角小英数記号20桁）
def test_create_case57_5():
    DATA["tid"] = "transaction10061"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_public(pdsUserId="C8000001", pdsUserName="PDSユーザドメイン検証成功テスト", accessToken=None)
    print("accessToken:" + token_result["accessToken"])
    header = {"pdsUserId": "C8000001", "Content-Type": "application/json", "timeStamp": "2022/08/23 15:12:01.690", "accessToken": token_result["accessToken"], "Authorization": "Bearer " + token_result["jwt"]}

    response = client.post("/api/2.0/c0123456789012345678/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No57-6.PDSユーザID 値が設定されていない（空値）
def test_create_case57_6(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["pdsUserId"] = None
    DATA["tid"] = "transaction10062"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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
    request_body = createRouter.requestBody(tid=DATA["tid"], info=DATA["info"])
    response = createRouter.input_check(
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


# No57-7.PDSユーザID 文字列型以外、7桁、C以外の文字で始まる
def test_create_case57_7(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["pdsUserId"] = '1234567'
    DATA["tid"] = "transaction10063"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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
    request_body = createRouter.requestBody(tid=DATA["tid"], info=DATA["info"])
    response = createRouter.input_check(
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
            }
        ]
    }
    print(response)


# No57-8.PDSユーザID 文字列型、8桁、入力規則違反していない（C＋数値7桁）
def test_create_case57_8(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10064"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No57-9.タイムスタンプ 値が設定されていない（空値）
def test_create_case57_9(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["timeStamp"] = None
    DATA["tid"] = "transaction10067"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No57-10.タイムスタンプ 文字列型以外、22桁
def test_create_case57_10(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["timeStamp"] = '1234567890123456789012'
    DATA["tid"] = "transaction10068"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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
    request_body = createRouter.requestBody(tid=DATA["tid"], info=DATA["info"])
    response = createRouter.input_check(
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


# No57-11.タイムスタンプ 文字列型、24桁、入力規則違反している　hh:mmがhhh:mm
def test_create_case57_11(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["timeStamp"] = '2022/09/30 12:000:00.000'
    DATA["tid"] = "transaction10069"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No57-12.PDSユーザID 文字列型、23桁、入力規則違反していない　「yyyy/MM/dd hh:mm:ss.iii」
def test_create_case57_12(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10070"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No57-13.アクセストークン 値が設定されていない（空値）
def test_create_case57_13(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["accessToken"] = None
    DATA["tid"] = "transaction10071"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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
    request_body = createRouter.requestBody(tid=DATA["tid"], info=DATA["info"])
    response = createRouter.input_check(
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


# No57-14.アクセストークン 文字列型以外、201桁
def test_create_case57_14(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["accessToken"] = "123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901"
    DATA["tid"] = "transaction10072"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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
    request_body = createRouter.requestBody(tid=DATA["tid"], info=DATA["info"])
    response = createRouter.input_check(
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


# No57-15.アクセストークン 文字列型、199桁、入力可能文字以外が含まれる（全角）
def test_create_case57_15(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["accessToken"] = "あ123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678"
    DATA["tid"] = "transaction10073"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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
    request_body = createRouter.requestBody(tid=DATA["tid"], info=DATA["info"])
    response = createRouter.input_check(
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


# No57-16.アクセストークン 文字列型、200桁、入力可能文字のみ（半角英数字） [a-fA-F0-9]
def test_create_case57_16(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10074"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No57-17.トランザクションID 値が設定されていない（空値）
def test_create_case57_17(create_header):
    header = create_header["header"]
    DATA["tid"] = None
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No57-18.トランザクションID 文字列型以外、37桁
def test_create_case57_18(create_header):
    header = create_header["header"]
    DATA["tid"] = 1234567890123456789012345678901234567
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No57-19.トランザクションID 文字列型、37桁、入力可能文字以外が含まれる(全角)
def test_create_case57_19(create_header):
    header = create_header["header"]
    DATA["tid"] = "あ1234567890abcdefghijklmnopqrstuvwxyz"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No57-20.トランザクションID 文字列型、36桁、入力可能文字のみ（半角英数字） [a-zA-Z0-9]
def test_create_case57_20(create_header):
    header = create_header["header"]
    DATA["tid"] = "1234567890aBcDeFgHiJkLmNoPqRsTuVwXyZ"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No57-21.検索用ユーザID 文字列型以外、37桁
def test_create_case57_21(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tid"] = "transaction10079"
    data_copy["info"]["userId"] = 1234567890123456789012345678901234567
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
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


# No57-22.検索用ユーザID 文字列型、36桁
def test_create_case57_22(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tid"] = "transaction10080"
    data_copy["info"]["userId"] = "12345aiueoAIUEOあいうえおアイウエオ亜伊宇江御+-*/%$"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No57-23.検索用日時 文字列型以外、22桁、
def test_create_case57_23(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tid"] = "transaction10081"
    data_copy["info"]["saveDate"] = 1234567890123456789012
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
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


# No57-24.検索用日時 文字列型、24桁、入力規則違反している（形式は yyyy/MM/dd hh:mm:ss.iii でない　yyyyy/MMがyyyy/MMM）
def test_create_case57_24(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tid"] = "transaction10082"
    data_copy["info"]["saveDate"] = "2022/011/01 10:00:00.000"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
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


# No57-25.検索用日時 文字列型、23桁、入力規則違反していない（形式は yyyy/MM/dd hh:mm:ss.iii である）　[0-9 :/.]
def test_create_case57_25(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tid"] = "transaction10083"
    data_copy["info"]["saveDate"] = "2022/11/01 10:00:00.000"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No57-26.保存したいバイナリデータ 文字列型以外
def test_create_case57_26(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tid"] = "transaction10084"
    # imageHashの要素数は一致している必要があるので設定
    data_copy["info"]["imageHash"] = "1234567890"
    data_copy["info"]["image"] = 1234567890
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
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


# No57-27.保存したいバイナリデータ 文字列以外の要素を含む配列
def test_create_case57_27(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tid"] = "transaction10085"
    # imageHashの要素数は一致している必要があるので設定
    data_copy["info"]["imageHash"] = "1234567890"
    data_copy["info"]["image"] = [1234567890]
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
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


# No57-28.保存したいバイナリデータ 文字列、14680065桁、入力可能文字以外が含まれる（全角）
def test_create_case57_28(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tid"] = "transaction10086"
    # imageHashの要素数は一致している必要があるので設定
    data_copy["info"]["imageHash"] = "1234567890"
    f = open('tests/public/14MB.txt', 'r', encoding='UTF-8')
    text = f.read()
    data_copy["info"]["image"] = "あ" + text
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
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


# No57-29.保存したいバイナリデータ 文字列、146800641桁、入力可能文字以外が含まれる（半角記号 +/=以外）
def test_create_case57_29(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tid"] = "transaction10087"
    # imageHashの要素数は一致している必要があるので設定
    data_copy["info"]["imageHash"] = "1234567890"
    f = open('tests/public/140MB.txt', 'r', encoding='UTF-8')
    text = f.read()
    data_copy["info"]["image"] = "$" + text
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
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


# No57-30.保存したいバイナリデータ 文字列要素のみの配列、１つの要素が14680065桁、入力可能文字以外が含まれる（全角）
def test_create_case57_30(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tid"] = "transaction10088"
    # imageHashの要素数は一致している必要があるので設定
    data_copy["info"]["imageHash"] = ["1234567890", "2345678901"]
    f = open('tests/public/14MB.txt', 'r', encoding='UTF-8')
    text = f.read()
    data_copy["info"]["image"] = ["あ" + text, "い" + text]
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
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


# No57-31.保存したいバイナリデータ 文字列要素のみの配列、全ての要素の合計が146800641桁、入力可能文字以外が含まれる（半角記号 +/=以外）
def test_create_case57_31(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tid"] = "transaction10089"
    # imageHashの要素数は一致している必要があるので設定
    data_copy["info"]["imageHash"] = ["1234567890", "2345678901", "3456789012", "4567890123", "5678901234", "6789012345", "7890123456", "8901234567", "9012345678", "0123456789"]
    f = open('tests/public/14MB.txt', 'r', encoding='UTF-8')
    text = f.read()
    data_copy["info"]["image"] = ["$" + text, text, text, text, text, text, text, text, text, text]
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
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


# No57-32.保存したいバイナリデータ 文字列、14680064桁、入力可能文字のみ　[a-zA-Z0-9+/=]
def test_create_case57_32(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tid"] = "transaction10090"
    # imageHashの要素数は一致している必要があるので設定
    data_copy["info"]["imageHash"] = "1234567890"
    f = open('tests/public/14MB.txt', 'r', encoding='UTF-8')
    text = f.read()
    data_copy["info"]["image"] = text
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No57-33.保存したいバイナリデータ 文字列要素のみの配列、全ての要素の合計が146800640桁、入力可能文字のみ　[a-zA-Z0-9+/=]
def test_create_case57_33(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tid"] = "transaction10091"
    # imageHashの要素数は一致している必要があるので設定
    data_copy["info"]["imageHash"] = ["1234567890", "2345678901", "3456789012", "4567890123", "5678901234", "6789012345", "7890123456", "8901234567", "9012345678", "0123456789"]
    f = open('tests/public/14MB.txt', 'r', encoding='UTF-8')
    text = f.read()
    data_copy["info"]["image"] = [text, text, text, text, text, text, text, text, text, text]
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No57-34.保存したいバイナリデータのハッシュ値 文字列型以外
def test_create_case57_34(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tid"] = "transaction10092"
    # imageの要素数は一致している必要があるので設定
    data_copy["info"]["image"] = "1234567890"
    data_copy["info"]["imageHash"] = 1234567890
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
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


# No57-35.保存したいバイナリデータのハッシュ値 文字列型以外の要素を含む配列
def test_create_case57_35(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tid"] = "transaction10093"
    # imageの要素数は一致している必要があるので設定
    data_copy["info"]["image"] = ["1234567890", "2345678901"]
    data_copy["info"]["imageHash"] = [1234567890, 2345678901]
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
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


# No57-36.保存したいバイナリデータのハッシュ値 文字列型、入力可能文字以外が含まれる（全角）
def test_create_case57_36(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tid"] = "transaction10094"
    # imageの要素数は一致している必要があるので設定
    data_copy["info"]["image"] = "1234567890"
    data_copy["info"]["imageHash"] = "あ" + "1234567890"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
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


# No57-37.保存したいバイナリデータのハッシュ値 文字列型の要素のみの配列、入力可能文字以外が含まれる（半角記号）
def test_create_case57_37(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tid"] = "transaction10095"
    # imageの要素数は一致している必要があるので設定
    data_copy["info"]["image"] = ["1234567890", "2345678901"]
    data_copy["info"]["imageHash"] = ["1234567890", "$" + "2345678901"]
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
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


# No57-38.保存したいバイナリデータのハッシュ値 文字列型、入力可能文字のみ　[a-zA-Z0-9]
def test_create_case57_38(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tid"] = "transaction10096"
    # imageの要素数は一致している必要があるので設定
    data_copy["info"]["image"] = "abc1234567890"
    data_copy["info"]["imageHash"] = "abc1234567890"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No57-39.保存したいバイナリデータのハッシュ値 文字列型、入力可能文字のみ　[a-zA-Z0-9]
def test_create_case57_39(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tid"] = "transaction10097"
    # imageの要素数は一致している必要があるので設定
    data_copy["info"]["image"] = ["abc1234567890", "abc2345678901"]
    data_copy["info"]["imageHash"] = ["abc1234567890", "abc2345678901"]
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No57-40.セキュリティレベル 文字列型以外、3桁
def test_create_case57_40(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tid"] = "transaction10098"
    data_copy["info"]["secureLevel"] = 123
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
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


# No57-41.セキュリティレベル 文字列型、3桁、入力可能文字以外を含む（半角スペース）
def test_create_case57_41(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tid"] = "transaction10099"
    data_copy["info"]["secureLevel"] = "1 2"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
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


# No57-42.セキュリティレベル 文字列型、2桁、入力可能文字以外を含む
def test_create_case57_42(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tid"] = "transaction10100"
    data_copy["info"]["secureLevel"] = "あi"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No57-43.保存したいデータ 文字列型か辞書型以外、5001桁
def test_create_case57_43(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tid"] = "transaction10101"
    data_copy["info"]["data"] = 123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
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


# No57-44.保存したいデータ 文字列型、5001桁
def test_create_case57_44(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tid"] = "transaction10102"
    data_copy["info"]["data"] = "123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
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


# No57-45.保存したいデータ 辞書型、5001桁
def test_create_case57_45(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tid"] = "transaction10103"
    data_copy["info"]["data"] = {"key": "value12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345"}
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
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


# No57-46.保存したいデータ 文字列型、5000桁
def test_create_case57_46(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tid"] = "transaction10104"
    data_copy["info"]["data"] = "12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No57-47.保存したいデータ 辞書型、5000桁
def test_create_case57_47(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tid"] = "transaction10105"
    data_copy["info"]["data"] = {"key": "value1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234"}
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No58.「引数．ヘッダパラメータ．PDSユーザID」と「引数．PDSユーザドメイン情報．PDSユーザID」の値が一致しない場合、「変数．エラー情報リスト」にエラー情報を追加する
def test_create_case58(mocker: MockerFixture, create_header):
    # 返却値の変更
    mocker.patch("util.commonUtil.CommonUtilClass.check_pds_user_domain").return_value = {"result": True, "pdsUserInfo": {"pdsUserId": "C1234567"}}
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["pdsUserId"] = 'C9876543'
    DATA["tid"] = "transaction10106"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No59.「引数．リクエストボディ．情報．保存したいバイナリデータ」、「引数．リクエストボディ．情報．保存したいバイナリデータのハッシュ値」の要素数が不一致の場合、「変数．エラー情報リスト」にエラー情報を追加する(「引数．リクエストボディ．情報．保存したいバイナリデータ」、「引数．リクエストボディ．情報．保存したいバイナリデータのハッシュ値」がstringの場合、要素数1のarrayに変換する)
def test_create_case59(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tid"] = "transaction10107"
    # imageの要素数は一致している必要があるので設定
    data_copy["info"]["image"] = ["abc1234567890", "abc2345678901"]
    data_copy["info"]["imageHash"] = "abc1234567890"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
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


# No60.変数．エラー情報がない
def test_create_case60(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tid"] = "transaction10108"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No61.変数．エラー情報がある
def test_create_case61(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tid"] = None
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
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


# No62.「引数．リクエストボディ．保存したいバイナリデータ」の要素数が0
def test_create_case62(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tid"] = "transaction10110"
    data_copy["info"]["image"] = []
    data_copy["info"]["imageHash"] = []
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No63.「引数．リクエストボディ．保存したいバイナリデータ」の要素数が0以外
def test_create_case63(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tid"] = "transaction10111"
    data_copy["info"]["image"] = ["aiueo"]
    data_copy["info"]["imageHash"] = ["12345"]
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No64.バイナリデータ情報取得処理が成功する
def test_create_case64(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tid"] = "transaction10112"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No65.個人情報バイナリデータ登録処理リスト作成処理が成功する
def test_create_case65(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tid"] = "transaction10113"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No66.個人情報バイナリデータ登録処理実行処理が失敗する
@pytest.mark.asyncio
async def test_create_case66(create_header):
    header = create_header["header"]
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    # バイナリデータ情報取得処理が失敗するデータ（登録済みのトランザクションID）で実行する
    create_model = createModel(trace_logger, Request({"type": "http", "headers": {}, "method": "post", "path": ""}), header["pdsUserId"], {}, "pds-user-create")
    request_body = modelRequestBody(tid="transaction1", info=DATA["info"])
    common_util = CommonUtilClass(trace_logger)
    pds_user_db_secret_info = common_util.get_secret_info("pds-c0000000-sm")
    response = await create_model.user_profile_binary_data_acquisition_exec(
        request_body=request_body,
        kms_id="fdb4c6aa-50b0-4ed1-bdad-32c21e0a0387",
        bucket_name="pds-c0000000-bucket",
        pds_user_db_secret_info=pds_user_db_secret_info
    )
    assert response == {
        "result": False,
        "errorInfo": response["errorInfo"]
    }
    print(response)


# No67.個人情報バイナリデータ登録処理実行処理が成功する
def test_create_case67(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tid"] = "transaction10114"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No68.「変数．個人情報バイナリデータ登録処理実行結果リスト[]．処理結果」にfalseが存在する
@pytest.mark.asyncio
async def test_create_case68(create_header):
    header = create_header["header"]
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    # バイナリデータ情報取得処理が失敗するデータ（登録済みのトランザクションID）で実行する
    create_model = createModel(trace_logger, Request({"type": "http", "headers": {}, "method": "post", "path": ""}), header["pdsUserId"], {}, "pds-user-create")
    request_body = modelRequestBody(tid="transaction1", info=DATA["info"])
    common_util = CommonUtilClass(trace_logger)
    pds_user_db_secret_info = common_util.get_secret_info("pds-c0000000-sm")
    response = await create_model.user_profile_binary_data_acquisition_exec(
        request_body=request_body,
        kms_id="fdb4c6aa-50b0-4ed1-bdad-32c21e0a0387",
        bucket_name="pds-c0000000-bucket",
        pds_user_db_secret_info=pds_user_db_secret_info
    )
    assert response == {
        "result": False,
        "errorInfo": response["errorInfo"]
    }
    print(response)


# No69.「変数．個人情報バイナリデータ登録処理実行結果リスト[]．処理結果」にfalseが存在しない
def test_create_case69(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tid"] = "transaction10116"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No70.個人情報バイナリデータ登録処理実行エラー処理が成功する
@pytest.mark.asyncio
async def test_create_case70(create_header):
    header = create_header["header"]
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    # バイナリデータ情報取得処理が失敗するデータ（登録済みのトランザクションID）で実行する
    create_model = createModel(trace_logger, Request({"type": "http", "headers": {}, "method": "post", "path": ""}), header["pdsUserId"], {}, "pds-user-create")
    request_body = modelRequestBody(tid="transaction1", info=DATA["info"])
    common_util = CommonUtilClass(trace_logger)
    pds_user_db_secret_info = common_util.get_secret_info("pds-c0000000-sm")
    response = await create_model.user_profile_binary_data_acquisition_exec(
        request_body=request_body,
        kms_id="fdb4c6aa-50b0-4ed1-bdad-32c21e0a0387",
        bucket_name="pds-c0000000-bucket",
        pds_user_db_secret_info=pds_user_db_secret_info
    )
    assert response == {
        "result": False,
        "errorInfo": response["errorInfo"]
    }
    print(response)


# No71.変数．エラー情報がない
def test_create_case71(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tid"] = "transaction10118"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(data_copy))
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No72.ロールバック処理が失敗する
def test_create_case72(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10119"
    mocker.patch.object(SqlConstClass, "USER_PROFILE_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    mocker.patch.object(PostgresDbUtilClass, "rollback_transaction", return_value={"result": False, "errorObject": Exception("test-exception"), "stackTrace": "test-exception"})
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No73.ロールバック処理が成功する
def test_create_case73(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10120"
    mocker.patch.object(SqlConstClass, "USER_PROFILE_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No74.共通エラーチェック処理が成功（エラー情報有り）
def test_create_case74(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10121"
    mocker.patch.object(SqlConstClass, "USER_PROFILE_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    mocker.patch.object(PostgresDbUtilClass, "rollback_transaction", return_value={"result": False, "errorObject": Exception("test-exception"), "stackTrace": "test-exception"})
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No75.変数．エラー情報がない
def test_create_case75(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10122"
    mocker.patch.object(SqlConstClass, "USER_PROFILE_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No76.ロールバック処理が失敗する
def test_create_case76(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10123"
    mocker.patch.object(SqlConstClass, "USER_PROFILE_VALID_FLG_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    mocker.patch.object(PostgresDbUtilClass, "rollback_transaction", return_value={"result": False, "errorObject": Exception("test-exception"), "stackTrace": "test-exception"})
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No77.ロールバック処理が成功する
def test_create_case77(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10124"
    mocker.patch.object(SqlConstClass, "USER_PROFILE_VALID_FLG_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No78.共通エラーチェック処理が成功（エラー情報有り）
def test_create_case78(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10125"
    mocker.patch.object(SqlConstClass, "USER_PROFILE_VALID_FLG_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    mocker.patch.object(PostgresDbUtilClass, "rollback_transaction", return_value={"result": False, "errorObject": Exception("test-exception"), "stackTrace": "test-exception"})
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No79.変数．エラー情報がない
def test_create_case79(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10126"
    mocker.patch.object(SqlConstClass, "USER_PROFILE_VALID_FLG_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No80.ロールバック処理が失敗する
def test_create_case80(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10127"
    mocker.patch.object(Collection, "insert_one", side_effect=PyMongoError('testException'))
    mocker.patch.object(ClientSession, "abort_transaction", side_effect=PyMongoError('testException'))
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No81.ロールバック処理が成功する
def test_create_case81(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10128"
    mocker.patch.object(Collection, "insert_one", side_effect=PyMongoError('testException'))
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No82.共通エラーチェック処理が成功（エラー情報有り）
def test_create_case82(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10129"
    mocker.patch.object(Collection, "insert_one", side_effect=PyMongoError('testException'))
    mocker.patch.object(ClientSession, "abort_transaction", side_effect=PyMongoError('testException'))
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No83.変数．エラー情報がない
def test_create_case83(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction10130"
    mocker.patch.object(Collection, "insert_one", side_effect=PyMongoError('testException'))
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
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


# No4.機能内結合テスト用テストコード
def test_create_combined_case4(create_header):
    header = create_header["header"]
    DATA["tid"] = "transaction19875"
    DATA["info"]["image"] = "abcde"
    DATA["info"]["imageHash"] = "123"
    response = client.post("/api/2.0/pds-user-create/transaction", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())
