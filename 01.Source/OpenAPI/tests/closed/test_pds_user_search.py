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
DATA = {
    "pdsUser": "C9876543",
    "fromDate": "2022/09/01",
    "toDate": "2022/12/31",
    "pdsUserStatus": True
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
            "pdsUserId": DATA["pdsUser"],
            "Content-Type": "application/json",
            "accessToken": token_result["accessToken"],
            "timeStamp": "2022/08/23 15:12:01.690",
            "Authorization": "Bearer " + token_result["jwt"]
        }
    }


# No1.01.メイン処理_01.アクセストークン検証処理　異常系　アクセストークン検証処理が失敗する
# No3.01.メイン処理_02.共通エラーチェック処理　正常系　共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_search_case1(create_header):
    header = create_header["header"]
    header["accessToken"] = "518302174323385ee79afc2e37e3783f15e48e43d75f004a83e41667996087770c5e474023c0d6969529b49a8fd553ca454e54adbf473ac1a129fd4b0314abc4d4f33e4349749110f5b1774db69d5f87944e3a86c7d3ee10390a825f8bf35f1813774c94"
    response = client.post("/api/2.0/pdsuser/search", headers=header, data=json.dumps(DATA))
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
# No5.01.メイン処理_03.パラメータ検証処理　正常系　パラメータ検証処理が成功する
# No7.01.メイン処理_05.DB接続準備処理　正常系　接続に成功する
# No9.01.メイン処理_06.PDSユーザ検索処理　正常系　PDSユーザ検索処理が成功する
# No12.01.メイン処理_08.PDSユーザ情報作成処理　正常系　PDSユーザ情報作成処理に成功する
# No14.01.メイン処理_09.アクセストークン発行処理　正常系　アクセストークン発行処理が成功する
# No17.01.メイン処理_11.終了処理　正常系　変数．エラー情報がない
# 全ての条件入力(PDSユーザ検索テキスト,PDSユーザ公開鍵有効期限From,PDSユーザ公開鍵有効期限To,PDSユーザ公開鍵有効状態)
def test_pds_user_search_case2(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser/search", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "pdsUserInfo": response.json()["pdsUserInfo"]
    }
    print(response.json())


# No3.01.メイン処理_02.共通エラーチェック処理　正常系　共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_search_case3(create_header):
    header = create_header["header"]
    header["accessToken"] = "518302174323385ee79afc2e37e3783f15e48e43d75f004a83e41667996087770c5e474023c0d6969529b49a8fd553ca454e54adbf473ac1a129fd4b0314abc4d4f33e4349749110f5b1774db69d5f87944e3a86c7d3ee10390a825f8bf35f1813774c94"
    response = client.post("/api/2.0/pdsuser/search", headers=header, data=json.dumps(DATA))
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


# No4.01.メイン処理_03.引数検証処理チェック処理　異常系　引数．ヘッダパラメータ．タイムスタンプ　値が設定されていない（空値）
# No5.01.メイン処理_04.共通エラーチェック処理　正常系　共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_search_case4_1_1(create_header):
    header = create_header["header"]
    header["timeStamp"] = ""
    response = client.post("/api/2.0/pdsuser/search", headers=header, data=json.dumps(DATA))
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


# No4.01.メイン処理_03.引数検証処理チェック処理　異常系　引数．ヘッダパラメータ．タイムスタンプ　値が設定されている　文字列型である　２４桁である　入力規則違反している　hh:mmがhhh:mm
# No5.01.メイン処理_04.共通エラーチェック処理　正常系　共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_search_case4_1_2(create_header):
    header = create_header["header"]
    header["timeStamp"] = "2022/08/23 155:12:01.690"
    response = client.post("/api/2.0/pdsuser/search", headers=header, data=json.dumps(DATA))
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


# No4.01.メイン処理_03.引数検証処理チェック処理　異常系　引数．ヘッダパラメータ．タイムスタンプ　値が設定されている　文字列型ではない
# No5.01.メイン処理_04.共通エラーチェック処理　正常系　共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_search_case4_1_3(create_header):
    header = create_header["header"]
    header["timeStamp"] = 123456789012345678901234
    response = client.post("/api/2.0/pdsuser/search", headers=header, data=json.dumps(DATA))
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


# No4.01.メイン処理_03.引数検証処理チェック処理　異常系　引数．ヘッダパラメータ．アクセストークン　値が設定されていない（空値）
# No5.01.メイン処理_04.共通エラーチェック処理　正常系　共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_search_case4_2_1(create_header):
    header = create_header["header"]
    header["accessToken"] = ""
    response = client.post("/api/2.0/pdsuser/search", headers=header, data=json.dumps(DATA))
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


# No4.01.メイン処理_03.引数検証処理チェック処理　異常系　引数．ヘッダパラメータ．アクセストークン　値が設定されている　文字列型である　２０１桁である　入力可能文字以外が含まれる（全角）
# No5.01.メイン処理_04.共通エラーチェック処理　正常系　共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_search_case4_2_2(create_header):
    header = create_header["header"]
    header["accessToken"] = "１2345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890"
    response = client.post("/api/2.0/pdsuser/search", headers=header, data=json.dumps(DATA))
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


# No4.01.メイン処理_03.引数検証処理チェック処理　異常系　引数．ヘッダパラメータ．アクセストークン　値が設定されている　文字列型ではない
# No5.01.メイン処理_04.共通エラーチェック処理　正常系　共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_search_case4_2_3(create_header):
    header = create_header["header"]
    header["accessToken"] = 12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
    response = client.post("/api/2.0/pdsuser/search", headers=header, data=json.dumps(DATA))
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


# No4.01.メイン処理_03.引数検証処理チェック処理　異常系　引数．リクエストボディ．PDSユーザ検索テキスト　文字列型ではない
# No5.01.メイン処理_04.共通エラーチェック処理　正常系　共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_search_case4_3_1(create_header):
    header = create_header["header"]
    DATA["pdsUser"] = 12345
    response = client.post("/api/2.0/pdsuser/search", headers=header, data=json.dumps(DATA))
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


# No4.01.メイン処理_03.引数検証処理チェック処理　正常系　引数．リクエストボディ．PDSユーザ検索テキスト　文字列型である　６４桁である
def test_pds_user_search_case4_3_2(create_header):
    header = create_header["header"]
    DATA["pdsUser"] = "最大文字数テストＸＸＸＸＸＸＸＸＸＸＸＸＸＸＸＸＸＸＸＸＸＸＸＸＸＸＸＸＸＸＸＸＸＸＸＸＸＸＸＸＸＸＸＸＸＸＸＸＸＸＸＸＸＸＸＸ"
    DATA["fromDate"] = None
    DATA["toDate"] = None
    DATA["pdsUserStatus"] = True
    response = client.post("/api/2.0/pdsuser/search", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "pdsUserInfo": response.json()["pdsUserInfo"]
    }
    print(response.json())


# No4.01.メイン処理_03.引数検証処理チェック処理　追加
# PDSユーザ検索テキスト以外条件入力(PDSユーザ検索テキスト,PDSユーザ公開鍵有効期限From,PDSユーザ公開鍵有効期限To,PDSユーザ公開鍵有効状態)
def test_pds_user_search_case4_3_3(create_header):
    header = create_header["header"]
    DATA["pdsUser"] = None
    response = client.post("/api/2.0/pdsuser/search", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "pdsUserInfo": response.json()["pdsUserInfo"]
    }
    print(response.json())


# No4.01.メイン処理_03.引数検証処理チェック処理　異常系　引数．リクエストボディ．検索日From　１１桁である　入力規則違反している（形式は yyyy/MM/dd でない　hh:mmがhhh:mm）
# No5.01.メイン処理_04.共通エラーチェック処理　正常系　共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_search_case4_4_1(create_header):
    header = create_header["header"]
    DATA["fromDate"] = "2022/09/0"
    response = client.post("/api/2.0/pdsuser/search", headers=header, data=json.dumps(DATA))
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


# No4.01.メイン処理_03.引数検証処理チェック処理　正常系　引数．リクエストボディ．検索日From　１０桁である　入力規則違反していない（形式は yyyy/MM/dd である）　[0-9/]
def test_pds_user_search_case4_4_2(create_header):
    header = create_header["header"]
    DATA["pdsUser"] = None
    DATA["fromDate"] = "2022/09/01"
    DATA["toDate"] = None
    DATA["pdsUserStatus"] = True
    response = client.post("/api/2.0/pdsuser/search", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "pdsUserInfo": response.json()["pdsUserInfo"]
    }
    print(response.json())


# No4.01.メイン処理_03.引数検証処理チェック処理　追加
# PDSユーザ公開鍵有効期限From以外条件入力(PDSユーザ検索テキスト,PDSユーザ公開鍵有効期限From,PDSユーザ公開鍵有効期限To,PDSユーザ公開鍵有効状態)
def test_pds_user_search_case4_4_3(create_header):
    header = create_header["header"]
    DATA["fromDate"] = None
    response = client.post("/api/2.0/pdsuser/search", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "pdsUserInfo": response.json()["pdsUserInfo"]
    }
    print(response.json())


# No4.01.メイン処理_03.引数検証処理チェック処理　異常系　引数．リクエストボディ．検索日To　１１桁である　入力規則違反している（形式は yyyy/MM/dd でない　hh:mmがhhh:mm）
# No5.01.メイン処理_04.共通エラーチェック処理　正常系　共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_search_case4_5_1(create_header):
    header = create_header["header"]
    DATA["toDate"] = "2022/12/0"
    response = client.post("/api/2.0/pdsuser/search", headers=header, data=json.dumps(DATA))
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


# No4.01.メイン処理_03.引数検証処理チェック処理　正常系　引数．リクエストボディ．検索日To　１０桁である　入力規則違反していない（形式は yyyy/MM/dd である）　[0-9/]
def test_pds_user_search_case4_5_2(create_header):
    header = create_header["header"]
    DATA["pdsUser"] = None
    DATA["fromDate"] = None
    DATA["toDate"] = "2022/12/01"
    DATA["pdsUserStatus"] = True
    response = client.post("/api/2.0/pdsuser/search", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "pdsUserInfo": response.json()["pdsUserInfo"]
    }
    print(response.json())


# No4.01.メイン処理_03.引数検証処理チェック処理　追加
# PDSユーザ公開鍵有効期限To以外条件入力(PDSユーザ検索テキスト,PDSユーザ公開鍵有効期限From,PDSユーザ公開鍵有効期限To,PDSユーザ公開鍵有効状態)
def test_pds_user_search_case4_5_3(create_header):
    header = create_header["header"]
    DATA["toDate"] = None
    response = client.post("/api/2.0/pdsuser/search", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "pdsUserInfo": response.json()["pdsUserInfo"]
    }
    print(response.json())


# No4.01.メイン処理_03.引数検証処理チェック処理　異常系　引数．リクエストボディ．PDSユーザ公開鍵有効状態　論理型ではない
# No5.01.メイン処理_04.共通エラーチェック処理　正常系　共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_search_case4_6_1(create_header):
    header = create_header["header"]
    DATA["pdsUser"] = None
    DATA["fromDate"] = None
    DATA["toDate"] = None
    DATA["pdsUserStatus"] = "True"
    response = client.post("/api/2.0/pdsuser/search", headers=header, data=json.dumps(DATA))
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


# No4.01.メイン処理_03.引数検証処理チェック処理　正常系　引数．リクエストボディ．PDSユーザ公開鍵有効状態　論理型である
def test_pds_user_search_case4_6_2(create_header):
    header = create_header["header"]
    DATA["pdsUser"] = None
    DATA["fromDate"] = None
    DATA["toDate"] = None
    DATA["pdsUserStatus"] = True
    response = client.post("/api/2.0/pdsuser/search", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "pdsUserInfo": response.json()["pdsUserInfo"]
    }
    print(response.json())


# No4.01.メイン処理_03.引数検証処理チェック処理　追加
# PDSユーザ公開鍵有効状態以外条件入力(PDSユーザ検索テキスト,PDSユーザ公開鍵有効期限From,PDSユーザ公開鍵有効期限To,PDSユーザ公開鍵有効状態)
def test_pds_user_search_case4_6_3(create_header):
    header = create_header["header"]
    DATA["pdsUserStatus"] = None
    response = client.post("/api/2.0/pdsuser/search", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "pdsUserInfo": response.json()["pdsUserInfo"]
    }
    print(response.json())


# No4.01.メイン処理_03.引数検証処理チェック処理　異常系　引数．リクエストボディ．検索日Fromと、引数．リクエストボディ．検索日To　検索日Fromが検索日Toの値を超過している
# No5.01.メイン処理_04.共通エラーチェック処理　正常系　共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_search_case4_7_1(create_header):
    header = create_header["header"]
    DATA["fromDate"] = "2022/12/31"
    DATA["toDate"] = "2022/12/01"
    response = client.post("/api/2.0/pdsuser/search", headers=header, data=json.dumps(DATA))
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


# No4.01.メイン処理_03.引数検証処理チェック処理　正常系　引数．リクエストボディ．検索日Fromと、引数．リクエストボディ．検索日To　検索日Fromが検索日Toの値を超過していない
def test_pds_user_search_case4_7_2(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser/search", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "pdsUserInfo": response.json()["pdsUserInfo"]
    }
    print(response.json())


# No4.01.メイン処理_03.引数検証処理チェック処理　追加
# PDSユーザ公開鍵有効状態以外条件入力(PDSユーザ検索テキスト,PDSユーザ公開鍵有効期限From,PDSユーザ公開鍵有効期限To,PDSユーザ公開鍵有効状態)
def test_pds_user_search_case4_8(create_header):
    header = create_header["header"]
    DATA["pdsUser"] = None
    DATA["fromDate"] = None
    DATA["toDate"] = None
    DATA["pdsUserStatus"] = None
    response = client.post("/api/2.0/pdsuser/search", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "pdsUserInfo": response.json()["pdsUserInfo"]
    }
    print(response.json())


# No6.01.メイン処理_05.DB接続準備処理　異常系　接続に失敗する　設定値を異常な値に変更する
def test_pds_user_search_case6(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.commonUtil.CommonUtilClass.get_secret_info").return_value = {"host": "test", "port": "test", "username": "test", "password": "test"}
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser/search", headers=header, data=json.dumps(DATA))
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
    print(response)


# No8.01.メイン処理_06.PDSユーザ検索処理　異常系　PDSユーザ検索処理が失敗する
def test_pds_user_search_case8(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "PDS_USER_SEARCH_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser/search", headers=header, data=json.dumps(DATA))
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
    print(response)


# No13.01.メイン処理_09.アクセストークン発行処理　異常系　アクセストークン発行処理が失敗する
# No15.01.メイン処理_10.共通エラーチェック処理　異常系　共通エラーチェック処理が成功（エラー情報有り）
# No16.01.メイン処理_11.終了処理　正常系　変数．エラー情報がある(No.15でエラー）
def test_pds_user_search_case13(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "ACCESS_TOKEN_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser/search", headers=header, data=json.dumps(DATA))
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
    print(response)


# No18.01.メイン処理_06.PDSユーザ検索処理　正常系　PDSユーザ検索処理が成功する　0件の場合
def test_pds_user_search_case18(create_header):
    header = create_header["header"]
    DATA["pdsUser"] = "C0000000"
    response = client.post("/api/2.0/pdsuser/search", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "pdsUserInfo": response.json()["pdsUserInfo"]
    }
    print(response.json())
