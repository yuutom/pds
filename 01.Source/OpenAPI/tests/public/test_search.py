import random
import string
from fastapi.testclient import TestClient
from app import app
from fastapi import Request
import pytest
from pytest_mock.plugin import MockerFixture
from util.tokenUtil import TokenUtilClass
import util.logUtil as logUtil
import json
from const.systemConst import SystemConstClass
import routers.public.searchRouter as searchRouter
from routers.public.searchRouter import requestBody

client = TestClient(app)
EXEC_NAME: str = "search"

BEARER = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0Zk9wZXJhdG9ySWQiOiJsLXRlc3QiLCJ0Zk9wZXJhdG9yTmFtZSI6Ilx1MzBlZFx1MzBiMFx1MzBhNFx1MzBmM1x1MzBjNlx1MzBiOVx1MzBjOCIsInRmT3BlcmF0b3JQYXNzd29yZFJlc2V0RmxnIjpmYWxzZSwiYWNjZXNzVG9rZW4iOiJiZGE4ZGY3OThiYzViZGZhMWZkODIyNmRiYmQ0OTMyMTY5ZmY5MjAzNWM0YzFlY2FjZjY2OGUyYzk2ZjAwZThlZTUxNTBiNGM0NTc0NjlkN2I4YmY1NzIxZDZlM2NiNzFiY2RiYzA3ODRiYzcyZWVlNjk1OGE3NTBiMWJkMWEzZWFmZWQ0OWFhNWU0ODZjYzQyZmM3OWNhMWY3MGQzZmM3Yzc0YzE5NjM3ODUzMjRhZDRhNGM0NjkxOGE4NjQ1N2ZiODE3NDU1MCIsImV4cCI6MTY2MTc0NjY3MX0.LCRjPEqKMkRQ_phaYnO7S7pd3SU_rgon-wsX14DBsPA"
ACCESS_TOKEN = "bda8df798bc5bdfa1fd8226dbbd4932169ff92035c4c1ecacf668e2c96f00e8ee5150b4c457469d7b8bf5721d6e3cb71bcdbc0784bc72eee6958a750b1bd1a3eafed49aa5e486cc42fc79ca1f70d3fc7c74c1963785324ad4a4c46918a86457fb8174550"
HEADER = {"pdsUserId": "C9876543", "Content-Type": "application/json", "timeStamp": "2022/08/23 15:12:01.690", "accessToken": ACCESS_TOKEN, "Authorization": "Bearer " + BEARER}
DATA = {
    "userIdMatchMode": "前方一致",
    "userIdStr": "C0123456",
    "dataJson": "data.name.first",
    "dataMatchMode": "前方一致",
    "dataStr": "taro",
    "imageHash": "glakjgirhul",
    "fromDate": "2023/01/01",
    "toDate": "2023/12/31"
}

REQUEST_BODY = requestBody(
    userIdMatchMode=DATA["userIdMatchMode"],
    userIdStr=DATA["userIdStr"],
    dataJson=DATA["dataJson"],
    dataMatchMode=DATA["dataMatchMode"],
    dataStr=DATA["dataStr"],
    imageHash=DATA["imageHash"],
    fromDate=DATA["fromDate"],
    toDate=DATA["toDate"]
)


@pytest.fixture
def create_header():
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_public(pdsUserId="C9876543", pdsUserName="PDSユーザ登録テスト", accessToken=None)
    print("accessToken:" + token_result["accessToken"])
    yield {"header": {"pdsUserId": "C9876543", "Content-Type": "application/json", "timeStamp": "2022/08/23 15:12:01.690", "accessToken": token_result["accessToken"], "Authorization": "Bearer " + token_result["jwt"]}}


# No1.事前処理が失敗する
def test_search_case1(mocker: MockerFixture, create_header):
    mocker.patch("util.commonUtil.CommonUtilClass.check_pds_user_domain").side_effect = Exception('testException')
    header = create_header["header"]
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(DATA))
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


# No2.事前処理が成功する
def test_search_case2(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "maxPage": response.json()["maxPage"],
        "maxCount": response.json()["maxCount"],
        "pageNo": response.json()["pageNo"],
        "tidList": response.json()["tidList"]
    }
    print(response.json())


# No3.検索条件作成処理が成功する
def test_search_case3(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "maxPage": response.json()["maxPage"],
        "maxCount": response.json()["maxCount"],
        "pageNo": response.json()["pageNo"],
        "tidList": response.json()["tidList"]
    }
    print(response.json())


# No4.tidリスト作成処理が失敗する
def test_search_case4(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.commonUtil.CommonUtilClass.mongodb_search").side_effect = Exception('testException')
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(DATA))
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


# No5.tidリスト作成処理が成功する
def test_search_case5(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "maxPage": response.json()["maxPage"],
        "maxCount": response.json()["maxCount"],
        "pageNo": response.json()["pageNo"],
        "tidList": response.json()["tidList"]
    }
    print(response.json())


# No6.共通エラーチェック処理が成功する（エラー情報有り）
def test_search_case6(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.commonUtil.CommonUtilClass.mongodb_search").side_effect = Exception('testException')
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(DATA))
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


# No7.返却項目成形処理が成功する（１０００件以上、２０００件未満）
# ヘッダパラメータ．ページNo.の指定なし
def test_search_case7(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["userIdStr"] = None
    data_copy["dataJson"] = None
    data_copy["dataStr"] = None
    response = client.post("/api/2.0/pds-user-create/transaction/search/", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "maxPage": response.json()["maxPage"],
        "maxCount": response.json()["maxCount"],
        "pageNo": response.json()["pageNo"],
        "tidList": response.json()["tidList"]
    }
    print(response.json())


# No8.返却項目成形処理が成功する（１０００件以上、２０００件未満）
# ヘッダパラメータ．ページNo.が１の場合
def test_search_case8(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["userIdStr"] = None
    data_copy["dataJson"] = None
    data_copy["dataStr"] = None
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "maxPage": response.json()["maxPage"],
        "maxCount": response.json()["maxCount"],
        "pageNo": response.json()["pageNo"],
        "tidList": response.json()["tidList"]
    }
    print(response.json())


# No9.返却項目成形処理が成功する（１０００件以上、２０００件未満）
# ヘッダパラメータ．ページNo.が２の場合
def test_search_case9(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["userIdStr"] = None
    data_copy["dataJson"] = None
    data_copy["dataStr"] = None
    response = client.post("/api/2.0/pds-user-create/transaction/search/2", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "maxPage": response.json()["maxPage"],
        "maxCount": response.json()["maxCount"],
        "pageNo": response.json()["pageNo"],
        "tidList": response.json()["tidList"]
    }
    print(response.json())


# No10.返却項目成形処理が成功する（１０００件以上、２０００件未満）
# ヘッダパラメータ．ページNo.が３の場合
def test_search_case10(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["userIdStr"] = None
    data_copy["dataJson"] = None
    data_copy["dataStr"] = None
    response = client.post("/api/2.0/pds-user-create/transaction/search/3", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "maxPage": response.json()["maxPage"],
        "maxCount": response.json()["maxCount"],
        "pageNo": response.json()["pageNo"],
        "tidList": response.json()["tidList"]
    }
    print(response.json())


# No11.返却項目成形処理が成功する（取得データなし）
def test_search_case11(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["userIdStr"] = "C987654321"
    data_copy["dataJson"] = None
    data_copy["dataStr"] = None
    response = client.post("/api/2.0/pds-user-create/transaction/search/2", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "maxPage": response.json()["maxPage"],
        "maxCount": response.json()["maxCount"],
        "pageNo": response.json()["pageNo"],
        "tidList": response.json()["tidList"]
    }
    print(response.json())


# No12.アクセストークン発行処理が失敗する
def test_search_case12(mocker: MockerFixture, create_header):
    header = create_header["header"]
    # Exception
    mocker.patch("util.tokenUtil.TokenUtilClass.create_token_public").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    # ErrorInfo
    # mocker.patch("util.commonUtil.CommonUtilClass.insert_api_history").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test Exception"}}
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(DATA))
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


# No13.アクセストークン発行処理が成功する
def test_search_case13(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "maxPage": response.json()["maxPage"],
        "maxCount": response.json()["maxCount"],
        "pageNo": response.json()["pageNo"],
        "tidList": response.json()["tidList"]
    }
    print(response.json())


# No14.共通エラーチェック処理が成功する（エラー情報有り）
def test_search_case14(mocker: MockerFixture, create_header):
    header = create_header["header"]
    # Exception
    mocker.patch("util.tokenUtil.TokenUtilClass.create_token_public").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    # ErrorInfo
    # mocker.patch("util.commonUtil.CommonUtilClass.insert_api_history").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test Exception"}}
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(DATA))
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


# No15.API実行履歴登録処理が失敗する
def test_search_case15(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.commonUtil.get_datetime_str_no_symbol").side_effect = ["20220927145527512", "20220101000000000"]
    mocker.patch("util.commonUtil.get_random_ascii").side_effect = ["O1MOs01uEKinK", ''.join(random.choices(string.ascii_letters + string.digits, k=13))]
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "030001",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No16.API実行履歴登録処理が成功する
def test_search_case16(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "maxPage": response.json()["maxPage"],
        "maxCount": response.json()["maxCount"],
        "pageNo": response.json()["pageNo"],
        "tidList": response.json()["tidList"]
    }
    print(response.json())


# No17.終了処理 返却パラメータを作成し返却する
def test_search_case17(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "maxPage": response.json()["maxPage"],
        "maxCount": response.json()["maxCount"],
        "pageNo": response.json()["pageNo"],
        "tidList": response.json()["tidList"]
    }
    print(response.json())


# No18.総合テスト
# リクエストのリクエストボディ．保存データJsonキー情報」がNull以外の場合
# 事前処理が成功する
# tidリスト作成処理が成功する
# API実行履歴登録処理が成功する
# アクセストークン発行処理が成功する
# 返却パラメータを作成し返却する
def test_search_case18(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "maxPage": response.json()["maxPage"],
        "maxCount": response.json()["maxCount"],
        "pageNo": response.json()["pageNo"],
        "tidList": response.json()["tidList"]
    }
    print(response.json())


# No19.総合テスト
# リクエストのリクエストボディ．保存データJsonキー情報」がNullの場合
# 事前処理が成功する
# tidリスト作成処理が成功する
# API実行履歴登録処理が成功する
# アクセストークン発行処理が成功する
# 返却パラメータを作成し返却する
def test_search_case19(create_header):
    header = create_header["header"]
    data_copy = DATA
    data_copy["dataJson"] = None
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "maxPage": response.json()["maxPage"],
        "maxCount": response.json()["maxCount"],
        "pageNo": response.json()["pageNo"],
        "tidList": response.json()["tidList"]
    }
    print(response.json())


# No20.PDSユーザドメイン検証処理が失敗する
def test_search_case20(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA
    mocker.patch("util.commonUtil.CommonUtilClass.check_pds_user_domain").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
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


# No21.PDSユーザドメイン検証処理が成功する
def test_search_case21(create_header):
    header = create_header["header"]
    data_copy = DATA
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "maxPage": response.json()["maxPage"],
        "maxCount": response.json()["maxCount"],
        "pageNo": response.json()["pageNo"],
        "tidList": response.json()["tidList"]
    }
    print(response.json())


# No22.共通エラーチェック処理が成功（エラー情報有り）
def test_search_case22(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA
    mocker.patch("util.commonUtil.CommonUtilClass.check_pds_user_domain").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
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


# No23.アクセストークン検証処理が失敗する
def test_search_case23(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA
    mocker.patch("util.tokenUtil.TokenUtilClass.verify_token_public").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
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


# No24.アクセストークン検証処理が成功する
def test_search_case24(create_header):
    header = create_header["header"]
    data_copy = DATA
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "maxPage": response.json()["maxPage"],
        "maxCount": response.json()["maxCount"],
        "pageNo": response.json()["pageNo"],
        "tidList": response.json()["tidList"]
    }
    print(response.json())


# No25.アクセストークン検証処理が失敗する
def test_search_case25(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA
    mocker.patch("util.tokenUtil.TokenUtilClass.verify_token_public").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
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


# No26-1.ページNo 文字列型ではない
def test_search_case26_1(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA
    # URLは必ず文字列になってしまうので検証できないため直接呼び出し
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "maxPage": response.json()["maxPage"],
        "maxCount": response.json()["maxCount"],
        "pageNo": response.json()["pageNo"],
        "tidList": response.json()["tidList"]
    }
    print(response.json())

    # 入力チェックを直接呼び出してエラーになることを確認
    response = searchRouter.input_check(
        trace_logger,
        1,
        "pds-user-create",
        REQUEST_BODY,
        header["pdsUserId"],
        header["accessToken"],
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
            }
        ]
    }
    print(response)


# No26-2.ページNo 文字列型、入力可能文字以外を含む（半角英）
def test_search_case26_2(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA
    # URLは必ず文字列になってしまうので検証できないため直接呼び出し
    response = client.post("/api/2.0/pds-user-create/transaction/search/a", headers=header, data=json.dumps(data_copy))
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


# No26-3.ページNo 文字列型、入力可能文字のみ（半角数字） [0-9]
def test_search_case26_3(create_header):
    header = create_header["header"]
    data_copy = DATA
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "maxPage": response.json()["maxPage"],
        "maxCount": response.json()["maxCount"],
        "pageNo": response.json()["pageNo"],
        "tidList": response.json()["tidList"]
    }
    print(response.json())


# No26-4.PDSユーザドメイン名 値が設定されていない（空値）
def test_search_case26_4(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA
    response = client.post("/api/2.0//transaction/search/1", headers=header, data=json.dumps(data_copy))
    # パスパラメータを空にするとURLが不正になるので確認不可であることを確認
    assert response.status_code == 404
    print(response.json())

    # 入力チェックを直接呼び出してエラーになることを確認
    response = searchRouter.input_check(
        trace_logger,
        "1",
        None,
        REQUEST_BODY,
        header["pdsUserId"],
        header["accessToken"],
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


# No26-2.PDSユーザドメイン名 文字列型以外、21文字
# パスパラメータはURLで絶対に文字列になるので型チェックできない
def test_search_case26_5(create_header):
    # PDSユーザドメイン名に誤りがある場合には、PDSユーザドメイン検証でエラーになってしまうので入力チェックまで到達できないことを確認
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    data_copy = DATA
    header = create_header["header"]
    response = client.post("/api/2.0/[012345678901, 23456]/transaction/search/1", headers=header, data=json.dumps(data_copy))
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
    response = searchRouter.input_check(
        trace_logger,
        "1",
        [123456789012, 23456],
        REQUEST_BODY,
        header["pdsUserId"],
        header["accessToken"],
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


# No26-3.PDSユーザドメイン名 文字列型、4文字、全角を含む
def test_search_case26_6(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    data_copy = DATA
    header = create_header["header"]
    response = client.post("/api/2.0/あ123/transaction/search/1", headers=header, data=json.dumps(data_copy))
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
    response = searchRouter.input_check(
        trace_logger,
        "1",
        "あ123",
        REQUEST_BODY,
        header["pdsUserId"],
        header["accessToken"],
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


# No26-7.PDSユーザドメイン名 文字列型、5文字、入力規則違反していない（URL利用可能文字のみの半角小英数記号５桁）
def test_search_case26_7():
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_public(pdsUserId="C8000000", pdsUserName="PDSユーザドメイン検証成功テスト", accessToken=None)
    data_copy = DATA
    print("accessToken:" + token_result["accessToken"])
    header = {"pdsUserId": "C8000000", "Content-Type": "application/json", "timeStamp": "2022/08/23 15:12:01.690", "accessToken": token_result["accessToken"], "Authorization": "Bearer " + token_result["jwt"]}

    response = client.post("/api/2.0/c0123/transaction/search/1", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No26-8.PDSユーザドメイン名 文字列型、20文字、入力規則違反していない（URL利用可能文字のみの半角小英数記号20桁）
def test_search_case26_8():
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_public(pdsUserId="C8000001", pdsUserName="PDSユーザドメイン検証成功テスト", accessToken=None)
    print("accessToken:" + token_result["accessToken"])
    header = {"pdsUserId": "C8000001", "Content-Type": "application/json", "timeStamp": "2022/08/23 15:12:01.690", "accessToken": token_result["accessToken"], "Authorization": "Bearer " + token_result["jwt"]}
    data_copy = DATA

    response = client.post("/api/2.0/c0123456789012345678/transaction/search/1", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No26-9.PDSユーザID 値が設定されていない（空値）
def test_search_case26_9(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["pdsUserId"] = None
    data_copy = DATA
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
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

    # PDSユーザIDに誤りがある場合には、PDSユーザドメイン検証でエラーになってしまうので入力チェックまで到達できないことを確認
    # 入力チェックを直接呼び出してエラーになることを確認
    response = searchRouter.input_check(
        trace_logger,
        "pds-user-create",
        REQUEST_BODY,
        header["pdsUserId"],
        header["accessToken"],
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


# No26-10.PDSユーザID 文字列型以外、7桁、C以外の文字で始まる
def test_search_case26_10(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["pdsUserId"] = '1234567'
    data_copy = DATA
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
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
    # 入力チェックを直接呼び出してエラーになることを確認
    response = searchRouter.input_check(
        trace_logger,
        "pds-user-create",
        REQUEST_BODY,
        int(header["pdsUserId"]),
        header["accessToken"],
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
            },
            {
                "errorCode": "020003",
                "message": response["errorInfo"][2]["message"]
            }
        ]
    }
    print(response)


# No26-11.PDSユーザID 文字列型、8桁、入力規則違反していない（C＋数値7桁）
def test_search_case26_11(create_header):
    header = create_header["header"]
    data_copy = DATA
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No26-12.タイムスタンプ 値が設定されていない（空値）
def test_search_case26_12(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["timeStamp"] = None
    data_copy = DATA
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
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


# No26-13.タイムスタンプ 文字列型以外、22桁
def test_search_case26_13(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA
    header["timeStamp"] = '1234567890123456789012'
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
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

    # ヘッダパラメータは文字列型以外を許容しないので、
    # 入力チェックを直接呼び出してエラーになることを確認
    response = searchRouter.input_check(
        trace_logger,
        "pds-user-create",
        REQUEST_BODY,
        header["pdsUserId"],
        header["accessToken"],
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


# No26-14.タイムスタンプ 文字列型、24桁、入力規則違反している　hh:mmがhhh:mm
def test_search_case26_14(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["timeStamp"] = '2022/09/30 12:000:00.000'
    data_copy = DATA
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
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


# No26-15.PDSユーザID 文字列型、23桁、入力規則違反していない　「yyyy/MM/dd hh:mm:ss.iii」
def test_search_case26_15(create_header):
    header = create_header["header"]
    data_copy = DATA
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No26-16.アクセストークン 値が設定されていない（空値）
def test_search_case26_16(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["accessToken"] = None
    data_copy = DATA
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
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

    # アクセストークンが不正な場合には、アクセストークン検証処理でエラーが発生して、入力チェックに到達しないため、
    # 入力チェックを直接呼び出してエラーになることを確認
    response = searchRouter.input_check(
        trace_logger,
        "pds-user-create",
        REQUEST_BODY,
        header["pdsUserId"],
        header["accessToken"],
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


# No26-17.アクセストークン 文字列型以外、201桁
def test_search_case26_17(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["accessToken"] = "123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901"
    data_copy = DATA
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020014",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())

    # アクセストークンが不正な場合には、アクセストークン検証処理でエラーが発生して、入力チェックに到達しないため、
    # 入力チェックを直接呼び出してエラーになることを確認
    response = searchRouter.input_check(
        trace_logger,
        "pds-user-create",
        REQUEST_BODY,
        header["pdsUserId"],
        int(header["accessToken"]),
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
                "errorCode": "020014",
                "message": response["errorInfo"][1]["message"]
            }
        ]
    }
    print(response)


# No26-18.アクセストークン 文字列型、199桁、入力可能文字以外が含まれる（全角）
def test_search_case26_18(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["accessToken"] = "あ123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678"
    data_copy = DATA
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
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

    # アクセストークンが不正な場合には、アクセストークン検証処理でエラーが発生して、入力チェックに到達しないため、
    # 入力チェックを直接呼び出してエラーになることを確認
    response = searchRouter.input_check(
        trace_logger,
        "pds-user-create",
        REQUEST_BODY,
        header["pdsUserId"],
        header["accessToken"],
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
                "errorCode": "020014",
                "message": response["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020003",
                "message": response["errorInfo"][1]["message"]
            }
        ]
    }
    print(response)


# No26-19.アクセストークン 文字列型、200桁、入力可能文字のみ（半角英数字） [a-fA-F0-9]
def test_search_case26_19(create_header):
    header = create_header["header"]
    data_copy = DATA
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No26-20.検索用ユーザID検索モード 文字列以外、入力可能文字以外が含まれる
def test_search_case26_20(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA
    data_copy["userIdMatchMode"] = 123
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
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


# No26-21.検索用ユーザID検索モード 文字列、入力可能文字以外が含まれる
def test_search_case26_21(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA
    data_copy["userIdMatchMode"] = "検索"
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
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


# No26-22.検索用ユーザID検索モード 文字列、入力可能文字のみ
def test_search_case26_22(create_header):
    header = create_header["header"]
    data_copy = DATA
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No26-23.検索用ユーザID検索文字列 文字列以外、37桁
def test_search_case26_23(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA
    data_copy["userIdStr"] = 1234567890123456789012345678901234567
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
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


# No26-24.検索用ユーザID検索文字列 文字列、36桁
def test_search_case26_24(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA
    data_copy["userIdStr"] = "123456789012345678901234567890123456"
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No26-25.保存データJsonキー情報 文字列以外
def test_search_case26_25(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA
    data_copy["dataJson"] = 123
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
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


# No26-26.保存データJsonキー情報 文字列
def test_search_case26_26(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No26-27.保存データ検索モード 文字列以外
def test_search_case26_27(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA
    data_copy["dataMatchMode"] = 123
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
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


# No26-28.保存データ検索モード 文字列、入力可能文字以外が含まれる
def test_search_case26_28(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA
    data_copy["userIdMatchMode"] = "検索"
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
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


# No26-29.保存データ検索モード 文字列、入力可能文字のみ
def test_search_case26_29(create_header):
    header = create_header["header"]
    data_copy = DATA
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "maxPage": response.json()["maxPage"],
        "maxCount": response.json()["maxCount"],
        "pageNo": response.json()["pageNo"],
        "tidList": response.json()["tidList"]
    }
    print(response.json())


# No26-30.保存データ検索文字列 文字列以外
def test_search_case26_30(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA
    data_copy["dataStr"] = 123
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
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


# No26-31.保存データ検索文字列 文字列
def test_search_case26_31(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "maxPage": response.json()["maxPage"],
        "maxCount": response.json()["maxCount"],
        "pageNo": response.json()["pageNo"],
        "tidList": response.json()["tidList"]
    }
    print(response.json())


# No26-32.保存されたバイナリデータのハッシュ値 文字列型以外
def test_search_case26_32(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA
    data_copy["imageHash"] = 123456
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
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


# No26-33.保存されたバイナリデータのハッシュ値 文字列型以外
def test_search_case26_33(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA
    data_copy["imageHash"] = "あ123456"
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
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


# No26-34.保存データ検索文字列 文字列
def test_search_case26_34(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "maxPage": response.json()["maxPage"],
        "maxCount": response.json()["maxCount"],
        "pageNo": response.json()["pageNo"],
        "tidList": response.json()["tidList"]
    }
    print(response.json())


# No26-35.検索用日時From 文字列以外、11文字
def test_search_case26_35(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA
    data_copy["fromDate"] = 12345678901
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
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


# No26-36.検索用日時From 文字列、9文字、入力規則不正
def test_search_case26_36(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA
    data_copy["fromDate"] = "202/01/01"
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
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


# No26-37.検索用日時From 文字列、10文字、入力規則
def test_search_case26_37(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "maxPage": response.json()["maxPage"],
        "maxCount": response.json()["maxCount"],
        "pageNo": response.json()["pageNo"],
        "tidList": response.json()["tidList"]
    }
    print(response.json())


# No26-38.検索用日時To 文字列以外、11文字
def test_search_case26_38(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA
    data_copy["toDate"] = 12345678901
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
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


# No26-39.検索用日時To 文字列、9文字、入力規則不正
def test_search_case26_39(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA
    data_copy["toDate"] = "202/01/01"
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
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


# No26-40.検索用日時To 文字列、10文字、入力規則
def test_search_case26_40(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "maxPage": response.json()["maxPage"],
        "maxCount": response.json()["maxCount"],
        "pageNo": response.json()["pageNo"],
        "tidList": response.json()["tidList"]
    }
    print(response.json())


# No26-41.検索日時Fromと検索用日時To 相関 FromがToを超過
def test_search_case26_41(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA
    data_copy["fromDate"] = "2023/01/02"
    data_copy["toDate"] = "2023/01/01"
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
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


# No26-42.検索日時Fromと検索用日時To 相関 FromがToを超過しない
def test_search_case26_42(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "maxPage": response.json()["maxPage"],
        "maxCount": response.json()["maxCount"],
        "pageNo": response.json()["pageNo"],
        "tidList": response.json()["tidList"]
    }
    print(response.json())


# No26-43.「引数．ヘッダパラメータ．PDSユーザID」と「引数．PDSユーザドメイン情報．PDSユーザID」の値が一致しない場合、「変数．エラー情報リスト」にエラー情報を追加する
def test_search_case26_43(mocker: MockerFixture, create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    # 返却値の変更
    mocker.patch("util.commonUtil.CommonUtilClass.check_pds_user_domain").return_value = {"result": True, "pdsUserInfo": {"pdsUserId": "C1234567"}}
    data_copy = DATA
    header = create_header["header"]
    header["pdsUserId"] = 'C9876543'
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
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


# No26-44.検索日時Fromと検索用日時To 相関 FromがToを超過しない
def test_search_case26_44(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "maxPage": response.json()["maxPage"],
        "maxCount": response.json()["maxCount"],
        "pageNo": response.json()["pageNo"],
        "tidList": response.json()["tidList"]
    }
    print(response.json())


# No27.共通エラーチェック処理が成功する（エラー情報有り）
def test_search_case27(mocker: MockerFixture, create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    # 返却値の変更
    mocker.patch("util.commonUtil.CommonUtilClass.check_pds_user_domain").return_value = {"result": True, "pdsUserInfo": {"pdsUserId": "C1234567"}}
    data_copy = DATA
    header = create_header["header"]
    header["pdsUserId"] = 'C9876543'
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
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


# No28.終了処理
def test_search_case28(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA
    response = client.post("/api/2.0/pds-user-create/transaction/search/1", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"],
        "maxPage": response.json()["maxPage"],
        "maxCount": response.json()["maxCount"],
        "pageNo": response.json()["pageNo"],
        "tidList": response.json()["tidList"]
    }
    print(response.json())
