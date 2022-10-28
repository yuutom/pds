from fastapi.testclient import TestClient
from app import app
from fastapi import Request
import pytest
from pytest_mock.plugin import MockerFixture
from util.commonUtil import CommonUtilClass
import util.logUtil as logUtil
from exceptionClass.PDSException import PDSException
from const.messageConst import MessageConstClass
from const.systemConst import SystemConstClass
from const.sqlConst import SqlConstClass

client = TestClient(app)

HEADER = {}
request_dict = {
    "tfOperatorId": "t-test3",
    "tfOperatorPassword": "abcdedABC123%"
}
trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", request_dict, Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
common_util = CommonUtilClass(trace_logger)


@pytest.fixture
def data():
    common_db_info_response = common_util.get_common_db_info_and_connection()
    yield {"approvalUserId": 't-test4', "approvalUserPassword": 'abcdedABC123%', "commonDbInfo": common_db_info_response}


# 01.引数検証処理チェック処理
# No1_1.引数．承認者TFオペレータIDの値が設定されていない (空値)
def test_check_approval_user_info_case1_1(data):
    data_copy = data.copy()
    data_copy["approvalUserId"] = ""
    with pytest.raises(PDSException) as e:
        common_util.check_approval_user_info(
            approvalUserId=data_copy["approvalUserId"],
            approvalUserPassword=data_copy["approvalUserPassword"],
            commonDbInfo=data_copy["commonDbInfo"]
        )

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "承認者TFオペレータID")
    }
    print(e)


# No1_2.引数．承認者TFオペレータIDの値が設定されている
def test_check_approval_user_info_case1_2(data):
    data_copy = data.copy()
    response = common_util.check_approval_user_info(
        approvalUserId=data_copy["approvalUserId"],
        approvalUserPassword=data_copy["approvalUserPassword"],
        commonDbInfo=data_copy["commonDbInfo"]
    )
    assert response == {
        "result": True
    }
    print(response)


# No1_3.引数．承認者TFオペレータパスワードの値が設定されていない (空値)
def test_check_approval_user_info_case1_3(data):
    data_copy = data.copy()
    data_copy["approvalUserPassword"] = ""
    with pytest.raises(PDSException) as e:
        common_util.check_approval_user_info(
            approvalUserId=data_copy["approvalUserId"],
            approvalUserPassword=data_copy["approvalUserPassword"],
            commonDbInfo=data_copy["commonDbInfo"]
        )

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "承認者TFオペレータパスワード")
    }
    print(e)


# No1_4.引数．承認者TFオペレータIDの値が設定されている
def test_check_approval_user_info_case1_4(data):
    data_copy = data.copy()
    response = common_util.check_approval_user_info(
        approvalUserId=data_copy["approvalUserId"],
        approvalUserPassword=data_copy["approvalUserPassword"],
        commonDbInfo=data_copy["commonDbInfo"]
    )
    assert response == {
        "result": True
    }
    print(response)


# No1_5.引数．共通DB接続情報の値が設定されていない (空値)
def test_check_approval_user_info_case1_5(data):
    data_copy = data.copy()
    data_copy["commonDbInfo"] = ""
    with pytest.raises(PDSException) as e:
        common_util.check_approval_user_info(
            approvalUserId=data_copy["approvalUserId"],
            approvalUserPassword=data_copy["approvalUserPassword"],
            commonDbInfo=data_copy["commonDbInfo"]
        )

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "共通DB接続情報")
    }
    print(e)


# No1_6.引数．共通DB接続情報の値が設定されている
def test_check_approval_user_info_case1_6(data):
    data_copy = data.copy()
    response = common_util.check_approval_user_info(
        approvalUserId=data_copy["approvalUserId"],
        approvalUserPassword=data_copy["approvalUserPassword"],
        commonDbInfo=data_copy["commonDbInfo"]
    )
    assert response == {
        "result": True
    }
    print(response)


# 02.パスワードのハッシュ化処理
# 正常系
# No2.「引数．承認TFオペレータパスワード」をハッシュ化してハッシュ化済パスワードを作成する
def test_check_approval_user_info_case2(data):
    data_copy = data.copy()
    response = common_util.check_approval_user_info(
        approvalUserId=data_copy["approvalUserId"],
        approvalUserPassword=data_copy["approvalUserPassword"],
        commonDbInfo=data_copy["commonDbInfo"]
    )
    assert response == {
        "result": True
    }
    print(response)


# 03.共通DB接続準備処理
# 異常系
# No3.接続に失敗する
# 設定値を異常な値に変更する
def test_check_approval_user_info_case3(data, mocker: MockerFixture):
    data_copy = data.copy()
    # Exception
    mocker.patch("util.commonUtil.CommonUtilClass.get_secret_info").return_value = {"host": "test", "port": "test", "username": "test", "password": "test"}
    response = common_util.check_approval_user_info(
        approvalUserId=data_copy["approvalUserId"],
        approvalUserPassword=data_copy["approvalUserPassword"],
        commonDbInfo=data_copy["commonDbInfo"]
    )
    assert response == {
        "result": False,
        'errorInfo': {
            'errorCode': '999999',
            'message': logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
        }
    }
    print(response)


# 正常系
# No4.接続に成功する
def test_check_approval_user_info_case4(data):
    data_copy = data.copy()
    response = common_util.check_approval_user_info(
        approvalUserId=data_copy["approvalUserId"],
        approvalUserPassword=data_copy["approvalUserPassword"],
        commonDbInfo=data_copy["commonDbInfo"]
    )
    assert response == {
        "result": True
    }
    print(response)


# 04.TFオペレータ取得処理
# 異常系
# No5.TFオペレータ取得処理が失敗する（posgresqlエラー）
def test_check_approval_user_info_case5(data, mocker: MockerFixture):
    data_copy = data.copy()
    mocker.patch.object(SqlConstClass, "CHECK_APPROVAL_USER_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    with pytest.raises(PDSException) as e:
        common_util.check_approval_user_info(
            approvalUserId=data_copy["approvalUserId"],
            approvalUserPassword=data_copy["approvalUserPassword"],
            commonDbInfo=data_copy["commonDbInfo"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "991028",
        "message": logUtil.message_build(MessageConstClass.ERRORS["991028"]["message"], "991028")
    }
    print(e)


# 異常系
# No6.TFオペレータ取得処理が失敗する（カウントが１件以外）
def test_check_approval_user_info_case6(data):
    data_copy = data.copy()
    data_copy["approvalUserId"] = "t-test5"
    with pytest.raises(PDSException) as e:
        common_util.check_approval_user_info(
            approvalUserId=data_copy["approvalUserId"],
            approvalUserPassword=data_copy["approvalUserPassword"],
            commonDbInfo=data_copy["commonDbInfo"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020004",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020004"]["message"], data_copy["approvalUserId"])
    }
    print(e)


# 正常系
# No7.TFオペレータ取得処理が成功する
def test_check_approval_user_info_case7(data):
    data_copy = data.copy()
    response = common_util.check_approval_user_info(
        approvalUserId=data_copy["approvalUserId"],
        approvalUserPassword=data_copy["approvalUserPassword"],
        commonDbInfo=data_copy["commonDbInfo"]
    )
    assert response == {
        "result": True
    }
    print(response)


# 05.共通エラーチェック処理
# 正常系
# No8.共通エラーチェック処理が成功（エラー情報有り）
def test_check_approval_user_info_case8(data, mocker: MockerFixture):
    data_copy = data.copy()
    mocker.patch.object(SqlConstClass, "CHECK_APPROVAL_USER_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    with pytest.raises(PDSException) as e:
        common_util.check_approval_user_info(
            approvalUserId=data_copy["approvalUserId"],
            approvalUserPassword=data_copy["approvalUserPassword"],
            commonDbInfo=data_copy["commonDbInfo"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "991028",
        "message": logUtil.message_build(MessageConstClass.ERRORS["991028"]["message"], "991028")
    }
    print(e)


# 06.終了処理
# 正常系
# No9.変数．エラー情報がない
def test_check_approval_user_info_case9(data):
    data_copy = data.copy()
    response = common_util.check_approval_user_info(
        approvalUserId=data_copy["approvalUserId"],
        approvalUserPassword=data_copy["approvalUserPassword"],
        commonDbInfo=data_copy["commonDbInfo"]
    )
    assert response == {
        "result": True
    }
    print(response)
