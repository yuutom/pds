import pytest
import asyncio
from fastapi import Request
from pytest_mock.plugin import MockerFixture
import util.logUtil as logUtil
from exceptionClass.PDSException import PDSException
from const.messageConst import MessageConstClass
from const.systemConst import SystemConstClass
from util.userProfileUtil import UserProfileUtilClass
from util.commonUtil import CommonUtilClass
from const.sqlConst import SqlConstClass

KMS_ID = "fdb4c6aa-50b0-4ed1-bdad-32c21e0a0387"
BUCKET_NAME = "pds-c0000000-bucket"

DATA = {
    "transactionId": "transaction40000",
    "binaryDataId": "abcdefghijklmnopqrstuvwxyz000000",
    "sepNo": 1,
    "binarySeparateData": b"aiueo"
}


@pytest.fixture
def create_user_profile_util():
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    user_profile_util = UserProfileUtilClass(trace_logger)
    yield user_profile_util


@pytest.fixture
def create_pds_user_db_info():
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    common_util = CommonUtilClass(trace_logger)
    pds_user_db_info = common_util.get_secret_info("pds-c0000000-sm")
    yield pds_user_db_info


# 01.引数検証処理チェック処理
# No1_1.トランザクションIDの値が設定されていない (空値)
@pytest.mark.asyncio
async def test_insert_binary_separate_data_case1_1(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transactionId"] = ""
    data_copy["binaryDataId"] = "abcdefghijklmnopqrstuvwxyz000000"
    with pytest.raises(PDSException) as e:
        await user_profile_util.insert_binary_separate_data(
            transactionId=data_copy["transactionId"],
            binaryDataId=data_copy["binaryDataId"],
            sepNo=data_copy["sepNo"],
            binarySeparateData=data_copy["binarySeparateData"],
            userProfileKmsId=KMS_ID,
            bucketName=BUCKET_NAME,
            pdsUserDbInfo=pds_user_db_info
        )

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "トランザクションID")
    }
    print(e)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No1_2.トランザクションIDの値が設定されている
@pytest.mark.asyncio
async def test_insert_binary_separate_data_case1_2(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["binaryDataId"] = "abcdefghijklmnopqrstuvwxyz000001"
    response = await user_profile_util.insert_binary_separate_data(
        transactionId=data_copy["transactionId"],
        binaryDataId=data_copy["binaryDataId"],
        sepNo=data_copy["sepNo"],
        binarySeparateData=data_copy["binarySeparateData"],
        userProfileKmsId=KMS_ID,
        bucketName=BUCKET_NAME,
        pdsUserDbInfo=pds_user_db_info
    )

    assert response == {
        "result": True,
        "errorInfo": None
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No1_3.バイナリデータIDの値が設定されていない (空値)
@pytest.mark.asyncio
async def test_insert_binary_separate_data_case1_3(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["binaryDataId"] = ""
    with pytest.raises(PDSException) as e:
        await user_profile_util.insert_binary_separate_data(
            transactionId=data_copy["transactionId"],
            binaryDataId=data_copy["binaryDataId"],
            sepNo=data_copy["sepNo"],
            binarySeparateData=data_copy["binarySeparateData"],
            userProfileKmsId=KMS_ID,
            bucketName=BUCKET_NAME,
            pdsUserDbInfo=pds_user_db_info
        )

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "バイナリデータID")
    }
    print(e)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No1_4.バイナリデータIDの値が設定されている
@pytest.mark.asyncio
async def test_insert_binary_separate_data_case1_4(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["binaryDataId"] = "abcdefghijklmnopqrstuvwxyz000003"
    response = await user_profile_util.insert_binary_separate_data(
        transactionId=data_copy["transactionId"],
        binaryDataId=data_copy["binaryDataId"],
        sepNo=data_copy["sepNo"],
        binarySeparateData=data_copy["binarySeparateData"],
        userProfileKmsId=KMS_ID,
        bucketName=BUCKET_NAME,
        pdsUserDbInfo=pds_user_db_info
    )

    assert response == {
        "result": True,
        "errorInfo": None
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No1_5.セパレートNoの値が設定されていない (空値)
@pytest.mark.asyncio
async def test_insert_binary_separate_data_case1_5(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["binaryDataId"] = "abcdefghijklmnopqrstuvwxyz000004"
    data_copy["sepNo"] = None
    with pytest.raises(PDSException) as e:
        await user_profile_util.insert_binary_separate_data(
            transactionId=data_copy["transactionId"],
            binaryDataId=data_copy["binaryDataId"],
            sepNo=data_copy["sepNo"],
            binarySeparateData=data_copy["binarySeparateData"],
            userProfileKmsId=KMS_ID,
            bucketName=BUCKET_NAME,
            pdsUserDbInfo=pds_user_db_info
        )

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "セパレートNo")
    }
    print(e)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No1_6.セパレートNoの値が設定されている
@pytest.mark.asyncio
async def test_insert_binary_separate_data_case1_6(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["binaryDataId"] = "abcdefghijklmnopqrstuvwxyz000005"
    response = await user_profile_util.insert_binary_separate_data(
        transactionId=data_copy["transactionId"],
        binaryDataId=data_copy["binaryDataId"],
        sepNo=data_copy["sepNo"],
        binarySeparateData=data_copy["binarySeparateData"],
        userProfileKmsId=KMS_ID,
        bucketName=BUCKET_NAME,
        pdsUserDbInfo=pds_user_db_info
    )

    assert response == {
        "result": True,
        "errorInfo": None
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No1_7.分割バイナリデータの値が設定されていない (空値)
@pytest.mark.asyncio
async def test_insert_binary_separate_data_case1_7(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["binaryDataId"] = "abcdefghijklmnopqrstuvwxyz000006"
    data_copy["binarySeparateData"] = ""
    with pytest.raises(PDSException) as e:
        await user_profile_util.insert_binary_separate_data(
            transactionId=data_copy["transactionId"],
            binaryDataId=data_copy["binaryDataId"],
            sepNo=data_copy["sepNo"],
            binarySeparateData=data_copy["binarySeparateData"],
            userProfileKmsId=KMS_ID,
            bucketName=BUCKET_NAME,
            pdsUserDbInfo=pds_user_db_info
        )

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "分割バイナリデータ")
    }
    print(e)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No1_8.分割バイナリデータの値が設定されている
@pytest.mark.asyncio
async def test_insert_binary_separate_data_case1_8(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["binaryDataId"] = "abcdefghijklmnopqrstuvwxyz000007"
    response = await user_profile_util.insert_binary_separate_data(
        transactionId=data_copy["transactionId"],
        binaryDataId=data_copy["binaryDataId"],
        sepNo=data_copy["sepNo"],
        binarySeparateData=data_copy["binarySeparateData"],
        userProfileKmsId=KMS_ID,
        bucketName=BUCKET_NAME,
        pdsUserDbInfo=pds_user_db_info
    )

    assert response == {
        "result": True,
        "errorInfo": None
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No1_9.個人情報暗号・復号化用KMSIDの値が設定されていない (空値)
@pytest.mark.asyncio
async def test_insert_binary_separate_data_case1_9(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["binaryDataId"] = "abcdefghijklmnopqrstuvwxyz000008"
    with pytest.raises(PDSException) as e:
        await user_profile_util.insert_binary_separate_data(
            transactionId=data_copy["transactionId"],
            binaryDataId=data_copy["binaryDataId"],
            sepNo=data_copy["sepNo"],
            binarySeparateData=data_copy["binarySeparateData"],
            userProfileKmsId="",
            bucketName=BUCKET_NAME,
            pdsUserDbInfo=pds_user_db_info
        )

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "個人情報暗号・復号化用KMSID")
    }
    print(e)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No1_10.個人情報暗号・復号化用KMSIDの値が設定されている
@pytest.mark.asyncio
async def test_insert_binary_separate_data_case1_10(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["binaryDataId"] = "abcdefghijklmnopqrstuvwxyz000009"
    response = await user_profile_util.insert_binary_separate_data(
        transactionId=data_copy["transactionId"],
        binaryDataId=data_copy["binaryDataId"],
        sepNo=data_copy["sepNo"],
        binarySeparateData=data_copy["binarySeparateData"],
        userProfileKmsId=KMS_ID,
        bucketName=BUCKET_NAME,
        pdsUserDbInfo=pds_user_db_info
    )

    assert response == {
        "result": True,
        "errorInfo": None
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No1_11.バケット名の値が設定されていない (空値)
@pytest.mark.asyncio
async def test_insert_binary_separate_data_case1_11(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["binaryDataId"] = "abcdefghijklmnopqrstuvwxyz000010"
    with pytest.raises(PDSException) as e:
        await user_profile_util.insert_binary_separate_data(
            transactionId=data_copy["transactionId"],
            binaryDataId=data_copy["binaryDataId"],
            sepNo=data_copy["sepNo"],
            binarySeparateData=data_copy["binarySeparateData"],
            userProfileKmsId=KMS_ID,
            bucketName="",
            pdsUserDbInfo=pds_user_db_info
        )

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "バケット名")
    }
    print(e)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No1_12.バケット名が設定されている
@pytest.mark.asyncio
async def test_insert_binary_separate_data_case1_12(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["binaryDataId"] = "abcdefghijklmnopqrstuvwxyz000011"
    response = await user_profile_util.insert_binary_separate_data(
        transactionId=data_copy["transactionId"],
        binaryDataId=data_copy["binaryDataId"],
        sepNo=data_copy["sepNo"],
        binarySeparateData=data_copy["binarySeparateData"],
        userProfileKmsId=KMS_ID,
        bucketName=BUCKET_NAME,
        pdsUserDbInfo=pds_user_db_info
    )

    assert response == {
        "result": True,
        "errorInfo": None
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No1_13.PDSユーザDB接続情報の値が設定されていない (空値)
@pytest.mark.asyncio
async def test_insert_binary_separate_data_case1_13(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    data_copy = DATA.copy()
    data_copy["binaryDataId"] = "abcdefghijklmnopqrstuvwxyz000012"
    with pytest.raises(PDSException) as e:
        await user_profile_util.insert_binary_separate_data(
            transactionId=data_copy["transactionId"],
            binaryDataId=data_copy["binaryDataId"],
            sepNo=data_copy["sepNo"],
            binarySeparateData=data_copy["binarySeparateData"],
            userProfileKmsId=KMS_ID,
            bucketName=BUCKET_NAME,
            pdsUserDbInfo=None
        )

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "PDSユーザDB接続情報")
    }
    print(e)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No1_14.PDSユーザDB接続情報の値が設定されている
@pytest.mark.asyncio
async def test_insert_binary_separate_data_case1_14(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["binaryDataId"] = "abcdefghijklmnopqrstuvwxyz000013"
    response = await user_profile_util.insert_binary_separate_data(
        transactionId=data_copy["transactionId"],
        binaryDataId=data_copy["binaryDataId"],
        sepNo=data_copy["sepNo"],
        binarySeparateData=data_copy["binarySeparateData"],
        userProfileKmsId=KMS_ID,
        bucketName=BUCKET_NAME,
        pdsUserDbInfo=pds_user_db_info
    )

    assert response == {
        "result": True,
        "errorInfo": None
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No2.「分割バイナリファイル情報作成処理」が失敗する
@pytest.mark.asyncio
async def test_insert_binary_separate_data_case2(mocker: MockerFixture, create_user_profile_util):
    # Exception
    mocker.patch("util.kmsUtil.KmsUtilClass.generate_kms_data_key").side_effect = Exception('testException')
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["binaryDataId"] = "abcdefghijklmnopqrstuvwxyz000014"
    response = await user_profile_util.insert_binary_separate_data(
        transactionId=data_copy["transactionId"],
        binaryDataId=data_copy["binaryDataId"],
        sepNo=data_copy["sepNo"],
        binarySeparateData=data_copy["binarySeparateData"],
        userProfileKmsId=KMS_ID,
        bucketName=BUCKET_NAME,
        pdsUserDbInfo=pds_user_db_info
    )
    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "990065",
            "message": "予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：990065）"
        }
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No3.「分割バイナリファイル情報作成処理」が成功する
@pytest.mark.asyncio
async def test_insert_binary_separate_data_case3(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["binaryDataId"] = "abcdefghijklmnopqrstuvwxyz000015"
    response = await user_profile_util.insert_binary_separate_data(
        transactionId=data_copy["transactionId"],
        binaryDataId=data_copy["binaryDataId"],
        sepNo=data_copy["sepNo"],
        binarySeparateData=data_copy["binarySeparateData"],
        userProfileKmsId=KMS_ID,
        bucketName=BUCKET_NAME,
        pdsUserDbInfo=pds_user_db_info
    )

    assert response == {
        "result": True,
        "errorInfo": None
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No4.「変数．分割バイナリファイル情報作成処理実行結果．エラー情報」がNullの場合、「05.PDSユーザDB接続準備処理」に遷移する
@pytest.mark.asyncio
async def test_insert_binary_separate_data_case4(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["binaryDataId"] = "abcdefghijklmnopqrstuvwxyz000016"
    response = await user_profile_util.insert_binary_separate_data(
        transactionId=data_copy["transactionId"],
        binaryDataId=data_copy["binaryDataId"],
        sepNo=data_copy["sepNo"],
        binarySeparateData=data_copy["binarySeparateData"],
        userProfileKmsId=KMS_ID,
        bucketName=BUCKET_NAME,
        pdsUserDbInfo=pds_user_db_info
    )

    assert response == {
        "result": True,
        "errorInfo": None
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No5.「変数．分割バイナリファイル情報作成処理実行結果．エラー情報」がNull以外の場合、「04.分割バイナリファイル情報作成エラー処理」に遷移する
@pytest.mark.asyncio
async def test_insert_binary_separate_data_case5(mocker: MockerFixture, create_user_profile_util):
    # Exception
    mocker.patch("util.kmsUtil.KmsUtilClass.generate_kms_data_key").side_effect = Exception('testException')
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["binaryDataId"] = "abcdefghijklmnopqrstuvwxyz000017"
    response = await user_profile_util.insert_binary_separate_data(
        transactionId=data_copy["transactionId"],
        binaryDataId=data_copy["binaryDataId"],
        sepNo=data_copy["sepNo"],
        binarySeparateData=data_copy["binarySeparateData"],
        userProfileKmsId=KMS_ID,
        bucketName=BUCKET_NAME,
        pdsUserDbInfo=pds_user_db_info
    )
    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "990065",
            "message": "予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：990065）"
        }
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No6.レスポンス情報を作成し、返却する
@pytest.mark.asyncio
async def test_insert_binary_separate_data_case6(mocker: MockerFixture, create_user_profile_util):
    # Exception
    mocker.patch("util.kmsUtil.KmsUtilClass.generate_kms_data_key").side_effect = Exception('testException')
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["binaryDataId"] = "abcdefghijklmnopqrstuvwxyz000018"
    response = await user_profile_util.insert_binary_separate_data(
        transactionId=data_copy["transactionId"],
        binaryDataId=data_copy["binaryDataId"],
        sepNo=data_copy["sepNo"],
        binarySeparateData=data_copy["binarySeparateData"],
        userProfileKmsId=KMS_ID,
        bucketName=BUCKET_NAME,
        pdsUserDbInfo=pds_user_db_info
    )
    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "990065",
            "message": "予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：990065）"
        }
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No7.PDSユーザDB接続に失敗する。設定値を異常な値に変更する
@pytest.mark.asyncio
async def test_insert_binary_separate_data_case7(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["binaryDataId"] = "abcdefghijklmnopqrstuvwxyz000019"
    pds_user_db_info["host"] = "test-db"
    with pytest.raises(PDSException) as e:
        await user_profile_util.insert_binary_separate_data(
            transactionId=data_copy["transactionId"],
            binaryDataId=data_copy["binaryDataId"],
            sepNo=data_copy["sepNo"],
            binarySeparateData=data_copy["binarySeparateData"],
            userProfileKmsId=KMS_ID,
            bucketName=BUCKET_NAME,
            pdsUserDbInfo=pds_user_db_info
        )

    assert e.value.args[0] == {
        "errorCode": "999999",
        "message": "予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：999999）"
    }
    print(e)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No8.PDSユーザDB接続に成功する。
@pytest.mark.asyncio
async def test_insert_binary_separate_data_case8(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["binaryDataId"] = "abcdefghijklmnopqrstuvwxyz000020"
    response = await user_profile_util.insert_binary_separate_data(
        transactionId=data_copy["transactionId"],
        binaryDataId=data_copy["binaryDataId"],
        sepNo=data_copy["sepNo"],
        binarySeparateData=data_copy["binarySeparateData"],
        userProfileKmsId=KMS_ID,
        bucketName=BUCKET_NAME,
        pdsUserDbInfo=pds_user_db_info
    )

    assert response == {
        "result": True,
        "errorInfo": None
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No9.個人情報バイナリ分割データ登録処理が失敗する（posgresqlエラー）
@pytest.mark.asyncio
async def test_insert_binary_separate_data_case9(mocker: MockerFixture, create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["binaryDataId"] = "abcdefghijklmnopqrstuvwxyz000021"
    mocker.patch.object(SqlConstClass, "USER_PROFILE_BINARY_SEPARATE_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    response = await user_profile_util.insert_binary_separate_data(
        transactionId=data_copy["transactionId"],
        binaryDataId=data_copy["binaryDataId"],
        sepNo=data_copy["sepNo"],
        binarySeparateData=data_copy["binarySeparateData"],
        userProfileKmsId=KMS_ID,
        bucketName=BUCKET_NAME,
        pdsUserDbInfo=pds_user_db_info
    )

    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "991028",
            "message": "予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：991028）"
        }
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No10.個人情報バイナリ分割データ登録処理が成功する
@pytest.mark.asyncio
async def test_insert_binary_separate_data_case10(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["binaryDataId"] = "abcdefghijklmnopqrstuvwxyz000022"
    response = await user_profile_util.insert_binary_separate_data(
        transactionId=data_copy["transactionId"],
        binaryDataId=data_copy["binaryDataId"],
        sepNo=data_copy["sepNo"],
        binarySeparateData=data_copy["binarySeparateData"],
        userProfileKmsId=KMS_ID,
        bucketName=BUCKET_NAME,
        pdsUserDbInfo=pds_user_db_info
    )

    assert response == {
        "result": True,
        "errorInfo": None
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No11.「変数．エラー情報」がNullの場合、「11.トランザクションコミット処理」に遷移する
@pytest.mark.asyncio
async def test_insert_binary_separate_data_case11(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["binaryDataId"] = "abcdefghijklmnopqrstuvwxyz000023"
    response = await user_profile_util.insert_binary_separate_data(
        transactionId=data_copy["transactionId"],
        binaryDataId=data_copy["binaryDataId"],
        sepNo=data_copy["sepNo"],
        binarySeparateData=data_copy["binarySeparateData"],
        userProfileKmsId=KMS_ID,
        bucketName=BUCKET_NAME,
        pdsUserDbInfo=pds_user_db_info
    )

    assert response == {
        "result": True,
        "errorInfo": None
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No12.「変数．エラー情報」がNull以外の場合、「09.トランザクションロールバック処理」に遷移する
@pytest.mark.asyncio
async def test_insert_binary_separate_data_case12(mocker: MockerFixture, create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["binaryDataId"] = "abcdefghijklmnopqrstuvwxyz000024"
    mocker.patch.object(SqlConstClass, "USER_PROFILE_BINARY_SEPARATE_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    response = await user_profile_util.insert_binary_separate_data(
        transactionId=data_copy["transactionId"],
        binaryDataId=data_copy["binaryDataId"],
        sepNo=data_copy["sepNo"],
        binarySeparateData=data_copy["binarySeparateData"],
        userProfileKmsId=KMS_ID,
        bucketName=BUCKET_NAME,
        pdsUserDbInfo=pds_user_db_info
    )

    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "991028",
            "message": "予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：991028）"
        }
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No13.「個人情報バイナリデータ登録トランザクション」をロールバックする
@pytest.mark.asyncio
async def test_insert_binary_separate_data_case13(mocker: MockerFixture, create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["binaryDataId"] = "abcdefghijklmnopqrstuvwxyz000025"
    mocker.patch.object(SqlConstClass, "USER_PROFILE_BINARY_SEPARATE_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    response = await user_profile_util.insert_binary_separate_data(
        transactionId=data_copy["transactionId"],
        binaryDataId=data_copy["binaryDataId"],
        sepNo=data_copy["sepNo"],
        binarySeparateData=data_copy["binarySeparateData"],
        userProfileKmsId=KMS_ID,
        bucketName=BUCKET_NAME,
        pdsUserDbInfo=pds_user_db_info
    )

    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "991028",
            "message": "予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：991028）"
        }
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No14.レスポンス情報を作成し、返却する
@pytest.mark.asyncio
async def test_insert_binary_separate_data_case14(mocker: MockerFixture, create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["binaryDataId"] = "abcdefghijklmnopqrstuvwxyz000026"
    mocker.patch.object(SqlConstClass, "USER_PROFILE_BINARY_SEPARATE_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    response = await user_profile_util.insert_binary_separate_data(
        transactionId=data_copy["transactionId"],
        binaryDataId=data_copy["binaryDataId"],
        sepNo=data_copy["sepNo"],
        binarySeparateData=data_copy["binarySeparateData"],
        userProfileKmsId=KMS_ID,
        bucketName=BUCKET_NAME,
        pdsUserDbInfo=pds_user_db_info
    )

    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "991028",
            "message": "予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：991028）"
        }
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No15.コミットが成功する
@pytest.mark.asyncio
async def test_insert_binary_separate_data_case15(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["binaryDataId"] = "abcdefghijklmnopqrstuvwxyz000027"
    response = await user_profile_util.insert_binary_separate_data(
        transactionId=data_copy["transactionId"],
        binaryDataId=data_copy["binaryDataId"],
        sepNo=data_copy["sepNo"],
        binarySeparateData=data_copy["binarySeparateData"],
        userProfileKmsId=KMS_ID,
        bucketName=BUCKET_NAME,
        pdsUserDbInfo=pds_user_db_info
    )

    assert response == {
        "result": True,
        "errorInfo": None
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No16.分割バイナリデータ保存処理に失敗する（5回）
@pytest.mark.asyncio
async def test_insert_binary_separate_data_case16(mocker: MockerFixture, create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["binaryDataId"] = "abcdefghijklmnopqrstuvwxyz000028"
    # Exception
    mocker.patch("util.s3AioUtil.s3AioUtilClass.async_put_file").return_value = False
    response = await user_profile_util.insert_binary_separate_data(
        transactionId=data_copy["transactionId"],
        binaryDataId=data_copy["binaryDataId"],
        sepNo=data_copy["sepNo"],
        binarySeparateData=data_copy["binarySeparateData"],
        userProfileKmsId=KMS_ID,
        bucketName=BUCKET_NAME,
        pdsUserDbInfo=pds_user_db_info
    )

    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "990021",
            "message": "予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：990021）"
        }
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No17.分割バイナリデータ保存処理に成功する（1回目）
@pytest.mark.asyncio
async def test_insert_binary_separate_data_case17(mocker: MockerFixture, create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["binaryDataId"] = "abcdefghijklmnopqrstuvwxyz000029"
    response = await user_profile_util.insert_binary_separate_data(
        transactionId=data_copy["transactionId"],
        binaryDataId=data_copy["binaryDataId"],
        sepNo=data_copy["sepNo"],
        binarySeparateData=data_copy["binarySeparateData"],
        userProfileKmsId=KMS_ID,
        bucketName=BUCKET_NAME,
        pdsUserDbInfo=pds_user_db_info
    )

    assert response == {
        "result": True,
        "errorInfo": None
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No18.分割バイナリデータ保存処理に成功する（5回目）
@pytest.mark.asyncio
async def test_insert_binary_separate_data_case18(mocker: MockerFixture, create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["binaryDataId"] = "abcdefghijklmnopqrstuvwxyz000030"
    mocker.patch("util.s3AioUtil.s3AioUtilClass.async_put_file").side_effect = [False, False, False, False, True]
    response = await user_profile_util.insert_binary_separate_data(
        transactionId=data_copy["transactionId"],
        binaryDataId=data_copy["binaryDataId"],
        sepNo=data_copy["sepNo"],
        binarySeparateData=data_copy["binarySeparateData"],
        userProfileKmsId=KMS_ID,
        bucketName=BUCKET_NAME,
        pdsUserDbInfo=pds_user_db_info
    )

    assert response == {
        "result": True,
        "errorInfo": None
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No19.「変数．エラー情報」がNullの場合、「15.終了処理」に遷移する
@pytest.mark.asyncio
async def test_insert_binary_separate_data_case19(mocker: MockerFixture, create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["binaryDataId"] = "abcdefghijklmnopqrstuvwxyz000031"
    response = await user_profile_util.insert_binary_separate_data(
        transactionId=data_copy["transactionId"],
        binaryDataId=data_copy["binaryDataId"],
        sepNo=data_copy["sepNo"],
        binarySeparateData=data_copy["binarySeparateData"],
        userProfileKmsId=KMS_ID,
        bucketName=BUCKET_NAME,
        pdsUserDbInfo=pds_user_db_info
    )

    assert response == {
        "result": True,
        "errorInfo": None
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No20.「変数．エラー情報」がNull以外の場合、「14.分割バイナリデータ保存エラー処理」に遷移する
@pytest.mark.asyncio
async def test_insert_binary_separate_data_case20(mocker: MockerFixture, create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["binaryDataId"] = "abcdefghijklmnopqrstuvwxyz000032"
    # Exception
    mocker.patch("util.s3AioUtil.s3AioUtilClass.async_put_file").return_value = False
    response = await user_profile_util.insert_binary_separate_data(
        transactionId=data_copy["transactionId"],
        binaryDataId=data_copy["binaryDataId"],
        sepNo=data_copy["sepNo"],
        binarySeparateData=data_copy["binarySeparateData"],
        userProfileKmsId=KMS_ID,
        bucketName=BUCKET_NAME,
        pdsUserDbInfo=pds_user_db_info
    )

    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "990021",
            "message": "予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：990021）"
        }
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No21.「個人情報バイナリデータ登録トランザクション」をロールバックする
@pytest.mark.asyncio
async def test_insert_binary_separate_data_case21(mocker: MockerFixture, create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["binaryDataId"] = "abcdefghijklmnopqrstuvwxyz000033"
    # Exception
    mocker.patch("util.s3AioUtil.s3AioUtilClass.async_put_file").return_value = False
    response = await user_profile_util.insert_binary_separate_data(
        transactionId=data_copy["transactionId"],
        binaryDataId=data_copy["binaryDataId"],
        sepNo=data_copy["sepNo"],
        binarySeparateData=data_copy["binarySeparateData"],
        userProfileKmsId=KMS_ID,
        bucketName=BUCKET_NAME,
        pdsUserDbInfo=pds_user_db_info
    )

    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "990021",
            "message": "予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：990021）"
        }
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No22.レスポンス情報を作成し、返却する
@pytest.mark.asyncio
async def test_insert_binary_separate_data_case22(mocker: MockerFixture, create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["binaryDataId"] = "abcdefghijklmnopqrstuvwxyz000034"
    response = await user_profile_util.insert_binary_separate_data(
        transactionId=data_copy["transactionId"],
        binaryDataId=data_copy["binaryDataId"],
        sepNo=data_copy["sepNo"],
        binarySeparateData=data_copy["binarySeparateData"],
        userProfileKmsId=KMS_ID,
        bucketName=BUCKET_NAME,
        pdsUserDbInfo=pds_user_db_info
    )

    assert response == {
        "result": True,
        "errorInfo": None
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)
