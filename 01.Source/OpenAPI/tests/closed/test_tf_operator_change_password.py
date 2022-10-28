from fastapi.testclient import TestClient
from util.commonUtil import CommonUtilClass
from const.sqlConst import SqlConstClass
from app import app
from fastapi import Request
import pytest
from pytest_mock.plugin import MockerFixture
from util.tokenUtil import TokenUtilClass
import util.logUtil as logUtil
import json
from util.postgresDbUtil import PostgresDbUtilClass
from const.systemConst import SystemConstClass

client = TestClient(app)
trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
common_util = CommonUtilClass(trace_logger)
# 共通DB接続準備処理
common_db_info_response = common_util.get_common_db_info_and_connection()

BEARER = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0Zk9wZXJhdG9ySWQiOiJsLXRlc3QiLCJ0Zk9wZXJhdG9yTmFtZSI6Ilx1MzBlZFx1MzBiMFx1MzBhNFx1MzBmM1x1MzBjNlx1MzBiOVx1MzBjOCIsInRmT3BlcmF0b3JQYXNzd29yZFJlc2V0RmxnIjpmYWxzZSwiYWNjZXNzVG9rZW4iOiJiZGE4ZGY3OThiYzViZGZhMWZkODIyNmRiYmQ0OTMyMTY5ZmY5MjAzNWM0YzFlY2FjZjY2OGUyYzk2ZjAwZThlZTUxNTBiNGM0NTc0NjlkN2I4YmY1NzIxZDZlM2NiNzFiY2RiYzA3ODRiYzcyZWVlNjk1OGE3NTBiMWJkMWEzZWFmZWQ0OWFhNWU0ODZjYzQyZmM3OWNhMWY3MGQzZmM3Yzc0YzE5NjM3ODUzMjRhZDRhNGM0NjkxOGE4NjQ1N2ZiODE3NDU1MCIsImV4cCI6MTY2MTc0NjY3MX0.LCRjPEqKMkRQ_phaYnO7S7pd3SU_rgon-wsX14DBsPA"
ACCESS_TOKEN = "bda8df798bc5bdfa1fd8226dbbd4932169ff92035c4c1ecacf668e2c96f00e8ee5150b4c457469d7b8bf5721d6e3cb71bcdbc0784bc72eee6958a750b1bd1a3eafed49aa5e486cc42fc79ca1f70d3fc7c74c1963785324ad4a4c46918a86457fb8174550"
HEADER = {"Content-Type": "application/json", "timeStamp": "2022/08/23 15:12:01.690", "accessToken": ACCESS_TOKEN, "Authorization": "Bearer " + BEARER}
PDS_USER_HEADER = {"pdsUserId": "C5100003", "pdsUserName": "PDS_CHANGE"}
DATA = {
    "tfOperatorPassword": "test_1234",
    "tfOperatorConfirmPassword": "test_1234"
}
# テスト挿入用データ
TF_OPERATOR_INFO = {
    "tfOperatorId": "pc-test-change",
    "tfOperatorName": "変更太郎"
}
TEST_INSERT_DATA = {
    "tfOperatorId": TF_OPERATOR_INFO["tfOperatorId"],
    "tfOperatorName": "TFオペレータ名",
    "tfOperatorMail": "test@gmail.com",
    "password": "c4dd4d78918000b9d5758b87fa45b2f8db71b1675dd46da09d556b5220481f40d1a0e5a8c2d4351fd4176d1c6a12033438e56d94ccfb24de29b2c303703889d8",
    "passwordResetFlg": True,
    "tfOperatorDisableFlg": False,
    "passwordExpire": "2022-12-30",
    "passwordFirstGeneration": "363652832d15a5c7a685d13ab873c62c8ac56e33ceb14e148a25b6b508aaf56c42e5426d04eb450e8f4abe5a4b6764b35de0c03d12af493d194e3ab77fd967fe",
    "passwordSecondGeneration": "5250658d1f5b5d5417c69ccf8e7487ae64046e18525ea63cac10c0211a91aa72925fb0ac486ac3eb0bcbc2c66abd7c05e7289214a74a7b9451383805b207bedb",
    "passwordThirdGeneration": "06178841d416babe1b9a7c70dcc554e2ebdee689c72ea1d0bfdec9a611d7cc1a48106c1dbdf1a802963343c2b92b5a6553298185a06c677deb1c5599eb388249",
    "passwordFourthGeneration": "826a7db3669565d0a5ed7d2dec297f1db14b5dc1915d5fcfa45271b20b2af7702394d1289a54e8a9e12708dae2f520e535a3a6762133bb7e4a7bde8427c64e7f"
}
# TFオペレータテーブル削除SQL
TF_OPERATOR_DELETE_SQL = """
    DELETE FROM m_tf_operator
    WHERE
        m_tf_operator.tf_operator_id = %s;
"""

# TFオペレータテーブル更新SQL
TF_OPERATOR_UPDATE_SQL = """
    UPDATE m_tf_operator
    SET
        tf_operator_disable_flg = True
    WHERE
        m_tf_operator.tf_operator_id = %s;
"""


# テスト用のTFオペレータクラス
class testTfOperator:
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

    def update(self, tfOperatorId: str):
        common_db_connection_resource: PostgresDbUtilClass = None
        common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
        common_db_connection = common_db_info_response["common_db_connection"]

        response = common_db_connection_resource.update(
            common_db_connection,
            TF_OPERATOR_UPDATE_SQL,
            tfOperatorId
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

    def delete(self, tfOperatorId: str):
        common_db_connection_resource: PostgresDbUtilClass = None
        common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
        common_db_connection = common_db_info_response["common_db_connection"]

        responseTfOperator = common_db_connection_resource.delete(
            common_db_connection,
            TF_OPERATOR_DELETE_SQL,
            tfOperatorId
        )
        print(responseTfOperator)

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
            "Content-Type": "application/json",
            "accessToken": token_result["accessToken"],
            "timeStamp": "2022/08/23 15:12:01.690",
            "Authorization": "Bearer " + token_result["jwt"]
        }
    }


@pytest.fixture
def db():
    test = testTfOperator()
    result = test.selectTfOperator(TF_OPERATOR_INFO["tfOperatorId"])
    if result["rowcount"] == 0:
        test.insert()
    return test


# No1.01.メイン処理_01.アクセストークン検証処理　異常系　アクセストークン検証処理が失敗する
# No3.01.メイン処理_02.共通エラーチェック処理　正常系　共通エラーチェック処理が成功（エラー情報有り）
def test_tf_operator_change_password_case1(create_header):
    header = create_header["header"]
    header["accessToken"] = "518302174323385ee79afc2e37e3783f15e48e43d75f004a83e41667996087770c5e474023c0d6969529b49a8fd553ca454e54adbf473ac1a129fd4b0314abc4d4f33e4349749110f5b1774db69d5f87944e3a86c7d3ee10390a825f8bf35f1813774c94"
    response = client.post("/api/2.0/tfoperator/changepassword", headers=header, data=json.dumps(DATA))
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


def test(db):
    db.insert()


# No2.01.メイン処理_01.アクセストークン検証処理　正常系　アクセストークン検証処理が成功する
# No5.01.メイン処理_03.パラメータ検証処理　正常系　パラメータ検証処理が成功する
# No7.01.メイン処理_05.パスワードのハッシュ化処理　正常系　パスワードのハッシュ化処理が成功する
# No9.01.メイン処理_06.DB接続準備処理　正常系　接続に成功する
# No12.01.メイン処理_07.TFオペレータ取得処理　正常系　TFオペレータ取得処理で取得件数が1件
# No21.01.メイン処理_11.トランザクション作成処理　正常系　トランザクション作成処理が成功する
# No23.01.メイン処理_12.TFオペレータ更新処理　正常系　TFオペレータ更新処理が成功する
# No26.01.メイン処理_14.トランザクションコミット処理　正常系　トランザクションコミット処理が成功する
# No28.01.メイン処理_15.アクセストークン発行処理　正常系　アクセストークン発行処理が成功する
# No30.01.メイン処理_17.終了処理　正常系　変数．エラー情報がない
def test_tf_operator_change_password_case2(db: testTfOperator, create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/tfoperator/changepassword", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())

    # 最後にテスト用に挿入したデータを削除する
    # db.delete(TF_OPERATOR_INFO["tfOperatorId"])


# No4.01.メイン処理_03.パラメータ検証処理　パラメータ検証処理が失敗する
def test_tf_operator_change_password_case4(create_header):
    header = create_header["header"]
    DATA["tfOperatorPassword"] = ""
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/changepassword", headers=header, data=json.dumps(data_copy))
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
                "errorCode": "020010",
                "message": response.json()["errorInfo"][2]["message"]
            },
            {
                "errorCode": "030007",
                "message": response.json()["errorInfo"][3]["message"]
            }
        ]
    }
    print(response.json())


# No6.01.メイン処理_04.共通エラーチェック処理　正常系　共通エラーチェック処理が成功（エラー情報有り）
def test_tf_operator_change_password_case6(create_header):
    header = create_header["header"]
    DATA["tfOperatorPassword"] = ""
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/changepassword", headers=header, data=json.dumps(data_copy))
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
                "errorCode": "020010",
                "message": response.json()["errorInfo"][2]["message"]
            },
            {
                "errorCode": "030007",
                "message": response.json()["errorInfo"][3]["message"]
            }
        ]
    }
    print(response.json())


# No8.01.メイン処理_06.DB接続準備処理_接続に失敗する　設定値を異常な値に変更する
def test_tf_operator_change_password_case8(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.commonUtil.CommonUtilClass.get_secret_info").return_value = {"host": "test", "port": "test", "username": "test", "password": "test"}
    header = create_header["header"]
    response = client.post("/api/2.0/tfoperator/changepassword", headers=header, data=json.dumps(DATA))
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


# No10.01.メイン処理_07.TFオペレータ取得処理　異常系　TFオペレータ取得処理で取得件数が0件
# No13.01.メイン処理_08.共通エラーチェック処理　正常系　共通エラーチェック処理が成功（エラー情報有り）
def test_tf_operator_change_password_case10(db: testTfOperator, create_header):
    header = create_header["header"]
    # テスト用に挿入したデータを削除する
    db.delete(TF_OPERATOR_INFO["tfOperatorId"])
    response = client.post("/api/2.0/tfoperator/changepassword", headers=header, data=json.dumps(DATA))
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


# No11.01.メイン処理_07.TFオペレータ取得処理　異常系　TFオペレータ取得処理でTFオペレータ．TFオペレータ無効化フラグがtrue
# No13.01.メイン処理_08.共通エラーチェック処理　正常系　共通エラーチェック処理が成功（エラー情報有り）
def test_tf_operator_change_password_case11(db: testTfOperator, create_header):
    header = create_header["header"]
    # TFオペレータ無効化フラグをtrueにする更新
    db.update(TF_OPERATOR_INFO["tfOperatorId"])
    response = client.post("/api/2.0/tfoperator/changepassword", headers=header, data=json.dumps(DATA))
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

    # 最後にテスト用に挿入したデータを削除する
    db.delete(TF_OPERATOR_INFO["tfOperatorId"])


# No14.01.メイン処理_09.TFオペレータ情報整合性チェック処理　異常系　TFオペレータ情報整合性チェック処理で、パスワードと変更後パスワードが一致
# No19.01.メイン処理_10.共通エラーチェック処理　正常系　共通エラーチェック処理が成功（エラー情報有り）
def test_tf_operator_change_password_case14(db: testTfOperator, create_header):
    header = create_header["header"]
    DATA["tfOperatorPassword"] = "test_1234567890"
    DATA["tfOperatorConfirmPassword"] = "test_1234567890"
    response = client.post("/api/2.0/tfoperator/changepassword", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "030014",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())

    # 最後にテスト用に挿入したデータを削除する
    db.delete(TF_OPERATOR_INFO["tfOperatorId"])


# No15.01.メイン処理_09.TFオペレータ情報整合性チェック処理　異常系　TFオペレータ情報整合性チェック処理で、パスワード（1世代前）と変更後パスワードが一致
# No19.01.メイン処理_10.共通エラーチェック処理　正常系　共通エラーチェック処理が成功（エラー情報有り）
def test_tf_operator_change_password_case15(db: testTfOperator, create_header):
    header = create_header["header"]
    DATA["tfOperatorPassword"] = "1st_generation"
    DATA["tfOperatorConfirmPassword"] = "1st_generation"
    response = client.post("/api/2.0/tfoperator/changepassword", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "030014",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())

    # 最後にテスト用に挿入したデータを削除する
    db.delete(TF_OPERATOR_INFO["tfOperatorId"])


# No16.01.メイン処理_09.TFオペレータ情報整合性チェック処理　異常系　TFオペレータ情報整合性チェック処理で、パスワード（2世代前）と変更後パスワードが一致
# No19.01.メイン処理_10.共通エラーチェック処理　正常系　共通エラーチェック処理が成功（エラー情報有り）
def test_tf_operator_change_password_case16(db: testTfOperator, create_header):
    header = create_header["header"]
    DATA["tfOperatorPassword"] = "2nd_generation"
    DATA["tfOperatorConfirmPassword"] = "2nd_generation"
    response = client.post("/api/2.0/tfoperator/changepassword", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "030014",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())

    # 最後にテスト用に挿入したデータを削除する
    db.delete(TF_OPERATOR_INFO["tfOperatorId"])


# No17.01.メイン処理_09.TFオペレータ情報整合性チェック処理　異常系　TFオペレータ情報整合性チェック処理で、パスワード（3世代前）と変更後パスワードが一致
# No19.01.メイン処理_10.共通エラーチェック処理　正常系　共通エラーチェック処理が成功（エラー情報有り）
def test_tf_operator_change_password_case17(db: testTfOperator, create_header):
    header = create_header["header"]
    DATA["tfOperatorPassword"] = "3rd_generation"
    DATA["tfOperatorConfirmPassword"] = "3rd_generation"
    response = client.post("/api/2.0/tfoperator/changepassword", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "030014",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())

    # 最後にテスト用に挿入したデータを削除する
    db.delete(TF_OPERATOR_INFO["tfOperatorId"])


# No18.01.メイン処理_09.TFオペレータ情報整合性チェック処理　異常系　TFオペレータ情報整合性チェック処理で、パスワード（4世代前）と変更後パスワードが一致
# No19.01.メイン処理_10.共通エラーチェック処理　正常系　共通エラーチェック処理が成功（エラー情報有り）
def test_tf_operator_change_password_case18(db: testTfOperator, create_header):
    header = create_header["header"]
    DATA["tfOperatorPassword"] = "4th_generation"
    DATA["tfOperatorConfirmPassword"] = "4th_generation"
    response = client.post("/api/2.0/tfoperator/changepassword", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "030014",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())

    # 最後にテスト用に挿入したデータを削除する
    db.delete(TF_OPERATOR_INFO["tfOperatorId"])


# No22.01.メイン処理_12.TFオペレータ更新処理　異常系　TFオペレータ更新処理が失敗する
def test_tf_operator_change_password_case22(mocker: MockerFixture, db: testTfOperator, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "TF_OPERATOR_CHANGE_PASSWORD_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    response = client.post("/api/2.0/tfoperator/changepassword", headers=header, data=json.dumps(DATA))
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
    db.delete(TF_OPERATOR_INFO["tfOperatorId"])


# No24.01.メイン処理_13.共通エラーチェック処理　正常系　共通エラーチェック処理が成功（エラー情報有り）
def test_tf_operator_change_password_case24(mocker: MockerFixture, db: testTfOperator, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "TF_OPERATOR_CHANGE_PASSWORD_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    response = client.post("/api/2.0/tfoperator/changepassword", headers=header, data=json.dumps(DATA))
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
    db.delete(TF_OPERATOR_INFO["tfOperatorId"])


# No.25.01.メイン処理_14.トランザクションコミット処理　トランザクションコミット処理が失敗する
def test_tf_operator_change_password_case25(mocker: MockerFixture, db: testTfOperator, create_header):
    # Exception
    mocker.patch.object(PostgresDbUtilClass, "commit_transaction", side_effect=Exception('testException'))
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/changepassword", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": response.json()["errorInfo"]
    }
    print(response.json())

    # 最後にテスト用に挿入したデータを削除する
    db.delete(TF_OPERATOR_INFO["tfOperatorId"])


# No.27.01.メイン処理_15.アクセストークン発行処理　異常系　アクセストークン発行処理が失敗する
def test_tf_operator_change_password_case27(mocker: MockerFixture, db: testTfOperator, create_header):
    mocker.patch("util.tokenUtil.TokenUtilClass.verify_token_closed").return_value = {'result': True, 'payload': {'tfOperatorId': 't-test4', 'tfOperatorName': 'テスト', 'accessToken': '14d517e61315fbf0545b765dd0e7ca296d65a5403aef84a360efe191e8b6d28a6c30dda7557e269b8c800327a13fa3ce5833fc0351c884addb340921883eac40d03d92281ac6a7cf18c32aebfd6bf48c71aedc781f707ca0714b3c804c1526e2d2a6ad0a'}}
    mocker.patch("util.tokenUtil.TokenUtilClass.create_token_closed").return_value = Exception('testException')
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/changepassword", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": response.json()["errorInfo"]
    }
    print(response.json())

    # 最後にテスト用に挿入したデータを削除する
    db.delete(TF_OPERATOR_INFO["tfOperatorId"])


# No.29.01.メイン処理_16.共通エラーチェック処理　正常系　共通エラーチェック処理が成功（エラー情報有り）
def test_tf_operator_change_password_case29(mocker: MockerFixture, db: testTfOperator, create_header):
    mocker.patch("util.tokenUtil.TokenUtilClass.verify_token_closed").return_value = {'result': True, 'payload': {'tfOperatorId': 't-test4', 'tfOperatorName': 'テスト', 'accessToken': '14d517e61315fbf0545b765dd0e7ca296d65a5403aef84a360efe191e8b6d28a6c30dda7557e269b8c800327a13fa3ce5833fc0351c884addb340921883eac40d03d92281ac6a7cf18c32aebfd6bf48c71aedc781f707ca0714b3c804c1526e2d2a6ad0a'}}
    mocker.patch("util.tokenUtil.TokenUtilClass.create_token_closed").return_value = Exception('testException')
    header = create_header["header"]
    data_copy = DATA.copy()
    response = client.post("/api/2.0/tfoperator/changepassword", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": response.json()["errorInfo"]
    }
    print(response.json())

    # 最後にテスト用に挿入したデータを削除する
    db.delete(TF_OPERATOR_INFO["tfOperatorId"])


# No31.パラメータ検証処理_01.パラメータ検証処理　異常系　引数．ヘッダパラメータ．タイムスタンプ　値が設定されていない（空値）
# No33.パラメータ検証処理_02.終了処理　正常系　変数．エラー情報がある
def test_tf_operator_change_password_case31_1_1(create_header):
    header = create_header["header"]
    header["timeStamp"] = ""
    response = client.post("/api/2.0/tfoperator/changepassword", headers=header, data=json.dumps(DATA))
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


# No31.パラメータ検証処理_01.パラメータ検証処理　異常系　引数．ヘッダパラメータ．タイムスタンプ　値が設定されている　文字列型である　２２桁である
# No33.パラメータ検証処理_02.終了処理　正常系　変数．エラー情報がある
def test_tf_operator_change_password_case31_1_2(create_header):
    header = create_header["header"]
    header["timeStamp"] = "2022/08/23 15:12:01.69"
    response = client.post("/api/2.0/tfoperator/changepassword", headers=header, data=json.dumps(DATA))
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


# No31.パラメータ検証処理_01.パラメータ検証処理　異常系　引数．ヘッダパラメータ．タイムスタンプ　値が設定されている　文字列型ではない
# No33.パラメータ検証処理_02.終了処理　正常系　変数．エラー情報がある
def test_tf_operator_change_password_case31_1_3(create_header):
    header = create_header["header"]
    header["timeStamp"] = 123456789012345678901234
    response = client.post("/api/2.0/tfoperator/changepassword", headers=header, data=json.dumps(DATA))
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
            },
            {
                "errorCode": "020003",
                "message": response.json()["errorInfo"][2]["message"]
            }
        ]
    }
    print(response.json())


# No31.パラメータ検証処理_01.パラメータ検証処理　異常系　引数．ヘッダパラメータ．アクセストークン　値が設定されていない（空値）
# No33.パラメータ検証処理_02.終了処理　正常系　変数．エラー情報がある
def test_tf_operator_change_password_case31_2_1(create_header):
    header = create_header["header"]
    header["accessToken"] = ""
    response = client.post("/api/2.0/tfoperator/changepassword", headers=header, data=json.dumps(DATA))
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


# No31.パラメータ検証処理_01.パラメータ検証処理　正常系　引数．ヘッダパラメータ．アクセストークン　値が設定されている　文字列型である　２０１桁である　入力可能文字以外が含まれる（全角）
# No33.パラメータ検証処理_02.終了処理　正常系　変数．エラー情報がある
def test_tf_operator_change_password_case31_2_2(create_header):
    header = create_header["header"]
    header["accessToken"] = "１23456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901"
    response = client.post("/api/2.0/tfoperator/changepassword", headers=header, data=json.dumps(DATA))
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


# No31.パラメータ検証処理_01.パラメータ検証処理　正常系　引数．ヘッダパラメータ．アクセストークン　値が設定されている　文字列型ではない　２０１桁である
# No33.パラメータ検証処理_02.終了処理　正常系　変数．エラー情報がある
def test_tf_operator_change_password_case31_2_3(create_header):
    header = create_header["header"]
    header["accessToken"] = 123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901
    response = client.post("/api/2.0/tfoperator/changepassword", headers=header, data=json.dumps(DATA))
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


# No31.パラメータ検証処理_01.パラメータ検証処理　異常系　引数．リクエストボディ．TFオペレータパスワード　値が設定されていない（空値）
# No33.パラメータ検証処理_02.終了処理　正常系　変数．エラー情報がある
def test_tf_operator_change_password_case31_3_1(create_header):
    header = create_header["header"]
    DATA["tfOperatorPassword"] = ""
    response = client.post("/api/2.0/tfoperator/changepassword", headers=header, data=json.dumps(DATA))
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
                "errorCode": "020010",
                "message": response.json()["errorInfo"][2]["message"]
            },
            {
                "errorCode": "030007",
                "message": response.json()["errorInfo"][3]["message"]
            }
        ]
    }
    print(response.json())


# No31.パラメータ検証処理_01.パラメータ検証処理　異常系　引数．リクエストボディ．TFオペレータパスワード　値が設定されている　文字列型ではない　７桁である　英大文字、英小文字、数字、記号のうち３種類未満
# No33.パラメータ検証処理_02.終了処理　正常系　変数．エラー情報がある
def test_tf_operator_change_password_case31_3_2(create_header):
    header = create_header["header"]
    DATA["tfOperatorPassword"] = 1234567
    response = client.post("/api/2.0/tfoperator/changepassword", headers=header, data=json.dumps(DATA))
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
            },
            {
                "errorCode": "030007",
                "message": response.json()["errorInfo"][2]["message"]
            }
        ]
    }
    print(response.json())


# No31.パラメータ検証処理_01.パラメータ検証処理　異常系　引数．リクエストボディ．TFオペレータパスワード　値が設定されている　文字列型である　６１８桁である　入力可能文字以外が含まれる（半角記号※２）　英大文字、英小文字、数字、記号のうち３種類未満
# No33.パラメータ検証処理_02.終了処理　正常系　変数．エラー情報がある
def test_tf_operator_change_password_case31_3_3(create_header):
    header = create_header["header"]
    DATA["tfOperatorPassword"] = "123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890testtest01123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890testtest01123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890testtest01123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890testtest01123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890testtest01123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890testtest01123456789012345678"
    response = client.post("/api/2.0/tfoperator/changepassword", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020002",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020010",
                "message": response.json()["errorInfo"][1]["message"]
            },
            {
                "errorCode": "030007",
                "message": response.json()["errorInfo"][2]["message"]
            }
        ]
    }
    print(response.json())


# No31.パラメータ検証処理_01.パラメータ検証処理　正常系　引数．リクエストボディ．TFオペレータパスワード　値が設定されている　文字列型である　８桁である　入力可能文字のみ（入力可能文字規則※１）　英大文字、英小文字、数字、記号のうち３種類以上
def test_tf_operator_change_password_case31_3_4(create_header):
    header = create_header["header"]
    DATA["tfOperatorPassword"] = "test_1234"
    response = client.post("/api/2.0/tfoperator/changepassword", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No31.パラメータ検証処理_01.パラメータ検証処理　正常系　引数．リクエストボディ．TFオペレータパスワード　値が設定されている　文字列型である　６１７桁である　入力可能文字のみ（入力可能文字規則※１）　英大文字、英小文字、数字、記号のうち３種類以上
def test_tf_operator_change_password_case31_3_5(create_header):
    header = create_header["header"]
    DATA["tfOperatorPassword"] = "123456789_12345678901234567890123456789012345678901234567890123456789012345678901234567890testtest01123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890testtest01123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890testtest01123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890testtest01123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890testtest01123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890testtest0112345678901234567"
    DATA["tfOperatorConfirmPassword"] = "123456789_12345678901234567890123456789012345678901234567890123456789012345678901234567890testtest01123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890testtest01123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890testtest01123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890testtest01123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890testtest01123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890testtest0112345678901234567"
    response = client.post("/api/2.0/tfoperator/changepassword", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No31.パラメータ検証処理_01.パラメータ検証処理　異常系　引数．リクエストボディ．TFオペレータパスワード(確認用)　値が設定されていない（空値）
# No33.パラメータ検証処理_02.終了処理　正常系　変数．エラー情報がある
def test_tf_operator_change_password_case31_4_1(create_header):
    header = create_header["header"]
    DATA["tfOperatorConfirmPassword"] = ""
    response = client.post("/api/2.0/tfoperator/changepassword", headers=header, data=json.dumps(DATA))
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
                "errorCode": "020010",
                "message": response.json()["errorInfo"][2]["message"]
            },
            {
                "errorCode": "030007",
                "message": response.json()["errorInfo"][3]["message"]
            }
        ]
    }
    print(response.json())


# No31.パラメータ検証処理_01.パラメータ検証処理　異常系　引数．リクエストボディ．TFオペレータパスワード(確認用)　値が設定されている　文字列型ではない　７桁である　英大文字、英小文字、数字、記号のうち３種類未満
# No33.パラメータ検証処理_02.終了処理　正常系　変数．エラー情報がある
def test_tf_operator_change_password_case31_4_2(create_header):
    header = create_header["header"]
    DATA["tfOperatorConfirmPassword"] = 1234567
    response = client.post("/api/2.0/tfoperator/changepassword", headers=header, data=json.dumps(DATA))
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
            },
            {
                "errorCode": "030007",
                "message": response.json()["errorInfo"][2]["message"]
            }
        ]
    }
    print(response.json())


# No31.パラメータ検証処理_01.パラメータ検証処理　異常系　引数．リクエストボディ．TFオペレータパスワード(確認用)　値が設定されている　文字列型である　６１８桁である　英大文字、英小文字、数字、記号のうち３種類未満
# No33.パラメータ検証処理_02.終了処理　正常系　変数．エラー情報がある
def test_tf_operator_change_password_case31_4_3(create_header):
    header = create_header["header"]
    DATA["tfOperatorConfirmPassword"] = "123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890testtest01123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890testtest01123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890testtest01123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890testtest01123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890testtest01123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890testtest01123456789012345678"
    response = client.post("/api/2.0/tfoperator/changepassword", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020002",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020010",
                "message": response.json()["errorInfo"][1]["message"]
            },
            {
                "errorCode": "030007",
                "message": response.json()["errorInfo"][2]["message"]
            }
        ]
    }
    print(response.json())


# No31.パラメータ検証処理_01.パラメータ検証処理　異常系　引数．リクエストボディ．TFオペレータパスワード(確認用)　値が設定されている　文字列型である　８桁である　入力可能文字のみ（入力可能文字規則※１）　英大文字、英小文字、数字、記号のうち３種類以上
# No33.パラメータ検証処理_02.終了処理　正常系　変数．エラー情報がある
def test_tf_operator_change_password_case31_4_4(create_header):
    header = create_header["header"]
    DATA["tfOperatorConfirmPassword"] = "test_1234"
    response = client.post("/api/2.0/tfoperator/changepassword", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No31.パラメータ検証処理_01.パラメータ検証処理　正常系　引数．リクエストボディ．TFオペレータパスワード(確認用)　値が設定されている　文字列型である　６１７桁である　入力可能文字のみ（入力可能文字規則※１）　英大文字、英小文字、数字、記号のうち３種類以上
# No33.パラメータ検証処理_02.終了処理　正常系　変数．エラー情報がある
def test_tf_operator_change_password_case31_4_5(create_header):
    header = create_header["header"]
    DATA["tfOperatorPassword"] = "123456789_12345678901234567890123456789012345678901234567890123456789012345678901234567890testtest01123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890testtest01123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890testtest01123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890testtest01123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890testtest01123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890testtest0112345678901234567"
    DATA["tfOperatorConfirmPassword"] = "123456789_12345678901234567890123456789012345678901234567890123456789012345678901234567890testtest01123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890testtest01123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890testtest01123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890testtest01123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890testtest01123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890testtest0112345678901234567"
    response = client.post("/api/2.0/tfoperator/changepassword", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No31.パラメータ検証処理_01.パラメータ検証処理　異常系　引数．リクエストボディ．TFオペレータパスワードと引数．リクエストボディ．TFオペレータパスワード(確認用)　値が一致しない
# No33.パラメータ検証処理_02.終了処理　正常系　変数．エラー情報がある
def test_tf_operator_change_password_case31_5_1(create_header):
    header = create_header["header"]
    DATA["tfOperatorPassword"] = "test_1234"
    DATA["tfOperatorConfirmPassword"] = "test_12345"
    response = client.post("/api/2.0/tfoperator/changepassword", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "030007",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No31.パラメータ検証処理_01.パラメータ検証処理　異常系　引数．リクエストボディ．TFオペレータパスワードと、引数．リクエストボディ．TFオペレータID　値が同一である
# No33.パラメータ検証処理_02.終了処理　正常系　変数．エラー情報がある
def test_tf_operator_change_password_case31_6_1(create_header):
    header = create_header["header"]
    DATA["tfOperatorPassword"] = TF_OPERATOR_INFO["tfOperatorId"]
    DATA["tfOperatorId"] = TF_OPERATOR_INFO["tfOperatorId"]
    response = client.post("/api/2.0/tfoperator/changepassword", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020010",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "030007",
                "message": response.json()["errorInfo"][1]["message"]
            },
            {
                "errorCode": "030012",
                "message": response.json()["errorInfo"][2]["message"]
            }
        ]
    }
    print(response.json())


# No31.パラメータ検証処理_01.パラメータ検証処理　異常系　引数．リクエストボディ．TFオペレータパスワード(確認用)と、引数．リクエストボディ．TFオペレータID　値が同一である
# No33.パラメータ検証処理_02.終了処理　正常系　変数．エラー情報がある
def test_tf_operator_change_password_case31_7_1(create_header):
    header = create_header["header"]
    DATA["tfOperatorConfirmPassword"] = TF_OPERATOR_INFO["tfOperatorId"]
    DATA["tfOperatorId"] = TF_OPERATOR_INFO["tfOperatorId"]
    response = client.post("/api/2.0/tfoperator/changepassword", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020010",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "030007",
                "message": response.json()["errorInfo"][1]["message"]
            },
            {
                "errorCode": "030012",
                "message": response.json()["errorInfo"][2]["message"]
            }
        ]
    }
    print(response.json())


# No34.ロールバック処理_01.ロールバック処理　異常系　TFオペレータ更新トランザクションのロールバック処理が失敗する
# No36.ロールバック処理_02.共通エラーチェック処理　正常系　共通エラーチェック処理が成功（エラー情報有り）
def test_tf_operator_change_password_case34(mocker: MockerFixture, db: testTfOperator, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "TF_OPERATOR_CHANGE_PASSWORD_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    # Exception
    mocker.patch.object(PostgresDbUtilClass, "rollback_transaction", side_effect=Exception('testException'))
    header = create_header["header"]
    response = client.post("/api/2.0/tfoperator/changepassword", headers=header, data=json.dumps(DATA))
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
    db.delete(TF_OPERATOR_INFO["tfOperatorId"])


# No35.ロールバック処理_01.ロールバック処理　正常系　TFオペレータ更新トランザクションのロールバック処理が成功する
# No37.ロールバック処理_03.終了処理　正常系　変数．エラー情報がない
def test_tf_operator_change_password_case35(mocker: MockerFixture, db: testTfOperator, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "TF_OPERATOR_CHANGE_PASSWORD_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    response = client.post("/api/2.0/tfoperator/changepassword", headers=header, data=json.dumps(DATA))
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
    # db.delete(TF_OPERATOR_INFO["tfOperatorId"])
