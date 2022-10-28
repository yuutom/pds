from fastapi.testclient import TestClient
from const.sqlConst import SqlConstClass
from app import app
from fastapi import Request
import pytest
from pytest_mock.plugin import MockerFixture
import util.logUtil as logUtil
from util.commonUtil import CommonUtilClass
from util.postgresDbUtil import PostgresDbUtilClass
from util.billUtil import BillUtilClass
from exceptionClass.PDSException import PDSException
from const.messageConst import MessageConstClass
from const.billConst import billConstClass
from const.systemConst import SystemConstClass

client = TestClient(app)


trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
common_util = CommonUtilClass(trace_logger)
bill_util = BillUtilClass(trace_logger)

common_db_connection_resource: PostgresDbUtilClass = None
common_db_info_response = common_util.get_common_db_info_and_connection()

DATA = {
    "pdsUserId": "C0000012",
    "commonDbConnectionInfo": common_db_info_response
}


# No1.リソース請求金額計算処理_01.引数検証処理チェック処理　異常系　引数．PDSユーザIDの値が設定されていない場合
def test_resource_billing_exec_case1_1_1():
    data_copy = DATA.copy()
    data_copy["pdsUserId"] = ""
    with pytest.raises(PDSException) as e:
        bill_util.resource_billing_exec(pdsUserId=data_copy["pdsUserId"], common_db_info=data_copy["commonDbConnectionInfo"])

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "PDSユーザID")
    }
    print(e)


# No1.リソース請求金額計算処理_01.引数検証処理チェック処理　異常系　引数．共通DB接続情報の値が設定されていない場合
def test_resource_billing_exec_case1_2_1():
    data_copy = DATA.copy()
    data_copy["commonDbConnectionInfo"] = ""
    with pytest.raises(PDSException) as e:
        bill_util.resource_billing_exec(pdsUserId=data_copy["pdsUserId"], common_db_info=data_copy["commonDbConnectionInfo"])

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "共通DB接続情報")
    }
    print(e)


# No1.リソース請求金額計算処理_01.引数検証処理チェック処理　正常系　引数．PDSユーザIDの値が設定されている場合
# No1.リソース請求金額計算処理_01.引数検証処理チェック処理　正常系　引数．共通DB接続情報の値が設定されている場合
def test_resource_billing_exec_case1_1_2():
    data_copy = DATA.copy()
    response = bill_util.resource_billing_exec(pdsUserId=data_copy["pdsUserId"], common_db_info=data_copy["commonDbConnectionInfo"])
    assert response == {
        "result": True,
        "resourceBilling": billConstClass.BILL['charge01']
    }
    print(response)


# No2.リソース請求金額計算処理_02.PDSユーザ情報取得処理　正常系
# No5.リソース請求金額計算処理_03.共通エラーチェック処理　正常系
# No8.リソース請求金額計算処理_04.PDSユーザDB接続準備処理　正常系
# No9.リソース請求金額計算処理_05.CloudWatchコスト監視実行処理　正常系
# No10.リソース請求金額計算処理_06.金額取得処理　正常系
# No11.リソース請求金額計算処理_07.終了処理　正常系
def test_resource_billing_exec_case2():
    data_copy = DATA.copy()
    response = bill_util.resource_billing_exec(pdsUserId=data_copy["pdsUserId"], common_db_info=data_copy["commonDbConnectionInfo"])
    assert response == {
        "result": True,
        "resourceBilling": billConstClass.BILL['charge01']
    }
    print(response)


# No3.リソース請求金額計算処理_02. PDSユーザ情報取得処理　異常系　「変数．PDSユーザ取得結果」の要素数が0の場合
# No6.リソース請求金額計算処理_03.共通エラーチェック処理　正常系　共通エラーチェック処理が成功（エラー情報有り）
def test_resource_billing_exec_case3():
    data_copy = DATA.copy()
    data_copy["pdsUserId"] = "C0000050"
    with pytest.raises(PDSException) as e:
        bill_util.resource_billing_exec(pdsUserId=data_copy["pdsUserId"], common_db_info=data_copy["commonDbConnectionInfo"])

    assert e.value.args[0] == {
        "errorCode": "020004",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020004"]["message"], data_copy["pdsUserId"])
    }
    print(e)


# No4.リソース請求金額計算処理_02. PDSユーザ情報取得処理　異常系　postgresqlのエラーが発生
def test_resource_billing_exec_case4(mocker: MockerFixture):
    data_copy = DATA.copy()
    mocker.patch.object(SqlConstClass, "PDS_USER_RESOURCE_BILLING_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    with pytest.raises(PDSException) as e:
        bill_util.resource_billing_exec(pdsUserId=data_copy["pdsUserId"], common_db_info=data_copy["commonDbConnectionInfo"])

    assert e.value.args[0] == {
        "errorCode": "999999",
        "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
    }
    print(e)


# No7.リソース請求金額計算処理_04.PDSユーザDB接続準備処理　異常系　接続に失敗する　設定値を異常な値に変更する
def test_resource_billing_exec_case7(mocker: MockerFixture):
    data_copy = DATA.copy()
    mocker.patch("util.commonUtil.CommonUtilClass.get_secret_info").return_value = {"host": "test", "port": "test", "username": "test", "password": "test"}
    with pytest.raises(PDSException) as e:
        bill_util.resource_billing_exec(pdsUserId=data_copy["pdsUserId"], common_db_info=data_copy["commonDbConnectionInfo"])

    assert e.value.args[0] == {
        "errorCode": "999999",
        "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
    }
    print(e)
