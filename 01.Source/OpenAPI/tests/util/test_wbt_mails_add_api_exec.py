from fastapi.testclient import TestClient
from util.commonUtil import CommonUtilClass
from app import app
from fastapi import Request
import pytest
# from pytest_mock.plugin import MockerFixture
from util.tokenUtil import TokenUtilClass
import util.logUtil as logUtil
# import json
from exceptionClass.PDSException import PDSException
from const.messageConst import MessageConstClass
from const.systemConst import SystemConstClass

client = TestClient(app)

BEARER = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0Zk9wZXJhdG9ySWQiOiJsLXRlc3QiLCJ0Zk9wZXJhdG9yTmFtZSI6Ilx1MzBlZFx1MzBiMFx1MzBhNFx1MzBmM1x1MzBjNlx1MzBiOVx1MzBjOCIsInRmT3BlcmF0b3JQYXNzd29yZFJlc2V0RmxnIjpmYWxzZSwiYWNjZXNzVG9rZW4iOiJiZGE4ZGY3OThiYzViZGZhMWZkODIyNmRiYmQ0OTMyMTY5ZmY5MjAzNWM0YzFlY2FjZjY2OGUyYzk2ZjAwZThlZTUxNTBiNGM0NTc0NjlkN2I4YmY1NzIxZDZlM2NiNzFiY2RiYzA3ODRiYzcyZWVlNjk1OGE3NTBiMWJkMWEzZWFmZWQ0OWFhNWU0ODZjYzQyZmM3OWNhMWY3MGQzZmM3Yzc0YzE5NjM3ODUzMjRhZDRhNGM0NjkxOGE4NjQ1N2ZiODE3NDU1MCIsImV4cCI6MTY2MTc0NjY3MX0.LCRjPEqKMkRQ_phaYnO7S7pd3SU_rgon-wsX14DBsPA"
ACCESS_TOKEN = "bda8df798bc5bdfa1fd8226dbbd4932169ff92035c4c1ecacf668e2c96f00e8ee5150b4c457469d7b8bf5721d6e3cb71bcdbc0784bc72eee6958a750b1bd1a3eafed49aa5e486cc42fc79ca1f70d3fc7c74c1963785324ad4a4c46918a86457fb8174550"
HEADER = {"pdsUserId": "C9876543", "pdsUserDomainName": "pds-user-create", "Content-Type": "application/json", "timeStamp": "2022/08/23 15:12:01.690", "accessToken": ACCESS_TOKEN, "Authorization": "Bearer " + BEARER}
DATA = {
    "repositoryType": "0",
    "attachedFilesFileName": "testSendFile.csv",
    "downloadDeadline": "2022/12/31 23:59:00.123",
    "replyDeadline": "2022/12/31 23:59:00.123",
    "comment": "コメントコメント",
    "mailAddressTo": "testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;test@abc.com",
    "mailAddressCc": "test4@lincrea.co.jp;test5@lincrea.co.jp",
    "title": "テストタイトル"
}

trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
token_util = TokenUtilClass(trace_logger)


@pytest.fixture
def create_auth():
    token_result = token_util.create_token_public(HEADER["pdsUserId"], HEADER["pdsUserName"], None)
    print(token_result["accessToken"], token_result["jwt"])
    yield {"accessToken": token_result["accessToken"], "jwt": token_result["jwt"]}


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．種別　値が設定されていない（空値）
def test_wbt_mails_add_api_exec_case1_1_1():
    data_copy = DATA.copy()
    data_copy["repositoryType"] = ""
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "種別")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．種別　文字列型ではない
def test_wbt_mails_add_api_exec_case1_1_2():
    data_copy = DATA.copy()
    data_copy["repositoryType"] = 1
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020019",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "種別", "文字列")
    }


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．種別　2桁である
def test_wbt_mails_add_api_exec_case1_1_3():
    data_copy = DATA.copy()
    data_copy["repositoryType"] = "12"
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020014",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020014"]["message"], "種別", "1")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．種別　入力規則違反している（全角）
def test_wbt_mails_add_api_exec_case1_1_4():
    data_copy = DATA.copy()
    data_copy["repositoryType"] = "１"
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020003",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "種別")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．種別　２桁である　入力規則違反している（半角英字）
def test_wbt_mails_add_api_exec_case1_1_5():
    data_copy = DATA.copy()
    data_copy["repositoryType"] = "ab"
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020014",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020014"]["message"], "種別", "1")
    }
    assert e.value.args[1] == {
        "errorCode": "020003",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "種別")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　２桁である　引数．種別　入力規則違反している（半角数字[3-9]）
def test_wbt_mails_add_api_exec_case1_1_6():
    data_copy = DATA.copy()
    data_copy["repositoryType"] = "34"
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020014",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020014"]["message"], "種別", "1")
    }
    assert e.value.args[1] == {
        "errorCode": "020003",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "種別")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．種別　入力規則違反している（半角数字[3-9]）
def test_wbt_mails_add_api_exec_case1_1_7():
    data_copy = DATA.copy()
    data_copy["repositoryType"] = "3"
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020003",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "種別")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．種別　２桁である　入力規則違反していない（[0-2]）
def test_wbt_mails_add_api_exec_case1_1_8():
    data_copy = DATA.copy()
    data_copy["repositoryType"] = "02"
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020014",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020014"]["message"], "種別", "1")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．種別　２桁である　入力規則違反している（半角数字[3-9]）
def test_wbt_mails_add_api_exec_case1_1_9():
    data_copy = DATA.copy()
    data_copy["repositoryType"] = "13"
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020014",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020014"]["message"], "種別", "1")
    }
    assert e.value.args[1] == {
        "errorCode": "020003",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "種別")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　正常系　引数．種別
def test_wbt_mails_add_api_exec_case1_1_10():
    data_copy = DATA.copy()
    data_copy["repositoryType"] = "1"
    common_util = CommonUtilClass(trace_logger)
    response = common_util.wbt_mails_add_api_exec(
        repositoryType=data_copy["repositoryType"],
        fileName=data_copy["attachedFilesFileName"],
        downloadDeadline=data_copy["downloadDeadline"],
        replyDeadline=data_copy["replyDeadline"],
        comment=data_copy["comment"],
        mailAddressTo=data_copy["mailAddressTo"],
        mailAddressCc=data_copy["mailAddressCc"],
        title=data_copy["title"]
    )
    assert response == {
        "result": True,
        "attachedFiles": [
            {
                "id": response["attachedFiles"][0]["id"],
                "fileName": response["attachedFiles"][0]["fileName"],
                "extension": response["attachedFiles"][0]["extension"]
            },
            {
                "id": response["attachedFiles"][1]["id"],
                "fileName": response["attachedFiles"][1]["fileName"],
                "extension": response["attachedFiles"][1]["extension"]
            }
        ],
        "id": response["id"]
    }
    print(response)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．送信するファイル名　値が設定されていない（空値）
def test_wbt_mails_add_api_exec_case1_2_1():
    data_copy = DATA.copy()
    data_copy["attachedFilesFileName"] = ""
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "送信するファイル名")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．送信するファイル名　文字列型ではない
def test_wbt_mails_add_api_exec_case1_2_2():
    data_copy = DATA.copy()
    data_copy["attachedFilesFileName"] = 1
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020019",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "送信するファイル名", "文字列")
    }


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．送信するファイル名　257桁である
def test_wbt_mails_add_api_exec_case1_2_3():
    data_copy = DATA.copy()
    data_copy["attachedFilesFileName"] = "1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123.csv"
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020002",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020002"]["message"], "送信するファイル名", "256")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．送信するファイル名　256桁である　入力規則違反している（禁則文字９種類を含む　\　/　:　*　?　"　<　>　|　）
def test_wbt_mails_add_api_exec_case1_2_4():
    data_copy = DATA.copy()
    data_copy["attachedFilesFileName"] = "1:*3456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345"
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020003",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "送信するファイル名")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．送信するファイル名　入力規則違反している（拡張子を除いて２５６文字を超過する）
def test_wbt_mails_add_api_exec_case1_2_5():
    data_copy = DATA.copy()
    data_copy["attachedFilesFileName"] = "12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567"
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020002",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020002"]["message"], "送信するファイル名", "256")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．送信するファイル名　入力規則違反している（拡張子が１６文字を超過する）
def test_wbt_mails_add_api_exec_case1_2_6():
    data_copy = DATA.copy()
    data_copy["attachedFilesFileName"] = "12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789.csv1234567890info"
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020002",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020002"]["message"], "送信するファイル名", "256")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．送信するファイル名　２５６桁である　入力規則違反している（ピリオドで始まる）
def test_wbt_mails_add_api_exec_case1_2_7():
    data_copy = DATA.copy()
    data_copy["attachedFilesFileName"] = ".csv"
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020014",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020014"]["message"], "送信するファイル名", "256")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．送信するファイル名　文字列型ではない　２５７桁である　入力規則違反していない
def test_wbt_mails_add_api_exec_case1_2_8():
    data_copy = DATA.copy()
    data_copy["attachedFilesFileName"] = 12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "999999",
        "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．送信するファイル名　文字列型である　２５７桁である　入力規則違反している（ピリオドで始まる）
def test_wbt_mails_add_api_exec_case1_2_9():
    data_copy = DATA.copy()
    data_copy["attachedFilesFileName"] = ".2345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567"
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020002",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020002"]["message"], "送信するファイル名", "256")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　正常系　引数．送信するファイル名
def test_wbt_mails_add_api_exec_case1_2_10():
    data_copy = DATA.copy()
    data_copy["attachedFilesFileName"] = "123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012.csv"
    common_util = CommonUtilClass(trace_logger)
    response = common_util.wbt_mails_add_api_exec(
        repositoryType=data_copy["repositoryType"],
        fileName=data_copy["attachedFilesFileName"],
        downloadDeadline=data_copy["downloadDeadline"],
        replyDeadline=data_copy["replyDeadline"],
        comment=data_copy["comment"],
        mailAddressTo=data_copy["mailAddressTo"],
        mailAddressCc=data_copy["mailAddressCc"],
        title=data_copy["title"]
    )
    assert response == {
        "result": True,
        "attachedFiles": [
            {
                "id": response["attachedFiles"][0]["id"],
                "fileName": response["attachedFiles"][0]["fileName"],
                "extension": response["attachedFiles"][0]["extension"]
            },
            {
                "id": response["attachedFiles"][1]["id"],
                "fileName": response["attachedFiles"][1]["fileName"],
                "extension": response["attachedFiles"][1]["extension"]
            }
        ],
        "id": response["id"]
    }
    print(response)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．引き取り期限　値が設定されていない（空値）
def test_wbt_mails_add_api_exec_case1_3_1():
    data_copy = DATA.copy()
    data_copy["downloadDeadline"] = ""
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "引き取り期限")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．引き取り期限　文字列型ではない
def test_wbt_mails_add_api_exec_case1_3_2():
    data_copy = DATA.copy()
    data_copy["downloadDeadline"] = 1
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020019",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "引き取り期限", "文字列")
    }


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．引き取り期限　22桁である　入力規則違反していない（YYYY-MM-DDThh:mm:ss.sssZ）
def test_wbt_mails_add_api_exec_case1_3_3():
    data_copy = DATA.copy()
    data_copy["downloadDeadline"] = "2022-09-30 23:59:59.00"
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020014",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020014"]["message"], "引き取り期限", "23")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．引き取り期限　23桁である　入力規則違反している（YYYY-MMがYYY-MMM）
def test_wbt_mails_add_api_exec_case1_3_4():
    data_copy = DATA.copy()
    data_copy["downloadDeadline"] = "202-209-30 23:59:59.000"
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020003",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "引き取り期限", "23")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．引き取り期限　24桁である　入力規則違反している（hh:mmがhhh:m）
def test_wbt_mails_add_api_exec_case1_3_5():
    data_copy = DATA.copy()
    data_copy["downloadDeadline"] = "2022-09-30 235:59:59.000"
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020014",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020014"]["message"], "引き取り期限", "23")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．引き取り期限　文字列型ではない　24桁である　入力規則違反している（hh:mmがhhh:m）
# TODO:テストデータについて確認
def test_wbt_mails_add_api_exec_case1_3_6():
    data_copy = DATA.copy()
    data_copy["downloadDeadline"] = "2022-09-30 235:59:59.000"
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020014",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020014"]["message"], "引き取り期限", "23")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．引き取り期限　文字列型ではない　23桁である　入力規則違反している（hh:mmがhhh:m）
def test_wbt_mails_add_api_exec_case1_3_7():
    data_copy = DATA.copy()
    data_copy["downloadDeadline"] = "2022-09-30 235:9:59.000"
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020003",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "引き取り期限", "23")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．引き取り期限　文字列型ではない　24桁である　入力規則違反していない（YYYY-MM-DDThh:mm:ss.sssZ）
def test_wbt_mails_add_api_exec_case1_3_8():
    data_copy = DATA.copy()
    data_copy["downloadDeadline"] = "2022-09-30 23:59:59.0000"
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020014",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020014"]["message"], "引き取り期限", "23")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．引き取り期限　文字列型である　24桁である　入力規則違反している（hh:mmがhhh:m）
def test_wbt_mails_add_api_exec_case1_3_9():
    data_copy = DATA.copy()
    data_copy["downloadDeadline"] = "2022-09-30 235:9:59.0000"
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020014",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020014"]["message"], "引き取り期限", "23")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　正常系　引数．引き取り期限
def test_wbt_mails_add_api_exec_case1_3_10():
    data_copy = DATA.copy()
    data_copy["downloadDeadline"] = "2022/12/31 23:59:00.123"
    common_util = CommonUtilClass(trace_logger)
    response = common_util.wbt_mails_add_api_exec(
        repositoryType=data_copy["repositoryType"],
        fileName=data_copy["attachedFilesFileName"],
        downloadDeadline=data_copy["downloadDeadline"],
        replyDeadline=data_copy["replyDeadline"],
        comment=data_copy["comment"],
        mailAddressTo=data_copy["mailAddressTo"],
        mailAddressCc=data_copy["mailAddressCc"],
        title=data_copy["title"]
    )
    assert response == {
        "result": True,
        "attachedFiles": [
            {
                "id": response["attachedFiles"][0]["id"],
                "fileName": response["attachedFiles"][0]["fileName"],
                "extension": response["attachedFiles"][0]["extension"]
            },
            {
                "id": response["attachedFiles"][1]["id"],
                "fileName": response["attachedFiles"][1]["fileName"],
                "extension": response["attachedFiles"][1]["extension"]
            }
        ],
        "id": response["id"]
    }
    print(response)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．返信期限　文字列型ではない
def test_wbt_mails_add_api_exec_case1_4_1():
    data_copy = DATA.copy()
    data_copy["replyDeadline"] = 1
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020019",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "返信期限", "文字列")
    }


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．返信期限　22桁である　入力規則違反していない（YYYY-MM-DDThh:mm:ss.sssZ）
def test_wbt_mails_add_api_exec_case1_4_2():
    data_copy = DATA.copy()
    data_copy["replyDeadline"] = "2022-09-30 23:59:59.00"
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020014",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020014"]["message"], "返信期限", "23")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．返信期限　23桁である　入力規則違反している（YYYY-MMがYYY-MMM）
def test_wbt_mails_add_api_exec_case1_4_3():
    data_copy = DATA.copy()
    data_copy["replyDeadline"] = "202-209-30 23:59:59.000"
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020003",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "返信期限", "23")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．返信期限　24桁である　入力規則違反している（hh:mmがhhh:m）
def test_wbt_mails_add_api_exec_case1_4_4():
    data_copy = DATA.copy()
    data_copy["replyDeadline"] = "2022-09-30 235:59:59.000"
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020014",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020014"]["message"], "返信期限", "23")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．返信期限　文字列型ではない　24桁である　入力規則違反している（hh:mmがhhh:m）
# TODO:テストデータについて確認
def test_wbt_mails_add_api_exec_case1_4_5():
    data_copy = DATA.copy()
    data_copy["replyDeadline"] = "2022-09-30 235:59:59.000"
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020014",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020014"]["message"], "返信期限", "23")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．返信期限　文字列型ではない　23桁である　入力規則違反している（hh:mmがhhh:m）
def test_wbt_mails_add_api_exec_case1_4_6():
    data_copy = DATA.copy()
    data_copy["replyDeadline"] = "2022-09-30 235:9:59.000"
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020003",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "返信期限", "23")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．返信期限　文字列型ではない　24桁である　入力規則違反していない（YYYY-MM-DDThh:mm:ss.sssZ）
def test_wbt_mails_add_api_exec_case1_4_7():
    data_copy = DATA.copy()
    data_copy["replyDeadline"] = "2022-09-30 23:59:59.0000"
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020014",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020014"]["message"], "返信期限", "23")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．返信期限　文字列型である　24桁である　入力規則違反している（hh:mmがhhh:m）
def test_wbt_mails_add_api_exec_case1_4_8():
    data_copy = DATA.copy()
    data_copy["replyDeadline"] = "2022-09-30 235:9:59.0000"
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020014",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020014"]["message"], "返信期限", "23")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　正常系　引数．返信期限
def test_wbt_mails_add_api_exec_case1_4_9():
    data_copy = DATA.copy()
    data_copy["replyDeadline"] = "2022/12/31 23:59:00.123"
    common_util = CommonUtilClass(trace_logger)
    response = common_util.wbt_mails_add_api_exec(
        repositoryType=data_copy["repositoryType"],
        fileName=data_copy["attachedFilesFileName"],
        downloadDeadline=data_copy["downloadDeadline"],
        replyDeadline=data_copy["replyDeadline"],
        comment=data_copy["comment"],
        mailAddressTo=data_copy["mailAddressTo"],
        mailAddressCc=data_copy["mailAddressCc"],
        title=data_copy["title"]
    )
    assert response == {
        "result": True,
        "attachedFiles": [
            {
                "id": response["attachedFiles"][0]["id"],
                "fileName": response["attachedFiles"][0]["fileName"],
                "extension": response["attachedFiles"][0]["extension"]
            },
            {
                "id": response["attachedFiles"][1]["id"],
                "fileName": response["attachedFiles"][1]["fileName"],
                "extension": response["attachedFiles"][1]["extension"]
            }
        ],
        "id": response["id"]
    }
    print(response)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．メッセージ　値が設定されていない（空値）
def test_wbt_mails_add_api_exec_case1_5_1():
    data_copy = DATA.copy()
    data_copy["comment"] = ""
    common_util = CommonUtilClass(trace_logger)
    response = common_util.wbt_mails_add_api_exec(
        repositoryType=data_copy["repositoryType"],
        fileName=data_copy["attachedFilesFileName"],
        downloadDeadline=data_copy["downloadDeadline"],
        replyDeadline=data_copy["replyDeadline"],
        comment=data_copy["comment"],
        mailAddressTo=data_copy["mailAddressTo"],
        mailAddressCc=data_copy["mailAddressCc"],
        title=data_copy["title"]
    )
    assert response == {
        "result": True,
        "attachedFiles": [
            {
                "id": response["attachedFiles"][0]["id"],
                "fileName": response["attachedFiles"][0]["fileName"],
                "extension": response["attachedFiles"][0]["extension"]
            },
            {
                "id": response["attachedFiles"][1]["id"],
                "fileName": response["attachedFiles"][1]["fileName"],
                "extension": response["attachedFiles"][1]["extension"]
            }
        ],
        "id": response["id"]
    }
    print(response)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．メッセージ　文字列型ではない
def test_wbt_mails_add_api_exec_case1_5_2():
    data_copy = DATA.copy()
    data_copy["comment"] = 1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020019",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "メッセージ", "文字列")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．メッセージ　文字列型である　４００１桁である
def test_wbt_mails_add_api_exec_case1_5_3():
    data_copy = DATA.copy()
    data_copy["comment"] = "12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901"
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020002",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020002"]["message"], "メッセージ", "4000")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．メッセージ　文字列型である　４００１桁である　入力規則違反している（桁数が４００１桁である）
def test_wbt_mails_add_api_exec_case1_5_4():
    data_copy = DATA.copy()
    data_copy["comment"] = "12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901"
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020002",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020002"]["message"], "メッセージ", "4000")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．メッセージ　文字列型ではない　４００１桁である　入力規則違反している（桁数が４００１桁である）
def test_wbt_mails_add_api_exec_case1_5_5():
    data_copy = DATA.copy()
    data_copy["comment"] = 12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020019",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "メッセージ", "文字列")
    }
    assert e.value.args[1] == {
        "errorCode": "020002",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020002"]["message"], "メッセージ", "4000")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　正常系　引数．メッセージ
def test_wbt_mails_add_api_exec_case1_5_6():
    data_copy = DATA.copy()
    common_util = CommonUtilClass(trace_logger)
    response = common_util.wbt_mails_add_api_exec(
        repositoryType=data_copy["repositoryType"],
        fileName=data_copy["attachedFilesFileName"],
        downloadDeadline=data_copy["downloadDeadline"],
        replyDeadline=data_copy["replyDeadline"],
        comment=data_copy["comment"],
        mailAddressTo=data_copy["mailAddressTo"],
        mailAddressCc=data_copy["mailAddressCc"],
        title=data_copy["title"]
    )
    assert response == {
        "result": True,
        "attachedFiles": [
            {
                "id": response["attachedFiles"][0]["id"],
                "fileName": response["attachedFiles"][0]["fileName"],
                "extension": response["attachedFiles"][0]["extension"]
            },
            {
                "id": response["attachedFiles"][1]["id"],
                "fileName": response["attachedFiles"][1]["fileName"],
                "extension": response["attachedFiles"][1]["extension"]
            }
        ],
        "id": response["id"]
    }
    print(response)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．Toメールアドレス　値が設定されていない（空値）
def test_wbt_mails_add_api_exec_case1_6_1():
    data_copy = DATA.copy()
    data_copy["mailAddressTo"] = ""
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "Toメールアドレス")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．Toメールアドレス　文字列型ではない　5桁である
def test_wbt_mails_add_api_exec_case1_6_2():
    data_copy = DATA.copy()
    data_copy["mailAddressTo"] = 12345
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020019",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "Toメールアドレス", "文字列")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．Toメールアドレス　文字列型である　4桁である　入力規則違反していない（入力規則※１）
def test_wbt_mails_add_api_exec_case1_6_3():
    data_copy = DATA.copy()
    data_copy["mailAddressTo"] = "a@bc"
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020016",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020016"]["message"], "Toメールアドレス", "5")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．Toメールアドレス　文字列型である　513桁である　入力規則違反していない（入力規則※１）
def test_wbt_mails_add_api_exec_case1_6_4():
    data_copy = DATA.copy()
    data_copy["mailAddressTo"] = "testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;test@aaaabc.com"
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020002",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020002"]["message"], "Toメールアドレス", "512")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．Toメールアドレス　文字列型である　512桁である　入力規則違反している（@を含まない）
def test_wbt_mails_add_api_exec_case1_6_5():
    data_copy = DATA.copy()
    data_copy["mailAddressTo"] = "testmailabcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;test@abc.com"
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020003",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "Toメールアドレス")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．Toメールアドレス　文字列型である　513桁である　入力規則違反している（全角）
def test_wbt_mails_add_api_exec_case1_6_6():
    data_copy = DATA.copy()
    data_copy["mailAddressTo"] = "Ｔstmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;test@abc.com"
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020003",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "Toメールアドレス", "512")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．Toメールアドレス　文字列型である　4桁である　入力規則違反している（半角記号※２）
def test_wbt_mails_add_api_exec_case1_6_7():
    data_copy = DATA.copy()
    data_copy["mailAddressTo"] = "!#$%"
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020016",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020016"]["message"], "Toメールアドレス", "5")
    }
    assert e.value.args[1] == {
        "errorCode": "020003",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "Toメールアドレス")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．Toメールアドレス　文字列型である　4桁である　入力規則違反している（半角記号※２）
def test_wbt_mails_add_api_exec_case1_6_8():
    data_copy = DATA.copy()
    data_copy["mailAddressTo"] = "!#$%"
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020016",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020016"]["message"], "Toメールアドレス", "5")
    }
    assert e.value.args[1] == {
        "errorCode": "020003",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "Toメールアドレス")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．Toメールアドレス　文字列型である　513桁である　入力規則違反していない（入力規則※１）
def test_wbt_mails_add_api_exec_case1_6_9():
    data_copy = DATA.copy()
    data_copy["mailAddressTo"] = "testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;test@abcaaa.com"
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020002",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020002"]["message"], "Toメールアドレス", "512")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　正常系　引数．Toメールアドレス　文字列型である　5桁である　入力規則違反していない（入力規則※１）
def test_wbt_mails_add_api_exec_case1_6_10():
    data_copy = DATA.copy()
    data_copy["mailAddressTo"] = "t@a.b"
    common_util = CommonUtilClass(trace_logger)
    response = common_util.wbt_mails_add_api_exec(
        repositoryType=data_copy["repositoryType"],
        fileName=data_copy["attachedFilesFileName"],
        downloadDeadline=data_copy["downloadDeadline"],
        replyDeadline=data_copy["replyDeadline"],
        comment=data_copy["comment"],
        mailAddressTo=data_copy["mailAddressTo"],
        mailAddressCc=data_copy["mailAddressCc"],
        title=data_copy["title"]
    )
    assert response == {
        "result": True,
        "attachedFiles": [
            {
                "id": response["attachedFiles"][0]["id"],
                "fileName": response["attachedFiles"][0]["fileName"],
                "extension": response["attachedFiles"][0]["extension"]
            },
            {
                "id": response["attachedFiles"][1]["id"],
                "fileName": response["attachedFiles"][1]["fileName"],
                "extension": response["attachedFiles"][1]["extension"]
            }
        ],
        "id": response["id"]
    }
    print(response)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　正常系　引数．Toメールアドレス　文字列型である　5桁である　入力規則違反していない（入力規則※１）
# TODO:case1_6_10と同様
def test_wbt_mails_add_api_exec_case1_6_11():
    data_copy = DATA.copy()
    data_copy["mailAddressTo"] = "t@a.b"
    common_util = CommonUtilClass(trace_logger)
    response = common_util.wbt_mails_add_api_exec(
        repositoryType=data_copy["repositoryType"],
        fileName=data_copy["attachedFilesFileName"],
        downloadDeadline=data_copy["downloadDeadline"],
        replyDeadline=data_copy["replyDeadline"],
        comment=data_copy["comment"],
        mailAddressTo=data_copy["mailAddressTo"],
        mailAddressCc=data_copy["mailAddressCc"],
        title=data_copy["title"]
    )
    assert response == {
        "result": True,
        "attachedFiles": [
            {
                "id": response["attachedFiles"][0]["id"],
                "fileName": response["attachedFiles"][0]["fileName"],
                "extension": response["attachedFiles"][0]["extension"]
            },
            {
                "id": response["attachedFiles"][1]["id"],
                "fileName": response["attachedFiles"][1]["fileName"],
                "extension": response["attachedFiles"][1]["extension"]
            }
        ],
        "id": response["id"]
    }
    print(response)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　正常系　引数．Toメールアドレス　文字列型である　512桁である　入力規則違反していない（入力規則※１）
def test_wbt_mails_add_api_exec_case1_6_12():
    data_copy = DATA.copy()
    common_util = CommonUtilClass(trace_logger)
    response = common_util.wbt_mails_add_api_exec(
        repositoryType=data_copy["repositoryType"],
        fileName=data_copy["attachedFilesFileName"],
        downloadDeadline=data_copy["downloadDeadline"],
        replyDeadline=data_copy["replyDeadline"],
        comment=data_copy["comment"],
        mailAddressTo=data_copy["mailAddressTo"],
        mailAddressCc=data_copy["mailAddressCc"],
        title=data_copy["title"]
    )
    assert response == {
        "result": True,
        "attachedFiles": [
            {
                "id": response["attachedFiles"][0]["id"],
                "fileName": response["attachedFiles"][0]["fileName"],
                "extension": response["attachedFiles"][0]["extension"]
            },
            {
                "id": response["attachedFiles"][1]["id"],
                "fileName": response["attachedFiles"][1]["fileName"],
                "extension": response["attachedFiles"][1]["extension"]
            }
        ],
        "id": response["id"]
    }
    print(response)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．Ccメールアドレス　文字列型ではない　5桁である
def test_wbt_mails_add_api_exec_case1_7_1():
    data_copy = DATA.copy()
    data_copy["mailAddressCc"] = 12345
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020019",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "Ccメールアドレス", "文字列")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．Ccメールアドレス　文字列型である　4桁である　入力規則違反していない（入力規則※１）
def test_wbt_mails_add_api_exec_case1_7_2():
    data_copy = DATA.copy()
    data_copy["mailAddressCc"] = "a@bc"
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020016",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020016"]["message"], "Ccメールアドレス", "5")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．Ccメールアドレス　文字列型である　513桁である　入力規則違反していない（入力規則※１）
def test_wbt_mails_add_api_exec_case1_7_3():
    data_copy = DATA.copy()
    data_copy["mailAddressCc"] = "testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;test@abcaaa.com"
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020002",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020002"]["message"], "Ccメールアドレス", "512")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．Ccメールアドレス　文字列型である　512桁である　入力規則違反している（@を含まない）
def test_wbt_mails_add_api_exec_case1_7_4():
    data_copy = DATA.copy()
    data_copy["mailAddressCc"] = "testmailabcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;test@abc.com"
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020003",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "Ccメールアドレス")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．Ccメールアドレス　文字列型である　513桁である　入力規則違反している（全角）
def test_wbt_mails_add_api_exec_case1_7_5():
    data_copy = DATA.copy()
    data_copy["mailAddressCc"] = "Ｔstmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;test@abcaaa.com"
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020002",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020002"]["message"], "Ccメールアドレス", "512")
    }
    assert e.value.args[1] == {
        "errorCode": "020003",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "Ccメールアドレス")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．Ccメールアドレス　文字列型である　4桁である　入力規則違反している（半角記号※２）
def test_wbt_mails_add_api_exec_case1_7_6():
    data_copy = DATA.copy()
    data_copy["mailAddressCc"] = "!#$%"
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020016",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020016"]["message"], "Ccメールアドレス", "5")
    }
    assert e.value.args[1] == {
        "errorCode": "020003",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "Ccメールアドレス")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．Ccメールアドレス　文字列型である　4桁である　入力規則違反している（半角記号※２）
def test_wbt_mails_add_api_exec_case1_7_7():
    data_copy = DATA.copy()
    data_copy["mailAddressCc"] = "!#$%"
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020016",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020016"]["message"], "Ccメールアドレス", "5")
    }
    assert e.value.args[1] == {
        "errorCode": "020003",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "Ccメールアドレス")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．Ccメールアドレス　文字列型である　513桁である　入力規則違反していない（入力規則※１）
def test_wbt_mails_add_api_exec_case1_7_8():
    data_copy = DATA.copy()
    data_copy["mailAddressCc"] = "testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;testmail@abcd.co.jp;test@abcaaa.com"
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020002",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020002"]["message"], "Ccメールアドレス", "512")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　正常系　引数．Ccメールアドレス　文字列型である　5桁である　入力規則違反していない（入力規則※１）
def test_wbt_mails_add_api_exec_case1_7_9():
    data_copy = DATA.copy()
    data_copy["mailAddressCc"] = "t@a.b"
    common_util = CommonUtilClass(trace_logger)
    response = common_util.wbt_mails_add_api_exec(
        repositoryType=data_copy["repositoryType"],
        fileName=data_copy["attachedFilesFileName"],
        downloadDeadline=data_copy["downloadDeadline"],
        replyDeadline=data_copy["replyDeadline"],
        comment=data_copy["comment"],
        mailAddressTo=data_copy["mailAddressTo"],
        mailAddressCc=data_copy["mailAddressCc"],
        title=data_copy["title"]
    )
    assert response == {
        "result": True,
        "attachedFiles": [
            {
                "id": response["attachedFiles"][0]["id"],
                "fileName": response["attachedFiles"][0]["fileName"],
                "extension": response["attachedFiles"][0]["extension"]
            },
            {
                "id": response["attachedFiles"][1]["id"],
                "fileName": response["attachedFiles"][1]["fileName"],
                "extension": response["attachedFiles"][1]["extension"]
            }
        ],
        "id": response["id"]
    }
    print(response)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　正常系　引数．Ccメールアドレス　文字列型である　5桁である　入力規則違反していない（入力規則※１）
# TODO:case1_7_10と同様
def test_wbt_mails_add_api_exec_case1_7_10():
    data_copy = DATA.copy()
    data_copy["mailAddressCc"] = "t@a.b"
    common_util = CommonUtilClass(trace_logger)
    response = common_util.wbt_mails_add_api_exec(
        repositoryType=data_copy["repositoryType"],
        fileName=data_copy["attachedFilesFileName"],
        downloadDeadline=data_copy["downloadDeadline"],
        replyDeadline=data_copy["replyDeadline"],
        comment=data_copy["comment"],
        mailAddressTo=data_copy["mailAddressTo"],
        mailAddressCc=data_copy["mailAddressCc"],
        title=data_copy["title"]
    )
    assert response == {
        "result": True,
        "attachedFiles": [
            {
                "id": response["attachedFiles"][0]["id"],
                "fileName": response["attachedFiles"][0]["fileName"],
                "extension": response["attachedFiles"][0]["extension"]
            },
            {
                "id": response["attachedFiles"][1]["id"],
                "fileName": response["attachedFiles"][1]["fileName"],
                "extension": response["attachedFiles"][1]["extension"]
            }
        ],
        "id": response["id"]
    }
    print(response)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　正常系　引数．Ccメールアドレス　文字列型である　512桁である　入力規則違反していない（入力規則※１）
def test_wbt_mails_add_api_exec_case1_7_11():
    data_copy = DATA.copy()
    common_util = CommonUtilClass(trace_logger)
    response = common_util.wbt_mails_add_api_exec(
        repositoryType=data_copy["repositoryType"],
        fileName=data_copy["attachedFilesFileName"],
        downloadDeadline=data_copy["downloadDeadline"],
        replyDeadline=data_copy["replyDeadline"],
        comment=data_copy["comment"],
        mailAddressTo=data_copy["mailAddressTo"],
        mailAddressCc=data_copy["mailAddressCc"],
        title=data_copy["title"]
    )
    assert response == {
        "result": True,
        "attachedFiles": [
            {
                "id": response["attachedFiles"][0]["id"],
                "fileName": response["attachedFiles"][0]["fileName"],
                "extension": response["attachedFiles"][0]["extension"]
            },
            {
                "id": response["attachedFiles"][1]["id"],
                "fileName": response["attachedFiles"][1]["fileName"],
                "extension": response["attachedFiles"][1]["extension"]
            }
        ],
        "id": response["id"]
    }
    print(response)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．メール件名　値が設定されていない（空値）
def test_wbt_mails_add_api_exec_case1_8_1():
    data_copy = DATA.copy()
    data_copy["title"] = ""
    common_util = CommonUtilClass(trace_logger)
    response = common_util.wbt_mails_add_api_exec(
        repositoryType=data_copy["repositoryType"],
        fileName=data_copy["attachedFilesFileName"],
        downloadDeadline=data_copy["downloadDeadline"],
        replyDeadline=data_copy["replyDeadline"],
        comment=data_copy["comment"],
        mailAddressTo=data_copy["mailAddressTo"],
        mailAddressCc=data_copy["mailAddressCc"],
        title=data_copy["title"]
    )
    assert response == {
        "result": True,
        "attachedFiles": [
            {
                "id": response["attachedFiles"][0]["id"],
                "fileName": response["attachedFiles"][0]["fileName"],
                "extension": response["attachedFiles"][0]["extension"]
            },
            {
                "id": response["attachedFiles"][1]["id"],
                "fileName": response["attachedFiles"][1]["fileName"],
                "extension": response["attachedFiles"][1]["extension"]
            }
        ],
        "id": response["id"]
    }
    print(response)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．メール件名　文字列型ではない
def test_wbt_mails_add_api_exec_case1_8_2():
    data_copy = DATA.copy()
    data_copy["title"] = 1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020019",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "メール件名", "文字列")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．メール件名　文字列型である　257桁である
def test_wbt_mails_add_api_exec_case1_8_3():
    data_copy = DATA.copy()
    data_copy["title"] = "12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567"
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020002",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020002"]["message"], "メール件名", "256")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．メール件名　文字列型である　257桁である
# case1_8_3と同様
def test_wbt_mails_add_api_exec_case1_8_4():
    data_copy = DATA.copy()
    data_copy["title"] = "12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567"
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020002",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020002"]["message"], "メール件名", "256")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．メール件名　文字列型ではない　257桁である
def test_wbt_mails_add_api_exec_case1_8_5():
    data_copy = DATA.copy()
    data_copy["title"] = 12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020019",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "メール件名", "文字列")
    }
    assert e.value.args[1] == {
        "errorCode": "020002",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020002"]["message"], "メール件名", "256")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　異常系　引数．メール件名　文字列型ではない　256桁である
def test_wbt_mails_add_api_exec_case1_8_6():
    data_copy = DATA.copy()
    data_copy["title"] = 12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.wbt_mails_add_api_exec(
            repositoryType=data_copy["repositoryType"],
            fileName=data_copy["attachedFilesFileName"],
            downloadDeadline=data_copy["downloadDeadline"],
            replyDeadline=data_copy["replyDeadline"],
            comment=data_copy["comment"],
            mailAddressTo=data_copy["mailAddressTo"],
            mailAddressCc=data_copy["mailAddressCc"],
            title=data_copy["title"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020019",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "メール件名", "文字列")
    }
    print(e)


# No1.WBT新規メール情報登録API実行_01.引数検証処理チェック　正常系　引数．メール件名　文字列型である　256桁である
def test_wbt_mails_add_api_exec_case1_8_7():
    data_copy = DATA.copy()
    common_util = CommonUtilClass(trace_logger)
    response = common_util.wbt_mails_add_api_exec(
        repositoryType=data_copy["repositoryType"],
        fileName=data_copy["attachedFilesFileName"],
        downloadDeadline=data_copy["downloadDeadline"],
        replyDeadline=data_copy["replyDeadline"],
        comment=data_copy["comment"],
        mailAddressTo=data_copy["mailAddressTo"],
        mailAddressCc=data_copy["mailAddressCc"],
        title=data_copy["title"]
    )
    assert response == {
        "result": True,
        "attachedFiles": [
            {
                "id": response["attachedFiles"][0]["id"],
                "fileName": response["attachedFiles"][0]["fileName"],
                "extension": response["attachedFiles"][0]["extension"]
            },
            {
                "id": response["attachedFiles"][1]["id"],
                "fileName": response["attachedFiles"][1]["fileName"],
                "extension": response["attachedFiles"][1]["extension"]
            }
        ],
        "id": response["id"]
    }
    print(response)


# No2.WBT新規メール情報登録API実行_02.メールアドレスリスト作成処理　正常系　Toメールアドレスが1件（セミコロンで区切りなし）
def test_wbt_mails_add_api_exec_case2():
    data_copy = DATA.copy()
    data_copy["mailAddressTo"] = "test1@lincrea.co.jp"
    common_util = CommonUtilClass(trace_logger)
    response = common_util.wbt_mails_add_api_exec(
        repositoryType=data_copy["repositoryType"],
        fileName=data_copy["attachedFilesFileName"],
        downloadDeadline=data_copy["downloadDeadline"],
        replyDeadline=data_copy["replyDeadline"],
        comment=data_copy["comment"],
        mailAddressTo=data_copy["mailAddressTo"],
        mailAddressCc=data_copy["mailAddressCc"],
        title=data_copy["title"]
    )
    assert response == {
        "result": True,
        "attachedFiles": [
            {
                "id": response["attachedFiles"][0]["id"],
                "fileName": response["attachedFiles"][0]["fileName"],
                "extension": response["attachedFiles"][0]["extension"]
            },
            {
                "id": response["attachedFiles"][1]["id"],
                "fileName": response["attachedFiles"][1]["fileName"],
                "extension": response["attachedFiles"][1]["extension"]
            }
        ],
        "id": response["id"]
    }
    print(response)


# No3.WBT新規メール情報登録API実行_02.メールアドレスリスト作成処理　正常系　Toメールアドレスが2件（セミコロンで区切りあり）
def test_wbt_mails_add_api_exec_case3():
    data_copy = DATA.copy()
    data_copy["mailAddressTo"] = "test1@lincrea.co.jp;test2@lincrea.co.jp"
    common_util = CommonUtilClass(trace_logger)
    response = common_util.wbt_mails_add_api_exec(
        repositoryType=data_copy["repositoryType"],
        fileName=data_copy["attachedFilesFileName"],
        downloadDeadline=data_copy["downloadDeadline"],
        replyDeadline=data_copy["replyDeadline"],
        comment=data_copy["comment"],
        mailAddressTo=data_copy["mailAddressTo"],
        mailAddressCc=data_copy["mailAddressCc"],
        title=data_copy["title"]
    )
    assert response == {
        "result": True,
        "attachedFiles": [
            {
                "id": response["attachedFiles"][0]["id"],
                "fileName": response["attachedFiles"][0]["fileName"],
                "extension": response["attachedFiles"][0]["extension"]
            },
            {
                "id": response["attachedFiles"][1]["id"],
                "fileName": response["attachedFiles"][1]["fileName"],
                "extension": response["attachedFiles"][1]["extension"]
            }
        ],
        "id": response["id"]
    }
    print(response)


# No4.WBT新規メール情報登録API実行_02.メールアドレスリスト作成処理　正常系　Ccメールアドレスが設定されていない
def test_wbt_mails_add_api_exec_case4():
    data_copy = DATA.copy()
    data_copy["mailAddressTo"] = "test1@lincrea.co.jp"
    data_copy["mailAddressCc"] = ""
    common_util = CommonUtilClass(trace_logger)
    response = common_util.wbt_mails_add_api_exec(
        repositoryType=data_copy["repositoryType"],
        fileName=data_copy["attachedFilesFileName"],
        downloadDeadline=data_copy["downloadDeadline"],
        replyDeadline=data_copy["replyDeadline"],
        comment=data_copy["comment"],
        mailAddressTo=data_copy["mailAddressTo"],
        mailAddressCc=data_copy["mailAddressCc"],
        title=data_copy["title"]
    )
    assert response == {
        "result": True,
        "attachedFiles": [
            {
                "id": response["attachedFiles"][0]["id"],
                "fileName": response["attachedFiles"][0]["fileName"],
                "extension": response["attachedFiles"][0]["extension"]
            },
            {
                "id": response["attachedFiles"][1]["id"],
                "fileName": response["attachedFiles"][1]["fileName"],
                "extension": response["attachedFiles"][1]["extension"]
            }
        ],
        "id": response["id"]
    }
    print(response)


# No5.WBT新規メール情報登録API実行_02.メールアドレスリスト作成処理　正常系　Ccメールアドレスが1件（セミコロンで区切りなし）
def test_wbt_mails_add_api_exec_case5():
    data_copy = DATA.copy()
    data_copy["mailAddressTo"] = "test1@lincrea.co.jp"
    data_copy["mailAddressCc"] = "test2@lincrea.co.jp"
    common_util = CommonUtilClass(trace_logger)
    response = common_util.wbt_mails_add_api_exec(
        repositoryType=data_copy["repositoryType"],
        fileName=data_copy["attachedFilesFileName"],
        downloadDeadline=data_copy["downloadDeadline"],
        replyDeadline=data_copy["replyDeadline"],
        comment=data_copy["comment"],
        mailAddressTo=data_copy["mailAddressTo"],
        mailAddressCc=data_copy["mailAddressCc"],
        title=data_copy["title"]
    )
    assert response == {
        "result": True,
        "attachedFiles": [
            {
                "id": response["attachedFiles"][0]["id"],
                "fileName": response["attachedFiles"][0]["fileName"],
                "extension": response["attachedFiles"][0]["extension"]
            },
            {
                "id": response["attachedFiles"][1]["id"],
                "fileName": response["attachedFiles"][1]["fileName"],
                "extension": response["attachedFiles"][1]["extension"]
            }
        ],
        "id": response["id"]
    }
    print(response)


# No6.WBT新規メール情報登録API実行_02.メールアドレスリスト作成処理　正常系　Ccメールアドレスが2件（セミコロンで区切りあり）
def test_wbt_mails_add_api_exec_case6():
    data_copy = DATA.copy()
    data_copy["mailAddressTo"] = "test1@lincrea.co.jp"
    data_copy["mailAddressCc"] = "test2@lincrea.co.jp;test3@lincrea.co.jp"
    common_util = CommonUtilClass(trace_logger)
    response = common_util.wbt_mails_add_api_exec(
        repositoryType=data_copy["repositoryType"],
        fileName=data_copy["attachedFilesFileName"],
        downloadDeadline=data_copy["downloadDeadline"],
        replyDeadline=data_copy["replyDeadline"],
        comment=data_copy["comment"],
        mailAddressTo=data_copy["mailAddressTo"],
        mailAddressCc=data_copy["mailAddressCc"],
        title=data_copy["title"]
    )
    assert response == {
        "result": True,
        "attachedFiles": [
            {
                "id": response["attachedFiles"][0]["id"],
                "fileName": response["attachedFiles"][0]["fileName"],
                "extension": response["attachedFiles"][0]["extension"]
            },
            {
                "id": response["attachedFiles"][1]["id"],
                "fileName": response["attachedFiles"][1]["fileName"],
                "extension": response["attachedFiles"][1]["extension"]
            }
        ],
        "id": response["id"]
    }
    print(response)


# No7.WBT新規メール情報登録API実行_03.新規メール情報登録API実行　異常系　新規メール情報登録API実行に失敗する
def test_wbt_mails_add_api_exec_case7():
    data_copy = DATA.copy()
    data_copy["mailAddressTo"] = "test1@lincrea.co.jp"
    data_copy["mailAddressCc"] = "test2@lincrea.co.jp;test3@lincrea.co.jp"
    common_util = CommonUtilClass(trace_logger)
    response = common_util.wbt_mails_add_api_exec(
        repositoryType=data_copy["repositoryType"],
        fileName=data_copy["attachedFilesFileName"],
        downloadDeadline=data_copy["downloadDeadline"],
        replyDeadline=data_copy["replyDeadline"],
        comment=data_copy["comment"],
        mailAddressTo=data_copy["mailAddressTo"],
        mailAddressCc=data_copy["mailAddressCc"],
        title=data_copy["title"]
    )
    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "990011",
            "message": logUtil.message_build(MessageConstClass.ERRORS["990011"]["message"], "990011")
        }
    }
    print(response)


# No8.WBT新規メール情報登録API実行_03.新規メール情報登録API実行　正常系　新規メール情報登録API実行に成功する
def test_wbt_mails_add_api_exec_case8():
    data_copy = DATA.copy()
    data_copy["mailAddressTo"] = "test1@lincrea.co.jp"
    data_copy["mailAddressCc"] = "test2@lincrea.co.jp;test3@lincrea.co.jp"
    common_util = CommonUtilClass(trace_logger)
    response = common_util.wbt_mails_add_api_exec(
        repositoryType=data_copy["repositoryType"],
        fileName=data_copy["attachedFilesFileName"],
        downloadDeadline=data_copy["downloadDeadline"],
        replyDeadline=data_copy["replyDeadline"],
        comment=data_copy["comment"],
        mailAddressTo=data_copy["mailAddressTo"],
        mailAddressCc=data_copy["mailAddressCc"],
        title=data_copy["title"]
    )
    assert response == {
        "result": True,
        "attachedFiles": [
            {
                "id": response["attachedFiles"][0]["id"],
                "fileName": response["attachedFiles"][0]["fileName"],
                "extension": response["attachedFiles"][0]["extension"]
            },
            {
                "id": response["attachedFiles"][1]["id"],
                "fileName": response["attachedFiles"][1]["fileName"],
                "extension": response["attachedFiles"][1]["extension"]
            }
        ],
        "id": response["id"]
    }
    print(response)


# No9.WBT新規メール情報登録API実行_04.新規メール情報登録API実行チェック処理　正常系　「変数．エラー情報」が設定されていない場合、「06.終了処理」に遷移する
def test_wbt_mails_add_api_exec_case9():
    data_copy = DATA.copy()
    data_copy["mailAddressTo"] = "test1@lincrea.co.jp"
    data_copy["mailAddressCc"] = "test2@lincrea.co.jp;test3@lincrea.co.jp"
    common_util = CommonUtilClass(trace_logger)
    response = common_util.wbt_mails_add_api_exec(
        repositoryType=data_copy["repositoryType"],
        fileName=data_copy["attachedFilesFileName"],
        downloadDeadline=data_copy["downloadDeadline"],
        replyDeadline=data_copy["replyDeadline"],
        comment=data_copy["comment"],
        mailAddressTo=data_copy["mailAddressTo"],
        mailAddressCc=data_copy["mailAddressCc"],
        title=data_copy["title"]
    )
    assert response == {
        "result": True,
        "attachedFiles": [
            {
                "id": response["attachedFiles"][0]["id"],
                "fileName": response["attachedFiles"][0]["fileName"],
                "extension": response["attachedFiles"][0]["extension"]
            },
            {
                "id": response["attachedFiles"][1]["id"],
                "fileName": response["attachedFiles"][1]["fileName"],
                "extension": response["attachedFiles"][1]["extension"]
            }
        ],
        "id": response["id"]
    }
    print(response)


# No10.WBT新規メール情報登録API実行_04.新規メール情報登録API実行チェック処理　正常系　「変数．エラー情報」が設定されている場合、「05. 新規メール情報登録API実行チエラー処理」に遷移する
def test_wbt_mails_add_api_exec_case10():
    data_copy = DATA.copy()
    data_copy["mailAddressTo"] = "test1@lincrea.co.jp"
    data_copy["mailAddressCc"] = "test2@lincrea.co.jp;test3@lincrea.co.jp"
    common_util = CommonUtilClass(trace_logger)
    response = common_util.wbt_mails_add_api_exec(
        repositoryType=data_copy["repositoryType"],
        fileName=data_copy["attachedFilesFileName"],
        downloadDeadline=data_copy["downloadDeadline"],
        replyDeadline=data_copy["replyDeadline"],
        comment=data_copy["comment"],
        mailAddressTo=data_copy["mailAddressTo"],
        mailAddressCc=data_copy["mailAddressCc"],
        title=data_copy["title"]
    )
    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "990011",
            "message": logUtil.message_build(MessageConstClass.ERRORS["990011"]["message"], "990011")
        }
    }
    print(response)


# No11.WBT新規メール情報登録API実行_05. 新規メール情報登録API実行エラー処理　正常系　変数．エラー情報がある
def test_wbt_mails_add_api_exec_case11():
    data_copy = DATA.copy()
    data_copy["mailAddressTo"] = "test1@lincrea.co.jp"
    data_copy["mailAddressCc"] = "test2@lincrea.co.jp;test3@lincrea.co.jp"
    common_util = CommonUtilClass(trace_logger)
    response = common_util.wbt_mails_add_api_exec(
        repositoryType=data_copy["repositoryType"],
        fileName=data_copy["attachedFilesFileName"],
        downloadDeadline=data_copy["downloadDeadline"],
        replyDeadline=data_copy["replyDeadline"],
        comment=data_copy["comment"],
        mailAddressTo=data_copy["mailAddressTo"],
        mailAddressCc=data_copy["mailAddressCc"],
        title=data_copy["title"]
    )
    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "990011",
            "message": logUtil.message_build(MessageConstClass.ERRORS["990011"]["message"], "990011")
        }
    }
    print(response)


# No12.WBT新規メール情報登録API実行_06.終了処理　正常系　変数．エラー情報がない
def test_wbt_mails_add_api_exec_case12():
    data_copy = DATA.copy()
    data_copy["mailAddressTo"] = "test1@lincrea.co.jp"
    data_copy["mailAddressCc"] = "test2@lincrea.co.jp;test3@lincrea.co.jp"
    common_util = CommonUtilClass(trace_logger)
    response = common_util.wbt_mails_add_api_exec(
        repositoryType=data_copy["repositoryType"],
        fileName=data_copy["attachedFilesFileName"],
        downloadDeadline=data_copy["downloadDeadline"],
        replyDeadline=data_copy["replyDeadline"],
        comment=data_copy["comment"],
        mailAddressTo=data_copy["mailAddressTo"],
        mailAddressCc=data_copy["mailAddressCc"],
        title=data_copy["title"]
    )
    assert response == {
        "result": True,
        "attachedFiles": [
            {
                "id": response["attachedFiles"][0]["id"],
                "fileName": response["attachedFiles"][0]["fileName"],
                "extension": response["attachedFiles"][0]["extension"]
            },
            {
                "id": response["attachedFiles"][1]["id"],
                "fileName": response["attachedFiles"][1]["fileName"],
                "extension": response["attachedFiles"][1]["extension"]
            }
        ],
        "id": response["id"]
    }
    print(response)
