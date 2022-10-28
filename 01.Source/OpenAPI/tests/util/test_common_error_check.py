from fastapi.testclient import TestClient
from app import app
from fastapi import Request
import pytest
import util.logUtil as logUtil
from const.systemConst import SystemConstClass
from const.sqlConst import SqlConstClass
from util.commonUtil import CommonUtilClass
from const.messageConst import MessageConstClass
from util.tokenUtil import TokenUtilClass
from util.postgresDbUtil import PostgresDbUtilClass
from exceptionClass.PDSException import PDSException
from pytest_mock.plugin import MockerFixture
import json

client = TestClient(app)

trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
common_util = CommonUtilClass(trace_logger)
token_util = TokenUtilClass(trace_logger)


TF_OPERATOR_INFO = {
    "tfOperatorId": "pc-test",
    "tfOperatorName": "変更太郎"
}
DATA = {
    "pdsUserId": "C0000001",
    "fromDate": "2022/01/01",
    "toDate": "2022/12/31"
}
DATA2 = {
    "tfOperatorId": "create-unit-test",
    "tfOperatorName": "単体登録",
    "tfOperatorMail": "touroku@trk.co.jp"
}


@pytest.fixture
def data():
    yield {
        "errorInfo": {
            "errorCode": "020020",
            "message": logUtil.message_build(MessageConstClass.ERRORS["020020"]["message"], "TFオペレータ名")
        }
    }


@pytest.fixture
def create_header():
    token_result = token_util.create_token_closed(tfOperatorInfo=TF_OPERATOR_INFO, accessToken=None)
    yield {
        "header": {
            "Content-Type": "application/json",
            "accessToken": token_result["accessToken"],
            "timeStamp": "2022/08/23 15:12:01.690",
            "Authorization": "Bearer " + token_result["jwt"]
        }
    }


# 共通エラーチェック処理
# 01.エラー情報有無判定処理
# No1.◆正常系 「引数．エラー情報」がNullの場合、「05.終了処理」に遷移する
def test_common_error_check_case1(data):
    data_copy = data.copy()
    data_copy["errorInfo"] = None
    common_util.common_error_check(
        error_info=data_copy["errorInfo"]
    )


# No2.◆正常系 「引数．エラー情報」がNull以外の場合、「02.コールバック関数実行判定処理」に遷移する
def test_common_error_check_case2(data):
    data_copy = data.copy()
    with pytest.raises(PDSException) as e:
        common_util.common_error_check(
            error_info=data_copy["errorInfo"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == data_copy["errorInfo"]
    print(e)


# 02.コールバック関数実行判定処理
# No3.◆正常系 「引数．コールバック関数」がの要素数が0の場合、「04.例外オブジェクト作成処理」に遷移する
def test_common_error_check_case3(data):
    data_copy = data.copy()
    with pytest.raises(PDSException) as e:
        common_util.common_error_check(
            error_info=data_copy["errorInfo"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == data_copy["errorInfo"]
    print(e)


# No4.◆正常系 「引数．コールバック関数」の要素数が0以外の場合、「03.コールバック関数実行処理」に遷移する
def test_common_error_check_case4(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "TF_OPERATOR_REGISTER_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.post("/api/2.0/tfOperator/regist", headers=header, data=json.dumps(DATA2))
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


# 03.コールバック関数実行処理
# No5.◆異常系 コールバック関数実行処理が失敗する
def test_common_error_check_case5(mocker: MockerFixture, create_header):
    header = create_header["header"]
    # Exception
    mocker.patch.object(SqlConstClass, "TF_OPERATOR_REGISTER_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    mocker.patch.object(PostgresDbUtilClass, "rollback_transaction", side_effect=Exception('testException'))
    response = client.post("/api/2.0/tfOperator/regist", headers=header, data=json.dumps(DATA2))
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


# No6.◆正常系 コールバック関数実行処理が成功する
def test_common_error_check_case6(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "TF_OPERATOR_REGISTER_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.post("/api/2.0/tfOperator/regist", headers=header, data=json.dumps(DATA2))
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


# 04.例外オブジェクト作成処理
# No7.◆異常系　例外オブジェクト作成処理が失敗する
def test_common_error_check_case7(mocker: MockerFixture, data):
    data_copy = data.copy()
    data_copy["errorInfo"] = data.copy()
    mocker.patch("OpenAPI.exceptionClass.PDSException.PDSException").side_effect = Exception('testException')
    with pytest.raises(PDSException) as e:
        common_util.common_error_check(
            error_info=data_copy["errorInfo"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == data_copy["errorInfo"]
    print(e)


# No8.◆正常系　例外オブジェクト作成処理が成功する
def test_common_error_check_case8(data):
    data_copy = data.copy()
    with pytest.raises(PDSException) as e:
        common_util.common_error_check(
            error_info=data_copy["errorInfo"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == data_copy["errorInfo"]
    print(e)


# 05.終了処理
# No9.◆正常系
def test_common_error_check_case9(data):
    data_copy = data.copy()
    data_copy["errorInfo"] = None
    common_util.common_error_check(
        error_info=data_copy["errorInfo"]
    )