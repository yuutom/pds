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
from const.systemConst import SystemConstClass
from const.sqlConst import SqlConstClass
import routers.closed.multiDownloadRouter as multiDownloadRouter
from models.closed.multiDownloadModel import multiDownloadModel
from models.closed.multiDownloadModel import requestBody as modelRequestBody
from routers.closed.multiDownloadRouter import requestBody as routerRequestBody
from util.postgresDbUtil import PostgresDbUtilClass
# import util.commonUtil as commonUtil
from const.fileNameConst import FileNameConstClass
from util.commonUtil import CommonUtilClass
from exceptionClass.PDSException import PDSException


client = TestClient(app)
EXEC_NAME: str = "multiDownload"

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

REQUEST_BODY = {
    "pdsUserId": "C9876543",
    "searchCriteria": SEARCH_CRITERIA,
    "tidList": None,
    "approvalUserId": "approvalUser",
    "approvalUserPassword": "abcdedABC123",
    "mailAddressTo": "test1@gmail.com",
    "mailAddressCc": "test2@gmail.com"
}

REQUEST_BODY_TASK = {
    "requestNo": "1c655b66a4b94254902cfaf598574f89",
    "pdsUserId": "C9876543"
}

REQUEST_BODY_TASK_2GB = {
    "requestNo": "f2ddb4be21c948508f3de9c267a9e00c",
    "pdsUserId": "C9876543"
}

TF_OPERATOR_INFO = {
    "tfOperatorId": "t-test4",
    "tfOperatorName": "テスト"
}

TID_LIST = [
    "transaction30000"
]

GB2_TID_LIST = [
    "transaction1500001",
    "transaction1500002",
    "transaction1500003",
    "transaction1500004",
    "transaction1500005",
    "transaction1500006",
    "transaction1500007",
    "transaction1500008",
    "transaction1500009",
    "transaction1500010",
    "transaction1500011",
    "transaction1500012",
    "transaction1500013",
    "transaction1500014",
    "transaction1500015",
    "transaction1500016",
    "transaction1500017",
    "transaction1500018",
    "transaction1500019",
    "transaction1500020"
]

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
def test_multi_download_case1(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.tokenUtil.TokenUtilClass.verify_token_closed").side_effect = Exception('testException')
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multiDownload", headers=header, data=json.dumps(request_body_copy))
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
def test_multi_download_case2(create_header):
    header = create_header["header"]
    none_search_criteria = {
        "userIdMatchMode": None,
        "userIdStr": None,
        "dataJsonKey": None,
        "dataMatchMode": None,
        "dataStr": None,
        "imageHash": None,
        "fromDate": "2022/01/01",
        "toDate": "2022/12/31"
    }
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["tidList"] = TID_LIST
    request_body_copy["searchCriteria"] = none_search_criteria
    response = client.post("/api/2.0/transaction/multiDownload", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "inquiryId": response.json()["inquiryId"]
    }
    print(response.json())


# No3.接続に失敗する。設定値を異常な値に変更する
def test_multi_download_case3(mocker: MockerFixture, create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    mocker.patch.object(SystemConstClass, "PDS_COMMON_DB_SECRET_INFO", {"SECRET_NAME": "pds-common-sm-ng"})
    multi_download_model = multiDownloadModel(trace_logger, Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    model_request = modelRequestBody(**REQUEST_BODY)
    with pytest.raises(PDSException) as e:
        multi_download_model.main(model_request)

    assert e.value.args[0] == {
        "errorCode": "999999",
        "message": e.value.args[0]["message"]
    }
    print(e)


# No4.接続に成功する
def test_multi_download_case4(create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multiDownload", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "inquiryId": response.json()["inquiryId"]
    }
    print(response.json())


# No5.承認者情報確認処理が失敗する
def test_multi_download_case5(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.commonUtil.CommonUtilClass.check_approval_user_info").side_effect = Exception('testException')
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multiDownload", headers=header, data=json.dumps(request_body_copy))
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
def test_multi_download_case6(create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multiDownload", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "inquiryId": response.json()["inquiryId"]
    }
    print(response.json())


# No7.「変数.PDSユーザ情報」が0件
def test_multi_download_case7(create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["pdsUserId"] = "C3333333"
    response = client.post("/api/2.0/transaction/multiDownload", headers=header, data=json.dumps(request_body_copy))
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
def test_multi_download_case8(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "MONGODB_SECRET_NAME_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multiDownload", headers=header, data=json.dumps(request_body_copy))
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
def test_multi_download_case9(create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multiDownload", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "inquiryId": response.json()["inquiryId"]
    }
    print(response.json())


# No10.共通エラーチェック処理が成功（エラー情報有り）
def test_multi_download_case10(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "MONGODB_SECRET_NAME_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multiDownload", headers=header, data=json.dumps(request_body_copy))
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
def test_multi_download_case11(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multiDownload", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "inquiryId": response.json()["inquiryId"]
    }
    print(response.json())


# No12.リクエストの「リクエストボディ．tidリスト」がNull以外
def test_multi_download_case12(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["tidList"] = ["transaction1", "transaction2"]
    response = client.post("/api/2.0/transaction/multiDownload", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "inquiryId": response.json()["inquiryId"]
    }
    print(response.json())


# No13.tidリスト作成処理が失敗する
def test_multi_download_case13(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.commonUtil.CommonUtilClass.mongodb_search").side_effect = Exception('testException')
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multiDownload", headers=header, data=json.dumps(request_body_copy))
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
def test_multi_download_case14(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multiDownload", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "inquiryId": response.json()["inquiryId"]
    }
    print(response.json())


# No15.問い合わせID発行処理が成功する
def test_multi_download_case15(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multiDownload", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "inquiryId": response.json()["inquiryId"]
    }
    print(response.json())


# No16.WBT状態管理登録トランザクションのトランザクション作成処理が失敗する
#      コネクション作成時に自動作成なので検証不可


# No17.WBT状態管理登録トランザクションのトランザクション作成処理が成功する
#      コネクション作成時に自動作成なので検証不可


# No18.個人情報一括DL状態管理テーブル登録処理が失敗する
def test_multi_download_case18(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "MULTI_DOWUNLOAD_STATUS_MANAGE_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multiDownload", headers=header, data=json.dumps(request_body_copy))
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


# No19.個人情報一括DL状態管理テーブル登録処理が成功する
def test_multi_download_case19(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multiDownload", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "inquiryId": response.json()["inquiryId"]
    }
    print(response.json())


# No20.共通エラーチェック処理が成功（エラー情報有り）
def test_multi_download_case20(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "MULTI_DOWUNLOAD_STATUS_MANAGE_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multiDownload", headers=header, data=json.dumps(request_body_copy))
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


# No21.個人情報一括DL対象個人情報IDテーブル登録処理が失敗する
def test_multi_download_case21(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "MULTI_DOWUNLOAD_TARGET_TRANSACTION_ID_BULK_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multiDownload", headers=header, data=json.dumps(request_body_copy))
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


# No22.個人情報一括DL対象個人情報IDテーブル登録処理が成功する
def test_multi_download_case22(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multiDownload", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "inquiryId": response.json()["inquiryId"]
    }
    print(response.json())


# No23.共通エラーチェック処理が成功（エラー情報有り）
def test_multi_download_case23(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "MULTI_DOWUNLOAD_TARGET_TRANSACTION_ID_BULK_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multiDownload", headers=header, data=json.dumps(request_body_copy))
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


# No24.WBT状態管理登録トランザクションのコミット処理が失敗する
def test_multi_download_case24(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(PostgresDbUtilClass, "commit_transaction", side_effect=Exception('testException'))
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multiDownload", headers=header, data=json.dumps(request_body_copy))
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


# No25.WBT状態管理登録トランザクションのコミット処理が成功する
def test_multi_download_case25(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multiDownload", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "inquiryId": response.json()["inquiryId"]
    }
    print(response.json())


# No26.個人情報一括DLバッチキュー発行処理が失敗する
def test_multi_download_case26(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SystemConstClass, "SQS_MULTI_DOWNLOAD_QUEUE_NAME", 'testQueue')
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multiDownload", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "990052",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No27.個人情報一括DLバッチキュー発行処理が成功する
def test_multi_download_case27(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multiDownload", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "inquiryId": response.json()["inquiryId"]
    }
    print(response.json())


# No28.共通エラーチェック処理が成功（エラー情報有り）
def test_multi_download_case28(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SystemConstClass, "SQS_MULTI_DOWNLOAD_QUEUE_NAME", 'testQueue')
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multiDownload", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "990052",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No29.アクセストークン発行処理が失敗する
def test_multi_download_case29(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.tokenUtil.TokenUtilClass.create_token_closed").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multiDownload", headers=header, data=json.dumps(request_body_copy))
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


# No30.アクセストークン発行処理が成功する
def test_multi_download_case30(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multiDownload", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "inquiryId": response.json()["inquiryId"]
    }
    print(response.json())


# No31.共通エラーチェック処理が成功（エラー情報有り）
def test_multi_download_case31(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.tokenUtil.TokenUtilClass.create_token_closed").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multiDownload", headers=header, data=json.dumps(request_body_copy))
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


# No32.変数．エラー情報がある(No.5でエラー）
def test_multi_download_case32(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.commonUtil.CommonUtilClass.check_approval_user_info").side_effect = Exception('testException')
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multiDownload", headers=header, data=json.dumps(request_body_copy))
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


# No33.変数．エラー情報がない
def test_multi_download_case33(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multiDownload", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "inquiryId": response.json()["inquiryId"]
    }
    print(response.json())


# No34.アクセストークン検証処理が失敗する
def test_multi_download_case34(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.tokenUtil.TokenUtilClass.verify_token_closed").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multiDownload", headers=header, data=json.dumps(request_body_copy))
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


# No35.アクセストークン検証処理が成功する
def test_multi_download_case35(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multiDownload", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "inquiryId": response.json()["inquiryId"]
    }
    print(response.json())


# No36.共通エラーチェック処理が成功（エラー情報有り）
def test_multi_download_case36(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.tokenUtil.TokenUtilClass.verify_token_closed").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multiDownload", headers=header, data=json.dumps(request_body_copy))
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


# No37.パラメータ検証処理が失敗する
def test_multi_download_case37(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("routers.closed.multiDownloadRouter.input_check").side_effect = Exception("test-Exception")
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multiDownload", headers=header, data=json.dumps(request_body_copy))
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


# No38.パラメータ検証処理が成功する
def test_multi_download_case38(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multiDownload", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "inquiryId": response.json()["inquiryId"]
    }
    print(response.json())


# No39.共通エラーチェック処理が成功（エラー情報有り）
def test_multi_download_case39(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["pdsUserId"] = None
    response = client.post("/api/2.0/transaction/multiDownload", headers=header, data=json.dumps(request_body_copy))
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


# No40.変数．エラー情報がない
def test_multi_download_case40(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multiDownload", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "inquiryId": response.json()["inquiryId"]
    }
    print(response.json())


# No41-1.タイムスタンプ 値が設定されていない（空値）
def test_multi_download_case41_1(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-2.タイムスタンプ 文字列型以外、22桁
def test_multi_download_case41_2(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-3.タイムスタンプ 文字列型、24桁、入力規則違反している　hh:mmがhhh:mm
def test_multi_download_case41_3(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No26-16.アクセストークン 値が設定されていない（空値）
def test_multi_download_case41_4(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-5.アクセストークン 文字列型以外、201桁
def test_multi_download_case41_5(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-6.アクセストークン 文字列型、199桁、入力可能文字以外が含まれる（全角）
def test_multi_download_case41_6(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-7.アクセストークン 文字列型、200桁、入力可能文字のみ（半角英数字） [a-fA-F0-9]
def test_multi_download_case41_7(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-8.PDSユーザID 値が設定されていない（空値）
def test_multi_download_case41_8(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-9.PDSユーザID 文字列型以外、7桁、C以外の文字で始まる
def test_multi_download_case41_9(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-10.PDSユーザID 文字列型、8桁、入力規則違反していない（C＋数値7桁）
def test_multi_download_case41_10(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-11.検索用ユーザID検索モード 文字列以外、入力可能文字以外が含まれる
def test_multi_download_case41_11(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-12.検索用ユーザID検索モード 文字列、入力可能文字以外が含まれる
def test_multi_download_case41_12(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-13.検索用ユーザID検索モード 文字列、入力可能文字のみ
def test_multi_download_case41_13(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-14.検索用ユーザID検索文字列 文字列以外、37桁
def test_multi_download_case41_14(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-15.検索用ユーザID検索文字列 文字列、36桁
def test_multi_download_case41_15(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-16.保存データJsonキー情報 文字列以外
def test_multi_download_case41_16(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-17.保存データJsonキー情報 文字列
def test_multi_download_case41_17(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-18.保存データ検索モード 文字列以外
def test_multi_download_case41_18(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-19.保存データ検索モード 文字列、入力可能文字以外が含まれる
def test_multi_download_case41_19(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-20.保存データ検索モード 文字列、入力可能文字のみ
def test_multi_download_case41_20(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-21.保存データ検索文字列 文字列以外
def test_multi_download_case41_21(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-22.保存データ検索文字列 文字列
def test_multi_download_case41_22(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-23.保存されたバイナリデータのハッシュ値 文字列型以外
def test_multi_download_case41_23(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-24.保存されたバイナリデータのハッシュ値 入力可能文字以外を含む
def test_multi_download_case41_24(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-25.保存されたバイナリデータのハッシュ値 入力可能文字
def test_multi_download_case41_25(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-26.検索用日時From 文字列以外、11文字
def test_multi_download_case41_26(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-27.検索用日時From 文字列以外、11文字
def test_multi_download_case41_27(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-28.検索用日時From 文字列、10文字、入力規則
def test_multi_download_case41_28(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-29.検索用日時To 文字列以外、11文字
def test_multi_download_case41_29(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-30.検索用日時To 文字列以外、11文字
def test_multi_download_case41_30(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-31.検索用日時To 文字列、10文字、入力規則
def test_multi_download_case41_31(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-32.承認TFオペレータID 未入力
def test_multi_download_case41_32(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-33.承認TFオペレータID 文字列以外 16桁超過
def test_multi_download_case41_33(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-34.承認TFオペレータID 文字列 3桁未満 入力可能文字以外を含む
def test_multi_download_case41_34(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-35.承認TFオペレータID 文字列 16桁 入力可能文字のみ
def test_multi_download_case41_35(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-36.承認TFオペレータパスワード 未入力
def test_multi_download_case41_36(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-37.承認TFオペレータパスワード 文字列以外 8桁未満
def test_multi_download_case41_37(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-38.承認TFオペレータパスワード 文字列 617桁超過 入力可能文字以外を含む 入力規則違反
def test_multi_download_case41_38(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-39.承認TFオペレータパスワード 文字列 8桁 入力可能文字のみ 入力規則
def test_multi_download_case41_39(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-40.メールアドレスTo 未入力
def test_multi_download_case41_40(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-41.宛先To 文字列以外
def test_multi_download_case41_41(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-42.宛先To 文字列 512桁超過 入力可能文字以外を含む 入力規則違反
def test_multi_download_case41_42(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-43.宛先To 文字列 512桁 入力可能文字のみ 入力規則
def test_multi_download_case41_43(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-44.宛先Cc 文字列以外
def test_multi_download_case41_44(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-45.宛先Cc 文字列 512桁超過 入力可能文字以外を含む 入力規則違反
def test_multi_download_case41_45(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-46.宛先Cc 文字列 512桁 入力可能文字のみ 入力規則
def test_multi_download_case41_46(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-47.承認ユーザIDとトークン検証結果のIDが同じ
def test_multi_download_case41_47(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-48.承認ユーザIDとトークン検証結果のIDが異なる
def test_multi_download_case41_48(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-49.tidリスト 文字列以外 36桁超過
def test_multi_download_case41_49(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-50.tidリスト 配列型文字列以外を含む 36桁超過
def test_multi_download_case41_50(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-51.tidリスト 文字列 36桁 入力可能文字のみ
def test_multi_download_case41_51(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-52.tidリスト 配列型文字列のみ 36桁 入力可能文字のみ
def test_multi_download_case41_52(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-53.検索日時Fromと検索用日時To 相関 FromがToを超過
def test_multi_download_case41_53(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No41-54.検索日時Fromと検索用日時To 相関 FromがToを超過しない
def test_multi_download_case41_54(create_header):
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
    response = multiDownloadRouter.input_check(
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


# No42.変数．エラー情報がない
def test_multi_download_case42(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multiDownload", headers=header, data=json.dumps(request_body_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "inquiryId": response.json()["inquiryId"]
    }
    print(response.json())


# No43.変数．エラー情報がある
def test_multi_download_case43(mocker: MockerFixture, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["pdsUserId"] = None
    response = client.post("/api/2.0/transaction/multiDownload", headers=header, data=json.dumps(request_body_copy))
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


# No44.パラメータ取得処理が失敗する
def test_multi_download_case44(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    request_body_task_copy["pdsUserId"] = None
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No45.パラメータ取得処理が成功する
def test_multi_download_case45(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No46.接続に失敗する。設定値を異常な値に変更する
def test_multi_download_case46(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    mocker.patch.object(SystemConstClass, "PDS_COMMON_DB_SECRET_INFO", {"SECRET_NAME": "pds-common-sm-ng"})
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No47.接続に成功する
def test_multi_download_case47(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No48.「変数.PDSユーザ情報」が0件
def test_multi_download_case48(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    request_body_task_copy["pdsUserId"] = "C3333333"
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No49.PDSユーザ取得処理が失敗する
def test_multi_download_case49(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    mocker.patch.object(SqlConstClass, "MONGODB_SECRET_NAME_BUCKET_NAME_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No50.PDSユーザ取得処理が成功する
def test_multi_download_case50(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No51.共通エラーチェック処理が成功（エラー情報有り）
def test_multi_download_case51(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    mocker.patch.object(SqlConstClass, "MONGODB_SECRET_NAME_BUCKET_NAME_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No52.個人情報一括DL状態管理取得処理が失敗する
def test_multi_download_case52(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    mocker.patch.object(SqlConstClass, "MULTI_DOWUNLOAD_TARGET_TRANSACTION_ID_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No53.個人情報一括DL状態管理取得処理が成功する
def test_multi_download_case53(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No54.共通エラーチェック処理が成功（エラー情報有り）
def test_multi_download_case54(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    mocker.patch.object(SqlConstClass, "MULTI_DOWUNLOAD_TARGET_TRANSACTION_ID_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No55.接続に失敗する。設定値を異常な値に変更する
def test_multi_download_case55(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    mocker.patch("util.commonUtil.CommonUtilClass.get_pds_user_db_info_and_connection").side_effect = Exception('testException')
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No56.接続に成功する
def test_multi_download_case56(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No57.「変数.個人情報取得結果」が0件
def test_multi_download_case57(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    request_body_task_copy["requestNo"] = "1b3de9435e024541a9fc43dd96f73dbe"
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No58.個人情報取得処理実行処理が失敗する
def test_multi_download_case58(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    mocker.patch.object(SqlConstClass, "USER_PROFILE_MULTI_DOWNLOAD_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No59.個人情報取得処理実行処理が成功する
def test_multi_download_case59(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No60.共通エラーチェック処理が成功（エラー情報有り）
def test_multi_download_case60(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    mocker.patch.object(SqlConstClass, "USER_PROFILE_MULTI_DOWNLOAD_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No61.個人情報取得処理リスト初期化処理が成功する
def test_multi_download_case61(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No62.「変数．個人情報取得結果リスト」の要素が0以外
def test_multi_download_case62(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No63.個人情報取得処理リスト作成処理が成功する
def test_multi_download_case63(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No64.個人情報取得処理実行処理が失敗する
def test_multi_download_case64(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    mocker.patch.object(SqlConstClass, "USER_PROFILE_BINARY_GET_READ_TARGET_SQL", """ SELECT * FROM AAAAAA; """)
    mocker.patch("util.kmsUtil.KmsUtilClass.decrypt_kms_data_key").side_effect = Exception("test-exception")
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No65.個人情報取得処理実行処理が成功する
def test_multi_download_case65(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No66.共通エラーチェック処理が成功（エラー情報有り）
def test_multi_download_case66(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    mocker.patch.object(SqlConstClass, "USER_PROFILE_BINARY_GET_READ_TARGET_SQL", """ SELECT * FROM AAAAAA; """)
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No67.個人情報一括DLファイル分割リスト初期化処理が成功する
def test_multi_download_case67(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No68.「変数．変数．個人情報取得結果リスト」の要素が0以外
def test_multi_download_case68(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No69.個人情報作成処理が成功する
def test_multi_download_case69(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No70.個人情報作成処理が成功する（2GB超過のデータで対応）
def test_multi_download_case70(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    request_body_task_copy = REQUEST_BODY_TASK_2GB.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No71.分割ファイルリスト情報作成が成功する
def test_multi_download_case71(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No72.個人情報一括DL通知ファイルリスト初期化処理が成功する
def test_multi_download_case72(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No73.「変数．分割ファイルリスト」の要素が0以外
def test_multi_download_case73(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No74.jsonファイル作成処理が失敗する
def test_multi_download_case74(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    mocker.patch.object(FileNameConstClass, "MULTI_DOWNLOAD_JSON_NAME", 13)
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No75.jsonファイル作成処理が成功する
def test_multi_download_case75(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No76.個人情報一括DL状態管理更新トランザクションのトランザクション作成処理が失敗する
#      コネクション作成時に自動作成なので検証不可


# No77.個人情報一括DL状態管理更新トランザクションのトランザクション作成処理が成功する
#      コネクション作成時に自動作成なので検証不可


# No78.個人情報一括DL状態管理更新処理が失敗する
def test_multi_download_case78(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    mocker.patch.object(SqlConstClass, "MULTI_DOWUNLOAD_STATUS_MANAGE_WBT_EXEC_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No79.個人情報一括DL状態管理更新処理が成功する
def test_multi_download_case79(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No80.共通エラーチェック処理が成功（エラー情報有り）
def test_multi_download_case80(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    mocker.patch.object(SqlConstClass, "MULTI_DOWUNLOAD_STATUS_MANAGE_WBT_EXEC_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No81.個人情報一括DL状態管理更新トランザクションのコミット処理が失敗する
def test_multi_download_case81(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    mocker.patch.object(PostgresDbUtilClass, "commit_transaction", side_effect=Exception('testException'))
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No82.個人情報一括DL状態管理更新トランザクションのコミット処理が成功する
def test_multi_download_case82(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No83.「変数．個人情報一括DL通知ファイルリスト」の要素数が0
#      tidリストが存在しない場合というのが前提になるのでPytestだけではテスト不可？デバッグでテストする
def test_multi_download_case83(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No84.「変数．個人情報一括DL通知ファイルリスト」の要素数が0以外
def test_multi_download_case84(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No85.WBT新規メール情報登録API実行処理が失敗する
def test_multi_download_case85(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    mocker.patch("util.commonUtil.CommonUtilClass.wbt_mails_add_api_exec").side_effect = Exception('testException')
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No86.WBT新規メール情報登録API実行処理が成功する
def test_multi_download_case86(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No87.共通エラーチェック処理が成功（エラー情報有り）
def test_multi_download_case87(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    mocker.patch("util.commonUtil.CommonUtilClass.wbt_mails_add_api_exec").side_effect = Exception('testException')
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No88.WBTファイル登録API実行処理が失敗する
def test_multi_download_case88(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    mocker.patch("util.commonUtil.CommonUtilClass.wbt_file_add_api_exec").side_effect = Exception('testException')
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No89.WBTファイル登録API実行処理が成功する
def test_multi_download_case89(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No90.共通エラーチェック処理が成功（エラー情報有り）
def test_multi_download_case90(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    mocker.patch("util.commonUtil.CommonUtilClass.wbt_file_add_api_exec").side_effect = Exception('testException')
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No91.個人情報一括DL通知ファイル削除処理が成功する
def test_multi_download_case91(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No92.WBT状態管理更新トランザクションのトランザクション作成処理が失敗する
#      コネクション作成時に自動作成なので検証不可


# No93.WBT状態管理更新トランザクションのトランザクション作成処理が成功する
#      コネクション作成時に自動作成なので検証不可


# No94.個人情報一括DL状態管理テーブル更新処理が失敗する
def test_multi_download_case94(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    mocker.patch.object(SqlConstClass, "MULTI_DOWUNLOAD_STATUS_MANAGE_MAIL_ID_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No95.「変数．個人情報一括DL通知ファイル[変数．一括DLファイルループ数]．インデックス」が 0
def test_multi_download_case95(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No96.「変数．個人情報一括DL通知ファイル[変数．一括DLファイルループ数]．インデックス」が 0以外
def test_multi_download_case96(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No97.個人情報一括DL状態管理テーブル更新処理が成功する
def test_multi_download_case97(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No98.共通エラーチェック処理が成功（エラー情報有り）
def test_multi_download_case98(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    mocker.patch.object(SqlConstClass, "MULTI_DOWUNLOAD_STATUS_MANAGE_MAIL_ID_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No99.WBT状態管理更新トランザクションのコミット処理が失敗する
def test_multi_download_case99(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    mocker.patch.object(PostgresDbUtilClass, "commit_transaction", side_effect=[True, Exception('testException')])
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No100.WBT状態管理更新トランザクションのコミット処理が成功する
def test_multi_download_case100(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No101.WBT状態管理更新トランザクションのトランザクション作成処理が失敗する
#      コネクション作成時に自動作成なので検証不可


# No102.WBT状態管理更新トランザクションのトランザクション作成処理が成功する
#      コネクション作成時に自動作成なので検証不可


# No103.個人情報一括DL状態管理テーブル更新処理が失敗する
def test_multi_download_case103(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    mocker.patch.object(SqlConstClass, "MULTI_DOWUNLOAD_STATUS_MANAGE_EXIT_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No104.個人情報一括DL状態管理テーブル更新処理が成功する
def test_multi_download_case104(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No105.共通エラーチェック処理が成功（エラー情報有り）
def test_multi_download_case105(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    mocker.patch.object(SqlConstClass, "MULTI_DOWUNLOAD_STATUS_MANAGE_EXIT_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No106.個人情報一括DL状態管理更新トランザクションのコミット処理が失敗する
def test_multi_download_case106(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    mocker.patch.object(PostgresDbUtilClass, "commit_transaction", side_effect=[True, True, Exception('testException')])
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No107.個人情報一括DL状態管理更新トランザクションのコミット処理が成功する
def test_multi_download_case107(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No108.API実行履歴登録処理が失敗する
def test_multi_download_case108(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    mocker.patch("util.commonUtil.get_datetime_str_no_symbol").side_effect = ["20220927145527512", "20220927145527512", "20220101000000000"]
    mocker.patch("util.commonUtil.get_random_ascii").side_effect = ["O1MOs01uEKinK", ''.join(random.choices(string.ascii_letters + string.digits, k=13))]
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No109.API実行履歴登録処理が成功する
def test_multi_download_case109(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No111.変数．エラー情報がない
def test_multi_download_case111(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No112.接続に失敗する。設定値を異常な値に変更する
@pytest.mark.asyncio
async def test_multi_download_case112(mocker: MockerFixture):
    pds_user_db_secret_info = {
        "host": "pds-c0000000.cluster-ct7qlfhnwver.ap-northeast-1.rds.amazonaws.com",
        "port": "5432",
        "username": "postgres-NG",
        "password": "9qj5LHTj4V6RozYkoDzo",
    }
    transaction_id = "transaction1500001"
    pds_user_info = {
        "pdsUserId": "C9876543",
        "pdsUserDomainName": "pds-user-create",
        "s3ImageDataBucketName": "pds-c0000000-bucket"
    }
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    common_util = CommonUtilClass(trace_logger)
    common_db_info_response = common_util.get_common_db_info_and_connection()
    tf_operator_id = "t-test4"
    multi_download_model = multiDownloadModel(trace_logger, REQUEST)
    with pytest.raises(PDSException) as e:
        await multi_download_model.get_user_profile_info_exec(
            pds_user_db_secret_info=pds_user_db_secret_info,
            transaction_id=transaction_id,
            pds_user_info=pds_user_info,
            request_id=REQUEST_BODY_TASK["requestNo"],
            common_db_info_response=common_db_info_response,
            request_body=REQUEST_BODY_TASK,
            request=REQUEST,
            tf_operator_id=tf_operator_id
        )

    assert e.value.args[0] == {
        "errorCode": "999999",
        "message": e.value.args[0]["message"]
    }
    print(e)


# No113.接続に成功する
@pytest.mark.asyncio
async def test_multi_download_case113(mocker: MockerFixture):
    pds_user_db_secret_info = {
        "host": "pds-c0000000.cluster-ct7qlfhnwver.ap-northeast-1.rds.amazonaws.com",
        "port": "5432",
        "username": "postgres",
        "password": "9qj5LHTj4V6RozYkoDzo",
    }
    transaction_id = "transaction1500001"
    pds_user_info = {
        "pdsUserId": "C9876543",
        "pdsUserDomainName": "pds-user-create",
        "s3ImageDataBucketName": "pds-c0000000-bucket"
    }
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    common_util = CommonUtilClass(trace_logger)
    common_db_info_response = common_util.get_common_db_info_and_connection()
    tf_operator_id = "t-test4"
    multi_download_model = multiDownloadModel(trace_logger, REQUEST)
    response = await multi_download_model.get_user_profile_info_exec(
        pds_user_db_secret_info=pds_user_db_secret_info,
        transaction_id=transaction_id,
        pds_user_info=pds_user_info,
        request_id=REQUEST_BODY_TASK["requestNo"],
        common_db_info_response=common_db_info_response,
        request_body=REQUEST_BODY_TASK,
        request=REQUEST,
        tf_operator_id=tf_operator_id
    )
    assert response == {
        "result": True,
        "transactionId": transaction_id,
        "transactionInfo": response["transactionInfo"]
    }


# No114.「変数.個人情報取得結果リスト」が0件
@pytest.mark.asyncio
async def test_multi_download_case114(mocker: MockerFixture):
    pds_user_db_secret_info = {
        "host": "pds-c0000000.cluster-ct7qlfhnwver.ap-northeast-1.rds.amazonaws.com",
        "port": "5432",
        "username": "postgres",
        "password": "9qj5LHTj4V6RozYkoDzo",
    }
    # 存在しないトランザクションIDを指定
    transaction_id = "transaction0"
    pds_user_info = {
        "pdsUserId": "C9876543",
        "pdsUserDomainName": "pds-user-create",
        "s3ImageDataBucketName": "pds-c0000000-bucket"
    }
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    common_util = CommonUtilClass(trace_logger)
    common_db_info_response = common_util.get_common_db_info_and_connection()
    tf_operator_id = "t-test4"
    multi_download_model = multiDownloadModel(trace_logger, REQUEST)
    response = await multi_download_model.get_user_profile_info_exec(
        pds_user_db_secret_info=pds_user_db_secret_info,
        transaction_id=transaction_id,
        pds_user_info=pds_user_info,
        request_id=REQUEST_BODY_TASK["requestNo"],
        common_db_info_response=common_db_info_response,
        request_body=REQUEST_BODY_TASK,
        request=REQUEST,
        tf_operator_id=tf_operator_id
    )

    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "020004",
            "message": response["errorInfo"]["message"]
        }
    }
    print(response)


# No115.個人情報取得処理が失敗する
@pytest.mark.asyncio
async def test_multi_download_case115(mocker: MockerFixture):
    pds_user_db_secret_info = {
        "host": "pds-c0000000.cluster-ct7qlfhnwver.ap-northeast-1.rds.amazonaws.com",
        "port": "5432",
        "username": "postgres",
        "password": "9qj5LHTj4V6RozYkoDzo",
    }
    transaction_id = "transaction1500001"
    pds_user_info = {
        "pdsUserId": "C9876543",
        "pdsUserDomainName": "pds-user-create",
        "s3ImageDataBucketName": "pds-c0000000-bucket"
    }
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    common_util = CommonUtilClass(trace_logger)
    common_db_info_response = common_util.get_common_db_info_and_connection()
    tf_operator_id = "t-test4"
    mocker.patch.object(SqlConstClass, "USER_PROFILE_READ_SQL", """ SELECT * FROM AAAAAA; """)
    multi_download_model = multiDownloadModel(trace_logger, REQUEST)
    response = await multi_download_model.get_user_profile_info_exec(
        pds_user_db_secret_info=pds_user_db_secret_info,
        transaction_id=transaction_id,
        pds_user_info=pds_user_info,
        request_id=REQUEST_BODY_TASK["requestNo"],
        common_db_info_response=common_db_info_response,
        request_body=REQUEST_BODY_TASK,
        request=REQUEST,
        tf_operator_id=tf_operator_id
    )

    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "991028",
            "message": response["errorInfo"]["message"]
        }
    }
    print(response)


# No116.個人情報取得処理が成功する
@pytest.mark.asyncio
async def test_multi_download_case116(mocker: MockerFixture):
    pds_user_db_secret_info = {
        "host": "pds-c0000000.cluster-ct7qlfhnwver.ap-northeast-1.rds.amazonaws.com",
        "port": "5432",
        "username": "postgres",
        "password": "9qj5LHTj4V6RozYkoDzo",
    }
    transaction_id = "transaction30000"
    pds_user_info = {
        "pdsUserId": "C9876543",
        "pdsUserDomainName": "pds-user-create",
        "s3ImageDataBucketName": "pds-c0000000-bucket"
    }
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    common_util = CommonUtilClass(trace_logger)
    common_db_info_response = common_util.get_common_db_info_and_connection()
    tf_operator_id = "t-test4"
    multi_download_model = multiDownloadModel(trace_logger, REQUEST)
    response = await multi_download_model.get_user_profile_info_exec(
        pds_user_db_secret_info=pds_user_db_secret_info,
        transaction_id=transaction_id,
        pds_user_info=pds_user_info,
        request_id=REQUEST_BODY_TASK["requestNo"],
        common_db_info_response=common_db_info_response,
        request_body=REQUEST_BODY_TASK,
        request=REQUEST,
        tf_operator_id=tf_operator_id
    )
    assert response == {
        "result": True,
        "transactionId": transaction_id,
        "transactionInfo": response["transactionInfo"]
    }


# No117.共通エラーチェック処理が成功（エラー情報有り）
@pytest.mark.asyncio
async def test_multi_download_case117(mocker: MockerFixture):
    pds_user_db_secret_info = {
        "host": "pds-c0000000.cluster-ct7qlfhnwver.ap-northeast-1.rds.amazonaws.com",
        "port": "5432",
        "username": "postgres",
        "password": "9qj5LHTj4V6RozYkoDzo",
    }
    transaction_id = "transaction30000"
    pds_user_info = {
        "pdsUserId": "C9876543",
        "pdsUserDomainName": "pds-user-create",
        "s3ImageDataBucketName": "pds-c0000000-bucket"
    }
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    common_util = CommonUtilClass(trace_logger)
    common_db_info_response = common_util.get_common_db_info_and_connection()
    tf_operator_id = "t-test4"
    mocker.patch.object(SqlConstClass, "USER_PROFILE_READ_SQL", """ SELECT * FROM AAAAAA; """)
    multi_download_model = multiDownloadModel(trace_logger, REQUEST)
    response = await multi_download_model.get_user_profile_info_exec(
        pds_user_db_secret_info=pds_user_db_secret_info,
        transaction_id=transaction_id,
        pds_user_info=pds_user_info,
        request_id=REQUEST_BODY_TASK["requestNo"],
        common_db_info_response=common_db_info_response,
        request_body=REQUEST_BODY_TASK,
        request=REQUEST,
        tf_operator_id=tf_operator_id
    )
    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "991028",
            "message": response["errorInfo"]["message"]
        }
    }
    print(response)


# No118.個人情報取得処理が失敗する
@pytest.mark.asyncio
async def test_multi_download_case118(mocker: MockerFixture):
    pds_user_db_secret_info = {
        "host": "pds-c0000000.cluster-ct7qlfhnwver.ap-northeast-1.rds.amazonaws.com",
        "port": "5432",
        "username": "postgres",
        "password": "9qj5LHTj4V6RozYkoDzo",
    }
    transaction_id = "transaction30000"
    pds_user_info = {
        "pdsUserId": "C9876543",
        "pdsUserDomainName": "pds-user-create",
        "s3ImageDataBucketName": "pds-c0000000-bucket"
    }
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    common_util = CommonUtilClass(trace_logger)
    common_db_info_response = common_util.get_common_db_info_and_connection()
    tf_operator_id = "t-test4"
    mocker.patch.object(SqlConstClass, "USER_PROFILE_BINARY_GET_READ_TARGET_SQL", """ SELECT * FROM AAAAAA; """)
    multi_download_model = multiDownloadModel(trace_logger, REQUEST)
    response = await multi_download_model.get_user_profile_info_exec(
        pds_user_db_secret_info=pds_user_db_secret_info,
        transaction_id=transaction_id,
        pds_user_info=pds_user_info,
        request_id=REQUEST_BODY_TASK["requestNo"],
        common_db_info_response=common_db_info_response,
        request_body=REQUEST_BODY_TASK,
        request=REQUEST,
        tf_operator_id=tf_operator_id
    )
    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "991028",
            "message": response["errorInfo"]["message"]
        }
    }
    print(response)


# No119.個人バイナリ情報取得処理が成功する
@pytest.mark.asyncio
async def test_multi_download_case119(mocker: MockerFixture):
    pds_user_db_secret_info = {
        "host": "pds-c0000000.cluster-ct7qlfhnwver.ap-northeast-1.rds.amazonaws.com",
        "port": "5432",
        "username": "postgres",
        "password": "9qj5LHTj4V6RozYkoDzo",
    }
    transaction_id = "transaction30000"
    pds_user_info = {
        "pdsUserId": "C9876543",
        "pdsUserDomainName": "pds-user-create",
        "s3ImageDataBucketName": "pds-c0000000-bucket"
    }
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    common_util = CommonUtilClass(trace_logger)
    common_db_info_response = common_util.get_common_db_info_and_connection()
    tf_operator_id = "t-test4"
    multi_download_model = multiDownloadModel(trace_logger, REQUEST)
    response = await multi_download_model.get_user_profile_info_exec(
        pds_user_db_secret_info=pds_user_db_secret_info,
        transaction_id=transaction_id,
        pds_user_info=pds_user_info,
        request_id=REQUEST_BODY_TASK["requestNo"],
        common_db_info_response=common_db_info_response,
        request_body=REQUEST_BODY_TASK,
        request=REQUEST,
        tf_operator_id=tf_operator_id
    )
    assert response == {
        "result": True,
        "transactionId": transaction_id,
        "transactionInfo": response["transactionInfo"]
    }


# No120.共通エラーチェック処理が成功（エラー情報有り）
@pytest.mark.asyncio
async def test_multi_download_case120(mocker: MockerFixture):
    pds_user_db_secret_info = {
        "host": "pds-c0000000.cluster-ct7qlfhnwver.ap-northeast-1.rds.amazonaws.com",
        "port": "5432",
        "username": "postgres",
        "password": "9qj5LHTj4V6RozYkoDzo",
    }
    transaction_id = "transaction30000"
    pds_user_info = {
        "pdsUserId": "C9876543",
        "pdsUserDomainName": "pds-user-create",
        "s3ImageDataBucketName": "pds-c0000000-bucket"
    }
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    common_util = CommonUtilClass(trace_logger)
    common_db_info_response = common_util.get_common_db_info_and_connection()
    tf_operator_id = "t-test4"
    mocker.patch.object(SqlConstClass, "USER_PROFILE_BINARY_GET_READ_TARGET_SQL", """ SELECT * FROM AAAAAA; """)
    multi_download_model = multiDownloadModel(trace_logger, REQUEST)
    response = await multi_download_model.get_user_profile_info_exec(
        pds_user_db_secret_info=pds_user_db_secret_info,
        transaction_id=transaction_id,
        pds_user_info=pds_user_info,
        request_id=REQUEST_BODY_TASK["requestNo"],
        common_db_info_response=common_db_info_response,
        request_body=REQUEST_BODY_TASK,
        request=REQUEST,
        tf_operator_id=tf_operator_id
    )
    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "991028",
            "message": response["errorInfo"]["message"]
        }
    }
    print(response)


# No121.「変数．個人バイナリ情報取得結果リスト」が0件
@pytest.mark.asyncio
async def test_multi_download_case121(mocker: MockerFixture):
    pds_user_db_secret_info = {
        "host": "pds-c0000000.cluster-ct7qlfhnwver.ap-northeast-1.rds.amazonaws.com",
        "port": "5432",
        "username": "postgres",
        "password": "9qj5LHTj4V6RozYkoDzo",
    }
    # バイナリデータが存在しないトランザクションIDを指定
    transaction_id = "transaction30002"
    pds_user_info = {
        "pdsUserId": "C9876543",
        "pdsUserDomainName": "pds-user-create",
        "s3ImageDataBucketName": "pds-c0000000-bucket"
    }
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    common_util = CommonUtilClass(trace_logger)
    common_db_info_response = common_util.get_common_db_info_and_connection()
    tf_operator_id = "t-test4"
    multi_download_model = multiDownloadModel(trace_logger, REQUEST)
    response = await multi_download_model.get_user_profile_info_exec(
        pds_user_db_secret_info=pds_user_db_secret_info,
        transaction_id=transaction_id,
        pds_user_info=pds_user_info,
        request_id=REQUEST_BODY_TASK["requestNo"],
        common_db_info_response=common_db_info_response,
        request_body=REQUEST_BODY_TASK,
        request=REQUEST,
        tf_operator_id=tf_operator_id
    )
    assert response == {
        "result": True,
        "transactionId": transaction_id,
        "transactionInfo": response["transactionInfo"]
    }
    print(response)


# No122.「変数．個人バイナリ情報取得結果リスト」が1件以上
@pytest.mark.asyncio
async def test_multi_download_case122(mocker: MockerFixture):
    pds_user_db_secret_info = {
        "host": "pds-c0000000.cluster-ct7qlfhnwver.ap-northeast-1.rds.amazonaws.com",
        "port": "5432",
        "username": "postgres",
        "password": "9qj5LHTj4V6RozYkoDzo",
    }
    transaction_id = "transaction30000"
    pds_user_info = {
        "pdsUserId": "C9876543",
        "pdsUserDomainName": "pds-user-create",
        "s3ImageDataBucketName": "pds-c0000000-bucket"
    }
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    common_util = CommonUtilClass(trace_logger)
    common_db_info_response = common_util.get_common_db_info_and_connection()
    tf_operator_id = "t-test4"
    multi_download_model = multiDownloadModel(trace_logger, REQUEST)
    response = await multi_download_model.get_user_profile_info_exec(
        pds_user_db_secret_info=pds_user_db_secret_info,
        transaction_id=transaction_id,
        pds_user_info=pds_user_info,
        request_id=REQUEST_BODY_TASK["requestNo"],
        common_db_info_response=common_db_info_response,
        request_body=REQUEST_BODY_TASK,
        request=REQUEST,
        tf_operator_id=tf_operator_id
    )
    assert response == {
        "result": True,
        "transactionId": transaction_id,
        "transactionInfo": response["transactionInfo"]
    }


# No123.終了処理が成功する
@pytest.mark.asyncio
async def test_multi_download_case123(mocker: MockerFixture):
    pds_user_db_secret_info = {
        "host": "pds-c0000000.cluster-ct7qlfhnwver.ap-northeast-1.rds.amazonaws.com",
        "port": "5432",
        "username": "postgres",
        "password": "9qj5LHTj4V6RozYkoDzo",
    }
    # バイナリデータが存在しないトランザクションIDを指定
    transaction_id = "transaction30002"
    pds_user_info = {
        "pdsUserId": "C9876543",
        "pdsUserDomainName": "pds-user-create",
        "s3ImageDataBucketName": "pds-c0000000-bucket"
    }
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    common_util = CommonUtilClass(trace_logger)
    common_db_info_response = common_util.get_common_db_info_and_connection()
    tf_operator_id = "t-test4"
    multi_download_model = multiDownloadModel(trace_logger, REQUEST)
    response = await multi_download_model.get_user_profile_info_exec(
        pds_user_db_secret_info=pds_user_db_secret_info,
        transaction_id=transaction_id,
        pds_user_info=pds_user_info,
        request_id=REQUEST_BODY_TASK["requestNo"],
        common_db_info_response=common_db_info_response,
        request_body=REQUEST_BODY_TASK,
        request=REQUEST,
        tf_operator_id=tf_operator_id
    )
    assert response == {
        "result": True,
        "transactionId": transaction_id,
        "transactionInfo": response["transactionInfo"]
    }


# No124.ループ処理用変数初期化処理が成功する
@pytest.mark.asyncio
async def test_multi_download_case124(mocker: MockerFixture):
    pds_user_db_secret_info = {
        "host": "pds-c0000000.cluster-ct7qlfhnwver.ap-northeast-1.rds.amazonaws.com",
        "port": "5432",
        "username": "postgres",
        "password": "9qj5LHTj4V6RozYkoDzo",
    }
    transaction_id = "transaction30000"
    pds_user_info = {
        "pdsUserId": "C9876543",
        "pdsUserDomainName": "pds-user-create",
        "s3ImageDataBucketName": "pds-c0000000-bucket"
    }
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    common_util = CommonUtilClass(trace_logger)
    common_db_info_response = common_util.get_common_db_info_and_connection()
    tf_operator_id = "t-test4"
    multi_download_model = multiDownloadModel(trace_logger, REQUEST)
    response = await multi_download_model.get_user_profile_info_exec(
        pds_user_db_secret_info=pds_user_db_secret_info,
        transaction_id=transaction_id,
        pds_user_info=pds_user_info,
        request_id=REQUEST_BODY_TASK["requestNo"],
        common_db_info_response=common_db_info_response,
        request_body=REQUEST_BODY_TASK,
        request=REQUEST,
        tf_operator_id=tf_operator_id
    )
    assert response == {
        "result": True,
        "transactionId": transaction_id,
        "transactionInfo": response["transactionInfo"]
    }


# No125.「変数．個人バイナリ情報取得結果リスト」の要素数が0件以外
# No133.「変数．個人情報バイナリデータループ数」と「変数．個人情報バイナリ情報取得結果リスト」の要素数が一致
# No134.「変数．個人情報バイナリデータループ数」と「変数．個人情報バイナリ情報取得結果リスト」の要素数が一致しない
# No135.バイナリデータ取得処理リスト作成処理が成功する
# No136.バイナリデータハッシュ値格納リスト追加処理が成功する
@pytest.mark.asyncio
async def test_multi_download_case125(mocker: MockerFixture):
    pds_user_db_secret_info = {
        "host": "pds-c0000000.cluster-ct7qlfhnwver.ap-northeast-1.rds.amazonaws.com",
        "port": "5432",
        "username": "postgres",
        "password": "9qj5LHTj4V6RozYkoDzo",
    }
    transaction_id = "transaction30000"
    pds_user_info = {
        "pdsUserId": "C9876543",
        "pdsUserDomainName": "pds-user-create",
        "s3ImageDataBucketName": "pds-c0000000-bucket"
    }
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    common_util = CommonUtilClass(trace_logger)
    common_db_info_response = common_util.get_common_db_info_and_connection()
    tf_operator_id = "t-test4"
    multi_download_model = multiDownloadModel(trace_logger, REQUEST)
    response = await multi_download_model.get_user_profile_info_exec(
        pds_user_db_secret_info=pds_user_db_secret_info,
        transaction_id=transaction_id,
        pds_user_info=pds_user_info,
        request_id=REQUEST_BODY_TASK["requestNo"],
        common_db_info_response=common_db_info_response,
        request_body=REQUEST_BODY_TASK,
        request=REQUEST,
        tf_operator_id=tf_operator_id
    )
    assert response == {
        "result": True,
        "transactionId": transaction_id,
        "transactionInfo": response["transactionInfo"]
    }


# No126.「変数．個人バイナリ情報取得結果リスト[変数．個人情報バイナリデータループ数][1]」が変わった
# No127.「変数．個人バイナリ情報取得結果リスト[変数．個人情報バイナリデータループ数][1]」が同じ
# No128.バイナリデータ取得処理リスト作成処理が成功する
# No129.バイナリデータハッシュ値格納リスト追加処理が成功する
# No130.バイナリデータ取得対象初期化処理が成功する
# No131.バイナリデータ要素数インクリメント処理が成功する
# No132.バイナリデータ要素数インクリメント処理が成功する
@pytest.mark.asyncio
async def test_multi_download_case126(mocker: MockerFixture):
    pds_user_db_secret_info = {
        "host": "pds-c0000000.cluster-ct7qlfhnwver.ap-northeast-1.rds.amazonaws.com",
        "port": "5432",
        "username": "postgres",
        "password": "9qj5LHTj4V6RozYkoDzo",
    }
    # バイナリデータが複数件登録されたデータを選択
    transaction_id = "transaction30003"
    pds_user_info = {
        "pdsUserId": "C9876543",
        "pdsUserDomainName": "pds-user-create",
        "s3ImageDataBucketName": "pds-c0000000-bucket"
    }
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    common_util = CommonUtilClass(trace_logger)
    common_db_info_response = common_util.get_common_db_info_and_connection()
    tf_operator_id = "t-test4"
    multi_download_model = multiDownloadModel(trace_logger, REQUEST)
    response = await multi_download_model.get_user_profile_info_exec(
        pds_user_db_secret_info=pds_user_db_secret_info,
        transaction_id=transaction_id,
        pds_user_info=pds_user_info,
        request_id=REQUEST_BODY_TASK["requestNo"],
        common_db_info_response=common_db_info_response,
        request_body=REQUEST_BODY_TASK,
        request=REQUEST,
        tf_operator_id=tf_operator_id
    )
    assert response == {
        "result": True,
        "transactionId": transaction_id,
        "transactionInfo": response["transactionInfo"]
    }


# No137.個人情報バイナリ分割データ登録処理実行処理が失敗する
@pytest.mark.asyncio
async def test_multi_download_case137(mocker: MockerFixture):
    pds_user_db_secret_info = {
        "host": "pds-c0000000.cluster-ct7qlfhnwver.ap-northeast-1.rds.amazonaws.com",
        "port": "5432",
        "username": "postgres",
        "password": "9qj5LHTj4V6RozYkoDzo",
    }
    transaction_id = "transaction30000"
    pds_user_info = {
        "pdsUserId": "C9876543",
        "pdsUserDomainName": "pds-user-create",
        "s3ImageDataBucketName": "pds-c0000000-bucket"
    }
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    common_util = CommonUtilClass(trace_logger)
    common_db_info_response = common_util.get_common_db_info_and_connection()
    tf_operator_id = "t-test4"
    mocker.patch("util.s3AioUtil.s3AioUtilClass.get_file").side_effect = Exception('testException')
    multi_download_model = multiDownloadModel(trace_logger, REQUEST)
    response = await multi_download_model.get_user_profile_info_exec(
        pds_user_db_secret_info=pds_user_db_secret_info,
        transaction_id=transaction_id,
        pds_user_info=pds_user_info,
        request_id=REQUEST_BODY_TASK["requestNo"],
        common_db_info_response=common_db_info_response,
        request_body=REQUEST_BODY_TASK,
        request=REQUEST,
        tf_operator_id=tf_operator_id
    )
    assert response == {
        "result": False,
        "errorInfo": [
            {"errorCode": "990024", "message": response["errorInfo"][0]["message"]},
            {"errorCode": "990024", "message": response["errorInfo"][1]["message"]}
        ]
    }
    print(response)


# No138.個人情報バイナリ分割データ登録処理実行処理が成功する
# No139.変数．エラー情報がない
@pytest.mark.asyncio
async def test_multi_download_case138(mocker: MockerFixture):
    pds_user_db_secret_info = {
        "host": "pds-c0000000.cluster-ct7qlfhnwver.ap-northeast-1.rds.amazonaws.com",
        "port": "5432",
        "username": "postgres",
        "password": "9qj5LHTj4V6RozYkoDzo",
    }
    transaction_id = "transaction30000"
    pds_user_info = {
        "pdsUserId": "C9876543",
        "pdsUserDomainName": "pds-user-create",
        "s3ImageDataBucketName": "pds-c0000000-bucket"
    }
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    common_util = CommonUtilClass(trace_logger)
    common_db_info_response = common_util.get_common_db_info_and_connection()
    tf_operator_id = "t-test4"
    multi_download_model = multiDownloadModel(trace_logger, REQUEST)
    response = await multi_download_model.get_user_profile_info_exec(
        pds_user_db_secret_info=pds_user_db_secret_info,
        transaction_id=transaction_id,
        pds_user_info=pds_user_info,
        request_id=REQUEST_BODY_TASK["requestNo"],
        common_db_info_response=common_db_info_response,
        request_body=REQUEST_BODY_TASK,
        request=REQUEST,
        tf_operator_id=tf_operator_id
    )
    assert response == {
        "result": True,
        "transactionId": transaction_id,
        "transactionInfo": response["transactionInfo"]
    }
    print(response)


# No140.トランザクション作成処理が失敗する
#      コネクション作成時に自動作成なので検証不可


# No141.トランザクション作成処理が成功する
#      コネクション作成時に自動作成なので検証不可


# No142.個人情報更新処理が失敗する
# No144.共通エラーチェック処理が成功（エラー情報有り）
@pytest.mark.asyncio
async def test_multi_download_case142(mocker: MockerFixture):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    common_util = CommonUtilClass(trace_logger)
    common_db_info_response = common_util.get_common_db_info_and_connection()
    mocker.patch.object(SqlConstClass, "MULTI_DOWUNLOAD_STATUS_MANAGE_EXIT_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    multi_download_model = multiDownloadModel(trace_logger, REQUEST)
    with pytest.raises(PDSException) as e:
        await multi_download_model.update_multi_download_status_manage(
            REQUEST_BODY_TASK["requestNo"],
            common_db_info_response
        )
    assert e.value.args[0] == {
        "errorCode": "991028",
        "message": e.value.args[0]["message"]
    }
    print(e)


# No143.個人情報更新処理が成功する
# No146.トランザクションコミット処理が成功する
# No147.変数．エラー情報がない
def test_multi_download_case143(mocker: MockerFixture):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    common_util = CommonUtilClass(trace_logger)
    common_db_info_response = common_util.get_common_db_info_and_connection()
    multi_download_model = multiDownloadModel(trace_logger, REQUEST)
    response = multi_download_model.update_multi_download_status_manage(
        REQUEST_BODY_TASK["requestNo"],
        common_db_info_response
    )
    assert response is None
    print(response)


# No145.トランザクションコミット処理が失敗する
@pytest.mark.asyncio
async def test_multi_download_case145(mocker: MockerFixture):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    common_util = CommonUtilClass(trace_logger)
    common_db_info_response = common_util.get_common_db_info_and_connection()
    mocker.patch.object(PostgresDbUtilClass, "commit_transaction", side_effect=Exception('testException'))
    multi_download_model = multiDownloadModel(trace_logger, REQUEST)
    with pytest.raises(PDSException) as e:
        await multi_download_model.update_multi_download_status_manage(
            REQUEST_BODY_TASK["requestNo"],
            common_db_info_response
        )
    assert e.value.args[0] == {
        "errorCode": "999999",
        "message": e.value.args[0]["message"]
    }
    print(e)


# No148.WBT状態管理登録トランザクションのロールバック処理が失敗する
# No150.共通エラーチェック処理が成功（エラー情報有り）
def test_multi_download_case148(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "MULTI_DOWUNLOAD_TARGET_TRANSACTION_ID_BULK_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    mocker.patch.object(PostgresDbUtilClass, "rollback_transaction", return_value={"result": False, "errorObject": Exception("test-exception"), "stackTrace": "test-exception"})
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multiDownload", headers=header, data=json.dumps(request_body_copy))
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


# No149.WBT状態管理登録トランザクションのロールバック処理が成功する
# No151.変数．エラー情報がない
def test_multi_download_case149(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "MULTI_DOWUNLOAD_TARGET_TRANSACTION_ID_BULK_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/transaction/multiDownload", headers=header, data=json.dumps(request_body_copy))
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


# No152.WBT状態管理更新トランザクションのロールバック処理が失敗する
# No154.共通エラーチェック処理が成功（エラー情報有り）
def test_multi_download_case152(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    mocker.patch.object(SqlConstClass, "MULTI_DOWUNLOAD_STATUS_MANAGE_EXIT_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    mocker.patch.object(PostgresDbUtilClass, "rollback_transaction", return_value={"result": False, "errorObject": Exception("test-exception"), "stackTrace": "test-exception"})
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No153.WBT状態管理更新トランザクションのロールバック処理が成功する
# No155.変数．エラー情報がない
def test_multi_download_case153(mocker: MockerFixture):
    # 標準出力をモック
    header = {}
    mocker.patch.object(SqlConstClass, "MULTI_DOWUNLOAD_STATUS_MANAGE_EXIT_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    request_body_task_copy = REQUEST_BODY_TASK.copy()
    response = client.post("/api/2.0/transaction/multiDownload/task", headers=header, data=json.dumps(request_body_task_copy))
    print(response.json())


# No156.WBT状態管理更新トランザクションのロールバック処理が失敗する
# No158.共通エラーチェック処理が成功（エラー情報有り）
@pytest.mark.asyncio
async def test_multi_download_case156(mocker: MockerFixture):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    common_util = CommonUtilClass(trace_logger)
    common_db_info_response = common_util.get_common_db_info_and_connection()
    mocker.patch.object(SqlConstClass, "MULTI_DOWUNLOAD_STATUS_MANAGE_EXIT_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    mocker.patch.object(PostgresDbUtilClass, "rollback_transaction", return_value={"result": False, "errorObject": Exception("test-exception"), "stackTrace": "test-exception"})
    multi_download_model = multiDownloadModel(trace_logger, REQUEST)
    with pytest.raises(PDSException) as e:
        await multi_download_model.update_multi_download_status_manage(
            REQUEST_BODY_TASK["requestNo"],
            common_db_info_response
        )
    assert e.value.args[0] == {
        "errorCode": "999999",
        "message": e.value.args[0]["message"]
    }
    print(e)


# No157.WBT状態管理更新トランザクションのロールバック処理が成功する
# No159.変数．エラー情報がない
@pytest.mark.asyncio
async def test_multi_download_case157(mocker: MockerFixture):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    common_util = CommonUtilClass(trace_logger)
    common_db_info_response = common_util.get_common_db_info_and_connection()
    mocker.patch.object(SqlConstClass, "MULTI_DOWUNLOAD_STATUS_MANAGE_EXIT_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    multi_download_model = multiDownloadModel(trace_logger, REQUEST)
    with pytest.raises(PDSException) as e:
        await multi_download_model.update_multi_download_status_manage(
            REQUEST_BODY_TASK["requestNo"],
            common_db_info_response
        )
    assert e.value.args[0] == {
        "errorCode": "991028",
        "message": e.value.args[0]["message"]
    }
    print(e)
