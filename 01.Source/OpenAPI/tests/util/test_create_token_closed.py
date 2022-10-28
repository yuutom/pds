# from re import T
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

HEADER = {"tfOperatorId": "access-test", "tfOperatorName": "アクセス"}

trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
token_util = TokenUtilClass(trace_logger)
common_util = CommonUtilClass(trace_logger)
# 共通DB接続準備処理
common_db_info_response = common_util.get_common_db_info_and_connection()
# 検証に使用するデータ
DATA = {
    "tfOperatorInfo": {
        "tfOperatorId": HEADER["tfOperatorId"],
        "tfOperatorName": HEADER["tfOperatorName"]
    },
    "accessToken": None
}
# テスト挿入用データ
TEST_INSERT_DATA = {
    "tfOperatorId": HEADER["tfOperatorId"],
    "tfOperatorName": "TFオペレータ名",
    "tfOperatorMail": "test@gmail.com",
    "password": "90d76e0f1eb5bb68f4d42742ec8c534174d4e5340e834893283ebe4250e26003d816d2e4a90e477e3978a72f5a85a773f87ed476cdd869adeb719773c19603eb",
    "passwordResetFlg": True,
    "tfOperatorDisableFlg": False,
    "passwordExpire": "2022-12-30",
    "passwordFirstGeneration": None,
    "passwordSecondGeneration": None,
    "passwordThirdGeneration": None,
    "passwordFourthGeneration": None
}
# アクセストークン無効化テスト挿入用データ
TEST_ACCESS_TOKEN_INSERT_DATA = {
    "accessToken": "3a80a8eb72c836c66a188b6e188410aff0f86c9aa2f4b99af919e9809eaff47c859cc4c3a50efb04ed726efe60ab1272827b976b9b6df699f97102d3e516c50c0ad1b69349df16027b05dc8422b4784695589001f7c7a30e2d0a55e24f9e1c0e0d0e3ade",
    "tfOperatorId": HEADER["tfOperatorId"],
    "pdsUserId": None,
    "validFlg": True,
    "periodDatetime": "2022/09/20 17:07:19.532",
    "jwtSecretKey": "a7ed3f1a4e8d4ccb80f1de5dc67ed0dc"
}
# アクセストークンテーブル削除SQL
ACCESS_TOKEN_CLOSED_DELETE_SQL = """
    DELETE FROM t_access_token
    WHERE
        t_access_token.access_token = %s
        AND t_access_token.tf_operator_id = %s;
"""
# TFオペレータテーブル削除SQL
TF_OPERATOR_DELETE_SQL = """
    DELETE FROM m_tf_operator
    WHERE
        m_tf_operator.tf_operator_id = %s;
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
            SqlConstClass.TF_OPERATOR_REGISTER_INSERT_SQL,
            TEST_INSERT_DATA["tfOperatorId"],
            TEST_INSERT_DATA["tfOperatorName"],
            TEST_INSERT_DATA["tfOperatorMail"],
            TEST_INSERT_DATA["password"],
            TEST_INSERT_DATA["passwordResetFlg"],
            TEST_INSERT_DATA["tfOperatorDisableFlg"],
            TEST_INSERT_DATA["passwordExpire"],
            TEST_INSERT_DATA["passwordFirstGeneration"],
            TEST_INSERT_DATA["passwordSecondGeneration"],
            TEST_INSERT_DATA["passwordThirdGeneration"],
            TEST_INSERT_DATA["passwordFourthGeneration"]
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

    def selectTfOperator(self, tfOperatorId: str):
        common_db_connection_resource: PostgresDbUtilClass = None
        common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
        common_db_connection = common_db_info_response["common_db_connection"]

        tf_operator_result = common_db_connection_resource.select_tuple_one(
            common_db_connection,
            SqlConstClass.ACCESS_TOKEN_CLOSED_TF_OPERATOR_VERIF_SQL,
            tfOperatorId,
            False
        )
        print(tf_operator_result)

        if tf_operator_result["rowcount"] == 0:
            return {
                "rowcount": tf_operator_result["rowcount"]
            }

        tf_operator_column_list = [
            "passwordResetFlg"
        ]
        tf_operator_data_list = tf_operator_result["query_results"]
        tf_operator_dict = {column: data for column, data in zip(tf_operator_column_list, tf_operator_data_list)}
        return {
            "rowcount": tf_operator_result["rowcount"],
            "pdsUser": tf_operator_dict
        }

    def delete(self, accessToken: str, tfOperatorId: str):
        common_db_connection_resource: PostgresDbUtilClass = None
        common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
        common_db_connection = common_db_info_response["common_db_connection"]

        responseAccessToken = common_db_connection_resource.delete(
            common_db_connection,
            ACCESS_TOKEN_CLOSED_DELETE_SQL,
            accessToken,
            tfOperatorId
        )
        print(responseAccessToken)

        responseTfOperator = common_db_connection_resource.delete(
            common_db_connection,
            TF_OPERATOR_DELETE_SQL,
            tfOperatorId
        )
        print(responseTfOperator)

        # トランザクションコミット処理
        common_db_connection_resource.commit_transaction(common_db_connection)


@pytest.fixture
def db():
    test = testAccessToken()
    result = test.selectTfOperator(HEADER["tfOperatorId"])
    if result["rowcount"] == 0:
        test.insert()
    return test


# No1.アクセストークン発行処理（非公開用）_01.引数検証処理チェック　異常系　引数．TFオペレータID　値が設定されていない（空値）
def test_create_token_closed_case1_1_1():
    data_copy = DATA.copy()
    data_copy["tfOperatorInfo"]["tfOperatorId"] = ""
    with pytest.raises(PDSException) as e:
        token_util.create_token_closed(
            tfOperatorInfo=data_copy["tfOperatorInfo"],
            accessToken=data_copy["accessToken"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "TFオペレータID")
    }
    print(e)


# No1.アクセストークン発行処理（非公開用）_01.引数検証処理チェック　異常系　引数．TFオペレータ名　値が設定されていない（空値）
def test_create_token_closed_case1_2_1():
    data_copy = DATA.copy()
    data_copy["tfOperatorInfo"]["tfOperatorName"] = ""
    with pytest.raises(PDSException) as e:
        token_util.create_token_closed(
            tfOperatorInfo=data_copy["tfOperatorInfo"],
            accessToken=data_copy["accessToken"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "TFオペレータ名")
    }
    print(e)


# No1.アクセストークン発行処理（非公開用）_01.引数検証処理チェック　異常系　TFオペレータIDが異常な値
def test_create_token_closed_case2():
    data_copy = DATA.copy()
    data_copy["tfOperatorInfo"]["tfOperatorId"] = ""
    with pytest.raises(PDSException) as e:
        token_util.create_token_closed(
            tfOperatorInfo=data_copy["tfOperatorInfo"],
            accessToken=data_copy["accessToken"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "TFオペレータID")
    }
    print(e)


def test_create_token_closed_case3(db: testAccessToken):
    data_copy = DATA.copy()
    response = token_util.create_token_closed(
        tfOperatorInfo=data_copy["tfOperatorInfo"],
        accessToken=data_copy["accessToken"]
    )
    assert response == {
        "result": True,
        "accessToken": response["accessToken"],
        "jwt": response["jwt"]
    }
    print(response)

    # 最後にテスト用に挿入したデータを削除する
    db.delete(response["accessToken"], data_copy["tfOperatorInfo"]["tfOperatorId"])


# No4.アクセストークン発行処理（非公開用）_01.引数検証処理チェック　異常系　アクセストークンが異常な値
def test_create_token_closed_case4():
    data_copy = DATA.copy()
    data_copy["accessToken"] = "%"
    with pytest.raises(PDSException) as e:
        token_util.create_token_closed(
            tfOperatorInfo=data_copy["tfOperatorInfo"],
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


# No6.アクセストークン発行処理（非公開用）_02.DB接続準備処理　異常系　接続に失敗する　設定値を異常な値に変更する
def test_create_token_closed_case6(mocker: MockerFixture):
    data_copy = DATA.copy()
    mocker.patch("util.commonUtil.CommonUtilClass.get_secret_info").return_value = {"host": "test", "port": "test", "username": "test", "password": "test"}
    response = token_util.create_token_closed(
        tfOperatorInfo=data_copy["tfOperatorInfo"],
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


# No7.アクセストークン発行処理（非公開用）_02.DB接続準備処理　正常系　接続に成功する
def test_create_token_closed_case7(db: testAccessToken):
    data_copy = DATA.copy()
    response = token_util.create_token_closed(
        tfOperatorInfo=data_copy["tfOperatorInfo"],
        accessToken=data_copy["accessToken"]
    )
    assert response == {
        "result": True,
        "accessToken": response["accessToken"],
        "jwt": response["jwt"]
    }
    print(response)

    # 最後にテスト用に挿入したデータを削除する
    db.delete(response["accessToken"], data_copy["tfOperatorInfo"]["tfOperatorId"])


# No8.アクセストークン発行処理（非公開用）_03.TFオペレータ取得処理　異常系　PDSユーザ取得処理で取得結果が1件以外
# No12.アクセストークン発行処理（非公開用）_05.TFオペレータ取得エラー処理　正常系　「変数．エラー情報」が設定されている場合、「05.PDSユーザ取得エラー処理」に遷移する
# No13.アクセストークン発行処理（非公開用）_05.PDSユーザ取得エラー処理　正常系　レスポンス情報を作成し、返却する
def test_create_token_closed_case8():
    data_copy = DATA.copy()
    response = token_util.create_token_closed(
        tfOperatorInfo=data_copy["tfOperatorInfo"],
        accessToken=data_copy["accessToken"]
    )
    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "020004",
            "message": logUtil.message_build(MessageConstClass.ERRORS["020004"]["logMessage"], "TFオペレータ")
        }
    }
    print(response)


# No9.アクセストークン発行処理（非公開用）_03.PDSユーザ取得処理　異常系　postgresqlのエラーが発生
def test_create_token_closed_case9(mocker: MockerFixture):
    data_copy = DATA.copy()
    mocker.patch.object(SqlConstClass, "ACCESS_TOKEN_CLOSED_TF_OPERATOR_VERIF_SQL", """ SELECT * FROM AAAAAA; """)
    response = token_util.create_token_closed(
        tfOperatorInfo=data_copy["tfOperatorInfo"],
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


# No16.アクセストークン発行処理（非公開用）_08.アクセストークン判定処理　正常系　引数．アクセストークンがある
# No19.アクセストークン発行処理（非公開用）_09.アクセストークン無効処理　アクセストークン無効処理が成功する
# No20.アクセストークン発行処理（非公開用）_10.アクセストークン無効チェック処理　正常系　「変数．エラー情報」が設定されていない場合、「13.アクセストークン登録処理」に遷移する
# No31.アクセストークン発行処理（非公開用）_17.トランザクションコミット処理　正常系　アクセストークン登録処理が成功する
def test_create_token_closed_case16(db: testAccessToken):
    db.insertAccessToken()
    data_copy = DATA.copy()
    data_copy["accessToken"] = TEST_ACCESS_TOKEN_INSERT_DATA["accessToken"]
    response = token_util.create_token_closed(
        tfOperatorInfo=data_copy["tfOperatorInfo"],
        accessToken=data_copy["accessToken"]
    )
    assert response == {
        "result": True,
        "accessToken": response["accessToken"],
        "jwt": response["jwt"]
    }
    print(response)

    # 最後にテスト用に挿入したデータを削除する
    db.delete(response["accessToken"], data_copy["tfOperatorInfo"]["tfOperatorId"])


# No18.アクセストークン発行処理（非公開用）_09.アクセストークン無効処理　異常系　アクセストークン無効処理が失敗する
# No21.アクセストークン発行処理（非公開用）_10.アクセストークン無効チェック処理　「変数．エラー情報」が設定されている場合、「11.トランザクションロールバック処理」に遷移する
# No22.アクセストークン発行処理（非公開用）_11.トランザクションロールバック処理　「アクセストークン発行トランザクション」をロールバックする
# No23.アクセストークン発行処理（非公開用）_12.アクセストークン無効エラー処理　正常系　レスポンス情報を作成し、返却する
def test_create_token_closed_case18(db: testAccessToken, mocker: MockerFixture):
    db.insertAccessToken()
    # Exception
    mocker.patch.object(SqlConstClass, "ACCESS_TOKEN_CLOSED_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    data_copy = DATA.copy()
    data_copy["accessToken"] = TEST_ACCESS_TOKEN_INSERT_DATA["accessToken"]
    response = token_util.create_token_closed(
        tfOperatorInfo=data_copy["tfOperatorInfo"],
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


# No19.アクセストークン発行処理（非公開用）_09.アクセストークン無効処理　正常系　アクセストークン無効処理が成功する
def test_create_token_closed_case19():
    data_copy = DATA.copy()
    data_copy["accessToken"] = ""
    response = token_util.create_token_closed(
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


# No24.アクセストークン発行処理（非公開用）_13.アクセストークン登録処理　異常系　アクセストークン登録処理が失敗する
# No27.アクセストークン発行処理（非公開用）_14.アクセストークン登録チェック処理　「変数．エラー情報」が設定されている場合、「15.アクセストークン発行トランザクションロールバック処理」に遷移する
# No29.アクセストークン発行処理（非公開用）_15.トランザクションロールバック処理　「アクセストークン発行トランザクション」をロールバックする
# No30.アクセストークン発行処理（非公開用）_16.アクセストークン登録エラー処理　正常系　レスポンス情報を作成し、返却する
def test_create_token_closed_case24(db: testAccessToken, mocker: MockerFixture):
    db.insertAccessToken()
    # Exception
    mocker.patch.object(SqlConstClass, "ACCESS_TOKEN_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    data_copy = DATA.copy()
    data_copy["accessToken"] = TEST_ACCESS_TOKEN_INSERT_DATA["accessToken"]
    response = token_util.create_token_closed(
        tfOperatorInfo=data_copy["tfOperatorInfo"],
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
