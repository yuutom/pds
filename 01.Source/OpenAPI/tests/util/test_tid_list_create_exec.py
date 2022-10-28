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

client = TestClient(app)

HEADER = {"pds_user_domain_name": "toppan-f", "pds_user_id": "C0123456"}
SEARCH_CRITERIA = {
    "userIdMatchMode": "前方一致",
    "userIdStr": "C0123456",
    "dataJsonKey": None,
    "dataMatchMode": "前方一致",
    "dataStr": "taro",
    "imageHash": "glakjgirhul",
    "fromDate": "2023/01/01",
    "toDate": "2023/12/31"
}

trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
common_util = CommonUtilClass(trace_logger)
pds_user_domain_check_result = common_util.check_pds_user_domain(HEADER["pds_user_domain_name"], HEADER["pds_user_id"])
PDS_USER_INFO = pds_user_domain_check_result["pdsUserInfo"]


@pytest.fixture
def create_common_util():
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    common_util = CommonUtilClass(trace_logger)
    yield common_util


# 01.引数検証処理チェック処理
# No1_1.引数．検索条件の値が設定されていない (空値)
def test_tid_list_create_exec1_1(mocker: MockerFixture, create_common_util):
    SEARCH_CRITERIA = None
    with pytest.raises(PDSException) as e:
        common_util.tid_list_create_exec(
            SEARCH_CRITERIA,
            PDS_USER_INFO
        )

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "検索条件")
    }
    print(e)


# No1_2.引数．検索条件の値が設定されている
def test_tid_list_create_exec1_2(mocker: MockerFixture, create_common_util):
    response = common_util.tid_list_create_exec(
        SEARCH_CRITERIA,
        PDS_USER_INFO
    )
    assert response == {
        "result": True,
        "tidList": response["tidList"]
    }
    print(response)


# No1_3.引数．PDSユーザ情報の値が設定されていない (空値)
def test_tid_list_create_exec1_3(mocker: MockerFixture, create_common_util):
    PDS_USER_INFO = None
    with pytest.raises(PDSException) as e:
        common_util.tid_list_create_exec(
            SEARCH_CRITERIA,
            PDS_USER_INFO
        )

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "PDSユーザ情報")
    }
    print(e)


# No1_4.引数．PDSユーザ情報の値が設定されている
def test_tid_list_create_exec1_4(mocker: MockerFixture, create_common_util):
    response = common_util.tid_list_create_exec(
        SEARCH_CRITERIA,
        PDS_USER_INFO
    )
    assert response == {
        "result": True,
        "tidList": response["tidList"]
    }
    print(response)


# 02.MongoDB検索判定処理
# No2.「引数．保存データJsonキー情報」がNullの場合、「04.個人情報検索処理」に遷移する
def test_tid_list_create_exec2(mocker: MockerFixture, create_common_util):
    response = common_util.tid_list_create_exec(
        SEARCH_CRITERIA,
        PDS_USER_INFO
    )
    assert response == {
        "result": True,
        "tidList": response["tidList"]
    }
    print(response)


# No3.「引数．保存データJsonキー情報」がNull以外の場合、「02.MongoDB検索処理」に遷移する
def test_tid_list_create_exec3(mocker: MockerFixture, create_common_util):
    SEARCH_CRITERIA["dataJsonKey"] = "data.name.first"
    common_util: CommonUtilClass = create_common_util
    response = common_util.tid_list_create_exec(
        SEARCH_CRITERIA,
        PDS_USER_INFO
    )
    assert response == {
        "result": True,
        "tidList": response["tidList"]
    }
    print(response)


# 03.MongoDB検索処理
# No4.MongoDB検索処理が失敗する
def test_tid_list_create_exec4(mocker: MockerFixture, create_common_util):
    SEARCH_CRITERIA["dataJsonKey"] = "data.name.first"
    common_util: CommonUtilClass = create_common_util
    mocker.patch("util.commonUtil.CommonUtilClass.mongodb_search").side_effect = Exception('testException')
    with pytest.raises(PDSException) as e:
        common_util.tid_list_create_exec(
            SEARCH_CRITERIA,
            PDS_USER_INFO
        )

    assert e.value.args[0] == {
        "errorCode": "999999",
        "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
    }
    print(e)


# No5.MongoDB検索処理が成功する
def test_tid_list_create_exec5(mocker: MockerFixture, create_common_util):
    SEARCH_CRITERIA["dataJsonKey"] = "data.name.first"
    common_util: CommonUtilClass = create_common_util
    response = common_util.tid_list_create_exec(
        SEARCH_CRITERIA,
        PDS_USER_INFO
    )
    assert response == {
        "result": True,
        "tidList": response["tidList"]
    }
    print(response)


# 04.個人情報検索処理
# No6.個人情報検索処理が失敗する
def test_tid_list_create_exec6(mocker: MockerFixture, create_common_util):
    common_util: CommonUtilClass = create_common_util
    mocker.patch("util.commonUtil.CommonUtilClass.search_user_profile").side_effect = Exception('testException')
    with pytest.raises(PDSException) as e:
        common_util.tid_list_create_exec(
            SEARCH_CRITERIA,
            PDS_USER_INFO
        )
    assert e.value.args[0] == {
        "errorCode": "999999",
        "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
    }
    print(e)


# No7.個人情報検索処理が成功する
def test_tid_list_create_exec7(mocker: MockerFixture, create_common_util):
    common_util: CommonUtilClass = create_common_util
    response = common_util.tid_list_create_exec(
        SEARCH_CRITERIA,
        PDS_USER_INFO
    )
    assert response == {
        "result": True,
        "tidList": response["tidList"]
    }
    print(response)


# No8.TID重複除外処理が成功する
def test_tid_list_create_exec8(mocker: MockerFixture, create_common_util):
    SEARCH_CRITERIA["dataJsonKey"] = "data.name.first"
    common_util: CommonUtilClass = create_common_util
    response = common_util.tid_list_create_exec(
        SEARCH_CRITERIA,
        PDS_USER_INFO
    )
    assert response == {
        "result": True,
        "tidList": response["tidList"]
    }
    print(response)


# 07.終了処理
# No9.エラー情報がない
def test_tid_list_create_exec9(mocker: MockerFixture, create_common_util):
    common_util: CommonUtilClass = create_common_util
    response = common_util.tid_list_create_exec(
        SEARCH_CRITERIA,
        PDS_USER_INFO
    )
    assert response == {
        "result": True,
        "tidList": response["tidList"]
    }
    print(response)
