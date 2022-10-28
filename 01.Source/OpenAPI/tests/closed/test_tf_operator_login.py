from const.sqlConst import SqlConstClass
from fastapi.testclient import TestClient
from app import app
from fastapi import Request
import pytest
from pytest_mock.plugin import MockerFixture
import json
import util.logUtil as logUtil
## 固定値クラス
from const.messageConst import MessageConstClass
from const.systemConst import SystemConstClass
import routers.closed.tfOperatorLoginRouter as tfOperatorLoginRouter
from routers.closed.tfOperatorLoginRouter import requestBody as routerRequestBody

client = TestClient(app)

# 処理名
EXEC_NAME: str = "tfOperatorLogin"

DATA = {
    "tfOperatorId": "t-test4",
    "tfOperatorPassword": "abcdedABC123"
}


@pytest.fixture
def create_header():
    yield {
        "header": {
            "Content-Type": "application/json",
            "timeStamp": "2022/08/23 15:12:01.690"
        }
    }


# 01.パラメータ検証処理
# 異常系
# No.01.パラメータ検証処理が失敗する
def test_tf_operator_login_case1(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfOperatorId"] = ""
    response = client.post("/api/2.0/tfoperator/login", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "010006",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# 正常系
# No.02.パラメータ検証処理が成功する
def test_tf_operator_login_case2(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/login", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "tfOperatorId": data_copy["tfOperatorId"],
        "tfOperatorName": response.json()["tfOperatorName"],
        "tfOperatorPasswordResetFlg": response.json()["tfOperatorPasswordResetFlg"],
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 02.共通エラーチェック処理
# 正常系
# No.03.共通エラーチェック処理が成功
def test_tf_operator_login_case3(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfOperatorId"] = ""
    response = client.post("/api/2.0/tfoperator/login", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "010006",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# 03.パスワードのハッシュ化処理
# 正常系
# No.04.パスワードのハッシュ化処理が成功した場合
def test_tf_operator_login_case4(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/login", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "tfOperatorId": data_copy["tfOperatorId"],
        "tfOperatorName": response.json()["tfOperatorName"],
        "tfOperatorPasswordResetFlg": response.json()["tfOperatorPasswordResetFlg"],
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 04.DB接続準備処理
# 異常系
# No.05.接続に失敗する　設定値を異常な値に変更する
def test_tf_operator_login_case5(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.commonUtil.CommonUtilClass.get_secret_info").return_value = {"host": "test", "port": "test", "username": "test", "password": "test"}
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/login", headers=header, data=json.dumps(data_copy))
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


# 正常系
# No.06.接続に成功する
def test_tf_operator_login_case6(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/login", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "tfOperatorId": data_copy["tfOperatorId"],
        "tfOperatorName": response.json()["tfOperatorName"],
        "tfOperatorPasswordResetFlg": response.json()["tfOperatorPasswordResetFlg"],
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 05.TFオペレータ取得処理
# 異常系
# No.07.TFオペレータ取得処理の取得件数が0件
def test_tf_operator_login_case7(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfOperatorId"] = "t-test100"
    response = client.post("/api/2.0/tfoperator/login", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "010006",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# 異常系
# No.08.TFオペレータ取得処理が失敗する
def test_tf_operator_login_case8(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "TF_OPERATOR_LOGIN_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/login", headers=header, data=json.dumps(data_copy))
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


# 正常系
# No.09.TFオペレータ取得処理の取得件数が1件
def test_tf_operator_login_case9(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/login", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "tfOperatorId": data_copy["tfOperatorId"],
        "tfOperatorName": response.json()["tfOperatorName"],
        "tfOperatorPasswordResetFlg": response.json()["tfOperatorPasswordResetFlg"],
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 06.共通エラーチェック処理
# 正常系
# No.10.共通エラーチェック処理が成功する (エラー情報有り)
def test_tf_operator_login_case10(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfOperatorId"] = "t-test100"
    response = client.post("/api/2.0/tfoperator/login", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "010006",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# 07.アクセストークン発行処理
# 異常系
# No.11.アクセストークン発行処理が失敗する
def test_tf_operator_login_case11(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.tokenUtil.TokenUtilClass.create_token_closed").return_value = {
        "result": False,
        "errorInfo": {
            "errorCode": "020004",
            "message": logUtil.message_build(MessageConstClass.ERRORS["020004"]["logMessage"], 'TFオペレータ')
        }
    }
    header = create_header["header"]
    response = client.post("/api/2.0/tfoperator/login", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": response.json()["errorInfo"][0]["errorCode"],
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# 正常系
# No.12.アクセストークン発行処理が成功する
def test_tf_operator_login_case12(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/login", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "tfOperatorId": data_copy["tfOperatorId"],
        "tfOperatorName": response.json()["tfOperatorName"],
        "tfOperatorPasswordResetFlg": response.json()["tfOperatorPasswordResetFlg"],
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 08.共通エラーチェック処理
# 正常系
# No.13.共通エラーチェック処理が成功（エラー情報有り）
def test_tf_operator_login_case13(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.tokenUtil.TokenUtilClass.create_token_closed").return_value = {
        "result": False,
        "errorInfo": {
            "errorCode": "020004",
            "message": logUtil.message_build(MessageConstClass.ERRORS["020004"]["logMessage"], 'TFオペレータ')
        }
    }
    header = create_header["header"]
    response = client.post("/api/2.0/tfoperator/login", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": response.json()["errorInfo"][0]["errorCode"],
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# 09.終了処理
# No.14.変数．エラー情報がない
def test_tf_operator_login_case14(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/login", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "tfOperatorId": data_copy["tfOperatorId"],
        "tfOperatorName": response.json()["tfOperatorName"],
        "tfOperatorPasswordResetFlg": response.json()["tfOperatorPasswordResetFlg"],
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# パラメータ検証処理
# 01.パラメータ検証処理
# No.15.TFオペレータログインAPI_01.引数検証処理チェック処理
# 引数．ヘッダパラメータ．タイムスタンプ
# 1.値が設定されていない ("")
def test_tf_operator_login_case15_1(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    header["timeStamp"] = ""
    response = client.post("/api/2.0/tfoperator/login", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "010006",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# 2.値が設定されていない (None)
def test_tf_operator_login_case15_2(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    header["timeStamp"] = None
    response = client.post("/api/2.0/tfoperator/login", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "010006",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# 3.文字列型ではなく24桁
def test_tf_operator_login_case15_3(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    header["timeStamp"] = 123456789012345678901234
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    router_request_body = routerRequestBody(**data_copy)
    response = tfOperatorLoginRouter.input_check(
        trace_logger,
        header["timeStamp"],
        router_request_body
    )
    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "010006",
            "message": response["errorInfo"]["message"]
        }
    }
    print(response)


# 4.文字列型で23桁
def test_tf_operator_login_case15_4(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    header["timeStamp"] = "2022/08/23 15:12:01.690"
    response = client.post("/api/2.0/tfoperator/login", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "tfOperatorId": data_copy["tfOperatorId"],
        "tfOperatorName": response.json()["tfOperatorName"],
        "tfOperatorPasswordResetFlg": response.json()["tfOperatorPasswordResetFlg"],
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 引数．リクエストボディ．TFオペレータID
# 1.値が設定されていない ("")
def test_tf_operator_login_case15_5(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfOperatorId"] = ""
    response = client.post("/api/2.0/tfoperator/login", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "010006",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# 2.値が設定されていない (None)
def test_tf_operator_login_case15_6(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfOperatorId"] = None
    response = client.post("/api/2.0/tfoperator/login", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "010006",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# 3.入力可能文字のみで文字列型ではなく2桁
def test_tf_operator_login_case15_7(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfOperatorId"] = 12
    response = client.post("/api/2.0/tfoperator/login", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "010006",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# 4.入力可能文字以外 (半角記号) を含み文字列型であり17桁
def test_tf_operator_login_case15_8(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfOperatorId"] = "!#$%&'()=~|{}*?,1"
    response = client.post("/api/2.0/tfoperator/login", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "010006",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# 5.入力可能文字のみで文字列型であり3桁
def test_tf_operator_login_case15_9(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfOperatorId"] = "123"
    response = client.post("/api/2.0/tfoperator/login", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "tfOperatorId": data_copy["tfOperatorId"],
        "tfOperatorName": response.json()["tfOperatorName"],
        "tfOperatorPasswordResetFlg": response.json()["tfOperatorPasswordResetFlg"],
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 6.入力可能文字のみで文字列型であり16桁
def test_tf_operator_login_case15_10(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfOperatorId"] = "1234567890123456"
    response = client.post("/api/2.0/tfoperator/login", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "tfOperatorId": data_copy["tfOperatorId"],
        "tfOperatorName": response.json()["tfOperatorName"],
        "tfOperatorPasswordResetFlg": response.json()["tfOperatorPasswordResetFlg"],
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 引数．リクエストボディ．TFオペレータパスワード
# 1.値が設定されていない ("")
def test_tf_operator_login_case15_11(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfOperatorPassword"] = ""
    response = client.post("/api/2.0/tfoperator/login", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "010006",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# 2.値が設定されていない (None)
def test_tf_operator_login_case15_12(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfOperatorPassword"] = None
    response = client.post("/api/2.0/tfoperator/login", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "010006",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# 3.入力可能文字のみで文字列型ではなく7桁
def test_tf_operator_login_case15_13(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfOperatorPassword"] = 1234567
    response = client.post("/api/2.0/tfoperator/login", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "010006",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# 4.入力可能文字以外 (半角記号) を含み文字列型であり618桁
def test_tf_operator_login_case15_14(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfOperatorPassword"] = "!#$%&'()=~|{}*?,11111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111"
    response = client.post("/api/2.0/tfoperator/login", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "010006",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# 5.入力可能文字のみで文字列型であり8桁(英大文字、英小文字、数字、記号のうち３種類以上)
def test_tf_operator_login_case15_15(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfOperatorId"] = "t-test8"
    data_copy["tfOperatorPassword"] = "@$aa1111"
    response = client.post("/api/2.0/tfoperator/login", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "tfOperatorId": data_copy["tfOperatorId"],
        "tfOperatorName": response.json()["tfOperatorName"],
        "tfOperatorPasswordResetFlg": response.json()["tfOperatorPasswordResetFlg"],
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 6.入力可能文字のみで文字列型であり617桁(英大文字、英小文字、数字、記号のうち３種類以上)
def test_tf_operator_login_case15_16(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfOperatorId"] = "t-test617"
    data_copy["tfOperatorPassword"] = "aaa@$aaaaaaaaaaa1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111"
    response = client.post("/api/2.0/tfoperator/login", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "tfOperatorId": data_copy["tfOperatorId"],
        "tfOperatorName": response.json()["tfOperatorName"],
        "tfOperatorPasswordResetFlg": response.json()["tfOperatorPasswordResetFlg"],
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 02.終了処理
# No.16.変数．エラー情報がない
def test_tf_operator_login_case16(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfOperatorId"] = "t-test617"
    data_copy["tfOperatorPassword"] = "aaa@$aaaaaaaaaaa1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111"
    response = client.post("/api/2.0/tfoperator/login", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "tfOperatorId": data_copy["tfOperatorId"],
        "tfOperatorName": response.json()["tfOperatorName"],
        "tfOperatorPasswordResetFlg": response.json()["tfOperatorPasswordResetFlg"],
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 02.終了処理
# No.17.変数．エラー情報がある
def test_tf_operator_login_case17(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfOperatorPassword"] = 1234567
    response = client.post("/api/2.0/tfoperator/login", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "010006",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())
