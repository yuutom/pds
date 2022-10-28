from fastapi.testclient import TestClient
from app import app
from fastapi import Request
import pytest
from util.kmsUtil import KmsUtilClass
import util.logUtil as logUtil
from exceptionClass.PDSException import PDSException
from const.messageConst import MessageConstClass
from const.systemConst import SystemConstClass
from pytest_mock.plugin import MockerFixture
import boto3
from botocore.stub import Stubber

client = TestClient(app)

trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
kms_util = KmsUtilClass(trace_logger)


@pytest.fixture
def data():
    yield {
        "kmsKeyId": "mrk-016ca5b891ed42cf84f9c01590611e4f"
    }


# 01.引数検証処理チェック処理
# KMS削除処理_01.引数検証処理チェック　シート参照
# No1_1.引数．KMSキーID_1
def test_delete_kms_key_case1_1(data):
    data_copy = data.copy()
    data_copy["kmsKeyId"] = None
    with pytest.raises(PDSException) as e:
        kms_util.delete_kms_key(
            kmsKeyId=data_copy["kmsKeyId"], replicate_delete_flg=True
        )

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "検索条件")
    }
    print(e)


# No1_2.引数．KMSキーID_2
def test_delete_kms_key_case1_2(data):
    data_copy = data.copy()
    data_copy["kmsKeyId"] = "mrk-f05f8b9b7ac74e02bd43ed15f2c3549c"
    kms_util.delete_kms_key(
        kmsKeyId=data_copy["kmsKeyId"], replicate_delete_flg=True
    )


# 02.KMSキー情報無効化処理
# 異常系
# No2.KMSの無効化に失敗する（6回以上）
def test_delete_kms_key_case2(mocker: MockerFixture, data):
    data_copy = data.copy()
    client = boto3.client(
        service_name="kms"
    )
    stubber = Stubber(client)
    stubber.add_response("disable_key", {"ResponseMetadata": {"HTTPStatusCode": "400"}})
    stubber.activate()
    kms_util.delete_kms_key(
        kmsKeyId=data_copy["kmsKeyId"], replicate_delete_flg=True
    )


# 正常系
# No3.KMSの無効化に成功する（1回目）
def test_delete_kms_key_case3(data):
    data_copy = data.copy()
    data_copy["kmsKeyId"] = "mrk-eb956e338e6940299496bf4f5398d35c"
    kms_util.delete_kms_key(
        kmsKeyId=data_copy["kmsKeyId"], replicate_delete_flg=True
    )


# 正常系
# No4.KMSの無効化に成功する（5回目）
def test_delete_kms_key_case4(data):
    data_copy = data.copy()
    data_copy["kmsKeyId"] = "mrk-eb2454502d8c43069a492dfa42983c86"
    response = kms_util.delete_kms_key(
        kmsKeyId=data_copy["kmsKeyId"]
    )
    assert response == {
        "result": True
    }
    print(response)


# 03.レプリケート削除フラグチェック処理
# 正常系
# No5.「引数．レプリケート削除フラグ」がfalseの場合
def test_delete_kms_key_case5(data):
    data_copy = data.copy()
    data_copy["kmsKeyId"] = "mrk-ebf6662046fe40bc8da69f66da2bb845"
    kms_util.delete_kms_key(
        kmsKeyId=data_copy["kmsKeyId"], replicate_delete_flg=False
    )


# 04.別リージョンKMSキー情報無効化処理
# 異常系
# No6.別リージョンのKMSの無効化に失敗する（6回以上）
def test_delete_kms_key_case6(mocker: MockerFixture, data):
    data_copy = data.copy()
    client = boto3.client(
        service_name="kms"
    )
    stubber = Stubber(client)
    stubber.add_response("disable_key", {"ResponseMetadata": {"HTTPStatusCode": "400"}})
    stubber.activate()
    response = kms_util.delete_kms_key(
        kmsKeyId=data_copy["kmsKeyId"], replicate_delete_flg=True
    )
    assert response == {
        "result": True
    }
    print(response)


# 正常系
# No7.別リージョンのKMSの無効化に成功する（1回目）
def test_delete_kms_key_case7(data):
    data_copy = data.copy()
    data_copy["kmsKeyId"] = "mrk-ecf611c6d83b481a94fa24692f0865f6"
    kms_util.delete_kms_key(
        kmsKeyId=data_copy["kmsKeyId"], replicate_delete_flg=True
    )


# 正常系
# No8.別リージョンのKMSの無効化に成功する（5回目）
def test_delete_kms_key_case8(data):
    data_copy = data.copy()
    data_copy["kmsKeyId"] = "mrk-eb2454502d8c43069a492dfa42983c86"
    response = kms_util.delete_kms_key(
        kmsKeyId=data_copy["kmsKeyId"]
    )
    assert response == {
        "result": True
    }
    print(response)


# 03.共通エラーチェック処理
# 正常系
# No9.共通エラーチェック処理が成功（エラー情報有り）
def test_delete_kms_key_case9(data):
    data_copy = data.copy()
    data_copy["kmsKeyId"] = "abcdefg"
    response = kms_util.delete_kms_key(
        kmsKeyId=data_copy["kmsKeyId"], replicate_delete_flg=True
    )
    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "990061",
            "message": logUtil.message_build(MessageConstClass.ERRORS["990061"]["message"], "990061")
        }
    }
    print(response)


# 04.KMSキー情報削除予定作成処理
# 異常系
# No10.KMSの削除に失敗する（6回以上）
def test_delete_kms_key_case10(mocker: MockerFixture, data):
    data_copy = data.copy()
    # Exception
    mocker.patch("boto3.client.").side_effect = Exception('testException')
    data_copy["kmsKeyId"] = "abcdefg"
    with pytest.raises(PDSException) as e:
        kms_util.delete_kms_key(
            kmsKeyId=data_copy["kmsKeyId"], replicate_delete_flg=True
        )

    assert e.value.args[0] == {
        "errorCode": "990061",
        "message": logUtil.message_build(MessageConstClass.ERRORS["990061"]["message"])
    }
    print(e)


# 正常系
# No11.KMSの削除に成功する（1回目）
def test_delete_kms_key_case11(data):
    data_copy = data.copy()
    data_copy["kmsKeyId"] = "mrk-eb2454502d8c43069a492dfa42983c86"
    kms_util.delete_kms_key(
        kmsKeyId=data_copy["kmsKeyId"], replicate_delete_flg=False
    )


# 正常系
# No12.KMSの削除に成功する（5回目）
def test_delete_kms_key_case12(data):
    data_copy = data.copy()
    response = kms_util.delete_kms_key(
        kmsKeyId=data_copy["kmsKeyId"], replicate_delete_flg=True
    )
    assert response == {
        "result": True
    }
    print(response)


# 07.レプリケート削除フラグチェック処理
# 正常系
# No13.「引数．レプリケート削除フラグ」がfalseの場合
def test_delete_kms_key_case13(data):
    data_copy = data.copy()
    data_copy["kmsKeyId"] = "mrk-ed9f69f52db349f19aa1016ebe9c241f"
    kms_util.delete_kms_key(
        kmsKeyId=data_copy["kmsKeyId"], replicate_delete_flg=False
    )


# 08.別リージョンKMSキー情報削除予定作成処理
# 異常系
# No14.別リージョンのKMSの削除に失敗する（6回以上）
def test_delete_kms_key_case14(mocker: MockerFixture, data):
    data_copy = data.copy()
    client = boto3.client(
        service_name="kms"
    )
    stubber = Stubber(client)
    stubber.add_response("disable_key", {"ResponseMetadata": {"HTTPStatusCode": "400"}})
    stubber.activate()
    response = kms_util.delete_kms_key(
        kmsKeyId=data_copy["kmsKeyId"], replicate_delete_flg=True
    )
    assert response == {
        "result": True
    }
    print(response)


# 正常系
# No15.別リージョンのKMSの削除に成功する（1回目）
def test_delete_kms_key_case15(data):
    data_copy = data.copy()
    data_copy["kmsKeyId"] = "mrk-ede43339aadf4443aef2aea3f249b212"
    kms_util.delete_kms_key(
        kmsKeyId=data_copy["kmsKeyId"], replicate_delete_flg=True
    )


# 正常系
# No16.別リージョンのKMSの削除に成功する（5回目）
def test_delete_kms_key_case16(data):
    data_copy = data.copy()
    data_copy["kmsKeyId"] = "mrk-eb2454502d8c43069a492dfa42983c86"
    response = kms_util.delete_kms_key(
        kmsKeyId=data_copy["kmsKeyId"]
    )
    assert response == {
        "result": True
    }
    print(response)


# 05.共通エラーチェック処理
# 正常系
# No17.共通エラーチェック処理が成功（エラー情報有り）
def test_delete_kms_key_case17(data):
    data_copy = data.copy()
    data_copy["kmsKeyId"] = "abcdefg"
    response = kms_util.delete_kms_key(
        kmsKeyId=data_copy["kmsKeyId"], replicate_delete_flg=True
    )
    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "990061",
            "message": logUtil.message_build(MessageConstClass.ERRORS["990061"]["message"], "990061")
        }
    }
    print(response)


# 06.終了処理
# 正常系
# No18.変数．エラー情報がない
def test_delete_kms_key_case18(data):
    data_copy = data.copy()
    data_copy["kmsKeyId"] = "mrk-eed7a197211440919cd0604cea147587"
    kms_util.delete_kms_key(
        kmsKeyId=data_copy["kmsKeyId"], replicate_delete_flg=True
    )
