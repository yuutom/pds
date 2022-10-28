from const.sqlConst import SqlConstClass
from fastapi.testclient import TestClient
from app import app
from fastapi import Request
import pytest
from pytest_mock.plugin import MockerFixture
from util.tokenUtil import TokenUtilClass
import util.logUtil as logUtil
import json
from const.systemConst import SystemConstClass
from util.postgresDbUtil import PostgresDbUtilClass
import routers.closed.tfOperatorDisableRouter as tfOperatorDisableRouter
from routers.closed.tfOperatorDisableRouter import requestBody as routerRequestBody

client = TestClient(app)

# 処理名
EXEC_NAME: str = "tfOperatorDisable"

DATA = {
    "tfOperatorId": "t-test3"
}


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
# No.01.アクセストークン検証処理が失敗する
def test_tf_operator_disable_case1(create_header):
    header = create_header["header"]
    header["accessToken"] = "518302174323385ee79afc2e37e3783f15e48e43d75f004a83e41667996087770c5e474023c0d6969529b49a8fd553ca454e54adbf473ac1a129fd4b0314abc4d4f33e4349749110f5b1774db69d5f87944e3a86c7d3ee10390a825f8bf35f1813774c94"
    response = client.post("/api/2.0/tfoperator/delete", headers=header, data=json.dumps(DATA))
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


# No.02.アクセストークン検証処理が成功する
def test_tf_operator_disable_case2(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/delete", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 02.共通エラーチェック処理
# No.03.共通エラーチェック処理が成功
def test_tf_operator_disable_case3(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    header["accessToken"] = "518302174323385ee79afc2e37e3783f15e48e43d75f004a83e41667996087770c5e474023c0d6969529b49a8fd553ca454e54adbf473ac1a129fd4b0314abc4d4f33e4349749110f5b1774db69d5f87944e3a86c7d3ee10390a825f8bf35f1813774c94"
    response = client.post("/api/2.0/tfoperator/delete", headers=header, data=json.dumps(data_copy))
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


# 03.パラメータ検証処理
# No.04.パラメータ検証処理が失敗する
def test_tf_operator_disable_case4(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfOperatorId"] = ""
    response = client.post("/api/2.0/tfoperator/delete", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020001",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020016",
                "message": response.json()["errorInfo"][1]["message"]
            }
        ]
    }
    print(response.json())


# No.05.パラメータ検証処理が成功する
def test_tf_operator_disable_case5(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/delete", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 04.共通エラーチェック処理
# No.06.共通エラーチェック処理が成功
def test_tf_operator_disable_case6(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfOperatorId"] = ""
    response = client.post("/api/2.0/tfoperator/delete", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020001",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020016",
                "message": response.json()["errorInfo"][1]["message"]
            }
        ]
    }
    print(response.json())


# 05.DB接続準備処理
# No.07.接続に失敗する
# 設定値を異常な値に変更する
def test_tf_operator_disable_case7(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.commonUtil.CommonUtilClass.get_secret_info").return_value = {"host": "test", "port": "test", "username": "test", "password": "test"}
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/delete", headers=header, data=json.dumps(data_copy))
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


# No.08.接続に成功する
def test_tf_operator_disable_case8(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/delete", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 06.TFオペレータ無効化検証処理
# No.09.TFオペレータ無効化検証処理で取得件数が0件
def test_tf_operator_disable_case9(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfOperatorId"] = "t-test10"
    response = client.post("/api/2.0/tfoperator/delete", headers=header, data=json.dumps(data_copy))
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


# No.10.TFオペレータ無効化検証処理で取得したTFオペレータ無効化フラグがtrue
def test_tf_operator_disable_case10(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfOperatorId"] = "t-test3"
    response = client.post("/api/2.0/tfoperator/delete", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "030009",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No.11.TFオペレータ無効化検証処理が失敗する
def test_tf_operator_disable_case11(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "TF_OPERATOR_INVALID_VERIF_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    response = client.post("/api/2.0/tfoperator/delete", headers=header, data=json.dumps(DATA))
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


# No.12.TFオペレータ無効化検証処理で取得件数が1件
def test_tf_operator_disable_case12(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/delete", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 07.共通エラーチェック処理
# No.13.共通エラーチェック処理が成功（エラー情報有り）
def test_tf_operator_disable_case13(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfOperatorId"] = "t-test10"
    response = client.post("/api/2.0/tfoperator/delete", headers=header, data=json.dumps(data_copy))
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


# 08.トランザクション作成処理
# No.14.トランザクション作成処理が失敗する


# No.15.トランザクション作成処理が成功する


# 09.TFオペレータ無効化フラグ更新処理
# No.16.TFオペレータ無効化フラグ更新処理が失敗する
def test_tf_operator_disable_case16(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "TF_OPERATOR_INVALID_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    response = client.post("/api/2.0/tfoperator/delete", headers=header, data=json.dumps(DATA))
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


# No.17.TFオペレータ無効化フラグ更新処理が成功する
def test_tf_operator_disable_case17(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/delete", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 10.共通エラーチェック処理
# No.18.共通エラーチェック処理が成功（エラー情報有り）
def test_tf_operator_disable_case18(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "TF_OPERATOR_INVALID_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    response = client.post("/api/2.0/tfoperator/delete", headers=header, data=json.dumps(DATA))
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
# No.19.トランザクションコミット処理が失敗する
def test_tf_operator_disable_case19(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(PostgresDbUtilClass, "commit_transaction", side_effect=Exception('testException'))
    header = create_header["header"]
    response = client.post("/api/2.0/tfoperator/delete", headers=header, data=json.dumps(DATA))
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


# No.20.トランザクションコミット処理が成功する
def test_tf_operator_disable_case20(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/delete", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 12.アクセストークン発行処理
# No.21.アクセストークン発行処理に失敗する
def test_tf_operator_disable_case21(create_header):
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
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/delete", headers=header, data=json.dumps(data_copy))
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


# No.22.アクセストークン発行処理に成功する
def test_tf_operator_disable_case22(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/delete", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 13.共通エラーチェック処理
# No.23.共通エラーチェック処理が成功
def test_tf_operator_disable_case23(create_header):
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
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/delete", headers=header, data=json.dumps(data_copy))
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


# 14.終了処理
# No.24.変数．エラー情報がない
def test_tf_operator_disable_case24(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/delete", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# パラメータ検証処理
# 01.パラメータ検証処理
# No.25_1.引数．ヘッダパラメータ．タイムスタンプの値が設定されていない (空値)
def test_tf_operator_disable_case25_1(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    header["timeStamp"] = None
    response = client.post("/api/2.0/tfoperator/delete", headers=header, data=json.dumps(data_copy))
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


# No.25_2.引数．ヘッダパラメータ．タイムスタンプの値が文字列型ではない
def test_tf_operator_disable_case25_2(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    header["timeStamp"] = 111111111111111111111111
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    router_request_body = routerRequestBody(**data_copy)
    response = tfOperatorDisableRouter.inputCheck(
        trace_logger,
        router_request_body,
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


# No.25_3.引数．ヘッダパラメータ．タイムスタンプの値が正常な値
def test_tf_operator_disable_case25_3(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/delete", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No.25_4.引数．ヘッダパラメータ．アクセストークンの値が設定されていない (空値)
def test_tf_operator_disable_case25_4(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    header["accessToken"] = None
    response = client.post("/api/2.0/tfoperator/delete", headers=header, data=json.dumps(data_copy))
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


# No.25_5.引数．ヘッダパラメータ．アクセストークンの値が文字列型ではない
def test_tf_operator_disable_case25_5(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    header["accessToken"] = 111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    router_request_body = routerRequestBody(**data_copy)
    response = tfOperatorDisableRouter.inputCheck(
        trace_logger,
        router_request_body,
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


# No.25_6.引数．ヘッダパラメータ．アクセストークンの値が正常な値
def test_tf_operator_disable_case25_6(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/delete", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No.25_7.引数．リクエストボディ．TFオペレータIDの値が設定されていない (空値)
def test_tf_operator_disable_case25_7(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfOperatorId"] = ""
    response = client.post("/api/2.0/tfoperator/delete", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020001",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020016",
                "message": response.json()["errorInfo"][1]["message"]
            }
        ]
    }
    print(response.json())


# No.25_8.引数．リクエストボディ．TFオペレータIDの値が文字列型ではなく、2桁
def test_tf_operator_disable_case25_8(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfOperatorId"] = 11
    response = client.post("/api/2.0/tfoperator/delete", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020016",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No.25_9.引数．リクエストボディ．TFオペレータIDの値が文字列型ではなく、17桁
def test_tf_operator_disable_case25_9(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfOperatorId"] = 11111111111111111
    response = client.post("/api/2.0/tfoperator/delete", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
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


# No.25_10.引数．リクエストボディ．TFオペレータIDの値が文字列型で3桁
def test_tf_operator_disable_case25_10(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfOperatorId"] = "123"
    response = client.post("/api/2.0/tfoperator/delete", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No.25_11.引数．リクエストボディ．TFオペレータIDの値が文字列型で16桁
def test_tf_operator_disable_case25_11(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfOperatorId"] = "1234567890123456"
    response = client.post("/api/2.0/tfoperator/delete", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No.26.終了処理　変数．エラー情報がある
def test_tf_operator_disable_case26(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfOperatorId"] = 11111111111111111
    response = client.post("/api/2.0/tfoperator/delete", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
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


# ロールバック処理
# 01.ロールバック処理
# No.27.TFオペレータ更新トランザクションのロールバック処理が失敗する
# Exception
def test_tf_operator_disable_case27(mocker: MockerFixture, create_header):
    mocker.patch.object(SqlConstClass, "TF_OPERATOR_INVALID_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    # Exception
    mocker.patch.object(PostgresDbUtilClass, "rollback_transaction", side_effect=Exception('testException'))
    header = create_header["header"]
    response = client.post("/api/2.0/tfoperator/delete", headers=header, data=json.dumps(DATA))
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


# No.28.TFオペレータ更新トランザクションのロールバック処理が成功する
# Exception
def test_tf_operator_disable_case28(mocker: MockerFixture, create_header):
    mocker.patch.object(SqlConstClass, "TF_OPERATOR_INVALID_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    response = client.post("/api/2.0/tfoperator/delete", headers=header, data=json.dumps(DATA))
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
def test_tf_operator_disable_case29(mocker: MockerFixture, create_header):
    mocker.patch.object(SqlConstClass, "TF_OPERATOR_INVALID_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    # Exception
    mocker.patch.object(PostgresDbUtilClass, "rollback_transaction", side_effect=Exception('testException'))
    header = create_header["header"]
    response = client.post("/api/2.0/tfoperator/delete", headers=header, data=json.dumps(DATA))
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
def test_tf_operator_disable_case30(mocker: MockerFixture, create_header):
    mocker.patch.object(SqlConstClass, "TF_OPERATOR_INVALID_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    response = client.post("/api/2.0/tfoperator/delete", headers=header, data=json.dumps(DATA))
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
