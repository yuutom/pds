import pytest
from fastapi import Request
from pytest_mock.plugin import MockerFixture
import util.logUtil as logUtil
from exceptionClass.PDSException import PDSException
from const.messageConst import MessageConstClass
from const.systemConst import SystemConstClass
from util.commonUtil import CommonUtilClass

KMS_ID = "fdb4c6aa-50b0-4ed1-bdad-32c21e0a0387"

DATA = {
    "transactionId": "transaction50000",
    "pdsUserId": "C9876543"
}


@pytest.fixture
def create_common_util():
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    common_util = CommonUtilClass(trace_logger)
    yield common_util


# 01.引数検証処理チェック処理
# No1_1.トランザクションIDの値が設定されていない (空値)
def test_transaction_delete_batch_queue_issue_case1_1(create_common_util):
    common_util: CommonUtilClass = create_common_util
    data_copy = DATA.copy()
    data_copy["transactionId"] = ""
    with pytest.raises(PDSException) as e:
        common_util.transaction_delete_batch_queue_issue(
            transactionId=data_copy["transactionId"],
            pdsUserId=data_copy["pdsUserId"]
        )

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "トランザクションID")
    }
    print(e)


# No1_2.トランザクションIDの値が設定されている
def test_transaction_delete_batch_queue_issue_case1_2(create_common_util):
    common_util: CommonUtilClass = create_common_util
    data_copy = DATA.copy()
    data_copy["transactionId"] = "transaction50001"
    try:
        response = common_util.transaction_delete_batch_queue_issue(
            transactionId=data_copy["transactionId"],
            pdsUserId=data_copy["pdsUserId"]
        )
        assert response is None
    except Exception as e:
        raise pytest.fail("raise" + e)


# No1_3.PDSユーザIDの値が設定されていない (空値)
def test_transaction_delete_batch_queue_issue_case1_3(create_common_util):
    common_util: CommonUtilClass = create_common_util
    data_copy = DATA.copy()
    data_copy["transactionId"] = "transaction50002"
    data_copy["pdsUserId"] = ""
    with pytest.raises(PDSException) as e:
        common_util.transaction_delete_batch_queue_issue(
            transactionId=data_copy["transactionId"],
            pdsUserId=data_copy["pdsUserId"]
        )

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "PDSユーザID")
    }
    print(e)


# No1_4.PDSユーザIDの値が設定されている
def test_transaction_delete_batch_queue_issue_case1_4(create_common_util):
    common_util: CommonUtilClass = create_common_util
    data_copy = DATA.copy()
    data_copy["transactionId"] = "transaction50003"
    try:
        response = common_util.transaction_delete_batch_queue_issue(
            transactionId=data_copy["transactionId"],
            pdsUserId=data_copy["pdsUserId"]
        )
        assert response is None
    except Exception as e:
        raise pytest.fail("raise" + e)


# No2.個人情報削除バッチキュー発行処理が失敗する
def test_transaction_delete_batch_queue_issue_case2(mocker: MockerFixture, create_common_util):
    # Exception
    common_util: CommonUtilClass = create_common_util
    mocker.patch.object(SystemConstClass, "SQS_QUEUE_NAME", "aaaaaa")
    data_copy = DATA.copy()
    data_copy["transactionId"] = "transaction50004"
    with pytest.raises(PDSException) as e:
        common_util.transaction_delete_batch_queue_issue(
            transactionId=data_copy["transactionId"],
            pdsUserId=data_copy["pdsUserId"]
        )

    assert e.value.args[0] == {
        "errorCode": "990051",
        "message": "予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：990051）"
    }
    print(e)


# No3.個人情報削除バッチキュー発行処理が成功する
def test_transaction_delete_batch_queue_issue_case3(create_common_util):
    common_util: CommonUtilClass = create_common_util

    data_copy = DATA.copy()
    data_copy["transactionId"] = "transaction50005"
    try:
        response = common_util.transaction_delete_batch_queue_issue(
            transactionId=data_copy["transactionId"],
            pdsUserId=data_copy["pdsUserId"]
        )
        assert response is None
    except Exception as e:
        raise pytest.fail("raise" + e)


# No4.共通エラーチェック処理が成功（エラー情報有り）
def test_transaction_delete_batch_queue_issue_case4(mocker: MockerFixture, create_common_util):
    # Exception
    common_util: CommonUtilClass = create_common_util
    mocker.patch.object(SystemConstClass, "SQS_QUEUE_NAME", "aaaaaa")
    data_copy = DATA.copy()
    data_copy["transactionId"] = "transaction50006"
    with pytest.raises(PDSException) as e:
        common_util.transaction_delete_batch_queue_issue(
            transactionId=data_copy["transactionId"],
            pdsUserId=data_copy["pdsUserId"]
        )

    assert e.value.args[0] == {
        "errorCode": "990051",
        "message": "予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：990051）"
    }
    print(e)


# No5.終了処理
def test_transaction_delete_batch_queue_issue_case5(mocker: MockerFixture, create_common_util):
    mocker.patch("util.kmsUtil.KmsUtilClass.generate_kms_data_key").side_effect = Exception('testException')
    common_util: CommonUtilClass = create_common_util
    data_copy = DATA.copy()
    data_copy["transactionId"] = "transaction50007"
    try:
        response = common_util.transaction_delete_batch_queue_issue(
            transactionId=data_copy["transactionId"],
            pdsUserId=data_copy["pdsUserId"]
        )
        assert response is None
    except Exception as e:
        raise pytest.fail("raise" + e)
