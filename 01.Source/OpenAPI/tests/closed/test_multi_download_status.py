from fastapi.testclient import TestClient
from const.sqlConst import SqlConstClass
from app import app
from fastapi import Request
import pytest
from pytest_mock.plugin import MockerFixture
from util.tokenUtil import TokenUtilClass
import util.logUtil as logUtil
import json
import datetime
from const.systemConst import SystemConstClass

client = TestClient(app)

BEARER = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0Zk9wZXJhdG9ySWQiOiJsLXRlc3QiLCJ0Zk9wZXJhdG9yTmFtZSI6Ilx1MzBlZFx1MzBiMFx1MzBhNFx1MzBmM1x1MzBjNlx1MzBiOVx1MzBjOCIsInRmT3BlcmF0b3JQYXNzd29yZFJlc2V0RmxnIjpmYWxzZSwiYWNjZXNzVG9rZW4iOiJiZGE4ZGY3OThiYzViZGZhMWZkODIyNmRiYmQ0OTMyMTY5ZmY5MjAzNWM0YzFlY2FjZjY2OGUyYzk2ZjAwZThlZTUxNTBiNGM0NTc0NjlkN2I4YmY1NzIxZDZlM2NiNzFiY2RiYzA3ODRiYzcyZWVlNjk1OGE3NTBiMWJkMWEzZWFmZWQ0OWFhNWU0ODZjYzQyZmM3OWNhMWY3MGQzZmM3Yzc0YzE5NjM3ODUzMjRhZDRhNGM0NjkxOGE4NjQ1N2ZiODE3NDU1MCIsImV4cCI6MTY2MTc0NjY3MX0.LCRjPEqKMkRQ_phaYnO7S7pd3SU_rgon-wsX14DBsPA"
ACCESS_TOKEN = "bda8df798bc5bdfa1fd8226dbbd4932169ff92035c4c1ecacf668e2c96f00e8ee5150b4c457469d7b8bf5721d6e3cb71bcdbc0784bc72eee6958a750b1bd1a3eafed49aa5e486cc42fc79ca1f70d3fc7c74c1963785324ad4a4c46918a86457fb8174550"
HEADER = {"Content-Type": "application/json", "timeStamp": "2022/08/23 15:12:01.690", "accessToken": ACCESS_TOKEN, "Authorization": "Bearer " + BEARER}
DATA = {
    "pdsUserId": "C0000011"
}
TF_OPERATOR_INFO = {
    "tfOperatorId": "pc-test",
    "tfOperatorName": "変更太郎"
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
def test_multi_download_status_case1(create_header):
    header = create_header["header"]
    header["accessToken"] = "518302174323385ee79afc2e37e3783f15e48e43d75f004a83e41667996087770c5e474023c0d6969529b49a8fd553ca454e54adbf473ac1a129fd4b0314abc4d4f33e4349749110f5b1774db69d5f87944e3a86c7d3ee10390a825f8bf35f1813774c94"
    response = client.post("/api/2.0/transaction/download/status", headers=header, data=json.dumps(DATA))
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
def test_multi_download_status_case2(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/transaction/download/status", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "multiDownloadInfo": response.json()["multiDownloadInfo"]
    }
    print(response.json())


# 02.共通エラーチェック処理
# No03.共通エラーチェック処理が成功
def test_multi_download_status_case3(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    header["accessToken"] = "518302174323385ee79afc2e37e3783f15e48e43d75f004a83e41667996087770c5e474023c0d6969529b49a8fd553ca454e54adbf473ac1a129fd4b0314abc4d4f33e4349749110f5b1774db69d5f87944e3a86c7d3ee10390a825f8bf35f1813774c94"
    response = client.post("/api/2.0/transaction/download/status", headers=header, data=json.dumps(data_copy))
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
def test_multi_download_status_case4(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserId"] = ""
    response = client.post("/api/2.0/transaction/download/status", headers=header, data=json.dumps(data_copy))
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
def test_multi_download_status_case5(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/transaction/download/status", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "multiDownloadInfo": response.json()["multiDownloadInfo"]
    }
    print(response.json())


# 04.共通エラーチェック処理
# No06.共通エラーチェック処理が成功（エラー情報有り）
def test_multi_download_status_case6(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserId"] = ""
    response = client.post("/api/2.0/transaction/download/status", headers=header, data=json.dumps(data_copy))
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
def test_multi_download_status_case7(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    # Exception
    mocker.patch("util.commonUtil.CommonUtilClass.get_secret_info").return_value = {"host": "test", "port": "test", "username": "test", "password": "test"}
    response = client.post("/api/2.0/transaction/download/status", headers=header, data=json.dumps(data_copy))
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
def test_multi_download_status_case8(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/transaction/download/status", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "multiDownloadInfo": response.json()["multiDownloadInfo"]
    }
    print(response.json())


# 06.個人情報一括DL状態管理取得処理
# No09.個人情報一括DL状態管理取得処理が失敗する
def test_multi_download_status_case9(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "MULTI_DOWUNLOAD_STATUS_UNION_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    response = client.post("/api/2.0/transaction/download/status", headers=header, data=json.dumps(DATA))
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


# No10.個人情報一括DL状態管理取得処理が成功する
def test_multi_download_status_case10(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/transaction/download/status", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "multiDownloadInfo": response.json()["multiDownloadInfo"]
    }
    print(response.json())


# 07.共通エラーチェック処理
# No11.共通エラーチェック処理が成功（エラー情報有り）
def test_multi_download_status_case11(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "MULTI_DOWUNLOAD_STATUS_UNION_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    response = client.post("/api/2.0/transaction/download/status", headers=header, data=json.dumps(DATA))
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


# 「変数．個人情報一括DL状態管理取得結果リスト」の要素数分繰り返す
# No12.個人情報一括DL状態管理取得処理の取得件数が0件
def test_multi_download_status_case12(mocker: MockerFixture, create_header):
    # Exception
    header = create_header["header"]
    DATA["pdsUserId"] = "C7777777"
    response = client.post("/api/2.0/transaction/download/status", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "multiDownloadInfo": response.json()["multiDownloadInfo"]
    }
    print(response.json())


# No13.個人情報一括DL状態管理取得処理の取得件数が0件以外
def test_multi_download_status_case13(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/transaction/download/status", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "multiDownloadInfo": response.json()["multiDownloadInfo"]
    }
    print(response.json())


# 08.実行ステータスチェック処理
# No14.変数．個人情報一括DL状態管理取得結果[変数．WBTループ数][1] = 2
def test_multi_download_status_case14(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.postgresDbUtil.PostgresDbUtilClass.select_tuple_list").return_value = {
        "result": True,
        "rowcount": 1,
        "query_results": [('3', '2', 'sample03', datetime.datetime(2022, 8, 20, 19, 32, 31, 490000), datetime.datetime(2022, 8, 21, 19, 32, 31, 490000))]
    }
    header = create_header["header"]
    response = client.post("/api/2.0/transaction/download/status", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "multiDownloadInfo": response.json()["multiDownloadInfo"]
    }
    print(response.json())


# No15.変数．個人情報一括DL状態管理取得結果[変数．WBTループ数][1] = 2以外
def test_multi_download_status_case15(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.postgresDbUtil.PostgresDbUtilClass.select_tuple_list").return_value = {
        "result": True,
        "rowcount": 1,
        "query_results": [('1', '1', 'sample02', datetime.datetime(2022, 8, 20, 19, 32, 31, 490000), datetime.datetime(2022, 8, 21, 19, 32, 31, 490000))]
    }
    header = create_header["header"]
    response = client.post("/api/2.0/transaction/download/status", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "multiDownloadInfo": response.json()["multiDownloadInfo"]
    }
    print(response.json())


# 09.個人情報一括ダウンロード情報作成処理
# No16.変数．個人情報一括DL状態管理取得結果[変数．WBTループ数][1] = 1
def test_multi_download_status_case16(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.postgresDbUtil.PostgresDbUtilClass.select_tuple_list").return_value = {
        "result": True,
        "rowcount": 1,
        "query_results": [('1', '1', 'sample01', datetime.datetime(2022, 8, 20, 19, 32, 31, 490000), datetime.datetime(2022, 8, 21, 19, 32, 31, 490000))]
    }
    header = create_header["header"]
    response = client.post("/api/2.0/transaction/download/status", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "multiDownloadInfo": response.json()["multiDownloadInfo"]
    }
    print(response.json())


# No17.変数．個人情報一括DL状態管理取得結果[変数．WBTループ数][1] = 3
def test_multi_download_status_case17(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.postgresDbUtil.PostgresDbUtilClass.select_tuple_list").return_value = {
        "result": True,
        "rowcount": 1,
        "query_results": [('4', '3', 'sample04', datetime.datetime(2022, 8, 20, 19, 32, 31, 490000), datetime.datetime(2022, 8, 21, 19, 32, 31, 490000))]
    }
    header = create_header["header"]
    response = client.post("/api/2.0/transaction/download/status", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "multiDownloadInfo": response.json()["multiDownloadInfo"]
    }
    print(response.json())


# No18.変数．個人情報一括DL状態管理取得結果[変数．WBTループ数][1] = 9
def test_multi_download_status_case18(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.postgresDbUtil.PostgresDbUtilClass.select_tuple_list").return_value = {
        "result": True,
        "rowcount": 1,
        "query_results": [('5', '9', 'sample05', datetime.datetime(2022, 8, 20, 19, 32, 31, 490000), datetime.datetime(2022, 8, 21, 19, 32, 31, 490000))]
    }
    header = create_header["header"]
    response = client.post("/api/2.0/transaction/download/status", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "multiDownloadInfo": response.json()["multiDownloadInfo"]
    }
    print(response.json())


# No19.個人情報一括ダウンロード情報作成処理が成功する
def test_multi_download_status_case19(mocker: MockerFixture, create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/transaction/download/status", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "multiDownloadInfo": response.json()["multiDownloadInfo"]
    }
    print(response.json())


# 10.WBTのタスク結果取得API実行処理
# No20.WBTのタスク結果取得API実行処理が失敗する
def test_multi_download_status_case20(mocker: MockerFixture, create_header):
    # Exception
    header = create_header["header"]
    response = client.post("/api/2.0/transaction/download/status", headers=header, data=json.dumps(DATA))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "990018",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No21.WBTのタスク結果取得API実行処理が成功する
def test_multi_download_status_case21(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/transaction/download/status", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "multiDownloadInfo": response.json()["multiDownloadInfo"]
    }
    print(response.json())


# 11.共通エラーチェック処理
# No22.共通エラーチェック処理が成功（エラー情報有り）
def test_multi_download_status_case22(mocker: MockerFixture, create_header):
    # Exception
    header = create_header["header"]
    response = client.post("/api/2.0/transaction/download/status", headers=header, data=json.dumps(DATA))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "990018",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# 12.個人情報一括ダウンロード情報作成処理
# No23.変数．タスク結果取得API実行結果がPROCESSING
def test_multi_download_status_case23(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/transaction/download/status", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "multiDownloadInfo": response.json()["multiDownloadInfo"]
    }
    print(response.json())


# No24.変数．タスク結果取得API実行結果がFINISHED
def test_multi_download_status_case24(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/transaction/download/status", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "multiDownloadInfo": response.json()["multiDownloadInfo"]
    }
    print(response.json())


# No25.変数．タスク結果取得API実行結果がERROR_HAPPENED
def test_multi_download_status_case25(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/transaction/download/status", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "multiDownloadInfo": response.json()["multiDownloadInfo"]
    }
    print(response.json())


# No26.個人情報一括ダウンロード情報作成処理が成功する
def test_multi_download_status_case26(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/transaction/download/status", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "multiDownloadInfo": response.json()["multiDownloadInfo"]
    }
    print(response.json())


# 13.個人情報一括ダウンロード情報リスト追加処理
# No27.個人情報一括ダウンロード情報リスト追加処理が成功する
def test_multi_download_status_case27(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/transaction/download/status", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "multiDownloadInfo": response.json()["multiDownloadInfo"]
    }
    print(response.json())


# 14.アクセストークン発行処理
# No28.アクセストークン発行処理が失敗する
def test_multi_download_status_case28(mocker: MockerFixture, create_header):
    mocker.patch("util.tokenUtil.TokenUtilClass.create_token_closed").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/transaction/download/status", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": response.json()["errorInfo"]
    }
    print(response.json())


# No29.アクセストークン発行処理が成功する
def test_multi_download_status_case29(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/transaction/download/status", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "multiDownloadInfo": response.json()["multiDownloadInfo"]
    }
    print(response.json())


# 15.共通エラーチェック処理
# No30.共通エラーチェック処理が成功
def test_multi_download_status_case30(mocker: MockerFixture, create_header):
    mocker.patch("util.tokenUtil.TokenUtilClass.create_token_closed").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/transaction/download/status", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": response.json()["errorInfo"]
    }
    print(response.json())


# 16.終了処理
# No31.変数．エラー情報がある
def test_multi_download_status_case31(mocker: MockerFixture, create_header):
    mocker.patch("util.tokenUtil.TokenUtilClass.create_token_closed").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/transaction/download/status", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": response.json()["errorInfo"]
    }
    print(response.json())


# No32.変数．エラー情報がない
def test_multi_download_status_case32(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/transaction/download/status", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "multiDownloadInfo": response.json()["multiDownloadInfo"]
    }
    print(response.json())


# 02.パラメータ検証処理
# 01.パラメータ検証処理
# No33-01-01.引数．ヘッダパラメータ．タイムスタンプ 値が設定されていない（空値）
def test_multi_download_status_case33_1_1(create_header):
    header = create_header["header"]
    header["timeStamp"] = ""
    response = client.post("/api/2.0/transaction/download/status", headers=header, data=json.dumps(DATA))
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


# No33-01-02.引数．ヘッダパラメータ．タイムスタンプ ２４桁である 入力規則違反している　hh:mmがhhh:mm
def test_multi_download_status_case33_1_2(create_header):
    header = create_header["header"]
    header["timeStamp"] = "2022/08/23 151:12:01.690"
    response = client.post("/api/2.0/transaction/download/status", headers=header, data=json.dumps(DATA))
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


# No33-01-03.引数．ヘッダパラメータ．タイムスタンプ 正常
def test_multi_download_status_case33_1_3(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/transaction/download/status", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "multiDownloadInfo": response.json()["multiDownloadInfo"]
    }
    print(response.json())


# No33-02-01.引数．ヘッダパラメータ．アクセストークン 値が設定されていない（空値）
def test_multi_download_status_case33_2_1(create_header):
    header = create_header["header"]
    header["accessToken"] = ""
    response = client.post("/api/2.0/transaction/download/status", headers=header, data=json.dumps(DATA))
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


# No33-02-02.引数．ヘッダパラメータ．アクセストークン　文字列型である　201桁である 入力可能文字以外が含まれる(全角)
def test_multi_download_status_case33_2_2(create_header):
    header = create_header["header"]
    header["accessToken"] = "ＡＢＣＤＥＦＧＨＩＪ" * 20 + "Ｋ"
    response = client.post("/api/2.0/transaction/download/status", headers=header, data=json.dumps(DATA))
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


# No33-02-03.引数．ヘッダパラメータ．アクセストークン 正常
def test_multi_download_status_case33_2_3(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/transaction/download/status", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "multiDownloadInfo": response.json()["multiDownloadInfo"]
    }
    print(response.json())


# No33-03-01.引数．リクエストボディ．PDSユーザID 値が設定されていない（空値）
def test_multi_download_status_case33_3_1(create_header):
    header = create_header["header"]
    DATA["pdsUserId"] = ""
    response = client.post("/api/2.0/transaction/download/status", headers=header, data=json.dumps(DATA))
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


# No33-03-02.引数．リクエストボディ．PDSユーザID　値が設定されている　文字列型ではない　7桁である
def test_multi_download_status_case33_3_2(create_header):
    header = create_header["header"]
    DATA["pdsUserId"] = 1234567
    response = client.post("/api/2.0/transaction/download/status", headers=header, data=json.dumps(DATA))
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


# No33-03-03.引数．リクエストボディ．PDSユーザID 正常
def test_multi_download_status_case33_3_3(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/transaction/download/status", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "multiDownloadInfo": response.json()["multiDownloadInfo"]
    }
    print(response.json())


# 02.終了処理
# No34.変数．エラー情報がない
def test_multi_download_status_case34(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/transaction/download/status", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "multiDownloadInfo": response.json()["multiDownloadInfo"]
    }
    print(response.json())


# No35.変数．エラー情報がある
def test_multi_download_status_case35(create_header):
    header = create_header["header"]
    DATA["pdsUserId"] = 1234567
    response = client.post("/api/2.0/transaction/download/status", headers=header, data=json.dumps(DATA))
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
