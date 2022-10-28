from fastapi.testclient import TestClient
from util.commonUtil import CommonUtilClass
from app import app
from fastapi import Request
import pytest
from pytest_mock.plugin import MockerFixture
from util.tokenUtil import TokenUtilClass
from util.fileUtil import NoHeaderOneItemCsvStringClass
import util.logUtil as logUtil
import json
from util.postgresDbUtil import PostgresDbUtilClass
from const.systemConst import SystemConstClass
from models.closed.pdsUserCreateModel import pdsUserCreateModelClass
from models.closed.pdsUserCreateModel import requestBody as modelRequestBody
from routers.closed.pdsUserCreateRouter import requestBody as routerRequestBody
import routers.closed.pdsUserCreateRouter as pdsUserCreateRouter
from exceptionClass.PDSException import PDSException

# 定数クラス
from const.sqlConst import SqlConstClass

client = TestClient(app)
trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
token_util = TokenUtilClass(trace_logger)
common_util = CommonUtilClass(trace_logger)
# 共通DB接続準備処理
common_db_info_response = common_util.get_common_db_info_and_connection()
EXEC_NAME: str = "pdsUserCreate"

BEARER = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0Zk9wZXJhdG9ySWQiOiJsLXRlc3QiLCJ0Zk9wZXJhdG9yTmFtZSI6Ilx1MzBlZFx1MzBiMFx1MzBhNFx1MzBmM1x1MzBjNlx1MzBiOVx1MzBjOCIsInRmT3BlcmF0b3JQYXNzd29yZFJlc2V0RmxnIjpmYWxzZSwiYWNjZXNzVG9rZW4iOiJiZGE4ZGY3OThiYzViZGZhMWZkODIyNmRiYmQ0OTMyMTY5ZmY5MjAzNWM0YzFlY2FjZjY2OGUyYzk2ZjAwZThlZTUxNTBiNGM0NTc0NjlkN2I4YmY1NzIxZDZlM2NiNzFiY2RiYzA3ODRiYzcyZWVlNjk1OGE3NTBiMWJkMWEzZWFmZWQ0OWFhNWU0ODZjYzQyZmM3OWNhMWY3MGQzZmM3Yzc0YzE5NjM3ODUzMjRhZDRhNGM0NjkxOGE4NjQ1N2ZiODE3NDU1MCIsImV4cCI6MTY2MTc0NjY3MX0.LCRjPEqKMkRQ_phaYnO7S7pd3SU_rgon-wsX14DBsPA"
ACCESS_TOKEN = "bda8df798bc5bdfa1fd8226dbbd4932169ff92035c4c1ecacf668e2c96f00e8ee5150b4c457469d7b8bf5721d6e3cb71bcdbc0784bc72eee6958a750b1bd1a3eafed49aa5e486cc42fc79ca1f70d3fc7c74c1963785324ad4a4c46918a86457fb8174550"
HEADER = {"Content-Type": "application/json", "timeStamp": "2022/08/23 15:12:01.690", "accessToken": ACCESS_TOKEN, "Authorization": "Bearer " + BEARER}
DATA = {
    "pdsUserId": "C1000000",
    "pdsUserName": "PDS登録テストユーザ1",
    "pdsUserDomainName": "pdsuser-create1",
    "pdsUserPublicKeyStartDate": "2022/11/01",
    "pdsUserPublicKeyExpectedDate": "2022/12/31",
    "tfContactAddress": "t.ii@lincrea.co.jp",
    "multiDownloadFileSendAddressTo": "test1@gmail.com",
    "multiDownloadFileSendAddressCc": "test2@gmail.com",
    "multiDeleteFileSendAddressTo": "test3@gmail.com",
    "multiDeleteFileSendAddressCc": "test4@gmail.com",
    "publicKeySendAddressTo": "test5@gmail.com",
    "publicKeySendAddressCc": "test6@gmail.com"
}
TF_OPERATOR_INFO = {
    "tfOperatorId": "approvalUser",
    "tfOperatorName": "abcdedABC123"
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


# No1.アクセストークン検証処理が失敗する
# No3.共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_create_case1(create_header):
    header = create_header["header"]
    header["accessToken"] = "518302174323385ee79afc2e37e3783f15e48e43d75f004a83e41667996087770c5e474023c0d6969529b49a8fd553ca454e54adbf473ac1a129fd4b0314abc4d4f33e4349749110f5b1774db69d5f87944e3a86c7d3ee10390a825f8bf35f1813774c94"
    response = client.post("/api/2.0/pdsuser/regist", headers=header, data=json.dumps(DATA))
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
# No5.パラメータ検証処理が成功する
# No8.接続に成功する
# No11.PDSユーザ取得処理が成功する
# No14.PDSユーザリソース作成処理が成功する
# No17.KMS登録処理に成功する
# No20.KMSレプリケート処理に成功する
# No23.KMS公開鍵取得処理に成功する
# No26.TF公開鍵通知ファイル作成処理に成功する
# No28.APIキー通知ファイル作成処理に成功する
# No30.PDSユーザ登録トランザクションのトランザクション作成処理が成功する
# No32.PDSユーザ登録処理が成功する
# No34.WBTメール件名作成処理に成功する
# No36.PDSユーザ公開鍵登録処理が成功する
# No39.WBT新規メール情報登録API実行処理が成功する
# No42.WBTファイル登録API実行処理が成功する
# No45.PDSユーザ登録トランザクションのコミット処理が成功する
# No47.PDSユーザ公開鍵更新トランザクションのトランザクション作成処理が成功する
# No49.WBT送信メールID更新処理が成功する
# No52.PDSユーザ公開鍵更新トランザクションのコミット処理が成功する
# No54.アクセストークン発行処理が成功する
# No57.変数．エラー情報がない
def test_pds_user_create_case2(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserId"] = "C6000001"
    # MongoDB設定初期化処理は別でテストする
    mocker.patch.object(pdsUserCreateModelClass, "initial_mongodb", side_effect={"result": True})
    response = client.post("/api/2.0/pdsuser/regist", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No4.パラメータ検証処理が失敗する
# No6.共通エラーチェック処理が成功（エラー情報有り）
# No56.変数．エラー情報があるNo.6でエラー）
def test_pds_user_create_case4(create_header):
    header = create_header["header"]
    header["timeStamp"] = ""
    response = client.post("/api/2.0/pdsuser/regist", headers=header, data=json.dumps(DATA))
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
            },
        ]
    }
    print(response.json())


# No7.接続に失敗する 設定値を異常な値に変更する
def test_pds_user_create_case7(mocker: MockerFixture, create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    # main処理を直接呼び出して対応する
    mocker.patch.object(SystemConstClass, "PDS_COMMON_DB_SECRET_INFO", {"SECRET_NAME": "pds-common-sm-ng"})
    model = pdsUserCreateModelClass(trace_logger)
    with pytest.raises(PDSException) as e:
        model.main(modelRequestBody(**DATA))

    assert e.value.args[0] == {
        "errorCode": "999999",
        "message": e.value.args[0]["message"]
    }
    print(e)


# No9.PDSユーザ取得処理のカウントが0以外
def test_pds_user_create_case9(create_header):
    header = create_header["header"]
    DATA["pdsUserId"] = "C9876543"
    response = client.post("/api/2.0/pdsuser/regist", headers=header, data=json.dumps(DATA))
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


# No10.PDSユーザ取得処理が失敗する
# No12.共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_create_case10(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "PDS_USER_EXIST_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.post("/api/2.0/pdsuser/regist", headers=header, data=json.dumps(DATA))
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


# No13.PDSユーザリソース作成処理が失敗する
# No15.共通エラーチェック処理が成功（エラー情報有り）
# No61.CloudFormationテンプレート存在検証処理が失敗する
# No63.共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_create_case13(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserId"] = "C6000001"
    mocker.patch.object(SystemConstClass, "CFN_PREFIX", "test-object")
    response = client.post("/api/2.0/pdsuser/regist", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "990023",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No16.KMS登録処理に失敗する
# No18.共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_create_case16(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(pdsUserCreateModelClass, "create_pds_user_resource", return_value={"result": True, "apiKey": "aiueo12345aiueo12345aiueo12345", "stackOutputInfo": {"BucketName": "pds-c0000000-bucket", "KmsId": "fdb4c6aa-50b0-4ed1-bdad-32c21e0a0387", "OsakaAzaMongoSecretName": "pds-c0000000-mongo-osaka-a-sm", "pds-c0000000-mongo-osaka-c-sm": "pds-c0000000-mongo-osaka-c-sm", "PdsUserDbSecretsName": "pds-c6000001-sm-dev", "TokyoAzaMongoSecretName": "pds-c0000000-mongo-tokyo-a-sm", "TokyoAzcMongoSecretName": "pds-c0000000-mongo-tokyo-c-sm"}})
    mocker.patch("util.kmsUtil.KmsUtilClass.create_pds_user_kms_key").side_effect = Exception("test-exception")
    response = client.post("/api/2.0/pdsuser/regist", headers=header, data=json.dumps(DATA))
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


# No19.KMS登録処理に失敗する
# No21.共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_create_case19(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.kmsUtil.KmsUtilClass.create_pds_user_kms_key").side_effect = Exception("test-exception")
    response = client.post("/api/2.0/pdsuser/regist", headers=header, data=json.dumps(DATA))
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


# No22.KMS公開鍵取得処理に失敗した
# No24.共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_create_case22(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.kmsUtil.KmsUtilClass.replicate_pds_user_kms_key").side_effect = Exception("test-exception")
    response = client.post("/api/2.0/pdsuser/regist", headers=header, data=json.dumps(DATA))
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


# No25.TF公開鍵通知ファイル作成処理に失敗する
def test_pds_user_create_case25(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("base64.b64encode").side_effect = Exception("test-exception")
    response = client.post("/api/2.0/pdsuser/regist", headers=header, data=json.dumps(DATA))
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


# No27.APIキー通知ファイル作成処理に失敗する
def test_pds_user_create_case27(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(NoHeaderOneItemCsvStringClass, "__formatCsv", side_effect=["aaaaaaaa", Exception("test-exception")])
    response = client.post("/api/2.0/pdsuser/regist", headers=header, data=json.dumps(DATA))
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


# No29.PDSユーザ登録トランザクションのトランザクション作成処理が失敗する
#      ※コネクション作成時に自動作成されるのでテスト不可


# No31.PDSユーザ登録処理が失敗する
# No33.共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_create_case31(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "PDS_USER_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.post("/api/2.0/pdsuser/regist", headers=header, data=json.dumps(DATA))
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


# No35.PDSユーザ公開鍵登録処理が失敗する
# No37.共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_create_case35(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "PDS_USER_KEY_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.post("/api/2.0/pdsuser/regist", headers=header, data=json.dumps(DATA))
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


# No38.WBT新規メール情報登録API実行処理が失敗する
# No40.共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_create_case38(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(CommonUtilClass, "wbt_mails_add_api_exec", side_effect=Exception('testException'))
    response = client.post("/api/2.0/pdsuser/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "990011",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No41.WBTファイル登録API実行処理が失敗する
# No43.共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_create_case41(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(CommonUtilClass, "wbt_file_add_api_exec", side_effect=Exception('testException'))
    response = client.post("/api/2.0/pdsuser/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "990013",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No44.PDSユーザ登録トランザクションのコミット処理が失敗する
def test_pds_user_create_case44(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(PostgresDbUtilClass, "commit_transaction", side_effect=Exception('testException'))
    response = client.post("/api/2.0/pdsuser/regist", headers=header, data=json.dumps(DATA))
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


# No46.PDSユーザ公開鍵更新トランザクションのトランザクション作成処理が失敗する
#      ※ロールバック・コミット時に自動作成されるのでテスト不可


# No47.WBT送信メールID更新処理が失敗する
# No50.共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_create_case48(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "PDS_USER_KEY_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.post("/api/2.0/pdsuser/regist", headers=header, data=json.dumps(DATA))
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


# No51.PDSユーザ公開鍵更新トランザクションのコミット処理が失敗する
def test_pds_user_create_case51(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(PostgresDbUtilClass, "commit_transaction", side_effect=[None, Exception('testException')])
    response = client.post("/api/2.0/pdsuser/regist", headers=header, data=json.dumps(DATA))
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


# No53.アクセストークン発行処理が失敗する
# No55.共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_create_case53(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.tokenUtil.TokenUtilClass.create_token_closed").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    response = client.post("/api/2.0/pdsuser/regist", headers=header, data=json.dumps(DATA))
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


# No56-1.タイムスタンプ 値が設定されていない（空値）
def test_pds_user_create_case56_1(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
        trace_logger=trace_logger,
        request_body=router_request_body,
        access_token=header["accessToken"],
        time_stamp=None
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


# No56-2.タイムスタンプ 文字列型以外、22桁
def test_pds_user_create_case56_2(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["timeStamp"] = '1234567890123456789012'
    data_copy = DATA.copy()
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
        trace_logger=trace_logger,
        request_body=router_request_body,
        access_token=header["accessToken"],
        time_stamp=int(header["timeStamp"])
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


# No56-3.タイムスタンプ 文字列型、24桁、入力規則違反している　hh:mmがhhh:mm
def test_pds_user_create_case56_3(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["timeStamp"] = '2022/09/30 12:000:00.000'
    data_copy = DATA.copy()
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
        trace_logger=trace_logger,
        request_body=router_request_body,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"]
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


# No56-4.アクセストークン 値が設定されていない（空値）
def test_pds_user_create_case56_4(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
        trace_logger=trace_logger,
        request_body=router_request_body,
        access_token=None,
        time_stamp=header["timeStamp"]
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


# No56-5.アクセストークン 文字列型以外、201桁
def test_pds_user_create_case56_5(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["accessToken"] = "123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901"
    data_copy = DATA.copy()
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
        trace_logger=trace_logger,
        request_body=router_request_body,
        access_token=int(header["accessToken"]),
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


# No56-6.アクセストークン 文字列型、199桁、入力可能文字以外が含まれる（全角）
def test_pds_user_create_case56_6(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    header["accessToken"] = "あ123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678"
    data_copy = DATA.copy()
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
        trace_logger=trace_logger,
        request_body=router_request_body,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"]
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


# No56-7.アクセストークン 文字列型、200桁、入力可能文字のみ（半角英数字） [a-fA-F0-9]
def test_pds_user_create_case56_7(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
        trace_logger=trace_logger,
        request_body=router_request_body,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"]
    )
    assert response == {
        "result": True
    }
    print(response)


# No56-8.PDSユーザID 値が設定されていない（空値）
def test_pds_user_create_case56_8(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserId"] = None
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
        trace_logger=trace_logger,
        request_body=router_request_body,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"]
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


# No56-9.PDSユーザID 文字列型以外、7桁、C以外の文字で始まる
def test_pds_user_create_case56_9(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserId"] = 1234567
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
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


# No56-10.PDSユーザID 文字列型、8桁、入力規則違反していない（C＋数値7桁）
def test_pds_user_create_case56_10(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
        trace_logger=trace_logger,
        request_body=router_request_body,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"]
    )
    assert response == {
        "result": True
    }
    print(response)


# No56-11.PDSユーザ名 値が設定されていない（空値）
def test_pds_user_create_case56_11(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserName"] = None
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
        trace_logger=trace_logger,
        request_body=router_request_body,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"]
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


# No56-12.PDSユーザ名  文字列型以外、65桁
def test_pds_user_create_case56_12(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserName"] = 12345678901234567890123456789012345678901234567890123456789012345
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
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
                "errorCode": "020002",
                "message": response["errorInfo"][1]["message"]
            },
        ]
    }
    print(response)


# No56-13.PDSユーザ名  文字列型、65桁、入力可能文字以外を含む
def test_pds_user_create_case56_13(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserName"] = " 1234567890123456789012345678901234567890123456789012345678901234"
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
        trace_logger=trace_logger,
        request_body=router_request_body,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"]
    )
    assert response == {
        "result": False,
        "errorInfo": [
            {
                "errorCode": "020002",
                "message": response["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020020",
                "message": response["errorInfo"][1]["message"]
            },
        ]
    }
    print(response)


# No56-14.PDSユーザ名  文字列型、64桁、入力可能文字以外を含まない
def test_pds_user_create_case56_14(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserName"] = "aiueoあいうえお123456789012345678901234567890123456789012345678901234"
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
        trace_logger=trace_logger,
        request_body=router_request_body,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"]
    )
    assert response == {
        "result": True
    }
    print(response)


# No56-15.PDSユーザドメイン名 値が設定されていない（空値）
def test_pds_user_create_case56_15(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserDomainName"] = None
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
        trace_logger=trace_logger,
        request_body=router_request_body,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"]
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


# No56-16.PDSユーザドメイン名  文字列型以外、21桁
def test_pds_user_create_case56_16(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserDomainName"] = 123456789012345678901
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
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
                "errorCode": "020002",
                "message": response["errorInfo"][1]["message"]
            },
        ]
    }
    print(response)


# No56-17.PDSユーザドメイン名  文字列型、4桁、入力規則違反（全角）
def test_pds_user_create_case56_17(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserDomainName"] = "aaaあ"
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
        trace_logger=trace_logger,
        request_body=router_request_body,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"]
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
            },
        ]
    }
    print(response)


# No56-18.PDSユーザドメイン名  文字列型、5桁、入力規則
def test_pds_user_create_case56_18(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserDomainName"] = "aiueo"
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
        trace_logger=trace_logger,
        request_body=router_request_body,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"]
    )
    assert response == {
        "result": True
    }
    print(response)


# No56-19.PDSユーザドメイン名  文字列型、20桁、入力規則
def test_pds_user_create_case56_19(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserDomainName"] = "aiueo-aiueo-aiueo-ai"
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
        trace_logger=trace_logger,
        request_body=router_request_body,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"]
    )
    assert response == {
        "result": True
    }
    print(response)


# No56-20.PDSユーザ公開鍵開始日 値が設定されていない（空値）
def test_pds_user_create_case56_20(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserPublicKeyStartDate"] = None
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
        trace_logger=trace_logger,
        request_body=router_request_body,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"]
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


# No56-21.PDSユーザ公開鍵開始日 文字列型以外、11桁
def test_pds_user_create_case56_21(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserPublicKeyStartDate"] = 12345678901
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
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


# No56-22.PDSユーザ公開鍵開始日 文字列型、9桁、入力規則違反
def test_pds_user_create_case56_22(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserPublicKeyStartDate"] = "202/01/01"
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
        trace_logger=trace_logger,
        request_body=router_request_body,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"]
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


# No56-23.PDSユーザ公開鍵開始日 文字列型、10桁、入力規則
def test_pds_user_create_case56_23(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserPublicKeyStartDate"] = "2022/01/01"
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
        trace_logger=trace_logger,
        request_body=router_request_body,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"]
    )
    assert response == {
        "result": True
    }
    print(response)


# No56-24.PDSユーザ公開鍵終了予定日 値が設定されていない（空値）
def test_pds_user_create_case56_24(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserPublicKeyExpectedDate"] = None
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
        trace_logger=trace_logger,
        request_body=router_request_body,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"]
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


# No56-25.PDSユーザ公開鍵終了予定日 文字列型以外、11桁
def test_pds_user_create_case56_25(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserPublicKeyExpectedDate"] = 12345678901
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
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


# No56-26.PDSユーザ公開鍵終了予定日 文字列型、9桁、入力規則違反
def test_pds_user_create_case56_26(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserPublicKeyExpectedDate"] = "202/01/01"
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
        trace_logger=trace_logger,
        request_body=router_request_body,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"]
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


# No56-27.PDSユーザ公開鍵終了予定日 文字列型、10桁、入力規則
def test_pds_user_create_case56_27(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
        trace_logger=trace_logger,
        request_body=router_request_body,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"]
    )
    assert response == {
        "result": True
    }
    print(response)


# No56-28.TF担当者メールアドレス 値が設定されていない（空値）
def test_pds_user_create_case56_28(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfContactAddress"] = None
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
        trace_logger=trace_logger,
        request_body=router_request_body,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"]
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


# No56-29.TF担当者メールアドレス 文字列型以外
def test_pds_user_create_case56_29(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfContactAddress"] = 1234567
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
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
            }
        ]
    }
    print(response)


# No56-30.TF担当者メールアドレス 文字列型、513桁、入力規則違反
def test_pds_user_create_case56_30(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfContactAddress"] = "あ12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012"
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
        trace_logger=trace_logger,
        request_body=router_request_body,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"]
    )
    assert response == {
        "result": False,
        "errorInfo": [
            {
                "errorCode": "020002",
                "message": response["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020003",
                "message": response["errorInfo"][1]["message"]
            }
        ]
    }
    print(response)


# No56-31.TF担当者メールアドレス 文字列型、512桁、入力規則
def test_pds_user_create_case56_31(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfContactAddress"] = "1234567890@1234567890.1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890"
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
        trace_logger=trace_logger,
        request_body=router_request_body,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"]
    )
    assert response == {
        "result": True
    }
    print(response)


# No56-32.一括DL送付先アドレスTo 値が設定されていない（空値）
def test_pds_user_create_case56_32(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["multiDownloadFileSendAddressTo"] = None
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
        trace_logger=trace_logger,
        request_body=router_request_body,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"]
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


# No56-33.一括DL送付先アドレスTo 文字列型以外
def test_pds_user_create_case56_33(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["multiDownloadFileSendAddressTo"] = 1234567
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
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
            }
        ]
    }
    print(response)


# No56-34.一括DL送付先アドレスTo 文字列型、513桁、入力規則違反
def test_pds_user_create_case56_34(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["multiDownloadFileSendAddressTo"] = "あ12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012"
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
        trace_logger=trace_logger,
        request_body=router_request_body,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"]
    )
    assert response == {
        "result": False,
        "errorInfo": [
            {
                "errorCode": "020002",
                "message": response["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020003",
                "message": response["errorInfo"][1]["message"]
            }
        ]
    }
    print(response)


# No56-35.一括DL送付先アドレスTo 文字列型、512桁、入力規則
def test_pds_user_create_case56_35(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["multiDownloadFileSendAddressTo"] = "1234567890@1234567890.1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890"
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
        trace_logger=trace_logger,
        request_body=router_request_body,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"]
    )
    assert response == {
        "result": True
    }
    print(response)


# No56-36.一括DL送付先アドレスCc 文字列型以外
def test_pds_user_create_case56_36(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["multiDownloadFileSendAddressCc"] = 1234567
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
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
            }
        ]
    }
    print(response)


# No56-37.一括DL送付先アドレスCc 文字列型、513桁、入力規則違反
def test_pds_user_create_case56_37(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["multiDownloadFileSendAddressCc"] = "あ12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012"
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
        trace_logger=trace_logger,
        request_body=router_request_body,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"]
    )
    assert response == {
        "result": False,
        "errorInfo": [
            {
                "errorCode": "020002",
                "message": response["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020003",
                "message": response["errorInfo"][1]["message"]
            }
        ]
    }
    print(response)


# No56-38.一括DL送付先アドレスCc 文字列型、512桁、入力規則
def test_pds_user_create_case56_38(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["multiDownloadFileSendAddressCc"] = "1234567890@1234567890.1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890"
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
        trace_logger=trace_logger,
        request_body=router_request_body,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"]
    )
    assert response == {
        "result": True
    }
    print(response)


# No56-39.一括削除送付先アドレスTo 値が設定されていない（空値）
def test_pds_user_create_case56_39(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["multiDeleteFileSendAddressTo"] = None
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
        trace_logger=trace_logger,
        request_body=router_request_body,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"]
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


# No56-40.一括削除送付先アドレスTo 文字列型以外
def test_pds_user_create_case56_40(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["multiDeleteFileSendAddressTo"] = 1234567
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
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
            }
        ]
    }
    print(response)


# No56-41.一括削除送付先アドレスTo 文字列型、513桁、入力規則違反
def test_pds_user_create_case56_41(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["multiDeleteFileSendAddressTo"] = "あ12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012"
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
        trace_logger=trace_logger,
        request_body=router_request_body,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"]
    )
    assert response == {
        "result": False,
        "errorInfo": [
            {
                "errorCode": "020002",
                "message": response["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020003",
                "message": response["errorInfo"][1]["message"]
            }
        ]
    }
    print(response)


# No56-42.一括削除送付先アドレスTo 文字列型、512桁、入力規則
def test_pds_user_create_case56_42(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["multiDeleteFileSendAddressTo"] = "1234567890@1234567890.1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890"
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
        trace_logger=trace_logger,
        request_body=router_request_body,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"]
    )
    assert response == {
        "result": True
    }
    print(response)


# No56-43.一括削除送付先アドレスCc 文字列型以外
def test_pds_user_create_case56_43(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["multiDeleteFileSendAddressCc"] = 1234567
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
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
            }
        ]
    }
    print(response)


# No56-44.一括削除送付先アドレスCc 文字列型、513桁、入力規則違反
def test_pds_user_create_case56_44(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["multiDeleteFileSendAddressCc"] = "あ12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012"
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
        trace_logger=trace_logger,
        request_body=router_request_body,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"]
    )
    assert response == {
        "result": False,
        "errorInfo": [
            {
                "errorCode": "020002",
                "message": response["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020003",
                "message": response["errorInfo"][1]["message"]
            }
        ]
    }
    print(response)


# No56-45.一括削除送付先アドレスCc 文字列型、512桁、入力規則
def test_pds_user_create_case56_45(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["multiDeleteFileSendAddressCc"] = "1234567890@1234567890.1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890"
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
        trace_logger=trace_logger,
        request_body=router_request_body,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"]
    )
    assert response == {
        "result": True
    }
    print(response)


# No56-46.公開鍵送付先アドレスTo 値が設定されていない（空値）
def test_pds_user_create_case56_46(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["publicKeySendAddressTo"] = None
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
        trace_logger=trace_logger,
        request_body=router_request_body,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"]
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


# No56-47.公開鍵送付先アドレスTo 文字列型以外
def test_pds_user_create_case56_47(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["publicKeySendAddressTo"] = 1234567
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
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
            }
        ]
    }
    print(response)


# No56-48.公開鍵送付先アドレスTo 文字列型、513桁、入力規則違反
def test_pds_user_create_case56_48(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["publicKeySendAddressTo"] = "あ12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012"
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
        trace_logger=trace_logger,
        request_body=router_request_body,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"]
    )
    assert response == {
        "result": False,
        "errorInfo": [
            {
                "errorCode": "020002",
                "message": response["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020003",
                "message": response["errorInfo"][1]["message"]
            }
        ]
    }
    print(response)


# No56-49.公開鍵送付先アドレスTo 文字列型、512桁、入力規則
def test_pds_user_create_case56_49(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["publicKeySendAddressTo"] = "1234567890@1234567890.1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890"
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
        trace_logger=trace_logger,
        request_body=router_request_body,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"]
    )
    assert response == {
        "result": True
    }
    print(response)


# No56-50.公開鍵送付先アドレスCc 文字列型以外
def test_pds_user_create_case56_50(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["publicKeySendAddressCc"] = 1234567
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
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
            }
        ]
    }
    print(response)


# No56-51.公開鍵送付先アドレスCc 文字列型、513桁、入力規則違反
def test_pds_user_create_case56_51(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["publicKeySendAddressCc"] = "あ12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012"
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
        trace_logger=trace_logger,
        request_body=router_request_body,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"]
    )
    assert response == {
        "result": False,
        "errorInfo": [
            {
                "errorCode": "020002",
                "message": response["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020003",
                "message": response["errorInfo"][1]["message"]
            }
        ]
    }
    print(response)


# No56-52.公開鍵送付先アドレスCc 文字列型、512桁、入力規則
def test_pds_user_create_case56_52(create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["publicKeySendAddressCc"] = "1234567890@1234567890.1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890"
    router_request_body = routerRequestBody(**data_copy)
    response = pdsUserCreateRouter.input_check(
        trace_logger=trace_logger,
        request_body=router_request_body,
        access_token=header["accessToken"],
        time_stamp=header["timeStamp"]
    )
    assert response == {
        "result": True
    }
    print(response)


# No59.変数．エラー情報がない
def test_pds_user_create_case59(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No60.変数．エラー情報がある
def test_pds_user_create_case60(create_header):
    header = create_header["header"]
    header["timeStamp"] = ""
    response = client.post("/api/2.0/pdsuser/regist", headers=header, data=json.dumps(DATA))
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
            },
        ]
    }
    print(response.json())


# No62.CloudFormationテンプレート存在検証処理が成功する
# No65.CloudFormationテンプレート実行処理が成功する
# No68.CloudFormation終了監視処理が成功する
# No70.変数．エラー情報がNull
# No81.スタック情報取得処理が成功する
# No83.APIキー作成処理が成功する
# No85.RDSテーブル作成処理が成功する
# No87.変数．エラー情報がない
def test_pds_user_create_case62(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No64.CloudFormationテンプレート実行処理が失敗する
# No66.共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_create_case64(create_header):
    header = create_header["header"]
    # デバッグで対応する必要あり
    response = client.post("/api/2.0/pdsuser/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "990072",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No67.CloudFormation終了監視処理が失敗する
# No69.共通エラーチェック処理が成功（エラー情報有り）
# No76.レスポンス情報を作成 「変数．エラー情報」に値が設定されている
# No79.レスポンス情報を返却 CloudFormationテンプレート実行エラー処理が成功する
def test_pds_user_create_case67(create_header):
    header = create_header["header"]
    # デバッグで対応する必要あり
    response = client.post("/api/2.0/pdsuser/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "990073",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No71.変数．CloudFormation情報取得処理実行結果[0]．StackStatus = ROLLBACK_COMPLETE以外
# No75.スタックロールバックエラー情報作成処理が成功する
# No77.レスポンス情報を作成 「変数．ロールバックエラー情報」に値が設定されている
def test_pds_user_create_case71(create_header):
    header = create_header["header"]
    # デバッグで対応する必要あり
    response = client.post("/api/2.0/pdsuser/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "990073",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "990071",
                "message": response.json()["errorInfo"][1]["message"]
            }
        ]
    }
    print(response.json())


# No72.変数．CloudFormation情報取得処理実行結果[0]．StackStatus = ROLLBACK_COMPLETE
# No74.PDSユーザリソース削除処理が成功する
def test_pds_user_create_case72(create_header):
    header = create_header["header"]
    # デバッグで対応する必要あり
    response = client.post("/api/2.0/pdsuser/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "990073",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response)


# No73.PDSユーザリソース削除処理が失敗する
# No78.レスポンス情報を作成 「変数．PDSユーザリソース削除処理実行結果．処理結果」がfalse
def test_pds_user_create_case73(create_header):
    header = create_header["header"]
    # デバッグで対応する必要あり
    response = client.post("/api/2.0/pdsuser/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "990073",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "990074",
                "message": response.json()["errorInfo"][1]["message"]
            }
        ]
    }
    print(response)


# No80.スタック情報取得処理が失敗する
# No82.共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_create_case80(create_header):
    header = create_header["header"]
    # デバッグで対応する必要あり
    response = client.post("/api/2.0/pdsuser/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "990073",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No84.RDSテーブル作成処理が失敗する
# No86.共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_create_case84(mocker: MockerFixture, create_header):
    header = create_header["header"]
    # デバッグで対応する必要あり
    mocker.patch.object(SqlConstClass, "USER_PROFILE_TABLE_CREATE", """ SELECT * FROM AAAAAA; """)
    response = client.post("/api/2.0/pdsuser/regist", headers=header, data=json.dumps(DATA))
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


# No88.CloudFormationスタック削除処理 失敗した場合
# No89.CloudFormationスタック削除処理が失敗する
# No91.共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_create_case88(mocker: MockerFixture, create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    model = pdsUserCreateModelClass(trace_logger)
    client = model.create_cfn_client()
    with pytest.raises(PDSException) as e:
        model.delete_pds_user_resource(client, "AAAA-stack-set")

    assert e.value.args[0] == {
        "errorCode": "990074",
        "message": e.value.args[0]["message"]
    }
    print(e)


# No90.CloudFormationスタック削除処理が成功する
# No92.変数．エラー情報がない
def test_pds_user_create_case90(mocker: MockerFixture, create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    data_copy = DATA.copy()
    model = pdsUserCreateModelClass(trace_logger)
    client = model.create_cfn_client()
    try:
        model.delete_pds_user_resource(client, data_copy["pdsUserId"] + "-stack-set")
    except Exception as e:
        print(e)
        pytest.fail("Raise Exception")


# No93.接続に失敗する 設定値を異常な値に変更する
def test_pds_user_create_case93(mocker: MockerFixture, create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    data_copy = DATA.copy()
    model = pdsUserCreateModelClass(trace_logger)
    with pytest.raises(PDSException) as e:
        model.create_rds_table("pds-c0000000-sm-ng", data_copy["pdsUserId"])
    assert e.value.args[0] == {
        "errorCode": "999999",
        "message": e.value.args[0]["message"]
    }
    print(e)


# No94.接続に成功する
# No96.PDSユーザDB作成トランザクションのトランザクション作成処理が成功する
# No98.PDSユーザごとのテーブル作成処理が成功する
# No101.PDSユーザDB作成トランザクションのトランザクションコミット処理が成功する
# No102.変数．エラー情報がない
def test_pds_user_create_case94(mocker: MockerFixture, create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    data_copy = DATA.copy()
    model = pdsUserCreateModelClass(trace_logger)
    try:
        model.create_rds_table("pds-c0000000-sm", data_copy["pdsUserId"])
    except Exception as e:
        print(e)
        pytest.fail("Raise Exception")


# No95.PDSユーザDB作成トランザクションのトランザクション作成処理が失敗する
#      ※コネクション作成時にトランザクションが作成されるのでテスト不可


# No97.PDSユーザごとのテーブル作成処理が失敗する
# No99.共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_create_case97(mocker: MockerFixture, create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    data_copy = DATA.copy()
    mocker.patch.object(SqlConstClass, "USER_PROFILE_TABLE_CREATE", """ SELECT * FROM AAAAAA; """)
    model = pdsUserCreateModelClass(trace_logger)
    with pytest.raises(PDSException) as e:
        model.create_rds_table("pds-c0000000-sm", data_copy["pdsUserId"])
    assert e.value.args[0] == {
        "errorCode": "999999",
        "message": e.value.args[0]["message"]
    }
    print(e)


# No100.PDSユーザDB作成トランザクションのトランザクションコミット処理が失敗する
def test_pds_user_create_case100(mocker: MockerFixture, create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    data_copy = DATA.copy()
    mocker.patch.object(PostgresDbUtilClass, "commit_transaction", side_effect=PDSException("test-exception"))
    model = pdsUserCreateModelClass(trace_logger)
    with pytest.raises(PDSException) as e:
        model.create_rds_table("pds-c0000000-sm", data_copy["pdsUserId"])
    assert e.value.args[0] == {
        "errorCode": "999999",
        "message": e.value.args[0]["message"]
    }
    print(e)
