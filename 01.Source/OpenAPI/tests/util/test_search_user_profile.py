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
from const.sqlConst import SqlConstClass

client = TestClient(app)

HEADER = {"pds_user_domain_name": "toppan-f", "pds_user_id": "C0123456"}

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
        "pdsUserInstanceSecretName": pds_user_info["pdsUserInstanceSecretName"],
        "searchCriteria": {
            "userIdMatchMode": None,
            "userIdStr": HEADER["pds_user_domain_name"],
            "dataJsonKey": None,
            "dataMatchMode": None,
            "dataStr": None,
            "imageHash": None,
            "fromDate": None,
            "toDate": None
        },
        "objectIdList": None
    }


# No1_1.引数検証処理チェック
# 異常系　引数．PDSユーザDBインスタンスシークレット名　値が設定されていない（空値）
def test_search_user_profile_case1_1(data):
    data_copy = data.copy()
    data_copy["pdsUserInstanceSecretName"] = ""
    with pytest.raises(PDSException) as e:
        common_util.search_user_profile(
            pdsUserInstanceSecretName=data_copy["pdsUserInstanceSecretName"],
            searchCriteria=data_copy["searchCriteria"],
            objectIdList=data_copy["objectIdList"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "PDSユーザDBインスタンスシークレット名")
    }
    print(e)


# No1_2.引数検証処理チェック
# 正常系　引数．PDSユーザDBインスタンスシークレット名　値が設定されている
def test_search_user_profile_case1_2(data):
    data_copy = data.copy()
    response = common_util.search_user_profile(
        pdsUserInstanceSecretName=data_copy["pdsUserInstanceSecretName"],
        searchCriteria=data_copy["searchCriteria"],
        objectIdList=data_copy["objectIdList"]
    )
    assert response == {
        "result": True,
        "count": response["count"],
        "transactionId": response["transactionId"],
        "userId": response["userId"],
        "saveDate": response["saveDate"],
        "data": response["data"],
        "imageHash": response["imageHash"]
    }
    print(response)


# No2.PDSユーザDB接続情報取得処理　異常系
# 接続に失敗する
# 設定値を異常な値に変更する
def test_search_user_profile_case2(data, mocker: MockerFixture):
    data_copy = data.copy()
    # Exception
    mocker.patch("util.commonUtil.CommonUtilClass.get_secret_info").return_value = {"host": "test", "port": "test", "username": "test", "password": "test"}
    response = common_util.search_user_profile(
        pdsUserInstanceSecretName=data_copy["pdsUserInstanceSecretName"],
        searchCriteria=data_copy["searchCriteria"],
        objectIdList=data_copy["objectIdList"]
    )
    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "999999",
            "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
        }
    }
    print(response)


# No3.PDSユーザDB接続情報取得処理　正常系
# 接続に成功する
def test_search_user_profile_case3(data):
    data_copy = data.copy()
    response = common_util.search_user_profile(
        pdsUserInstanceSecretName=data_copy["pdsUserInstanceSecretName"],
        searchCriteria=data_copy["searchCriteria"],
        objectIdList=data_copy["objectIdList"]
    )
    assert response == {
        "result": True,
        "count": response["count"],
        "transactionId": response["transactionId"],
        "userId": response["userId"],
        "saveDate": response["saveDate"],
        "data": response["data"],
        "imageHash": response["imageHash"]
    }
    print(response)


# No4.検索条件作成処理
# 「引数．検索条件。検索用日時From」がNull以外の場合
def test_search_user_profile_case4(data):
    data_copy = data.copy()
    data_copy["searchCriteria"]["fromDate"] = "2022-09-12"
    response = common_util.search_user_profile(
        pdsUserInstanceSecretName=data_copy["pdsUserInstanceSecretName"],
        searchCriteria=data_copy["searchCriteria"],
        objectIdList=data_copy["objectIdList"]
    )
    assert response == {
        "result": True,
        "count": response["count"],
        "transactionId": response["transactionId"],
        "userId": response["userId"],
        "saveDate": response["saveDate"],
        "data": response["data"],
        "imageHash": response["imageHash"]
    }
    print(response)


# No5.検索条件作成処理
# 「引数．検索条件。検索用日時To」がNull以外の場合
def test_search_user_profile_case5(data):
    data_copy = data.copy()
    data_copy["searchCriteria"]["toDate"] = "2022-09-12"
    response = common_util.search_user_profile(
        pdsUserInstanceSecretName=data_copy["pdsUserInstanceSecretName"],
        searchCriteria=data_copy["searchCriteria"],
        objectIdList=data_copy["objectIdList"]
    )
    assert response == {
        "result": True,
        "count": response["count"],
        "transactionId": response["transactionId"],
        "userId": response["userId"],
        "saveDate": response["saveDate"],
        "data": response["data"],
        "imageHash": response["imageHash"]
    }
    print(response)


# No6.検索条件作成処理
# 「引数．検索条件．保存されたバイナリデータハッシュ値」がNull以外の場合
def test_search_user_profile_case6(data):
    data_copy = data.copy()
    data_copy["searchCriteria"]["imageHash"] = "abs"
    response = common_util.search_user_profile(
        pdsUserInstanceSecretName=data_copy["pdsUserInstanceSecretName"],
        searchCriteria=data_copy["searchCriteria"],
        objectIdList=data_copy["objectIdList"]
    )
    assert response == {
        "result": True,
        "count": response["count"],
        "transactionId": response["transactionId"],
        "userId": response["userId"],
        "saveDate": response["saveDate"],
        "data": response["data"],
        "imageHash": response["imageHash"]
    }
    print(response)


# No7．検索条件作成処理
# 「引数．検索条件．検索用ユーザID検索文字列」がNull以外の場合　かつ「引数．検索条件．検索用ユーザID検索モード」が "前方一致"の場合
def test_search_user_profile_case7(data):
    data_copy = data.copy()
    data_copy["searchCriteria"]["userIdStr"] = "abs"
    data_copy["searchCriteria"]["userIdMatchMode"] = "前方一致"
    response = common_util.search_user_profile(
        pdsUserInstanceSecretName=data_copy["pdsUserInstanceSecretName"],
        searchCriteria=data_copy["searchCriteria"],
        objectIdList=data_copy["objectIdList"]
    )
    assert response == {
        "result": True,
        "count": response["count"],
        "transactionId": response["transactionId"],
        "userId": response["userId"],
        "saveDate": response["saveDate"],
        "data": response["data"],
        "imageHash": response["imageHash"]
    }
    print(response)


# No8.検索条件作成処理
# 「引数．検索条件．検索用ユーザID検索文字列」がNull以外の場合　かつ「引数．検索条件．検索用ユーザID検索モード」が "後方一致"の場合
def test_search_user_profile_case8(data):
    data_copy = data.copy()
    data_copy["searchCriteria"]["userIdStr"] = "abs"
    data_copy["searchCriteria"]["userIdMatchMode"] = "後方一致"
    response = common_util.search_user_profile(
        pdsUserInstanceSecretName=data_copy["pdsUserInstanceSecretName"],
        searchCriteria=data_copy["searchCriteria"],
        objectIdList=data_copy["objectIdList"]
    )
    assert response == {
        "result": True,
        "count": response["count"],
        "transactionId": response["transactionId"],
        "userId": response["userId"],
        "saveDate": response["saveDate"],
        "data": response["data"],
        "imageHash": response["imageHash"]
    }
    print(response)


# No9.検索条件作成処理
# 「引数．検索条件．検索用ユーザID検索文字列」がNull以外の場合　かつ「引数．検索条件．検索用ユーザID検索モード」が "部分一致"の場合
def test_search_user_profile_case9(data):
    data_copy = data.copy()
    data_copy["searchCriteria"]["userIdStr"] = "abs"
    data_copy["searchCriteria"]["userIdMatchMode"] = "部分一致"
    response = common_util.search_user_profile(
        pdsUserInstanceSecretName=data_copy["pdsUserInstanceSecretName"],
        searchCriteria=data_copy["searchCriteria"],
        objectIdList=data_copy["objectIdList"]
    )
    assert response == {
        "result": True,
        "count": response["count"],
        "transactionId": response["transactionId"],
        "userId": response["userId"],
        "saveDate": response["saveDate"],
        "data": response["data"],
        "imageHash": response["imageHash"]
    }
    print(response)


# No10.検索条件作成処理
# 「引数．objectidリスト」がNull以外の場合
def test_search_user_profile_case10(data):
    data_copy = data.copy()
    data_copy["objectIdList"] = "object"
    response = common_util.search_user_profile(
        pdsUserInstanceSecretName=data_copy["pdsUserInstanceSecretName"],
        searchCriteria=data_copy["searchCriteria"],
        objectIdList=data_copy["objectIdList"]
    )
    assert response == {
        "result": True,
        "count": response["count"],
        "transactionId": response["transactionId"],
        "userId": response["userId"],
        "saveDate": response["saveDate"],
        "data": response["data"],
        "imageHash": response["imageHash"]
    }
    print(response)


# No11.検索条件作成処理
# 「引数．objectidリスト」がNullの場合、かつ「引数．検索条件．保存データ検索文字列」がNull以外の場合
def test_search_user_profile_case11(data):
    data_copy = data.copy()
    data_copy["objectIdList"] = None
    data_copy["searchCriteria"]["dataStr"] = "abc"
    response = common_util.search_user_profile(
        pdsUserInstanceSecretName=data_copy["pdsUserInstanceSecretName"],
        searchCriteria=data_copy["searchCriteria"],
        objectIdList=data_copy["objectIdList"]
    )
    assert response == {
        "result": True,
        "count": response["count"],
        "transactionId": response["transactionId"],
        "userId": response["userId"],
        "saveDate": response["saveDate"],
        "data": response["data"],
        "imageHash": response["imageHash"]
    }
    print(response)


# No12.検索条件作成処理
# 「引数．objectidリスト」がNullの場合、かつ「引数．検索条件．保存データ検索文字列」がNull以外の場合　かつ「引数．検索条件．保存データ検索モード」が "前方一致"の場合
def test_search_user_profile_case12(data):
    data_copy = data.copy()
    data_copy["objectIdList"] = None
    data_copy["searchCriteria"]["dataStr"] = "abc"
    data_copy["searchCriteria"]["dataMatchMode"] = "前方一致"
    response = common_util.search_user_profile(
        pdsUserInstanceSecretName=data_copy["pdsUserInstanceSecretName"],
        searchCriteria=data_copy["searchCriteria"],
        objectIdList=data_copy["objectIdList"]
    )
    assert response == {
        "result": True,
        "count": response["count"],
        "transactionId": response["transactionId"],
        "userId": response["userId"],
        "saveDate": response["saveDate"],
        "data": response["data"],
        "imageHash": response["imageHash"]
    }
    print(response)


# No13.検索条件作成処理
# 「引数．objectidリスト」がNullの場合、かつ「引数．検索条件．保存データ検索文字列」がNull以外の場合　かつ「引数．検索条件．保存データ検索モード」が "後方一致"の場合
def test_search_user_profile_case13(data):
    data_copy = data.copy()
    data_copy["objectIdList"] = None
    data_copy["searchCriteria"]["dataStr"] = "abc"
    data_copy["searchCriteria"]["dataMatchMode"] = "後方一致"
    response = common_util.search_user_profile(
        pdsUserInstanceSecretName=data_copy["pdsUserInstanceSecretName"],
        searchCriteria=data_copy["searchCriteria"],
        objectIdList=data_copy["objectIdList"]
    )
    assert response == {
        "result": True,
        "count": response["count"],
        "transactionId": response["transactionId"],
        "userId": response["userId"],
        "saveDate": response["saveDate"],
        "data": response["data"],
        "imageHash": response["imageHash"]
    }
    print(response)


# No14.検索条件作成処理
# 「引数．objectidリスト」がNullの場合、かつ「引数．検索条件．保存データ検索文字列」がNull以外の場合　かつ「引数．検索条件．保存データ検索モード」が "部分一致"の場合
def test_search_user_profile_case14(data):
    data_copy = data.copy()
    data_copy["objectIdList"] = None
    data_copy["searchCriteria"]["dataStr"] = "abc"
    data_copy["searchCriteria"]["dataMatchMode"] = "部分一致"
    response = common_util.search_user_profile(
        pdsUserInstanceSecretName=data_copy["pdsUserInstanceSecretName"],
        searchCriteria=data_copy["searchCriteria"],
        objectIdList=data_copy["objectIdList"]
    )
    assert response == {
        "result": True,
        "count": response["count"],
        "transactionId": response["transactionId"],
        "userId": response["userId"],
        "saveDate": response["saveDate"],
        "data": response["data"],
        "imageHash": response["imageHash"]
    }
    print(response)


# No15.個人情報取得処理　異常系　
# 個人情報取得処理が失敗する　postgresqlのエラーが発生
def test_search_user_profile_case15(data, mocker: MockerFixture):
    data_copy = data.copy()
    mocker.patch.object(SqlConstClass, "USER_PROFILE_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    data_copy["objectIdList"] = None
    data_copy["searchCriteria"]["dataStr"] = "abc"
    data_copy["searchCriteria"]["dataMatchMode"] = "部分一致"
    with pytest.raises(PDSException) as e:
        common_util.search_user_profile(
            pdsUserInstanceSecretName=data_copy["pdsUserInstanceSecretName"],
            searchCriteria=data_copy["searchCriteria"],
            objectIdList=data_copy["objectIdList"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "991028",
        "message": logUtil.message_build(MessageConstClass.ERRORS["991028"]["message"], "991028")
    }
    print(e)


# No16.個人情報取得処理 No.4
# 個人情報取得処理が成功する
def test_search_user_profile_case16(data):
    data_copy = data.copy()
    data_copy["searchCriteria"]["fromDate"] = "2023-09-03"
    response = common_util.search_user_profile(
        pdsUserInstanceSecretName=data_copy["pdsUserInstanceSecretName"],
        searchCriteria=data_copy["searchCriteria"],
        objectIdList=data_copy["objectIdList"]
    )
    assert response == {
        "result": True,
        "count": response["count"],
        "transactionId": response["transactionId"],
        "userId": response["userId"],
        "saveDate": response["saveDate"],
        "data": response["data"],
        "imageHash": response["imageHash"]
    }
    print(response)


# No17.個人情報取得処理 No.5
# 個人情報取得処理が成功する
def test_search_user_profile_case17(data):
    data_copy = data.copy()
    data_copy["searchCriteria"]["toDate"] = "2023-08-31"
    response = common_util.search_user_profile(
        pdsUserInstanceSecretName=data_copy["pdsUserInstanceSecretName"],
        searchCriteria=data_copy["searchCriteria"],
        objectIdList=data_copy["objectIdList"]
    )
    assert response == {
        "result": True,
        "count": response["count"],
        "transactionId": response["transactionId"],
        "userId": response["userId"],
        "saveDate": response["saveDate"],
        "data": response["data"],
        "imageHash": response["imageHash"]
    }
    print(response)


# No18.個人情報取得処理 No.6
# 個人情報取得処理が成功する
def test_search_user_profile_case18(data):
    data_copy = data.copy()
    data_copy["searchCriteria"]["imageHash"] = "abs984"
    response = common_util.search_user_profile(
        pdsUserInstanceSecretName=data_copy["pdsUserInstanceSecretName"],
        searchCriteria=data_copy["searchCriteria"],
        objectIdList=data_copy["objectIdList"]
    )
    assert response == {
        "result": True,
        "count": response["count"],
        "transactionId": response["transactionId"],
        "userId": response["userId"],
        "saveDate": response["saveDate"],
        "data": response["data"],
        "imageHash": response["imageHash"]
    }
    print(response)


# No19.個人情報取得処理 No.7
# 個人情報取得処理が成功する
def test_search_user_profile_case19(data):
    data_copy = data.copy()
    data_copy["searchCriteria"]["userIdStr"] = "C00"
    data_copy["searchCriteria"]["userIdMatchMode"] = "前方一致"
    response = common_util.search_user_profile(
        pdsUserInstanceSecretName=data_copy["pdsUserInstanceSecretName"],
        searchCriteria=data_copy["searchCriteria"],
        objectIdList=data_copy["objectIdList"]
    )
    assert response == {
        "result": True,
        "count": response["count"],
        "transactionId": response["transactionId"],
        "userId": response["userId"],
        "saveDate": response["saveDate"],
        "data": response["data"],
        "imageHash": response["imageHash"]
    }
    print(response)


# No20.個人情報取得処理 No.8
# 個人情報取得処理が成功する
def test_search_user_profile_case20(data):
    data_copy = data.copy()
    data_copy["searchCriteria"]["userIdStr"] = "890"
    data_copy["searchCriteria"]["userIdMatchMode"] = "後方一致"
    response = common_util.search_user_profile(
        pdsUserInstanceSecretName=data_copy["pdsUserInstanceSecretName"],
        searchCriteria=data_copy["searchCriteria"],
        objectIdList=data_copy["objectIdList"]
    )
    assert response == {
        "result": True,
        "count": response["count"],
        "transactionId": response["transactionId"],
        "userId": response["userId"],
        "saveDate": response["saveDate"],
        "data": response["data"],
        "imageHash": response["imageHash"]
    }
    print(response)


# No21.個人情報取得処理 No.9
# 個人情報取得処理が成功する
def test_search_user_profile_case21(data):
    data_copy = data.copy()
    data_copy["searchCriteria"]["userIdStr"] = "890"
    data_copy["searchCriteria"]["userIdMatchMode"] = "部分一致"
    response = common_util.search_user_profile(
        pdsUserInstanceSecretName=data_copy["pdsUserInstanceSecretName"],
        searchCriteria=data_copy["searchCriteria"],
        objectIdList=data_copy["objectIdList"]
    )
    assert response == {
        "result": True,
        "count": response["count"],
        "transactionId": response["transactionId"],
        "userId": response["userId"],
        "saveDate": response["saveDate"],
        "data": response["data"],
        "imageHash": response["imageHash"]
    }
    print(response)


# No22.個人情報取得処理 No.10
# 個人情報取得処理が成功する
def test_search_user_profile_case22(data):
    data_copy = data.copy()
    data_copy["objectIdList"] = ["bbb", "ccc"]
    response = common_util.search_user_profile(
        pdsUserInstanceSecretName=data_copy["pdsUserInstanceSecretName"],
        searchCriteria=data_copy["searchCriteria"],
        objectIdList=data_copy["objectIdList"]
    )
    assert response == {
        "result": True,
        "count": response["count"],
        "transactionId": response["transactionId"],
        "userId": response["userId"],
        "saveDate": response["saveDate"],
        "data": response["data"],
        "imageHash": response["imageHash"]
    }
    print(response)


# No23.個人情報取得処理 No.11
# 個人情報取得処理が成功する
def test_search_user_profile_case23(data):
    data_copy = data.copy()
    data_copy["objectIdList"] = None
    data_copy["searchCriteria"]["dataStr"] = "abc"
    response = common_util.search_user_profile(
        pdsUserInstanceSecretName=data_copy["pdsUserInstanceSecretName"],
        searchCriteria=data_copy["searchCriteria"],
        objectIdList=data_copy["objectIdList"]
    )
    assert response == {
        "result": True,
        "count": response["count"],
        "transactionId": response["transactionId"],
        "userId": response["userId"],
        "saveDate": response["saveDate"],
        "data": response["data"],
        "imageHash": response["imageHash"]
    }
    print(response)


# No24.個人情報取得処理 No.12
# 個人情報取得処理が成功する
def test_search_user_profile_case24(data):
    data_copy = data.copy()
    data_copy["objectIdList"] = None
    data_copy["searchCriteria"]["dataStr"] = "abc"
    data_copy["searchCriteria"]["dataMatchMode"] = "前方一致"
    response = common_util.search_user_profile(
        pdsUserInstanceSecretName=data_copy["pdsUserInstanceSecretName"],
        searchCriteria=data_copy["searchCriteria"],
        objectIdList=data_copy["objectIdList"]
    )
    assert response == {
        "result": True,
        "count": response["count"],
        "transactionId": response["transactionId"],
        "userId": response["userId"],
        "saveDate": response["saveDate"],
        "data": response["data"],
        "imageHash": response["imageHash"]
    }
    print(response)


# No25.個人情報取得処理 No.13
# 個人情報取得処理が成功する
def test_search_user_profile_case25(data):
    data_copy = data.copy()
    data_copy["objectIdList"] = None
    data_copy["searchCriteria"]["dataStr"] = "abc"
    data_copy["searchCriteria"]["dataMatchMode"] = "後方一致"
    response = common_util.search_user_profile(
        pdsUserInstanceSecretName=data_copy["pdsUserInstanceSecretName"],
        searchCriteria=data_copy["searchCriteria"],
        objectIdList=data_copy["objectIdList"]
    )
    assert response == {
        "result": True,
        "count": response["count"],
        "transactionId": response["transactionId"],
        "userId": response["userId"],
        "saveDate": response["saveDate"],
        "data": response["data"],
        "imageHash": response["imageHash"]
    }
    print(response)


# No26.個人情報取得処理 No.14
# 個人情報取得処理が成功する
def test_search_user_profile_case26(data):
    data_copy = data.copy()
    data_copy["objectIdList"] = None
    data_copy["searchCriteria"]["dataStr"] = "abc"
    data_copy["searchCriteria"]["dataMatchMode"] = "部分一致"
    response = common_util.search_user_profile(
        pdsUserInstanceSecretName=data_copy["pdsUserInstanceSecretName"],
        searchCriteria=data_copy["searchCriteria"],
        objectIdList=data_copy["objectIdList"]
    )
    assert response == {
        "result": True,
        "count": response["count"],
        "transactionId": response["transactionId"],
        "userId": response["userId"],
        "saveDate": response["saveDate"],
        "data": response["data"],
        "imageHash": response["imageHash"]
    }
    print(response)


# No27.共通エラーチェック処理
# 共通エラーチェック処理が成功（エラー情報有り）
def test_search_user_profile_case27(data, mocker: MockerFixture):
    data_copy = data.copy()
    mocker.patch.object(SqlConstClass, "USER_PROFILE_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    data_copy["objectIdList"] = None
    data_copy["searchCriteria"]["dataStr"] = "abc"
    data_copy["searchCriteria"]["dataMatchMode"] = "部分一致"
    with pytest.raises(PDSException) as e:
        common_util.search_user_profile(
            pdsUserInstanceSecretName=data_copy["pdsUserInstanceSecretName"],
            searchCriteria=data_copy["searchCriteria"],
            objectIdList=data_copy["objectIdList"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "991028",
        "message": logUtil.message_build(MessageConstClass.ERRORS["991028"]["message"], "991028")
    }
    print(e)


# No28.終了処理
def test_search_user_profile_case28(data):
    data_copy = {
        "pdsUserInstanceSecretName": data["pdsUserInstanceSecretName"],
        "searchCriteria": {
            "userIdMatchMode": "前方一致",
            "userIdStr": "C00",
            "dataJsonKey": "data.name.firstName",
            "dataMatchMode": "前方一致",
            "dataStr": "taro",
            "imageHash": "glakjgirhul",
            "fromDate": "2023/01/01",
            "toDate": "2023/12/31"
        },
        "objectIdList": None
    }
    response = common_util.search_user_profile(
        pdsUserInstanceSecretName=data_copy["pdsUserInstanceSecretName"],
        searchCriteria=data_copy["searchCriteria"],
        objectIdList=data_copy["objectIdList"]
    )
    assert response == {
        "result": True,
        "count": response["count"],
        "transactionId": response["transactionId"],
        "userId": response["userId"],
        "saveDate": response["saveDate"],
        "data": response["data"],
        "imageHash": response["imageHash"]
    }
    print(response)
