from fastapi.testclient import TestClient
from app import app
from fastapi import Request
import pytest
from pytest_mock.plugin import MockerFixture
from util.tokenUtil import TokenUtilClass
import util.logUtil as logUtil
import json
from const.sqlConst import SqlConstClass
from const.systemConst import SystemConstClass
from const.messageConst import MessageConstClass
from util.postgresDbUtil import PostgresDbUtilClass
import routers.closed.pdsUserAuthInfoCreateRouter as pdsUserAuthInfoCreateRouter
from routers.closed.pdsUserAuthInfoCreateRouter import requestBody as routerRequestBody

client = TestClient(app)

# 処理名
EXEC_NAME: str = "pdsUserAuthInfoCreate"

DATA = {
    "pdsUserId": "C0000011"
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


# メイン処理
# 01.アクセストークン検証処理
# No.1.アクセストークン検証処理が失敗する
def test_pds_user_auth_info_create_case1(create_header):
    header = create_header["header"]
    header["accessToken"] = "518302174323385ee79afc2e37e3783f15e48e43d75f004a83e41667996087770c5e474023c0d6969529b49a8fd553ca454e54adbf473ac1a129fd4b0314abc4d4f33e4349749110f5b1774db69d5f87944e3a86c7d3ee10390a825f8bf35f1813774c94"
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": response.json()["errorInfo"]
    }
    print(response.json())


# No.2.アクセストークン検証処理が成功する
def test_pds_user_auth_info_create_case2(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 02.共通エラーチェック処理
# No.3.共通エラーチェック処理が成功
def test_pds_user_auth_info_create_case3(create_header):
    header = create_header["header"]
    header["accessToken"] = "518302174323385ee79afc2e37e3783f15e48e43d75f004a83e41667996087770c5e474023c0d6969529b49a8fd553ca454e54adbf473ac1a129fd4b0314abc4d4f33e4349749110f5b1774db69d5f87944e3a86c7d3ee10390a825f8bf35f1813774c94"
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": response.json()["errorInfo"]
    }
    print(response.json())


# 03.パラメータ検証処理
# No.4.パラメータ検証処理が失敗する
def test_pds_user_auth_info_create_case4(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserId"] = ""
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": response.json()["errorInfo"]
    }
    print(response.json())


# No.5.パラメータ検証処理が成功する
def test_pds_user_auth_info_create_case5(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 04.共通エラーチェック処理
# No.6.共通エラーチェック処理が成功
def test_pds_user_auth_info_create_case6(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserId"] = ""
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": response.json()["errorInfo"]
    }
    print(response.json())


# 05.DB接続準備処理
# No.7.接続に失敗する
def test_pds_user_auth_info_create_case7(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.commonUtil.CommonUtilClass.get_secret_info").return_value = {"host": "test", "port": "test", "username": "test", "password": "test"}
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
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


# No.8.接続に成功する
def test_pds_user_auth_info_create_case8(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 06.PDSユーザ取得処理
# No.9.PDSユーザ取得処理の取得件数が0件
def test_pds_user_auth_info_create_case9(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserId"] = "C1111112"
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
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


# No.10.PDSユーザ取得処理が失敗する
def test_pds_user_auth_info_create_case10(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "PDS_USER_AUTH_CREATE_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
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


# No.11.PDSユーザ取得処理が成功する
def test_pds_user_auth_info_create_case11(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 07.PDSユーザ整合性検証処理
# No.12.変数．PDSユーザ取得結果[1]が無効
def test_pds_user_auth_info_create_case12(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserId"] = "C0000100"
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
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


# 08.共通エラーチェック処理
# No.13.共通エラーチェック処理が成功
def test_pds_user_auth_info_create_case13(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserId"] = "C1111111"
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": response.json()["errorInfo"]
    }
    print(response.json())


# 09.PDSユーザ公開鍵インデックス最大値取得処理
# No.14.PDSユーザ公開鍵インデックス最大値取得処理の取得件数が0件
def test_pds_user_auth_info_create_case14(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserId"] = "C1111111"
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
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


# No.15.PDSユーザ公開鍵インデックス最大値取得処理が失敗する
def test_pds_user_auth_info_create_case15(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "PDS_USER_AUTH_CREATE_MAX_INDEX_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
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


# No.16.PDSユーザ公開鍵インデックス最大値取得処理が成功する
def test_pds_user_auth_info_create_case16(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 10.共通エラーチェック処理
# No.17.共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_auth_info_create_case17(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserId"] = "C1111111"
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": response.json()["errorInfo"]
    }
    print(response.json())


# 11.キーペア作成処理
# No.18_1.キーペア作成処理が成功した場合
def test_pds_user_auth_info_create_case18_1(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No.18_2.キーペア作成処理に失敗した場合
def test_pds_user_auth_info_create_case18_2(mocker: MockerFixture, create_header):
    mocker.patch("util.kmsUtil.KmsUtilClass.create_pds_user_kms_key").return_value = None
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "990062",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# 13.キーペアレプリケート処理
# No.18_3.キーペアレプリケート処理が成功した場合
def test_pds_user_auth_info_create_case18_3(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No.18_4.キーペアレプリケート処理が失敗した場合
def test_pds_user_auth_info_create_case18_4(mocker: MockerFixture, create_header):
    mocker.patch("util.kmsUtil.KmsUtilClass.replicate_pds_user_kms_key").return_value = None
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "990063",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# 15.キーペア取得処理
# No.18_5.キーペア取得処理が成功した場合
def test_pds_user_auth_info_create_case18_5(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No.18_6.キーペア取得処理に失敗した場合
def test_pds_user_auth_info_create_case18_6(mocker: MockerFixture, create_header):
    mocker.patch("util.kmsUtil.KmsUtilClass.get_kms_public_key").return_value = None
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "990064",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# 18.WBTメール件名作成処理
# No.19.WBTメール件名作成処理が成功した場合
def test_pds_user_auth_info_create_case19(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 19.トランザクション作成処理
# No.20.PDSユーザ認証情報発行トランザクションのトランザクション作成処理が失敗する


# No.21.PDSユーザ認証情報発行トランザクションのトランザクション作成処理が成功する


# 20.PDSユーザ公開鍵登録処理
# No.22.PDSユーザ公開鍵登録処理が失敗する
def test_pds_user_auth_info_create_case22(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "PDS_USER_KEY_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
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


# No.23.PDSユーザ公開鍵登録処理が成功する
def test_pds_user_auth_info_create_case23(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 21.共通エラーチェック処理
# No.24.共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_auth_info_create_case24(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "PDS_USER_KEY_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
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


# 22.WBT新規メール情報登録API実行処理
# No.25.WBT新規メール情報登録API実行処理が失敗する
def test_pds_user_auth_info_create_case25(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.commonUtil.CommonUtilClass.wbt_mails_add_api_exec").side_effect = Exception('testException')
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": response.json()["errorInfo"]
    }
    print(response.json())


# No.26.WBT新規メール情報登録API実行処理が成功する
def test_pds_user_auth_info_create_case26(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 23.共通エラーチェック処理
# No.27.共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_auth_info_create_case27(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.commonUtil.CommonUtilClass.wbt_mails_add_api_exec").return_value = {'result': False, 'errorInfo': {"errorCode": "020001", "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "種別")}}
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": response.json()["errorInfo"]
    }
    print(response.json())


# 24.WBTファイル登録API実行処理
# No.28.WBTファイル登録API実行処理が失敗する
def test_pds_user_auth_info_create_case28(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.commonUtil.CommonUtilClass.wbt_file_add_api_exec").side_effect = Exception('testException')
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": response.json()["errorInfo"]
    }
    print(response.json())


# No.29.WBTファイル登録API実行処理が成功する
def test_pds_user_auth_info_create_case29(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 25.共通エラーチェック処理
# No.30.共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_auth_info_create_case30(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.commonUtil.CommonUtilClass.wbt_file_add_api_exec").return_value = {'result': False, 'errorInfo': {"errorCode": "020001", "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "メールID")}}
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": response.json()["errorInfo"]
    }
    print(response.json())


# 20.トランザクションコミット処理
# No.31.PDSユーザ認証情報発行トランザクションのトランザクションコミット処理が失敗する
def test_pds_user_auth_info_create_case31(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(PostgresDbUtilClass, "commit_transaction", side_effect=Exception('testException'))
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": response.json()["errorInfo"]
    }
    print(response.json())


# No.32.PDSユーザ認証情報発行トランザクションのトランザクションコミット処理が成功する
def test_pds_user_auth_info_create_case32(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 21.トランザクション作成処理
# No.33.WBT送信メールID更新トランザクションのトランザクション作成処理が失敗する


# No.34.WBT送信メールID更新トランザクションのトランザクション作成処理が成功する

# 22.WBT送信メールID更新処理
# No.35.WBT送信メールID更新処理が失敗する
def test_pds_user_auth_info_create_case35(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "PDS_USER_KEY_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": response.json()["errorInfo"]
    }
    print(response.json())


# No.36.WBT送信メールID更新処理が成功する
def test_pds_user_auth_info_create_case36(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 23.共通エラーチェック処理
# No.37.共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_auth_info_create_case37(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "PDS_USER_KEY_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": response.json()["errorInfo"]
    }
    print(response.json())


# 24.トランザクションコミット処理
# No.38.WBT送信メールID更新トランザクションのトランザクションコミット処理が失敗する
def test_pds_user_auth_info_create_case38(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(PostgresDbUtilClass, "commit_transaction", side_effect=[True, Exception('testException')])
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": response.json()["errorInfo"]
    }
    print(response.json())


# No.39.WBT送信メールID更新トランザクションのトランザクションコミット処理が成功する
def test_pds_user_auth_info_create_case39(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 25.TF公開鍵通知ファイル削除処理
# No.40.TF公開鍵通知ファイル削除処理が成功する
def test_pds_user_auth_info_create_case40(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 26.アクセストークン発行処理
# No.41.アクセストークン発行処理が失敗する
def test_pds_user_auth_info_create_case41(mocker: MockerFixture, create_header):
    mocker.patch("util.tokenUtil.TokenUtilClass.verify_token_closed").return_value = {'result': True, 'payload': {'tfOperatorId': 't-test4', 'tfOperatorName': 'テスト', 'accessToken': '14d517e61315fbf0545b765dd0e7ca296d65a5403aef84a360efe191e8b6d28a6c30dda7557e269b8c800327a13fa3ce5833fc0351c884addb340921883eac40d03d92281ac6a7cf18c32aebfd6bf48c71aedc781f707ca0714b3c804c1526e2d2a6ad0a'}}
    mocker.patch("util.tokenUtil.TokenUtilClass.create_token_closed").return_value = Exception('testException')
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": response.json()["errorInfo"]
    }
    print(response.json())


# No.42.アクセストークン発行処理が成功する
def test_pds_user_auth_info_create_case42(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 27.共通エラーチェック処理
# No.43.共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_auth_info_create_case43(mocker: MockerFixture, create_header):
    mocker.patch("util.tokenUtil.TokenUtilClass.verify_token_closed").return_value = {'result': True, 'payload': {'tfOperatorId': 't-test4', 'tfOperatorName': 'テスト', 'accessToken': '14d517e61315fbf0545b765dd0e7ca296d65a5403aef84a360efe191e8b6d28a6c30dda7557e269b8c800327a13fa3ce5833fc0351c884addb340921883eac40d03d92281ac6a7cf18c32aebfd6bf48c71aedc781f707ca0714b3c804c1526e2d2a6ad0a'}}
    mocker.patch("util.tokenUtil.TokenUtilClass.create_token_closed").return_value = Exception('testException')
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": response.json()["errorInfo"]
    }
    print(response.json())


# 28.終了処理
# No.44.変数．エラー情報がある
def test_pds_user_auth_info_create_case44(mocker: MockerFixture, create_header):
    mocker.patch("util.tokenUtil.TokenUtilClass.verify_token_closed").return_value = {'result': True, 'payload': {'tfOperatorId': 't-test4', 'tfOperatorName': 'テスト', 'accessToken': '14d517e61315fbf0545b765dd0e7ca296d65a5403aef84a360efe191e8b6d28a6c30dda7557e269b8c800327a13fa3ce5833fc0351c884addb340921883eac40d03d92281ac6a7cf18c32aebfd6bf48c71aedc781f707ca0714b3c804c1526e2d2a6ad0a'}}
    mocker.patch("util.tokenUtil.TokenUtilClass.create_token_closed").return_value = Exception('testException')
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": response.json()["errorInfo"]
    }
    print(response.json())


# No.45.変数．エラー情報がない
def test_pds_user_auth_info_create_case45(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# パラメータ検証処理
# 01.パラメータ検証処理
# No.46_1.タイムスタンプの値が設定されていない ("")
def test_pds_user_auth_info_create_case46_1(create_header):
    header = create_header["header"]
    header["timeStamp"] = ""
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
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


# No.46_2.タイムスタンプの値が設定されていない (None)
def test_pds_user_auth_info_create_case46_2(create_header):
    header = create_header["header"]
    header["timeStamp"] = None
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
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


# No.46_3.タイムスタンプが文字列型ではなく24桁
def test_pds_user_auth_info_create_case46_3(create_header):
    header = create_header["header"]
    header["timeStamp"] = 123456789012345678901234
    data_copy = DATA.copy()
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserAuthInfoCreateRouter.input_check(
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


# No.46_4.タイムスタンプが正常な値で23桁
def test_pds_user_auth_info_create_case46_4(create_header):
    header = create_header["header"]
    header["timeStamp"] = "2022/08/23 15:12:01.690"
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No.46_5.アクセストークンの値が設定されていない ("")
def test_pds_user_auth_info_create_case46_5(create_header):
    header = create_header["header"]
    header["accessToken"] = ""
    data_copy = DATA.copy()
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserAuthInfoCreateRouter.input_check(
        trace_logger,
        router_request_body,
        header["accessToken"],
        header["timeStamp"]
    )
    assert response == {
        "result": False,
        "errorInfo": [
            {
                "errorCode": "020001",
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


# No.46_6.アクセストークンの値が設定されていない (None)
def test_pds_user_auth_info_create_case46_6(create_header):
    header = create_header["header"]
    header["accessToken"] = None
    data_copy = DATA.copy()
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserAuthInfoCreateRouter.input_check(
        trace_logger,
        router_request_body,
        header["accessToken"],
        header["timeStamp"]
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


# No.46_7.アクセストークンが文字列型ではなく201桁
def test_pds_user_auth_info_create_case46_7(create_header):
    header = create_header["header"]
    header["accessToken"] = 123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901
    data_copy = DATA.copy()
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserAuthInfoCreateRouter.input_check(
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


# No.46_8.アクセストークンが正常な値で200桁
def test_pds_user_auth_info_create_case46_8(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No.46_9.PDSユーザIDの値が設定されていない ("")
def test_pds_user_auth_info_create_case46_9(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserId"] = ""
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
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


# No.46_10.PDSユーザIDの値が設定されていない (None)
def test_pds_user_auth_info_create_case46_10(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserId"] = None
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
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


# No.46_11.PDSユーザIDが文字列型ではなく7桁
def test_pds_user_auth_info_create_case46_11(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserId"] = 1234567
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
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


# No.46_12.PDSユーザIDが正常な値8桁
def test_pds_user_auth_info_create_case46_12(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserId"] = "C0000011"
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 02.終了処理
# No.47.変数．エラー情報がない
def test_pds_user_auth_info_create_case47(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserId"] = "C0000011"
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No.48.変数．エラー情報がある
def test_pds_user_auth_info_create_case48(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserId"] = 1234567
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": response.json()["errorInfo"]
    }
    print(response.json())


# ロールバック処理 (PDSユーザ認証情報発行トランザクション)
# 01.ロールバック処理
# No.49.PDSユーザ認証情報発行トランザクションのロールバック処理が失敗する
def test_pds_user_auth_info_create_case49(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    mocker.patch.object(SqlConstClass, "PDS_USER_KEY_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    mocker.patch.object(PostgresDbUtilClass, "rollback_transaction", side_effect=Exception('testException'))
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
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


# No.50.PDSユーザ認証情報発行トランザクションのロールバック処理が成功する
def test_pds_user_auth_info_create_case50(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    mocker.patch.object(SqlConstClass, "PDS_USER_KEY_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
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
# No.51.共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_auth_info_create_case51(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    mocker.patch.object(SqlConstClass, "PDS_USER_KEY_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    mocker.patch.object(PostgresDbUtilClass, "rollback_transaction", side_effect=Exception('testException'))
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
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
# No.52.変数．エラー情報がない
def test_pds_user_auth_info_create_case52(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    mocker.patch.object(SqlConstClass, "PDS_USER_KEY_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
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


# ロールバック処理 (WBT送信メールID更新トランザクション)
# 01.ロールバック処理
# No.53.WBT送信メールID更新トランザクションのロールバック処理が失敗する
def test_pds_user_auth_info_create_case53(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    mocker.patch.object(SqlConstClass, "PDS_USER_KEY_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    mocker.patch.object(PostgresDbUtilClass, "rollback_transaction", side_effect=Exception('testException'))
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
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


# No.54.WBT送信メールID更新トランザクションのロールバック処理が成功する
def test_pds_user_auth_info_create_case54(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    mocker.patch.object(SqlConstClass, "PDS_USER_KEY_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
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
# No.55.共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_auth_info_create_case55(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    mocker.patch.object(SqlConstClass, "PDS_USER_KEY_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    mocker.patch.object(PostgresDbUtilClass, "rollback_transaction", side_effect=Exception('testException'))
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
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
# No.56.変数．エラー情報がない
def test_pds_user_auth_info_create_case56(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    mocker.patch.object(SqlConstClass, "PDS_USER_KEY_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.post("/api/2.0/pdsuser/generate", headers=header, data=json.dumps(data_copy))
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
