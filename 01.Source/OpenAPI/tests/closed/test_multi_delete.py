from fastapi.testclient import TestClient
import random
import string
from app import app
from fastapi import Request
import pytest
from pytest_mock.plugin import MockerFixture
from util.tokenUtil import TokenUtilClass
import util.logUtil as logUtil
import json
from const.systemConst import SystemConstClass
from const.sqlConst import SqlConstClass
import routers.closed.multiDeleteRouter as multiDeleteRouter
from routers.closed.multiDeleteRouter import requestBody as routerRequestBody
from models.closed.multiDeleteModel import multiDeleteModel
from models.closed.multiDeleteModel import requestBody as modelRequestBody
from util.postgresDbUtil import PostgresDbUtilClass
# import util.commonUtil as commonUtil
from exceptionClass.PDSException import PDSException


client = TestClient(app)
EXEC_NAME: str = "multiDelete"

BEARER = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0Zk9wZXJhdG9ySWQiOiJsLXRlc3QiLCJ0Zk9wZXJhdG9yTmFtZSI6Ilx1MzBlZFx1MzBiMFx1MzBhNFx1MzBmM1x1MzBjNlx1MzBiOVx1MzBjOCIsInRmT3BlcmF0b3JQYXNzd29yZFJlc2V0RmxnIjpmYWxzZSwiYWNjZXNzVG9rZW4iOiJiZGE4ZGY3OThiYzViZGZhMWZkODIyNmRiYmQ0OTMyMTY5ZmY5MjAzNWM0YzFlY2FjZjY2OGUyYzk2ZjAwZThlZTUxNTBiNGM0NTc0NjlkN2I4YmY1NzIxZDZlM2NiNzFiY2RiYzA3ODRiYzcyZWVlNjk1OGE3NTBiMWJkMWEzZWFmZWQ0OWFhNWU0ODZjYzQyZmM3OWNhMWY3MGQzZmM3Yzc0YzE5NjM3ODUzMjRhZDRhNGM0NjkxOGE4NjQ1N2ZiODE3NDU1MCIsImV4cCI6MTY2MTc0NjY3MX0.LCRjPEqKMkRQ_phaYnO7S7pd3SU_rgon-wsX14DBsPA"
ACCESS_TOKEN = "bda8df798bc5bdfa1fd8226dbbd4932169ff92035c4c1ecacf668e2c96f00e8ee5150b4c457469d7b8bf5721d6e3cb71bcdbc0784bc72eee6958a750b1bd1a3eafed49aa5e486cc42fc79ca1f70d3fc7c74c1963785324ad4a4c46918a86457fb8174550"
HEADER = {"Content-Type": "application/json", "timeStamp": "2022/08/23 15:12:01.690", "accessToken": ACCESS_TOKEN, "Authorization": "Bearer " + BEARER}

SEARCH_CRITERIA = {
    "userIdMatchMode": "前方一致",
    "userIdStr": "C0123456",
    "dataJsonKey": "data.name.first",
    "dataMatchMode": "前方一致",
    "dataStr": "taro",
    "imageHash": "glakjgirhul",
    "fromDate": "2023/01/01",
    "toDate": "2023/12/31"
}

TID_LIST = [
    "transaction40000",
    "transaction40001",
    "transaction40002",
]

REQUEST_BODY = {
    "pdsUserId": "C9876543",
    "searchCriteria": SEARCH_CRITERIA,
    "tidList": TID_LIST,
    "tidListFileName": "test.csv",
    "approvalUserId": "approvalUser",
    "approvalUserPassword": "abcdedABC123",
    "mailAddressTo": "test1@gmail.com",
    "mailAddressCc": "test2@gmail.com",
    "multiDeleteAgreementStr": "削除する"
}

TF_OPERATOR_INFO = {
    "tfOperatorId": "t-test4",
    "tfOperatorName": "テスト"
}

REQUEST = Request({"type": "http", "headers": {}, "method": "post", "path": "", "query_string": "", "root_path": "http://localhost", "scope": {"headers": {"host": "localhost"}}})


@pytest.fixture
def create_header():
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_closed(tfOperatorInfo=TF_OPERATOR_INFO, accessToken=None)
    print("accessToken:" + token_result["accessToken"])
    yield {
        "header": {
            "Content-Type": "application/json",
            "accessToken": token_result["accessToken"],
            "timeStamp": "2022/08/23 15:12:01.690",
            "Authorization": "Bearer " + token_result["jwt"]
        }
    }


# No1.事前処理が失敗する
def test_multi_delete_case1(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.tokenUtil.TokenUtilClass.verify_token_closed").side_effect = Exception('testException')
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
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
def test_multi_delete_case2(create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
    }
    print(response.json())


# No3.接続に失敗する。設定値を異常な値に変更する
def test_multi_delete_case3(mocker: MockerFixture, create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    mocker.patch.object(SystemConstClass, "PDS_COMMON_DB_SECRET_INFO", {"SECRET_NAME": "pds-common-sm-ng"})
    multi_delete_model = multiDeleteModel(trace_logger, Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    model_request = modelRequestBody(**REQUEST_BODY)
    with pytest.raises(PDSException) as e:
        multi_delete_model.main(model_request)

    assert e.value.args[0] == {
        "errorCode": "999999",
        "message": e.value.args[0]["message"]
    }
    print(e)


# No4.接続に成功する
def test_multi_delete_case4(create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
    }
    print(response.json())


# No5.承認者情報確認処理が失敗する
def test_multi_delete_case5(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.commonUtil.CommonUtilClass.check_approval_user_info").side_effect = Exception('testException')
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
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


# No6.承認者情報確認処理が成功する
def test_multi_delete_case6(create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
    }
    print(response.json())


# No7.「変数.PDSユーザ情報」が0件
def test_multi_delete_case7(create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["pdsUserId"] = "C3333333"
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
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


# No8.PDSユーザ取得処理が失敗する
def test_multi_delete_case8(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "MONGODB_SECRET_NAME_AND_S3_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
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


# No9.PDSユーザ取得処理が成功する
def test_multi_delete_case9(create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
    }
    print(response.json())


# No10.共通エラーチェック処理が成功（エラー情報有り）
def test_multi_delete_case10(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "MONGODB_SECRET_NAME_AND_S3_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
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


# No11.リクエストの「リクエストボディ．tidリスト」がNull
def test_multi_delete_case11(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["tidList"] = None
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No12.リクエストの「リクエストボディ．tidリスト」がNull以外
def test_multi_delete_case12(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
    }
    print(response.json())


# No13.tidリスト作成処理が失敗する
def test_multi_delete_case13(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.commonUtil.CommonUtilClass.mongodb_search").side_effect = Exception('testException')
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["tidList"] = None
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
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


# No14.tidリスト作成処理が成功する
def test_multi_delete_case14(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["tidList"] = None
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No15.共通エラーチェック処理が成功（エラー情報有り）
def test_multi_delete_case15(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.commonUtil.CommonUtilClass.mongodb_search").side_effect = Exception('testException')
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["tidList"] = None
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
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


# No16.接続に失敗する。設定値を異常な値に変更する
def test_multi_delete_case16(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["pdsUserId"] = "C5000000"
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
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


# No17.接続に成功する
def test_multi_delete_case17(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No18.個人情報バイナリデータ論理削除トランザクションのトランザクション作成処理が失敗する
#      コネクション作成時に自動作成なので検証不可


# No19.個人情報バイナリデータ論理削除トランザクションのトランザクション作成処理が成功する
#      コネクション作成時に自動作成なので検証不可


# No20.変数．tidリストに値が存在する
def test_multi_delete_case20(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No21.変数．tidリストが存在しない
def test_multi_delete_case21(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["tidList"] = None
    request_body_copy["searchCriteria"]["dataStr"] = "jiro"
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No22.個人情報取得処理が失敗する
def test_multi_delete_case22(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "USER_PROFILE_TRANSACTION_ID_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
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


# No23.個人情報取得処理が成功する
def test_multi_delete_case23(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No24.共通エラーチェック処理が成功（エラー情報有り）
def test_multi_delete_case24(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "USER_PROFILE_TRANSACTION_ID_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
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


# No25.tidリストファイル作成処理が成功する
def test_multi_delete_case25(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No26.個人情報バイナリデータ論理削除処理が失敗する
def test_multi_delete_case26(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "USER_PROFILE_DELETE_BINARY_DATA_MULTI_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
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


# No27.個人情報バイナリデータ論理削除処理が成功する
def test_multi_delete_case27(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No28.個人情報論理削除処理が失敗する
def test_multi_delete_case28(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "USER_PROFILE_DELETE_DATA_MULTI_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
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


# No29.個人情報論理削除処理が成功する
def test_multi_delete_case29(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No30.TIDリスト保存処理が失敗する
def test_multi_delete_case30(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    mocker.patch("util.s3Util.s3UtilClass.put_file").return_value = False
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "990021",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No31.TIDリスト保存処理が成功する
def test_multi_delete_case31(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No32.共通エラーチェック処理が成功（エラー情報有り）
def test_multi_delete_case32(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    mocker.patch("util.s3Util.s3UtilClass.put_file").return_value = False
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "990021",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No33.リクエストのリクエストボディ．tidリストがNull
def test_multi_delete_case33(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["tidList"] = None
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No34.リクエストのリクエストボディ．tidリストがNull以外
def test_multi_delete_case34(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No35.リクエストのリクエストボディ．保存したいデータJSONキーがNull
def test_multi_delete_case35(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["searchCriteria"]["dataJsonKey"] = None
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No36.リクエストのリクエストボディ．保存したいデータJSONキーがNull以外
def test_multi_delete_case36(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No37.削除レポートファイル作成処理が失敗する
def test_multi_delete_case37(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.pdfUtil.PdfUtilClass.create_pdf").side_effect = Exception('testException')
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
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


# No38.削除レポートファイル作成処理が成功する
def test_multi_delete_case38(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No39.削除レポートファイル保存処理が失敗する
def test_multi_delete_case39(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.s3Util.s3UtilClass.put_file").side_effect = [True, False, False, False, False, False]
    mocker.patch.object(multiDeleteModel, "delete_s3_file", side_effect=None)
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "990021",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No40.削除レポートファイル保存処理が成功する
def test_multi_delete_case40(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No41.共通エラーチェック処理が成功（エラー情報有り）
def test_multi_delete_case41(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.s3Util.s3UtilClass.put_file").side_effect = [True, False, False, False, False, False]
    mocker.patch.object(multiDeleteModel, "delete_s3_file", side_effect=None)
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "990021",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No42.WBT新規メール情報登録API実行処理が失敗する
def test_multi_delete_case42(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.commonUtil.CommonUtilClass.wbt_mails_add_api_exec").side_effect = Exception('testException')
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "990011",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No43.WBT新規メール情報登録API実行処理が成功する
def test_multi_delete_case43(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No44.共通エラーチェック処理が成功（エラー情報有り）
def test_multi_delete_case44(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.commonUtil.CommonUtilClass.wbt_mails_add_api_exec").side_effect = Exception('testException')
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "990011",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No45.WBTファイル登録API実行処理が失敗する
def test_multi_delete_case45(mocker: MockerFixture, create_header):

    header = create_header["header"]
    mocker.patch("util.commonUtil.CommonUtilClass.wbt_file_add_api_exec").side_effect = Exception('testException')
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "990013",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No46.WBTファイル登録API実行処理が成功する
def test_multi_delete_case46(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No47.共通エラーチェック処理が成功（エラー情報有り）
def test_multi_delete_case47(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.commonUtil.CommonUtilClass.wbt_file_add_api_exec").side_effect = Exception('testException')
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "990013",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No48.個人情報削除トランザクションのコミット処理が失敗する
def test_multi_delete_case48(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(PostgresDbUtilClass, "commit_transaction", side_effect=Exception('testException'))
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
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


# No49.個人情報削除トランザクションのコミット処理が成功する
def test_multi_delete_case49(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No50.個人情報削除バッチキュー発行処理が失敗する
def test_multi_delete_case50(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SystemConstClass, "SQS_QUEUE_NAME", "aaaaaa")
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
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


# No51.個人情報削除バッチキュー発行処理が成功する
def test_multi_delete_case51(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No52.アクセストークン発行処理が失敗する
def test_multi_delete_case52(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.tokenUtil.TokenUtilClass.create_token_closed").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
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


# No53.アクセストークン発行処理が成功する
def test_multi_delete_case53(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
    }
    print(response.json())


# No54.共通エラーチェック処理が成功（エラー情報有り）
def test_multi_delete_case54(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.tokenUtil.TokenUtilClass.create_token_closed").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
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


# No55.API実行履歴登録処理が失敗する
def test_multi_delete_case55(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    mocker.patch("util.commonUtil.get_datetime_str_no_symbol").side_effect = ["20220927145527512", "20220927145527512", "20220927145527512", "20220101000000000"]
    mocker.patch("util.commonUtil.get_random_ascii").side_effect = ["O1MOs01uEKinK", ''.join(random.choices(string.ascii_letters + string.digits, k=13))]
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
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


# No56.API実行履歴登録処理が成功する
def test_multi_delete_case56(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
    }
    print(response.json())


# No57.変数．エラー情報がある(No.7でエラー）
def test_multi_delete_case57(create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["pdsUserId"] = "C3333333"
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
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


# No58.変数．エラー情報がない
def test_multi_delete_case58(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
    }
    print(response.json())


# No59.アクセストークン検証処理が失敗する
def test_multi_delete_case59(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.tokenUtil.TokenUtilClass.verify_token_closed").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
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


# No60.アクセストークン検証処理が成功する
def test_multi_delete_case60(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
    }
    print(response.json())


# No61.共通エラーチェック処理が成功（エラー情報有り）
def test_multi_delete_case61(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.tokenUtil.TokenUtilClass.verify_token_closed").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
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


# No62.パラメータ検証処理が失敗する
def test_multi_delete_case62(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("routers.closed.multiDeleteRouter.input_check").side_effect = Exception("test-Exception")
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
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


# No63.パラメータ検証処理が成功する
def test_multi_delete_case63(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
    }
    print(response.json())


# No64.共通エラーチェック処理が成功（エラー情報有り）
def test_multi_delete_case64(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["pdsUserId"] = None
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
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


# No65.変数．エラー情報がない
def test_multi_delete_case65(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
    }
    print(response.json())


# No66-1.タイムスタンプ 値が設定されていない（空値）
def test_multi_delete_case66_1(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**REQUEST_BODY)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=None,
        request_body=router_request_body,
        token_verify_response=token_verify_response
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


# No66-2.タイムスタンプ 文字列型以外、22桁
def test_multi_delete_case66_2(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["timeStamp"] = '1234567890123456789012'
    router_request_body = routerRequestBody(**REQUEST_BODY)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=int(header["timeStamp"]),
        request_body=router_request_body,
        token_verify_response=token_verify_response
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


# No66-3.タイムスタンプ 文字列型、24桁、入力規則違反している　hh:mmがhhh:mm
def test_multi_delete_case66_3(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["timeStamp"] = '2022/09/30 12:000:00.000'
    router_request_body = routerRequestBody(**REQUEST_BODY)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
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


# No66-4.アクセストークン 値が設定されていない（空値）
def test_multi_delete_case66_4(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**REQUEST_BODY)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=None,
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
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


# No66-5.アクセストークン 文字列型以外、201桁
def test_multi_delete_case66_5(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["accessToken"] = "123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901"
    router_request_body = routerRequestBody(**REQUEST_BODY)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=int(header["accessToken"]),
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
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


# No66-6.アクセストークン 文字列型、199桁、入力可能文字以外が含まれる（全角）
def test_multi_delete_case66_6(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["accessToken"] = "あ123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678"
    router_request_body = routerRequestBody(**REQUEST_BODY)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
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


# No66-7.アクセストークン 文字列型、200桁、入力可能文字のみ（半角英数字） [a-fA-F0-9]
def test_multi_delete_case66_7(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**REQUEST_BODY)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
    )
    assert response == {
        "result": True
    }
    print(response)


# No66-8.PDSユーザID 値が設定されていない（空値）
def test_multi_delete_case66_8(create_header):
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["pdsUserId"] = None
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
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


# No66-9.PDSユーザID 文字列型以外、7桁、C以外の文字で始まる
def test_multi_delete_case66_9(create_header):
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["pdsUserId"] = 1234567
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
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


# No66-10.PDSユーザID 文字列型、8桁、入力規則違反していない（C＋数値7桁）
def test_multi_delete_case66_10(create_header):
    request_body_copy = REQUEST_BODY.copy()
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
    )
    assert response == {
        "result": True
    }
    print(response)


# No66-11.検索用ユーザID検索モード 文字列以外、入力可能文字以外が含まれる
def test_multi_delete_case66_11(create_header):
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["searchCriteria"]["userIdMatchMode"] = 123
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
    )
    assert response == {
        "result": False,
        "errorInfo": [
            {
                "errorCode": "020019",
                "message": response["errorInfo"][0]["message"]
            }
        ]
    }
    print(response)


# No66-12.検索用ユーザID検索モード 文字列、入力可能文字以外が含まれる
def test_multi_delete_case66_12(create_header):
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["searchCriteria"]["userIdMatchMode"] = "検索"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
    )
    assert response == {
        "result": False,
        "errorInfo": [
            {
                "errorCode": "020020",
                "message": response["errorInfo"][0]["message"]
            }
        ]
    }
    print(response)


# No66-13.検索用ユーザID検索モード 文字列、入力可能文字のみ
def test_multi_delete_case66_13(create_header):
    request_body_copy = REQUEST_BODY.copy()
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
    )
    assert response == {
        "result": True
    }
    print(response)


# No66-14.検索用ユーザID検索文字列 文字列以外、37桁
def test_multi_delete_case66_14(create_header):
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["searchCriteria"]["userIdStr"] = 1234567890123456789012345678901234567
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
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


# No66-15.検索用ユーザID検索文字列 文字列、36桁
def test_multi_delete_case66_15(create_header):
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["searchCriteria"]["userIdStr"] = "123456789012345678901234567890123456"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
    )
    assert response == {
        "result": True
    }
    print(response)


# No66-16.保存データJsonキー情報 文字列以外
def test_multi_delete_case66_16(create_header):
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["searchCriteria"]["dataJsonKey"] = 123
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
    )
    assert response == {
        "result": False,
        "errorInfo": [
            {
                "errorCode": "020019",
                "message": response["errorInfo"][0]["message"]
            }
        ]
    }
    print(response)


# No66-17.保存データJsonキー情報 文字列
def test_multi_delete_case66_17(create_header):
    request_body_copy = REQUEST_BODY.copy()
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
    )
    assert response == {
        "result": True
    }
    print(response)


# No66-18.保存データ検索モード 文字列以外
def test_multi_delete_case66_18(create_header):
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["searchCriteria"]["dataMatchMode"] = 123
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
    )
    assert response == {
        "result": False,
        "errorInfo": [
            {
                "errorCode": "020019",
                "message": response["errorInfo"][0]["message"]
            }
        ]
    }
    print(response)


# No66-19.保存データ検索モード 文字列、入力可能文字以外が含まれる
def test_multi_delete_case66_19(create_header):
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["searchCriteria"]["userIdMatchMode"] = "検索"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
    )
    assert response == {
        "result": False,
        "errorInfo": [
            {
                "errorCode": "020020",
                "message": response["errorInfo"][0]["message"]
            }
        ]
    }
    print(response)


# No66-20.保存データ検索モード 文字列、入力可能文字のみ
def test_multi_delete_case66_20(create_header):
    request_body_copy = REQUEST_BODY.copy()
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
    )
    assert response == {
        "result": True
    }
    print(response)


# No66-21.保存データ検索文字列 文字列以外
def test_multi_delete_case66_21(create_header):
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["searchCriteria"]["dataStr"] = 123
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
    )
    assert response == {
        "result": False,
        "errorInfo": [
            {
                "errorCode": "020019",
                "message": response["errorInfo"][0]["message"]
            }
        ]
    }
    print(response)


# No66-22.保存データ検索文字列 文字列
def test_multi_delete_case66_22(create_header):
    request_body_copy = REQUEST_BODY.copy()
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
    )
    assert response == {
        "result": True
    }
    print(response)


# No66-23.保存されたバイナリデータのハッシュ値 文字列型以外
def test_multi_delete_case66_23(create_header):
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["searchCriteria"]["imageHash"] = 123456
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
    )
    assert response == {
        "result": False,
        "errorInfo": [
            {
                "errorCode": "020019",
                "message": response["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020020",
                "message": response["errorInfo"][1]["message"]
            }
        ]
    }
    print(response)


# No66-24.保存されたバイナリデータのハッシュ値 入力可能文字以外を含む
def test_multi_delete_case66_24(create_header):
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["searchCriteria"]["imageHash"] = "あ123456"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
    )
    assert response == {
        "result": False,
        "errorInfo": [
            {
                "errorCode": "020020",
                "message": response["errorInfo"][0]["message"]
            }
        ]
    }
    print(response)


# No66-25.保存されたバイナリデータのハッシュ値 入力可能文字
def test_multi_delete_case66_25(create_header):
    request_body_copy = REQUEST_BODY.copy()
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
    )
    assert response == {
        "result": True
    }
    print(response)


# No66-26.検索用日時From 文字列以外、11文字
def test_multi_delete_case66_26(create_header):
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["searchCriteria"]["fromDate"] = 12345678901
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
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


# No66-27.検索用日時From 文字列以外、11文字
def test_multi_delete_case66_27(create_header):
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["searchCriteria"]["fromDate"] = "202/01/01"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
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


# No66-28.検索用日時From 文字列、10文字、入力規則
def test_multi_delete_case66_28(create_header):
    request_body_copy = REQUEST_BODY.copy()
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
    )
    assert response == {
        "result": True
    }
    print(response)


# No66-29.検索用日時To 文字列以外、11文字
def test_multi_delete_case66_29(create_header):
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["searchCriteria"]["toDate"] = 12345678901
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
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


# No66-30.検索用日時To 文字列以外、11文字
def test_multi_delete_case66_30(create_header):
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["searchCriteria"]["toDate"] = "202/01/01"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
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
            },
            {
                "errorCode": "030006",
                "message": response["errorInfo"][2]["message"]
            }
        ]
    }
    print(response)


# No66-31.検索用日時To 文字列、10文字、入力規則
def test_multi_delete_case66_31(create_header):
    request_body_copy = REQUEST_BODY.copy()
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
    )
    assert response == {
        "result": True
    }
    print(response)


# No66-32.承認TFオペレータID 未入力
def test_multi_delete_case66_32(create_header):
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["approvalUserId"] = None
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
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


# No66-33.承認TFオペレータID 文字列以外 16桁超過
def test_multi_delete_case66_33(create_header):
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["approvalUserId"] = 12345678901234567
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
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


# No66-34.承認TFオペレータID 文字列 3桁未満 入力可能文字以外を含む
def test_multi_delete_case66_34(create_header):
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["approvalUserId"] = "あ12"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
    )
    assert response == {
        "result": False,
        "errorInfo": [
            {
                "errorCode": "020020",
                "message": response["errorInfo"][0]["message"]
            }
        ]
    }
    print(response)


# No66-35.承認TFオペレータID 文字列 16桁 入力可能文字のみ
def test_multi_delete_case66_35(create_header):
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["approvalUserId"] = "1234567890123456"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
    )
    assert response == {
        "result": True
    }
    print(response)


# No66-36.承認TFオペレータパスワード 未入力
def test_multi_delete_case66_36(create_header):
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["approvalUserPassword"] = None
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
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


# No66-37.承認TFオペレータパスワード 文字列以外 8桁未満
def test_multi_delete_case66_37(create_header):
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["approvalUserPassword"] = 1234567
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
    )
    assert response == {
        "result": False,
        "errorInfo": [
            {
                "errorCode": "020019",
                "message": response["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020016",
                "message": response["errorInfo"][1]["message"]
            }
        ]
    }
    print(response)


# No66-38.承認TFオペレータパスワード 文字列 617桁超過 入力可能文字以外を含む 入力規則違反
def test_multi_delete_case66_38(create_header):
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["approvalUserPassword"] = "あ12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
    )
    assert response == {
        "result": False,
        "errorInfo": [
            {
                "errorCode": "020002",
                "message": response["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020020",
                "message": response["errorInfo"][1]["message"]
            },
            {
                "errorCode": "020010",
                "message": response["errorInfo"][2]["message"]
            }
        ]
    }
    print(response)


# No66-39.承認TFオペレータパスワード 文字列 8桁 入力可能文字のみ 入力規則
def test_multi_delete_case66_39(create_header):
    request_body_copy = REQUEST_BODY.copy()
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
    )
    assert response == {
        "result": True
    }
    print(response)


# No66-40.メールアドレスTo 未入力
def test_multi_delete_case66_40(create_header):
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["mailAddressTo"] = None
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
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


# No66-41.宛先To 文字列以外
def test_multi_delete_case66_41(create_header):
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["mailAddressTo"] = 1234567
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
    )
    assert response == {
        "result": False,
        "errorInfo": [
            {
                "errorCode": "020019",
                "message": response["errorInfo"][0]["message"]
            }
        ]
    }
    print(response)


# No66-42.宛先To 文字列 512桁超過 入力可能文字以外を含む 入力規則違反
def test_multi_delete_case66_42(create_header):
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["mailAddressTo"] = "あ12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
    )
    assert response == {
        "result": False,
        "errorInfo": [
            {
                "errorCode": "020002",
                "message": response["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020003",
                "message": response["errorInfo"][1]["message"]
            }
        ]
    }
    print(response)


# No66-43.宛先To 文字列 512桁 入力可能文字のみ 入力規則
def test_multi_delete_case66_43(create_header):
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["mailAddressTo"] = "1234567890@1234567890.1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
    )
    assert response == {
        "result": True
    }
    print(response)


# No66-44.宛先Cc 文字列以外
def test_multi_delete_case66_44(create_header):
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["mailAddressTo"] = 1234567
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
    )
    assert response == {
        "result": False,
        "errorInfo": [
            {
                "errorCode": "020019",
                "message": response["errorInfo"][0]["message"]
            }
        ]
    }
    print(response)


# No66-45.宛先Cc 文字列 512桁超過 入力可能文字以外を含む 入力規則違反
def test_multi_delete_case66_45(create_header):
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["mailAddressTo"] = "あ12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
    )
    assert response == {
        "result": False,
        "errorInfo": [
            {
                "errorCode": "020002",
                "message": response["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020003",
                "message": response["errorInfo"][1]["message"]
            }
        ]
    }
    print(response)


# No66-46.宛先Cc 文字列 512桁 入力可能文字のみ 入力規則
def test_multi_delete_case66_46(create_header):
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["mailAddressTo"] = "1234567890@1234567890.1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
    )
    assert response == {
        "result": True
    }
    print(response)


# No66-47.tidリストファイル名 文字列以外
def test_multi_delete_case66_47(create_header):
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["tidListFileName"] = 1234567890
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
    )
    assert response == {
        "result": False,
        "errorInfo": [
            {
                "errorCode": "020019",
                "message": response["errorInfo"][0]["message"]
            }
        ]
    }
    print(response)


# No66-48.tidリストファイル名 文字列 入力可能文字以外を含む
def test_multi_delete_case66_48(create_header):
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["tidListFileName"] = "12345/67890"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
    )
    assert response == {
        "result": False,
        "errorInfo": [
            {
                "errorCode": "020020",
                "message": response["errorInfo"][0]["message"]
            }
        ]
    }
    print(response)


# No66-49.tidリストファイル名 文字列 入力可能文字のみ
def test_multi_delete_case66_49(create_header):
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["tidListFileName"] = "1234567890"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
    )
    assert response == {
        "result": True
    }
    print(response)


# No66-50.一括削除同意テキスト 文字列以外 4桁未満
def test_multi_delete_case66_50(create_header):
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["multiDeleteAgreementStr"] = 123
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
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


# No66-51.一括削除同意テキスト 文字列 4桁超過 入力規則違反
def test_multi_delete_case66_51(create_header):
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["multiDeleteAgreementStr"] = "1234＆"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
    )
    assert response == {
        "result": False,
        "errorInfo": [
            {
                "errorCode": "020003",
                "message": response["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020014",
                "message": response["errorInfo"][1]["message"]
            }
        ]
    }
    print(response)


# No66-52.一括削除同意テキスト 文字列 4桁 入力可能文字のみ 入力規則
def test_multi_delete_case66_52(create_header):
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["multiDeleteAgreementStr"] = "削除する"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
    )
    assert response == {
        "result": True
    }
    print(response)


# No66-53.tidリスト 文字列以外 36桁超過
def test_multi_download_case66_53(create_header):
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["tidList"] = 1234567890123456789012345678901234567
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
    )
    assert response == {
        "result": False,
        "errorInfo": [
            {
                "errorCode": "020019",
                "message": response["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020020",
                "message": response["errorInfo"][1]["message"]
            },
            {
                "errorCode": "020002",
                "message": response["errorInfo"][2]["message"]
            }
        ]
    }
    print(response)


# No66-54.tidリスト 配列型文字列以外を含む 36桁超過
def test_multi_download_case66_54(create_header):
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["tidList"] = [1234567890123456789012345678901234567]
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
    )
    assert response == {
        "result": False,
        "errorInfo": [
            {
                "errorCode": "020020",
                "message": response["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020002",
                "message": response["errorInfo"][1]["message"]
            }
        ]
    }
    print(response)


# No66-55.tidリスト 文字列 3D6桁 入力可能文字のみ
def test_multi_download_case66_55(create_header):
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["tidList"] = "123456789012345678901234567890123456"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
    )
    assert response == {
        "result": True
    }
    print(response)


# No66-56.tidリスト 配列型文字列のみ 36桁 入力可能文字のみ
def test_multi_download_case66_56(create_header):
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["tidList"] = ["123456789012345678901234567890123456", "234567890123456789012345678901234567"]
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
    )
    assert response == {
        "result": True
    }
    print(response)


# No66-57.承認ユーザIDとトークン検証結果のIDが同じ
def test_multi_delete_case66_57(create_header):
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["approvalUserId"] = "t-test4"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
    )
    assert response == {
        "result": False,
        "errorInfo": [
            {
                "errorCode": "030016",
                "message": response["errorInfo"][0]["message"]
            }
        ]
    }
    print(response)


# No66-58.承認ユーザIDとトークン検証結果のIDが異なる
def test_multi_delete_case66_58(create_header):
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["mailAddressTo"] = "1234567890@1234567890.1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
    )
    assert response == {
        "result": True
    }
    print(response)


# No66-59.検索日時Fromと検索用日時To 相関 FromがToを超過
def test_multi_delete_case66_59(create_header):
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["searchCriteria"]["fromDate"] = "2023/01/02"
    request_body_copy["searchCriteria"]["toDate"] = "2023/01/01"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
    )
    assert response == {
        "result": False,
        "errorInfo": [
            {
                "errorCode": "030006",
                "message": response["errorInfo"][0]["message"]
            }
        ]
    }
    print(response)


# No66-60.検索日時Fromと検索用日時To 相関 FromがToを超過しない
def test_multi_delete_case66_60(create_header):
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["searchCriteria"]["fromDate"] = "2023/01/01"
    request_body_copy["searchCriteria"]["toDate"] = "2023/01/01"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    router_request_body = routerRequestBody(**request_body_copy)
    token_verify_response = {
        "result": True,
        "payload": {
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト",
            "accessToken": header["accessToken"]
        }
    }
    response = multiDeleteRouter.input_check(
        trace_logger=trace_logger,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"],
        request_body=router_request_body,
        token_verify_response=token_verify_response
    )
    assert response == {
        "result": True
    }
    print(response)


# No67.変数．エラー情報がない
def test_multi_delete_case67(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
    }
    print(response.json())


# No68.変数．エラー情報がある
def test_multi_delete_case68(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["pdsUserId"] = None
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
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


# No69.個人情報バイナリデータ論理削除処理が失敗する
def test_multi_delete_case69(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "USER_PROFILE_DELETE_BINARY_DATA_MULTI_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
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


# No70.個人情報バイナリデータ論理削除処理が成功する
def test_multi_delete_case70(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No71.共通エラーチェック処理が成功（エラー情報有り）
def test_multi_delete_case71(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "USER_PROFILE_DELETE_BINARY_DATA_MULTI_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
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


# No72.変数．エラー情報がない
def test_multi_delete_case72(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No73.個人情報更新処理が失敗する
def test_multi_delete_case73(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "USER_PROFILE_DELETE_DATA_MULTI_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
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


# No74.個人情報更新処理が成功する
def test_multi_delete_case74(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No75.共通エラーチェック処理が成功（エラー情報有り）
def test_multi_delete_case75(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "USER_PROFILE_DELETE_DATA_MULTI_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
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


# No76.変数．エラー情報がない
def test_multi_delete_case76(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No77.S3のファイル削除処理が失敗する（5回まで許容）
def test_multi_delete_case77(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.commonUtil.CommonUtilClass.wbt_mails_add_api_exec").side_effect = Exception('testException')
    mocker.patch("util.s3Util.s3UtilClass.deleteFile").return_value = False
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "990022",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No78.S3のファイル削除処理が失敗する
def test_multi_delete_case78(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.commonUtil.CommonUtilClass.wbt_mails_add_api_exec").side_effect = Exception('testException')
    mocker.patch("util.s3Util.s3UtilClass.deleteFile").return_value = False
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "990022",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No79.S3のファイル削除処理が成功する
def test_multi_delete_case79(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    mocker.patch("util.commonUtil.CommonUtilClass.wbt_mails_add_api_exec").side_effect = Exception('testException')
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "990011",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No80.共通エラーチェック処理が成功（エラー情報有り）
def test_multi_delete_case80(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    mocker.patch("util.commonUtil.CommonUtilClass.wbt_mails_add_api_exec").side_effect = Exception('testException')
    mocker.patch("util.s3Util.s3UtilClass.deleteFile").return_value = False
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "990022",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No81.変数．エラー情報がない
def test_multi_delete_case81(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    mocker.patch("util.commonUtil.CommonUtilClass.wbt_mails_add_api_exec").side_effect = Exception('testException')
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "990011",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No82.ロールバック処理が失敗する
def test_multi_delete_case82(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "USER_PROFILE_DELETE_BINARY_DATA_MULTI_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    mocker.patch.object(PostgresDbUtilClass, "rollback_transaction", return_value={"result": False, "errorObject": Exception("test-exception"), "stackTrace": "test-exception"})
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
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


# No83.ロールバック処理が成功する
def test_multi_delete_case83(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "USER_PROFILE_DELETE_BINARY_DATA_MULTI_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
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


# No84.共通エラーチェック処理が成功（エラー情報有り）
def test_multi_delete_case84(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "USER_PROFILE_DELETE_BINARY_DATA_MULTI_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    mocker.patch.object(PostgresDbUtilClass, "rollback_transaction", return_value={"result": False, "errorObject": Exception("test-exception"), "stackTrace": "test-exception"})
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
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


# No85.変数．エラー情報がない
def test_multi_delete_case85(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "USER_PROFILE_DELETE_BINARY_DATA_MULTI_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
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


# No86.変数．削除レコード数が0
def test_multi_delete_case86(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["tidList"] = ["transaction0"]
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No87.変数．削除レコード数が0以外
def test_multi_delete_case87(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multidelete", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())
