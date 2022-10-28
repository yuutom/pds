from fastapi.testclient import TestClient
from app import app
from fastapi import Request
import pytest
import json
from pytest_mock.plugin import MockerFixture
from util.tokenUtil import TokenUtilClass
import util.logUtil as logUtil
from const.sqlConst import SqlConstClass
from const.systemConst import SystemConstClass
import routers.public.tokenRouter as tokenRouter

client = TestClient(app)
EXEC_NAME: str = "create"

BEARER = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0Zk9wZXJhdG9ySWQiOiJsLXRlc3QiLCJ0Zk9wZXJhdG9yTmFtZSI6Ilx1MzBlZFx1MzBiMFx1MzBhNFx1MzBmM1x1MzBjNlx1MzBiOVx1MzBjOCIsInRmT3BlcmF0b3JQYXNzd29yZFJlc2V0RmxnIjpmYWxzZSwiYWNjZXNzVG9rZW4iOiJiZGE4ZGY3OThiYzViZGZhMWZkODIyNmRiYmQ0OTMyMTY5ZmY5MjAzNWM0YzFlY2FjZjY2OGUyYzk2ZjAwZThlZTUxNTBiNGM0NTc0NjlkN2I4YmY1NzIxZDZlM2NiNzFiY2RiYzA3ODRiYzcyZWVlNjk1OGE3NTBiMWJkMWEzZWFmZWQ0OWFhNWU0ODZjYzQyZmM3OWNhMWY3MGQzZmM3Yzc0YzE5NjM3ODUzMjRhZDRhNGM0NjkxOGE4NjQ1N2ZiODE3NDU1MCIsImV4cCI6MTY2MTc0NjY3MX0.LCRjPEqKMkRQ_phaYnO7S7pd3SU_rgon-wsX14DBsPA"
ACCESS_TOKEN = "bda8df798bc5bdfa1fd8226dbbd4932169ff92035c4c1ecacf668e2c96f00e8ee5150b4c457469d7b8bf5721d6e3cb71bcdbc0784bc72eee6958a750b1bd1a3eafed49aa5e486cc42fc79ca1f70d3fc7c74c1963785324ad4a4c46918a86457fb8174550"
HEADER = {"pdsUserId": "C6100001", "Content-Type": "application/json", "timeStamp": "2022/10/21 21:35:07.000", "accessToken": ACCESS_TOKEN, "Authorization": "Bearer " + BEARER}
DATA = {
    "code1": "KgYq4xgtEEIAZd63Ru+/bmTyy74p4hWDF1fh916pEmOqDyReb1CMrz63VCckH+oqLFF4/6gVNvw8mAg0Xvesjx5QY6baej7dD0kCF5LOsYPnMhtdLm7t94DuiLtXWbImf9gKFZvCO85Nuap8c6nUQgaPFhfzkRzk+3b0gRTb7y0hq3HKEUms+HRH8d4/dTbbphV97XRjrSwa8tY3VsZM9srP5ik7yO/DHr9TxjVREqiNJRTQFVWi+eCHaRsPw1YASlx7qAEXBURmud7yPFtFGYE/i65+LlLWVLUIP0eNI8LHP/fdxgwSIMra8oaCekW8hc3agVwfcdfK27K9LA7hpNeTv1JTfOyjSr473GxJP8ZEgPC+LkHEYo5oduWmJnYTYpPDg85PmqwVrPWhmDKlNfl4XDdSuvW30EyOc2t9aAW9pt7Py6x0iTsOAgNOAc6ZlNeW0IVbq7+LgiBGE4m+Rr/s5UWRxfMrPgPBkvqRuTWq5nEwHA/C4jz1uNQrjhMyG65x7n2dmFwhiVF0A5jSGrwXZdIZVY6zAHXGaTDRy7R4D794jc/fpDErhEMZPlR/s/kh8hfqRjMIOMpYZT8DS98Ix+d+xXJCeY6DIdBvcC+ABznj++ne3uIenpI0hSH4BLBByCdwyUchJHQ4TPPqICvMYxx0GZiQgN66aIevOaU=",
    "code2": "N8K720emm7sGJDIt+dmYDVJqo/yNvz1jh7XFHi8G64P3EmFzZm5CiuTtn714/cpf0FXEaJcI1vgzWBRDK1JQSm+5u9H4x+THt+ibFeRvgZZ7iRXU4pChq0HrrRiBDnN9+3vIcEHuVuiD3m1783K4cTb4P8Lt89j5qkvW8k6U6f0/htON4bF77A1Eqr7QRB7L+la08S/ljCKK3RoOAJ2I0rR3pCn9pkmw2l+FNfHsPKq1gnJ2ni0UHB/5S3W1MjNC9Yfc3gJTVGqRPjO5RXM6lQJKvROj8H3xzGADc0NW6U06f6xPdvjp6//4Nriq8wIvlwuhaTO2rjw8NHsoZoNgeSY0xEF8cRheC6qLna/zucv5r5IqM4l5Rz7MQhuGfwK78CgTJL6yjulBXJJSmTO2giP0w2XQm/gmHV9b6kif1xJP8tv75ofJgQaP56l6hiE7BRlYahTxxun42c6EvJ30EkNrTL+8NrEnhFPudveDpCfF6Oct+X9dnOcXawRKCdJQec9tOJDa5GGB3LLJED4v7jHlgJbhQ6nj4YipQPA1vH/RLYcYJBhJsiX4v263Kx2JMrlUmDBKku3GmL/xWBJbCtok1csC5Ivutsg9MffQCFZQ6U88piWbGTqWqHftaCFCDptxqq5X9jwjdQKXwvXxOf3hlxSdMw5W7cVfDqV3lHg="
}


@pytest.fixture
def create_header():
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    yield {"header": {"pdsUserId": "C6100001", "Content-Type": "application/json", "timeStamp": "2022/10/21 21:35:07.000", "Authorization": "Bearer " + "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0Zk9wZXJhdG9ySWQiOiJsLXRlc3QiLCJ0Zk9wZXJhdG9yTmFtZSI6Ilx1MzBlZFx1MzBiMFx1MzBhNFx1MzBmM1x1MzBjNlx1MzBiOVx1MzBjOCIsInRmT3BlcmF0b3JQYXNzd29yZFJlc2V0RmxnIjpmYWxzZSwiYWNjZXNzVG9rZW4iOiJmZWJhZGZjZjM1ODMzNTg5ODZkYmZmOTNkOGNiMmQwZDMwNjM3YjkyZjIyYTM0MTU5ZjM0MTAzNGNmNGRjN2NmZmNlODVjNmRjOGM2N2I4NjJmMzgwZmY2OTcwN2I1MTI3NmVkZTUzY2MxYTkzMmY0YjNjMjJhZTE5ZWRjODQ1MTg5ZjM3YzgwZTZlZjljYmI1ZWQ2ZTg2ODRhOTJkZDU1YWZmNjM0YmI3MGYwYjFiZjYyZDE1OWY0OGJkZDBlY2JhNGE4YzA5YiIsImV4cCI6MTY2MTk0OTI5M30.kjjbHSRFVDhBts19bT8fJViJzA29bk-o8T0pMGboSUs"}}


# No1.PDSユーザドメイン検証処理が失敗する
def test_token_case1(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.commonUtil.CommonUtilClass.check_pds_user_domain").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
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


# No2.PDSユーザドメイン検証処理が成功する
def test_token_case2(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No3.共通エラーチェック処理が成功（エラー情報有り）
def test_token_case3(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.commonUtil.CommonUtilClass.check_pds_user_domain").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
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


# No4.パラメータ検証処理が失敗する
def test_token_case4(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("routers.public.tokenRouter.input_check").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
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


# No5.パラメータ検証処理が成功する
def test_token_case5(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No6.共通エラーチェック処理が成功する（エラー情報有り）
def test_token_case6(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("routers.public.tokenRouter.input_check").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
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


# 05.DB接続準備処理
# No7.接続に失敗する
# 設定値を異常な値に変更する
def test_token_case7(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.commonUtil.CommonUtilClass.get_secret_info").return_value = {"host": "test", "port": "test", "username": "test", "password": "test"}
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
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
def test_token_case8(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 06.PDSユーザPDSユーザ公開鍵情報取得処理
# No9.PDSユーザPDSユーザ公開鍵情報取得処理が失敗する
def test_token_case9(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "PDS_USER_PDS_USER_PUBLIC_KEY_TOKEN_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
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


# No10.PDSユーザPDSユーザ公開鍵情報取得処理が成功する
def test_token_case10(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 07.共通エラーチェック処理
# No11.共通エラーチェック処理が成功する（エラー情報有り）
def test_token_case11(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "PDS_USER_PDS_USER_PUBLIC_KEY_TOKEN_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
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


# 08.アクセストークン検証フラグ作成処理
# No12.「変数．アクセストークン検証フラグ」を初期化する
def test_token_case12(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 変数．PDSユーザPDSユーザ公開鍵取得結果の要素数分繰り返す
# No13.変数．PDSユーザPDSユーザ公開鍵取得結果の要素数が0件の場合
def test_token_case13(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.postgresDbUtil.PostgresDbUtilClass.select_tuple_list").return_value = {"result": True, "rowcount": 0, "query_results": []}
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "990001",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No14.変数．PDSユーザPDSユーザ公開鍵取得結果の要素数が1件以上の場合
def test_token_case14(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 09.暗号化文字列２復号化処理
# No15.復号化する
def test_token_case15(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 10.暗号化文字列２復号化チェック処理
# No16.「変数．暗号化文字列２復号化処理実行結果」とリクエストのリクエストボディ．暗号化文字列１が一致しない場合、繰り返し
def test_token_case16(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No17.「変数．暗号化文字列２復号化処理実行結果」とリクエストのリクエストボディ．暗号化文字列１が一致する場合、「10.暗号化文字列１復号化処理」に遷移する
def test_token_case17(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 11.暗号化文字列１復号化処理
# No18.暗号化文字列１復号化処理が失敗する
def test_token_case18(mocker: MockerFixture, create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "990001",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No19.復号化した結果のAPIKeyと「変数．PDSユーザPDSユーザ公開鍵取得結果リスト[変数．PDSユーザ公開鍵ループ数][0]」が一致しない
def test_token_case19(mocker: MockerFixture, create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
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


# No20.復号化した結果のタイムスタンプとヘッダパラメータのタイムスタンプが誤差 (1000ミリ秒) を超えている
def test_token_case20(mocker: MockerFixture, create_header):
    # Exception
    header = create_header["header"]
    header["timeStamp"] = "2023/10/21 21:35:09.300"
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
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


# No21.暗号化文字列１復号化処理が成功する
def test_token_case21(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 12.共通エラーチェック処理
# No22.共通エラーチェック処理が成功する（エラー情報有り）
def test_token_case22(mocker: MockerFixture, create_header):
    # Exception
    header = create_header["header"]
    header["timeStamp"] = "2023/10/21 21:35:09.300"
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
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


# 13.アクセストークン検証フラグ更新処理
# No23.「変数．アクセストークン検証フラグ」をtrueで更新する
def test_token_case23(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 14.アクセストークン検証フラグ確認処理
# No24.「変数．アクセストークン検証フラグ」がfalseの場合、「変数．エラー情報」を作成し、エラーログをCloudWatchにログ出力する
def test_token_case24(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.postgresDbUtil.PostgresDbUtilClass.select_tuple_list").return_value = {"result": True, "rowcount": 0, "query_results": []}
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "990001",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# 15.共通エラーチェック処理
# No25.共通エラーチェック処理が成功する（エラー情報有り）
def test_token_case25(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.postgresDbUtil.PostgresDbUtilClass.select_tuple_list").return_value = {"result": True, "rowcount": 0, "query_results": []}
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "990001",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# 16.API実行履歴登録処理
# No26.API実行履歴登録処理が失敗する
def test_token_case26(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.commonUtil.CommonUtilClass.insert_api_history").side_effect = Exception('testException')
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
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


# No27.API実行履歴登録処理が成功する
def test_token_case27(mocker: MockerFixture, create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
    }
    print(response.json())


# 17.共通エラーチェック処理
# No28.共通エラーチェック処理が成功（エラー情報有り）
def test_token_case28(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.commonUtil.CommonUtilClass.insert_api_history").side_effect = Exception('testException')
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
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


# 18.アクセストークン発行処理
# No29.アクセストークン発行処理が失敗する
def test_token_case29(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.tokenUtil.TokenUtilClass.create_token_public").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
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


# No30.アクセストークン発行処理が成功する
def test_token_case30(mocker: MockerFixture, create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
    }
    print(response.json())


# No31.共通エラーチェック処理が成功（エラー情報有り）
def test_token_case31(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.tokenUtil.TokenUtilClass.create_token_public").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
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


# 20.終了処理
# No32.終了処理
def test_token_case32(mocker: MockerFixture, create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
    }
    print(response.json())


# 21.引数検証処理
# No33-1.PDSユーザドメイン名 値が設定されていない（空値）
def test_token_case33_1(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    response = client.post("/api/2.0//token", headers=header, data=json.dumps(DATA))
    assert response.status_code == 404
    print(response.json())

    # 入力チェックを直接呼び出してエラーになることを確認
    request_body = tokenRouter.requestBody(code1=DATA["code1"], code2=DATA["code2"])
    response = tokenRouter.input_check(
        trace_logger,
        None,
        request_body,
        header["pdsUserId"],
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


# No33-2.PDSユーザドメイン名 文字列型以外、21文字
# パスパラメータはURLで絶対に文字列になるので型チェックできない
def test_token_case33_2(create_header):
    # PDSユーザドメイン名に誤りがある場合には、PDSユーザドメイン検証でエラーになってしまうので入力チェックまで到達できないことを確認
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    response = client.post("/api/2.0/[012345678901, 23456]/token", headers=header, data=json.dumps(DATA))
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

    # PDSユーザドメイン名に誤りがある場合には、PDSユーザドメイン検証でエラーになってしまうので入力チェックまで到達できないことを確認
    # 入力チェックを直接呼び出してエラーになることを確認
    request_body = tokenRouter.requestBody(code1=DATA["code1"], code2=DATA["code2"])
    response = tokenRouter.input_check(
        trace_logger,
        123456789012345678901,
        request_body,
        header["pdsUserId"],
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
            },
        ]
    }
    print(response)


# No33-3.PDSユーザドメイン名 文字列型、4文字、全角を含む
# パスパラメータはURLで絶対に文字列になるので型チェックできない
def test_token_case33_3(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    response = client.post("/api/2.0/あ123/token", headers=header, data=json.dumps(DATA))
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

    # PDSユーザドメイン名に誤りがある場合には、PDSユーザドメイン検証でエラーになってしまうので入力チェックまで到達できないことを確認
    # 入力チェックを直接呼び出してエラーになることを確認
    request_body = tokenRouter.requestBody(code1=DATA["code1"], code2=DATA["code2"])
    response = tokenRouter.input_check(
        trace_logger,
        "あ123",
        request_body,
        header["pdsUserId"],
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


# No33-4.PDSユーザドメイン名 文字列型、5文字、入力規則違反していない（URL利用可能文字のみの半角小英数記号５桁）
def test_token_case33_4(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/c0123/token", headers=header, data=json.dumps(DATA))
    print(response)


# No33-5.PDSユーザドメイン名 文字列型、20文字、入力規則違反していない（URL利用可能文字のみの半角小英数記号20桁）
def test_token_case33_5(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/c0123456789012345678/token", headers=header, data=json.dumps(DATA))
    print(response)


# No33-6.PDSユーザID 値が設定されていない（空値）
def test_token_case33_6(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["pdsUserId"] = None
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
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

    # PDSユーザIDに誤りがある場合には、PDSユーザドメイン検証でエラーになってしまうので入力チェックまで到達できないことを確認
    request_body = tokenRouter.requestBody(code1=DATA["code1"], code2=DATA["code2"])
    response = tokenRouter.input_check(
        trace_logger,
        "pds-user-create",
        request_body,
        header["pdsUserId"],
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


# No33-7.PDSユーザID 文字列型以外、7桁、C以外の文字で始まる
def test_token_case33_7(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["pdsUserId"] = '1234567'
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
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

    # PDSユーザIDに誤りがある場合には、PDSユーザドメイン検証でエラーになってしまうので入力チェックまで到達できないことを確認
    request_body = tokenRouter.requestBody(code1=DATA["code1"], code2=DATA["code2"])
    response = tokenRouter.input_check(
        trace_logger,
        "pds-user-create",
        request_body,
        int(header["pdsUserId"]),
        header["timeStamp"],
        {
            "result": True,
            "pdsUserInfo": {"pdsUserId": int(header["pdsUserId"])}
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


# No33-8.PDSユーザID 文字列型、8桁、入力規則違反していない（C＋数値7桁）
def test_token_case33_8(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No33-9.タイムスタンプ 値が設定されていない（空値）
def test_token_case33_9(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["timeStamp"] = None
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
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


# No33-10.タイムスタンプ 文字列型以外、22桁
def test_token_case33_10(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["timeStamp"] = '1234567890123456789012'
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
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

    # ヘッダパラメータは文字列型以外を許容しないので、入力チェックを直接呼び出してエラーになることを確認
    request_body = tokenRouter.requestBody(code1=DATA["code1"], code2=DATA["code2"])
    response = tokenRouter.input_check(
        trace_logger,
        "pds-user-create",
        request_body,
        header["pdsUserId"],
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


# No33-11.タイムスタンプ 文字列型、24桁、入力規則違反している　hh:mmがhhh:mm
def test_token_case33_11(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["timeStamp"] = '2022/09/30 12:000:00.000'
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
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


# No33-12.暗号化文字列1 値が設定されていない（空値）
def test_token_case33_12(create_header):
    header = create_header["header"]
    DATA["code1"] = ""
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
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


# No33-13.暗号化文字列1 文字列型以外、2053桁
def test_token_case33_13(create_header):
    header = create_header["header"]
    DATA["code1"] = int("1" * 2053)
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020019",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020002",
                "message": response.json()["errorInfo"][1]["message"]
            }
        ]
    }
    print(response.json())


# No33-14.暗号化文字列1 文字列型以外、683桁
def test_token_case33_14(create_header):
    header = create_header["header"]
    DATA["code1"] = int("1" * 683)
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020019",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020016",
                "message": response.json()["errorInfo"][1]["message"]
            }
        ]
    }
    print(response.json())


# No33-15.暗号化文字列1 文字列型、684桁
def test_token_case33_15(create_header):
    header = create_header["header"]
    DATA["code1"] = "1" * 684
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
    print(response)


# No33-16.暗号化文字列1 文字列型、2052桁
def test_token_case33_16(create_header):
    header = create_header["header"]
    DATA["code1"] = "1" * 2052
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
    print(response)


# No33-17.暗号化文字列2 値が設定されていない（空値）
def test_token_case33_17(create_header):
    header = create_header["header"]
    DATA["code2"] = ""
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
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


# No33-18.暗号化文字列2 文字列型以外、2053桁
def test_token_case33_18(create_header):
    header = create_header["header"]
    DATA["code2"] = int("1" * 2053)
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020019",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020002",
                "message": response.json()["errorInfo"][1]["message"]
            }
        ]
    }
    print(response.json())


# No33-19.暗号化文字列2 文字列型以外、683桁
def test_token_case33_19(create_header):
    header = create_header["header"]
    DATA["code2"] = int("1" * 683)
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020019",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020016",
                "message": response.json()["errorInfo"][1]["message"]
            }
        ]
    }
    print(response.json())


# No33-20.暗号化文字列2 文字列型、684桁
def test_token_case33_20(create_header):
    header = create_header["header"]
    DATA["code2"] = "1" * 684
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
    print(response)


# No33-21.暗号化文字列2 文字列型、2052桁
def test_token_case33_21(create_header):
    header = create_header["header"]
    DATA["code2"] = "1" * 2052
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
    print(response)


# No33-22.「引数．ヘッダパラメータ．PDSユーザID」と「引数．PDSユーザドメイン情報．PDSユーザID」の値が一致しない場合、「変数．エラー情報リスト」にエラー情報を追加する
def test_token_case33_22(mocker: MockerFixture, create_header):
    # 返却値の変更
    mocker.patch("util.commonUtil.CommonUtilClass.check_pds_user_domain").return_value = {"result": True, "pdsUserInfo": {"pdsUserId": "C1234567"}}
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["pdsUserId"] = 'C9876543'
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
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


# No33-23.「引数．ヘッダパラメータ．PDSユーザID」と「引数．PDSユーザドメイン情報．PDSユーザID」の値が一致する
def test_token_case33_23(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser-create2/token", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())
