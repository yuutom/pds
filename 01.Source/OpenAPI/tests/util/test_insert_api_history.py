from const.sqlConst import SqlConstClass
from fastapi.testclient import TestClient
import json
import datetime
from app import app
from fastapi import Request
import pytest
from pytest_mock.plugin import MockerFixture
from util.commonUtil import CommonUtilClass
import util.commonUtil as commonUtil
from util.tokenUtil import TokenUtilClass
import util.logUtil as logUtil
from exceptionClass.PDSException import PDSException
from const.messageConst import MessageConstClass
from const.apitypeConst import apitypeConstClass
from const.systemConst import SystemConstClass
from util.postgresDbUtil import PostgresDbUtilClass

client = TestClient(app)

HEADER = {"pdsUserId": "C0000013", "pdsUserName": "API実行履歴登録テスト"}
trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
common_util = CommonUtilClass(trace_logger)
token_util = TokenUtilClass(trace_logger)


@pytest.fixture
def data():
    token_result = token_util.create_token_public(HEADER["pdsUserId"], HEADER["pdsUserName"], None)
    timeStamp = commonUtil.get_datetime_jst()
    yield {
        "execId": commonUtil.get_datetime_str_no_symbol() + commonUtil.get_random_ascii(13),
        "pdsUserId": HEADER["pdsUserId"],
        "apiType": apitypeConstClass.API_TYPE["DELETE"],
        "pathParamPdsUserDomainName": "toppan-f",
        "execPath": 'http://127.0.0.1:8000/api/2.0/toppan-f/transaction?tid=transaction100',
        "execParam": json.dumps({
            "path_param": {"pdsUserDomainName": "toppan-f"},
            "query_param": {"tid": "transaction100"},
            "header_param": {
                'pdsuserid': HEADER["pdsUserId"],
                'timestamp': timeStamp.strftime('%Y/%m/%d %H:%M:%S.%f')[:-3],
                'accesstoken': token_result["accessToken"],
                'authorization': 'Bearer ' + token_result["jwt"],
                'user-agent': 'PostmanRuntime/7.29.2',
                'accept': '*/*',
                'postman-token': 'b7aba963-23e3-4c2e-b26a-63e71229d0ae',
                'host': '127.0.0.1:8000',
                'accept-encoding': 'gzip, deflate, br',
                'connection': 'keep-alive'
            }
        }),
        "execStatus": True,
        "execUserId": None,
        "registerDatetime": commonUtil.get_str_datetime()
    }


def test_insert_api_history_case(data):
    data_copy = data.copy()
    data_copy["apiType"] = apitypeConstClass.API_TYPE["BATCH_DOWNLOAD"]
    data_copy["registerDatetime"] = "2023/01/01 00:00:00.001"
    response = common_util.insert_api_history(
        execId=data_copy["execId"],
        pdsUserId=data_copy["pdsUserId"],
        apiType=data_copy["apiType"],
        pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
        execPath=data_copy["execPath"],
        execParam=data_copy["execParam"],
        execStatus=data_copy["execStatus"],
        execUserId=data_copy["execUserId"],
        registerDatetime=data_copy["registerDatetime"]
    )
    assert response == {
        "result": True
    }
    print(response)


# 01.引数検証処理チェック処理
# API実行履歴登録処理_01.引数検証処理チェック　シート参照
# No1_1.引数．実行ID_1
def test_insert_api_history_case_1_1(data):
    data_copy = data.copy()
    data_copy["execId"] = ""
    with pytest.raises(PDSException) as e:
        common_util.insert_api_history(
            execId=data_copy["execId"],
            pdsUserId=data_copy["pdsUserId"],
            apiType=data_copy["apiType"],
            pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
            execPath=data_copy["execPath"],
            execParam=data_copy["execParam"],
            execStatus=data_copy["execStatus"],
            execUserId=data_copy["execUserId"],
            registerDatetime=data_copy["registerDatetime"]
        )

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "実行ID")
    }
    print(e)


# No1_2.引数．実行ID_2
def test_insert_api_history_case_1_2(data):
    data_copy = data.copy()
    data_copy["execId"] = 123456789
    with pytest.raises(PDSException) as e:
        common_util.insert_api_history(
            execId=data_copy["execId"],
            pdsUserId=data_copy["pdsUserId"],
            apiType=data_copy["apiType"],
            pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
            execPath=data_copy["execPath"],
            execParam=data_copy["execParam"],
            execStatus=data_copy["execStatus"],
            execUserId=data_copy["execUserId"],
            registerDatetime=data_copy["registerDatetime"]
        )

    assert e.value.args[0] == {
        "errorCode": "020019",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "実行ID", "文字列")
    }
    print(e)


# No1_3.引数．実行ID_3
def test_insert_api_history_case_1_3(data):
    data_copy = data.copy()
    response = common_util.insert_api_history(
        execId=data_copy["execId"],
        pdsUserId=data_copy["pdsUserId"],
        apiType=data_copy["apiType"],
        pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
        execPath=data_copy["execPath"],
        execParam=data_copy["execParam"],
        execStatus=data_copy["execStatus"],
        execUserId=data_copy["execUserId"],
        registerDatetime=data_copy["registerDatetime"]
    )
    assert response == {
        "result": True
    }
    print(response)


# No1_4.引数．API種別_1
def test_insert_api_history_case_1_4(data):
    data_copy = data.copy()
    data_copy["apiType"] = ""
    with pytest.raises(PDSException) as e:
        common_util.insert_api_history(
            execId=data_copy["execId"],
            pdsUserId=data_copy["pdsUserId"],
            apiType=data_copy["apiType"],
            pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
            execPath=data_copy["execPath"],
            execParam=data_copy["execParam"],
            execStatus=data_copy["execStatus"],
            execUserId=data_copy["execUserId"],
            registerDatetime=data_copy["registerDatetime"]
        )

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "API種別")
    }
    print(e)


# No1_5.引数．API種別_2
def test_insert_api_history_case_1_5(data):
    data_copy = data.copy()
    data_copy["apiType"] = 123456789
    with pytest.raises(PDSException) as e:
        common_util.insert_api_history(
            execId=data_copy["execId"],
            pdsUserId=data_copy["pdsUserId"],
            apiType=data_copy["apiType"],
            pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
            execPath=data_copy["execPath"],
            execParam=data_copy["execParam"],
            execStatus=data_copy["execStatus"],
            execUserId=data_copy["execUserId"],
            registerDatetime=data_copy["registerDatetime"]
        )

    assert e.value.args[0] == {
        "errorCode": "020019",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "API種別", "文字列")
    }
    print(e)


# No1_6.引数．API種別_3
def test_insert_api_history_case_1_6(data):
    data_copy = data.copy()
    data_copy["apiType"] = "０12345678"
    with pytest.raises(PDSException) as e:
        common_util.insert_api_history(
            execId=data_copy["execId"],
            pdsUserId=data_copy["pdsUserId"],
            apiType=data_copy["apiType"],
            pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
            execPath=data_copy["execPath"],
            execParam=data_copy["execParam"],
            execStatus=data_copy["execStatus"],
            execUserId=data_copy["execUserId"],
            registerDatetime=data_copy["registerDatetime"]
        )

    assert e.value.args[0] == {
        "errorCode": "020020",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020020"]["message"], "API種別")
    }
    print(e)


# No1_7.引数．API種別_4
def test_insert_api_history_case_1_7(data):
    data_copy = data.copy()
    data_copy["apiType"] = "9"
    with pytest.raises(PDSException) as e:
        common_util.insert_api_history(
            execId=data_copy["execId"],
            pdsUserId=data_copy["pdsUserId"],
            apiType=data_copy["apiType"],
            pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
            execPath=data_copy["execPath"],
            execParam=data_copy["execParam"],
            execStatus=data_copy["execStatus"],
            execUserId=data_copy["execUserId"],
            registerDatetime=data_copy["registerDatetime"]
        )

    assert e.value.args[0] == {
        "errorCode": "020020",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020020"]["message"], "API種別")
    }
    print(e)


# No1_8.引数．API種別_5
def test_insert_api_history_case_1_8(data):
    data_copy = data.copy()
    data_copy["apiType"] = 9
    with pytest.raises(PDSException) as e:
        common_util.insert_api_history(
            execId=data_copy["execId"],
            pdsUserId=data_copy["pdsUserId"],
            apiType=data_copy["apiType"],
            pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
            execPath=data_copy["execPath"],
            execParam=data_copy["execParam"],
            execStatus=data_copy["execStatus"],
            execUserId=data_copy["execUserId"],
            registerDatetime=data_copy["registerDatetime"]
        )

    assert e.value.args[0] == {
        "errorCode": "020019",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "API種別", "文字列")
    }
    print(e)


# No1_9.引数．API種別_6
def test_insert_api_history_case_1_9(data):
    data_copy = data.copy()
    response = common_util.insert_api_history(
        execId=data_copy["execId"],
        pdsUserId=data_copy["pdsUserId"],
        apiType=data_copy["apiType"],
        pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
        execPath=data_copy["execPath"],
        execParam=data_copy["execParam"],
        execStatus=data_copy["execStatus"],
        execUserId=data_copy["execUserId"],
        registerDatetime=data_copy["registerDatetime"]
    )
    assert response == {
        "result": True
    }
    print(response)


# No1_10.引数．パスパラメータPDSユーザドメイン_1
def test_insert_api_history_case_1_10(data):
    data_copy = data.copy()
    data_copy["pathParamPdsUserDomainName"] = 12345
    with pytest.raises(PDSException) as e:
        common_util.insert_api_history(
            execId=data_copy["execId"],
            pdsUserId=data_copy["pdsUserId"],
            apiType=data_copy["apiType"],
            pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
            execPath=data_copy["execPath"],
            execParam=data_copy["execParam"],
            execStatus=data_copy["execStatus"],
            execUserId=data_copy["execUserId"],
            registerDatetime=data_copy["registerDatetime"]
        )

    assert e.value.args[0] == {
        "errorCode": "020019",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "パスパラメータPDSユーザドメイン", "文字列")
    }
    print(e)


# No1_11.引数．パスパラメータPDSユーザドメイン_2
def test_insert_api_history_case_1_11(data):
    data_copy = data.copy()
    data_copy["pathParamPdsUserDomainName"] = "1234"
    with pytest.raises(PDSException) as e:
        common_util.insert_api_history(
            execId=data_copy["execId"],
            pdsUserId=data_copy["pdsUserId"],
            apiType=data_copy["apiType"],
            pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
            execPath=data_copy["execPath"],
            execParam=data_copy["execParam"],
            execStatus=data_copy["execStatus"],
            execUserId=data_copy["execUserId"],
            registerDatetime=data_copy["registerDatetime"]
        )

    assert e.value.args[0] == {
        "errorCode": "020016",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020016"]["message"], "パスパラメータPDSユーザドメイン", "5")
    }
    assert e.value.args[1] == {
        "errorCode": "020003",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "パスパラメータPDSユーザドメイン")
    }
    print(e)


# No1_12.引数．パスパラメータPDSユーザドメイン_3
def test_insert_api_history_case_1_12(data):
    data_copy = data.copy()
    data_copy["pathParamPdsUserDomainName"] = "abcdefghijk0123456789"
    with pytest.raises(PDSException) as e:
        common_util.insert_api_history(
            execId=data_copy["execId"],
            pdsUserId=data_copy["pdsUserId"],
            apiType=data_copy["apiType"],
            pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
            execPath=data_copy["execPath"],
            execParam=data_copy["execParam"],
            execStatus=data_copy["execStatus"],
            execUserId=data_copy["execUserId"],
            registerDatetime=data_copy["registerDatetime"]
        )

    assert e.value.args[0] == {
        "errorCode": "020002",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020002"]["message"], "パスパラメータPDSユーザドメイン", "20")
    }
    assert e.value.args[1] == {
        "errorCode": "020003",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "パスパラメータPDSユーザドメイン")
    }
    print(e)


# No1_13.引数．パスパラメータPDSユーザドメイン_4
def test_insert_api_history_case_1_13(data):
    data_copy = data.copy()
    data_copy["pathParamPdsUserDomainName"] = "ａbcdefghij0123456789"
    with pytest.raises(PDSException) as e:
        common_util.insert_api_history(
            execId=data_copy["execId"],
            pdsUserId=data_copy["pdsUserId"],
            apiType=data_copy["apiType"],
            pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
            execPath=data_copy["execPath"],
            execParam=data_copy["execParam"],
            execStatus=data_copy["execStatus"],
            execUserId=data_copy["execUserId"],
            registerDatetime=data_copy["registerDatetime"]
        )

    assert e.value.args[0] == {
        "errorCode": "020003",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "パスパラメータPDSユーザドメイン")
    }
    print(e)


# No1_14.引数．パスパラメータPDSユーザドメイン_5
def test_insert_api_history_case_1_14(data):
    data_copy = data.copy()
    data_copy["pathParamPdsUserDomainName"] = "Abcdefghij0123456789"
    with pytest.raises(PDSException) as e:
        common_util.insert_api_history(
            execId=data_copy["execId"],
            pdsUserId=data_copy["pdsUserId"],
            apiType=data_copy["apiType"],
            pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
            execPath=data_copy["execPath"],
            execParam=data_copy["execParam"],
            execStatus=data_copy["execStatus"],
            execUserId=data_copy["execUserId"],
            registerDatetime=data_copy["registerDatetime"]
        )

    assert e.value.args[0] == {
        "errorCode": "020003",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "パスパラメータPDSユーザドメイン")
    }
    print(e)


# No1_15.引数．パスパラメータPDSユーザドメイン_6
def test_insert_api_history_case_1_15(data):
    data_copy = data.copy()
    data_copy["pathParamPdsUserDomainName"] = 123456789012345678900
    with pytest.raises(PDSException) as e:
        common_util.insert_api_history(
            execId=data_copy["execId"],
            pdsUserId=data_copy["pdsUserId"],
            apiType=data_copy["apiType"],
            pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
            execPath=data_copy["execPath"],
            execParam=data_copy["execParam"],
            execStatus=data_copy["execStatus"],
            execUserId=data_copy["execUserId"],
            registerDatetime=data_copy["registerDatetime"]
        )

    assert e.value.args[0] == {
        "errorCode": "020019",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "パスパラメータPDSユーザドメイン", "文字列")
    }
    assert e.value.args[1] == {
        "errorCode": "020002",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020002"]["message"], "パスパラメータPDSユーザドメイン", "20")
    }
    print(e)


# No1_16.引数．パスパラメータPDSユーザドメイン_7
def test_insert_api_history_case_1_16(data):
    data_copy = data.copy()
    data_copy["pathParamPdsUserDomainName"] = 1234
    with pytest.raises(PDSException) as e:
        common_util.insert_api_history(
            execId=data_copy["execId"],
            pdsUserId=data_copy["pdsUserId"],
            apiType=data_copy["apiType"],
            pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
            execPath=data_copy["execPath"],
            execParam=data_copy["execParam"],
            execStatus=data_copy["execStatus"],
            execUserId=data_copy["execUserId"],
            registerDatetime=data_copy["registerDatetime"]
        )

    assert e.value.args[0] == {
        "errorCode": "020019",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "パスパラメータPDSユーザドメイン", "文字列")
    }
    assert e.value.args[1] == {
        "errorCode": "020016",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020016"]["message"], "パスパラメータPDSユーザドメイン", "5")
    }
    print(e)


# No1_17.引数．パスパラメータPDSユーザドメイン_8
def test_insert_api_history_case_1_17(data):
    data_copy = data.copy()
    data_copy["pathParamPdsUserDomainName"] = "A123"
    with pytest.raises(PDSException) as e:
        common_util.insert_api_history(
            execId=data_copy["execId"],
            pdsUserId=data_copy["pdsUserId"],
            apiType=data_copy["apiType"],
            pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
            execPath=data_copy["execPath"],
            execParam=data_copy["execParam"],
            execStatus=data_copy["execStatus"],
            execUserId=data_copy["execUserId"],
            registerDatetime=data_copy["registerDatetime"]
        )

    assert e.value.args[0] == {
        "errorCode": "020016",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020016"]["message"], "パスパラメータPDSユーザドメイン", "5")
    }
    assert e.value.args[1] == {
        "errorCode": "020003",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "パスパラメータPDSユーザドメイン")
    }
    print(e)


# No1_18.引数．パスパラメータPDSユーザドメイン_9
def test_insert_api_history_case_1_18(data):
    data_copy = data.copy()
    data_copy["pathParamPdsUserDomainName"] = "12345678901234567890a"
    with pytest.raises(PDSException) as e:
        common_util.insert_api_history(
            execId=data_copy["execId"],
            pdsUserId=data_copy["pdsUserId"],
            apiType=data_copy["apiType"],
            pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
            execPath=data_copy["execPath"],
            execParam=data_copy["execParam"],
            execStatus=data_copy["execStatus"],
            execUserId=data_copy["execUserId"],
            registerDatetime=data_copy["registerDatetime"]
        )

    assert e.value.args[0] == {
        "errorCode": "020002",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020002"]["message"], "パスパラメータPDSユーザドメイン", "20")
    }
    print(e)


# No1_19.引数．パスパラメータPDSユーザドメイン_10
def test_insert_api_history_case_1_19(data):
    data_copy = data.copy()
    data_copy["pathParamPdsUserDomainName"] = "abc12"
    response = common_util.insert_api_history(
        execId=data_copy["execId"],
        pdsUserId=data_copy["pdsUserId"],
        apiType=data_copy["apiType"],
        pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
        execPath=data_copy["execPath"],
        execParam=data_copy["execParam"],
        execStatus=data_copy["execStatus"],
        execUserId=data_copy["execUserId"],
        registerDatetime=data_copy["registerDatetime"]
    )
    assert response == {
        "result": True
    }
    print(response)


# No1_20.引数．パスパラメータPDSユーザドメイン_11
def test_insert_api_history_case_1_20(data):
    data_copy = data.copy()
    data_copy["pathParamPdsUserDomainName"] = "toppa"
    response = common_util.insert_api_history(
        execId=data_copy["execId"],
        pdsUserId=data_copy["pdsUserId"],
        apiType=data_copy["apiType"],
        pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
        execPath=data_copy["execPath"],
        execParam=data_copy["execParam"],
        execStatus=data_copy["execStatus"],
        execUserId=data_copy["execUserId"],
        registerDatetime=data_copy["registerDatetime"]
    )
    assert response == {
        "result": True
    }
    print(response)


# No1_21.引数．パスパラメータPDSユーザドメイン_12
def test_insert_api_history_case_1_21(data):
    data_copy = data.copy()
    data_copy["pathParamPdsUserDomainName"] = "abcdefghijklmn123456"
    response = common_util.insert_api_history(
        execId=data_copy["execId"],
        pdsUserId=data_copy["pdsUserId"],
        apiType=data_copy["apiType"],
        pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
        execPath=data_copy["execPath"],
        execParam=data_copy["execParam"],
        execStatus=data_copy["execStatus"],
        execUserId=data_copy["execUserId"],
        registerDatetime=data_copy["registerDatetime"]
    )
    assert response == {
        "result": True
    }
    print(response)


# No1_22.引数．実行パス_1
def test_insert_api_history_case_1_22(data):
    data_copy = data.copy()
    data_copy["execPath"] = ""
    with pytest.raises(PDSException) as e:
        common_util.insert_api_history(
            execId=data_copy["execId"],
            pdsUserId=data_copy["pdsUserId"],
            apiType=data_copy["apiType"],
            pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
            execPath=data_copy["execPath"],
            execParam=data_copy["execParam"],
            execStatus=data_copy["execStatus"],
            execUserId=data_copy["execUserId"],
            registerDatetime=data_copy["registerDatetime"]
        )

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "実行パス")
    }
    print(e)


# No1_23.引数．実行パス_2
def test_insert_api_history_case_1_23(data):
    data_copy = data.copy()
    data_copy["execPath"] = 12345
    with pytest.raises(PDSException) as e:
        common_util.insert_api_history(
            execId=data_copy["execId"],
            pdsUserId=data_copy["pdsUserId"],
            apiType=data_copy["apiType"],
            pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
            execPath=data_copy["execPath"],
            execParam=data_copy["execParam"],
            execStatus=data_copy["execStatus"],
            execUserId=data_copy["execUserId"],
            registerDatetime=data_copy["registerDatetime"]
        )

    assert e.value.args[0] == {
        "errorCode": "020019",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "実行パス", "文字列")
    }
    print(e)


# No1_24.引数．実行パス_3
def test_insert_api_history_case_1_24(data):
    data_copy = data.copy()
    response = common_util.insert_api_history(
        execId=data_copy["execId"],
        pdsUserId=data_copy["pdsUserId"],
        apiType=data_copy["apiType"],
        pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
        execPath=data_copy["execPath"],
        execParam=data_copy["execParam"],
        execStatus=data_copy["execStatus"],
        execUserId=data_copy["execUserId"],
        registerDatetime=data_copy["registerDatetime"]
    )
    assert response == {
        "result": True
    }
    print(response)


# No1_25.引数．実行パラメータ_1
def test_insert_api_history_case_1_25(data):
    data_copy = data.copy()
    data_copy["execParam"] = ""
    with pytest.raises(PDSException) as e:
        common_util.insert_api_history(
            execId=data_copy["execId"],
            pdsUserId=data_copy["pdsUserId"],
            apiType=data_copy["apiType"],
            pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
            execPath=data_copy["execPath"],
            execParam=data_copy["execParam"],
            execStatus=data_copy["execStatus"],
            execUserId=data_copy["execUserId"],
            registerDatetime=data_copy["registerDatetime"]
        )

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "実行パラメータ")
    }
    print(e)


# No1_26.引数．実行パラメータ_2
def test_insert_api_history_case_1_26(data):
    data_copy = data.copy()
    data_copy["execParam"] = 12345
    with pytest.raises(PDSException) as e:
        common_util.insert_api_history(
            execId=data_copy["execId"],
            pdsUserId=data_copy["pdsUserId"],
            apiType=data_copy["apiType"],
            pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
            execPath=data_copy["execPath"],
            execParam=data_copy["execParam"],
            execStatus=data_copy["execStatus"],
            execUserId=data_copy["execUserId"],
            registerDatetime=data_copy["registerDatetime"]
        )

    assert e.value.args[0] == {
        "errorCode": "020019",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "実行パラメータ", "文字列")
    }
    print(e)


# No1_27.引数．実行パラメータ_3
def test_insert_api_history_case_1_27(data):
    data_copy = data.copy()
    response = common_util.insert_api_history(
        execId=data_copy["execId"],
        pdsUserId=data_copy["pdsUserId"],
        apiType=data_copy["apiType"],
        pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
        execPath=data_copy["execPath"],
        execParam=data_copy["execParam"],
        execStatus=data_copy["execStatus"],
        execUserId=data_copy["execUserId"],
        registerDatetime=data_copy["registerDatetime"]
    )
    assert response == {
        "result": True
    }
    print(response)


# No1_28.引数．実行ステータス_1
def test_insert_api_history_case_1_28(data):
    data_copy = data.copy()
    data_copy["execStatus"] = ""
    with pytest.raises(PDSException) as e:
        common_util.insert_api_history(
            execId=data_copy["execId"],
            pdsUserId=data_copy["pdsUserId"],
            apiType=data_copy["apiType"],
            pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
            execPath=data_copy["execPath"],
            execParam=data_copy["execParam"],
            execStatus=data_copy["execStatus"],
            execUserId=data_copy["execUserId"],
            registerDatetime=data_copy["registerDatetime"]
        )

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "実行ステータス")
    }
    print(e)


# No1_29.引数．実行ステータス_2
def test_insert_api_history_case_1_29(data):
    data_copy = data.copy()
    data_copy["execStatus"] = 12345
    with pytest.raises(PDSException) as e:
        common_util.insert_api_history(
            execId=data_copy["execId"],
            pdsUserId=data_copy["pdsUserId"],
            apiType=data_copy["apiType"],
            pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
            execPath=data_copy["execPath"],
            execParam=data_copy["execParam"],
            execStatus=data_copy["execStatus"],
            execUserId=data_copy["execUserId"],
            registerDatetime=data_copy["registerDatetime"]
        )

    assert e.value.args[0] == {
        "errorCode": "020019",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "実行ステータス", "論理")
    }
    print(e)


# No1_30.引数．実行ステータス_3
def test_insert_api_history_case_1_30(data):
    data_copy = data.copy()
    response = common_util.insert_api_history(
        execId=data_copy["execId"],
        pdsUserId=data_copy["pdsUserId"],
        apiType=data_copy["apiType"],
        pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
        execPath=data_copy["execPath"],
        execParam=data_copy["execParam"],
        execStatus=data_copy["execStatus"],
        execUserId=data_copy["execUserId"],
        registerDatetime=data_copy["registerDatetime"]
    )
    assert response == {
        "result": True
    }
    print(response)


# No1_31.引数．実行ユーザID_1
def test_insert_api_history_case_1_31(data):
    data_copy = data.copy()
    data_copy["execUserId"] = 123
    with pytest.raises(PDSException) as e:
        common_util.insert_api_history(
            execId=data_copy["execId"],
            pdsUserId=data_copy["pdsUserId"],
            apiType=data_copy["apiType"],
            pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
            execPath=data_copy["execPath"],
            execParam=data_copy["execParam"],
            execStatus=data_copy["execStatus"],
            execUserId=data_copy["execUserId"],
            registerDatetime=data_copy["registerDatetime"]
        )

    assert e.value.args[0] == {
        "errorCode": "020019",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "実行ユーザID", "文字列")
    }
    print(e)


# No1_32.引数．実行ユーザID_2
def test_insert_api_history_case_1_32(data):
    data_copy = data.copy()
    data_copy["execUserId"] = "12"
    with pytest.raises(PDSException) as e:
        common_util.insert_api_history(
            execId=data_copy["execId"],
            pdsUserId=data_copy["pdsUserId"],
            apiType=data_copy["apiType"],
            pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
            execPath=data_copy["execPath"],
            execParam=data_copy["execParam"],
            execStatus=data_copy["execStatus"],
            execUserId=data_copy["execUserId"],
            registerDatetime=data_copy["registerDatetime"]
        )

    assert e.value.args[0] == {
        "errorCode": "020016",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020016"]["message"], "実行ユーザID", "3")
    }
    print(e)


# No1_33.引数．実行ユーザID_3
def test_insert_api_history_case_1_33(data):
    data_copy = data.copy()
    data_copy["execUserId"] = "abcdefghijklmnopq"
    with pytest.raises(PDSException) as e:
        common_util.insert_api_history(
            execId=data_copy["execId"],
            pdsUserId=data_copy["pdsUserId"],
            apiType=data_copy["apiType"],
            pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
            execPath=data_copy["execPath"],
            execParam=data_copy["execParam"],
            execStatus=data_copy["execStatus"],
            execUserId=data_copy["execUserId"],
            registerDatetime=data_copy["registerDatetime"]
        )

    assert e.value.args[0] == {
        "errorCode": "020002",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020002"]["message"], "実行ユーザID", "16")
    }
    print(e)


# No1_34.引数．実行ユーザID_4
def test_insert_api_history_case_1_34(data):
    data_copy = data.copy()
    data_copy["execUserId"] = 12345678901234567
    with pytest.raises(PDSException) as e:
        common_util.insert_api_history(
            execId=data_copy["execId"],
            pdsUserId=data_copy["pdsUserId"],
            apiType=data_copy["apiType"],
            pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
            execPath=data_copy["execPath"],
            execParam=data_copy["execParam"],
            execStatus=data_copy["execStatus"],
            execUserId=data_copy["execUserId"],
            registerDatetime=data_copy["registerDatetime"]
        )

    assert e.value.args[0] == {
        "errorCode": "020019",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "実行ユーザID", "文字列")
    }
    assert e.value.args[1] == {
        "errorCode": "020002",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020002"]["message"], "実行ユーザID", "16")
    }
    print(e)


# No1_35.引数．実行ユーザID_5
def test_insert_api_history_case_1_35(data):
    data_copy = data.copy()
    data_copy["execUserId"] = 12
    with pytest.raises(PDSException) as e:
        common_util.insert_api_history(
            execId=data_copy["execId"],
            pdsUserId=data_copy["pdsUserId"],
            apiType=data_copy["apiType"],
            pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
            execPath=data_copy["execPath"],
            execParam=data_copy["execParam"],
            execStatus=data_copy["execStatus"],
            execUserId=data_copy["execUserId"],
            registerDatetime=data_copy["registerDatetime"]
        )

    assert e.value.args[0] == {
        "errorCode": "020019",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "実行ユーザID", "文字列")
    }
    assert e.value.args[1] == {
        "errorCode": "020016",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020016"]["message"], "実行ユーザID", "3")
    }
    print(e)


# No1_36.引数．実行ユーザID_6
def test_insert_api_history_case_1_36(data):
    data_copy = data.copy()
    data_copy["execUserId"] = "123"
    response = common_util.insert_api_history(
        execId=data_copy["execId"],
        pdsUserId=data_copy["pdsUserId"],
        apiType=data_copy["apiType"],
        pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
        execPath=data_copy["execPath"],
        execParam=data_copy["execParam"],
        execStatus=data_copy["execStatus"],
        execUserId=data_copy["execUserId"],
        registerDatetime=data_copy["registerDatetime"]
    )
    assert response == {
        "result": True
    }
    print(response)


# No1_37.引数．実行ユーザID_7
def test_insert_api_history_case_1_37(data):
    data_copy = data.copy()
    data_copy["execUserId"] = "1234567890123456"
    response = common_util.insert_api_history(
        execId=data_copy["execId"],
        pdsUserId=data_copy["pdsUserId"],
        apiType=data_copy["apiType"],
        pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
        execPath=data_copy["execPath"],
        execParam=data_copy["execParam"],
        execStatus=data_copy["execStatus"],
        execUserId=data_copy["execUserId"],
        registerDatetime=data_copy["registerDatetime"]
    )
    assert response == {
        "result": True
    }
    print(response)


# No1_38.引数．実行日時_1
def test_insert_api_history_case_1_38(data):
    data_copy = data.copy()
    data_copy["registerDatetime"] = None
    with pytest.raises(PDSException) as e:
        common_util.insert_api_history(
            execId=data_copy["execId"],
            pdsUserId=data_copy["pdsUserId"],
            apiType=data_copy["apiType"],
            pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
            execPath=data_copy["execPath"],
            execParam=data_copy["execParam"],
            execStatus=data_copy["execStatus"],
            execUserId=data_copy["execUserId"],
            registerDatetime=data_copy["registerDatetime"]
        )

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "実行日時")
    }
    print(e)


# No1_39.引数．実行日時_2
def test_insert_api_history_case_1_39(data):
    data_copy = data.copy()
    data_copy["registerDatetime"] = 1234567890
    with pytest.raises(PDSException) as e:
        common_util.insert_api_history(
            execId=data_copy["execId"],
            pdsUserId=data_copy["pdsUserId"],
            apiType=data_copy["apiType"],
            pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
            execPath=data_copy["execPath"],
            execParam=data_copy["execParam"],
            execStatus=data_copy["execStatus"],
            execUserId=data_copy["execUserId"],
            registerDatetime=data_copy["registerDatetime"]
        )

    assert e.value.args[0] == {
        "errorCode": "020019",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "実行日時", "文字列")
    }
    print(e)


# No1_40.引数．実行日時_3
def test_insert_api_history_case_1_40(data):
    data_copy = data.copy()
    data_copy["registerDatetime"] = "2022/09/09 12:00:00.00"
    with pytest.raises(PDSException) as e:
        common_util.insert_api_history(
            execId=data_copy["execId"],
            pdsUserId=data_copy["pdsUserId"],
            apiType=data_copy["apiType"],
            pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
            execPath=data_copy["execPath"],
            execParam=data_copy["execParam"],
            execStatus=data_copy["execStatus"],
            execUserId=data_copy["execUserId"],
            registerDatetime=data_copy["registerDatetime"]
        )

    assert e.value.args[0] == {
        "errorCode": "020014",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020014"]["message"], "実行日時", "23")
    }
    print(e)


# No1_41.引数．実行日時_4
def test_insert_api_history_case_1_41(data):
    data_copy = data.copy()
    data_copy["registerDatetime"] = "2022/09/09 12:00:00.0000"
    with pytest.raises(PDSException) as e:
        common_util.insert_api_history(
            execId=data_copy["execId"],
            pdsUserId=data_copy["pdsUserId"],
            apiType=data_copy["apiType"],
            pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
            execPath=data_copy["execPath"],
            execParam=data_copy["execParam"],
            execStatus=data_copy["execStatus"],
            execUserId=data_copy["execUserId"],
            registerDatetime=data_copy["registerDatetime"]
        )

    assert e.value.args[0] == {
        "errorCode": "020014",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020014"]["message"], "実行日時", "23")
    }
    print(e)


# No1_42.引数．実行日時_5
def test_insert_api_history_case_1_42(data):
    data_copy = data.copy()
    data_copy["registerDatetime"] = "022/009/09 12:00:00.000"
    with pytest.raises(PDSException) as e:
        common_util.insert_api_history(
            execId=data_copy["execId"],
            pdsUserId=data_copy["pdsUserId"],
            apiType=data_copy["apiType"],
            pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
            execPath=data_copy["execPath"],
            execParam=data_copy["execParam"],
            execStatus=data_copy["execStatus"],
            execUserId=data_copy["execUserId"],
            registerDatetime=data_copy["registerDatetime"]
        )

    assert e.value.args[0] == {
        "errorCode": "020003",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "実行日時")
    }
    print(e)


# No1_43.引数．実行日時_6
def test_insert_api_history_case_1_43(data):
    data_copy = data.copy()
    data_copy["registerDatetime"] = "2022/09/09 012:0:00.000"
    with pytest.raises(PDSException) as e:
        common_util.insert_api_history(
            execId=data_copy["execId"],
            pdsUserId=data_copy["pdsUserId"],
            apiType=data_copy["apiType"],
            pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
            execPath=data_copy["execPath"],
            execParam=data_copy["execParam"],
            execStatus=data_copy["execStatus"],
            execUserId=data_copy["execUserId"],
            registerDatetime=data_copy["registerDatetime"]
        )

    assert e.value.args[0] == {
        "errorCode": "020003",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "実行日時")
    }
    print(e)


# No1_44.引数．実行日時_7
def test_insert_api_history_case_1_44(data):
    data_copy = data.copy()
    data_copy["registerDatetime"] = "２０２２/09/09 12:00:00.000"
    with pytest.raises(PDSException) as e:
        common_util.insert_api_history(
            execId=data_copy["execId"],
            pdsUserId=data_copy["pdsUserId"],
            apiType=data_copy["apiType"],
            pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
            execPath=data_copy["execPath"],
            execParam=data_copy["execParam"],
            execStatus=data_copy["execStatus"],
            execUserId=data_copy["execUserId"],
            registerDatetime=data_copy["registerDatetime"]
        )

    assert e.value.args[0] == {
        "errorCode": "020003",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "実行日時")
    }
    print(e)


# No1_45.引数．実行日時_8
def test_insert_api_history_case_1_45(data):
    data_copy = data.copy()
    data_copy["registerDatetime"] = "2022/09/09 12:00:00.iii"
    with pytest.raises(PDSException) as e:
        common_util.insert_api_history(
            execId=data_copy["execId"],
            pdsUserId=data_copy["pdsUserId"],
            apiType=data_copy["apiType"],
            pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
            execPath=data_copy["execPath"],
            execParam=data_copy["execParam"],
            execStatus=data_copy["execStatus"],
            execUserId=data_copy["execUserId"],
            registerDatetime=data_copy["registerDatetime"]
        )

    assert e.value.args[0] == {
        "errorCode": "020003",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "実行日時")
    }
    print(e)


# No1_46.引数．実行日時_9
def test_insert_api_history_case_1_46(data):
    data_copy = data.copy()
    data_copy["registerDatetime"] = "2022/09/09 12:000:0.iii"
    with pytest.raises(PDSException) as e:
        common_util.insert_api_history(
            execId=data_copy["execId"],
            pdsUserId=data_copy["pdsUserId"],
            apiType=data_copy["apiType"],
            pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
            execPath=data_copy["execPath"],
            execParam=data_copy["execParam"],
            execStatus=data_copy["execStatus"],
            execUserId=data_copy["execUserId"],
            registerDatetime=data_copy["registerDatetime"]
        )

    assert e.value.args[0] == {
        "errorCode": "020003",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "実行日時")
    }
    print(e)


# No1_47.引数．実行日時_10
def test_insert_api_history_case_1_47(data):
    data_copy = data.copy()
    data_copy["registerDatetime"] = "2022/09/09 12:000:00.iii"
    with pytest.raises(PDSException) as e:
        common_util.insert_api_history(
            execId=data_copy["execId"],
            pdsUserId=data_copy["pdsUserId"],
            apiType=data_copy["apiType"],
            pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
            execPath=data_copy["execPath"],
            execParam=data_copy["execParam"],
            execStatus=data_copy["execStatus"],
            execUserId=data_copy["execUserId"],
            registerDatetime=data_copy["registerDatetime"]
        )

    assert e.value.args[0] == {
        "errorCode": "020014",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020014"]["message"], "実行日時", "23")
    }
    assert e.value.args[1] == {
        "errorCode": "020003",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "実行日時")
    }
    print(e)


# No1_48.引数．実行日時_11
def test_insert_api_history_case_1_48(data):
    data_copy = data.copy()
    data_copy["registerDatetime"] = datetime.datetime(2022, 9, 9, 12, 0, 000, 000)
    with pytest.raises(PDSException) as e:
        common_util.insert_api_history(
            execId=data_copy["execId"],
            pdsUserId=data_copy["pdsUserId"],
            apiType=data_copy["apiType"],
            pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
            execPath=data_copy["execPath"],
            execParam=data_copy["execParam"],
            execStatus=data_copy["execStatus"],
            execUserId=data_copy["execUserId"],
            registerDatetime=data_copy["registerDatetime"]
        )

    assert e.value.args[0] == {
        "errorCode": "020019",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "実行日時", "文字列")
    }
    print(e)


# No1_49.引数．実行日時12
def test_insert_api_history_case_1_49(data):
    data_copy = data.copy()
    response = common_util.insert_api_history(
        execId=data_copy["execId"],
        pdsUserId=data_copy["pdsUserId"],
        apiType=data_copy["apiType"],
        pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
        execPath=data_copy["execPath"],
        execParam=data_copy["execParam"],
        execStatus=data_copy["execStatus"],
        execUserId=data_copy["execUserId"],
        registerDatetime=data_copy["registerDatetime"]
    )
    assert response == {
        "result": True
    }
    print(response)


# 異常系
# No2.PDSユーザIDが異常な値
def test_insert_api_history_case2(data):
    data_copy = data.copy()
    data_copy["pdsUserId"] = "abcdefg"
    with pytest.raises(PDSException) as e:
        common_util.insert_api_history(
            execId=data_copy["execId"],
            pdsUserId=data_copy["pdsUserId"],
            apiType=data_copy["apiType"],
            pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
            execPath=data_copy["execPath"],
            execParam=data_copy["execParam"],
            execStatus=data_copy["execStatus"],
            execUserId=data_copy["execUserId"],
            registerDatetime=data_copy["registerDatetime"]
        )

    assert e.value.args[0] == {
        "errorCode": "020014",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020014"]["message"], "PDSユーザID", "8")
    }
    print(e)


# 正常系
# No3.PDSユーザIDが正常な値
def test_insert_api_history_case3(data):
    data_copy = data.copy()
    response = common_util.insert_api_history(
        execId=data_copy["execId"],
        pdsUserId=data_copy["pdsUserId"],
        apiType=data_copy["apiType"],
        pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
        execPath=data_copy["execPath"],
        execParam=data_copy["execParam"],
        execStatus=data_copy["execStatus"],
        execUserId=data_copy["execUserId"],
        registerDatetime=data_copy["registerDatetime"]
    )
    assert response == {
        "result": True
    }
    print(response)


# 02.DB接続準備処理
# 異常系
# No4.接続に失敗する
def test_insert_api_history_case4(data, mocker: MockerFixture):
    data_copy = data.copy()
    # Exception
    mocker.patch("util.commonUtil.CommonUtilClass.get_secret_info").return_value = {"host": "test", "port": "test", "username": "test", "password": "test"}
    response = common_util.insert_api_history(
        execId=data_copy["execId"],
        pdsUserId=data_copy["pdsUserId"],
        apiType=data_copy["apiType"],
        pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
        execPath=data_copy["execPath"],
        execParam=data_copy["execParam"],
        execStatus=data_copy["execStatus"],
        execUserId=data_copy["execUserId"],
        registerDatetime=data_copy["registerDatetime"]
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
# No5.接続に成功する
def test_insert_api_history_case5(data):
    data_copy = data.copy()
    response = common_util.insert_api_history(
        execId=data_copy["execId"],
        pdsUserId=data_copy["pdsUserId"],
        apiType=data_copy["apiType"],
        pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
        execPath=data_copy["execPath"],
        execParam=data_copy["execParam"],
        execStatus=data_copy["execStatus"],
        execUserId=data_copy["execUserId"],
        registerDatetime=data_copy["registerDatetime"]
    )
    assert response == {
        "result": True
    }
    print(response)


# 03.API実行履歴登録処理
# 正常系
# No6.API実行履歴登録処理が失敗する
def test_insert_api_history_case6(data, mocker: MockerFixture):
    data_copy = data.copy()
    # Exception
    mocker.patch.object(SqlConstClass, "API_HISTORY_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    with pytest.raises(PDSException) as e:
        common_util.insert_api_history(
            execId=data_copy["execId"],
            pdsUserId=data_copy["pdsUserId"],
            apiType=data_copy["apiType"],
            pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
            execPath=data_copy["execPath"],
            execParam=data_copy["execParam"],
            execStatus=data_copy["execStatus"],
            execUserId=data_copy["execUserId"],
            registerDatetime=data_copy["registerDatetime"]
        )
    assert e.value.args[0] == {
        "errorCode": "991028",
        "message": logUtil.message_build(MessageConstClass.ERRORS["991028"]["message"], "991028")
    }
    print(e)


# 正常系
# No7.API実行履歴登録処理が成功する
def test_insert_api_history_case7(data):
    data_copy = data.copy()
    response = common_util.insert_api_history(
        execId=data_copy["execId"],
        pdsUserId=data_copy["pdsUserId"],
        apiType=data_copy["apiType"],
        pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
        execPath=data_copy["execPath"],
        execParam=data_copy["execParam"],
        execStatus=data_copy["execStatus"],
        execUserId=data_copy["execUserId"],
        registerDatetime=data_copy["registerDatetime"]
    )
    assert response == {
        "result": True
    }
    print(response)


# 04.終了処理
# No8.変数．エラー情報がある
def test_insert_api_history_case8(data, mocker: MockerFixture):
    data_copy = data.copy()
    # Exception
    mocker.patch.object(SqlConstClass, "API_HISTORY_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    with pytest.raises(PDSException) as e:
        common_util.insert_api_history(
            execId=data_copy["execId"],
            pdsUserId=data_copy["pdsUserId"],
            apiType=data_copy["apiType"],
            pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
            execPath=data_copy["execPath"],
            execParam=data_copy["execParam"],
            execStatus=data_copy["execStatus"],
            execUserId=data_copy["execUserId"],
            registerDatetime=data_copy["registerDatetime"]
        )
    assert e.value.args[0] == {
        "errorCode": "991028",
        "message": logUtil.message_build(MessageConstClass.ERRORS["991028"]["message"], "991028")
    }
    print(e)


# No9.変数．エラー情報がない
def test_insert_api_history_case9(data):
    data_copy = data.copy()
    response = common_util.insert_api_history(
        execId=data_copy["execId"],
        pdsUserId=data_copy["pdsUserId"],
        apiType=data_copy["apiType"],
        pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
        execPath=data_copy["execPath"],
        execParam=data_copy["execParam"],
        execStatus=data_copy["execStatus"],
        execUserId=data_copy["execUserId"],
        registerDatetime=data_copy["registerDatetime"]
    )
    assert response == {
        "result": True
    }
    print(response)


# 03.トランザクション作成処理
# No.10.トランザクション作成に失敗する


# No.11.トランザクション作成に成功する


# 06.トランザクションコミット処理
# No.12.トランザクションコミット処理に失敗する
def test_insert_api_history_case12(data, mocker: MockerFixture):
    data_copy = data.copy()
    # Exception
    mocker.patch.object(PostgresDbUtilClass, "commit_transaction", side_effect=Exception('testException'))
    with pytest.raises(PDSException) as e:
        common_util.insert_api_history(
            execId=data_copy["execId"],
            pdsUserId=data_copy["pdsUserId"],
            apiType=data_copy["apiType"],
            pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
            execPath=data_copy["execPath"],
            execParam=data_copy["execParam"],
            execStatus=data_copy["execStatus"],
            execUserId=data_copy["execUserId"],
            registerDatetime=data_copy["registerDatetime"]
        )
    assert e.value.args[0] == {
        "errorCode": "999999",
        "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
    }
    print(e)


# No.13.トランザクションコミット処理に成功する
def test_insert_api_history_case13(data):
    data_copy = data.copy()
    response = common_util.insert_api_history(
        execId=data_copy["execId"],
        pdsUserId=data_copy["pdsUserId"],
        apiType=data_copy["apiType"],
        pathParamPdsUserDomainName=data_copy["pathParamPdsUserDomainName"],
        execPath=data_copy["execPath"],
        execParam=data_copy["execParam"],
        execStatus=data_copy["execStatus"],
        execUserId=data_copy["execUserId"],
        registerDatetime=data_copy["registerDatetime"]
    )
    assert response == {
        "result": True
    }
    print(response)
