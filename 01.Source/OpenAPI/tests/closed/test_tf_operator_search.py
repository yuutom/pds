from fastapi.testclient import TestClient
from app import app
from fastapi import Request
import pytest
from pytest_mock.plugin import MockerFixture
from util.tokenUtil import TokenUtilClass
import util.logUtil as logUtil
from const.systemConst import SystemConstClass
import routers.closed.tfOperatorSearchRouter as tfOperatorSearchRouter

client = TestClient(app)

# 処理名
EXEC_NAME: str = "tfOperatorSearch"


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


# 01.アクセストークン検証処理
# 異常系
# No1.アクセストークン検証処理が失敗する
def test_tf_operator_search_case1(create_header):
    header = create_header["header"]
    header["accessToken"] = "518302174323385ee79afc2e37e3783f15e48e43d75f004a83e41667996087770c5e474023c0d6969529b49a8fd553ca454e54adbf473ac1a129fd4b0314abc4d4f33e4349749110f5b1774db69d5f87944e3a86c7d3ee10390a825f8bf35f1813774c94"
    response = client.post("/api/2.0/tfoperator/search", headers=header)
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "010004",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No2.アクセストークン検証処理が成功する
def test_tf_operator_search_case2(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/tfoperator/search", headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tfOperatorInfo": response.json()["tfOperatorInfo"]
    }
    print(response.json())


# 02.共通エラーチェック処理
# No3.共通エラーチェック処理が成功 (エラー情報有り)
def test_tf_operator_search_case3(create_header):
    header = create_header["header"]
    header["accessToken"] = "518302174323385ee79afc2e37e3783f15e48e43d75f004a83e41667996087770c5e474023c0d6969529b49a8fd553ca454e54adbf473ac1a129fd4b0314abc4d4f33e4349749110f5b1774db69d5f87944e3a86c7d3ee10390a825f8bf35f1813774c94"
    response = client.post("/api/2.0/tfoperator/search", headers=header)
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "010004",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# 03.引数検証処理チェック処理
# No4_1.引数．ヘッダパラメータ．タイムスタンプの値が設定されていない (空値)
def test_tf_operator_search_case4_1(create_header):
    header = create_header["header"]
    header["timeStamp"] = None
    response = client.post("/api/2.0/tfoperator/search", headers=header)
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


# No4_2.引数．ヘッダパラメータ．タイムスタンプが文字列型ではない
def test_tf_operator_search_case4_2(create_header):
    header = create_header["header"]
    header["timeStamp"] = 123456789012345678901234
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    response = tfOperatorSearchRouter.input_check(
        trace_logger,
        header["accessToken"],
        header["timeStamp"]
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


# No4_3.引数．ヘッダパラメータ．タイムスタンプが正しい値である
def test_tf_operator_search_case4_3(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/tfoperator/search", headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tfOperatorInfo": response.json()["tfOperatorInfo"]
    }
    print(response.json())


# No4_4.引数．ヘッダパラメータ．アクセストークンの値が設定されていない (空値)
def test_tf_operator_search_case4_4(create_header):
    header = create_header["header"]
    header["accessToken"] = None
    response = client.post("/api/2.0/tfoperator/search", headers=header)
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


# No4_5.引数．ヘッダパラメータ．アクセストークンが文字列型ではない
def test_tf_operator_search_case4_5(create_header):
    header = create_header["header"]
    header["accessToken"] = 111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    response = tfOperatorSearchRouter.input_check(
        trace_logger,
        header["accessToken"],
        header["timeStamp"]
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


# No4_6.引数．ヘッダパラメータ．アクセストークンが正しい値である
def test_tf_operator_search_case4_6(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/tfoperator/search", headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tfOperatorInfo": response.json()["tfOperatorInfo"]
    }
    print(response.json())


# 04.共通エラーチェック処理
# N0.5.共通エラーチェック処理が成功
def test_tf_operator_search_case5(create_header):
    header = create_header["header"]
    header["timeStamp"] = None
    response = client.post("/api/2.0/tfoperator/search", headers=header)
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


# 05.DB接続準備処理
# No.6.接続に失敗する
# 設定値を異常な値に変更する
def test_tf_operator_search_case6(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.commonUtil.CommonUtilClass.get_secret_info").return_value = {"host": "test", "port": "test", "username": "test", "password": "test"}
    header = create_header["header"]
    response = client.post("/api/2.0/tfoperator/search", headers=header)
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


# No.7.接続に成功する
def test_tf_operator_search_case7(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/tfoperator/search", headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tfOperatorInfo": response.json()["tfOperatorInfo"]
    }
    print(response.json())


# 06.TFオペレータ全件検索処理
# No.8.TFオペレータ全件検索処理が失敗する
def test_tf_operator_search_case8(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("const.sqlConst.SqlConstClass.TF_OPERATOR_SELECT_SQL").return_value = """ SELECT * FROM AAAAAA; """
    header = create_header["header"]
    response = client.post("/api/2.0/tfoperator/search", headers=header)
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


# No.9.TFオペレータ全件検索処理が成功する
def test_tf_operator_search_case9(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/tfoperator/search", headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tfOperatorInfo": response.json()["tfOperatorInfo"]
    }
    print(response.json())


# 07.共通エラーチェック処理
# No.10.共通エラーチェック処理が成功
def test_tf_operator_search_case10(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("const.sqlConst.SqlConstClass.TF_OPERATOR_SELECT_SQL").return_value = """ SELECT * FROM AAAAAA; """
    header = create_header["header"]
    response = client.post("/api/2.0/tfoperator/search", headers=header)
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


# 08.TFオペレータ無効化フラグ反転処理
# No.11.TFオペレータ無効化フラグ反転処理が失敗する
def test_tf_operator_search_case11(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/tfoperator/search", headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tfOperatorInfo": response.json()["tfOperatorInfo"]
    }
    print(response.json())


# No.12.TFオペレータ無効化フラグ反転処理が成功する
def test_tf_operator_search_case12(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/tfoperator/search", headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tfOperatorInfo": response.json()["tfOperatorInfo"]
    }
    print(response.json())


# 09.アクセストークン発行処理
# No.13.アクセストークン発行処理に失敗する
def test_tf_operator_search_case13(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_public(
        pdsUserId="C0000001",
        pdsUserName="PDSユーザアクセス記録閲覧テスト",
        accessToken=None
    )
    header = create_header["header"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    header["accessToken"] = token_result["accessToken"]
    response = client.post("/api/2.0/tfoperator/search", headers=header)
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020001",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020001",
                "message": response.json()["errorInfo"][1]["message"]
            }
        ]
    }
    print(response.json())


# No.14.アクセストークン発行処理に成功する
def test_tf_operator_search_case14(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/tfoperator/search", headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tfOperatorInfo": response.json()["tfOperatorInfo"]
    }
    print(response.json())


# 10.共通エラーチェック処理
# No.15.共通エラーチェック処理が成功
def test_tf_operator_search_case15(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_public(
        pdsUserId="C0000001",
        pdsUserName="PDSユーザアクセス記録閲覧テスト",
        accessToken=None
    )
    header = create_header["header"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    header["accessToken"] = token_result["accessToken"]
    response = client.post("/api/2.0/tfoperator/search", headers=header)
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020001",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020001",
                "message": response.json()["errorInfo"][1]["message"]
            }
        ]
    }
    print(response.json())


# 11.終了処理
# No.16.変数．エラー情報がない
def test_tf_operator_search_case16(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/tfoperator/search", headers=header)
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "tfOperatorInfo": response.json()["tfOperatorInfo"]
    }
    print(response.json())
