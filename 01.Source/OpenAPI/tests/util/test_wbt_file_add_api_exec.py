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
import io

client = TestClient(app)
file_object: bytes = io.BytesIO()

BEARER = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0Zk9wZXJhdG9ySWQiOiJsLXRlc3QiLCJ0Zk9wZXJhdG9yTmFtZSI6Ilx1MzBlZFx1MzBiMFx1MzBhNFx1MzBmM1x1MzBjNlx1MzBiOVx1MzBjOCIsInRmT3BlcmF0b3JQYXNzd29yZFJlc2V0RmxnIjpmYWxzZSwiYWNjZXNzVG9rZW4iOiJiZGE4ZGY3OThiYzViZGZhMWZkODIyNmRiYmQ0OTMyMTY5ZmY5MjAzNWM0YzFlY2FjZjY2OGUyYzk2ZjAwZThlZTUxNTBiNGM0NTc0NjlkN2I4YmY1NzIxZDZlM2NiNzFiY2RiYzA3ODRiYzcyZWVlNjk1OGE3NTBiMWJkMWEzZWFmZWQ0OWFhNWU0ODZjYzQyZmM3OWNhMWY3MGQzZmM3Yzc0YzE5NjM3ODUzMjRhZDRhNGM0NjkxOGE4NjQ1N2ZiODE3NDU1MCIsImV4cCI6MTY2MTc0NjY3MX0.LCRjPEqKMkRQ_phaYnO7S7pd3SU_rgon-wsX14DBsPA"
ACCESS_TOKEN = "bda8df798bc5bdfa1fd8226dbbd4932169ff92035c4c1ecacf668e2c96f00e8ee5150b4c457469d7b8bf5721d6e3cb71bcdbc0784bc72eee6958a750b1bd1a3eafed49aa5e486cc42fc79ca1f70d3fc7c74c1963785324ad4a4c46918a86457fb8174550"
HEADER = {"pdsUserId": "C9876543", "pdsUserDomainName": "pds-user-create", "Content-Type": "application/json", "timeStamp": "2022/08/23 15:12:01.690", "accessToken": ACCESS_TOKEN, "Authorization": "Bearer " + BEARER}
DATA = {
    "mailId": 1,
    "fileId": 1,
    "file": file_object,
    "chunkNo": "12345",
    "chunkTotalNumber": "5"
}

trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
token_util = TokenUtilClass(trace_logger)
common_util = CommonUtilClass(trace_logger)


@pytest.fixture
def create_auth():
    token_result = token_util.create_token_public(HEADER["pdsUserId"], HEADER["pdsUserName"], None)
    print(token_result["accessToken"], token_result["jwt"])
    yield {"accessToken": token_result["accessToken"], "jwt": token_result["jwt"]}


# No1.WBTファイル登録API実行_01.引数検証処理チェック　異常系　引数．メールID　値が設定されていない（空値）
def test_wbt_file_add_api_exec_case1_1_1():
    data_copy = DATA.copy()
    data_copy["mailId"] = ""
    with pytest.raises(PDSException) as e:
        common_util.wbt_file_add_api_exec(
            mailId=data_copy["mailId"],
            fileId=data_copy["fileId"],
            file=data_copy["file"],
            chunkNo=data_copy["chunkNo"],
            chunkTotalNumber=data_copy["chunkTotalNumber"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "メールID")
    }
    assert e.value.args[1] == {
        "errorCode": "020019",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "メールID", "数値")
    }
    print(e)


# No1.WBTファイル登録API実行_01.引数検証処理チェック　異常系　引数．メールID　数値型ではない
def test_wbt_file_add_api_exec_case1_1_2():
    data_copy = DATA.copy()
    data_copy["mailId"] = "12"
    with pytest.raises(PDSException) as e:
        common_util.wbt_file_add_api_exec(
            mailId=data_copy["mailId"],
            fileId=data_copy["fileId"],
            file=data_copy["file"],
            chunkNo=data_copy["chunkNo"],
            chunkTotalNumber=data_copy["chunkTotalNumber"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020019",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "メールID", "数値")
    }
    print(e)


# No1.WBTファイル登録API実行_01.引数検証処理チェック　正常系　引数．メールID　値が設定されている　数値型である
def test_wbt_file_add_api_exec_case1_1_3():
    data_copy = DATA.copy()
    response = common_util.wbt_file_add_api_exec(
        mailId=data_copy["mailId"],
        fileId=data_copy["fileId"],
        file=data_copy["file"],
        chunkNo=data_copy["chunkNo"],
        chunkTotalNumber=data_copy["chunkTotalNumber"]
    )
    assert response == {
        "result": True
    }
    print(response)


# No1.WBTファイル登録API実行_01.引数検証処理チェック　異常系　引数．ファイルID　値が設定されていない（空値）
def test_wbt_file_add_api_exec_case1_2_1():
    data_copy = DATA.copy()
    data_copy["fileId"] = ""
    with pytest.raises(PDSException) as e:
        common_util.wbt_file_add_api_exec(
            mailId=data_copy["mailId"],
            fileId=data_copy["fileId"],
            file=data_copy["file"],
            chunkNo=data_copy["chunkNo"],
            chunkTotalNumber=data_copy["chunkTotalNumber"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "ファイルID")
    }
    assert e.value.args[1] == {
        "errorCode": "020019",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "ファイルID", "数値")
    }
    print(e)


# No1.WBTファイル登録API実行_01.引数検証処理チェック　異常系　引数．ファイルID　数値型ではない
def test_wbt_file_add_api_exec_case1_2_2():
    data_copy = DATA.copy()
    data_copy["fileId"] = "12"
    with pytest.raises(PDSException) as e:
        common_util.wbt_file_add_api_exec(
            mailId=data_copy["mailId"],
            fileId=data_copy["fileId"],
            file=data_copy["file"],
            chunkNo=data_copy["chunkNo"],
            chunkTotalNumber=data_copy["chunkTotalNumber"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020019",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "ファイルID", "数値")
    }
    print(e)


# No1.WBTファイル登録API実行_01.引数検証処理チェック　正常系　引数．ファイルID　値が設定されている　数値型である
def test_wbt_file_add_api_exec_case1_2_3():
    data_copy = DATA.copy()
    response = common_util.wbt_file_add_api_exec(
        mailId=data_copy["mailId"],
        fileId=data_copy["fileId"],
        file=data_copy["file"],
        chunkNo=data_copy["chunkNo"],
        chunkTotalNumber=data_copy["chunkTotalNumber"]
    )
    assert response == {
        "result": True
    }
    print(response)


# No1.WBTファイル登録API実行_01.引数検証処理チェック　異常系　引数．添付ファイル　値が設定されていない（空値）
def test_wbt_file_add_api_exec_case1_3_1():
    data_copy = DATA.copy()
    data_copy["file"] = ""
    with pytest.raises(PDSException) as e:
        common_util.wbt_file_add_api_exec(
            mailId=data_copy["mailId"],
            fileId=data_copy["fileId"],
            file=data_copy["file"],
            chunkNo=data_copy["chunkNo"],
            chunkTotalNumber=data_copy["chunkTotalNumber"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "添付ファイル")
    }
    print(e)


# No1.WBTファイル登録API実行_01.引数検証処理チェック　異常系　引数．添付ファイル　文字列型ではない
def test_wbt_file_add_api_exec_case1_3_2():
    data_copy = DATA.copy()
    data_copy["file"] = 12
    with pytest.raises(PDSException) as e:
        common_util.wbt_file_add_api_exec(
            mailId=data_copy["mailId"],
            fileId=data_copy["fileId"],
            file=data_copy["file"],
            chunkNo=data_copy["chunkNo"],
            chunkTotalNumber=data_copy["chunkTotalNumber"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020019",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "添付ファイル", "File Stream")
    }
    print(e)


# No1.WBTファイル登録API実行_01.引数検証処理チェック　正常系　引数．添付ファイル　値が設定されている　文字列型である
def test_wbt_file_add_api_exec_case1_3_3():
    data_copy = DATA.copy()
    response = common_util.wbt_file_add_api_exec(
        mailId=data_copy["mailId"],
        fileId=data_copy["fileId"],
        file=data_copy["file"],
        chunkNo=data_copy["chunkNo"],
        chunkTotalNumber=data_copy["chunkTotalNumber"]
    )
    assert response == {
        "result": True
    }
    print(response)


# No1.WBTファイル登録API実行_01.引数検証処理チェック　異常系　引数．チャンク番号　文字列型ではない　入力規則違反していない（１以上）
def test_wbt_file_add_api_exec_case1_4_1():
    data_copy = DATA.copy()
    data_copy["chunkNo"] = 1
    with pytest.raises(PDSException) as e:
        common_util.wbt_file_add_api_exec(
            mailId=data_copy["mailId"],
            fileId=data_copy["fileId"],
            file=data_copy["file"],
            chunkNo=data_copy["chunkNo"],
            chunkTotalNumber=data_copy["chunkTotalNumber"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020019",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "チャンク番号", "文字列")
    }
    print(e)


# No1.WBTファイル登録API実行_01.引数検証処理チェック　異常系　引数．チャンク番号　文字列型である　入力規則違反している（０）
def test_wbt_file_add_api_exec_case1_4_2():
    data_copy = DATA.copy()
    data_copy["chunkNo"] = "%"
    with pytest.raises(PDSException) as e:
        common_util.wbt_file_add_api_exec(
            mailId=data_copy["mailId"],
            fileId=data_copy["fileId"],
            file=data_copy["file"],
            chunkNo=data_copy["chunkNo"],
            chunkTotalNumber=data_copy["chunkTotalNumber"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020003",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "チャンク番号")
    }
    print(e)


# No1.WBTファイル登録API実行_01.引数検証処理チェック　異常系　引数．チャンク番号　文字列型である　入力規則違反している（半角英字記号、全角）
def test_wbt_file_add_api_exec_case1_4_3():
    data_copy = DATA.copy()
    data_copy["chunkNo"] = "あ"
    with pytest.raises(PDSException) as e:
        common_util.wbt_file_add_api_exec(
            mailId=data_copy["mailId"],
            fileId=data_copy["fileId"],
            file=data_copy["file"],
            chunkNo=data_copy["chunkNo"],
            chunkTotalNumber=data_copy["chunkTotalNumber"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020003",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "チャンク番号")
    }
    print(e)


# No1.WBTファイル登録API実行_01.引数検証処理チェック　正常系　引数．チャンク番号　値が設定されている　文字列型である　入力規則違反していない（１以上）
def test_wbt_file_add_api_exec_case1_4_4():
    data_copy = DATA.copy()
    response = common_util.wbt_file_add_api_exec(
        mailId=data_copy["mailId"],
        fileId=data_copy["fileId"],
        file=data_copy["file"],
        chunkNo=data_copy["chunkNo"],
        chunkTotalNumber=data_copy["chunkTotalNumber"]
    )
    assert response == {
        "result": True
    }
    print(response)


# No1.WBTファイル登録API実行_01.引数検証処理チェック　異常系　引数．チャンク分割総数　文字列型ではない　入力規則違反していない（１以上）
def test_wbt_file_add_api_exec_case1_5_1():
    data_copy = DATA.copy()
    data_copy["chunkTotalNumber"] = 1
    with pytest.raises(PDSException) as e:
        common_util.wbt_file_add_api_exec(
            mailId=data_copy["mailId"],
            fileId=data_copy["fileId"],
            file=data_copy["file"],
            chunkNo=data_copy["chunkNo"],
            chunkTotalNumber=data_copy["chunkTotalNumber"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020019",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "チャンク分割総数", "文字列")
    }
    print(e)


# No1.WBTファイル登録API実行_01.引数検証処理チェック　異常系　引数．チャンク分割総数　文字列型である　入力規則違反している（０）
def test_wbt_file_add_api_exec_case1_5_2():
    data_copy = DATA.copy()
    data_copy["chunkTotalNumber"] = "%"
    with pytest.raises(PDSException) as e:
        common_util.wbt_file_add_api_exec(
            mailId=data_copy["mailId"],
            fileId=data_copy["fileId"],
            file=data_copy["file"],
            chunkNo=data_copy["chunkNo"],
            chunkTotalNumber=data_copy["chunkTotalNumber"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020003",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "チャンク分割総数")
    }
    print(e)


# No1.WBTファイル登録API実行_01.引数検証処理チェック　異常系　引数．チャンク分割総数　文字列型である　入力規則違反している（半角英字記号、全角）
def test_wbt_file_add_api_exec_case1_5_3():
    data_copy = DATA.copy()
    data_copy["chunkTotalNumber"] = "あ"
    with pytest.raises(PDSException) as e:
        common_util.wbt_file_add_api_exec(
            mailId=data_copy["mailId"],
            fileId=data_copy["fileId"],
            file=data_copy["file"],
            chunkNo=data_copy["chunkNo"],
            chunkTotalNumber=data_copy["chunkTotalNumber"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020003",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "チャンク分割総数")
    }
    print(e)


# No1.WBTファイル登録API実行_01.引数検証処理チェック　正常系　引数．ファイル分割総数　値が設定されている　文字列型である　入力規則違反していない（１以上）
def test_wbt_file_add_api_exec_case1_5_4():
    data_copy = DATA.copy()
    response = common_util.wbt_file_add_api_exec(
        mailId=data_copy["mailId"],
        fileId=data_copy["fileId"],
        file=data_copy["file"],
        chunkNo=data_copy["chunkNo"],
        chunkTotalNumber=data_copy["chunkTotalNumber"]
    )
    assert response == {
        "result": True
    }
    print(response)


# No2.WBTファイル登録API実行_02.ファイル登録API実行　異常系　ファイル登録API実行に失敗する　パラメータ不正
def test_wbt_file_add_api_exec_case2():
    data_copy = DATA.copy()
    data_copy["mailId"] = "1"
    with pytest.raises(PDSException) as e:
        common_util.wbt_file_add_api_exec(
            mailId=data_copy["mailId"],
            fileId=data_copy["fileId"],
            file=data_copy["file"],
            chunkNo=data_copy["chunkNo"],
            chunkTotalNumber=data_copy["chunkTotalNumber"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020019",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "メールID", "数値")
    }
    print(e)


# No3.WBTファイル登録API実行_02.ファイル登録API実行　正常系　ファイル登録API実行に成功する
def test_wbt_file_add_api_exec_case3():
    data_copy = DATA.copy()
    response = common_util.wbt_file_add_api_exec(
        mailId=data_copy["mailId"],
        fileId=data_copy["fileId"],
        file=data_copy["file"],
        chunkNo=data_copy["chunkNo"],
        chunkTotalNumber=data_copy["chunkTotalNumber"]
    )
    assert response == {
        "result": True
    }
    print(response)


# No4.WBTファイル登録API実行_03.ファイル登録API実行チェック処理　正常系　「変数．エラー情報」が設定されていない場合、「06.終了処理」に遷移する
def test_wbt_file_add_api_exec_case4():
    data_copy = DATA.copy()
    response = common_util.wbt_file_add_api_exec(
        mailId=data_copy["mailId"],
        fileId=data_copy["fileId"],
        file=data_copy["file"],
        chunkNo=data_copy["chunkNo"],
        chunkTotalNumber=data_copy["chunkTotalNumber"]
    )
    assert response == {
        "result": True
    }
    print(response)


# No5.WBTファイル登録API実行_03.ファイル登録API実行チェック処理　正常系　「変数．エラー情報」が設定されている場合、「04. ファイル登録API実行エラー処理」に遷移する
def test_wbt_file_add_api_exec_case5():
    data_copy = DATA.copy()
    response = common_util.wbt_file_add_api_exec(
        mailId=data_copy["mailId"],
        fileId=data_copy["fileId"],
        file=data_copy["file"],
        chunkNo=data_copy["chunkNo"],
        chunkTotalNumber=data_copy["chunkTotalNumber"]
    )
    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "990013",
            "message": logUtil.message_build(MessageConstClass.ERRORS["990013"]["message"], "990013")
        }
    }
    print(response)


# No6.WBTファイル登録API実行_04. WBTファイル登録API実行エラー処理　正常系　変数．エラー情報がある
def test_wbt_file_add_api_exec_case6():
    data_copy = DATA.copy()
    response = common_util.wbt_file_add_api_exec(
        mailId=data_copy["mailId"],
        fileId=data_copy["fileId"],
        file=data_copy["file"],
        chunkNo=data_copy["chunkNo"],
        chunkTotalNumber=data_copy["chunkTotalNumber"]
    )
    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "990013",
            "message": logUtil.message_build(MessageConstClass.ERRORS["990013"]["message"], "990013")
        }
    }
    print(response)


# No7.BTファイル登録API実行_05.終了処理　正常系　変数．エラー情報がない
def test_wbt_file_add_api_exec_case7():
    data_copy = DATA.copy()
    response = common_util.wbt_file_add_api_exec(
        mailId=data_copy["mailId"],
        fileId=data_copy["fileId"],
        file=data_copy["file"],
        chunkNo=data_copy["chunkNo"],
        chunkTotalNumber=data_copy["chunkTotalNumber"]
    )
    assert response == {
        "result": True
    }
    print(response)
