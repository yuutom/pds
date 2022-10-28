from fastapi.testclient import TestClient
# from const.sqlConst import SqlConstClass
from app import app
from fastapi import Request
import pytest
# from util.commonUtil import get_str_datetime_in_X_days
# from pytest_mock.plugin import MockerFixture
from util.tokenUtil import TokenUtilClass
import util.logUtil as logUtil
import json
from const.systemConst import SystemConstClass
# from util.postgresDbUtil import PostgresDbUtilClass
# from const.wbtConst import wbtConstClass
# from const.fileNameConst import FileNameConstClass
# from util.commonUtil import CommonUtilClass

client = TestClient(app)

DATA = {
    "tfOperatorId": "create-int-test",
    "tfOperatorName": "機能間結合テスト",
    "tfOperatorMail": "int-test@xxx.yyy"
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
            "Content-Type": "application/json",
            "accessToken": token_result["accessToken"],
            "timeStamp": "2022/08/23 15:12:01.690",
            "Authorization": "Bearer " + token_result["jwt"]
        }
    }


def create_header_next(access_token):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_closed(tfOperatorInfo=TF_OPERATOR_INFO, accessToken=access_token)
    yield {
        "header": {
            "Content-Type": "application/json",
            "accessToken": token_result["accessToken"],
            "timeStamp": "2022/08/23 15:12:01.690",
            "Authorization": "Bearer " + token_result["jwt"]
        }
    }


def int_test_tf_operator_case(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No1.TFオペレータ登録→TFオペレータ検索・参照→ログイン→パスワード変更→ログイン（2回目以降）→メニュー
# ・TFオペレータの登録を行う
# ・登録したTFオペレータのIDと仮パスワードでログインする
# ・パスワード変更画面でパスワードを変更する
# ・ログイン画面に戻り、変更したパスワードでログインする
def test_int_tf_operator_case1(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    header = create_header["header"]
    regist_data = {
        "tfOperatorId": "create-int-test",
        "tfOperatorName": "機能間結合テスト",
        "tfOperatorMail": "int-test@xxx.yyy"
    }
    response_regist = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(regist_data))
    assert response_regist.status_code == 200
    assert response_regist.json() == {
        "status": "OK",
        "accessToken": response_regist.json()["accessToken"]
    }
    print(response_regist.json())

    TF_OPERATOR_INFO = {
        "tfOperatorId": "create-int-test",
        "tfOperatorName": "機能間結合テスト"
    }
    generated_access_token = response_regist.json()["accessToken"]
    token_result = token_util.create_token_closed(tfOperatorInfo=TF_OPERATOR_INFO, accessToken=generated_access_token)
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    response_search = client.post("/api/2.0/tfoperator/search", headers=header)
    assert response_search.status_code == 200
    assert response_search.json() == {
        "status": "OK",
        "accessToken": response_search.json()["accessToken"],
        "tfOperatorInfo": response_search.json()["tfOperatorInfo"]
    }
    print(response_search.json())

    generated_access_token = response_search.json()["accessToken"]
    token_result = token_util.create_token_closed(tfOperatorInfo=TF_OPERATOR_INFO, accessToken=generated_access_token)
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    login_data = {
        "tfOperatorId": "create-int-test",
        "tfOperatorPassword": "abcdedABC123"
    }
    response_login = client.post("/api/2.0/tfoperator/login", headers=header, data=json.dumps(login_data))
    assert response_login.status_code == 200
    assert response_login.json() == {
        "status": "OK",
        "tfOperatorId": DATA["tfOperatorId"],
        "tfOperatorName": DATA["tfOperatorName"],
        "tfOperatorPasswordResetFlg": True,
        "accessToken": response_login.json()["accessToken"]
    }
    print(response_login.json())

    generated_access_token = response_login.json()["accessToken"]
    token_result = token_util.create_token_closed(tfOperatorInfo=TF_OPERATOR_INFO, accessToken=generated_access_token)
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    change_pw_data = {
        "tfOperatorPassword": "test_1234",
        "tfOperatorConfirmPassword": "test_1234"
    }
    response_change_pw = client.post("/api/2.0/tfoperator/changepassword", headers=header, data=json.dumps(change_pw_data))
    assert response_change_pw.status_code == 200
    assert response_change_pw.json() == {
        "status": "OK",
        "accessToken": response_change_pw.json()["accessToken"]
    }
    print(response_change_pw.json())

    generated_access_token = response_change_pw.json()["accessToken"]
    token_result = token_util.create_token_closed(tfOperatorInfo=TF_OPERATOR_INFO, accessToken=generated_access_token)
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    login_data = {
        "tfOperatorId": "create-int-test",
        "tfOperatorPassword": "test_1234"
    }
    response = client.post("/api/2.0/tfoperator/login", headers=header, data=json.dumps(login_data))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "tfOperatorId": DATA["tfOperatorId"],
        "tfOperatorName": DATA["tfOperatorName"],
        "tfOperatorPasswordResetFlg": False,
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())
