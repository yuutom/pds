from fastapi.testclient import TestClient
from util.commonUtil import CommonUtilClass
from app import app
from fastapi import Request
import pytest
from pytest_mock.plugin import MockerFixture
from util.tokenUtil import TokenUtilClass
import util.logUtil as logUtil
from exceptionClass.PDSException import PDSException
from const.messageConst import MessageConstClass
from util.postgresDbUtil import PostgresDbUtilClass
from const.systemConst import SystemConstClass

# 定数クラス
from const.sqlConst import SqlConstClass

client = TestClient(app)

HEADER = {"pdsUserId": "C5100002", "pdsUserName": "アクセストークン発行テスト"}

trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
token_util = TokenUtilClass(trace_logger)
common_util = CommonUtilClass(trace_logger)
# 共通DB接続準備処理
common_db_info_response = common_util.get_common_db_info_and_connection()
# 検証に使用するデータ
DATA = {
    "pdsUserId": HEADER["pdsUserId"],
    "pdsUserName": HEADER["pdsUserName"],
    "accessToken": None
}
# テスト挿入用データ
TEST_INSERT_DATA = {
    "pdsUserId": HEADER["pdsUserId"],
    "groupId": "G0000001",
    "pdsUserName": HEADER["pdsUserName"],
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
# アクセストークン無効化テスト挿入用データ
TEST_ACCESS_TOKEN_INSERT_DATA = {
    "accessToken": "3a80a8eb72c836c66a188b6e188410aff0f86c9aa2f4b99af919e9809eaff47c859cc4c3a50efb04ed726efe60ab1272827b976b9b6df699f97102d3e516c50c0ad1b69349df16027b05dc8422b4784695589001f7c7a30e2d0a55e24f9e1c0e0d0e3ade",
    "tfOperatorId": "",
    "pdsUserId": HEADER["pdsUserId"],
    "validFlg": True,
    "periodDatetime": "2022/09/20 17:07:19.532",
    "jwtSecretKey": "a7ed3f1a4e8d4ccb80f1de5dc67ed0dc"
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


# テスト用のアクセストークン発行クラス
class testAccessToken:
    def __init__(self):
        pass

    def insert(self):
        common_db_connection_resource: PostgresDbUtilClass = None
        common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
        common_db_connection = common_db_info_response["common_db_connection"]

        response = common_db_connection_resource.insert(
            common_db_connection,
            SqlConstClass.PDS_USER_INSERT_SQL,
            TEST_INSERT_DATA["pdsUserId"],
            TEST_INSERT_DATA["groupId"],
            TEST_INSERT_DATA["pdsUserName"],
            TEST_INSERT_DATA["pdsUserDomainName"],
            TEST_INSERT_DATA["apiKey"],
            TEST_INSERT_DATA["pdsUserInstanceSecretName"],
            TEST_INSERT_DATA["s3ImageDataBucketName"],
            TEST_INSERT_DATA["tokyoAMongodbSecretName"],
            TEST_INSERT_DATA["tokyoCMongodbSecretName"],
            TEST_INSERT_DATA["osakaAMongodbSecretName"],
            TEST_INSERT_DATA["osakaCMongodbSecretName"],
            TEST_INSERT_DATA["userProfileKmsId"],
            TEST_INSERT_DATA["validFlg"],
            TEST_INSERT_DATA["salesAddress"],
            TEST_INSERT_DATA["downloadNoticeAddressTo"],
            TEST_INSERT_DATA["downloadNoticeAddressCc"],
            TEST_INSERT_DATA["deleteNoticeAddressTo"],
            TEST_INSERT_DATA["deleteNoticeAddressCc"],
            TEST_INSERT_DATA["credentialNoticeAddressTo"],
            TEST_INSERT_DATA["credentialNoticeAddressCc"]
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

        # トランザクションコミット処理
        common_db_connection_resource.commit_transaction(common_db_connection)


@pytest.fixture
def db():
    test = testAccessToken()
    result = test.selectPdsUser(HEADER["pdsUserId"], HEADER["pdsUserName"])
    if result["rowcount"] == 0:
        test.insert()
    return test


# No1.アクセストークン発行処理（公開用）_01.引数検証処理チェック　異常系　引数．PDSユーザID　値が設定されていない（空値）
# No2.アクセストークン発行処理（公開用）_01.引数検証処理チェック　異常系　PDSユーザIDが異常な値
def test_create_token_public_case1_1_1():
    data_copy = DATA.copy()
    data_copy["pdsUserId"] = ""
    with pytest.raises(PDSException) as e:
        token_util.create_token_public(
            pdsUserId=data_copy["pdsUserId"],
            pdsUserName=data_copy["pdsUserName"],
            accessToken=data_copy["accessToken"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "PDSユーザID")
    }
    print(e)


# No1.アクセストークン発行処理（公開用）_01.引数検証処理チェック　異常系　引数．PDSユーザ名　値が設定されていない（空値）
def test_create_token_public_case1_2_1():
    data_copy = DATA.copy()
    data_copy["pdsUserName"] = ""
    with pytest.raises(PDSException) as e:
        token_util.create_token_public(
            pdsUserId=data_copy["pdsUserId"],
            pdsUserName=data_copy["pdsUserName"],
            accessToken=data_copy["accessToken"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "PDSユーザ名")
    }
    print(e)


# No1.アクセストークン発行処理（公開用）_01.引数検証処理チェック　異常系　引数．PDSユーザ名　文字列型ではない
# TODO:Exceptionで落ちる(文字列以外で桁数を測れない)
def test_create_token_public_case1_2_2():
    data_copy = DATA.copy()
    data_copy["pdsUserName"] = 12
    with pytest.raises(PDSException) as e:
        token_util.create_token_public(
            pdsUserId=data_copy["pdsUserId"],
            pdsUserName=data_copy["pdsUserName"],
            accessToken=data_copy["accessToken"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020019",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "PDSユーザ名", "文字列")
    }
    print(e)


# No1.アクセストークン発行処理（公開用）_01.引数検証処理チェック　異常系　引数．PDSユーザ名　文字列型である　65桁である
def test_create_token_public_case1_2_3():
    data_copy = DATA.copy()
    data_copy["pdsUserName"] = "あいうえおかきくけこさしすせそたちつてとｱｲｳｴｵｶｷｸｹｺアイウエオカキクケコABCDEFGHIJＡＢＣＤＥＦＧＨＩＪ亜阿吾蛙伊"
    with pytest.raises(PDSException) as e:
        token_util.create_token_public(
            pdsUserId=data_copy["pdsUserId"],
            pdsUserName=data_copy["pdsUserName"],
            accessToken=data_copy["accessToken"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020002",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020002"]["message"], "PDSユーザ名", "64")
    }
    print(e)


# No1.アクセストークン発行処理（公開用）_01.引数検証処理チェック　異常系　引数．PDSユーザ名　文字列型である　64桁である　入力規則違反している（半角数値）
# TODO:入力不可文字を確認する
def test_create_token_public_case1_2_4():
    data_copy = DATA.copy()
    data_copy["pdsUserName"] = "%()うえおかきくけこさしすせそたちつてとｱｲｳｴｵｶｷｸｹｺアイウエオカキクケコABCDEFGHIJＡＢＣＤＥＦＧＨＩＪ亜阿吾"
    with pytest.raises(PDSException) as e:
        token_util.create_token_public(
            pdsUserId=data_copy["pdsUserId"],
            pdsUserName=data_copy["pdsUserName"],
            accessToken=data_copy["accessToken"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020020",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020020"]["message"], "PDSユーザ名")
    }
    print(e)


# No1.アクセストークン発行処理（公開用）_01.引数検証処理チェック　正常系　引数．PDSユーザ名　文字列型である　64桁である　入力規則違反していない
def test_create_token_public_case1_2_5(db: testAccessToken):
    data_copy = DATA.copy()
    data_copy["pdsUserName"] = "あいうえおかきくけこさしすせそたちつてとｱｲｳｴｵｶｷｸｹｺアイウエオカキクケコABCDEFGHIJＡＢＣＤＥＦＧＨＩＪ亜阿吾蛙"
    response = token_util.create_token_public(
        pdsUserId=data_copy["pdsUserId"],
        pdsUserName=data_copy["pdsUserName"],
        accessToken=data_copy["accessToken"]
    )
    assert response == {
        "result": True,
        "accessToken": response["accessToken"],
        "jwt": response["jwt"]

    }
    print(response)

    # 最後にテスト用に挿入したデータを削除する
    db.delete(response["accessToken"], data_copy["pdsUserId"], data_copy["pdsUserName"])


# No1.アクセストークン発行処理（公開用）_01.引数検証処理チェック　正常系　引数．PDSユーザID　値が設定されている
# No3.アクセストークン発行処理（公開用）_01.引数検証処理チェック　正常系　PDSユーザIDが正常な値
# No5.アクセストークン発行処理（公開用）_01.引数検証処理チェック　正常系　アクセストークンが正常な値
# No7.アクセストークン発行処理（公開用）_02.DB接続準備処理　正常系　接続に成功する
# No10.アクセストークン発行処理（公開用）_03.PDSユーザ取得処理　正常系　PDSユーザ取得処理で取得結果が1件
# No11.アクセストークン発行処理（公開用）_04.PDSユーザ取得チェック処理　正常系　「変数．エラー情報」が設定されていない場合、「06.JWT作成処理」に遷移する
# No14.アクセストークン発行処理（公開用）_06.JWT作成処理　正常系　JWT作成処理が成功する
# No15.アクセストークン発行処理（公開用）_07.トランザクション作成処理　正常系　アクセストークン発行トランザクションを作成する
# No17.アクセストークン発行処理（公開用）_08.アクセストークン判定処理　正常系　引数．アクセストークンがない
# No25.アクセストークン発行処理（公開用）_13.アクセストークン登録処理　正常系　アクセストークン登録処理が成功する
# No26.アクセストークン発行処理（公開用）_14.アクセストークン登録チェック処理　正常系　「変数．エラー情報」が設定されていない場合、「17.終了処理」に遷移する
# No28.アクセストークン発行処理（公開用）_14.アクセストークン登録チェック処理　正常系　アクセストークン登録処理が成功する
# No31.アクセストークン発行処理（公開用）_17.トランザクションコミット処理　正常系　アクセストークン登録処理が成功する
# No32.アクセストークン発行処理（公開用）_18.終了処理　正常系　変数．エラー情報がない
def test_create_token_public_case1_1_2(db: testAccessToken):
    data_copy = DATA.copy()
    response = token_util.create_token_public(
        pdsUserId=data_copy["pdsUserId"],
        pdsUserName=data_copy["pdsUserName"],
        accessToken=data_copy["accessToken"]
    )
    assert response == {
        "result": True,
        "accessToken": response["accessToken"],
        "jwt": response["jwt"]
    }
    print(response)

    # 最後にテスト用に挿入したデータを削除する
    db.delete(response["accessToken"], data_copy["pdsUserId"], data_copy["pdsUserName"])


# No4.アクセストークン発行処理（公開用）_04.PDSユーザ取得チェック処理　異常系　アクセストークンが異常な値
def test_create_token_public_case4():
    data_copy = DATA.copy()
    data_copy["accessToken"] = "%"
    with pytest.raises(PDSException) as e:
        token_util.create_token_public(
            pdsUserId=data_copy["pdsUserId"],
            pdsUserName=data_copy["pdsUserName"],
            accessToken=data_copy["accessToken"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020014",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020014"]["message"], "アクセストークン", "200")
    }
    assert e.value.args[1] == {
        "errorCode": "020003",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "アクセストークン")
    }
    print(e)


# No6.アクセストークン発行処理（公開用）_02.DB接続準備処理　異常系　接続に失敗する　設定値を異常な値に変更する
def test_create_token_public_case6(mocker: MockerFixture):
    data_copy = DATA.copy()
    mocker.patch("util.commonUtil.CommonUtilClass.get_secret_info").return_value = {"host": "test", "port": "test", "username": "test", "password": "test"}
    response = token_util.create_token_public(
        pdsUserId=data_copy["pdsUserId"],
        pdsUserName=data_copy["pdsUserName"],
        accessToken=data_copy["accessToken"]
    )
    assert response == {
        "result": False,
        'errorInfo': {
            'errorCode': '999999',
            'message': logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
        }
    }
    print(response)


# No8.アクセストークン発行処理（公開用）_03.PDSユーザ取得処理　異常系　PDSユーザ取得処理で取得結果が1件以外
# No12.アクセストークン発行処理（公開用）_04.PDSユーザ取得チェック処理　正常系　「変数．エラー情報」が設定されている場合、「05.PDSユーザ取得エラー処理」に遷移する
# No13.アクセストークン発行処理（公開用）_05.PDSユーザ取得エラー処理　正常系　レスポンス情報を作成し、返却する
def test_create_token_public_case8():
    data_copy = DATA.copy()
    response = token_util.create_token_public(
        pdsUserId=data_copy["pdsUserId"],
        pdsUserName=data_copy["pdsUserName"],
        accessToken=data_copy["accessToken"]
    )
    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "020004",
            "message": logUtil.message_build(MessageConstClass.ERRORS["020004"]["logMessage"], data_copy["pdsUserId"])
        }
    }
    print(response)


# No9.アクセストークン発行処理（公開用）_03.PDSユーザ取得処理　異常系　postgresqlのエラーが発生
def test_create_token_public_case9(mocker: MockerFixture):
    data_copy = DATA.copy()
    mocker.patch.object(SqlConstClass, "ACCESS_TOKEN_PUBLIC_PDS_USER_TOKEN_ISSUANCE_SQL", """ SELECT * FROM AAAAAA; """)
    response = token_util.create_token_public(
        pdsUserId=data_copy["pdsUserId"],
        pdsUserName=data_copy["pdsUserName"],
        accessToken=data_copy["accessToken"]
    )
    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "999999",
            "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
        }
    }
    print(response)


# No16.アクセストークン発行処理（公開用）_08.アクセストークン判定処理　正常系　引数．アクセストークンがある
# No19.アクセストークン発行処理（公開用）_09.アクセストークン無効処理　正常系　アクセストークン無効処理が成功する
# No20.アクセストークン発行処理（公開用）_10.アクセストークン無効チェック処理　正常系　「変数．エラー情報」が設定されていない場合、「13.アクセストークン登録処理」に遷移する
def test_create_token_public_case16(db: testAccessToken):
    db.insertAccessToken()
    data_copy = DATA.copy()
    data_copy["accessToken"] = TEST_ACCESS_TOKEN_INSERT_DATA["accessToken"]
    response = token_util.create_token_public(
        pdsUserId=data_copy["pdsUserId"],
        pdsUserName=data_copy["pdsUserName"],
        accessToken=data_copy["accessToken"]
    )
    assert response == {
        "result": True,
        "accessToken": response["accessToken"],
        "jwt": response["jwt"]

    }
    print(response)

    # 最後にテスト用に挿入したデータを削除する
    db.delete(response["accessToken"], data_copy["pdsUserId"], data_copy["pdsUserName"])


# No18.アクセストークン発行処理（公開用）_09.アクセストークン無効処理　異常系　引数．アクセストークンがある場合　アクセストークン無効処理が失敗する
# No23.アクセストークン発行処理（公開用）_12.アクセストークン無効エラー処理　正常系　レスポンス情報を作成し、返却する
def test_create_token_public_case18(db: testAccessToken, mocker: MockerFixture):
    db.insertAccessToken()
    mocker.patch("const.sqlConst.SqlConstClass.ACCESS_TOKEN_PUBLIC_UPDATE_SQL").return_value = """ SELECT * FROM AAAAAA; """
    data_copy = DATA.copy()
    data_copy["accessToken"] = TEST_ACCESS_TOKEN_INSERT_DATA["accessToken"]
    response = token_util.create_token_public(
        pdsUserId=data_copy["pdsUserId"],
        pdsUserName=data_copy["pdsUserName"],
        accessToken=data_copy["accessToken"]
    )
    assert response == {
        "result": False,
        "errorInfo": response["errorInfo"]
    }
    print(response)

    # 最後にテスト用に挿入したデータを削除する
    db.delete(data_copy["accessToken"], data_copy["pdsUserId"], data_copy["pdsUserName"])


# No21.アクセストークン発行処理（公開用）_10.アクセストークン無効チェック処理　正常系　「変数．エラー情報」が設定されている場合、「11.アクセストークン無効エラー処理」に遷移する
def test_create_token_public_case21(mocker: MockerFixture, db: testAccessToken):
    # Exception
    mocker.patch.object(SqlConstClass, "ACCESS_TOKEN_PUBLIC_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    data_copy = DATA.copy()
    data_copy["accessToken"] = TEST_ACCESS_TOKEN_INSERT_DATA["accessToken"]
    response = token_util.create_token_public(
        pdsUserId=data_copy["pdsUserId"],
        pdsUserName=data_copy["pdsUserName"],
        accessToken=data_copy["accessToken"]
    )
    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "999999",
            "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
        }
    }
    print(response)

    # 最後にテスト用に挿入したデータを削除する
    db.delete(data_copy["accessToken"], data_copy["pdsUserId"], data_copy["pdsUserName"])


# No24.アクセストークン発行処理（公開用）_13.アクセストークン登録処理　異常系　引数．アクセストークンがある場合アクセストークン登録処理が失敗する
def test_create_token_public_case24(mocker: MockerFixture, db: testAccessToken):
    # Exception
    mocker.patch.object(SqlConstClass, "ACCESS_TOKEN_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    data_copy = DATA.copy()
    data_copy["accessToken"] = TEST_ACCESS_TOKEN_INSERT_DATA["accessToken"]
    response = token_util.create_token_public(
        pdsUserId=data_copy["pdsUserId"],
        pdsUserName=data_copy["pdsUserName"],
        accessToken=data_copy["accessToken"]
    )
    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "991028",
            "message": logUtil.message_build(MessageConstClass.ERRORS["991028"]["message"], "991028")
        }
    }
    print(response)

    # 最後にテスト用に挿入したデータを削除する
    db.delete(data_copy["accessToken"], data_copy["pdsUserId"], data_copy["pdsUserName"])

