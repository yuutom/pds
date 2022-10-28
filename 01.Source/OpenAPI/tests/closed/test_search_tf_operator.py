from fastapi.testclient import TestClient
from const.sqlConst import SqlConstClass
from app import app
from fastapi import Request
import pytest
from pytest_mock.plugin import MockerFixture
from util.tokenUtil import TokenUtilClass
import util.logUtil as logUtil
import json
from const.systemConst import SystemConstClass

client = TestClient(app)

BEARER = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0Zk9wZXJhdG9ySWQiOiJsLXRlc3QiLCJ0Zk9wZXJhdG9yTmFtZSI6Ilx1MzBlZFx1MzBiMFx1MzBhNFx1MzBmM1x1MzBjNlx1MzBiOVx1MzBjOCIsInRmT3BlcmF0b3JQYXNzd29yZFJlc2V0RmxnIjpmYWxzZSwiYWNjZXNzVG9rZW4iOiJiZGE4ZGY3OThiYzViZGZhMWZkODIyNmRiYmQ0OTMyMTY5ZmY5MjAzNWM0YzFlY2FjZjY2OGUyYzk2ZjAwZThlZTUxNTBiNGM0NTc0NjlkN2I4YmY1NzIxZDZlM2NiNzFiY2RiYzA3ODRiYzcyZWVlNjk1OGE3NTBiMWJkMWEzZWFmZWQ0OWFhNWU0ODZjYzQyZmM3OWNhMWY3MGQzZmM3Yzc0YzE5NjM3ODUzMjRhZDRhNGM0NjkxOGE4NjQ1N2ZiODE3NDU1MCIsImV4cCI6MTY2MTc0NjY3MX0.LCRjPEqKMkRQ_phaYnO7S7pd3SU_rgon-wsX14DBsPA"
ACCESS_TOKEN = "bda8df798bc5bdfa1fd8226dbbd4932169ff92035c4c1ecacf668e2c96f00e8ee5150b4c457469d7b8bf5721d6e3cb71bcdbc0784bc72eee6958a750b1bd1a3eafed49aa5e486cc42fc79ca1f70d3fc7c74c1963785324ad4a4c46918a86457fb8174550"
HEADER = {"Content-Type": "application/json", "timeStamp": "2022/08/23 15:12:01.690", "accessToken": ACCESS_TOKEN, "Authorization": "Bearer " + BEARER}

SEARCH_CRITERIA_DATA = {
    "userIdMatchMode": "前方一致",
    "userIdStr": "C0123456",
    "dataJsonKey": "data.name.first",
    "dataMatchMode": "前方一致",
    "dataStr": "taro",
    "imageHash": "glakjgirhul",
    "fromDate": "2023/01/01",
    "toDate": "2023/12/31"
}
DATA = {
    "pdsUserId": "C9876543",
    "tidListOutputFlg": True,
    "searchCriteria": SEARCH_CRITERIA_DATA
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


# No1.01.事前処理　異常系　事前処理に失敗する
def test_search_tf_operator_case1(create_header):
    header = create_header["header"]
    header["accessToken"] = "518302174323385ee79afc2e37e3783f15e48e43d75f004a83e41667996087770c5e474023c0d6969529b49a8fd553ca454e54adbf473ac1a129fd4b0314abc4d4f33e4349749110f5b1774db69d5f87944e3a86c7d3ee10390a825f8bf35f1813774c94"
    response = client.post("/api/2.0/transaction/search/1", headers=header, data=json.dumps(DATA))
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


# No2.メイン処理_01.事前処理　正常系　事前処理に成功する
# No4.メイン処理_02.DB接続準備処理　正常系　接続に成功する
# No7.メイン処理_03.PDSユーザ取得処理　正常系　PDSユーザ取得処理が成功する（1件以上の場合）
# No9.メイン処理_05.MongoDB検索判定処理　正常系　リクエストのリクエストボディ．保存データJsonキー情報がNull
# No14.メイン処理_07.個人情報検索処理　正常系　個人情報検索処理が成功する
# No16.メイン処理_09.tidリスト出力有無フラグ判定処理　正常系　リクエストのリクエストボディ．tidリスト出力有無フラグがfalse
# No18.メイン処理_10.tidリスト未作成処理　正常系　tidリスト未作成処理が成功する
# No24.メイン処理_12.参照情報格納リスト作成処理　正常系　参照情報格納リスト作成処理が成功する
# No26.メイン処理_「変数．個人情報検索結果．トランザクションID」の種類数分繰り返す　正常系　「変数．個人情報検索結果．トランザクションID」の種類数が0以外
# No27.メイン処理_13.保存したいデータマスキング処理リスト作成処理　正常系　保存したいデータマスキング処理リスト作成処理が成功する
# No28.メイン処理_14.保存したいデータマスキング処理実行処理　正常系　保存したいデータマスキング処理実行処理が成功する
# No30.メイン処理_「変数．個人情報検索結果．トランザクションID」の種類数分繰り返す　正常系　「変数．個人情報検索結果．トランザクションID」の種類数が0以外
# No31.メイン処理_15.参照情報作成処理　正常系　参照情報作成処理が成功する（１０００件以上、２０００件未満）　ヘッダパラメータ．ページNo.の指定なし
# No37.メイン処理_16.アクセストークン発行処理　正常系　アクセストークン発行処理が成功する
# No40.メイン処理_18.終了処理　正常系　変数．エラー情報がない
# No42.事前処理_01.アクセストークン検証処理　正常系　アクセストークン検証処理が成功する
# No45.事前処理_03.パラメータ検証処理　正常系　パラメータ検証処理が成功する
# No47.事前処理_05.終了処理　正常系　変数．エラー情報がない
# No48.パラメータ検証処理_01.パラメータ検証処理
# No49.パラメータ検証処理_02.終了処理　正常系　変数．エラー情報がない
# No51.保存したいデータマスキング処理_01.Json判定処理　正常系　Json形式への変換ができない
# No53.保存したいデータマスキング処理_02.保存したいデータの文字列取得処理　正常系　保存したいデータの文字列取得処理が成功する
# No56.保存したいデータマスキング処理_05.Json文字列変換処理　正常系　Json文字列変換処理が成功する
# No57.保存したいデータマスキング処理_06.終了処理　正常系　変数．エラー情報がない
# ページNoあり
def test_search_tf_operator_case2_1(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/transaction/search/1", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "maxPage": response.json()["maxPage"],
        "maxCount": response.json()["maxCount"],
        "pageNo": response.json()["pageNo"],
        "tidList": response.json()["tidList"],
        "transactionInfoList": response.json()["transactionInfoList"]
    }
    print(response.json())


# No2.メイン処理_01.事前処理　正常系　事前処理に成功する
# No4.メイン処理_02.DB接続準備処理　正常系　接続に成功する
# No7.メイン処理_03.PDSユーザ取得処理　正常系　PDSユーザ取得処理が成功する（1件以上の場合）
# No9.メイン処理_05.MongoDB検索判定処理　正常系　リクエストのリクエストボディ．保存データJsonキー情報がNull
# No14.メイン処理_07.個人情報検索処理　正常系　個人情報検索処理が成功する
# No16.メイン処理_09.tidリスト出力有無フラグ判定処理　正常系　リクエストのリクエストボディ．tidリスト出力有無フラグがfalse
# No18.メイン処理_10.tidリスト未作成処理　正常系　tidリスト未作成処理が成功する
# No24.メイン処理_12.参照情報格納リスト作成処理　正常系　参照情報格納リスト作成処理が成功する
# No26.メイン処理_「変数．個人情報検索結果．トランザクションID」の種類数分繰り返す　正常系　「変数．個人情報検索結果．トランザクションID」の種類数が0以外
# No27.メイン処理_13.保存したいデータマスキング処理リスト作成処理　正常系　保存したいデータマスキング処理リスト作成処理が成功する
# No28.メイン処理_14.保存したいデータマスキング処理実行処理　正常系　保存したいデータマスキング処理実行処理が成功する
# No30.メイン処理_「変数．個人情報検索結果．トランザクションID」の種類数分繰り返す　正常系　「変数．個人情報検索結果．トランザクションID」の種類数が0以外
# No31.メイン処理_15.参照情報作成処理　正常系　参照情報作成処理が成功する（１０００件以上、２０００件未満）　ヘッダパラメータ．ページNo.の指定なし
# No37.メイン処理_16.アクセストークン発行処理　正常系　アクセストークン発行処理が成功する
# No40.メイン処理_18.終了処理　正常系　変数．エラー情報がない
# No42.事前処理_01.アクセストークン検証処理　正常系　アクセストークン検証処理が成功する
# No45.事前処理_03.パラメータ検証処理　正常系　パラメータ検証処理が成功する
# No47.事前処理_05.終了処理　正常系　変数．エラー情報がない
# No48.パラメータ検証処理_01.パラメータ検証処理
# No49.パラメータ検証処理_02.終了処理　正常系　変数．エラー情報がない
# No51.保存したいデータマスキング処理_01.Json判定処理　正常系　Json形式への変換ができない
# No53.保存したいデータマスキング処理_02.保存したいデータの文字列取得処理　正常系　保存したいデータの文字列取得処理が成功する
# No56.保存したいデータマスキング処理_05.Json文字列変換処理　正常系　Json文字列変換処理が成功する
# No57.保存したいデータマスキング処理_06.終了処理　正常系　変数．エラー情報がない
# ページNoなし
def test_search_tf_operator_case2_2(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/transaction/search", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "maxPage": response.json()["maxPage"],
        "maxCount": response.json()["maxCount"],
        "pageNo": response.json()["pageNo"],
        "tidList": response.json()["tidList"],
        "transactionInfoList": response.json()["transactionInfoList"]
    }
    print(response.json())


# No3.メイン処理_02.DB接続準備処理　異常系　接続に失敗する
def test_search_tf_operator_case3(mocker: MockerFixture, create_header):
    header = create_header["header"]
    # Exception
    mocker.patch("util.commonUtil.CommonUtilClass.get_secret_info").return_value = {"host": "test", "port": "test", "username": "test", "password": "test"}
    response = client.post("/api/2.0/transaction/search/1", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
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


# No5.メイン処理_03.PDSユーザ取得処理　異常系　PDSユーザ取得処理が失敗する
def test_search_tf_operator_case5(mocker: MockerFixture, create_header):
    header = create_header["header"]
    # Exception
    mocker.patch.object(SqlConstClass, "MONGODB_SECRET_NAME_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.post("/api/2.0/transaction/search/1", headers=header, data=json.dumps(DATA))
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


# No6.メイン処理_03.PDSユーザ取得処理　正常系　PDSユーザ取得処理が成功する（0件の場合）
def test_search_tf_operator_case6(create_header):
    header = create_header["header"]
    DATA["pdsUserId"] = "C0000000"
    response = client.post("/api/2.0/transaction/search/1", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "maxPage": response.json()["maxPage"],
        "maxCount": response.json()["maxCount"],
        "pageNo": response.json()["pageNo"],
        "tidList": response.json()["tidList"],
        "transactionInfoList": response.json()["transactionInfoList"]
    }
    print(response.json())


# No9.メイン処理_05.MongoDB検索判定処理　正常系　リクエストのリクエストボディ．保存データJsonキー情報がNull
def test_search_tf_operator_case9(create_header):
    header = create_header["header"]
    SEARCH_CRITERIA_DATA["dataJsonKey"] = None
    response = client.post("/api/2.0/transaction/search/1", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "maxPage": response.json()["maxPage"],
        "maxCount": response.json()["maxCount"],
        "pageNo": response.json()["pageNo"],
        "tidList": response.json()["tidList"],
        "transactionInfoList": response.json()["transactionInfoList"]
    }
    print(response.json())


# No11.メイン処理_06.MongoDB検索処理
# MongoDB検索処理が失敗する
def test_search_tf_operator_case11(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.commonUtil.CommonUtilClass.mongodb_search").side_effect = Exception('testException')
    response = client.post("/api/2.0/transaction/search/1", headers=header, data=json.dumps(DATA))
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


# No13.メイン処理_07.個人情報検索処理　異常系　個人情報検索処理が失敗する
def test_search_tf_operator_case13(mocker: MockerFixture, create_header):
    header = create_header["header"]
    # Exception
    mocker.patch.object(SqlConstClass, "USER_PROFILE_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.post("/api/2.0/transaction/search/1", headers=header, data=json.dumps(DATA))
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


# No16.メイン処理_09.tidリスト出力有無フラグ判定処理　正常系　リクエストのリクエストボディ．tidリスト出力有無フラグがfalse
def test_search_tf_operator_case16(create_header):
    header = create_header["header"]
    DATA["tidListOutputFlg"] = False
    response = client.post("/api/2.0/transaction/search/1", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "maxPage": response.json()["maxPage"],
        "maxCount": response.json()["maxCount"],
        "pageNo": response.json()["pageNo"],
        "tidList": response.json()["tidList"],
        "transactionInfoList": response.json()["transactionInfoList"]
    }
    print(response.json())


# No18.メイン処理_10.tidリスト未作成処理　正常系　tidリスト未作成処理が成功する
def test_search_tf_operator_case18(create_header):
    header = create_header["header"]
    DATA["tidListOutputFlg"] = False
    response = client.post("/api/2.0/transaction/search/1", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "maxPage": response.json()["maxPage"],
        "maxCount": response.json()["maxCount"],
        "pageNo": response.json()["pageNo"],
        "tidList": response.json()["tidList"],
        "transactionInfoList": response.json()["transactionInfoList"]
    }
    print(response.json())


# No19.メイン処理_11.tidリスト作成処理　正常系　tidリスト作成処理が成功する（１０００件以上、２０００件未満）
# ヘッダパラメータ．ページNo.の指定なし
def test_search_tf_operator_case19(create_header):
    header = create_header["header"]
    SEARCH_CRITERIA_DATA["userIdStr"] = None
    # SEARCH_CRITERIA_DATA["dataJsonKey"] = None
    # SEARCH_CRITERIA_DATA["dataMatchMode"] = None
    # SEARCH_CRITERIA_DATA["dataStr"] = None
    SEARCH_CRITERIA_DATA["imageHash"] = None
    SEARCH_CRITERIA_DATA["fromDate"] = None
    SEARCH_CRITERIA_DATA["toDate"] = None
    response = client.post("/api/2.0/transaction/search", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "maxPage": response.json()["maxPage"],
        "maxCount": response.json()["maxCount"],
        "pageNo": response.json()["pageNo"],
        "tidList": response.json()["tidList"],
        "transactionInfoList": response.json()["transactionInfoList"]
    }
    print(response.json())


# No20.メイン処理_11.tidリスト作成処理　正常系　tidリスト作成処理が成功する（１０００件以上、２０００件未満）
# ヘッダパラメータ．ページNo.が１の場合
def test_search_tf_operator_case20(create_header):
    header = create_header["header"]
    SEARCH_CRITERIA_DATA["userIdStr"] = None
    # SEARCH_CRITERIA_DATA["dataJsonKey"] = None
    response = client.post("/api/2.0/transaction/search/1", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "maxPage": response.json()["maxPage"],
        "maxCount": response.json()["maxCount"],
        "pageNo": response.json()["pageNo"],
        "tidList": response.json()["tidList"],
        "transactionInfoList": response.json()["transactionInfoList"]
    }
    print(response.json())


# No21.メイン処理_11.tidリスト作成処理　正常系　tidリスト作成処理が成功する（１０００件以上、２０００件未満）
# ヘッダパラメータ．ページNo.が２の場合
def test_search_tf_operator_case21(create_header):
    header = create_header["header"]
    SEARCH_CRITERIA_DATA["userIdStr"] = None
    # SEARCH_CRITERIA_DATA["dataJsonKey"] = None
    response = client.post("/api/2.0/transaction/search/2", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "maxPage": response.json()["maxPage"],
        "maxCount": response.json()["maxCount"],
        "pageNo": response.json()["pageNo"],
        "tidList": response.json()["tidList"],
        "transactionInfoList": response.json()["transactionInfoList"]
    }
    print(response.json())


# No22.メイン処理_11.tidリスト作成処理　正常系　tidリスト作成処理が成功する（１０００件以上、２０００件未満）
# ヘッダパラメータ．ページNo.が３の場合
def test_search_tf_operator_case22(create_header):
    header = create_header["header"]
    SEARCH_CRITERIA_DATA["userIdStr"] = None
    # SEARCH_CRITERIA_DATA["dataJsonKey"] = None
    response = client.post("/api/2.0/transaction/search/3", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "maxPage": response.json()["maxPage"],
        "maxCount": response.json()["maxCount"],
        "pageNo": response.json()["pageNo"],
        "tidList": response.json()["tidList"],
        "transactionInfoList": response.json()["transactionInfoList"]
    }
    print(response.json())


# No23.メイン処理_11.tidリスト作成処理　正常系　tidリスト作成処理が成功する（取得データなし）
def test_search_tf_operator_case23(create_header):
    header = create_header["header"]
    SEARCH_CRITERIA_DATA["userIdStr"] = "C987654321"
    # SEARCH_CRITERIA_DATA["dataJsonKey"] = None
    response = client.post("/api/2.0/transaction/search/2", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "maxPage": response.json()["maxPage"],
        "maxCount": response.json()["maxCount"],
        "pageNo": response.json()["pageNo"],
        "tidList": response.json()["tidList"],
        "transactionInfoList": response.json()["transactionInfoList"]
    }
    print(response.json())


# No41.事前処理_01.アクセストークン検証処理　異常系　アクセストークン検証処理が失敗する
def test_search_tf_operator_case41(create_header):
    header = create_header["header"]
    header["accessToken"] = "518302174323385ee79afc2e37e3783f15e48e43d75f004a83e41667996087770c5e474023c0d6969529b49a8fd553ca454e54adbf473ac1a129fd4b0314abc4d4f33e4349749110f5b1774db69d5f87944e3a86c7d3ee10390a825f8bf35f1813774c94"
    response = client.post("/api/2.0/transaction/search/1", headers=header, data=json.dumps(DATA))
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


# No48.パラメータ検証処理_01.パラメータ検証処理　異常系　引数．パスパラメータ．ページNo　文字列型である　入力可能文字以外が含まれる（半角英字）
def test_search_tf_operator_case48_1_1(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/transaction/search/1a", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020019",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020020",
                "message": response.json()["errorInfo"][1]["message"]
            }
        ]
    }
    print(response.json())


# No48.パラメータ検証処理_01.パラメータ検証処理　異常系　引数．ヘッダパラメータ．タイムスタンプ　値が設定されていない
def test_search_tf_operator_case48_2_1(create_header):
    header = create_header["header"]
    header["timeStamp"] = ""
    response = client.post("/api/2.0/transaction/search/1", headers=header, data=json.dumps(DATA))
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


# No48.パラメータ検証処理_01.パラメータ検証処理　異常系　引数．ヘッダパラメータ．タイムスタンプ　値が設定されている　文字列型ではない
def test_search_tf_operator_case48_2_2(create_header):
    header = create_header["header"]
    header["timeStamp"] = 1234567890
    response = client.post("/api/2.0/transaction/search/1", headers=header, data=json.dumps(DATA))
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
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No48.パラメータ検証処理_01.パラメータ検証処理　異常系　引数．ヘッダパラメータ．タイムスタンプ　値が設定されている　文字列型である　２４桁である　入力規則違反している　hh:mmがhhh:mm
def test_search_tf_operator_case48_2_3(create_header):
    header = create_header["header"]
    header["timeStamp"] = "2022/08/23 115:12:01.690"
    response = client.post("/api/2.0/transaction/search/1", headers=header, data=json.dumps(DATA))
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


# No48.パラメータ検証処理_01.パラメータ検証処理　異常系　引数．ヘッダパラメータ．アクセストークン　値が設定されていない（空値）
def test_search_tf_operator_case48_3_1(create_header):
    header = create_header["header"]
    header["accessToken"] = ""
    response = client.post("/api/2.0/transaction/search/1", headers=header, data=json.dumps(DATA))
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


# No48.パラメータ検証処理_01.パラメータ検証処理　異常系　引数．ヘッダパラメータ．アクセストークン　文字列型ではない
def test_search_tf_operator_case48_3_2(create_header):
    header = create_header["header"]
    header["accessToken"] = 111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111
    response = client.post("/api/2.0/transaction/search/1", headers=header)
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


# No48.パラメータ検証処理_01.パラメータ検証処理　異常系　引数．リクエストボディ．PDSユーザID　値が設定されていない（空値）
def test_search_tf_operator_case48_4_1(create_header):
    header = create_header["header"]
    DATA["pdsUserId"] = ""
    response = client.post("/api/2.0/transaction/search/1", headers=header, data=json.dumps(DATA))
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


# No48.パラメータ検証処理_01.パラメータ検証処理　異常系　引数．リクエストボディ．PDSユーザID　値が設定されている　文字列型である　入力規則違反している（C＋数値6桁）
def test_search_tf_operator_case48_4_2(create_header):
    header = create_header["header"]
    DATA["pdsUserId"] = "C123456"
    response = client.post("/api/2.0/transaction/search/1", headers=header, data=json.dumps(DATA))
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


# No48.パラメータ検証処理_01.パラメータ検証処理　異常系　引数．リクエストボディ．tidリスト出力有無フラグ　論理型ではない
def test_search_tf_operator_case48_5_1(create_header):
    header = create_header["header"]
    DATA["tidListOutputFlg"] = "1"
    response = client.post("/api/2.0/transaction/search/1", headers=header, data=json.dumps(DATA))
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


# No48.パラメータ検証処理_01.パラメータ検証処理　異常系　引数．リクエストボディ．検索用ユーザID検索文字列　３７桁である
def test_search_tf_operator_case48_6_1(create_header):
    header = create_header["header"]
    SEARCH_CRITERIA_DATA["userIdStr"] = "1234567890123456789012345678901234567"
    response = client.post("/api/2.0/transaction/search/1", headers=header, data=json.dumps(DATA))
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


# No48.パラメータ検証処理_01.パラメータ検証処理　異常系　引数．リクエストボディ．保存データJsonキー情報　文字列型ではない
def test_search_tf_operator_case48_7_1(create_header):
    header = create_header["header"]
    SEARCH_CRITERIA_DATA["dataJsonKey"] = 123
    response = client.post("/api/2.0/transaction/search/1", headers=header, data=json.dumps(DATA))
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


# No48.パラメータ検証処理_01.パラメータ検証処理　異常系　引数．リクエストボディ．保存データ検索モード　入力可能文字以外が含まれる
def test_search_tf_operator_case48_8_1(create_header):
    header = create_header["header"]
    SEARCH_CRITERIA_DATA["dataMatchMode"] = "123"
    response = client.post("/api/2.0/transaction/search/1", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020020",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No48.パラメータ検証処理_01.パラメータ検証処理　異常系　引数．リクエストボディ．保存データ検索文字列　文字列型ではない
def test_search_tf_operator_case48_9_1(create_header):
    header = create_header["header"]
    SEARCH_CRITERIA_DATA["dataStr"] = 123
    response = client.post("/api/2.0/transaction/search/1", headers=header, data=json.dumps(DATA))
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


# No48.パラメータ検証処理_01.パラメータ検証処理　異常系　引数．リクエストボディ．保存したいバイナリデータのハッシュ値　入力可能文字以外が含まれる（半角記号）
def test_search_tf_operator_case48_10_1(create_header):
    header = create_header["header"]
    SEARCH_CRITERIA_DATA["imageHash"] = "%"
    response = client.post("/api/2.0/transaction/search/1", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020020",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No48.パラメータ検証処理_01.パラメータ検証処理　異常系　引数．リクエストボディ．検索用日時From　１１桁である　入力規則違反している（形式は yyyy/MM/dd でない　hh:mmがhhh:mm）
def test_search_tf_operator_case48_11_1(create_header):
    header = create_header["header"]
    SEARCH_CRITERIA_DATA["fromDate"] = "2022/100/01"
    response = client.post("/api/2.0/transaction/search/1", headers=header, data=json.dumps(DATA))
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
            },
            {
                "errorCode": "030006",
                "message": response.json()["errorInfo"][2]["message"]
            }
        ]
    }
    print(response.json())


# No48.パラメータ検証処理_01.パラメータ検証処理　異常系　引数．リクエストボディ．検索用日時To　１１桁である　入力規則違反している（形式は yyyy/MM/dd でない　hh:mmがhhh:mm）
def test_search_tf_operator_case48_12_1(create_header):
    header = create_header["header"]
    SEARCH_CRITERIA_DATA["toDate"] = "2022/100/01"
    response = client.post("/api/2.0/transaction/search/1", headers=header, data=json.dumps(DATA))
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


# No48.パラメータ検証処理_01.パラメータ検証処理　異常系　引数．リクエストボディ．検索用日時To　１１桁である　入力規則違反している（形式は yyyy/MM/dd でない　hh:mmがhhh:mm）
def test_search_tf_operator_case48_13_1(create_header):
    header = create_header["header"]
    SEARCH_CRITERIA_DATA["fromDate"] = "2022/10/01"
    SEARCH_CRITERIA_DATA["toDate"] = "2022/09/30"
    response = client.post("/api/2.0/transaction/search/1", headers=header, data=json.dumps(DATA))
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


# No58.Jsonデータマスキング処理_01.マスキング対象コピ-取得処理　正常系　マスキング対象コピ-取得処理が成功する
# No59.Jsonデータマスキング処理_02.マスキング対象型判定処理　正常系　引数．マスキング対象がJson形式
# No61.Jsonデータマスキング処理_03.Jsonキー、バリューリスト取得処理　正常系　Jsonキー、バリューリスト取得処理が成功する
# No63.Jsonデータマスキング処理_「変数．Jsonキーリスト」の要素数だけ繰り返す　正常系　「引数．マスキング対象」の要素数が0件以外
# No64.Jsonデータマスキング処理_04.Jsonバリュー型判定　正常系　取得した値の型が、Json型 もしくは リスト型
# No66.Jsonデータマスキング処理_05.Jsonデータマスキング処理　正常系　Jsonデータマスキング処理が成功する
# No67.Jsonデータマスキング処理_06.文字数取得処理　正常系　文字数取得処理が成功する
# No68.Jsonデータマスキング処理_07.マスキング対象コピー更新処理　正常系　マスキング対象コピー更新処理が成功する
# No70.Jsonデータマスキング処理_「引数．マスキング対象」の要素数だけ繰り返す　正常系　「引数．マスキング対象」の要素数が0以外
# No71.Jsonデータマスキング処理_08.リストバリュー型判定　正常系　取得した値の型が、Json型 もしくは リスト型
# No73.Jsonデータマスキング処理_09.Jsonデータマスキング処理　正常系　Jsonデータマスキング処理が成功する
# No74.Jsonデータマスキング処理_10.文字数取得処理　正常系　文字数取得処理が成功する
# No75.Jsonデータマスキング処理_11.マスキング対象コピー更新処理　正常系　マスキング対象コピー更新処理が成功する
# No76.Jsonデータマスキング処理_12.終了処理　正常系　変数．エラー情報がない
def test_search_tf_operator_case58(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/transaction/search/1", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "maxPage": response.json()["maxPage"],
        "maxCount": response.json()["maxCount"],
        "pageNo": response.json()["pageNo"],
        "tidList": response.json()["tidList"],
        "transactionInfoList": response.json()["transactionInfoList"]
    }
    print(response.json())


# メイン処理
# 04.共通エラーチェック処理
# ◆正常系 共通エラーチェック処理が成功する（エラー情報有り）
def test_search_tf_operator_add_case4(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "MONGODB_SECRET_NAME_SELECT_SQL", """)
        SELECT
            m_pds_user.pds_user_instance_secret_name
            , m_pds_user.tokyo_a_mongodb_secret_name
            , m_pds_user.tokyo_c_mongodb_secret_name
            , m_pds_user.osaka_a_mongodb_secret_name
            , m_pds_user.osaka_c_mongodb_secret_name
        FROM
            m_pds_user
        WHERE
            m_pds_user.pds_user_id = "ABCDEFG"
            AND m_pds_user.valid_flg = True; """)
    response = client.post("/api/2.0/transaction/search/1", headers=header, data=json.dumps(DATA))
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

# 08.共通エラーチェック処理
# ◆正常系 共通エラーチェック処理が成功する（エラー情報有り）

# 17.共通エラーチェック処理
# ◆正常系 共通エラーチェック処理が成功（エラー情報有り）

# 18.API実行履歴登録処理
# ◆異常系 API実行履歴登録処理が失敗する

# ◆正常系 API実行履歴登録処理が成功する

# 19.終了処理
# 変数．エラー情報がある(直前のNo.39でエラー）

# 変数．エラー情報がない


# 事前処理
# 02.共通エラーチェック処理
# ◆正常系 共通エラーチェック処理が成功する（エラー情報有り）
def test_search_tf_operator_add_case45(create_header):
    header = create_header["header"]
    header["accessToken"] = "518302174323385ee79afc2e37e3783f15e48e43d75f004a83e41667996087770c5e474023c0d6969529b49a8fd553ca454e54adbf473ac1a129fd4b0314abc4d4f33e4349749110f5b1774db69d5f87944e3a86c7d3ee10390a825f8bf35f1813774c94"
    response = client.post("/api/2.0/transaction/search/1", headers=header, data=json.dumps(DATA))
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


# 04.共通エラーチェック処理
# ◆正常系 共通エラーチェック処理が成功する（エラー情報有り）
def test_search_tf_operator_add_case48(create_header):
    header = create_header["header"]
    header["timeStamp"] = "2022/08/23 115:12:01.690"
    response = client.post("/api/2.0/transaction/search/1", headers=header, data=json.dumps(DATA))
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
