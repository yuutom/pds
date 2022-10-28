from fastapi.testclient import TestClient
from app import app
from fastapi import Request
import pytest
from pytest_mock.plugin import MockerFixture
from util.tokenUtil import TokenUtilClass
import util.logUtil as logUtil
import json
from const.sqlConst import SqlConstClass
import routers.closed.pdsUserGetAccessRecordRouter as pdsUserGetAccessRecordRouter
from routers.closed.pdsUserGetAccessRecordRouter import requestBody as routerRequestBody
from const.systemConst import SystemConstClass

client = TestClient(app)

DATA = {
    "pdsUserId": "C9876543",
    "fromDate": "2022/01/01",
    "toDate": "2022/12/31"
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
            "pdsUserId": DATA["pdsUserId"],
            "Content-Type": "application/json",
            "accessToken": token_result["accessToken"],
            "timeStamp": "2022/08/23 15:12:01.690",
            "Authorization": "Bearer " + token_result["jwt"]
        }
    }


# 01.アクセストークン検証処理
# 異常系
# No1.アクセストークン検証処理が失敗する
def test_pds_user_get_access_record_case1(create_header):
    header = create_header["header"]
    header["accessToken"] = "518302174323385ee79afc2e37e3783f15e48e43d75f004a83e41667996087770c5e474023c0d6969529b49a8fd553ca454e54adbf473ac1a129fd4b0314abc4d4f33e4349749110f5b1774db69d5f87944e3a86c7d3ee10390a825f8bf35f1813774c94"
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(DATA))
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
def test_pds_user_get_access_record_case2(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "apiTypeCount": response.json()["apiTypeCount"],
        "apiUseInfo": response.json()["apiUseInfo"]
    }
    print(response.json())


# 異常系
# No3.共通エラーチェック処理が成功 (エラー情報有り)
def test_pds_user_get_access_record_case3(create_header):
    header = create_header["header"]
    header["accessToken"] = "518302174323385ee79afc2e37e3783f15e48e43d75f004a83e41667996087770c5e474023c0d6969529b49a8fd553ca454e54adbf473ac1a129fd4b0314abc4d4f33e4349749110f5b1774db69d5f87944e3a86c7d3ee10390a825f8bf35f1813774c94"
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(DATA))
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


# No4.パラメータ検証処理が失敗する
def test_pds_user_get_access_record_case4(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserId"] = "C0001"
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(data_copy))
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


# No5.パラメータ検証処理が成功する
def test_pds_user_get_access_record_case5(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "apiTypeCount": response.json()["apiTypeCount"],
        "apiUseInfo": response.json()["apiUseInfo"]
    }
    print(response.json())


# No6.共通エラーチェック処理が成功
def test_pds_user_get_access_record_case6(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserId"] = "C0001"
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(data_copy))
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


# 05.DB接続準備処理
# No7.接続に失敗する
# 設定値を異常な値に変更する
def test_pds_user_get_access_record_case7(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.commonUtil.CommonUtilClass.get_secret_info").return_value = {"host": "test", "port": "test", "username": "test", "password": "test"}
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(DATA))
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


# No8.接続に成功する
def test_pds_user_get_access_record_case8(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "apiTypeCount": response.json()["apiTypeCount"],
        "apiUseInfo": response.json()["apiUseInfo"]
    }
    print(response.json())


# 06.PDS利用状況取得処理
# No9.PDS利用状況取得処理が失敗する
def test_pds_user_get_access_record_case9(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "PDS_USER_USAGE_SITUATION_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(DATA))
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


# No10_1.PDS利用状況取得処理が成功する
# 実行日時の境界値を確認する
def test_pds_user_get_access_record_case10_1(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["fromDate"] = "2022/01/01"
    data_copy["toDate"] = "2022/05/01"
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "apiTypeCount": response.json()["apiTypeCount"],
        "apiUseInfo": response.json()["apiUseInfo"]
    }
    print(response.json())


# No10_2.PDS利用状況取得処理が成功する
# 実行日時の境界値を確認する
def test_pds_user_get_access_record_case10_2(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["fromDate"] = "2022/05/01"
    data_copy["toDate"] = "2022/06/30"
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "apiTypeCount": response.json()["apiTypeCount"],
        "apiUseInfo": response.json()["apiUseInfo"]
    }
    print(response.json())


# No10_3.PDS利用状況取得処理が成功する
# 実行日時の境界値を確認する
def test_pds_user_get_access_record_case10_3(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["fromDate"] = "2022/12/01"
    data_copy["toDate"] = "2023/01/01"
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "apiTypeCount": response.json()["apiTypeCount"],
        "apiUseInfo": response.json()["apiUseInfo"]
    }
    print(response.json())


# 07.共通エラーチェック処理
# No.11.共通エラーチェック処理が成功
def test_pds_user_get_access_record_case11(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "PDS_USER_USAGE_SITUATION_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(DATA))
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


# 08.API種別合計カウント初期化処理
# No.12.API種別合計カウント初期化処理に成功する
def test_pds_user_get_access_record_case12(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "apiTypeCount": response.json()["apiTypeCount"],
        "apiUseInfo": response.json()["apiUseInfo"]
    }
    print(response.json())


# 09.PDS利用状況情報作成処理
# No.13.PDS利用状況情報作成処理に成功する
def test_pds_user_get_access_record_case13(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "apiTypeCount": response.json()["apiTypeCount"],
        "apiUseInfo": response.json()["apiUseInfo"]
    }
    print(response.json())


# 10.API種別合計カウント加算処理
# No.14.API種別合計カウント加算処理に成功する（アクセストークン）
def test_pds_user_get_access_record_case14(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "apiTypeCount": response.json()["apiTypeCount"],
        "apiUseInfo": response.json()["apiUseInfo"]
    }
    print(response.json())


# No.15.API種別合計カウント加算処理に成功する(登録)
def test_pds_user_get_access_record_case15(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "apiTypeCount": response.json()["apiTypeCount"],
        "apiUseInfo": response.json()["apiUseInfo"]
    }
    print(response.json())


# No.16.API種別合計カウント加算処理に成功する（更新）
def test_pds_user_get_access_record_case16(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "apiTypeCount": response.json()["apiTypeCount"],
        "apiUseInfo": response.json()["apiUseInfo"]
    }
    print(response.json())


# No.17.API種別合計カウント加算処理に成功する（参照）
def test_pds_user_get_access_record_case17(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "apiTypeCount": response.json()["apiTypeCount"],
        "apiUseInfo": response.json()["apiUseInfo"]
    }
    print(response.json())


# No.18.API種別合計カウント加算処理に成功する（削除）
def test_pds_user_get_access_record_case18(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "apiTypeCount": response.json()["apiTypeCount"],
        "apiUseInfo": response.json()["apiUseInfo"]
    }
    print(response.json())


# No.19.API種別合計カウント加算処理に成功する（検索）
def test_pds_user_get_access_record_case19(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["fromDate"] = "2022/12/01"
    data_copy["toDate"] = "2023/12/01"
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "apiTypeCount": response.json()["apiTypeCount"],
        "apiUseInfo": response.json()["apiUseInfo"]
    }
    print(response.json())


# No.20.API種別合計カウント加算処理に成功する（一括削除）
def test_pds_user_get_access_record_case20(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "apiTypeCount": response.json()["apiTypeCount"],
        "apiUseInfo": response.json()["apiUseInfo"]
    }
    print(response.json())


# No.21.API種別合計カウント加算処理に成功する（一括DL）
def test_pds_user_get_access_record_case21(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["fromDate"] = "2022/12/01"
    data_copy["toDate"] = "2023/01/01"
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "apiTypeCount": response.json()["apiTypeCount"],
        "apiUseInfo": response.json()["apiUseInfo"]
    }
    print(response.json())


# 「変数．PDS利用状況取得結果リスト」の要素数分繰り返す
# No.22.PDS利用状況取得処理で取得結果が0件
def test_pds_user_get_access_record_case22(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["fromDate"] = "2030/01/01"
    data_copy["toDate"] = "2030/01/02"
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "apiTypeCount": response.json()["apiTypeCount"],
        "apiUseInfo": response.json()["apiUseInfo"]
    }
    print(response.json())


# 「変数．PDS利用状況取得結果リスト」の要素数分繰り返す
# No.23.PDS利用状況取得処理で取得結果が0件以外
def test_pds_user_get_access_record_case23(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "apiTypeCount": response.json()["apiTypeCount"],
        "apiUseInfo": response.json()["apiUseInfo"]
    }
    print(response.json())


# 11.アクセストークン発行処理
# No.24.アクセストークン発行処理が失敗する
def test_pds_user_get_access_record_case24(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "ACCESS_TOKEN_CLOSED_TF_OPERATOR_VERIF_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(data_copy))
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


# 11.アクセストークン発行処理
# No.24.アクセストークン発行処理が失敗する
def test_pds_user_get_access_record_case24_1(create_header):
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
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(data_copy))
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


# No.25.アクセストークン発行処理が成功する
def test_pds_user_get_access_record_case25(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "apiTypeCount": response.json()["apiTypeCount"],
        "apiUseInfo": response.json()["apiUseInfo"]
    }
    print(response.json())


# No.26.共通エラーチェック処理が成功
def test_pds_user_get_access_record_case26(create_header):
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
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(data_copy))
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


# 13.終了処理
# No.27.変数．エラー情報がある
def test_pds_user_get_access_record_case27(create_header):
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
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(data_copy))
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


# No.28.変数．エラー情報がない
def test_pds_user_get_access_record_case28(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "apiTypeCount": response.json()["apiTypeCount"],
        "apiUseInfo": response.json()["apiUseInfo"]
    }
    print(response.json())


# パラメータ検証処理
# 01.パラメータ検証処理
# No.29-1.引数．ヘッダパラメータ．タイムスタンプの値が設定されていない (空値)
def test_pds_user_get_access_record_case29_1(create_header):
    header = create_header["header"]
    header["timeStamp"] = None
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(data_copy))
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


# No.29-2.引数．ヘッダパラメータ．タイムスタンプが文字列型ではない
def test_pds_user_get_access_record_case29_2(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    header["timeStamp"] = 123456789012345678901234
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserGetAccessRecordRouter.input_check(
        trace_logger=trace_logger,
        request_body=router_request_body,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"]
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


# No.29-3.引数．ヘッダパラメータ．タイムスタンプが正常な値
def test_pds_user_get_access_record_case29_3(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "apiTypeCount": response.json()["apiTypeCount"],
        "apiUseInfo": response.json()["apiUseInfo"]
    }
    print(response.json())


# No.29-4.引数．ヘッダパラメータ．アクセストークンの値が設定されていない (空値)
def test_pds_user_get_access_record_case29_4(create_header):
    header = create_header["header"]
    header["accessToken"] = ""
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(data_copy))
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


# No.29-5.引数．ヘッダパラメータ．アクセストークンが文字列型ではない
def test_pds_user_get_access_record_case29_5(create_header):
    header = create_header["header"]
    header["accessToken"] = 111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111
    data_copy = DATA.copy()
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserGetAccessRecordRouter.input_check(
        trace_logger=trace_logger,
        request_body=router_request_body,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"]
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


# No.29-6.引数．ヘッダパラメータ．アクセストークンが正常な値
def test_pds_user_get_access_record_case29_6(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "apiTypeCount": response.json()["apiTypeCount"],
        "apiUseInfo": response.json()["apiUseInfo"]
    }
    print(response.json())


# No.29-7.引数．リクエストボディ．PDSユーザIDの値が設定されていない (空値)
def test_pds_user_get_access_record_case29_7(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserId"] = None
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(data_copy))
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


# No.29-8.引数．リクエストボディ．PDSユーザIDが文字列型ではない
def test_pds_user_get_access_record_case29_8(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserId"] = 1234567
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(data_copy))
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


# No.29-9.引数．リクエストボディ．PDSユーザIDが正常な値
def test_pds_user_get_access_record_case29_9(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "apiTypeCount": response.json()["apiTypeCount"],
        "apiUseInfo": response.json()["apiUseInfo"]
    }
    print(response.json())


# No.29-10.引数．リクエストボディ．検索日Fromが文字列型ではない
def test_pds_user_get_access_record_case29_10(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["fromDate"] = 1234567890
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020003",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No.29-11.引数．リクエストボディ．検索日Fromが文字列型である
def test_pds_user_get_access_record_case29_11(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "apiTypeCount": response.json()["apiTypeCount"],
        "apiUseInfo": response.json()["apiUseInfo"]
    }
    print(response.json())


# No.29-12.引数．リクエストボディ．検索日Toが文字列型ではない
def test_pds_user_get_access_record_case29_12(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["toDate"] = 1234567890
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020003",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "030006",
                "message": response.json()["errorInfo"][1]["message"]
            }
        ]
    }
    print(response.json())


# No.29-13.引数．リクエストボディ．検索日Toが文字列型である
def test_pds_user_get_access_record_case29_13(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "apiTypeCount": response.json()["apiTypeCount"],
        "apiUseInfo": response.json()["apiUseInfo"]
    }
    print(response.json())


# No.29-14.引数．リクエストボディ．検索日Fromが引数．リクエストボディ．検索日Toの値を超過している
def test_pds_user_get_access_record_case29_14(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["fromDate"] = "2022/06/01"
    data_copy["toDate"] = "2022/01/01"
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(data_copy))
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


# No.29-15.引数．リクエストボディ．検索日Fromが引数．リクエストボディ．検索日Toの値を超過していない
def test_pds_user_get_access_record_case29_15(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "apiTypeCount": response.json()["apiTypeCount"],
        "apiUseInfo": response.json()["apiUseInfo"]
    }
    print(response.json())


# No.30.終了処理　変数．エラー情報がない
def test_pds_user_get_access_record_case30(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "apiTypeCount": response.json()["apiTypeCount"],
        "apiUseInfo": response.json()["apiUseInfo"]
    }
    print(response.json())


# No.31.終了処理　変数．エラー情報がある
def test_pds_user_get_access_record_case31(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["fromDate"] = "2022/06/01"
    data_copy["toDate"] = "2022/01/01"
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(data_copy))
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


# 08.API種別合計カウント初期化処理
# No.32.API種別合計カウント初期化処理に成功する
def test_pds_user_get_access_record_case32(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["fromDate"] = "2022/01/01"
    data_copy["toDate"] = "2022/12/31"
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "apiTypeCount": response.json()["apiTypeCount"],
        "apiUseInfo": response.json()["apiUseInfo"]
    }
    print(response.json())


# 10.API種別合計カウント加算処理
# No.33.API種別合計カウント加算処理に成功する（検索(内部)）
def test_pds_user_get_access_record_case33(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["fromDate"] = "2022/01/01"
    data_copy["toDate"] = "2022/12/31"
    response = client.post("/api/2.0/pdsuser/getAccessRecord", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "apiTypeCount": response.json()["apiTypeCount"],
        "apiUseInfo": response.json()["apiUseInfo"]
    }
    print(response.json())
