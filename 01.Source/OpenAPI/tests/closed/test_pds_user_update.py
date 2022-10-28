from fastapi.testclient import TestClient
from util.commonUtil import CommonUtilClass
from app import app
from fastapi import Request
import pytest
from pytest_mock.plugin import MockerFixture
from util.tokenUtil import TokenUtilClass
import util.logUtil as logUtil
import json
from util.postgresDbUtil import PostgresDbUtilClass
from const.systemConst import SystemConstClass

# 定数クラス
from const.sqlConst import SqlConstClass

client = TestClient(app)
trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
token_util = TokenUtilClass(trace_logger)
common_util = CommonUtilClass(trace_logger)
# 共通DB接続準備処理
common_db_info_response = common_util.get_common_db_info_and_connection()

BEARER = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0Zk9wZXJhdG9ySWQiOiJsLXRlc3QiLCJ0Zk9wZXJhdG9yTmFtZSI6Ilx1MzBlZFx1MzBiMFx1MzBhNFx1MzBmM1x1MzBjNlx1MzBiOVx1MzBjOCIsInRmT3BlcmF0b3JQYXNzd29yZFJlc2V0RmxnIjpmYWxzZSwiYWNjZXNzVG9rZW4iOiJiZGE4ZGY3OThiYzViZGZhMWZkODIyNmRiYmQ0OTMyMTY5ZmY5MjAzNWM0YzFlY2FjZjY2OGUyYzk2ZjAwZThlZTUxNTBiNGM0NTc0NjlkN2I4YmY1NzIxZDZlM2NiNzFiY2RiYzA3ODRiYzcyZWVlNjk1OGE3NTBiMWJkMWEzZWFmZWQ0OWFhNWU0ODZjYzQyZmM3OWNhMWY3MGQzZmM3Yzc0YzE5NjM3ODUzMjRhZDRhNGM0NjkxOGE4NjQ1N2ZiODE3NDU1MCIsImV4cCI6MTY2MTc0NjY3MX0.LCRjPEqKMkRQ_phaYnO7S7pd3SU_rgon-wsX14DBsPA"
ACCESS_TOKEN = "bda8df798bc5bdfa1fd8226dbbd4932169ff92035c4c1ecacf668e2c96f00e8ee5150b4c457469d7b8bf5721d6e3cb71bcdbc0784bc72eee6958a750b1bd1a3eafed49aa5e486cc42fc79ca1f70d3fc7c74c1963785324ad4a4c46918a86457fb8174550"
HEADER = {"Content-Type": "application/json", "timeStamp": "2022/08/23 15:12:01.690", "accessToken": ACCESS_TOKEN, "Authorization": "Bearer " + BEARER}
DATA = {
    "pdsUserId": "C5100003",
    "tfContactAddress": "test@gmail.com",
    "pdsUserPublicKey": "dddd",
    "pdsUserPublicKeyIdx": 1,
    "multiDownloadFileSendAddressTo": "test1@gmail.com",
    "multiDownloadFileSendAddressCc": "test2@gmail.com",
    "multiDeleteFileSendAddressTo": "test3@gmail.com",
    "multiDeleteFileSendAddressCc": "test4@gmail.com",
    "publicKeySendAddressTo": "test5@gmail.com",
    "publicKeySendAddressCc": "test6@gmail.com"
}
TF_OPERATOR_INFO = {
    "tfOperatorId": "pc-test",
    "tfOperatorName": "変更太郎"
}
# PDSユーザテスト挿入用データ
TEST_PDS_USER_INSERT_DATA = {
    "pdsUserId": DATA["pdsUserId"],
    "groupId": "G0000001",
    "pdsUserName": "PDSユーザ更新テスト",
    "pdsUserDomainName": "token-create",
    "apiKey": None,
    "pdsUserInstanceSecretName": "pds-c0000000-sm",
    "s3ImageDataBucketName": "pds-c0000000-bucket",
    "tokyoAMongodbSecretName": "pds-c0000000-mongo-tokyo-a-sm",
    "tokyoCMongodbSecretName": "pds-c0000000-mongo-tokyo-c-sm",
    "osakaAMongodbSecretName": "pds-c0000000-mongo-osaka-a-sm",
    "osakaCMongodbSecretName": "pds-c0000000-mongo-osaka-c-sm",
    "userProfileKmsId": None,
    "validFlg": True,
    "salesAddress": "test1@gmail.com",
    "downloadNoticeAddressTo": None,
    "downloadNoticeAddressCc": None,
    "deleteNoticeAddressTo": None,
    "deleteNoticeAddressCc": None,
    "credentialNoticeAddressTo": None,
    "credentialNoticeAddressCc": None
}
# PDSユーザ公開鍵テスト挿入用データ
TEST_PDS_USER_KEY_INSERT_DATA = {
    "pdsUserId": DATA["pdsUserId"],
    "pdsKeyIdx": 1,
    "pdsKey": "+JpVou7KdEMg226QOplCEAYJD0=",
    "tfKeyKmsId": "441110cd-1a08-4f71-980b-9c3ee8d86747",
    "startDate": "2022/08/23",
    "updateDate": "2022/08/23",
    "endDate": "2022/08/23",
    "wbtSendMailId": "test0001",
    "wbtReplyDeadlineDate": "2022/08/23",
    "wbtReplyDeadlineCheckFlg": True,
    "wbtSendMailTitle": "【VRM/PDS v2.0】 PDSユーザ公開鍵通知・確認メール 1b5a05ee330f4b7ba62111e803f8de27",
    "validFlg": True
}
# アクセストークンテーブル取得SQL
ACCESS_TOKEN_PUBLIC_SELECT_SQL = """
    SELECT
        t_access_token.access_token
        , t_access_token.tf_operator_id
        , t_access_token.pds_user_id
        , t_access_token.valid_flg
        , t_access_token.period_datetime
        , t_access_token.jwt_secret_key
    FROM
        t_access_token
    WHERE
        t_access_token.access_token = %s
        AND t_access_token.pds_user_id = %s;
"""
# アクセストークンテーブル削除SQL
ACCESS_TOKEN_PUBLIC_DELETE_SQL = """
    DELETE FROM t_access_token
    WHERE
        t_access_token.access_token = %s
        AND t_access_token.pds_user_id = %s;
"""
# PDSユーザテーブル削除SQL
PDS_USER_DELETE_SQL = """
    DELETE FROM m_pds_user
    WHERE
        m_pds_user.pds_user_id = %s
        AND m_pds_user.pds_user_name = %s
        AND m_pds_user.valid_flg = %s;
"""
# PDSユーザ公開鍵テーブル削除SQL
PDS_USER_KEY_DELETE_SQL = """
    DELETE FROM m_pds_user_key
    WHERE
        m_pds_user_key.pds_user_id = %s
        AND m_pds_user_key.pds_key_idx = %s
        AND m_pds_user_key.valid_flg = %s;
"""
# アクセストークンテスト挿入用データ
TEST_ACCESS_TOKEN_INSERT_DATA = {
    "accessToken": "3a80a8eb72c836c66a188b6e188410aff0f86c9aa2f4b99af919e9809eaff47c859cc4c3a50efb04ed726efe60ab1272827b976b9b6df699f97102d3e516c50c0ad1b69349df16027b05dc8422b4784695589001f7c7a30e2d0a55e24f9e1c0e0d0e3ade",
    "tfOperatorId": "",
    "pdsUserId": DATA["pdsUserId"],
    "validFlg": True,
    "periodDatetime": "2022/09/20 17:07:19.532",
    "jwtSecretKey": "a7ed3f1a4e8d4ccb80f1de5dc67ed0dc"
}


# PDSユーザ更新テスト用クラス
class testPdsUserUpdate:
    def __init__(self):
        pass

    def insert(self):
        common_db_connection_resource: PostgresDbUtilClass = None
        common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
        common_db_connection = common_db_info_response["common_db_connection"]

        response = common_db_connection_resource.insert(
            common_db_connection,
            SqlConstClass.PDS_USER_INSERT_SQL,
            TEST_PDS_USER_INSERT_DATA["pdsUserId"],
            TEST_PDS_USER_INSERT_DATA["groupId"],
            TEST_PDS_USER_INSERT_DATA["pdsUserName"],
            TEST_PDS_USER_INSERT_DATA["pdsUserDomainName"],
            TEST_PDS_USER_INSERT_DATA["apiKey"],
            TEST_PDS_USER_INSERT_DATA["pdsUserInstanceSecretName"],
            TEST_PDS_USER_INSERT_DATA["s3ImageDataBucketName"],
            TEST_PDS_USER_INSERT_DATA["tokyoAMongodbSecretName"],
            TEST_PDS_USER_INSERT_DATA["tokyoCMongodbSecretName"],
            TEST_PDS_USER_INSERT_DATA["osakaAMongodbSecretName"],
            TEST_PDS_USER_INSERT_DATA["osakaCMongodbSecretName"],
            TEST_PDS_USER_INSERT_DATA["userProfileKmsId"],
            TEST_PDS_USER_INSERT_DATA["validFlg"],
            TEST_PDS_USER_INSERT_DATA["salesAddress"],
            TEST_PDS_USER_INSERT_DATA["downloadNoticeAddressTo"],
            TEST_PDS_USER_INSERT_DATA["downloadNoticeAddressCc"],
            TEST_PDS_USER_INSERT_DATA["deleteNoticeAddressTo"],
            TEST_PDS_USER_INSERT_DATA["deleteNoticeAddressCc"],
            TEST_PDS_USER_INSERT_DATA["credentialNoticeAddressTo"],
            TEST_PDS_USER_INSERT_DATA["credentialNoticeAddressCc"]
        )
        print(response)
        response = common_db_connection_resource.insert(
            common_db_connection,
            SqlConstClass.PDS_USER_KEY_INSERT_SQL,
            TEST_PDS_USER_KEY_INSERT_DATA["pdsUserId"],
            TEST_PDS_USER_KEY_INSERT_DATA["pdsKeyIdx"],
            TEST_PDS_USER_KEY_INSERT_DATA["pdsKey"],
            TEST_PDS_USER_KEY_INSERT_DATA["tfKeyKmsId"],
            TEST_PDS_USER_KEY_INSERT_DATA["startDate"],
            TEST_PDS_USER_KEY_INSERT_DATA["updateDate"],
            TEST_PDS_USER_KEY_INSERT_DATA["endDate"],
            TEST_PDS_USER_KEY_INSERT_DATA["wbtReplyDeadlineDate"],
            TEST_PDS_USER_KEY_INSERT_DATA["wbtReplyDeadlineCheckFlg"],
            TEST_PDS_USER_KEY_INSERT_DATA["wbtSendMailId"],
            TEST_PDS_USER_KEY_INSERT_DATA["wbtSendMailTitle"],
            TEST_PDS_USER_KEY_INSERT_DATA["validFlg"]
        )
        print(response)
        # トランザクションコミット処理
        common_db_connection_resource.commit_transaction(common_db_connection)

    def insertAccessToken(self):
        common_db_connection_resource: PostgresDbUtilClass = None
        common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
        common_db_connection = common_db_info_response["common_db_connection"]

        response = common_db_connection_resource.insert(
            common_db_connection,
            SqlConstClass.ACCESS_TOKEN_INSERT_SQL,
            TEST_ACCESS_TOKEN_INSERT_DATA["accessToken"],
            TEST_ACCESS_TOKEN_INSERT_DATA["tfOperatorId"],
            TEST_ACCESS_TOKEN_INSERT_DATA["pdsUserId"],
            TEST_ACCESS_TOKEN_INSERT_DATA["validFlg"],
            TEST_ACCESS_TOKEN_INSERT_DATA["periodDatetime"],
            TEST_ACCESS_TOKEN_INSERT_DATA["jwtSecretKey"]
        )
        print(response)
        # トランザクションコミット処理
        common_db_connection_resource.commit_transaction(common_db_connection)

    def selectPdsUser(self, pdsUserId: str, pdsUserName: str):
        common_db_connection_resource: PostgresDbUtilClass = None
        common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
        common_db_connection = common_db_info_response["common_db_connection"]

        pds_user_result = common_db_connection_resource.select_tuple_one(
            common_db_connection,
            SqlConstClass.ACCESS_TOKEN_PUBLIC_PDS_USER_TOKEN_ISSUANCE_SQL,
            pdsUserId,
            pdsUserName,
            True
        )
        print(pds_user_result)

        if pds_user_result["rowcount"] == 0:
            return {
                "rowcount": pds_user_result["rowcount"]
            }

        pds_user_column_list = [
            "pdsUserId"
        ]
        pds_user_data_list = pds_user_result["query_results"]
        pds_user_dict = {column: data for column, data in zip(pds_user_column_list, pds_user_data_list)}
        return {
            "rowcount": pds_user_result["rowcount"],
            "pdsUser": pds_user_dict
        }

    def selectAccessToken(self, accessToken: str, pdsUserId: str):
        common_db_connection_resource: PostgresDbUtilClass = None
        common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
        common_db_connection = common_db_info_response["common_db_connection"]

        access_token_result = common_db_connection_resource.select_tuple_one(
            common_db_connection,
            ACCESS_TOKEN_PUBLIC_SELECT_SQL,
            accessToken,
            pdsUserId
        )
        print(access_token_result)

        if access_token_result["rowcount"] == 0:
            return {
                "rowcount": access_token_result["rowcount"]
            }

        access_token_column_list = [
            "accessToken",
            "tfOperatorId",
            "pdsUserId",
            "validFlg",
            "periodDatetime",
            "jwtSecretKey"
        ]
        access_token_data_list = access_token_result["query_results"]
        access_token_dict = {column: data for column, data in zip(access_token_column_list, access_token_data_list)}
        return {
            "rowcount": access_token_result["rowcount"],
            "accessToken": access_token_dict
        }

    def delete(self, accessToken: str, pdsUserId: str, pdsUserName: str):
        common_db_connection_resource: PostgresDbUtilClass = None
        common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
        common_db_connection = common_db_info_response["common_db_connection"]

        responseAccessToken = common_db_connection_resource.delete(
            common_db_connection,
            ACCESS_TOKEN_PUBLIC_DELETE_SQL,
            accessToken,
            pdsUserId
        )
        print(responseAccessToken)

        responsePdsUser = common_db_connection_resource.delete(
            common_db_connection,
            PDS_USER_DELETE_SQL,
            pdsUserId,
            pdsUserName,
            True
        )
        print(responsePdsUser)

        responsePdsUser = common_db_connection_resource.delete(
            common_db_connection,
            PDS_USER_KEY_DELETE_SQL,
            pdsUserId,
            "1",
            True
        )
        print(responsePdsUser)

        # トランザクションコミット処理
        common_db_connection_resource.commit_transaction(common_db_connection)


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


@pytest.fixture
def db():
    test = testPdsUserUpdate()
    result = test.selectPdsUser(TEST_PDS_USER_INSERT_DATA["pdsUserId"], TEST_PDS_USER_INSERT_DATA["pdsUserName"])
    if result["rowcount"] == 0:
        test.insert()
    return test


# No1.01.メイン処理_01.アクセストークン検証処理　異常系　アクセストークン検証処理が失敗する
# No3.01.メイン処理_02.共通エラーチェック処理　正常系　共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_update_case1(create_header):
    header = create_header["header"]
    header["accessToken"] = "518302174323385ee79afc2e37e3783f15e48e43d75f004a83e41667996087770c5e474023c0d6969529b49a8fd553ca454e54adbf473ac1a129fd4b0314abc4d4f33e4349749110f5b1774db69d5f87944e3a86c7d3ee10390a825f8bf35f1813774c94"
    response = client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))
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
# No8.01.メイン処理_05.DB接続準備処理　正常系　接続に成功する
# No10.01.メイン処理_06.PDSユーザ鍵存在検証処理　正常系　PDSユーザ鍵存在検証処理が成功する
# No13.01.メイン処理_08.トランザクション作成処理　正常系　トランザクション作成処理が成功する
# No15.01.メイン処理_09.PDSユーザ更新処理　正常系　PDSユーザ更新処理が成功する
# No17.01.メイン処理_11.PDSユーザ公開鍵更新処理　正常系　PDSユーザ公開鍵更新処理が成功する
# No21.01.メイン処理_13.トランザクションコミット処理　正常系　トランザクションコミット処理が成功する
# No23.01.メイン処理_14.アクセストークン発行処理　正常系　アクセストークン発行処理が成功する
# No26.01.メイン処理_16.終了処理　正常系　変数．エラー情報がない
def test_pds_user_update_case2(db: testPdsUserUpdate, create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())

    # 最後にテスト用に挿入したデータを削除する
    db.delete(response.json()["accessToken"], TEST_PDS_USER_INSERT_DATA["pdsUserId"], TEST_PDS_USER_INSERT_DATA["pdsUserName"])


# No4.01.メイン処理_03.パラメータ検証処理　異常系　パラメータ検証処理が失敗する
def test_pds_user_update_case4(create_header):
    header = create_header["header"]
    header["timeStamp"] = ""
    response = client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))
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


# No6.01.メイン処理_04.共通エラーチェック処理　正常系　共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_update_case6(create_header):
    header = create_header["header"]
    header["timeStamp"] = ""
    response = client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))
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


# No07.01.メイン処理_05.DB接続準備処理　異常系　接続に失敗する
# 設定値を異常な値に変更する
def test_pds_user_update_case7(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.commonUtil.CommonUtilClass.get_secret_info").return_value = {"host": "test", "port": "test", "username": "test", "password": "test"}
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))
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


# No9.01.メイン処理_06.PDSユーザ鍵存在検証処理　異常系　PDSユーザ鍵存在検証処理が失敗する
# No11.01.メイン処理_07.共通エラーチェック処理　正常系　共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_update_case9(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "030013",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No14.01.メイン処理_09.PDSユーザ更新処理　異常系　PDSユーザ更新処理が失敗する
# No16.01.メイン処理_10.共通エラーチェック処理　正常系　共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_update_case14(mocker: MockerFixture, db: testPdsUserUpdate, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "PDS_USER_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))
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

    # 最後にテスト用に挿入したデータを削除する
    db.delete(header["accessToken"], TEST_PDS_USER_INSERT_DATA["pdsUserId"], TEST_PDS_USER_INSERT_DATA["pdsUserName"])


# No17.01.メイン処理_11.PDSユーザ公開鍵更新処理　異常系　PDSユーザ公開鍵更新処理が失敗する
# No19.01.メイン処理_12.共通エラーチェック処理　正常系　共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_update_case17(mocker: MockerFixture, db: testPdsUserUpdate, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "PDS_USER_UPDATE_SQL_PDS_USER_KEY_CONDITION", """ SELECT * FROM AAAAAA; """)
    response = client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))
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

    # 最後にテスト用に挿入したデータを削除する
    db.delete(header["accessToken"], TEST_PDS_USER_INSERT_DATA["pdsUserId"], TEST_PDS_USER_INSERT_DATA["pdsUserName"])


# No20.01.メイン処理_トランザクションコミット処理　異常系　トランザクションコミット処理が失敗する
def test_pds_user_update_case20(mocker: MockerFixture, db: testPdsUserUpdate, create_header):
    # Exception
    mocker.patch.object(PostgresDbUtilClass, "commit_transaction", side_effect=Exception('testException'))
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": response.json()["errorInfo"]
    }
    print(response.json())


# No22.01.メイン処理_22.アクセストークン発行処理　異常系　アクセストークン発行処理が失敗する
def test_pds_user_update_case22(mocker: MockerFixture, db: testPdsUserUpdate, create_header):
    mocker.patch("util.tokenUtil.TokenUtilClass.verify_token_closed").return_value = {'result': True, 'payload': {'tfOperatorId': 't-test4', 'tfOperatorName': 'テスト', 'accessToken': '14d517e61315fbf0545b765dd0e7ca296d65a5403aef84a360efe191e8b6d28a6c30dda7557e269b8c800327a13fa3ce5833fc0351c884addb340921883eac40d03d92281ac6a7cf18c32aebfd6bf48c71aedc781f707ca0714b3c804c1526e2d2a6ad0a'}}
    mocker.patch("util.tokenUtil.TokenUtilClass.create_token_closed").return_value = Exception('testException')
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": response.json()["errorInfo"]
    }
    print(response.json())


# No24.01.メイン処理_15.共通エラーチェック処理　正常系　共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_update_case24(mocker: MockerFixture, db: testPdsUserUpdate, create_header):
    mocker.patch("util.tokenUtil.TokenUtilClass.verify_token_closed").return_value = {'result': True, 'payload': {'tfOperatorId': 't-test4', 'tfOperatorName': 'テスト', 'accessToken': '14d517e61315fbf0545b765dd0e7ca296d65a5403aef84a360efe191e8b6d28a6c30dda7557e269b8c800327a13fa3ce5833fc0351c884addb340921883eac40d03d92281ac6a7cf18c32aebfd6bf48c71aedc781f707ca0714b3c804c1526e2d2a6ad0a'}}
    mocker.patch("util.tokenUtil.TokenUtilClass.create_token_closed").return_value = Exception('testException')
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": response.json()["errorInfo"]
    }
    print(response.json())


# No25.01.メイン処理_16.終了処理　変数．エラー情報がある
def test_pds_user_update_case25(mocker: MockerFixture, db: testPdsUserUpdate, create_header):
    mocker.patch("util.tokenUtil.TokenUtilClass.verify_token_closed").return_value = {'result': True, 'payload': {'tfOperatorId': 't-test4', 'tfOperatorName': 'テスト', 'accessToken': '14d517e61315fbf0545b765dd0e7ca296d65a5403aef84a360efe191e8b6d28a6c30dda7557e269b8c800327a13fa3ce5833fc0351c884addb340921883eac40d03d92281ac6a7cf18c32aebfd6bf48c71aedc781f707ca0714b3c804c1526e2d2a6ad0a'}}
    mocker.patch("util.tokenUtil.TokenUtilClass.create_token_closed").return_value = Exception('testException')
    header = create_header["header"]
    response = client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": response.json()["errorInfo"]
    }
    print(response.json())


# No27.01.メイン処理_03.引数検証処理チェック処理　異常系　引数．ヘッダパラメータ．タイムスタンプ　値が設定されていない（空値）
# No29.01.メイン処理_04.共通エラーチェック処理　正常系　共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_update_case27_1_1(create_header):
    header = create_header["header"]
    header["timeStamp"] = ""
    response = client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))
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


# No27.01.メイン処理_03.引数検証処理チェック処理　異常系　引数．ヘッダパラメータ．タイムスタンプ　値が設定されている　文字列型である　２４桁である　入力規則違反している　hh:mmがhhh:mm
# No29.01.メイン処理_04.共通エラーチェック処理　正常系　共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_update_case27_1_2(create_header):
    header = create_header["header"]
    header["timeStamp"] = "2022/08/23 155:12:01.690"
    response = client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))
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


# No27.01.メイン処理_03.引数検証処理チェック処理　異常系　引数．ヘッダパラメータ．タイムスタンプ　値が設定されている　文字列型ではない
# No29.01.メイン処理_04.共通エラーチェック処理　正常系　共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_update_case27_1_3(create_header):
    header = create_header["header"]
    header["timeStamp"] = 12345678901234567890123
    response = client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))
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


# No27.01.メイン処理_03.引数検証処理チェック処理　異常系　引数．ヘッダパラメータ．アクセストークン　値が設定されていない（空値）
# No29.01.メイン処理_04.共通エラーチェック処理　正常系　共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_update_case27_2_1(create_header):
    header = create_header["header"]
    header["accessToken"] = ""
    response = client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))
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


# No27.01.メイン処理_03.引数検証処理チェック処理　異常系　引数．ヘッダパラメータ．アクセストークン　値が設定されている　文字列型である　２０１桁である　入力可能文字以外が含まれる（全角）
# No29.01.メイン処理_04.共通エラーチェック処理　正常系　共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_update_case27_2_2(create_header):
    header = create_header["header"]
    header["accessToken"] = "１2345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890"
    response = client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))
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


# No27.01.メイン処理_03.引数検証処理チェック処理　異常系　引数．ヘッダパラメータ．アクセストークン　値が設定されている　文字列型ではない
# No29.01.メイン処理_04.共通エラーチェック処理　正常系　共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_update_case27_2_3(create_header):
    header = create_header["header"]
    header["accessToken"] = 12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
    response = client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))
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


# No27.01.メイン処理_03.引数検証処理チェック処理　異常系　引数．リクエストボディ．PDSユーザID
def test_pds_user_update_case27_3_1(create_header):
    header = create_header["header"]
    DATA["pdsUserId"] = ""
    response = client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))
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


# No27.01.メイン処理_03.引数検証処理チェック処理　異常系　引数．リクエストボディ．PDSユーザID
def test_pds_user_update_case27_3_2(create_header):
    header = create_header["header"]
    DATA["pdsUserId"] = 12
    response = client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))
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


# No27.01.メイン処理_03.引数検証処理チェック処理　異常系　引数．リクエストボディ．TF担当者メールアドレス
def test_pds_user_update_case27_4_1(create_header):
    header = create_header["header"]
    DATA["tfContactAddress"] = ""
    response = client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
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
            },
            {
                "errorCode": "020003",
                "message": response.json()["errorInfo"][2]["message"]
            }
        ]
    }
    print(response.json())


# No27.01.メイン処理_03.引数検証処理チェック処理　異常系　引数．リクエストボディ．TF担当者メールアドレス
def test_pds_user_update_case27_4_2(create_header):
    header = create_header["header"]
    DATA["tfContactAddress"] = 12
    response = client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
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


# No27.01.メイン処理_03.引数検証処理チェック処理　異常系　引数．リクエストボディ．PDSユーザ公開鍵
def test_pds_user_update_case27_5_1(create_header):
    header = create_header["header"]
    DATA["pdsUserPublicKey"] = ""
    response = client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))
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


# No27.01.メイン処理_03.引数検証処理チェック処理　異常系　引数．リクエストボディ．PDSユーザ公開鍵
def test_pds_user_update_case27_5_2(create_header):
    header = create_header["header"]
    DATA["pdsUserPublicKey"] = 12
    response = client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))
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


# No27.01.メイン処理_03.引数検証処理チェック処理　異常系　引数．リクエストボディ．PDSユーザ公開鍵インデックス
def test_pds_user_update_case27_6_1(create_header):
    header = create_header["header"]
    DATA["pdsUserPublicKeyIdx"] = ""
    response = client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020001",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020019",
                "message": response.json()["errorInfo"][1]["message"]
            }
        ]
    }
    print(response.json())


# No27.01.メイン処理_03.引数検証処理チェック処理　異常系　引数．リクエストボディ．PDSユーザ公開鍵インデックス
def test_pds_user_update_case27_6_2(create_header):
    header = create_header["header"]
    DATA["pdsUserPublicKeyIdx"] = "1"
    response = client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))
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


# No27.01.メイン処理_03.引数検証処理チェック処理　異常系　引数．リクエストボディ．PDSユーザ公開鍵インデックス
def test_pds_user_update_case27_6_3(create_header):
    header = create_header["header"]
    DATA["pdsUserPublicKeyIdx"] = "a"
    response = client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))
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


# No27.01.メイン処理_03.引数検証処理チェック処理　異常系　引数．リクエストボディ．一括DL送付先アドレスTo
def test_pds_user_update_case27_7_1(create_header):
    header = create_header["header"]
    DATA["multiDownloadFileSendAddressTo"] = ""
    response = client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
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
            },
            {
                "errorCode": "020003",
                "message": response.json()["errorInfo"][2]["message"]
            }
        ]
    }
    print(response.json())


# No27.01.メイン処理_03.引数検証処理チェック処理　異常系　引数．リクエストボディ．一括DL送付先アドレスTo
def test_pds_user_update_case27_7_2(create_header):
    header = create_header["header"]
    DATA["multiDownloadFileSendAddressTo"] = 12345
    response = client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))
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


# No27.01.メイン処理_03.引数検証処理チェック処理　異常系　引数．リクエストボディ．一括DL送付先アドレスTo
def test_pds_user_update_case27_7_3(create_header):
    header = create_header["header"]
    DATA["multiDownloadFileSendAddressTo"] = "1234"
    response = client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))
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


# No27.01.メイン処理_03.引数検証処理チェック処理　異常系　引数．リクエストボディ．一括DL送付先アドレスCc
def test_pds_user_update_case27_8_1(create_header):
    header = create_header["header"]
    DATA["multiDownloadFileSendAddressCc"] = ""
    response = client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
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
            },
            {
                "errorCode": "020003",
                "message": response.json()["errorInfo"][2]["message"]
            }
        ]
    }
    print(response.json())


# No27.01.メイン処理_03.引数検証処理チェック処理　異常系　引数．リクエストボディ．一括DL送付先アドレスCc
def test_pds_user_update_case27_8_2(create_header):
    header = create_header["header"]
    DATA["multiDownloadFileSendAddressCc"] = 12345
    response = client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))
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


# No27.01.メイン処理_03.引数検証処理チェック処理　異常系　引数．リクエストボディ．一括DL送付先アドレスCc
def test_pds_user_update_case27_8_3(create_header):
    header = create_header["header"]
    DATA["multiDownloadFileSendAddressCc"] = "1234"
    response = client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))
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


# No27.01.メイン処理_03.引数検証処理チェック処理　異常系　引数．リクエストボディ．一括削除送付先アドレスTo
def test_pds_user_update_case27_9_1(create_header):
    header = create_header["header"]
    DATA["multiDeleteFileSendAddressTo"] = ""
    response = client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
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
            },
            {
                "errorCode": "020003",
                "message": response.json()["errorInfo"][2]["message"]
            }
        ]
    }
    print(response.json())


# No27.01.メイン処理_03.引数検証処理チェック処理　異常系　引数．リクエストボディ．一括削除送付先アドレスTo
def test_pds_user_update_case27_9_2(create_header):
    header = create_header["header"]
    DATA["multiDeleteFileSendAddressTo"] = 12345
    response = client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))
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


# No27.01.メイン処理_03.引数検証処理チェック処理　異常系　引数．リクエストボディ．一括削除送付先アドレスTo
def test_pds_user_update_case27_9_3(create_header):
    header = create_header["header"]
    DATA["multiDeleteFileSendAddressTo"] = "1234"
    response = client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))
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


# No27.01.メイン処理_03.引数検証処理チェック処理　異常系　引数．リクエストボディ．一括削除送付先アドレスCc
def test_pds_user_update_case27_10_1(create_header):
    header = create_header["header"]
    DATA["multiDeleteFileSendAddressCc"] = ""
    response = client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
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
            },
            {
                "errorCode": "020003",
                "message": response.json()["errorInfo"][2]["message"]
            }
        ]
    }
    print(response.json())


# No27.01.メイン処理_03.引数検証処理チェック処理　異常系　引数．リクエストボディ．一括削除送付先アドレスCc
def test_pds_user_update_case27_10_2(create_header):
    header = create_header["header"]
    DATA["multiDeleteFileSendAddressCc"] = 12345
    response = client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))
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


# No27.01.メイン処理_03.引数検証処理チェック処理　異常系　引数．リクエストボディ．一括削除送付先アドレスCc
def test_pds_user_update_case27_10_3(create_header):
    header = create_header["header"]
    DATA["multiDeleteFileSendAddressCc"] = "1234"
    response = client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))
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


# No27.01.メイン処理_03.引数検証処理チェック処理　異常系　引数．リクエストボディ．公開鍵送付先アドレスTo
def test_pds_user_update_case27_11_1(create_header):
    header = create_header["header"]
    DATA["publicKeySendAddressTo"] = ""
    response = client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
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
            },
            {
                "errorCode": "020003",
                "message": response.json()["errorInfo"][2]["message"]
            }
        ]
    }
    print(response.json())


# No27.01.メイン処理_03.引数検証処理チェック処理　異常系　引数．リクエストボディ．公開鍵送付先アドレスTo
def test_pds_user_update_case27_11_2(create_header):
    header = create_header["header"]
    DATA["publicKeySendAddressTo"] = 12345
    response = client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))
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


# No27.01.メイン処理_03.引数検証処理チェック処理　異常系　引数．リクエストボディ．公開鍵送付先アドレスTo
def test_pds_user_update_case27_11_3(create_header):
    header = create_header["header"]
    DATA["publicKeySendAddressTo"] = "1234"
    response = client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))
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


# No27.01.メイン処理_03.引数検証処理チェック処理　異常系　引数．リクエストボディ．公開鍵送付先アドレスCc
def test_pds_user_update_case27_12_1(create_header):
    header = create_header["header"]
    DATA["publicKeySendAddressCc"] = ""
    response = client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
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
            },
            {
                "errorCode": "020003",
                "message": response.json()["errorInfo"][2]["message"]
            }
        ]
    }
    print(response.json())


# No27.01.メイン処理_03.引数検証処理チェック処理　異常系　引数．リクエストボディ．公開鍵送付先アドレスCc
def test_pds_user_update_case27_12_2(create_header):
    header = create_header["header"]
    DATA["publicKeySendAddressCc"] = 12345
    response = client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))
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


# No27.01.メイン処理_03.引数検証処理チェック処理　異常系　引数．リクエストボディ．公開鍵送付先アドレスCc
def test_pds_user_update_case27_12_3(create_header):
    header = create_header["header"]
    DATA["publicKeySendAddressCc"] = "1234"
    response = client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))
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


# No30.ロールバック処理_01.ロールバック処理　PDSユーザ更新トランザクションのロールバック処理が失敗する
def test_pds_user_update_case30(mocker: MockerFixture, db: testPdsUserUpdate, create_header):
    header = create_header["header"]
    # Exception
    mocker.patch.object(SqlConstClass, "PDS_USER_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    # Exception
    mocker.patch.object(PostgresDbUtilClass, "rollback_transaction", side_effect=Exception('testException'))
    client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))

    # 最後にテスト用に挿入したデータを削除する
    db.delete(header["accessToken"], TEST_PDS_USER_INSERT_DATA["pdsUserId"], TEST_PDS_USER_INSERT_DATA["pdsUserName"])


# No31.ロールバック処理_01.ロールバック処理　ロールバック処理が成功すること
def test_pds_user_update_case31(mocker: MockerFixture, db: testPdsUserUpdate, create_header):
    header = create_header["header"]
    # Exception
    mocker.patch.object(SqlConstClass, "PDS_USER_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))

    # 最後にテスト用に挿入したデータを削除する
    db.delete(header["accessToken"], TEST_PDS_USER_INSERT_DATA["pdsUserId"], TEST_PDS_USER_INSERT_DATA["pdsUserName"])


# No32.ロールバック処理_02.共通エラーチェック処理　共通エラーチェック処理が成功（エラー情報有り）
def test_pds_user_update_case32(mocker: MockerFixture, db: testPdsUserUpdate, create_header):
    header = create_header["header"]
    # Exception
    mocker.patch.object(SqlConstClass, "PDS_USER_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    # Exception
    mocker.patch.object(PostgresDbUtilClass, "rollback_transaction", side_effect=Exception('testException'))
    client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))

    # 最後にテスト用に挿入したデータを削除する
    db.delete(header["accessToken"], TEST_PDS_USER_INSERT_DATA["pdsUserId"], TEST_PDS_USER_INSERT_DATA["pdsUserName"])


# No33.ロールバック処理_03.終了処理　変数．エラー情報がない
def test_pds_user_update_case33(mocker: MockerFixture, db: testPdsUserUpdate, create_header):
    header = create_header["header"]
    # Exception
    mocker.patch.object(SqlConstClass, "PDS_USER_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    client.post("/api/2.0/pdsuser/update", headers=header, data=json.dumps(DATA))

    # 最後にテスト用に挿入したデータを削除する
    db.delete(header["accessToken"], TEST_PDS_USER_INSERT_DATA["pdsUserId"], TEST_PDS_USER_INSERT_DATA["pdsUserName"])
