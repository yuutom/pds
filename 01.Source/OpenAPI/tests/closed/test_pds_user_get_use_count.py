from fastapi.testclient import TestClient
from const.sqlConst import SqlConstClass
from app import app
from fastapi import Request
import pytest
from pytest_mock.plugin import MockerFixture
from util.tokenUtil import TokenUtilClass
from util.billUtil import BillUtilClass
import util.logUtil as logUtil
import json
from const.systemConst import SystemConstClass

client = TestClient(app)

BEARER = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0Zk9wZXJhdG9ySWQiOiJsLXRlc3QiLCJ0Zk9wZXJhdG9yTmFtZSI6Ilx1MzBlZFx1MzBiMFx1MzBhNFx1MzBmM1x1MzBjNlx1MzBiOVx1MzBjOCIsInRmT3BlcmF0b3JQYXNzd29yZFJlc2V0RmxnIjpmYWxzZSwiYWNjZXNzVG9rZW4iOiJiZGE4ZGY3OThiYzViZGZhMWZkODIyNmRiYmQ0OTMyMTY5ZmY5MjAzNWM0YzFlY2FjZjY2OGUyYzk2ZjAwZThlZTUxNTBiNGM0NTc0NjlkN2I4YmY1NzIxZDZlM2NiNzFiY2RiYzA3ODRiYzcyZWVlNjk1OGE3NTBiMWJkMWEzZWFmZWQ0OWFhNWU0ODZjYzQyZmM3OWNhMWY3MGQzZmM3Yzc0YzE5NjM3ODUzMjRhZDRhNGM0NjkxOGE4NjQ1N2ZiODE3NDU1MCIsImV4cCI6MTY2MTc0NjY3MX0.LCRjPEqKMkRQ_phaYnO7S7pd3SU_rgon-wsX14DBsPA"
ACCESS_TOKEN = "bda8df798bc5bdfa1fd8226dbbd4932169ff92035c4c1ecacf668e2c96f00e8ee5150b4c457469d7b8bf5721d6e3cb71bcdbc0784bc72eee6958a750b1bd1a3eafed49aa5e486cc42fc79ca1f70d3fc7c74c1963785324ad4a4c46918a86457fb8174550"
HEADER = {"Content-Type": "application/json", "timeStamp": "2022/08/23 15:12:01.690", "accessToken": ACCESS_TOKEN, "Authorization": "Bearer " + BEARER}
DATA = {
    "pdsUserId": "C9876543",
    "fromDate": "2022/01/01",
    "toDate": "2022/12/31"
}
TF_OPERATOR_INFO = {
    "tfOperatorId": "t-test4",
    "tfOperatorName": "テスト"
}


@pytest.fixture
def create_header():
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_closed(tfOperatorInfo=TF_OPERATOR_INFO, accessToken=None)
    yield {
        "header": {
            "pdsUserId": DATA["pdsUserId"],
            "Content-Type": "application/json",
            "accessToken": token_result["accessToken"],
            "timeStamp": "2022/08/23 15:12:01.690",
            "Authorization": "Bearer " + token_result["jwt"]
        }
    }


# No1.01.メイン処理_01.アクセストークン検証処理　異常系　アクセストークン検証処理が失敗する
def test_pds_user_get_use_count_case1(create_header):
    header = create_header["header"]
    header["accessToken"] = "518302174323385ee79afc2e37e3783f15e48e43d75f004a83e41667996087770c5e474023c0d6969529b49a8fd553ca454e54adbf473ac1a129fd4b0314abc4d4f33e4349749110f5b1774db69d5f87944e3a86c7d3ee10390a825f8bf35f1813774c94"
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(DATA))
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


# No2.01.メイン処理_01.アクセストークン検証処理　正常系　アクセストークン検証処理が成功する
def test_pds_user_get_use_count_case2(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "charge": response.json()["charge"],
        "pdsUseData": response.json()["pdsUseData"]
    }
    print(response.json())


# 02.共通エラーチェック処理
# No03.共通エラーチェック処理が成功
def test_pds_user_get_use_count_case3(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    header["accessToken"] = "518302174323385ee79afc2e37e3783f15e48e43d75f004a83e41667996087770c5e474023c0d6969529b49a8fd553ca454e54adbf473ac1a129fd4b0314abc4d4f33e4349749110f5b1774db69d5f87944e3a86c7d3ee10390a825f8bf35f1813774c94"
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(data_copy))
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
# No04.パラメータ検証処理が失敗する
def test_pds_user_get_use_count_case4(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserId"] = ""
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(data_copy))
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


# No05.パラメータ検証処理が成功する
def test_pds_user_get_use_count_case5(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "charge": response.json()["charge"],
        "pdsUseData": response.json()["pdsUseData"]
    }
    print(response.json())


# 04.共通エラーチェック処理
# No06.共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_get_use_count_case6(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserId"] = ""
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(data_copy))
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


# 05.DB接続準備処理
# No07.接続に失敗する
# 設定値を異常な値に変更する
def test_pds_user_get_use_count_case7(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    # Exception
    mocker.patch("util.commonUtil.CommonUtilClass.get_secret_info").return_value = {"host": "test", "port": "test", "username": "test", "password": "test"}
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(data_copy))
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


# No08.接続に成功する
def test_pds_user_get_use_count_case8(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "charge": response.json()["charge"],
        "pdsUseData": response.json()["pdsUseData"]
    }
    print(response.json())


# 06.API実行履歴取得処理
# No09.API実行履歴取得処理が失敗する
def test_pds_user_get_use_count_case9(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "PDS_USER_GET_USE_COUNT_API_HISTORY_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(DATA))
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


# No10.API実行履歴取得処理が成功する
def test_pds_user_get_use_count_case10(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "charge": response.json()["charge"],
        "pdsUseData": response.json()["pdsUseData"]
    }
    print(response.json())


# 変数．API実行履歴取得結果．API種別の種類数分繰り返す
# N0.11.API実行履歴取得結果が0件
def test_pds_user_get_use_count_case11(mocker: MockerFixture, create_header):
    # Exception
    header = create_header["header"]
    DATA["fromDate"] = "2028/01/01"
    DATA["toDate"] = ""
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "charge": response.json()["charge"],
        "pdsUseData": response.json()["pdsUseData"]
    }
    print(response.json())


# No12.API実行履歴取得結果が0件以外
def test_pds_user_get_use_count_case12(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "charge": response.json()["charge"],
        "pdsUseData": response.json()["pdsUseData"]
    }
    print(response.json())


# 07.共通エラーチェック処理
# No13.共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_get_use_count_case13(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "PDS_USER_GET_USE_COUNT_API_HISTORY_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(DATA))
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


# 08.請求金額取得処理
# No14.請求金額取得処理が失敗する
def test_pds_user_get_use_count_case14(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "BILLING_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(DATA))
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


# No15.請求金額取得処理が成功する
def test_pds_user_get_use_count_case15(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "charge": response.json()["charge"],
        "pdsUseData": response.json()["pdsUseData"]
    }
    print(response.json())


# 09.共通エラーチェック処理
# No16.共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_get_use_count_case16(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "BILLING_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(DATA))
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


# 10.累進請求金額計算処理
# No17.累進請求金額計算処理が失敗する
def test_pds_user_get_use_count_case17(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    # Exception
    mocker.patch.object(BillUtilClass, "progressive_billing_exec", side_effect=Exception('testException'))
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(data_copy))
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


# No18.累進請求金額計算処理が成功する
def test_pds_user_get_use_count_case18(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "charge": response.json()["charge"],
        "pdsUseData": response.json()["pdsUseData"]
    }
    print(response.json())


# 11.請求金額計算処理
# No19.正しく請求金額が計算されること
def test_pds_user_get_use_count_case19(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "charge": response.json()["charge"],
        "pdsUseData": response.json()["pdsUseData"]
    }
    print(response.json())


# 12.PDS利用状況データ作成処理
# No20~31.正しくカウントが加算されること
def test_pds_user_get_use_count_case20(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "charge": response.json()["charge"],
        "pdsUseData": response.json()["pdsUseData"]
    }
    print(response.json())


# 13.リソース請求金額計算処理
# No32.リソース請求金額計算処理が失敗する
def test_pds_user_get_use_count_case32(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "PDS_USER_RESOURCE_BILLING_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(DATA))
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


# No33.リソース請求金額計算処理が成功する
def test_pds_user_get_use_count_case33(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "charge": response.json()["charge"],
        "pdsUseData": response.json()["pdsUseData"]
    }
    print(response.json())


# 14.請求金額計算処理
# No34.請求金額計算処理が失敗する
def test_pds_user_get_use_count_case34(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    # Exception
    mocker.patch("util.billUtil.BillUtilClass.resource_billing_exec").return_value = {}
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(data_copy))
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


# No35.請求金額計算処理が成功する
def test_pds_user_get_use_count_case35(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "charge": response.json()["charge"],
        "pdsUseData": response.json()["pdsUseData"]
    }
    print(response.json())


# 15.アクセストークン発行処理
# No36.アクセストークン発行処理が失敗する
def test_pds_user_get_use_count_case36(mocker: MockerFixture, create_header):
    mocker.patch("util.tokenUtil.TokenUtilClass.verify_token_closed").return_value = {'result': True, 'payload': {'tfOperatorId': 't-test4', 'tfOperatorName': 'テスト', 'accessToken': '14d517e61315fbf0545b765dd0e7ca296d65a5403aef84a360efe191e8b6d28a6c30dda7557e269b8c800327a13fa3ce5833fc0351c884addb340921883eac40d03d92281ac6a7cf18c32aebfd6bf48c71aedc781f707ca0714b3c804c1526e2d2a6ad0a'}}
    mocker.patch("util.tokenUtil.TokenUtilClass.create_token_closed").return_value = Exception('testException')
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": response.json()["errorInfo"]
    }
    print(response.json())


# No37.アクセストークン発行処理が成功する
def test_pds_user_get_use_count_case37(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "charge": response.json()["charge"],
        "pdsUseData": response.json()["pdsUseData"]
    }
    print(response.json())


# 16.共通エラーチェック処理
# No38.共通エラーチェック処理が成功
def test_pds_user_get_use_count_case38(mocker: MockerFixture, create_header):
    mocker.patch("util.tokenUtil.TokenUtilClass.create_token_closed").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": response.json()["errorInfo"]
    }
    print(response.json())


# 17.終了処理
# No39.変数．エラー情報がある(直前のNo.３７でエラー）
def test_pds_user_get_use_count_case39(mocker: MockerFixture, create_header):
    mocker.patch("util.tokenUtil.TokenUtilClass.create_token_closed").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": response.json()["errorInfo"]
    }
    print(response.json())


# No40.変数．エラー情報がない
def test_pds_user_get_use_count_case40(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "charge": response.json()["charge"],
        "pdsUseData": response.json()["pdsUseData"]
    }
    print(response.json())


# 02.パラメータ検証処理
# 01.パラメータ検証処理
# No41-01-01.引数．ヘッダパラメータ．タイムスタンプ 値が設定されていない（空値）
def test_pds_user_get_use_count_case40_1_1(create_header):
    header = create_header["header"]
    header["timeStamp"] = ""
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(DATA))
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


# No41-01-02.引数．ヘッダパラメータ．タイムスタンプ 入力規則違反している　hh:mmがhhh:mm
def test_pds_user_get_use_count_case40_1_2(create_header):
    header = create_header["header"]
    header["timeStamp"] = "2022/08/23 151:12:01.690"
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(DATA))
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


# No41-01-03.引数．ヘッダパラメータ．タイムスタンプ 正常
def test_pds_user_get_use_count_case40_1_3(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "charge": response.json()["charge"],
        "pdsUseData": response.json()["pdsUseData"]
    }
    print(response.json())


# No41-02-01.引数．ヘッダパラメータ．アクセストークン 値が設定されていない（空値）
def test_pds_user_get_use_count_case40_2_1(create_header):
    header = create_header["header"]
    header["accessToken"] = ""
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(DATA))
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


# No41.引数．ヘッダパラメータ．アクセストークン　文字列型である　201桁である 入力可能文字以外が含まれる(全角)
def test_pds_user_get_use_count_case41_2_2(create_header):
    header = create_header["header"]
    header["accessToken"] = "ＡＢＣＤＥＦＧＨＩＪ" * 20 + "Ｋ"
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(DATA))
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


# No41-02-03.引数．ヘッダパラメータ．アクセストークン 正常
def test_pds_user_get_use_count_case41_2_3(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "charge": response.json()["charge"],
        "pdsUseData": response.json()["pdsUseData"]
    }
    print(response.json())


# No41-03-01.引数．リクエストボディ．PDSユーザID 値が設定されていない（空値）
def test_pds_user_get_use_count_case41_3_1(create_header):
    header = create_header["header"]
    DATA["pdsUserId"] = ""
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(DATA))
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


# No41-3-2.引数．リクエストボディ．PDSユーザID　値が設定されている　文字列型ではない　7桁である
def test_pds_user_get_use_count_case41_3_2(create_header):
    header = create_header["header"]
    DATA["pdsUserId"] = 1234567
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(DATA))
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


# No41-03-03.引数．リクエストボディ．PDSユーザID 正常
def test_pds_user_get_use_count_case41_3_3(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "charge": response.json()["charge"],
        "pdsUseData": response.json()["pdsUseData"]
    }
    print(response.json())


# No41-04-01.引数．リクエストボディ．検索日From 文字列型ではない １１桁である
def test_pds_user_get_use_count_case41_4_1(create_header):
    header = create_header["header"]
    DATA["fromDate"] = 12345678901
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(DATA))
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


# No41-04-02.引数．リクエストボディ．検索日From 正常
def test_pds_user_get_use_count_case41_4_2(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "charge": response.json()["charge"],
        "pdsUseData": response.json()["pdsUseData"]
    }
    print(response.json())


# No41-05-01.引数．リクエストボディ．検索日To 文字列型ではない １１桁である
def test_pds_user_get_use_count_case41_5_1(create_header):
    header = create_header["header"]
    DATA["toDate"] = 12345678901
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(DATA))
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


# No41-05-02.引数．リクエストボディ．検索日To 正常
def test_pds_user_get_use_count_case41_5_2(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "charge": response.json()["charge"],
        "pdsUseData": response.json()["pdsUseData"]
    }
    print(response.json())


# No41-06-01.引数．リクエストボディ．検索日Fromと、引数．リクエストボディ．検索日To 検索日Fromが検索日Toの値を超過している
def test_pds_user_get_use_count_case41_6_1(create_header):
    header = create_header["header"]
    DATA["fromDate"] = "2023/12/31"
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "030006",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No41-06-02.引数．リクエストボディ．検索日Fromと、引数．リクエストボディ．検索日To 検索日Fromが検索日Toの値を超過していない
def test_pds_user_get_use_count_case41_6_2(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "charge": response.json()["charge"],
        "pdsUseData": response.json()["pdsUseData"]
    }
    print(response.json())


# 02.終了処理
# No42.変数．エラー情報がない
def test_pds_user_get_use_count_case42(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "charge": response.json()["charge"],
        "pdsUseData": response.json()["pdsUseData"]
    }
    print(response.json())


# No43.変数．エラー情報がある
def test_pds_user_get_use_count_case43(create_header):
    header = create_header["header"]
    DATA["fromDate"] = "2023/12/31"
    response = client.post("/api/2.0/pdsuser/getUseCount", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "030006",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())
