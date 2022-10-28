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

FILE_SAVE_PATH_LIST = [
    "transaction1/43bca47eb3fb4e1095445382df70dd76_0",
    "transaction1/43bca47eb3fb4e1095445382df70dd76_1"
]

KMS_DATA_KEY_LIST = [
    "AQIDAHg0DWq+QsT8YvjfjmEE5bxJ0MUeydByhsRVOXOZiR3ANAF+5iLK3uh/lyU6gOfisw2iAAAAfjB8BgkqhkiG9w0BBwagbzBtAgEAMGgGCSqGSIb3DQEHATAeBglghkgBZQMEAS4wEQQMoPPY2/r4GbVdiKk0AgEQgDuNCODYYp5o69PFzUD5N6gxvWOCxAt3uiQNCx49c8XiGjDzR+/EE3jM0Pi/dr5pM8FXFqKPIkUKF97MQw==",
    "AQIDAHg0DWq+QsT8YvjfjmEE5bxJ0MUeydByhsRVOXOZiR3ANAHX1fo7tFw81KfVqiSA4rXsAAAAfjB8BgkqhkiG9w0BBwagbzBtAgEAMGgGCSqGSIb3DQEHATAeBglghkgBZQMEAS4wEQQMZ0riNg8VIkO5vzoRAgEQgDtXXEyHjmzQpnJXjxrhx8BjaXDK0jnZrj3laE7d7UAVbWm30TiyTSCj7ylCYUtKUiWx0TpYJ7qwyXDIPg=="
]

CHIPER_NONCE_LIST = [
    "rvvgNGS/EoRhr23CCTOkng==",
    "lShWDyHR8QgpLPC5aPSZqw=="
]

REQUEST = Request({"type": "http", "headers": {}, "method": "post", "path": "", "query_string": "", "root_path": "http://localhost", "scope": {"headers": {"host": "localhost"}}})


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
async def test_get_binary_data_case1_1(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    with pytest.raises(PDSException) as e:
        await user_profile_util.get_binary_data(
            pdsUserInfo=None,
            fileSavePathList=FILE_SAVE_PATH_LIST,
            kmsDataKeyList=KMS_DATA_KEY_LIST,
            chiperNonceList=CHIPER_NONCE_LIST,
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
async def test_get_binary_data_case1_2(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    response = await user_profile_util.get_binary_data(
        pdsUserInfo=PDS_USER_INFO,
        fileSavePathList=FILE_SAVE_PATH_LIST,
        kmsDataKeyList=KMS_DATA_KEY_LIST,
        chiperNonceList=CHIPER_NONCE_LIST,
        apiType="1",
        request=REQUEST,
        requestBody={}
    )

    assert response == {
        "result": True,
        "binaryData": response["binaryData"]
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No1_3.保存先パスリストの値が設定されていない (空値)
@pytest.mark.asyncio
async def test_get_binary_data_case1_3(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    with pytest.raises(PDSException) as e:
        await user_profile_util.get_binary_data(
            pdsUserInfo=PDS_USER_INFO,
            fileSavePathList=None,
            kmsDataKeyList=KMS_DATA_KEY_LIST,
            chiperNonceList=CHIPER_NONCE_LIST,
            apiType="1",
            request=REQUEST,
            requestBody={}
        )

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "保存先パスリスト")
    }
    print(e)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No1_4.保存先パスリストの値が設定されている
@pytest.mark.asyncio
async def test_get_binary_data_case1_4(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    response = await user_profile_util.get_binary_data(
        pdsUserInfo=PDS_USER_INFO,
        fileSavePathList=FILE_SAVE_PATH_LIST,
        kmsDataKeyList=KMS_DATA_KEY_LIST,
        chiperNonceList=CHIPER_NONCE_LIST,
        apiType="1",
        request=REQUEST,
        requestBody={}
    )

    assert response == {
        "result": True,
        "binaryData": response["binaryData"]
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No1_5.KMSデータキーリストの値が設定されていない (空値)
@pytest.mark.asyncio
async def test_get_binary_data_case1_5(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    with pytest.raises(PDSException) as e:
        await user_profile_util.get_binary_data(
            pdsUserInfo=PDS_USER_INFO,
            fileSavePathList=FILE_SAVE_PATH_LIST,
            kmsDataKeyList=None,
            chiperNonceList=CHIPER_NONCE_LIST,
            apiType="1",
            request=REQUEST,
            requestBody={}
        )

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "KMSデータキーリスト")
    }
    print(e)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No1_6.KMSデータキーリストの値が設定されている
@pytest.mark.asyncio
async def test_get_binary_data_case1_6(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    response = await user_profile_util.get_binary_data(
        pdsUserInfo=PDS_USER_INFO,
        fileSavePathList=FILE_SAVE_PATH_LIST,
        kmsDataKeyList=KMS_DATA_KEY_LIST,
        chiperNonceList=CHIPER_NONCE_LIST,
        apiType="1",
        request=REQUEST,
        requestBody={}
    )

    assert response == {
        "result": True,
        "binaryData": response["binaryData"]
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No1_7.暗号化ワンタイムパスワードリストの値が設定されていない (空値)
@pytest.mark.asyncio
async def test_get_binary_data_case1_7(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    with pytest.raises(PDSException) as e:
        await user_profile_util.get_binary_data(
            pdsUserInfo=PDS_USER_INFO,
            fileSavePathList=FILE_SAVE_PATH_LIST,
            kmsDataKeyList=KMS_DATA_KEY_LIST,
            chiperNonceList=None,
            apiType="1",
            request=REQUEST,
            requestBody={}
        )

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "暗号化ワンタイムパスワードリスト")
    }
    print(e)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No1_8.暗号化ワンタイムパスワードリストの値が設定されている
@pytest.mark.asyncio
async def test_get_binary_data_case1_8(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    response = await user_profile_util.get_binary_data(
        pdsUserInfo=PDS_USER_INFO,
        fileSavePathList=FILE_SAVE_PATH_LIST,
        kmsDataKeyList=KMS_DATA_KEY_LIST,
        chiperNonceList=CHIPER_NONCE_LIST,
        apiType="1",
        request=REQUEST,
        requestBody={}
    )

    assert response == {
        "result": True,
        "binaryData": response["binaryData"]
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No1_9.API種別の値が設定されていない (空値)
@pytest.mark.asyncio
async def test_get_binary_data_case1_9(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    with pytest.raises(PDSException) as e:
        await user_profile_util.get_binary_data(
            pdsUserInfo=PDS_USER_INFO,
            fileSavePathList=FILE_SAVE_PATH_LIST,
            kmsDataKeyList=KMS_DATA_KEY_LIST,
            chiperNonceList=CHIPER_NONCE_LIST,
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
async def test_get_binary_data_case1_10(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    response = await user_profile_util.get_binary_data(
        pdsUserInfo=PDS_USER_INFO,
        fileSavePathList=FILE_SAVE_PATH_LIST,
        kmsDataKeyList=KMS_DATA_KEY_LIST,
        chiperNonceList=CHIPER_NONCE_LIST,
        apiType="1",
        request=REQUEST,
        requestBody={}
    )

    assert response == {
        "result": True,
        "binaryData": response["binaryData"]
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No1_11.リクエスト情報の値が設定されていない (空値)
@pytest.mark.asyncio
async def test_get_binary_data_case1_11(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    with pytest.raises(PDSException) as e:
        await user_profile_util.get_binary_data(
            pdsUserInfo=PDS_USER_INFO,
            fileSavePathList=FILE_SAVE_PATH_LIST,
            kmsDataKeyList=KMS_DATA_KEY_LIST,
            chiperNonceList=CHIPER_NONCE_LIST,
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
async def test_get_binary_data_case1_12(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    response = await user_profile_util.get_binary_data(
        pdsUserInfo=PDS_USER_INFO,
        fileSavePathList=FILE_SAVE_PATH_LIST,
        kmsDataKeyList=KMS_DATA_KEY_LIST,
        chiperNonceList=CHIPER_NONCE_LIST,
        apiType="1",
        request=REQUEST,
        requestBody={}
    )

    assert response == {
        "result": True,
        "binaryData": response["binaryData"]
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No1_13.リクエストボディの値が設定されていない (空値)
@pytest.mark.asyncio
async def test_get_binary_data_case1_13(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    with pytest.raises(PDSException) as e:
        await user_profile_util.get_binary_data(
            pdsUserInfo=PDS_USER_INFO,
            fileSavePathList=FILE_SAVE_PATH_LIST,
            kmsDataKeyList=KMS_DATA_KEY_LIST,
            chiperNonceList=CHIPER_NONCE_LIST,
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
async def test_get_binary_data_case1_14(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    response = await user_profile_util.get_binary_data(
        pdsUserInfo=PDS_USER_INFO,
        fileSavePathList=FILE_SAVE_PATH_LIST,
        kmsDataKeyList=KMS_DATA_KEY_LIST,
        chiperNonceList=CHIPER_NONCE_LIST,
        apiType="1",
        request=REQUEST,
        requestBody={}
    )

    assert response == {
        "result": True,
        "binaryData": response["binaryData"]
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No2.「変数．個人バイナリ情報復号処理リスト」を初期化する
@pytest.mark.asyncio
async def test_get_binary_data_case2(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    response = await user_profile_util.get_binary_data(
        pdsUserInfo=PDS_USER_INFO,
        fileSavePathList=FILE_SAVE_PATH_LIST,
        kmsDataKeyList=KMS_DATA_KEY_LIST,
        chiperNonceList=CHIPER_NONCE_LIST,
        apiType="1",
        request=REQUEST,
        requestBody={}
    )

    assert response == {
        "result": True,
        "binaryData": response["binaryData"]
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No3.「引数．保存先パスリスト」の要素数が0の場合
@pytest.mark.asyncio
async def test_get_binary_data_case3(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    response = await user_profile_util.get_binary_data(
        pdsUserInfo=PDS_USER_INFO,
        fileSavePathList=[],
        kmsDataKeyList=KMS_DATA_KEY_LIST,
        chiperNonceList=CHIPER_NONCE_LIST,
        apiType="1",
        request=REQUEST,
        requestBody={}
    )

    assert response == {
        "result": True,
        "binaryData": response["binaryData"]
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No4.「引数．保存先パスリスト」の要素数が1以上の場合
@pytest.mark.asyncio
async def test_get_binary_data_case4(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    response = await user_profile_util.get_binary_data(
        pdsUserInfo=PDS_USER_INFO,
        fileSavePathList=FILE_SAVE_PATH_LIST,
        kmsDataKeyList=KMS_DATA_KEY_LIST,
        chiperNonceList=CHIPER_NONCE_LIST,
        apiType="1",
        request=REQUEST,
        requestBody={}
    )

    assert response == {
        "result": True,
        "binaryData": response["binaryData"]
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No5.個人バイナリ情報復号処理リスト作成処理が成功する
@pytest.mark.asyncio
async def test_get_binary_data_case5(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    response = await user_profile_util.get_binary_data(
        pdsUserInfo=PDS_USER_INFO,
        fileSavePathList=FILE_SAVE_PATH_LIST,
        kmsDataKeyList=KMS_DATA_KEY_LIST,
        chiperNonceList=CHIPER_NONCE_LIST,
        apiType="1",
        request=REQUEST,
        requestBody={}
    )

    assert response == {
        "result": True,
        "binaryData": response["binaryData"]
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No6.個人バイナリ情報複合処理を並列で実行し、失敗する
@pytest.mark.asyncio
async def test_get_binary_data_case6(mocker: MockerFixture, create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    mocker.patch("util.kmsUtil.KmsUtilClass.decrypt_kms_data_key").side_effect = Exception("test-Exception")
    with pytest.raises(PDSException) as e:
        await user_profile_util.get_binary_data(
            pdsUserInfo=PDS_USER_INFO,
            fileSavePathList=FILE_SAVE_PATH_LIST,
            kmsDataKeyList=KMS_DATA_KEY_LIST,
            chiperNonceList=CHIPER_NONCE_LIST,
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


# No7.個人バイナリ情報複合処理を並列で実行し、成功する（1件）
@pytest.mark.asyncio
async def test_get_binary_data_case7(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    response = await user_profile_util.get_binary_data(
        pdsUserInfo=PDS_USER_INFO,
        fileSavePathList=["transaction1/43bca47eb3fb4e1095445382df70dd76_0"],
        kmsDataKeyList=KMS_DATA_KEY_LIST,
        chiperNonceList=CHIPER_NONCE_LIST,
        apiType="1",
        request=REQUEST,
        requestBody={}
    )

    assert response == {
        "result": True,
        "binaryData": response["binaryData"]
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No8.個人バイナリ情報複合処理を並列で実行し、成功する（複数件）
@pytest.mark.asyncio
async def test_get_binary_data_case8(mocker: MockerFixture, create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    response = await user_profile_util.get_binary_data(
        pdsUserInfo=PDS_USER_INFO,
        fileSavePathList=FILE_SAVE_PATH_LIST,
        kmsDataKeyList=KMS_DATA_KEY_LIST,
        chiperNonceList=CHIPER_NONCE_LIST,
        apiType="1",
        request=REQUEST,
        requestBody={}
    )

    assert response == {
        "result": True,
        "binaryData": response["binaryData"]
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No9.共通エラーチェック処理が成功（エラー情報有り）
#     複合処理がFalseを返却することがないので不要？


# No10.リスト形式で返却されたレスポンスのバイナリデータを変数に結合していく（1件）
@pytest.mark.asyncio
async def test_get_binary_data_case10(mocker: MockerFixture, create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    response = await user_profile_util.get_binary_data(
        pdsUserInfo=PDS_USER_INFO,
        fileSavePathList=["transaction1/43bca47eb3fb4e1095445382df70dd76_0"],
        kmsDataKeyList=KMS_DATA_KEY_LIST,
        chiperNonceList=CHIPER_NONCE_LIST,
        apiType="1",
        request=REQUEST,
        requestBody={}
    )

    assert response == {
        "result": True,
        "binaryData": response["binaryData"]
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No11.リスト形式で返却されたレスポンスのバイナリデータを変数に結合していく（複数件）
@pytest.mark.asyncio
async def test_get_binary_data_case11(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    response = await user_profile_util.get_binary_data(
        pdsUserInfo=PDS_USER_INFO,
        fileSavePathList=FILE_SAVE_PATH_LIST,
        kmsDataKeyList=KMS_DATA_KEY_LIST,
        chiperNonceList=CHIPER_NONCE_LIST,
        apiType="1",
        request=REQUEST,
        requestBody={}
    )

    assert response == {
        "result": True,
        "binaryData": response["binaryData"]
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No12.終了処理
@pytest.mark.asyncio
async def test_get_binary_data_case12(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    response = await user_profile_util.get_binary_data(
        pdsUserInfo=PDS_USER_INFO,
        fileSavePathList=FILE_SAVE_PATH_LIST,
        kmsDataKeyList=KMS_DATA_KEY_LIST,
        chiperNonceList=CHIPER_NONCE_LIST,
        apiType="1",
        request=REQUEST,
        requestBody={}
    )

    assert response == {
        "result": True,
        "binaryData": response["binaryData"]
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)
