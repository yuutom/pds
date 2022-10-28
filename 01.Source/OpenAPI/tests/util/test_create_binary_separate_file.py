import pytest
from fastapi import Request
from pytest_mock.plugin import MockerFixture
import util.logUtil as logUtil
from exceptionClass.PDSException import PDSException
from const.messageConst import MessageConstClass
from const.systemConst import SystemConstClass
from util.userProfileUtil import UserProfileUtilClass

KMS_ID = "fdb4c6aa-50b0-4ed1-bdad-32c21e0a0387"

DATA = {
    "transactionId": "transaction50000",
    "splitImage": b"aiueo",
    "binaryDataId": "abcdefghijklmnopqrstuvwxyz000000",
    "sepNo": 1
}


@pytest.fixture
def create_user_profile_util():
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    user_profile_util = UserProfileUtilClass(trace_logger)
    yield user_profile_util


# 01.引数検証処理チェック処理
# No1_1.トランザクションIDの値が設定されていない (空値)
def test_create_binary_separate_file_case1_1(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    data_copy = DATA.copy()
    data_copy["transactionId"] = ""
    with pytest.raises(PDSException) as e:
        user_profile_util.create_binary_separate_file(
            transactionId=data_copy["transactionId"],
            splitImage=data_copy["splitImage"],
            userProfileKmsId=KMS_ID,
            binaryDataId=data_copy["binaryDataId"],
            sepNo=data_copy["sepNo"]
        )

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "トランザクションID")
    }
    print(e)


# No1_2.トランザクションIDの値が設定されている
def test_create_binary_separate_file_case1_2(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    data_copy = DATA.copy()
    data_copy["transactionId"] = "transaction50001"
    response = user_profile_util.create_binary_separate_file(
        transactionId=data_copy["transactionId"],
        splitImage=data_copy["splitImage"],
        userProfileKmsId=KMS_ID,
        binaryDataId=data_copy["binaryDataId"],
        sepNo=data_copy["sepNo"]
    )

    assert response == {
        "result": True,
        "fileSavePath": response["fileSavePath"],
        "uploadFile": response["uploadFile"],
        "kmsChiperDataKey": response["kmsChiperDataKey"],
        "chiperNonce": response["chiperNonce"]
    }
    print(response)


# No1_3.分割バイナリデータの値が設定されていない (空値)
def test_create_binary_separate_file_case1_3(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    data_copy = DATA.copy()
    data_copy["transactionId"] = "transaction50002"
    data_copy["splitImage"] = ""
    with pytest.raises(PDSException) as e:
        user_profile_util.create_binary_separate_file(
            transactionId=data_copy["transactionId"],
            splitImage=data_copy["splitImage"],
            userProfileKmsId=KMS_ID,
            binaryDataId=data_copy["binaryDataId"],
            sepNo=data_copy["sepNo"]
        )

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "分割バイナリデータ")
    }
    print(e)


# No1_4.分割バイナリデータの値が設定されている
def test_create_binary_separate_file_case1_4(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    data_copy = DATA.copy()
    data_copy["transactionId"] = "transaction50003"
    response = user_profile_util.create_binary_separate_file(
        transactionId=data_copy["transactionId"],
        splitImage=data_copy["splitImage"],
        userProfileKmsId=KMS_ID,
        binaryDataId=data_copy["binaryDataId"],
        sepNo=data_copy["sepNo"]
    )

    assert response == {
        "result": True,
        "fileSavePath": response["fileSavePath"],
        "uploadFile": response["uploadFile"],
        "kmsChiperDataKey": response["kmsChiperDataKey"],
        "chiperNonce": response["chiperNonce"]
    }
    print(response)


# No1_5.個人情報暗号・復号化用KMSIDの値が設定されていない (空値)
def test_create_binary_separate_file_case1_5(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util

    data_copy = DATA.copy()
    data_copy["transactionId"] = "transaction50004"
    with pytest.raises(PDSException) as e:
        user_profile_util.create_binary_separate_file(
            transactionId=data_copy["transactionId"],
            splitImage=data_copy["splitImage"],
            userProfileKmsId="",
            binaryDataId=data_copy["binaryDataId"],
            sepNo=data_copy["sepNo"]
        )

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "個人情報暗号・復号化用KMSID")
    }
    print(e)


# No1_6.個人情報暗号・復号化用KMSIDの値が設定されている
def test_create_binary_separate_file_case1_6(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util

    data_copy = DATA.copy()
    data_copy["transactionId"] = "transaction50005"
    response = user_profile_util.create_binary_separate_file(
        transactionId=data_copy["transactionId"],
        splitImage=data_copy["splitImage"],
        userProfileKmsId=KMS_ID,
        binaryDataId=data_copy["binaryDataId"],
        sepNo=data_copy["sepNo"]
    )

    assert response == {
        "result": True,
        "fileSavePath": response["fileSavePath"],
        "uploadFile": response["uploadFile"],
        "kmsChiperDataKey": response["kmsChiperDataKey"],
        "chiperNonce": response["chiperNonce"]
    }
    print(response)


# No1_7.保存画像IDの値が設定されていない (空値)
def test_create_binary_separate_file_case1_7(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util

    data_copy = DATA.copy()
    data_copy["transactionId"] = "transaction50006"
    data_copy["binaryDataId"] = ""
    with pytest.raises(PDSException) as e:
        user_profile_util.create_binary_separate_file(
            transactionId=data_copy["transactionId"],
            splitImage=data_copy["splitImage"],
            userProfileKmsId=KMS_ID,
            binaryDataId=data_copy["binaryDataId"],
            sepNo=data_copy["sepNo"]
        )

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "保存画像ID")
    }
    print(e)


# No1_8.保存画像IDの値が設定されている
def test_create_binary_separate_file_case1_8(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util

    data_copy = DATA.copy()
    data_copy["transactionId"] = "transaction50007"
    response = user_profile_util.create_binary_separate_file(
        transactionId=data_copy["transactionId"],
        splitImage=data_copy["splitImage"],
        userProfileKmsId=KMS_ID,
        binaryDataId=data_copy["binaryDataId"],
        sepNo=data_copy["sepNo"]
    )

    assert response == {
        "result": True,
        "fileSavePath": response["fileSavePath"],
        "uploadFile": response["uploadFile"],
        "kmsChiperDataKey": response["kmsChiperDataKey"],
        "chiperNonce": response["chiperNonce"]
    }
    print(response)


# No1_9.セパレートNoの値が設定されていない (空値)
def test_create_binary_separate_file_case1_9(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util

    data_copy = DATA.copy()
    data_copy["transactionId"] = "transaction50008"
    data_copy["sepNo"] = ""
    with pytest.raises(PDSException) as e:
        user_profile_util.create_binary_separate_file(
            transactionId=data_copy["transactionId"],
            splitImage=data_copy["splitImage"],
            userProfileKmsId=KMS_ID,
            binaryDataId=data_copy["binaryDataId"],
            sepNo=data_copy["sepNo"]
        )

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "セパレートNo")
    }
    print(e)


# No1_10.セパレートNoの値が設定されている
def test_create_binary_separate_file_case1_10(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util

    data_copy = DATA.copy()
    data_copy["transactionId"] = "transaction50009"
    response = user_profile_util.create_binary_separate_file(
        transactionId=data_copy["transactionId"],
        splitImage=data_copy["splitImage"],
        userProfileKmsId=KMS_ID,
        binaryDataId=data_copy["binaryDataId"],
        sepNo=data_copy["sepNo"]
    )

    assert response == {
        "result": True,
        "fileSavePath": response["fileSavePath"],
        "uploadFile": response["uploadFile"],
        "kmsChiperDataKey": response["kmsChiperDataKey"],
        "chiperNonce": response["chiperNonce"]
    }
    print(response)


# No2.KMSデータキー発行処理が失敗する
def test_create_binary_separate_file_case2(mocker: MockerFixture, create_user_profile_util):
    # Exception
    mocker.patch("util.kmsUtil.KmsUtilClass.generate_kms_data_key").side_effect = Exception('testException')
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    data_copy = DATA.copy()
    data_copy["transactionId"] = "transaction50010"
    response = user_profile_util.create_binary_separate_file(
        transactionId=data_copy["transactionId"],
        splitImage=data_copy["splitImage"],
        userProfileKmsId=KMS_ID,
        binaryDataId=data_copy["binaryDataId"],
        sepNo=data_copy["sepNo"]
    )
    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "990065",
            "message": "予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：990065）"
        }
    }
    print(response)


# No3.KMSデータキー発行処理が成功する
def test_create_binary_separate_file_case3(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util

    data_copy = DATA.copy()
    data_copy["transactionId"] = "transaction50011"
    response = user_profile_util.create_binary_separate_file(
        transactionId=data_copy["transactionId"],
        splitImage=data_copy["splitImage"],
        userProfileKmsId=KMS_ID,
        binaryDataId=data_copy["binaryDataId"],
        sepNo=data_copy["sepNo"]
    )

    assert response == {
        "result": True,
        "fileSavePath": response["fileSavePath"],
        "uploadFile": response["uploadFile"],
        "kmsChiperDataKey": response["kmsChiperDataKey"],
        "chiperNonce": response["chiperNonce"]
    }
    print(response)


# No4.「変数．分割バイナリファイル情報作成処理実行結果．エラー情報」がNullの場合、「05.PDSユーザDB接続準備処理」に遷移する
def test_create_binary_separate_file_case4(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util

    data_copy = DATA.copy()
    data_copy["transactionId"] = "transaction50012"
    response = user_profile_util.create_binary_separate_file(
        transactionId=data_copy["transactionId"],
        splitImage=data_copy["splitImage"],
        userProfileKmsId=KMS_ID,
        binaryDataId=data_copy["binaryDataId"],
        sepNo=data_copy["sepNo"]
    )

    assert response == {
        "result": True,
        "fileSavePath": response["fileSavePath"],
        "uploadFile": response["uploadFile"],
        "kmsChiperDataKey": response["kmsChiperDataKey"],
        "chiperNonce": response["chiperNonce"]
    }
    print(response)


# No5.「変数．分割バイナリファイル情報作成処理実行結果．エラー情報」がNull以外の場合、「04.分割バイナリファイル情報作成エラー処理」に遷移する
def test_create_binary_separate_file_case5(mocker: MockerFixture, create_user_profile_util):
    mocker.patch("util.kmsUtil.KmsUtilClass.generate_kms_data_key").side_effect = Exception('testException')
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    data_copy = DATA.copy()
    data_copy["transactionId"] = "transaction50013"
    response = user_profile_util.create_binary_separate_file(
        transactionId=data_copy["transactionId"],
        splitImage=data_copy["splitImage"],
        userProfileKmsId=KMS_ID,
        binaryDataId=data_copy["binaryDataId"],
        sepNo=data_copy["sepNo"]
    )
    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "990065",
            "message": "予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：990065）"
        }
    }
    print(response)


# No6.レスポンス情報を作成し、返却する
def test_create_binary_separate_file_case6(mocker: MockerFixture, create_user_profile_util):
    mocker.patch("util.kmsUtil.KmsUtilClass.generate_kms_data_key").side_effect = Exception('testException')
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    data_copy = DATA.copy()
    data_copy["transactionId"] = "transaction50014"
    response = user_profile_util.create_binary_separate_file(
        transactionId=data_copy["transactionId"],
        splitImage=data_copy["splitImage"],
        userProfileKmsId=KMS_ID,
        binaryDataId=data_copy["binaryDataId"],
        sepNo=data_copy["sepNo"]
    )
    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "990065",
            "message": "予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：990065）"
        }
    }
    print(response)


# No7.分割バイナリデータ暗号化処理
def test_create_binary_separate_file_case7(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    data_copy = DATA.copy()
    data_copy["transactionId"] = "transaction50015"
    response = user_profile_util.create_binary_separate_file(
        transactionId=data_copy["transactionId"],
        splitImage=data_copy["splitImage"],
        userProfileKmsId=KMS_ID,
        binaryDataId=data_copy["binaryDataId"],
        sepNo=data_copy["sepNo"]
    )

    assert response == {
        "result": True,
        "fileSavePath": response["fileSavePath"],
        "uploadFile": response["uploadFile"],
        "kmsChiperDataKey": response["kmsChiperDataKey"],
        "chiperNonce": response["chiperNonce"]
    }
    print(response)


# No8.分割バイナリデータ格納準備処理が成功する
def test_create_binary_separate_file_case8(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    data_copy = DATA.copy()
    data_copy["transactionId"] = "transaction50016"
    response = user_profile_util.create_binary_separate_file(
        transactionId=data_copy["transactionId"],
        splitImage=data_copy["splitImage"],
        userProfileKmsId=KMS_ID,
        binaryDataId=data_copy["binaryDataId"],
        sepNo=data_copy["sepNo"]
    )

    assert response == {
        "result": True,
        "fileSavePath": response["fileSavePath"],
        "uploadFile": response["uploadFile"],
        "kmsChiperDataKey": response["kmsChiperDataKey"],
        "chiperNonce": response["chiperNonce"]
    }
    print(response)


# No9.終了処理
def test_create_binary_separate_file_case9(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    data_copy = DATA.copy()
    data_copy["transactionId"] = "transaction50017"
    response = user_profile_util.create_binary_separate_file(
        transactionId=data_copy["transactionId"],
        splitImage=data_copy["splitImage"],
        userProfileKmsId=KMS_ID,
        binaryDataId=data_copy["binaryDataId"],
        sepNo=data_copy["sepNo"]
    )

    assert response == {
        "result": True,
        "fileSavePath": response["fileSavePath"],
        "uploadFile": response["uploadFile"],
        "kmsChiperDataKey": response["kmsChiperDataKey"],
        "chiperNonce": response["chiperNonce"]
    }
    print(response)
