from fastapi.testclient import TestClient
from typing import Optional, Any
from app import app
from fastapi import Request
# RequestBody
from pydantic import BaseModel
import pytest
from pytest_mock.plugin import MockerFixture
from util.tokenUtil import TokenUtilClass
import util.logUtil as logUtil
import json
from const.sqlConst import SqlConstClass
from const.systemConst import SystemConstClass
from util.postgresDbUtil import PostgresDbUtilClass
import routers.closed.pdsUserAuthInfoDisableRouter as pdsUserAuthInfoDisableRouter
from routers.closed.pdsUserAuthInfoDisableRouter import requestBody as routerRequestBody

client = TestClient(app)

# 処理名
EXEC_NAME: str = "pdsUserAuthInfoDisable"

DATA = {
    "pdsUserId": "C0000011",
    "pdsUserPublicKeyIdx": 100,
    "pdsUserPublicKeyEndDate": "2023/12/31"
}


class requestBody(BaseModel):
    """
    リクエストボディクラス

    Args:
        BaseModel (Object): Pydanticのベースクラス
    """
    pdsUserId: Optional[Any] = None
    pdsUserPublicKeyIdx: Optional[Any] = None
    pdsUserPublicKeyEndDate: Optional[Any] = None


@pytest.fixture
def create_header():
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_closed(
        tfOperatorInfo={
            "tfOperatorId": "t-test4",
            "tfOperatorName": "テスト"
        },
        accessToken=None
    )
    print("accessToken:" + token_result["accessToken"])
    yield {
        "header": {
            "Content-Type": "application/json",
            "accessToken": token_result["accessToken"],
            "timeStamp": "2022/08/23 15:12:01.690",
            "Authorization": "Bearer " + token_result["jwt"]
        }
    }


# メイン処理
# 01.アクセストークン検証処理
# No.1.アクセストークン検証処理が失敗する
def test_pds_user_auth_info_disable_case1(create_header):
    header = create_header["header"]
    header["accessToken"] = "518302174323385ee79afc2e37e3783f15e48e43d75f004a83e41667996087770c5e474023c0d6969529b49a8fd553ca454e54adbf473ac1a129fd4b0314abc4d4f33e4349749110f5b1774db69d5f87944e3a86c7d3ee10390a825f8bf35f1813774c94"
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/disable", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": response.json()["errorInfo"]
    }
    print(response.json())


# No.2.アクセストークン検証処理が成功する
def test_pds_user_auth_info_disable_case2(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/disable", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 02.共通エラーチェック処理
# No.3.共通エラーチェック処理が成功
def test_pds_user_auth_info_disable_case3(create_header):
    header = create_header["header"]
    header["accessToken"] = "518302174323385ee79afc2e37e3783f15e48e43d75f004a83e41667996087770c5e474023c0d6969529b49a8fd553ca454e54adbf473ac1a129fd4b0314abc4d4f33e4349749110f5b1774db69d5f87944e3a86c7d3ee10390a825f8bf35f1813774c94"
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/disable", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": response.json()["errorInfo"]
    }
    print(response.json())


# 03.パラメータ検証処理
# No.4.パラメータ検証処理が失敗する
def test_pds_user_auth_info_disable_case4(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserId"] = ""
    response = client.post("/api/2.0/pdsuser/disable", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": response.json()["errorInfo"]
    }
    print(response.json())


# No.5.パラメータ検証処理が成功する
def test_pds_user_auth_info_disable_case5(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/disable", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 04.共通エラーチェック処理
# No.6.共通エラーチェック処理が成功
def test_pds_user_auth_info_disable_case6(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserId"] = ""
    response = client.post("/api/2.0/pdsuser/disable", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": response.json()["errorInfo"]
    }
    print(response.json())


# 05.DB接続準備処理
# No.7.接続に失敗する 設定値を異常な値に変更する
def test_pds_user_auth_info_disable_case7(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.commonUtil.CommonUtilClass.get_secret_info").return_value = {"host": "test", "port": "test", "username": "test", "password": "test"}
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/disable", headers=header, data=json.dumps(data_copy))
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


# No.8.接続に成功する
def test_pds_user_auth_info_disable_case8(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/disable", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 06.PDSユーザ鍵存在検証処理
# No.9.PDSユーザ鍵存在検証処理が失敗する
def test_pds_user_auth_info_disable_case9(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserId"] = "C1111111"
    response = client.post("/api/2.0/pdsuser/disable", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "030013",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No.10.PDSユーザ鍵存在検証処理が成功する
def test_pds_user_auth_info_disable_case10(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/disable", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 07.共通エラーチェック処理
# No.11.PDSユーザ取得処理が成功する
def test_pds_user_auth_info_disable_case11(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserId"] = "C1111111"
    response = client.post("/api/2.0/pdsuser/disable", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "030013",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# 08.トランザクション作成処理
# No.12.トランザクション作成処理が失敗する


# No.13.トランザクション作成処理が成功する


# 09.PDSユーザ公開鍵更新処理
# No.14.PDSユーザ公開鍵更新処理が失敗する
def test_pds_user_auth_info_disable_case14(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "PDS_USER_UPDATE_SQL_PDS_USER_KEY_CONDITION", """ SELECT * FROM AAAAAA; """)
    mocker.patch.object(SqlConstClass, "PDS_USER_UPDATE_SQL_END_DATE_CONDITION", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/disable", headers=header, data=json.dumps(data_copy))
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


# No.15.PDSユーザ公開鍵更新処理が成功する
def test_pds_user_auth_info_disable_case15(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/disable", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 10.共通エラーチェック処理
# No.16.共通エラーチェック処理が成功
def test_pds_user_auth_info_disable_case16(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "PDS_USER_UPDATE_SQL_PDS_USER_KEY_CONDITION", """ SELECT * FROM AAAAAA; """)
    mocker.patch.object(SqlConstClass, "PDS_USER_UPDATE_SQL_END_DATE_CONDITION", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/disable", headers=header, data=json.dumps(data_copy))
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


# 11.トランザクションコミット処理
# No.17.トランザクションコミット処理が失敗する
def test_pds_user_auth_info_disable_case17(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(PostgresDbUtilClass, "commit_transaction", side_effect=Exception('testException'))
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/disable", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": response.json()["errorInfo"]
    }
    print(response.json())


# No.18.トランザクションコミット処理が成功する
def test_pds_user_auth_info_disable_case18(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/disable", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 12.アクセストークン発行処理
# No.19.アクセストークン発行処理が失敗する
def test_pds_user_auth_info_disable_case19(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "ACCESS_TOKEN_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/disable", headers=header, data=json.dumps(data_copy))
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


# No.20.アクセストークン発行処理が成功する
def test_pds_user_auth_info_disable_case20(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/disable", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 13.共通エラーチェック処理
# No.21.共通エラーチェック処理が成功
def test_pds_user_auth_info_disable_case21(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "ACCESS_TOKEN_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/disable", headers=header, data=json.dumps(data_copy))
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


# 14.終了処理
# No.22.変数．エラー情報がある
def test_pds_user_auth_info_disable_case22(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "ACCESS_TOKEN_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/disable", headers=header, data=json.dumps(data_copy))
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


# No.23.変数．エラー情報がない
def test_pds_user_auth_info_disable_case23(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/disable", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# パラメータ検証処理
# 01.パラメータ検証処理
# No.24.PDSユーザ認証情報無効化API_01.引数検証処理　シート参照
# No.24_1.引数．ヘッダパラメータ．タイムスタンプが空値 ("")
def test_pds_user_auth_info_disable_case24_1(create_header):
    header = create_header["header"]
    header["timeStamp"] = ""
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/disable", headers=header, data=json.dumps(data_copy))
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


# No.24_2.引数．ヘッダパラメータ．タイムスタンプが空値 (None)
def test_pds_user_auth_info_disable_case24_2(create_header):
    header = create_header["header"]
    header["timeStamp"] = None
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/disable", headers=header, data=json.dumps(data_copy))
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


# No.24_3.引数．ヘッダパラメータ．タイムスタンプが24桁で文字列型ではない
def test_pds_user_auth_info_disable_case24_3(create_header):
    header = create_header["header"]
    header["timeStamp"] = 123456789012345678901234
    data_copy = DATA.copy()
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserAuthInfoDisableRouter.input_check(
        trace_logger,
        header["accessToken"],
        header["timeStamp"],
        router_request_body
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


# No.24_4.引数．ヘッダパラメータ．タイムスタンプが23桁で文字列型
def test_pds_user_auth_info_disable_case24_4(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/disable", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No.24_5.引数．ヘッダパラメータ．アクセストークンが空値 ("")
def test_pds_user_auth_info_disable_case24_5(create_header):
    header = create_header["header"]
    header["accessToken"] = ""
    data_copy = DATA.copy()
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserAuthInfoDisableRouter.input_check(
        trace_logger,
        header["accessToken"],
        header["timeStamp"],
        router_request_body
    )
    assert response == {
        "result": False,
        "errorInfo": [
            {
                "errorCode": "020001",
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


# No.24_6.引数．ヘッダパラメータ．アクセストークンが空値 (None)
def test_pds_user_auth_info_disable_case24_6(create_header):
    header = create_header["header"]
    header["accessToken"] = None
    data_copy = DATA.copy()
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserAuthInfoDisableRouter.input_check(
        trace_logger,
        header["accessToken"],
        header["timeStamp"],
        router_request_body
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


# No.24_7.引数．ヘッダパラメータ．アクセストークンが201桁で文字列型ではない
def test_pds_user_auth_info_disable_case24_7(create_header):
    header = create_header["header"]
    header["accessToken"] = 123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901
    data_copy = DATA.copy()
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserAuthInfoDisableRouter.input_check(
        trace_logger,
        header["accessToken"],
        header["timeStamp"],
        router_request_body
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


# No.24_8.引数．ヘッダパラメータ．アクセストークンが200桁で文字列型
def test_pds_user_auth_info_disable_case24_8(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/disable", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No.24_9.引数．リクエストボディ．PDSユーザIDが空値 ("")
def test_pds_user_auth_info_disable_case24_9(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserId"] = ""
    response = client.post("/api/2.0/pdsuser/disable", headers=header, data=json.dumps(data_copy))
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


# No.24_10.引数．リクエストボディ．PDSユーザIDが空値 (None)
def test_pds_user_auth_info_disable_case24_10(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserId"] = None
    response = client.post("/api/2.0/pdsuser/disable", headers=header, data=json.dumps(data_copy))
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


# No.24_11.引数．リクエストボディ．PDSユーザIDが7桁で文字列型ではない
def test_pds_user_auth_info_disable_case24_11(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserId"] = 1234567
    response = client.post("/api/2.0/pdsuser/disable", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
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


# No.24_12.引数．リクエストボディ．PDSユーザIDが8桁で文字列型
def test_pds_user_auth_info_disable_case24_12(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/disable", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No.24_13.引数．リクエストボディ．PDSユーザ公開鍵終了日が空値 ("")
def test_pds_user_auth_info_disable_case24_13(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserPublicKeyEndDate"] = ""
    response = client.post("/api/2.0/pdsuser/disable", headers=header, data=json.dumps(data_copy))
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


# No.24_14.引数．リクエストボディ．PDSユーザ公開鍵終了日が空値 (None)
def test_pds_user_auth_info_disable_case24_14(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserPublicKeyEndDate"] = None
    response = client.post("/api/2.0/pdsuser/disable", headers=header, data=json.dumps(data_copy))
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


# No.24_15.引数．リクエストボディ．PDSユーザ公開鍵終了日が11桁で文字列型ではない
def test_pds_user_auth_info_disable_case24_15(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserPublicKeyEndDate"] = 123456789012345678901
    response = client.post("/api/2.0/pdsuser/disable", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
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


# No.24_16.引数．リクエストボディ．PDSユーザ公開鍵終了日が10桁で文字列型
def test_pds_user_auth_info_disable_case24_16(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/disable", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No.24_17.引数．リクエストボディ．PDSユーザ公開鍵インデックスが空値 ("")
def test_pds_user_auth_info_disable_case24_17(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserPublicKeyIdx"] = ""
    response = client.post("/api/2.0/pdsuser/disable", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020001",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020019",
                "message": response.json()["errorInfo"][1]["message"]
            }
        ]
    }
    print(response.json())


# No.24_18.引数．リクエストボディ．PDSユーザ公開鍵インデックスが空値 (None)
def test_pds_user_auth_info_disable_case24_18(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserPublicKeyIdx"] = None
    response = client.post("/api/2.0/pdsuser/disable", headers=header, data=json.dumps(data_copy))
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


# No.24_19.引数．リクエストボディ．PDSユーザ公開鍵インデックスが数値型ではない
def test_pds_user_auth_info_disable_case24_19(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserPublicKeyIdx"] = "100"
    response = client.post("/api/2.0/pdsuser/disable", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
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


# No.24_20.引数．リクエストボディ．PDSユーザ公開鍵インデックスが数値型で入力可能文字以外を含む


# No.24_21.引数．リクエストボディ．PDSユーザ公開鍵インデックスが数値型で入力可能文字以外を含まない
def test_pds_user_auth_info_disable_case24_21(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/disable", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 02.終了処理
# No.25.変数．エラー情報がない
def test_pds_user_auth_info_disable_case25(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/disable", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No.26.変数．エラー情報がある
def test_pds_user_auth_info_disable_case26(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserPublicKeyEndDate"] = ""
    response = client.post("/api/2.0/pdsuser/disable", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": response.json()["errorInfo"]
    }
    print(response.json())


# ロールバック処理
# 01.ロールバック処理
# No.27.PDSユーザ認証無効化トランザクションのロールバック処理が失敗する
def test_pds_user_auth_info_disable_case27(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    # Exception
    mocker.patch.object(SqlConstClass, "PDS_USER_UPDATE_SQL_END_DATE_CONDITION", """ SELECT * FROM AAAAAA; """)
    mocker.patch.object(PostgresDbUtilClass, "rollback_transaction", return_value={"result": False, "errorObject": Exception("test-exception"), "stackTrace": "test-exception"})
    response = client.post("/api/2.0/pdsuser/disable", headers=header, data=json.dumps(data_copy))
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


# No.28.PDSユーザ認証無効化トランザクションのロールバック処理が成功する
def test_pds_user_auth_info_disable_case28(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    # Exception
    mocker.patch.object(SqlConstClass, "PDS_USER_UPDATE_SQL_END_DATE_CONDITION", """ SELECT * FROM AAAAAA; """)
    response = client.post("/api/2.0/pdsuser/disable", headers=header, data=json.dumps(data_copy))
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
# No.29.共通エラーチェック処理が成功
def test_pds_user_auth_info_disable_case29(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    # Exception
    mocker.patch.object(SqlConstClass, "PDS_USER_UPDATE_SQL_END_DATE_CONDITION", """ SELECT * FROM AAAAAA; """)
    mocker.patch.object(PostgresDbUtilClass, "rollback_transaction", return_value={"result": False, "errorObject": Exception("test-exception"), "stackTrace": "test-exception"})
    response = client.post("/api/2.0/pdsuser/disable", headers=header, data=json.dumps(data_copy))
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
# No.30.変数．エラー情報がない
def test_pds_user_auth_info_disable_case30(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    # Exception
    mocker.patch.object(SqlConstClass, "PDS_USER_UPDATE_SQL_END_DATE_CONDITION", """ SELECT * FROM AAAAAA; """)
    response = client.post("/api/2.0/pdsuser/disable", headers=header, data=json.dumps(data_copy))
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
