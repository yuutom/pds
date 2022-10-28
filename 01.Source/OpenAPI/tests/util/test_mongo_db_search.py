from fastapi.testclient import TestClient
from util.commonUtil import CommonUtilClass
from app import app
from fastapi import Request
import pytest
from pytest_mock.plugin import MockerFixture
from util.tokenUtil import TokenUtilClass
import util.logUtil as logUtil
from exceptionClass.PDSException import PDSException
from const.messageConst import MessageConstClass
from const.systemConst import SystemConstClass

client = TestClient(app)

HEADER = {"pds_user_domain_name": "toppan-f", "pds_user_id": "C0123456"}

DATA = {
    "pdsUserInfo": None,
    "dataMatchMode": None,
    "dataJsonKey": None,
    "dataStr": None
}

trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
token_util = TokenUtilClass(trace_logger)
common_util = CommonUtilClass(trace_logger)

# 共通DB接続準備処理
common_db_info_response = common_util.get_common_db_info_and_connection()


@pytest.fixture
def data():
    pds_user_domain_check_result = common_util.check_pds_user_domain(HEADER["pds_user_domain_name"], HEADER["pds_user_id"])
    pds_user_info = pds_user_domain_check_result["pdsUserInfo"]

    # 検証に使用するデータ
    yield {
        "pdsUserInfo": pds_user_info,
        "dataMatchMode": "前方一致",
        "dataJsonKey": "data.name.first",
        "dataStr": "taro"
    }


# No1. MongoDB検索処理
# 01.引数検証処理チェック処理
# MongoDB検索処理_01.引数検証処理チェック　シート参照
# No.1_1.PDSユーザ情報が空値 (None)
def test_mongo_db_search_case1_1(data):
    data_copy = data.copy()
    data_copy["pdsUserInfo"] = None
    with pytest.raises(PDSException) as e:
        common_util.mongodb_search(
            pdsUserInfo=data_copy["pdsUserInfo"],
            dataMatchMode=data_copy["dataMatchMode"],
            dataJsonKey=data_copy["dataJsonKey"],
            dataStr=data_copy["dataStr"]
        )
    assert e.type == PDSException
    assert e.value.error_info_list == [
        {
            "errorCode": "020001",
            "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "PDSユーザ情報")
        }
    ]
    print(e)


# No.1_2.PDSユーザ情報が正常値
def test_mongo_db_search_case1_2(data):
    data_copy = data.copy()
    response = common_util.mongodb_search(
        pdsUserInfo=data_copy["pdsUserInfo"],
        dataMatchMode=data_copy["dataMatchMode"],
        dataJsonKey=data_copy["dataJsonKey"],
        dataStr=data_copy["dataStr"]
    )
    assert response == {
        "result": True,
        "objectIdList": response["objectIdList"]
    }
    print(response)


# No.1_3.保存データ検索モードが空値 (None)
def test_mongo_db_search_case1_3(data):
    data_copy = data.copy()
    data_copy["dataMatchMode"] = None
    with pytest.raises(PDSException) as e:
        common_util.mongodb_search(
            pdsUserInfo=data_copy["pdsUserInfo"],
            dataMatchMode=data_copy["dataMatchMode"],
            dataJsonKey=data_copy["dataJsonKey"],
            dataStr=data_copy["dataStr"]
        )
    assert e.type == PDSException
    assert e.value.error_info_list == [
        {
            "errorCode": "020001",
            "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "保存データ検索モード")
        }
    ]
    print(e)


# No.1_4.保存データ検索モードが正常値
def test_mongo_db_search_case1_4(data):
    data_copy = data.copy()
    response = common_util.mongodb_search(
        pdsUserInfo=data_copy["pdsUserInfo"],
        dataMatchMode=data_copy["dataMatchMode"],
        dataJsonKey=data_copy["dataJsonKey"],
        dataStr=data_copy["dataStr"]
    )
    assert response == {
        "result": True,
        "objectIdList": response["objectIdList"]
    }
    print(response)


# No.1_5.保存データJsonキー情報が空値 (None)
def test_mongo_db_search_case1_5(data):
    data_copy = data.copy()
    data_copy["dataJsonKey"] = None
    with pytest.raises(PDSException) as e:
        common_util.mongodb_search(
            pdsUserInfo=data_copy["pdsUserInfo"],
            dataMatchMode=data_copy["dataMatchMode"],
            dataJsonKey=data_copy["dataJsonKey"],
            dataStr=data_copy["dataStr"]
        )
    assert e.type == PDSException
    assert e.value.error_info_list == [
        {
            "errorCode": "020001",
            "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "保存データJsonキー情報")
        }
    ]
    print(e)


# No.1_6.保存データJsonキー情報が正常値
def test_mongo_db_search_case1_6(data):
    data_copy = data.copy()
    response = common_util.mongodb_search(
        pdsUserInfo=data_copy["pdsUserInfo"],
        dataMatchMode=data_copy["dataMatchMode"],
        dataJsonKey=data_copy["dataJsonKey"],
        dataStr=data_copy["dataStr"]
    )
    assert response == {
        "result": True,
        "objectIdList": response["objectIdList"]
    }
    print(response)


# No.1_7.保存データ検索文字列が空値 (None)
def test_mongo_db_search_case1_7(data):
    data_copy = data.copy()
    data_copy["dataStr"] = None
    with pytest.raises(PDSException) as e:
        common_util.mongodb_search(
            pdsUserInfo=data_copy["pdsUserInfo"],
            dataMatchMode=data_copy["dataMatchMode"],
            dataJsonKey=data_copy["dataJsonKey"],
            dataStr=data_copy["dataStr"]
        )
    assert e.type == PDSException
    assert e.value.error_info_list == [
        {
            "errorCode": "020001",
            "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "保存データ検索文字列")
        }
    ]
    print(e)


# No.1_8.保存データ検索文字列が正常値
def test_mongo_db_search_case1_8(data):
    data_copy = data.copy()
    response = common_util.mongodb_search(
        pdsUserInfo=data_copy["pdsUserInfo"],
        dataMatchMode=data_copy["dataMatchMode"],
        dataJsonKey=data_copy["dataJsonKey"],
        dataStr=data_copy["dataStr"]
    )
    assert response == {
        "result": True,
        "objectIdList": response["objectIdList"]
    }
    print(response)


# 02.MongoDB接続準備処理
# No.2.◆異常系 接続に失敗する 設定値を異常な値に変更する
def test_mongo_db_search_case2(mocker: MockerFixture, data):
    data_copy = data.copy()
    # Exception
    mocker.patch("util.commonUtil.CommonUtilClass.get_mongo_db_info_and_connection").side_effect = Exception('testException')
    with pytest.raises(PDSException) as e:
        common_util.mongodb_search(
            pdsUserInfo=data_copy["pdsUserInfo"],
            dataMatchMode=data_copy["dataMatchMode"],
            dataJsonKey=data_copy["dataJsonKey"],
            dataStr=data_copy["dataStr"]
        )
    assert e.type == PDSException
    assert e.value.error_info_list == [
        {
            "errorCode": "999999",
            "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
        }
    ]
    print(e)


# No.3.◆正常系 接続に成功する プログラムが配置されたリージョンが東京リージョンaの場合
def test_mongo_db_search_case3(mocker: MockerFixture, data):
    data_copy = data.copy()
    # Exception
    mocker.patch.object(SystemConstClass, "AWS_CONST", {"REGION": "ap-northeast-1"})
    response = common_util.mongodb_search(
        pdsUserInfo=data_copy["pdsUserInfo"],
        dataMatchMode=data_copy["dataMatchMode"],
        dataJsonKey=data_copy["dataJsonKey"],
        dataStr=data_copy["dataStr"]
    )
    assert response == {
        "result": True,
        "objectIdList": response["objectIdList"]
    }
    print(response)


# No.4.◆正常系 接続に成功する プログラムが配置されたリージョンが大阪リージョンaの場合
def test_mongo_db_search_case4(mocker: MockerFixture, data):
    data_copy = data.copy()
    # Exception
    mocker.patch.object(SystemConstClass, "AWS_CONST", {"REGION": "ap-northeast-3"})
    response = common_util.mongodb_search(
        pdsUserInfo=data_copy["pdsUserInfo"],
        dataMatchMode=data_copy["dataMatchMode"],
        dataJsonKey=data_copy["dataJsonKey"],
        dataStr=data_copy["dataStr"]
    )
    assert response == {
        "result": True,
        "objectIdList": response["objectIdList"]
    }
    print(response)


# No.5.◆正常系 接続に成功する プログラムが配置されたリージョンが東京リージョンcの場合
def test_mongo_db_search_case5(mocker: MockerFixture, data):
    data_copy = data.copy()
    data_copy["pdsUserInfo"]["tokyo_a_mongodb_secret_name"] = None
    # Exception
    mocker.patch.object(SystemConstClass, "AWS_CONST", {"REGION": "ap-northeast-1"})
    response = common_util.mongodb_search(
        pdsUserInfo=data_copy["pdsUserInfo"],
        dataMatchMode=data_copy["dataMatchMode"],
        dataJsonKey=data_copy["dataJsonKey"],
        dataStr=data_copy["dataStr"]
    )
    assert response == {
        "result": True,
        "objectIdList": response["objectIdList"]
    }
    print(response)


# No.6.◆正常系 接続に成功する プログラムが配置されたリージョンが大阪リージョンcの場合
def test_mongo_db_search_case6(mocker: MockerFixture, data):
    data_copy = data.copy()
    data_copy["pdsUserInfo"]["osaka_a_mongodb_secret_name"] = None
    # Exception
    mocker.patch.object(SystemConstClass, "AWS_CONST", {"REGION": "ap-northeast-3"})
    response = common_util.mongodb_search(
        pdsUserInfo=data_copy["pdsUserInfo"],
        dataMatchMode=data_copy["dataMatchMode"],
        dataJsonKey=data_copy["dataJsonKey"],
        dataStr=data_copy["dataStr"]
    )
    assert response == {
        "result": True,
        "objectIdList": response["objectIdList"]
    }
    print(response)


# 03.MongoDB検索処理
# No.7.◆異常系 TFオペレータ取得処理が失敗する（MongoDBエラー）
def test_mongo_db_search_case7(mocker: MockerFixture, data):
    data_copy = data.copy()
    # Exception
    mocker.patch("util.mongoDbUtil.MongoDbClass.find_filter").side_effect = Exception('testException')
    with pytest.raises(PDSException) as e:
        common_util.mongodb_search(
            pdsUserInfo=data_copy["pdsUserInfo"],
            dataMatchMode=data_copy["dataMatchMode"],
            dataJsonKey=data_copy["dataJsonKey"],
            dataStr=data_copy["dataStr"]
        )
    assert e.type == PDSException
    assert e.value.error_info_list == [
        {
            "errorCode": "999999",
            "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
        }
    ]
    print(e)


# No.8.◆正常系 MongoDB検索処理が成功する 「引数．リクエストボディ．保存データ検索モード」が"前方一致"の場合 東京リージョンa
def test_mongo_db_search_case8(data):
    data_copy = data.copy()
    data_copy["dataMatchMode"] = "前方一致"
    data_copy["dataStr"] = "ta"
    response = common_util.mongodb_search(
        pdsUserInfo=data_copy["pdsUserInfo"],
        dataMatchMode=data_copy["dataMatchMode"],
        dataJsonKey=data_copy["dataJsonKey"],
        dataStr=data_copy["dataStr"]
    )
    assert response == {
        "result": True,
        "objectIdList": response["objectIdList"]
    }
    print(response)


# No.9.◆正常系 MongoDB検索処理が成功する 「引数．リクエストボディ．保存データ検索モード」が"後方一致"の場合 東京リージョンa
def test_mongo_db_search_case9(data):
    data_copy = data.copy()
    data_copy["dataMatchMode"] = "後方一致"
    data_copy["dataStr"] = "ro"
    response = common_util.mongodb_search(
        pdsUserInfo=data_copy["pdsUserInfo"],
        dataMatchMode=data_copy["dataMatchMode"],
        dataJsonKey=data_copy["dataJsonKey"],
        dataStr=data_copy["dataStr"]
    )
    assert response == {
        "result": True,
        "objectIdList": response["objectIdList"]
    }
    print(response)


# No.10.◆正常系 MongoDB検索処理が成功する 「引数．リクエストボディ．保存データ検索モード」が"部分一致"の場合 東京リージョンa
def test_mongo_db_search_case10(data):
    data_copy = data.copy()
    data_copy["dataMatchMode"] = "部分一致"
    data_copy["dataStr"] = "ar"
    response = common_util.mongodb_search(
        pdsUserInfo=data_copy["pdsUserInfo"],
        dataMatchMode=data_copy["dataMatchMode"],
        dataJsonKey=data_copy["dataJsonKey"],
        dataStr=data_copy["dataStr"]
    )
    assert response == {
        "result": True,
        "objectIdList": response["objectIdList"]
    }
    print(response)


# No.11.◆正常系 MongoDB検索処理が成功する 東京リージョンc
def test_mongo_db_search_case11(mocker: MockerFixture, data):
    data_copy = data.copy()
    data_copy["pdsUserInfo"]["tokyo_a_mongodb_secret_name"] = None
    mocker.patch.object(SystemConstClass, "AWS_CONST", {"REGION": "ap-northeast-1"})
    response = common_util.mongodb_search(
        pdsUserInfo=data_copy["pdsUserInfo"],
        dataMatchMode=data_copy["dataMatchMode"],
        dataJsonKey=data_copy["dataJsonKey"],
        dataStr=data_copy["dataStr"]
    )
    assert response == {
        "result": True,
        "objectIdList": response["objectIdList"]
    }
    print(response)


# No.12.◆正常系 MongoDB検索処理が成功する 大阪リージョンa
def test_mongo_db_search_case12(mocker: MockerFixture, data):
    data_copy = data.copy()
    mocker.patch.object(SystemConstClass, "AWS_CONST", {"REGION": "ap-northeast-3"})
    response = common_util.mongodb_search(
        pdsUserInfo=data_copy["pdsUserInfo"],
        dataMatchMode=data_copy["dataMatchMode"],
        dataJsonKey=data_copy["dataJsonKey"],
        dataStr=data_copy["dataStr"]
    )
    assert response == {
        "result": True,
        "objectIdList": response["objectIdList"]
    }
    print(response)


# No.13.◆正常系 MongoDB検索処理が成功する 大阪リージョンc
def test_mongo_db_search_case13(mocker: MockerFixture, data):
    data_copy = data.copy()
    data_copy["pdsUserInfo"]["osaka_a_mongodb_secret_name"] = None
    mocker.patch.object(SystemConstClass, "AWS_CONST", {"REGION": "ap-northeast-3"})
    response = common_util.mongodb_search(
        pdsUserInfo=data_copy["pdsUserInfo"],
        dataMatchMode=data_copy["dataMatchMode"],
        dataJsonKey=data_copy["dataJsonKey"],
        dataStr=data_copy["dataStr"]
    )
    assert response == {
        "result": True,
        "objectIdList": response["objectIdList"]
    }
    print(response)


# 04.共通エラーチェック処理
# No.14.◆正常系 共通エラーチェック処理が成功（エラー情報有り）
def test_mongo_db_search_case14(mocker: MockerFixture, data):
    data_copy = data.copy()
    # Exception
    mocker.patch("util.mongoDbUtil.MongoDbClass.find_filter").return_value = {
        "result": False,
        "errorCode": "999999",
        "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
    }
    with pytest.raises(PDSException) as e:
        common_util.mongodb_search(
            pdsUserInfo=data_copy["pdsUserInfo"],
            dataMatchMode=data_copy["dataMatchMode"],
            dataJsonKey=data_copy["dataJsonKey"],
            dataStr=data_copy["dataStr"]
        )
    assert e.type == PDSException
    assert e.value.error_info_list == [
        {
            "errorCode": "992001",
            "message": logUtil.message_build(MessageConstClass.ERRORS["992001"]["message"], "992001")
        }
    ]
    print(e)


# 05.終了処理
# No.15.◆正常系
def test_mongo_db_search_case15(data):
    data_copy = data.copy()
    response = common_util.mongodb_search(
        pdsUserInfo=data_copy["pdsUserInfo"],
        dataMatchMode=data_copy["dataMatchMode"],
        dataJsonKey=data_copy["dataJsonKey"],
        dataStr=data_copy["dataStr"]
    )
    assert response == {
        "result": True,
        "objectIdList": response["objectIdList"]
    }
    print(response)
