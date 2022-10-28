import pytest
import asyncio
from fastapi import Request
from pytest_mock.plugin import MockerFixture
import util.logUtil as logUtil
from exceptionClass.PDSException import PDSException
from const.messageConst import MessageConstClass
from const.systemConst import SystemConstClass
import util.commonUtil as commonUtil
from util.userProfileUtil import UserProfileUtilClass
from util.commonUtil import CommonUtilClass
from const.sqlConst import SqlConstClass

DATA = {
    "transaction_id": "transaction30500",
    "save_image_idx": 1,
    "save_image_data": "aiueo12345",
    "save_image_data_hash": "98765abcde",
    "valid_flg": True,
    "save_image_data_array_index": 1
}

KMS_ID = "fdb4c6aa-50b0-4ed1-bdad-32c21e0a0387"
BUCKET_NAME = "pds-c0000000-bucket"


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
# No1_1.バイナリ登録データ．トランザクションIDの値が設定されていない (空値)
@pytest.mark.asyncio
async def test_insert_binary_data_case1_1(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transaction_id"] = ""
    with pytest.raises(PDSException) as e:
        await user_profile_util.insert_binary_data(
            binaryInsertData=data_copy,
            userProfileKmsId=KMS_ID,
            bucketName=BUCKET_NAME,
            pdsUserDbInfo=pds_user_db_info
        )

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "バイナリ登録データ．トランザクションID")
    }
    print(e)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No1_2.バイナリ登録データ．トランザクションIDの値が設定されている
@pytest.mark.asyncio
async def test_insert_binary_data_case1_2(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transaction_id"] = "transaction30501"
    response = await user_profile_util.insert_binary_data(
        binaryInsertData=data_copy,
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


# No1_3.バイナリ登録データ．保存画像インデックスの値が設定されていない (空値)
@pytest.mark.asyncio
async def test_insert_binary_data_case1_3(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transaction_id"] = "transaction30502"
    data_copy["save_image_idx"] = None
    with pytest.raises(PDSException) as e:
        await user_profile_util.insert_binary_data(
            binaryInsertData=data_copy,
            userProfileKmsId=KMS_ID,
            bucketName=BUCKET_NAME,
            pdsUserDbInfo=pds_user_db_info
        )

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "バイナリ登録データ．保存画像インデックス")
    }
    print(e)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No1_4.バイナリ登録データ．保存画像インデックスの値が設定されている
@pytest.mark.asyncio
async def test_insert_binary_data_case1_4(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transaction_id"] = "transaction30503"
    response = await user_profile_util.insert_binary_data(
        binaryInsertData=data_copy,
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


# No1_5.バイナリ登録データ．バイナリデータの値が設定されていない (空値)
@pytest.mark.asyncio
async def test_insert_binary_data_case1_5(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transaction_id"] = "transaction30504"
    data_copy["save_image_data"] = ""
    with pytest.raises(PDSException) as e:
        await user_profile_util.insert_binary_data(
            binaryInsertData=data_copy,
            userProfileKmsId=KMS_ID,
            bucketName=BUCKET_NAME,
            pdsUserDbInfo=pds_user_db_info
        )

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "バイナリ登録データ．バイナリデータ")
    }
    print(e)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No1_6.バイナリ登録データ．バイナリデータの値が設定されている
@pytest.mark.asyncio
async def test_insert_binary_data_case1_6(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transaction_id"] = "transaction30505"
    response = await user_profile_util.insert_binary_data(
        binaryInsertData=data_copy,
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


# No1_7.バイナリ登録データ．ハッシュ値の値が設定されていない (空値)
@pytest.mark.asyncio
async def test_insert_binary_data_case1_7(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transaction_id"] = "transaction30506"
    data_copy["save_image_data_hash"] = ""
    with pytest.raises(PDSException) as e:
        await user_profile_util.insert_binary_data(
            binaryInsertData=data_copy,
            userProfileKmsId=KMS_ID,
            bucketName=BUCKET_NAME,
            pdsUserDbInfo=pds_user_db_info
        )

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "バイナリ登録データ．ハッシュ値")
    }
    print(e)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No1_8.バイナリ登録データ．ハッシュ値の値が設定されている
@pytest.mark.asyncio
async def test_insert_binary_data_case1_8(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transaction_id"] = "transaction30507"
    response = await user_profile_util.insert_binary_data(
        binaryInsertData=data_copy,
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


# No1_9.バイナリ登録データ．有効フラグの値が設定されていない (空値)
@pytest.mark.asyncio
async def test_insert_binary_data_case1_9(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transaction_id"] = "transaction30508"
    data_copy["valid_flg"] = None
    with pytest.raises(PDSException) as e:
        await user_profile_util.insert_binary_data(
            binaryInsertData=data_copy,
            userProfileKmsId=KMS_ID,
            bucketName=BUCKET_NAME,
            pdsUserDbInfo=pds_user_db_info
        )

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "バイナリ登録データ．有効フラグ")
    }
    print(e)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No1_10.バイナリ登録データ．有効フラグの値が設定されている
@pytest.mark.asyncio
async def test_insert_binary_data_case1_10(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transaction_id"] = "transaction30509"
    response = await user_profile_util.insert_binary_data(
        binaryInsertData=data_copy,
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


# No1_11.バイナリ登録データ．表示順の値が設定されていない (空値)
@pytest.mark.asyncio
async def test_insert_binary_data_case1_11(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transaction_id"] = "transaction30510"
    data_copy["save_image_data_array_index"] = None
    with pytest.raises(PDSException) as e:
        await user_profile_util.insert_binary_data(
            binaryInsertData=data_copy,
            userProfileKmsId=KMS_ID,
            bucketName=BUCKET_NAME,
            pdsUserDbInfo=pds_user_db_info
        )

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "バイナリ登録データ．表示順")
    }
    print(e)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No1_12.バイナリ登録データ．表示順の値が設定されている
@pytest.mark.asyncio
async def test_insert_binary_data_case1_12(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transaction_id"] = "transaction30511"
    response = await user_profile_util.insert_binary_data(
        binaryInsertData=data_copy,
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


# No1_13.個人情報暗号・復号化用KMSIDの値が設定されていない (空値)
@pytest.mark.asyncio
async def test_insert_binary_data_case1_13(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transaction_id"] = "transaction30512"
    with pytest.raises(PDSException) as e:
        await user_profile_util.insert_binary_data(
            binaryInsertData=data_copy,
            userProfileKmsId=None,
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


# No1_14.個人情報暗号・復号化用KMSIDの値が設定されている
@pytest.mark.asyncio
async def test_insert_binary_data_case1_14(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transaction_id"] = "transaction30513"
    response = await user_profile_util.insert_binary_data(
        binaryInsertData=data_copy,
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


# No1_15.バケット名の値が設定されていない (空値)
@pytest.mark.asyncio
async def test_insert_binary_data_case1_15(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transaction_id"] = "transaction30514"
    with pytest.raises(PDSException) as e:
        await user_profile_util.insert_binary_data(
            binaryInsertData=data_copy,
            userProfileKmsId=KMS_ID,
            bucketName=None,
            pdsUserDbInfo=pds_user_db_info
        )

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "バケット名")
    }
    print(e)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No1_16.バケット名の値が設定されている
@pytest.mark.asyncio
async def test_insert_binary_data_case1_16(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transaction_id"] = "transaction30515"
    response = await user_profile_util.insert_binary_data(
        binaryInsertData=data_copy,
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


# No1_17.PDSユーザDB接続情報の値が設定されていない (空値)
@pytest.mark.asyncio
async def test_insert_binary_data_case1_17(create_user_profile_util):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    data_copy = DATA.copy()
    data_copy["transaction_id"] = "transaction30516"
    with pytest.raises(PDSException) as e:
        await user_profile_util.insert_binary_data(
            binaryInsertData=data_copy,
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


# No1_18.PDSユーザDB接続情報の値が設定されている
@pytest.mark.asyncio
async def test_insert_binary_data_case1_18(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transaction_id"] = "transaction30517"
    response = await user_profile_util.insert_binary_data(
        binaryInsertData=data_copy,
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


# No2.「変数．バイナリデータ」のデータサイズが2MB以下の場合、「変数．バイナリデータ」のデータサイズの半分の値を、「変数．チャンクサイズ」に格納する
#      0バイトの場合
# 入力チェックで弾かれるのでテスト不要


# No3.「変数．バイナリデータ」のデータサイズが2MB以下の場合、「変数．バイナリデータ」のデータサイズの半分の値を、「変数．チャンクサイズ」に格納する
@pytest.mark.asyncio
async def test_insert_binary_data_case3(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transaction_id"] = "transaction30519"
    response = await user_profile_util.insert_binary_data(
        binaryInsertData=data_copy,
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


# No4.「変数．バイナリデータ」のデータサイズが2MB以下の場合、「変数．バイナリデータ」のデータサイズの半分の値を、「変数．チャンクサイズ」に格納する
@pytest.mark.asyncio
async def test_insert_binary_data_case4(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transaction_id"] = "transaction30520"
    f = open('tests/public/14MB.txt', 'r', encoding='UTF-8')
    text = f.read()
    data_copy["save_image_data"] = text
    response = await user_profile_util.insert_binary_data(
        binaryInsertData=data_copy,
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


# No5.PDSユーザDB接続に失敗する。設定値を異常な値に変更する
@pytest.mark.asyncio
async def test_insert_binary_data_case5(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transaction_id"] = "transaction30521"
    pds_user_db_info["host"] = "test-db"
    with pytest.raises(PDSException) as e:
        await user_profile_util.insert_binary_data(
            binaryInsertData=data_copy,
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


# No6.PDSユーザDB接続に成功する。
@pytest.mark.asyncio
async def test_insert_binary_data_case6(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transaction_id"] = "transaction30522"
    response = await user_profile_util.insert_binary_data(
        binaryInsertData=data_copy,
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


# No7.UUID ( v4ハイフンなし) を作成して、「変数．バイナリデータID」に格納する
@pytest.mark.asyncio
async def test_insert_binary_data_case7(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transaction_id"] = "transaction30523"
    response = await user_profile_util.insert_binary_data(
        binaryInsertData=data_copy,
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


# No8.保存したいバイナリデータID一意検証処理が失敗する（posgresqlエラー）
@pytest.mark.asyncio
async def test_insert_binary_data_case8(mocker: MockerFixture, create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transaction_id"] = "transaction30524"
    mocker.patch.object(SqlConstClass, "USER_PROFILE_BINARY_UNIQUE_CHECK_SAVE_IMAGE_DATA_ID_SQL", """ SELECT * FROM AAAAAA; """)
    response = await user_profile_util.insert_binary_data(
        binaryInsertData=data_copy,
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


# No9.「変数．保存画像一意検証データリスト」が0件以外の場合
#     1回目失敗
@pytest.mark.asyncio
async def test_insert_binary_data_case9(mocker: MockerFixture, create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transaction_id"] = "transaction30525"
    # 登録済みのUUIDを返却する
    mocker.patch("util.commonUtil.get_uuid_no_hypen").side_effect = [
        "597b54455ca245a4ad8c766e58cd21d2",
        commonUtil.get_uuid_no_hypen(),
        commonUtil.get_uuid_no_hypen(),
        commonUtil.get_uuid_no_hypen()
    ]
    response = await user_profile_util.insert_binary_data(
        binaryInsertData=data_copy,
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


# No10.「変数．保存画像一意検証データリスト」が0件以外の場合
#      5回目
@pytest.mark.asyncio
async def test_insert_binary_data_case10(mocker: MockerFixture, create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transaction_id"] = "transaction30526"
    # 登録済みのUUIDを返却する
    mocker.patch("util.commonUtil.get_uuid_no_hypen").return_value = "597b54455ca245a4ad8c766e58cd21d2"
    response = await user_profile_util.insert_binary_data(
        binaryInsertData=data_copy,
        userProfileKmsId=KMS_ID,
        bucketName=BUCKET_NAME,
        pdsUserDbInfo=pds_user_db_info
    )

    assert response == {
        "result": False,
        "errorInfo": response["errorInfo"]
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No11.個人情報バイナリデータ登録処理が成功する
@pytest.mark.asyncio
async def test_insert_binary_data_case11(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transaction_id"] = "transaction30527"
    response = await user_profile_util.insert_binary_data(
        binaryInsertData=data_copy,
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


# No12.「変数．エラー情報」がNullの場合、「08.トランザクション作成処理」に遷移する
@pytest.mark.asyncio
async def test_insert_binary_data_case12(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transaction_id"] = "transaction30528"
    response = await user_profile_util.insert_binary_data(
        binaryInsertData=data_copy,
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


# No13.「変数．エラー情報」がNullの場合、「08.トランザクション作成処理」に遷移する
@pytest.mark.asyncio
async def test_insert_binary_data_case13(mocker: MockerFixture, create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transaction_id"] = "transaction30529"
    # 登録済みのUUIDを返却する
    mocker.patch("util.commonUtil.get_uuid_no_hypen").return_value = "597b54455ca245a4ad8c766e58cd21d2"
    response = await user_profile_util.insert_binary_data(
        binaryInsertData=data_copy,
        userProfileKmsId=KMS_ID,
        bucketName=BUCKET_NAME,
        pdsUserDbInfo=pds_user_db_info
    )

    assert response == {
        "result": False,
        "errorInfo": response["errorInfo"]
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No14.レスポンス情報を作成し、返却する
@pytest.mark.asyncio
async def test_insert_binary_data_case14(mocker: MockerFixture, create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transaction_id"] = "transaction30530"
    # 登録済みのUUIDを返却する
    mocker.patch("util.commonUtil.get_uuid_no_hypen").return_value = "597b54455ca245a4ad8c766e58cd21d2"
    response = await user_profile_util.insert_binary_data(
        binaryInsertData=data_copy,
        userProfileKmsId=KMS_ID,
        bucketName=BUCKET_NAME,
        pdsUserDbInfo=pds_user_db_info
    )

    assert response == {
        "result": False,
        "errorInfo": response["errorInfo"]
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No15.個人情報バイナリデータ登録処理が失敗する（posgresqlエラー）
@pytest.mark.asyncio
async def test_insert_binary_data_case15(mocker: MockerFixture, create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transaction_id"] = "transaction30531"
    mocker.patch.object(SqlConstClass, "USER_PROFILE_BINARY_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    response = await user_profile_util.insert_binary_data(
        binaryInsertData=data_copy,
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


# No16.個人情報バイナリデータ登録処理が成功する
@pytest.mark.asyncio
async def test_insert_binary_data_case16(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transaction_id"] = "transaction30532"
    response = await user_profile_util.insert_binary_data(
        binaryInsertData=data_copy,
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


# No17.「変数．エラー情報」がNullの場合、「13.トランザクションコミット処理」に遷移する
@pytest.mark.asyncio
async def test_insert_binary_data_case17(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transaction_id"] = "transaction30533"
    response = await user_profile_util.insert_binary_data(
        binaryInsertData=data_copy,
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


# No18.「変数．エラー情報」がNull以外の場合、「11.トランザクションロールバック処理」に遷移する
@pytest.mark.asyncio
async def test_insert_binary_data_case18(mocker: MockerFixture, create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transaction_id"] = "transaction30534"
    mocker.patch.object(SqlConstClass, "USER_PROFILE_BINARY_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    response = await user_profile_util.insert_binary_data(
        binaryInsertData=data_copy,
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


# No19.「個人情報バイナリデータ登録トランザクション」をロールバックする
@pytest.mark.asyncio
async def test_insert_binary_data_case19(mocker: MockerFixture, create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transaction_id"] = "transaction30535"
    mocker.patch.object(SqlConstClass, "USER_PROFILE_BINARY_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    response = await user_profile_util.insert_binary_data(
        binaryInsertData=data_copy,
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


# No20.レスポンス情報を作成し、返却する
@pytest.mark.asyncio
async def test_insert_binary_data_case20(mocker: MockerFixture, create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transaction_id"] = "transaction30536"
    mocker.patch.object(SqlConstClass, "USER_PROFILE_BINARY_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    response = await user_profile_util.insert_binary_data(
        binaryInsertData=data_copy,
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


# No21.コミットが成功する
@pytest.mark.asyncio
async def test_insert_binary_data_case21(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transaction_id"] = "transaction30537"
    response = await user_profile_util.insert_binary_data(
        binaryInsertData=data_copy,
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


# No22.「変数．分割バイナリデータリスト」の要素数が0の場合
#      0バイトが発生しないので分割バイナリデータリストは必ず1以上になるため再現不可
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No23.「変数．分割バイナリデータリスト」の要素数が1以上の場合
@pytest.mark.asyncio
async def test_insert_binary_data_case23(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transaction_id"] = "transaction30539"
    response = await user_profile_util.insert_binary_data(
        binaryInsertData=data_copy,
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


# No24.「変数．個人情報バイナリ分割データ登録処理リスト」に個人情報バイナリ分割データ登録処理を追加する
@pytest.mark.asyncio
async def test_insert_binary_data_case24(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transaction_id"] = "transaction30540"
    response = await user_profile_util.insert_binary_data(
        binaryInsertData=data_copy,
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


# No25.「変数．個人情報バイナリ分割データ登録処理リスト」をもとに、個人情報バイナリ分割データ登録処理を並列で実行し、失敗すること
@pytest.mark.asyncio
async def test_insert_binary_data_case25(mocker: MockerFixture, create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transaction_id"] = "transaction30541"
    # 個人情報分割データ登録処理でSQL実行エラーになる情報を付与
    mocker.patch.object(SqlConstClass, "USER_PROFILE_BINARY_SEPARATE_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    response = await user_profile_util.insert_binary_data(
        binaryInsertData=data_copy,
        userProfileKmsId=KMS_ID,
        bucketName=BUCKET_NAME,
        pdsUserDbInfo=pds_user_db_info
    )

    assert response == {
        "result": False,
        "errorInfo": response["errorInfo"]
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No26.「変数．個人情報バイナリ分割データ登録処理リスト」をもとに、個人情報バイナリ分割データ登録処理を並列で実行し、成功すること
@pytest.mark.asyncio
async def test_insert_binary_data_case26(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transaction_id"] = "transaction30542"
    response = await user_profile_util.insert_binary_data(
        binaryInsertData=data_copy,
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


# No27.「変数．個人情報バイナリ分割データ登録処理実行結果リスト[]．処理結果」にfalseが存在する場合、「17.個人情報バイナリ分割データ登録処理実行処理エラー処理」に遷移する
@pytest.mark.asyncio
async def test_insert_binary_data_case27(mocker: MockerFixture, create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transaction_id"] = "transaction30543"
    # 個人情報分割データ登録処理でSQL実行エラーになる情報を付与
    mocker.patch.object(SqlConstClass, "USER_PROFILE_BINARY_SEPARATE_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    response = await user_profile_util.insert_binary_data(
        binaryInsertData=data_copy,
        userProfileKmsId=KMS_ID,
        bucketName=BUCKET_NAME,
        pdsUserDbInfo=pds_user_db_info
    )

    assert response == {
        "result": False,
        "errorInfo": response["errorInfo"]
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No28.「変数．個人情報バイナリ分割データ登録処理実行結果リスト[]．処理結果」にfalseが存在しない場合、「18.終了処理」に遷移する
@pytest.mark.asyncio
async def test_insert_binary_data_case28(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transaction_id"] = "transaction30544"
    response = await user_profile_util.insert_binary_data(
        binaryInsertData=data_copy,
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


# No29.レスポンス情報を作成し、返却する
@pytest.mark.asyncio
async def test_insert_binary_data_case29(mocker: MockerFixture, create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transaction_id"] = "transaction30545"
    # 個人情報分割データ登録処理でSQL実行エラーになる情報を付与
    mocker.patch.object(SqlConstClass, "USER_PROFILE_BINARY_SEPARATE_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    response = await user_profile_util.insert_binary_data(
        binaryInsertData=data_copy,
        userProfileKmsId=KMS_ID,
        bucketName=BUCKET_NAME,
        pdsUserDbInfo=pds_user_db_info
    )

    assert response == {
        "result": False,
        "errorInfo": response["errorInfo"]
    }
    print(response)
    # 非同期のクローズまでに少し時間がかかり、待機させないとログにエラーが出力されるので追加
    await asyncio.sleep(0.250)


# No30.「変数．個人情報バイナリ分割データ登録処理実行結果リスト[]．処理結果」にfalseが存在しない場合、「15.終了処理」に遷移する
@pytest.mark.asyncio
async def test_insert_binary_data_case30(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transaction_id"] = "transaction30546"
    response = await user_profile_util.insert_binary_data(
        binaryInsertData=data_copy,
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


# No31.「変数．バイナリデータ」のデータサイズが2MB以下の場合、「変数．バイナリデータ」のデータサイズの半分の値を、「変数．チャンクサイズ」に格納する。（1バイトの場合のテスト）
@pytest.mark.asyncio
async def test_insert_binary_data_case31(create_user_profile_util, create_pds_user_db_info):
    user_profile_util: UserProfileUtilClass = create_user_profile_util
    pds_user_db_info: dict = create_pds_user_db_info
    data_copy = DATA.copy()
    data_copy["transaction_id"] = "transaction30547"
    data_copy["save_image_data"] = "a"
    response = await user_profile_util.insert_binary_data(
        binaryInsertData=data_copy,
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
