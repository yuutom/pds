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

PDS_USER_INFO = {
    "pdsUserId": "C9876543",
    "pdsUserDomainName": "pds-user-create",
    "s3ImageDataBucketName": "pds-c0000000-bucket"
}

FILE_SAVE_PATH = "transaction1/43bca47eb3fb4e1095445382df70dd76_0"

KMS_DATA_KEY = "AQIDAHg0DWq+QsT8YvjfjmEE5bxJ0MUeydByhsRVOXOZiR3ANAF+5iLK3uh/lyU6gOfisw2iAAAAfjB8BgkqhkiG9w0BBwagbzBtAgEAMGgGCSqGSIb3DQEHATAeBglghkgBZQMEAS4wEQQMoPPY2/r4GbVdiKk0AgEQgDuNCODYYp5o69PFzUD5N6gxvWOCxAt3uiQNCx49c8XiGjDzR+/EE3jM0Pi/dr5pM8FXFqKPIkUKF97MQw=="

CHIPER_NONCE = "rvvgNGS/EoRhr23CCTOkng=="

REQUEST = Request({"type": "http", "headers": {}, "method": "post", "path": "", "query_string": "", "root_path": "http://localhost", "scope": {"headers": {"host": "localhost"}}})

REQUEST_BODY = {}


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
# No1_1.PDSユーザ情報の値が設定されていない (空値)
@pytest.mark.asyncio
async def test_get_binary_decrypt_case1_1(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    with pytest.raises(PDSException) as e:
        await user_profile_util.get_binary_decrypt(
            pdsUserInfo=None,
            fileSavePath=FILE_SAVE_PATH,
            kmsDataKey=KMS_DATA_KEY,
            chiperNonce=CHIPER_NONCE,
            apiType="1",
            request=REQUEST,
            requestBody={}
        )

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "PDSユーザ情報")
    }
    print(e)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No1_2.PDSユーザ情報の値が設定されている
@pytest.mark.asyncio
async def test_get_binary_decrypt_case1_2(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    response = await user_profile_util.get_binary_decrypt(
        pdsUserInfo=PDS_USER_INFO,
        fileSavePath=FILE_SAVE_PATH,
        kmsDataKey=KMS_DATA_KEY,
        chiperNonce=CHIPER_NONCE,
        apiType="1",
        request=REQUEST,
        requestBody={}
    )

    assert response == {
        "result": True,
        "decryptionData": response["decryptionData"]
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No1_3.保存先パスの値が設定されていない (空値)
@pytest.mark.asyncio
async def test_get_binary_decrypt_case1_3(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    with pytest.raises(PDSException) as e:
        await user_profile_util.get_binary_decrypt(
            pdsUserInfo=PDS_USER_INFO,
            fileSavePath=None,
            kmsDataKey=KMS_DATA_KEY,
            chiperNonce=CHIPER_NONCE,
            apiType="1",
            request=REQUEST,
            requestBody={}
        )

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "保存先パス")
    }
    print(e)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No1_4.保存先パスの値が設定されている
@pytest.mark.asyncio
async def test_get_binary_decrypt_case1_4(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    response = await user_profile_util.get_binary_decrypt(
        pdsUserInfo=PDS_USER_INFO,
        fileSavePath=FILE_SAVE_PATH,
        kmsDataKey=KMS_DATA_KEY,
        chiperNonce=CHIPER_NONCE,
        apiType="1",
        request=REQUEST,
        requestBody={}
    )

    assert response == {
        "result": True,
        "decryptionData": response["decryptionData"]
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No1_5.KMSデータキーの値が設定されていない (空値)
@pytest.mark.asyncio
async def test_get_binary_decrypt_case1_5(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    with pytest.raises(PDSException) as e:
        await user_profile_util.get_binary_decrypt(
            pdsUserInfo=PDS_USER_INFO,
            fileSavePath=FILE_SAVE_PATH,
            kmsDataKey=None,
            chiperNonce=CHIPER_NONCE,
            apiType="1",
            request=REQUEST,
            requestBody={}
        )

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "KMSデータキー")
    }
    print(e)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No1_6.KMSデータキーの値が設定されている
@pytest.mark.asyncio
async def test_get_binary_decrypt_case1_6(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    response = await user_profile_util.get_binary_decrypt(
        pdsUserInfo=PDS_USER_INFO,
        fileSavePath=FILE_SAVE_PATH,
        kmsDataKey=KMS_DATA_KEY,
        chiperNonce=CHIPER_NONCE,
        apiType="1",
        request=REQUEST,
        requestBody={}
    )

    assert response == {
        "result": True,
        "decryptionData": response["decryptionData"]
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No1_7.暗号化ワンタイムパスワードの値が設定されていない (空値)
@pytest.mark.asyncio
async def test_get_binary_decrypt_case1_7(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    with pytest.raises(PDSException) as e:
        await user_profile_util.get_binary_decrypt(
            pdsUserInfo=PDS_USER_INFO,
            fileSavePath=FILE_SAVE_PATH,
            kmsDataKey=KMS_DATA_KEY,
            chiperNonce=None,
            apiType="1",
            request=REQUEST,
            requestBody={}
        )

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "暗号化ワンタイムパスワード")
    }
    print(e)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No1_8.暗号化ワンタイムパスワードの値が設定されている
@pytest.mark.asyncio
async def test_get_binary_decrypt_case1_8(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    response = await user_profile_util.get_binary_decrypt(
        pdsUserInfo=PDS_USER_INFO,
        fileSavePath=FILE_SAVE_PATH,
        kmsDataKey=KMS_DATA_KEY,
        chiperNonce=CHIPER_NONCE,
        apiType="1",
        request=REQUEST,
        requestBody={}
    )

    assert response == {
        "result": True,
        "decryptionData": response["decryptionData"]
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No1_9.API種別の値が設定されていない (空値)
@pytest.mark.asyncio
async def test_get_binary_decrypt_case1_9(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    with pytest.raises(PDSException) as e:
        await user_profile_util.get_binary_decrypt(
            pdsUserInfo=PDS_USER_INFO,
            fileSavePath=FILE_SAVE_PATH,
            kmsDataKey=KMS_DATA_KEY,
            chiperNonce=CHIPER_NONCE,
            apiType=None,
            request=REQUEST,
            requestBody={}
        )

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "API種別")
    }
    print(e)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No1_10.API種別の値が設定されている
@pytest.mark.asyncio
async def test_get_binary_decrypt_case1_10(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    response = await user_profile_util.get_binary_decrypt(
        pdsUserInfo=PDS_USER_INFO,
        fileSavePath=FILE_SAVE_PATH,
        kmsDataKey=KMS_DATA_KEY,
        chiperNonce=CHIPER_NONCE,
        apiType="1",
        request=REQUEST,
        requestBody={}
    )

    assert response == {
        "result": True,
        "decryptionData": response["decryptionData"]
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No1_11.リクエスト情報の値が設定されていない (空値)
@pytest.mark.asyncio
async def test_get_binary_decrypt_case1_11(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    with pytest.raises(PDSException) as e:
        await user_profile_util.get_binary_decrypt(
            pdsUserInfo=PDS_USER_INFO,
            fileSavePath=FILE_SAVE_PATH,
            kmsDataKey=KMS_DATA_KEY,
            chiperNonce=CHIPER_NONCE,
            apiType="1",
            request=None,
            requestBody={}
        )

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "リクエスト情報")
    }
    print(e)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No1_12.リクエスト情報の値が設定されている
@pytest.mark.asyncio
async def test_get_binary_decrypt_case1_12(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    response = await user_profile_util.get_binary_decrypt(
        pdsUserInfo=PDS_USER_INFO,
        fileSavePath=FILE_SAVE_PATH,
        kmsDataKey=KMS_DATA_KEY,
        chiperNonce=CHIPER_NONCE,
        apiType="1",
        request=REQUEST,
        requestBody={}
    )

    assert response == {
        "result": True,
        "decryptionData": response["decryptionData"]
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No1_13.リクエストボディの値が設定されていない (空値)
@pytest.mark.asyncio
async def test_get_binary_decrypt_case1_13(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    with pytest.raises(PDSException) as e:
        await user_profile_util.get_binary_decrypt(
            pdsUserInfo=PDS_USER_INFO,
            fileSavePath=FILE_SAVE_PATH,
            kmsDataKey=KMS_DATA_KEY,
            chiperNonce=CHIPER_NONCE,
            apiType="1",
            request=REQUEST,
            requestBody=None
        )

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "リクエストボディ")
    }
    print(e)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No1_14.リクエストボディの値が設定されている
@pytest.mark.asyncio
async def test_get_binary_decrypt_case1_14(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    response = await user_profile_util.get_binary_decrypt(
        pdsUserInfo=PDS_USER_INFO,
        fileSavePath=FILE_SAVE_PATH,
        kmsDataKey=KMS_DATA_KEY,
        chiperNonce=CHIPER_NONCE,
        apiType="1",
        request=REQUEST,
        requestBody={}
    )

    assert response == {
        "result": True,
        "decryptionData": response["decryptionData"]
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No2.S3からファイルの取得に失敗する
@pytest.mark.asyncio
async def test_get_binary_decrypt_case2(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    with pytest.raises(PDSException) as e:
        await user_profile_util.get_binary_decrypt(
            pdsUserInfo=PDS_USER_INFO,
            fileSavePath="aaa",
            kmsDataKey=KMS_DATA_KEY,
            chiperNonce=CHIPER_NONCE,
            apiType="1",
            request=REQUEST,
            requestBody={}
        )

    assert e.value.args[0] == {
        "errorCode": "990024",
        "message": '予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：990024）'
    }
    print(e)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No3.S3からファイルの取得に成功する
@pytest.mark.asyncio
async def test_get_binary_decrypt_case3(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    response = await user_profile_util.get_binary_decrypt(
        pdsUserInfo=PDS_USER_INFO,
        fileSavePath=FILE_SAVE_PATH,
        kmsDataKey=KMS_DATA_KEY,
        chiperNonce=CHIPER_NONCE,
        apiType="1",
        request=REQUEST,
        requestBody={}
    )

    assert response == {
        "result": True,
        "decryptionData": response["decryptionData"]
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No4.共通エラーチェック処理が成功（エラー情報有り）
@pytest.mark.asyncio
async def test_get_binary_decrypt_case4(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    with pytest.raises(PDSException) as e:
        await user_profile_util.get_binary_decrypt(
            pdsUserInfo=PDS_USER_INFO,
            fileSavePath="aaa",
            kmsDataKey=KMS_DATA_KEY,
            chiperNonce=CHIPER_NONCE,
            apiType="1",
            request=REQUEST,
            requestBody={}
        )

    assert e.value.args[0] == {
        "errorCode": "990024",
        "message": '予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：990024）'
    }
    print(e)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No5.KMSからデータ取得が失敗する
@pytest.mark.asyncio
async def test_get_binary_decrypt_case5(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    with pytest.raises(PDSException) as e:
        await user_profile_util.get_binary_decrypt(
            pdsUserInfo=PDS_USER_INFO,
            fileSavePath=FILE_SAVE_PATH,
            kmsDataKey="AAADAHg0DWq+QsT8YvjfjmEE5bxJ0MUeydByhsRVOXOZiR3ANAF+5iLK3uh/lyU6gOfisw2iAAAAfjB8BgkqhkiG9w0BBwagbzBtAgEAMGgGCSqGSIb3DQEHATAeBglghkgBZQMEAS4wEQQMoPPY2/r4GbVdiKk0AgEQgDuNCODYYp5o69PFzUD5N6gxvWOCxAt3uiQNCx49c8XiGjDzR+/EE3jM0Pi/dr5pM8FXFqKPIkUKF97MQw==",
            chiperNonce=CHIPER_NONCE,
            apiType="1",
            request=REQUEST,
            requestBody={}
        )

    assert e.value.args[0] == {
        "errorCode": "990066",
        "message": '予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：990066）'
    }
    print(e)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No6.KMSからデータ取得が成功する
@pytest.mark.asyncio
async def test_get_binary_decrypt_case6(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    response = await user_profile_util.get_binary_decrypt(
        pdsUserInfo=PDS_USER_INFO,
        fileSavePath=FILE_SAVE_PATH,
        kmsDataKey=KMS_DATA_KEY,
        chiperNonce=CHIPER_NONCE,
        apiType="1",
        request=REQUEST,
        requestBody={}
    )

    assert response == {
        "result": True,
        "decryptionData": response["decryptionData"]
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No7.共通エラーチェック処理が成功（エラー情報有り）
@pytest.mark.asyncio
async def test_get_binary_decrypt_case7(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    with pytest.raises(PDSException) as e:
        await user_profile_util.get_binary_decrypt(
            pdsUserInfo=PDS_USER_INFO,
            fileSavePath=FILE_SAVE_PATH,
            kmsDataKey="AAADAHg0DWq+QsT8YvjfjmEE5bxJ0MUeydByhsRVOXOZiR3ANAF+5iLK3uh/lyU6gOfisw2iAAAAfjB8BgkqhkiG9w0BBwagbzBtAgEAMGgGCSqGSIb3DQEHATAeBglghkgBZQMEAS4wEQQMoPPY2/r4GbVdiKk0AgEQgDuNCODYYp5o69PFzUD5N6gxvWOCxAt3uiQNCx49c8XiGjDzR+/EE3jM0Pi/dr5pM8FXFqKPIkUKF97MQw==",
            chiperNonce=CHIPER_NONCE,
            apiType="1",
            request=REQUEST,
            requestBody={}
        )

    assert e.value.args[0] == {
        "errorCode": "990066",
        "message": '予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：990066）'
    }
    print(e)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No8.「変数．バイナリデータ」を「変数．復号データキー」と「引数．暗号化ワンタイムパスワード」を使って復号化し、「変数．復号化データ」に格納する
@pytest.mark.asyncio
async def test_get_binary_decrypt_case8(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    response = await user_profile_util.get_binary_decrypt(
        pdsUserInfo=PDS_USER_INFO,
        fileSavePath=FILE_SAVE_PATH,
        kmsDataKey=KMS_DATA_KEY,
        chiperNonce=CHIPER_NONCE,
        apiType="1",
        request=REQUEST,
        requestBody={}
    )

    assert response == {
        "result": True,
        "decryptionData": response["decryptionData"]
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No9.個人バイナリ情報複合処理を並列で実行し、成功する（複数件）
@pytest.mark.asyncio
async def test_get_binary_decrypt_case9(mocker: MockerFixture, create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    response = await user_profile_util.get_binary_decrypt(
        pdsUserInfo=PDS_USER_INFO,
        fileSavePath=FILE_SAVE_PATH,
        kmsDataKey=KMS_DATA_KEY,
        chiperNonce=CHIPER_NONCE,
        apiType="1",
        request=REQUEST,
        requestBody={}
    )

    assert response == {
        "result": True,
        "decryptionData": response["decryptionData"]
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)
