from fastapi.testclient import TestClient
from const.sqlConst import SqlConstClass
from app import app
from fastapi import Request
import pytest
from pytest_mock.plugin import MockerFixture
from util.tokenUtil import TokenUtilClass
import util.logUtil as logUtil
from exceptionClass.PDSException import PDSException
from const.messageConst import MessageConstClass
from util.commonUtil import CommonUtilClass
from const.systemConst import SystemConstClass

client = TestClient(app)

BEARER = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0Zk9wZXJhdG9ySWQiOiJsLXRlc3QiLCJ0Zk9wZXJhdG9yTmFtZSI6Ilx1MzBlZFx1MzBiMFx1MzBhNFx1MzBmM1x1MzBjNlx1MzBiOVx1MzBjOCIsInRmT3BlcmF0b3JQYXNzd29yZFJlc2V0RmxnIjpmYWxzZSwiYWNjZXNzVG9rZW4iOiJiZGE4ZGY3OThiYzViZGZhMWZkODIyNmRiYmQ0OTMyMTY5ZmY5MjAzNWM0YzFlY2FjZjY2OGUyYzk2ZjAwZThlZTUxNTBiNGM0NTc0NjlkN2I4YmY1NzIxZDZlM2NiNzFiY2RiYzA3ODRiYzcyZWVlNjk1OGE3NTBiMWJkMWEzZWFmZWQ0OWFhNWU0ODZjYzQyZmM3OWNhMWY3MGQzZmM3Yzc0YzE5NjM3ODUzMjRhZDRhNGM0NjkxOGE4NjQ1N2ZiODE3NDU1MCIsImV4cCI6MTY2MTc0NjY3MX0.LCRjPEqKMkRQ_phaYnO7S7pd3SU_rgon-wsX14DBsPA"
ACCESS_TOKEN = "bda8df798bc5bdfa1fd8226dbbd4932169ff92035c4c1ecacf668e2c96f00e8ee5150b4c457469d7b8bf5721d6e3cb71bcdbc0784bc72eee6958a750b1bd1a3eafed49aa5e486cc42fc79ca1f70d3fc7c74c1963785324ad4a4c46918a86457fb8174550"
HEADER = {"pdsUserId": "C9876543", "pdsUserDomainName": "pds-user-create", "Content-Type": "application/json", "timeStamp": "2022/08/23 15:12:01.690", "accessToken": ACCESS_TOKEN, "Authorization": "Bearer " + BEARER}
DATA = {
    "pdsUserDomainName": HEADER["pdsUserDomainName"],
    "headerParamPdsUserId": HEADER["pdsUserId"]
}

trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
token_util = TokenUtilClass(trace_logger)

"""_summary_
@pytest.fixture
def create_auth():
    token_result = token_util.create_token_public(HEADER["pdsUserId"], HEADER["pdsUserName"], None)
    print(token_result["accessToken"], token_result["jwt"])
    yield {"accessToken": token_result["accessToken"], "jwt": token_result["jwt"]}
"""


# No1.PDSユーザドメイン検証処理_01.引数検証処理チェック　異常系　PDSユーザドメインが異常な値
def test_check_pds_user_domain_case1():
    data_copy = DATA.copy()
    data_copy["pdsUserDomainName"] = ""
    common_util = CommonUtilClass(trace_logger)
    # 指摘(Done)：pdsUserId=data_copy["pdsUserId"]⇒pdsUserId=data_copy["headerParamPdsUserId"] 横展開
    with pytest.raises(PDSException) as e:
        common_util.check_pds_user_domain(pdsUserDomainName=data_copy["pdsUserDomainName"], headerParamPdsUserId=data_copy["headerParamPdsUserId"])
    # 指摘(Done)：引数検証処理の異常時のassertはアクセストークン検証のテストケースを参考にしてください 横展開
    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "PDSユーザドメイン名")
    }
    print(e)


# No2.PDSユーザドメイン検証処理_01.引数検証処理チェック　正常系　PDSユーザドメインが正常な値
def test_check_pds_user_domain_case2():
    data_copy = DATA.copy()
    common_util = CommonUtilClass(trace_logger)
    response = common_util.check_pds_user_domain(pdsUserDomainName=data_copy["pdsUserDomainName"], headerParamPdsUserId=data_copy["headerParamPdsUserId"])
    assert response == {
        "result": True,
        # 指摘(Done)：response["pdsUserInfo"][項目名]になると思います
        "pdsUserInfo": {
            "pdsUserId": response["pdsUserInfo"]["pdsUserId"],
            "groupId": response["pdsUserInfo"]["groupId"],
            "pdsUserName": response["pdsUserInfo"]["pdsUserName"],
            "pdsUserDomainName": response["pdsUserInfo"]["pdsUserDomainName"],
            "apiKey": response["pdsUserInfo"]["apiKey"],
            "pdsUserInstanceSecretName": response["pdsUserInfo"]["pdsUserInstanceSecretName"],
            "s3ImageDataBucketName": response["pdsUserInfo"]["s3ImageDataBucketName"],
            "userProfilerKmsId": response["pdsUserInfo"]["userProfilerKmsId"],
            "tokyo_a_mongodb_secret_name": response["pdsUserInfo"]["tokyo_a_mongodb_secret_name"],
            "tokyo_c_mongodb_secret_name": response["pdsUserInfo"]["tokyo_c_mongodb_secret_name"],
            "osaka_a_mongodb_secret_name": response["pdsUserInfo"]["osaka_a_mongodb_secret_name"],
            "osaka_c_mongodb_secret_name": response["pdsUserInfo"]["osaka_c_mongodb_secret_name"],
            "validFlg": response["pdsUserInfo"]["validFlg"],
            "salesAddress": response["pdsUserInfo"]["salesAddress"],
            "downloadNoticeAddressTo": response["pdsUserInfo"]["downloadNoticeAddressTo"],
            "downloadNoticeAddressCc": response["pdsUserInfo"]["downloadNoticeAddressCc"],
            "deleteNoticeAddressTo": response["pdsUserInfo"]["deleteNoticeAddressTo"],
            "deleteNoticeAddressCc": response["pdsUserInfo"]["deleteNoticeAddressCc"],
            "credentialNoticeAddressTo": response["pdsUserInfo"]["credentialNoticeAddressTo"],
            "credentialNoticeAddressCc": response["pdsUserInfo"]["credentialNoticeAddressCc"]
        }
    }
    print(response)


# No3.PDSユーザドメイン検証処理_01.引数検証処理チェック　異常系　ヘッダパラメータPDSユーザIDが異常な値
def test_check_pds_user_domain_case3():
    data_copy = DATA.copy()
    data_copy["headerParamPdsUserId"] = ""
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.check_pds_user_domain(pdsUserDomainName=data_copy["pdsUserDomainName"], headerParamPdsUserId=data_copy["headerParamPdsUserId"])
    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "PDSユーザID")
    }
    print(e)


# No4.PDSユーザドメイン検証処理_01.引数検証処理チェック　正常系　ヘッダパラメータPDSユーザIDが正常な値
def test_check_pds_user_domain_case4():
    data_copy = DATA.copy()
    common_util = CommonUtilClass(trace_logger)
    response = common_util.check_pds_user_domain(pdsUserDomainName=data_copy["pdsUserDomainName"], headerParamPdsUserId=data_copy["headerParamPdsUserId"])
    assert response == {
        "result": True,
        "pdsUserInfo": {
            "pdsUserId": response["pdsUserInfo"]["pdsUserId"],
            "groupId": response["pdsUserInfo"]["groupId"],
            "pdsUserName": response["pdsUserInfo"]["pdsUserName"],
            "pdsUserDomainName": response["pdsUserInfo"]["pdsUserDomainName"],
            "apiKey": response["pdsUserInfo"]["apiKey"],
            "pdsUserInstanceSecretName": response["pdsUserInfo"]["pdsUserInstanceSecretName"],
            "s3ImageDataBucketName": response["pdsUserInfo"]["s3ImageDataBucketName"],
            "userProfilerKmsId": response["pdsUserInfo"]["userProfilerKmsId"],
            "tokyo_a_mongodb_secret_name": response["pdsUserInfo"]["tokyo_a_mongodb_secret_name"],
            "tokyo_c_mongodb_secret_name": response["pdsUserInfo"]["tokyo_c_mongodb_secret_name"],
            "osaka_a_mongodb_secret_name": response["pdsUserInfo"]["osaka_a_mongodb_secret_name"],
            "osaka_c_mongodb_secret_name": response["pdsUserInfo"]["osaka_c_mongodb_secret_name"],
            "validFlg": response["pdsUserInfo"]["validFlg"],
            "salesAddress": response["pdsUserInfo"]["salesAddress"],
            "downloadNoticeAddressTo": response["pdsUserInfo"]["downloadNoticeAddressTo"],
            "downloadNoticeAddressCc": response["pdsUserInfo"]["downloadNoticeAddressCc"],
            "deleteNoticeAddressTo": response["pdsUserInfo"]["deleteNoticeAddressTo"],
            "deleteNoticeAddressCc": response["pdsUserInfo"]["deleteNoticeAddressCc"],
            "credentialNoticeAddressTo": response["pdsUserInfo"]["credentialNoticeAddressTo"],
            "credentialNoticeAddressCc": response["pdsUserInfo"]["credentialNoticeAddressCc"]
        }
    }
    print(response)


# No5.PDSユーザドメイン検証処理_01.引数検証処理チェック　異常系　PDSユーザドメインが異常な値　ヘッダパラメータPDSユーザIDが異常な値
def test_check_pds_user_domain_case5():
    data_copy = DATA.copy()
    data_copy["pdsUserDomainName"] = ""
    data_copy["headerParamPdsUserId"] = ""
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.check_pds_user_domain(pdsUserDomainName=data_copy["pdsUserDomainName"], headerParamPdsUserId=data_copy["headerParamPdsUserId"])
    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "PDSユーザドメイン名")
    }
    assert e.value.args[1] == {
        "errorCode": "020016",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020016"]["message"], "PDSユーザドメイン名", "5")
    }
    assert e.value.args[2] == {
        "errorCode": "020003",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "PDSユーザドメイン名")
    }
    assert e.value.args[3] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "PDSユーザID")
    }
    assert e.value.args[4] == {
        "errorCode": "020014",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020014"]["message"], "PDSユーザID", "8")
    }
    assert e.value.args[5] == {
        "errorCode": "020003",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "PDSユーザID")
    }
    print(e)


# No6.PDSユーザドメイン検証処理_02.DB接続準備処理　異常系　接続に失敗する　設定値を異常な値に変更する
# TODO:内容確認
# 指摘(Done)：DBの接続情報の書き換えを実施する。下記のように実施
# data_copy = DATA.copy()
# common_util = CommonUtilClass(trace_logger)
# # mocker.patch("util.commonUtil.CommonUtilClass.get_secret_info").return_value = {"host": "test", "port": "test", "username": "test", "password": "test"}
# response = common_util.check_pds_user_domain(pdsUserDomainName=data_copy["pdsUserDomainName"], pdsUserId=data_copy["headerParamPdsUserId"])
# assert response == {
#     "result": False,
#     "errorInfo": response["errorInfo"]
# }
# print(response)

def test_check_pds_user_domain_case6(mocker: MockerFixture):
    data_copy = DATA.copy()
    common_util = CommonUtilClass(trace_logger)
    mocker.patch("util.commonUtil.CommonUtilClass.get_secret_info").return_value = {"host": "test", "port": "test", "username": "test", "password": "test"}
    response = common_util.check_pds_user_domain(pdsUserDomainName=data_copy["pdsUserDomainName"], headerParamPdsUserId=data_copy["headerParamPdsUserId"])
    assert response == {
        "result": False,
        "errorInfo": response["errorInfo"]
    }
    print(response)


# No7.PDSユーザドメイン検証処理_02.DB接続準備処理　正常系　接続に成功する
# 指摘(Done)： No4と同じ内容
def test_check_pds_user_domain_case7():
    data_copy = DATA.copy()
    common_util = CommonUtilClass(trace_logger)
    response = common_util.check_pds_user_domain(pdsUserDomainName=data_copy["pdsUserDomainName"], headerParamPdsUserId=data_copy["headerParamPdsUserId"])
    assert response == {
        "result": True,
        "pdsUserInfo": {
            "pdsUserId": response["pdsUserInfo"]["pdsUserId"],
            "groupId": response["pdsUserInfo"]["groupId"],
            "pdsUserName": response["pdsUserInfo"]["pdsUserName"],
            "pdsUserDomainName": response["pdsUserInfo"]["pdsUserDomainName"],
            "apiKey": response["pdsUserInfo"]["apiKey"],
            "pdsUserInstanceSecretName": response["pdsUserInfo"]["pdsUserInstanceSecretName"],
            "s3ImageDataBucketName": response["pdsUserInfo"]["s3ImageDataBucketName"],
            "userProfilerKmsId": response["pdsUserInfo"]["userProfilerKmsId"],
            "tokyo_a_mongodb_secret_name": response["pdsUserInfo"]["tokyo_a_mongodb_secret_name"],
            "tokyo_c_mongodb_secret_name": response["pdsUserInfo"]["tokyo_c_mongodb_secret_name"],
            "osaka_a_mongodb_secret_name": response["pdsUserInfo"]["osaka_a_mongodb_secret_name"],
            "osaka_c_mongodb_secret_name": response["pdsUserInfo"]["osaka_c_mongodb_secret_name"],
            "validFlg": response["pdsUserInfo"]["validFlg"],
            "salesAddress": response["pdsUserInfo"]["salesAddress"],
            "downloadNoticeAddressTo": response["pdsUserInfo"]["downloadNoticeAddressTo"],
            "downloadNoticeAddressCc": response["pdsUserInfo"]["downloadNoticeAddressCc"],
            "deleteNoticeAddressTo": response["pdsUserInfo"]["deleteNoticeAddressTo"],
            "deleteNoticeAddressCc": response["pdsUserInfo"]["deleteNoticeAddressCc"],
            "credentialNoticeAddressTo": response["pdsUserInfo"]["credentialNoticeAddressTo"],
            "credentialNoticeAddressCc": response["pdsUserInfo"]["credentialNoticeAddressCc"]
        }
    }
    print(response)


# No8.PDSユーザドメイン検証処理_03.PDSユーザ取得処理　異常系　PDSユーザ取得処理で取得結果が0件
# 指摘(None)：存在しないPDSユーザIDを指定する
def test_check_pds_user_domain_case8():
    data_copy = DATA.copy()
    data_copy["headerParamPdsUserId"] = "C1100001"
    common_util = CommonUtilClass(trace_logger)
    response = common_util.check_pds_user_domain(pdsUserDomainName=data_copy["pdsUserDomainName"], headerParamPdsUserId=data_copy["headerParamPdsUserId"])
    assert response == {
        "result": False,
        "errorInfo": response["errorInfo"]
    }
    print(response)


# No9.PDSユーザドメイン検証処理_03.PDSユーザ取得処理　異常系　postgresqlのエラーが発生
# 指摘(Done)：意味の通らないSQLへ書き換えを実施する。（存在しないテーブルを参照させる等）
# 　　　mocker.patch("const.sqlConst.SqlConstClass.PDS_USER_DOMAIN_NAME_SELECT_SQL").return_value = """ SELECT * FROM AAAAAA; """
#       response = common_util.check_pds_user_domain(pdsUserDomainName=data_copy["pdsUserDomainName"], pdsUserId=data_copy["headerParamPdsUserId"])
#       assert response == {
#           "result": False,
#           "errorInfo": response["errorInfo"]
#       }
#       print(response)
def test_check_pds_user_domain_case9(mocker: MockerFixture):
    data_copy = DATA.copy()
    common_util = CommonUtilClass(trace_logger)
    mocker.patch.object(SqlConstClass, "PDS_USER_DOMAIN_NAME_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    response = common_util.check_pds_user_domain(pdsUserDomainName=data_copy["pdsUserDomainName"], headerParamPdsUserId=data_copy["headerParamPdsUserId"])
    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "999999",
            "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
        }
    }
    print(response)


# No10.PDSユーザドメイン検証処理_03.PDSユーザ取得処理　正常系　PDSユーザ取得処理で取得結果が1件
# 指摘(Done)：No4と同じ
def test_check_pds_user_domain_case10():
    data_copy = DATA.copy()
    common_util = CommonUtilClass(trace_logger)
    response = common_util.check_pds_user_domain(pdsUserDomainName=data_copy["pdsUserDomainName"], headerParamPdsUserId=data_copy["headerParamPdsUserId"])
    assert response == {
        "result": True,
        "pdsUserInfo": {
            "pdsUserId": response["pdsUserInfo"]["pdsUserId"],
            "groupId": response["pdsUserInfo"]["groupId"],
            "pdsUserName": response["pdsUserInfo"]["pdsUserName"],
            "pdsUserDomainName": response["pdsUserInfo"]["pdsUserDomainName"],
            "apiKey": response["pdsUserInfo"]["apiKey"],
            "pdsUserInstanceSecretName": response["pdsUserInfo"]["pdsUserInstanceSecretName"],
            "s3ImageDataBucketName": response["pdsUserInfo"]["s3ImageDataBucketName"],
            "userProfilerKmsId": response["pdsUserInfo"]["userProfilerKmsId"],
            "tokyo_a_mongodb_secret_name": response["pdsUserInfo"]["tokyo_a_mongodb_secret_name"],
            "tokyo_c_mongodb_secret_name": response["pdsUserInfo"]["tokyo_c_mongodb_secret_name"],
            "osaka_a_mongodb_secret_name": response["pdsUserInfo"]["osaka_a_mongodb_secret_name"],
            "osaka_c_mongodb_secret_name": response["pdsUserInfo"]["osaka_c_mongodb_secret_name"],
            "validFlg": response["pdsUserInfo"]["validFlg"],
            "salesAddress": response["pdsUserInfo"]["salesAddress"],
            "downloadNoticeAddressTo": response["pdsUserInfo"]["downloadNoticeAddressTo"],
            "downloadNoticeAddressCc": response["pdsUserInfo"]["downloadNoticeAddressCc"],
            "deleteNoticeAddressTo": response["pdsUserInfo"]["deleteNoticeAddressTo"],
            "deleteNoticeAddressCc": response["pdsUserInfo"]["deleteNoticeAddressCc"],
            "credentialNoticeAddressTo": response["pdsUserInfo"]["credentialNoticeAddressTo"],
            "credentialNoticeAddressCc": response["pdsUserInfo"]["credentialNoticeAddressCc"]
        }
    }
    print(response)


# No11.PDSユーザドメイン検証処理_04.終了処理　変数．エラー情報がある
# 指摘(Done)：No11がない
def test_check_pds_user_domain_case11():
    data_copy = DATA.copy()
    data_copy["headerParamPdsUserId"] = "C1100001"
    common_util = CommonUtilClass(trace_logger)
    response = common_util.check_pds_user_domain(pdsUserDomainName=data_copy["pdsUserDomainName"], headerParamPdsUserId=data_copy["headerParamPdsUserId"])
    assert response == {
        "result": False,
        "errorInfo": response["errorInfo"]
    }
    print(response)


# No12.PDSユーザドメイン検証処理_04.終了処理　変数．エラー情報がない
# 指摘(Done)：No12がない
def test_check_pds_user_domain_case12():
    data_copy = DATA.copy()
    common_util = CommonUtilClass(trace_logger)
    response = common_util.check_pds_user_domain(pdsUserDomainName=data_copy["pdsUserDomainName"], headerParamPdsUserId=data_copy["headerParamPdsUserId"])
    assert response == {
        "result": True,
        "pdsUserInfo": {
            "pdsUserId": response["pdsUserInfo"]["pdsUserId"],
            "groupId": response["pdsUserInfo"]["groupId"],
            "pdsUserName": response["pdsUserInfo"]["pdsUserName"],
            "pdsUserDomainName": response["pdsUserInfo"]["pdsUserDomainName"],
            "apiKey": response["pdsUserInfo"]["apiKey"],
            "pdsUserInstanceSecretName": response["pdsUserInfo"]["pdsUserInstanceSecretName"],
            "s3ImageDataBucketName": response["pdsUserInfo"]["s3ImageDataBucketName"],
            "userProfilerKmsId": response["pdsUserInfo"]["userProfilerKmsId"],
            "tokyo_a_mongodb_secret_name": response["pdsUserInfo"]["tokyo_a_mongodb_secret_name"],
            "tokyo_c_mongodb_secret_name": response["pdsUserInfo"]["tokyo_c_mongodb_secret_name"],
            "osaka_a_mongodb_secret_name": response["pdsUserInfo"]["osaka_a_mongodb_secret_name"],
            "osaka_c_mongodb_secret_name": response["pdsUserInfo"]["osaka_c_mongodb_secret_name"],
            "validFlg": response["pdsUserInfo"]["validFlg"],
            "salesAddress": response["pdsUserInfo"]["salesAddress"],
            "downloadNoticeAddressTo": response["pdsUserInfo"]["downloadNoticeAddressTo"],
            "downloadNoticeAddressCc": response["pdsUserInfo"]["downloadNoticeAddressCc"],
            "deleteNoticeAddressTo": response["pdsUserInfo"]["deleteNoticeAddressTo"],
            "deleteNoticeAddressCc": response["pdsUserInfo"]["deleteNoticeAddressCc"],
            "credentialNoticeAddressTo": response["pdsUserInfo"]["credentialNoticeAddressTo"],
            "credentialNoticeAddressCc": response["pdsUserInfo"]["credentialNoticeAddressCc"]
        }
    }
    print(response)
