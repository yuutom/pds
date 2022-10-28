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
from util.postgresDbUtil import PostgresDbUtilClass
import routers.public.deleteRouter as deleteRouter
from const.messageConst import MessageConstClass

client = TestClient(app)
EXEC_NAME: str = "delete"

PDS_USER = {
    "pdsUserId": "C0000015",
    "pdsUserName": "個人情報削除テスト"
}
DATA = {
    "tid": "transaction130234",
    "info": {
        "userId": PDS_USER["pdsUserId"],
        "saveDate": "2022/09/26 10:00:00.000",
        "data": "{\"aaa\": \"bbb\"}",
        "image": ["abcde", "123456"],
        "imageHash": ["abc", "def"],
        "secureLevel": "2"
    }
}
TID = "transaction130234"


@pytest.fixture
def create_header():
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    print("accessToken:" + token_result["accessToken"])
    yield {
        "header": {
            "pdsUserId": PDS_USER["pdsUserId"],
            "Content-Type": "application/json",
            "timeStamp": "2022/08/23 15:12:01.690",
            "accessToken": token_result["accessToken"],
            "Authorization": "Bearer " + token_result["jwt"]
        }
    }


# 01.事前処理
# No1.事前処理が失敗する
def test_delete_case1(create_header):
    header = create_header["header"]
    tid = DATA["tid"]
    response = client.delete("/api/2.0/delete-profile2/transaction?tid=" + tid, headers=header)
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


# No2.事前処理が成功する
def test_delete_case2(create_header):
    DATA["tid"] = TID + "01"
    header = create_header["header"]
    response = client.post("/api/2.0/delete-profile/transaction", headers=header, data=json.dumps(DATA))
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    tid = DATA["tid"]
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    tid = DATA["tid"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 02.個人情報削除処理
# No3.個人情報削除処理が失敗する
def test_delete_case3(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "USER_PROFILE_DELETE_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    tid = DATA["tid"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
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


# No4.個人情報削除処理が成功する
def test_delete_case4(create_header):
    DATA["tid"] = TID + "101"
    header = create_header["header"]
    response = client.post("/api/2.0/delete-profile/transaction", headers=header, data=json.dumps(DATA))
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    tid = DATA["tid"]
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    tid = DATA["tid"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 03.個人情報削除バッチキュー発行処理
# No5.個人情報削除バッチキュー発行処理が失敗する
def test_delete_case5(mocker: MockerFixture, create_header):
    DATA["tid"] = TID + "02"
    header = create_header["header"]
    response = client.post("/api/2.0/delete-profile/transaction", headers=header, data=json.dumps(DATA))
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    tid = DATA["tid"]
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    tid = DATA["tid"]
    # Exception
    mocker.patch("util.commonUtil.CommonUtilClass.transaction_delete_batch_queue_issue").side_effect = Exception('testException')
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
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


# No6.個人情報削除バッチキュー発行処理が成功する
def test_delete_case6(create_header):
    DATA["tid"] = TID + "03"
    header = create_header["header"]
    response = client.post("/api/2.0/delete-profile/transaction", headers=header, data=json.dumps(DATA))
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    tid = DATA["tid"]
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    tid = DATA["tid"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 06.アクセストークン発行処理
# No7.アクセストークン発行処理が失敗する
def test_delete_case7(mocker: MockerFixture, create_header):
    DATA["tid"] = TID + "104"
    header = create_header["header"]
    response = client.post("/api/2.0/delete-profile/transaction", headers=header, data=json.dumps(DATA))
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    tid = DATA["tid"]
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    tid = DATA["tid"]
    # Exception
    mocker.patch.object(SqlConstClass, "ACCESS_TOKEN_PUBLIC_PDS_USER_TOKEN_ISSUANCE_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
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


# No8.アクセストークン発行処理が成功する
def test_delete_case8(create_header):
    DATA["tid"] = TID + "05"
    header = create_header["header"]
    response = client.post("/api/2.0/delete-profile/transaction", headers=header, data=json.dumps(DATA))
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    tid = DATA["tid"]
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    tid = DATA["tid"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 07.共通エラーチェック処理
# No9.共通エラーチェック処理が成功する
def test_delete_case9(mocker: MockerFixture, create_header):
    DATA["tid"] = TID + "06"
    header = create_header["header"]
    response = client.post("/api/2.0/delete-profile/transaction", headers=header, data=json.dumps(DATA))
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    tid = DATA["tid"]
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    tid = DATA["tid"]
    # Exception
    mocker.patch.object(SqlConstClass, "ACCESS_TOKEN_PUBLIC_PDS_USER_TOKEN_ISSUANCE_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
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


# 04.API実行履歴登録処理
# No10.API実行履歴登録処理が失敗する
def test_delete_case10(mocker: MockerFixture, create_header):
    DATA["tid"] = TID + "07"
    header = create_header["header"]
    response = client.post("/api/2.0/delete-profile/transaction", headers=header, data=json.dumps(DATA))
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    tid = DATA["tid"]
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    tid = DATA["tid"]
    # Exception
    mocker.patch("util.commonUtil.CommonUtilClass.insert_api_history").side_effect = Exception('testException')
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
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


# No11.API実行履歴登録処理が成功する
def test_delete_case11(create_header):
    DATA["tid"] = TID + "08"
    header = create_header["header"]
    response = client.post("/api/2.0/delete-profile/transaction", headers=header, data=json.dumps(DATA))
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    tid = DATA["tid"]
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    tid = DATA["tid"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 08.終了処理
# No12.返却パラメータを作成し返却する
def test_delete_case12(create_header):
    DATA["tid"] = TID + "09"
    header = create_header["header"]
    response = client.post("/api/2.0/delete-profile/transaction", headers=header, data=json.dumps(DATA))
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    tid = DATA["tid"]
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    tid = DATA["tid"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 事前処理
# 01.PDSユーザドメイン検証処理
# No13.PDSユーザドメイン検証処理が失敗する
def test_delete_case13(create_header):
    header = create_header["header"]
    tid = DATA["tid"]
    response = client.delete("/api/2.0/delete-profile2/transaction?tid=" + tid, headers=header)
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


# No14.PDSユーザドメイン検証処理が成功する
def test_delete_case14(create_header):
    DATA["tid"] = TID + "10"
    header = create_header["header"]
    response = client.post("/api/2.0/delete-profile/transaction", headers=header, data=json.dumps(DATA))
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    tid = DATA["tid"]
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    tid = DATA["tid"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 02.共通エラーチェック処理
# No15.共通エラーチェック処理が成功する (エラー情報有り)
def test_delete_case15(create_header):
    header = create_header["header"]
    tid = DATA["tid"]
    response = client.delete("/api/2.0/delete-profile2/transaction?tid=" + tid, headers=header)
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


# 03.アクセストークン検証処理
# No16.アクセストークン検証処理が失敗する
def test_delete_case16(mocker: MockerFixture, create_header):
    header = create_header["header"]
    tid = DATA["tid"]
    # Exception
    mocker.patch.object(SqlConstClass, "ACCESS_TOKEN_PUBLIC_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
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


# No17.アクセストークン検証処理が成功する
def test_delete_case17(create_header):
    DATA["tid"] = TID + "11"
    header = create_header["header"]
    response = client.post("/api/2.0/delete-profile/transaction", headers=header, data=json.dumps(DATA))
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    tid = DATA["tid"]
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    tid = DATA["tid"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 04.共通エラーチェック処理
# No18.共通エラーチェック処理が成功する
def test_delete_case18(mocker: MockerFixture, create_header):
    header = create_header["header"]
    tid = DATA["tid"]
    # Exception
    mocker.patch.object(SqlConstClass, "ACCESS_TOKEN_PUBLIC_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
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


# 03.パラメータ検証処理
# No19.パラメータ検証処理が失敗する
def test_delete_case19(mocker: MockerFixture, create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["pdsUserId"] = None
    response = deleteRouter.input_check(
        trace_logger,
        "delete-profile",
        DATA["tid"],
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


# No20.パラメータ検証処理が成功する
def test_delete_case20(create_header):
    DATA["tid"] = TID + "12"
    header = create_header["header"]
    response = client.post("/api/2.0/delete-profile/transaction", headers=header, data=json.dumps(DATA))
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    tid = DATA["tid"]
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    tid = DATA["tid"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 06.共通エラーチェック処理
# No21.共通エラーチェック処理が成功する
def test_delete_case21(mocker: MockerFixture, create_header):
    header = create_header["header"]
    tid = DATA["tid"]
    # 返却値の変更
    mocker.patch("routers.public.deleteRouter.input_check").return_value = {
        "result": False,
        "errorInfo": [
            {
                "errorCode": "020001",
                "message": logUtil.message_build(MessageConstClass.ERRORS["010002"]["message"])
            }
        ]
    }
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
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


# No22.返却パラメータを作成し返却する
def test_delete_case22(mocker: MockerFixture, create_header):
    DATA["tid"] = TID + "113"
    header = create_header["header"]
    response = client.post("/api/2.0/delete-profile/transaction", headers=header, data=json.dumps(DATA))
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    tid = DATA["tid"]
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    tid = DATA["tid"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# パラメータ検証処理
# 01.パラメータ検証処理
# No23.
# No23_1.PDSユーザドメイン名 文字列型以外、21文字
# パスパラメータはURLで絶対に文字列になるので型チェックできない
def test_delete_case23_1(create_header):
    # PDSユーザドメイン名に誤りがある場合には、PDSユーザドメイン検証でエラーになってしまうので入力チェックまで到達できないことを確認
    header = create_header["header"]
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    tid = DATA["tid"]
    response = client.delete("/api/2.0/[012345678901, 23456]/transaction?tid=" + tid, headers=header)
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
    response = deleteRouter.input_check(
        trace_logger,
        [123456789012, 23456],
        DATA["tid"],
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


# No23_2.PDSユーザドメイン名 文字列型、4文字、全角を含む
def test_delete_case23_2(create_header):
    header = create_header["header"]
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    tid = DATA["tid"]
    response = client.delete("/api/2.0/あ123/transaction?tid=" + tid, headers=header)
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
    response = deleteRouter.input_check(
        trace_logger,
        "あ123",
        DATA["tid"],
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


# No23_3.PDSユーザドメイン名 文字列型、5文字、URL可能文字以外を含む
def test_delete_case23_3(create_header):
    header = create_header["header"]
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    tid = DATA["tid"]
    response = client.delete("/api/2.0/%1234/transaction?tid=" + tid, headers=header)
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
    response = deleteRouter.input_check(
        trace_logger,
        "%1234",
        DATA["tid"],
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
                "errorCode": "020003",
                "message": response["errorInfo"][0]["message"]
            }
        ]
    }
    print(response)


# No23_4.PDSユーザドメイン名 文字列型、5文字、入力規則違反していない（URL利用可能文字のみの半角小英数記号５桁）
def test_delete_case23_4(create_header):
    DATA["tid"] = TID + "14"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_public(pdsUserId="C8000000", pdsUserName="PDSユーザドメイン検証成功テスト", accessToken=None)
    header = create_header["header"]
    header["pdsUserId"] = "C8000000"
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    response = client.post("/api/2.0/c0123/transaction", headers=header, data=json.dumps(DATA))
    token_result = token_util.create_token_public(pdsUserId="C8000000", pdsUserName="PDSユーザドメイン検証成功テスト", accessToken=None)
    tid = DATA["tid"]
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    tid = DATA["tid"]
    response = client.delete("/api/2.0/c0123/transaction?tid=" + tid, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No23_5.PDSユーザドメイン名 文字列型、20文字、入力規則違反していない（URL利用可能文字のみの半角小英数記号20桁）
def test_delete_case23_5(create_header):
    DATA["tid"] = TID + "15"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_public(pdsUserId="C8000001", pdsUserName="PDSユーザドメイン検証成功テスト", accessToken=None)
    header = create_header["header"]
    header["pdsUserId"] = "C8000001"
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    response = client.post("/api/2.0/c0123456789012345678/transaction", headers=header, data=json.dumps(DATA))
    token_result = token_util.create_token_public(pdsUserId="C8000001", pdsUserName="PDSユーザドメイン検証成功テスト", accessToken=None)
    tid = DATA["tid"]
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    tid = DATA["tid"]
    response = client.delete("/api/2.0/c0123456789012345678/transaction?tid=" + tid, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No23-6.トランザクションID 値が設定されていない（空値)
def test_delete_case23_6(create_header):
    DATA["tid"] = ""
    header = create_header["header"]
    response = client.post("/api/2.0/delete-profile/transaction", headers=header, data=json.dumps(DATA))
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    tid = DATA["tid"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
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


# No23_7.トランザクションID 文字列型以外、37桁
def test_delete_case23_7(create_header):
    # 入力チェックを直接呼び出してエラーになることを確認
    DATA["tid"] = 1234567890123456789012345678901234567
    header = create_header["header"]
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    response = deleteRouter.input_check(
        trace_logger,
        "delete-profile",
        DATA["tid"],
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


# No23_8.トランザクションID 文字列型、37桁、入力可能文字以外が含まれる(全角)
def test_delete_case23_8(create_header):
    # URLのクエリパラメータは文字列以外を許容しないので、
    # 入力チェックを直接呼び出してエラーになることを確認
    DATA["tid"] = "１234567890123456789012345678901234567"
    header = create_header["header"]
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    response = deleteRouter.input_check(
        trace_logger,
        "delete-profile",
        DATA["tid"],
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
                "errorCode": "020002",
                "message": response["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020020",
                "message": response["errorInfo"][1]["message"]
            }
        ]
    }
    print(response)


# No23_9.トランザクションID 文字列型、36桁、入力可能文字のみ（半角英数字） [a-zA-Z0-9]
def test_delete_case23_9(create_header):
    DATA["tid"] = "transaction2345678901234567890123457"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    header = create_header["header"]
    response = client.post("/api/2.0/delete-profile/transaction", headers=header, data=json.dumps(DATA))
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    tid = DATA["tid"]
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No23_10.PDSユーザID 値が設定されていない（空値）
def test_delete_case23_10(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["pdsUserId"] = None
    response = deleteRouter.input_check(
        trace_logger,
        "delete-profile",
        DATA["tid"],
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


# No23_11.PDSユーザID 文字列型以外、7桁、C以外の文字で始まる
def test_delete_case23_11(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["pdsUserId"] = '1234567'
    response = deleteRouter.input_check(
        trace_logger,
        "delete-profile",
        DATA["tid"],
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


# No23-12.PDSユーザID 文字列型、8桁、入力規則違反していない（C＋数値7桁）
def test_delete_case23_12(create_header):
    DATA["tid"] = TID + "16"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    header = create_header["header"]
    header["pdsUserId"] = 'C0000015'
    response = client.post("/api/2.0/delete-profile/transaction", headers=header, data=json.dumps(DATA))
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    tid = DATA["tid"]
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No23-13.タイムスタンプ 値が設定されていない（空値）
def test_delete_case23_13(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["timeStamp"] = None
    tid = DATA["tid"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
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


# No23-14.タイムスタンプ 文字列型以外、22桁
def test_delete_case23_14(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["timeStamp"] = '1234567890123456789012'
    tid = DATA["tid"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
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
    response = deleteRouter.input_check(
        trace_logger,
        "delete-profile",
        tid,
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


# No23-15.タイムスタンプ 文字列型、24桁、入力規則違反している　hh:mmがhhh:mm
def test_delete_case23_15(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["timeStamp"] = '2022/09/30 12:000:00.000'
    tid = DATA["tid"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
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


# No23-16.アクセストークン 値が設定されていない（空値）
def test_delete_case23_16(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["accessToken"] = None
    tid = DATA["tid"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
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
    response = deleteRouter.input_check(
        trace_logger,
        "pds-user-create",
        tid,
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


# No23-17.アクセストークン 文字列型以外、201桁
def test_delete_case23_17(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["accessToken"] = "123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901"
    tid = DATA["tid"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
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
    response = deleteRouter.input_check(
        trace_logger,
        "pds-user-create",
        tid,
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


# No23-18.アクセストークン 文字列型、199桁、入力可能文字以外が含まれる（全角）
def test_delete_case23_18(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["accessToken"] = "あ123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678"
    tid = DATA["tid"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
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
    response = deleteRouter.input_check(
        trace_logger,
        "pds-user-create",
        tid,
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


# No23-19.アクセストークン 文字列型、200桁、入力可能文字のみ（半角英数字） [a-fA-F0-9]
def test_delete_case23_19(create_header):
    DATA["tid"] = TID + "18"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    header = create_header["header"]
    response = client.post("/api/2.0/delete-profile/transaction", headers=header, data=json.dumps(DATA))
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    tid = DATA["tid"]
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }


# No23-20.「引数．ヘッダパラメータ．PDSユーザID」と「引数．PDSユーザドメイン情報．PDSユーザID」の値が一致しない場合、「変数．エラー情報リスト」にエラー情報を追加する
def test_delete_case23_20(mocker: MockerFixture, create_header):
    # 返却値の変更
    mocker.patch("util.commonUtil.CommonUtilClass.check_pds_user_domain").return_value = {"result": True, "pdsUserInfo": {"pdsUserId": "C1234567"}}
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["pdsUserId"] = 'C0000015'
    tid = DATA["tid"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
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


# 02.終了処理
# No24.変数．エラー情報がない
def test_delete_case24(mocker: MockerFixture, create_header):
    DATA["tid"] = TID + "19"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    header = create_header["header"]
    response = client.post("/api/2.0/delete-profile/transaction", headers=header, data=json.dumps(DATA))
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    tid = DATA["tid"]
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No25.変数．エラー情報がある
def test_delete_case25(mocker: MockerFixture, create_header):
    # 返却値の変更
    mocker.patch("util.commonUtil.CommonUtilClass.check_pds_user_domain").return_value = {"result": True, "pdsUserInfo": {"pdsUserId": "C1234567"}}
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["pdsUserId"] = 'C0000015'
    tid = DATA["tid"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
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


# 個人情報削除処理
# 01.PDSユーザDB接続準備処理
# No26.接続に失敗する
def test_delete_case26(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SystemConstClass, "PDS_USER_DB_NAME", "pds_user_db2")
    tid = DATA["tid"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
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


# No27.接続に成功する
def test_delete_case27(create_header):
    DATA["tid"] = TID + "19"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    header = create_header["header"]
    response = client.post("/api/2.0/delete-profile/transaction", headers=header, data=json.dumps(DATA))
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    tid = DATA["tid"]
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 02.個人情報取得処理
# No28.個人情報取得処理に失敗する
def test_delete_case28(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "USER_PROFILE_DELETE_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    tid = DATA["tid"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
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


# No29.個人情報取得処理に成功する
def test_delete_case29(create_header):
    DATA["tid"] = TID + "20"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    header = create_header["header"]
    response = client.post("/api/2.0/delete-profile/transaction", headers=header, data=json.dumps(DATA))
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    tid = DATA["tid"]
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 03.共通エラーチェック処理
# No30.共通エラーチェック処理が成功する (エラー情報有り)
def test_delete_case30(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "USER_PROFILE_DELETE_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    tid = DATA["tid"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
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


# 04.個人情報バイナリデータ取得処理
# No31.個人情報バイナリデータ取得処理に失敗する
def test_delete_case31(mocker: MockerFixture, create_header):
    DATA["tid"] = TID + "21"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    header = create_header["header"]
    response = client.post("/api/2.0/delete-profile/transaction", headers=header, data=json.dumps(DATA))
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    tid = DATA["tid"]
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "USER_PROFILE_DELETE_BINARY_DATA_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
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


# No32.個人情報バイナリデータ取得処理に成功する
def test_delete_case32(create_header):
    DATA["tid"] = TID + "25"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    header = create_header["header"]
    response = client.post("/api/2.0/delete-profile/transaction", headers=header, data=json.dumps(DATA))
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    tid = DATA["tid"]
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 05.共通エラーチェック処理
# No33.共通エラーチェック処理が成功（エラー情報有り）
def test_delete_case33(mocker: MockerFixture, create_header):
    DATA["tid"] = TID + "26"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    header = create_header["header"]
    response = client.post("/api/2.0/delete-profile/transaction", headers=header, data=json.dumps(DATA))
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    tid = DATA["tid"]
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "USER_PROFILE_DELETE_BINARY_DATA_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
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


# 07.個人情報バイナリデータ論理削除処理
# No34.個人情報バイナリデータ論理削除処理に失敗する
def test_delete_case34(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["tid"] = TID + "27"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    header = create_header["header"]
    response = client.post("/api/2.0/delete-profile/transaction", headers=header, data=json.dumps(DATA))
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    tid = DATA["tid"]
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    mocker.patch.object(SqlConstClass, "USER_PROFILE_DELETE_BINARY_DATA_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    tid = DATA["tid"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
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


# No35.個人情報バイナリデータ論理削除処理に成功する
def test_delete_case35(create_header):
    DATA["tid"] = TID + "28"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    header = create_header["header"]
    response = client.post("/api/2.0/delete-profile/transaction", headers=header, data=json.dumps(DATA))
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    tid = DATA["tid"]
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 08.個人情報論理削除処理
# No36.個人情報論理削除処理に失敗する
def test_delete_case36(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["tid"] = TID + "29"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    header = create_header["header"]
    response = client.post("/api/2.0/delete-profile/transaction", headers=header, data=json.dumps(DATA))
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    tid = DATA["tid"]
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    mocker.patch.object(SqlConstClass, "USER_PROFILE_DELETE_DATA_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    tid = DATA["tid"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
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


# No37.個人情報論理削除処理に成功する
def test_delete_case37(create_header):
    DATA["tid"] = TID + "130"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    header = create_header["header"]
    response = client.post("/api/2.0/delete-profile/transaction", headers=header, data=json.dumps(DATA))
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    tid = DATA["tid"]
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 09.トランザクションコミット処理
# No38.個人情報論理削除処理に成功する
def test_delete_case38(create_header):
    DATA["tid"] = TID + "31"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    header = create_header["header"]
    response = client.post("/api/2.0/delete-profile/transaction", headers=header, data=json.dumps(DATA))
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    tid = DATA["tid"]
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 10.終了処理
# No39.個人情報論理削除処理に成功する
def test_delete_case39(mocker: MockerFixture, create_header):
    DATA["tid"] = TID + "32"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    header = create_header["header"]
    response = client.post("/api/2.0/delete-profile/transaction", headers=header, data=json.dumps(DATA))
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    tid = DATA["tid"]
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 個人情報バイナリデータ論理削除処理
# 01.個人情報バイナリデータ更新処理
# No40.個人情報バイナリデータ更新処理に失敗する
def test_delete_case40(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["tid"] = TID + "33"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    header = create_header["header"]
    response = client.post("/api/2.0/delete-profile/transaction", headers=header, data=json.dumps(DATA))
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    tid = DATA["tid"]
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    mocker.patch.object(SqlConstClass, "USER_PROFILE_DELETE_BINARY_DATA_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    tid = DATA["tid"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
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


# No41.個人情報バイナリデータ更新処理に成功する
def test_delete_case41(create_header):
    DATA["tid"] = TID + "34"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    header = create_header["header"]
    response = client.post("/api/2.0/delete-profile/transaction", headers=header, data=json.dumps(DATA))
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    tid = DATA["tid"]
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 02.共通エラーチェック処理
# No42.共通エラーチェック処理が成功する (エラー情報有り)
def test_delete_case42(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["tid"] = TID + "35"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    header = create_header["header"]
    response = client.post("/api/2.0/delete-profile/transaction", headers=header, data=json.dumps(DATA))
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    tid = DATA["tid"]
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    mocker.patch.object(SqlConstClass, "USER_PROFILE_DELETE_BINARY_DATA_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    tid = DATA["tid"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
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


# 03.終了処理
# No43.正常系
def test_delete_case43(create_header):
    DATA["tid"] = TID + "136"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    header = create_header["header"]
    response = client.post("/api/2.0/delete-profile/transaction", headers=header, data=json.dumps(DATA))
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    tid = DATA["tid"]
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 個人情報論理削除処理
# 01.個人情報更新処理
# N044.個人情報更新処理に失敗する
def test_delete_case44(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["tid"] = TID + "37"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    header = create_header["header"]
    response = client.post("/api/2.0/delete-profile/transaction", headers=header, data=json.dumps(DATA))
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    tid = DATA["tid"]
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    mocker.patch.object(SqlConstClass, "USER_PROFILE_DELETE_DATA_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    tid = DATA["tid"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
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


# No45.個人情報更新処理に成功する
def test_delete_case45(mocker: MockerFixture, create_header):
    DATA["tid"] = TID + "38"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    header = create_header["header"]
    response = client.post("/api/2.0/delete-profile/transaction", headers=header, data=json.dumps(DATA))
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    tid = DATA["tid"]
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 02.共通エラーチェック処理
# No46.共通エラーチェック処理が成功する (エラー情報有り)
def test_delete_case46(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["tid"] = TID + "39"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    header = create_header["header"]
    response = client.post("/api/2.0/delete-profile/transaction", headers=header, data=json.dumps(DATA))
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    tid = DATA["tid"]
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    mocker.patch.object(SqlConstClass, "USER_PROFILE_DELETE_DATA_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    tid = DATA["tid"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
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


# 03.終了処理
# No47.正常系
def test_delete_case47(create_header):
    DATA["tid"] = TID + "40"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    header = create_header["header"]
    response = client.post("/api/2.0/delete-profile/transaction", headers=header, data=json.dumps(DATA))
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    tid = DATA["tid"]
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 01.ロールバック処理
# No48.ロールバック処理が失敗する
def test_delete_case48(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["tid"] = TID + "41"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    header = create_header["header"]
    response = client.post("/api/2.0/delete-profile/transaction", headers=header, data=json.dumps(DATA))
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    tid = DATA["tid"]
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    mocker.patch.object(SqlConstClass, "USER_PROFILE_DELETE_DATA_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    mocker.patch.object(PostgresDbUtilClass, "rollback_transaction", side_effect=Exception('testException'))
    tid = DATA["tid"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
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


# No49.ロールバック処理が成功する
def test_delete_case49(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["tid"] = TID + "42"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    header = create_header["header"]
    response = client.post("/api/2.0/delete-profile/transaction", headers=header, data=json.dumps(DATA))
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    tid = DATA["tid"]
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    mocker.patch.object(SqlConstClass, "USER_PROFILE_DELETE_DATA_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    tid = DATA["tid"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
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


# 02.共通エラーチェック処理
# No50.共通エラーチェック処理が成功 (エラー情報有り)
def test_delete_case50(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["tid"] = TID + "45"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    header = create_header["header"]
    response = client.post("/api/2.0/delete-profile/transaction", headers=header, data=json.dumps(DATA))
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    tid = DATA["tid"]
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    mocker.patch.object(SqlConstClass, "USER_PROFILE_DELETE_DATA_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    mocker.patch.object(PostgresDbUtilClass, "rollback_transaction", side_effect=Exception('testException'))
    tid = DATA["tid"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
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


# 03.終了処理
# No51.変数．エラー情報がない
def test_delete_case51(mocker: MockerFixture, create_header):
    header = create_header["header"]
    DATA["tid"] = TID + "46"
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    header = create_header["header"]
    response = client.post("/api/2.0/delete-profile/transaction", headers=header, data=json.dumps(DATA))
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    tid = DATA["tid"]
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    mocker.patch.object(SqlConstClass, "USER_PROFILE_DELETE_DATA_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    tid = DATA["tid"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
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
