from fastapi.testclient import TestClient
from util.commonUtil import CommonUtilClass
from app import app
from fastapi import Request
import pytest
from pytest_mock.plugin import MockerFixture
from util.tokenUtil import TokenUtilClass
import util.logUtil as logUtil
import json
from const.sqlConst import SqlConstClass
from const.systemConst import SystemConstClass
from util.postgresDbUtil import PostgresDbUtilClass
from util.fileUtil import NoHeaderOneItemCsvStringClass
from const.messageConst import MessageConstClass
import routers.closed.tfOperatorResetPasswordRouter as tfOperatorResetPasswordRouter
from routers.closed.tfOperatorResetPasswordRouter import requestBody as routerRequestBody

client = TestClient(app)

# 処理名
EXEC_NAME: str = "tfOperatorResetPassword"

TF_OPERATOR_INFO = {
    "tfOperatorId": "t-test4",
    "tfOperatorName": "テスト"
}
# TFオペレータテーブル更新SQL
TF_OPERATOR_UPDATE_SQL = """
    UPDATE m_tf_operator
    SET
        password = %s
        , tf_operator_password_reset_flg = False
        , tf_operator_disable_flg = False
        , password_expire = %s
        , password_first_generation = %s
        , password_second_generation = %s
        , password_third_generation = %s
        , password_fourth_generation = %s
    WHERE
        m_tf_operator.tf_operator_id = %s;
"""

DATA = {
    "tfOperatorId": TF_OPERATOR_INFO["tfOperatorId"]
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

    common_util = CommonUtilClass(trace_logger)
    # 共通DB接続準備処理
    common_db_info_response = common_util.get_common_db_info_and_connection()

    common_db_connection_resource: PostgresDbUtilClass = None
    common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
    common_db_connection = common_db_info_response["common_db_connection"]

    common_db_connection_resource.update(
        common_db_connection,
        TF_OPERATOR_UPDATE_SQL,
        "f028b202b1357025f15a60f973259a690f726eda61bf2060a9f43ef18bb4a32c54135119466ad8a650f933182908f2b8f174a64de2356a34e94bb46a3e261500",
        "2022-12-30",
        "363652832d15a5c7a685d13ab873c62c8ac56e33ceb14e148a25b6b508aaf56c42e5426d04eb450e8f4abe5a4b6764b35de0c03d12af493d194e3ab77fd967fe",
        "5250658d1f5b5d5417c69ccf8e7487ae64046e18525ea63cac10c0211a91aa72925fb0ac486ac3eb0bcbc2c66abd7c05e7289214a74a7b9451383805b207bedb",
        "06178841d416babe1b9a7c70dcc554e2ebdee689c72ea1d0bfdec9a611d7cc1a48106c1dbdf1a802963343c2b92b5a6553298185a06c677deb1c5599eb388249",
        "826a7db3669565d0a5ed7d2dec297f1db14b5dc1915d5fcfa45271b20b2af7702394d1289a54e8a9e12708dae2f520e535a3a6762133bb7e4a7bde8427c64e7f",
        TF_OPERATOR_INFO["tfOperatorId"]
    )
    # トランザクションコミット処理
    common_db_connection_resource.commit_transaction(common_db_connection)
    yield {
        "header": {
            "Content-Type": "application/json",
            "accessToken": token_result["accessToken"],
            "timeStamp": "2022/08/23 15:12:01.690",
            "Authorization": "Bearer " + token_result["jwt"]
        }
    }


def test(create_header):
    create_header["header"]


# メイン処理
# 01.アクセストークン検証処理
# No.1.アクセストークン検証処理が失敗する
def test_tf_operator_reset_password_case1(create_header):
    header = create_header["header"]
    header["accessToken"] = "518302174323385ee79afc2e37e3783f15e48e43d75f004a83e41667996087770c5e474023c0d6969529b49a8fd553ca454e54adbf473ac1a129fd4b0314abc4d4f33e4349749110f5b1774db69d5f87944e3a86c7d3ee10390a825f8bf35f1813774c94"
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": response.json()["errorInfo"]
    }
    print(response.json())


# No.2.アクセストークン検証処理が成功する
def test_tf_operator_reset_password_case2(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 02.共通エラーチェック処理
# No.3.共通エラーチェック処理が成功
def test_tf_operator_reset_password_case3(create_header):
    header = create_header["header"]
    header["accessToken"] = "518302174323385ee79afc2e37e3783f15e48e43d75f004a83e41667996087770c5e474023c0d6969529b49a8fd553ca454e54adbf473ac1a129fd4b0314abc4d4f33e4349749110f5b1774db69d5f87944e3a86c7d3ee10390a825f8bf35f1813774c94"
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": response.json()["errorInfo"]
    }
    print(response.json())


# 03.パラメータ検証処理
# No.4.パラメータ検証処理が失敗する
def test_tf_operator_reset_password_case4(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfOperatorId"] = ""
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": response.json()["errorInfo"]
    }
    print(response.json())


# No.5.パラメータ検証処理が成功する
def test_tf_operator_reset_password_case5(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 04.共通エラーチェック処理
# No.6.共通エラーチェック処理が成功
def test_tf_operator_reset_password_case6(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfOperatorId"] = ""
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": response.json()["errorInfo"]
    }
    print(response.json())


# 05.仮パスワード生成処理
# No.7.仮パスワード生成処理に成功する
def test_tf_operator_reset_password_case7(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 06.CSVファイル作成処理
# No.8.CSV作成処理に失敗する
def test_tf_operator_reset_password_case8(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(NoHeaderOneItemCsvStringClass, "__init__", side_effect=Exception('testException'))
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
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


# No.9.CSVファイル作成処理に成功する
def test_tf_operator_reset_password_case9(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 07.DB接続準備処理
# No.10.接続に失敗する 設定値を異常な値に変更する
def test_tf_operator_reset_password_case10(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.commonUtil.CommonUtilClass.get_secret_info").return_value = {"host": "test", "port": "test", "username": "test", "password": "test"}
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
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


# No.11.接続に成功する
def test_tf_operator_reset_password_case11(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 08.TFオペレータパスワードリセット情報取得処理
# No.12.TFオペレータパスワードリセット情報取得処理の、件数が0件
def test_tf_operator_reset_password_case12(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfOperatorId"] = "t-test000"
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
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


# No.13.TFオペレータパスワードリセット情報取得処理の、TFオペレータ．TFオペレータ無効化フラグがtrue
def test_tf_operator_reset_password_case13(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfOperatorId"] = "t-test3"
    TF_OPERATOR_UPDATE_SQL_2 = """
    UPDATE m_tf_operator
    SET
        password = %s
        , tf_operator_password_reset_flg = False
        , tf_operator_disable_flg = True
        , password_expire = %s

    WHERE
        m_tf_operator.tf_operator_id = %s;
    """

    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    common_util = CommonUtilClass(trace_logger)
    # 共通DB接続準備処理
    common_db_info_response = common_util.get_common_db_info_and_connection()

    common_db_connection_resource: PostgresDbUtilClass = None
    common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
    common_db_connection = common_db_info_response["common_db_connection"]

    common_db_connection_resource.update(
        common_db_connection,
        TF_OPERATOR_UPDATE_SQL_2,
        "f028b202b1357025f15a60f973259a690f726eda61bf2060a9f43ef18bb4a32c54135119466ad8a650f933182908f2b8f174a64de2356a34e94bb46a3e261500",
        "2022-12-30",
        data_copy["tfOperatorId"]
    )
    # トランザクションコミット処理
    common_db_connection_resource.commit_transaction(common_db_connection)

    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
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


# No.14.TFオペレータパスワードリセット情報取得処理が失敗する
def test_tf_operator_reset_password_case14(mocker: MockerFixture, create_header):
    mocker.patch.object(SqlConstClass, "TF_OPERATOR_RESET_PASSWORD_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
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


# No.15.TFオペレータパスワードリセット情報取得処理の、件数が1件
def test_tf_operator_reset_password_case15(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 09.共通エラーチェック処理
# No.16.共通エラーチェック処理が成功
def test_tf_operator_reset_password_case16(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfOperatorId"] = "t-test000"
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
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


# 10.トランザクション作成処理
# No.17.トランザクション作成処理が失敗する


# No.18.トランザクション作成処理が成功する


# 11.TFオペレータパスワードリセット処理
# No.19.TFオペレータパスワードリセット処理が失敗する
def test_tf_operator_reset_password_case19(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "TF_OPERATOR_RESET_PASSWORD_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
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


# No.20.TFオペレータパスワードリセット処理が成功する
def test_tf_operator_reset_password_case20(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 12.共通エラーチェック処理
# No.21.共通エラーチェック処理が成功
def test_tf_operator_reset_password_case21(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "TF_OPERATOR_RESET_PASSWORD_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
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


# 13.WBT新規メール情報登録API実行処理
# No.22.WBT新規メール情報登録API実行処理が失敗する
def test_tf_operator_reset_password_case22(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(CommonUtilClass, "wbt_mails_add_api_exec", side_effect=Exception('testException'))
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
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


# No.23.WBT新規メール情報登録API実行処理が成功する
def test_tf_operator_reset_password_case23(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 14.共通エラーチェック処理
# No.24.共通エラーチェック処理が成功
def test_tf_operator_reset_password_case24(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(CommonUtilClass, "wbt_mails_add_api_exec", return_value={"result": False, "errorInfo": {"errorCode": "020001", "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "種別")}})
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
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


# 15.WBTファイル登録API実行処理
# No.25.WBTファイル登録API実行処理が失敗する
def test_tf_operator_reset_password_case25(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(CommonUtilClass, "wbt_file_add_api_exec", side_effect=Exception('testException'))
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
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


# No.26.WBTファイル登録API実行処理が成功する
def test_tf_operator_reset_password_case26(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 16.共通エラーチェック処理
# No.27.共通エラーチェック処理が成功
def test_tf_operator_reset_password_case27(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(CommonUtilClass, "wbt_file_add_api_exec", return_value={"result": False, "errorInfo": {"errorCode": "020001", "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "メールID")}})
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
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


# 17.トランザクションコミット処理
# No.28.トランザクションコミット処理が失敗する
def test_tf_operator_reset_password_case28(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(PostgresDbUtilClass, "commit_transaction", side_effect=Exception('testException'))
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": response.json()["errorInfo"]
    }
    print(response.json())


# No.29.トランザクションコミット処理が成功する
def test_tf_operator_reset_password_case29(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 18.パスワード通知CSVの削除処理
# No.30.パスワード通知CSVの削除処理が成功する
def test_tf_operator_reset_password_case30(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 19.アクセストークン発行処理
# No.31.アクセストークン発行処理が失敗する
def test_tf_operator_reset_password_case31(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "ACCESS_TOKEN_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
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


# No.32.アクセストークン発行処理が成功する
def test_tf_operator_reset_password_case32(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 20.共通エラーチェック処理
# No.33.共通エラーチェック処理が成功
def test_tf_operator_reset_password_case33(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "ACCESS_TOKEN_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
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


# 21.終了処理
# No.34.変数．エラー情報がない
def test_tf_operator_reset_password_case34(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# パラメータ検証処理
# 01.パラメータ検証処理
# No.35.PDSユーザ認証情報無効化API_01.引数検証処理　シート参照
# No.35_1.引数．ヘッダパラメータ．タイムスタンプが空値 ("")
def test_tf_operator_reset_password_case35_1(create_header):
    header = create_header["header"]
    header["timeStamp"] = ""
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
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


# No.35_2.引数．ヘッダパラメータ．タイムスタンプが空値 (None)
def test_tf_operator_reset_password_case35_2(create_header):
    header = create_header["header"]
    header["timeStamp"] = None
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
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


# No.35_3.引数．ヘッダパラメータ．タイムスタンプが24桁で文字列型ではない
def test_tf_operator_reset_password_case35_3(create_header):
    header = create_header["header"]
    header["timeStamp"] = 123456789012345678901234
    data_copy = DATA.copy()
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    router_request_body = routerRequestBody(**data_copy)
    response = tfOperatorResetPasswordRouter.input_check(
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


# No.35_4.引数．ヘッダパラメータ．タイムスタンプが23桁で文字列型
def test_tf_operator_reset_password_case35_4(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No.35_5.引数．ヘッダパラメータ．アクセストークンが空値 ("")
def test_tf_operator_reset_password_case35_5(create_header):
    header = create_header["header"]
    header["accessToken"] = ""
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
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


# No.35_6.引数．ヘッダパラメータ．アクセストークンが空値 (None)
def test_tf_operator_reset_password_case35_6(create_header):
    header = create_header["header"]
    header["accessToken"] = None
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
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


# No.35_7.引数．ヘッダパラメータ．アクセストークンが201桁で文字列型ではない
def test_tf_operator_reset_password_case35_7(create_header):
    header = create_header["header"]
    header["accessToken"] = 123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901
    data_copy = DATA.copy()
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    router_request_body = routerRequestBody(**data_copy)
    response = tfOperatorResetPasswordRouter.input_check(
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


# No.35_8.引数．ヘッダパラメータ．アクセストークンが200桁で文字列型
def test_tf_operator_reset_password_case35_8(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No.35_9.引数．リクエストボディ．TFオペレータIDが空値 ("")
def test_tf_operator_reset_password_case35_9(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfOperatorId"] = ""
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
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
            }
        ]
    }
    print(response.json())


# No.35_10.引数．リクエストボディ．TFオペレータIDが空値 (None)
def test_tf_operator_reset_password_case35_10(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfOperatorId"] = None
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
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


# No.35_11.引数．リクエストボディ．TFオペレータIDが2桁で文字列型ではない
def test_tf_operator_reset_password_case35_11(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfOperatorId"] = 12
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
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


# No.35_12.引数．リクエストボディ．TFオペレータIDが17桁で入力可能文字以外を含み文字列型
def test_tf_operator_reset_password_case35_12(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfOperatorId"] = "1234567890abcdefg"
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
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


# No.35_13.引数．リクエストボディ．TFオペレータIDが3桁で入力可能文字のみであり文字列型
def test_tf_operator_reset_password_case35_13(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfOperatorId"] = "123"
    TF_OPERATOR_UPDATE_SQL_3 = """
    UPDATE m_tf_operator
    SET
        password = %s
        , tf_operator_password_reset_flg = False
        , tf_operator_disable_flg = False
        , password_expire = %s

    WHERE
        m_tf_operator.tf_operator_id = %s;
    """

    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    common_util = CommonUtilClass(trace_logger)
    # 共通DB接続準備処理
    common_db_info_response = common_util.get_common_db_info_and_connection()

    common_db_connection_resource: PostgresDbUtilClass = None
    common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
    common_db_connection = common_db_info_response["common_db_connection"]

    common_db_connection_resource.update(
        common_db_connection,
        TF_OPERATOR_UPDATE_SQL_3,
        "f028b202b1357025f15a60f973259a690f726eda61bf2060a9f43ef18bb4a32c54135119466ad8a650f933182908f2b8f174a64de2356a34e94bb46a3e261500",
        "2022-12-30",
        data_copy["tfOperatorId"]
    )
    # トランザクションコミット処理
    common_db_connection_resource.commit_transaction(common_db_connection)
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No.35_14.引数．リクエストボディ．TFオペレータIDが16桁で入力可能文字のみであり文字列型
def test_tf_operator_reset_password_case35_14(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfOperatorId"] = "1234567890123456"
    TF_OPERATOR_UPDATE_SQL_4 = """
    UPDATE m_tf_operator
    SET
        password = %s
        , tf_operator_password_reset_flg = False
        , tf_operator_disable_flg = False
        , password_expire = %s

    WHERE
        m_tf_operator.tf_operator_id = %s;
    """

    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    common_util = CommonUtilClass(trace_logger)
    # 共通DB接続準備処理
    common_db_info_response = common_util.get_common_db_info_and_connection()

    common_db_connection_resource: PostgresDbUtilClass = None
    common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
    common_db_connection = common_db_info_response["common_db_connection"]

    common_db_connection_resource.update(
        common_db_connection,
        TF_OPERATOR_UPDATE_SQL_4,
        "f028b202b1357025f15a60f973259a690f726eda61bf2060a9f43ef18bb4a32c54135119466ad8a650f933182908f2b8f174a64de2356a34e94bb46a3e261500",
        "2022-12-30",
        data_copy["tfOperatorId"]
    )
    # トランザクションコミット処理
    common_db_connection_resource.commit_transaction(common_db_connection)
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 02.終了処理
# No.36.変数．エラー情報がない
def test_tf_operator_reset_password_case36(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No.37.変数．エラー情報がある
def test_tf_operator_reset_password_case37(create_header):
    header = create_header["header"]
    header["TimeStamp"] = ""
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": response.json()["errorInfo"]
    }
    print(response.json())


# ロールバック処理
# 01.ロールバック処理
# No.38.ロールバック処理が失敗する
def test_tf_operator_reset_password_case38(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    # Exception
    mocker.patch.object(SqlConstClass, "TF_OPERATOR_RESET_PASSWORD_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    mocker.patch.object(PostgresDbUtilClass, "rollback_transaction", return_value={"result": False, "errorObject": Exception("test-exception"), "stackTrace": "test-exception"})
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
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


# No.39.ロールバック処理が成功する
def test_tf_operator_reset_password_case39(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    # Exception
    mocker.patch.object(SqlConstClass, "TF_OPERATOR_RESET_PASSWORD_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
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
# No.40.共通エラーチェック処理が成功
def test_tf_operator_reset_password_case40(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    # Exception
    mocker.patch.object(SqlConstClass, "TF_OPERATOR_RESET_PASSWORD_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    mocker.patch.object(PostgresDbUtilClass, "rollback_transaction", return_value={"result": False, "errorObject": Exception("test-exception"), "stackTrace": "test-exception"})
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
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
# No.41.変数．エラー情報がない
def test_tf_operator_reset_password_case41(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    # Exception
    mocker.patch.object(SqlConstClass, "TF_OPERATOR_RESET_PASSWORD_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.post("/api/2.0/tfoperator/resetpassword", headers=header, data=json.dumps(data_copy))
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
