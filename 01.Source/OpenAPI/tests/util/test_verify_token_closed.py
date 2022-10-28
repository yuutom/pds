from fastapi.testclient import TestClient
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

HEADER = {"tfOperatorId": 't-test4', "tfOperatorName": 'テスト'}
request_dict = {
    "tfOperatorId": "t-test4",
    "tfOperatorPassword": "abcdedABC123%"
}
trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
token_util = TokenUtilClass(trace_logger)


@pytest.fixture
def data():
    token_result = token_util.create_token_closed(
        {
            "tfOperatorId": HEADER["tfOperatorId"],
            "tfOperatorName": HEADER["tfOperatorName"]
        },
        None
    )
    yield {"accessToken": token_result["accessToken"], "jwt": token_result["jwt"]}


# 01.引数検証処理チェック処理
# アクセストークン検証（非公開用）_01.引数検証処理チェック　シート参照
# No1_1.引数．JWTの値が設定されていない (空値)
def test_verify_token_closed_case1_1(data):
    data_copy = data.copy()
    data_copy["jwt"] = None
    with pytest.raises(PDSException) as e:
        token_util.verify_token_closed(accessToken=data_copy["accessToken"], jwt=data_copy["jwt"])

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "JWT")
    }
    print(e)


# No1_2.引数．JWTの値が設定されていて文字列型ではない場合
def test_verify_token_closed_case1_2(data):
    data_copy = data.copy()
    data_copy["jwt"] = 123456789
    with pytest.raises(PDSException) as e:
        token_util.verify_token_closed(accessToken=data_copy["accessToken"], jwt=data_copy["jwt"])

    assert e.value.args[0] == {
        "errorCode": "020019",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "JWT", "文字列")
    }
    print(e)


# No1_3.JWTが正常な場合
def test_verify_token_closed_case1_3(data):
    data_copy = data.copy()
    response = token_util.verify_token_closed(accessToken=data_copy["accessToken"], jwt=data_copy["jwt"])
    assert response == {
        "result": True,
        "payload": {
            "tfOperatorId": HEADER["tfOperatorId"],
            "tfOperatorName": HEADER["tfOperatorName"],
            "accessToken": response["payload"]["accessToken"]
        }
    }
    print(response)


# 異常系
# No2.アクセストークンが異常な値
def test_verify_token_closed_case2(data):
    data_copy = data.copy()
    data_copy["accessToken"] = data_copy["accessToken"] + "abc"
    with pytest.raises(PDSException) as e:
        token_util.verify_token_closed(accessToken=data_copy["accessToken"], jwt=data_copy["jwt"])

    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020014",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020014"]["message"], "アクセストークン", "200")
    }
    print(e)


# 正常系
# No3.アクセストークンが正常な値
def test_verify_token_closed_case3(data):
    data_copy = data.copy()
    response = token_util.verify_token_closed(accessToken=data_copy["accessToken"], jwt=data_copy["jwt"])
    assert response == {
        "result": True,
        "payload": {
            "tfOperatorId": HEADER["tfOperatorId"],
            "tfOperatorName": HEADER["tfOperatorName"],
            "accessToken": response["payload"]["accessToken"]
        }
    }
    print(response)


# 02.DB接続準備処理
# 異常系
# No4.接続に失敗する
# 設定値を異常な値に変更する
def test_verify_token_closed_case4(data, mocker: MockerFixture):
    data_copy = data.copy()
    # Exception
    mocker.patch("util.commonUtil.CommonUtilClass.get_secret_info").return_value = {"host": "test", "port": "test", "username": "test", "password": "test"}
    response = token_util.verify_token_closed(accessToken=data_copy["accessToken"], jwt=data_copy["jwt"])
    assert response == {
        "result": False,
        'errorInfo': {
            'errorCode': '999999',
            'message': logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
        }
    }
    print(response)


# 正常系
# No5.接続に成功する
def test_verify_token_closed_case5(data):
    data_copy = data.copy()
    response = token_util.verify_token_closed(accessToken=data_copy["accessToken"], jwt=data_copy["jwt"])
    assert response == {
        "result": True,
        "payload": {
            "tfOperatorId": HEADER["tfOperatorId"],
            "tfOperatorName": HEADER["tfOperatorName"],
            "accessToken": response["payload"]["accessToken"]
        }
    }
    print(response)


# 03.アクセストークン取得処理
# 異常系
# No6.アクセストークン取得処理で取得結果が0件
def test_verify_token_closed_case6(data):
    data_copy = data.copy()
    data_copy["accessToken"] = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    response = token_util.verify_token_closed(accessToken=data_copy["accessToken"], jwt=data_copy["jwt"])
    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "010004",
            "message": logUtil.message_build(MessageConstClass.ERRORS["010004"]["message"])
        }
    }
    print(response)


# 異常系
# No7.postgresqlのエラーが発生
def test_verify_token_closed_case7(data, mocker: MockerFixture):
    data_copy = data.copy()
    # Exception
    mocker.patch.object(SqlConstClass, "ACCESS_TOKEN_CLOSED_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    response = token_util.verify_token_closed(accessToken=data_copy["accessToken"], jwt=data_copy["jwt"])
    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "991028",
            "message": logUtil.message_build(MessageConstClass.ERRORS["991028"]["message"], "991028")
        }
    }
    print(response)


# 正常系
# No8.アクセストークン取得処理で取得結果が1件
def test_verify_token_closed_case8(data):
    data_copy = data.copy()
    response = token_util.verify_token_closed(accessToken=data_copy["accessToken"], jwt=data_copy["jwt"])
    assert response == {
        "result": True,
        "payload": {
            "tfOperatorId": HEADER["tfOperatorId"],
            "tfOperatorName": HEADER["tfOperatorName"],
            "accessToken": response["payload"]["accessToken"]
        }
    }
    print(response)


# 04.アクセストークン取得チェック処理
# 正常系
# No9.「変数．エラー情報」が設定されていない場合、「06.JWT検証処理」に遷移する
def test_verify_token_closed_case9(data):
    data_copy = data.copy()
    response = token_util.verify_token_closed(accessToken=data_copy["accessToken"], jwt=data_copy["jwt"])
    assert response == {
        "result": True,
        "payload": {
            "tfOperatorId": HEADER["tfOperatorId"],
            "tfOperatorName": HEADER["tfOperatorName"],
            "accessToken": response["payload"]["accessToken"]
        }
    }
    print(response)


# 正常系
# No10.「変数．エラー情報」が設定されている場合、「05.アクセストークン取得エラー処理」に遷移する
def test_verify_token_closed_case10(data):
    data_copy = data.copy()
    data_copy["accessToken"] = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    response = token_util.verify_token_closed(accessToken=data_copy["accessToken"], jwt=data_copy["jwt"])
    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "010004",
            "message": logUtil.message_build(MessageConstClass.ERRORS["010004"]["message"])
        }
    }
    print(response)


# 05.アクセストークン取得エラー処理
# 正常系
# No11.レスポンス情報を作成し、返却する
def test_verify_token_closed_case11(data):
    data_copy = data.copy()
    data_copy["accessToken"] = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    response = token_util.verify_token_closed(accessToken=data_copy["accessToken"], jwt=data_copy["jwt"])
    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "010004",
            "message": logUtil.message_build(MessageConstClass.ERRORS["010004"]["message"])
        }
    }
    print(response)


# 06.JWT検証処理
# 異常系
# No12.JWT検証処理が失敗する※不正なJWT
def test_verify_token_closed_case12(data):
    data_copy = data.copy()
    data_copy["jwt"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0Zk9wZXJhdG9ySWQiOiJ0LXRlc3QzIiwidGZPcGVyYXRvck5hbWUiOiJcdTMwZWFcdTMwYmJcdTMwYzNcdTMwYzhcdTMwYzZcdTMwYjlcdTMwYzgiLCJ0Zk9wZXJhdG9yUGFzc3dvcmRSZXNldEZsZyI6dHJ1ZSwiYWNjZXNzVG9rZW4iOiI5MDA3ZTY5NjI3ZWQ0NmMyZWVmZTcyNzBiMWFmMzk5YjUxNDU4MzY4NjkxYjc5NzMwMWNhODMxZDQzYzMyNDI4NmM2M2I2YmJiMzgwYzA4YjZlOWUzYmYxNTgzZTdmZjE2ZDZkMmM3M2RjN2NhYjIwZmE0NzRkOGM5OTExYTM5MDcwNzNjNDBkZTcxNWRiN2NiNTg5ZGZjNTYxZTY5ZTUzMzVjMTM1OWZlZDAyOGVlNTI4ODUxMGY2NTEzYjY0MDgyMDJhM2IxYyIsImV4cCI6MTY2MjQwODk4Nn0.Iqg4LKqpVX3chjkBtyFbhphHt-zPUu98VpJtWHIR-CE"
    response = token_util.verify_token_closed(accessToken=data_copy["accessToken"], jwt=data_copy["jwt"])
    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "010007",
            "message": logUtil.message_build(MessageConstClass.ERRORS["010007"]["message"])
        }
    }


# 異常系
# No13.JWT検証処理が失敗する※30分以上経過したアクセストークン
def test_verify_token_closed_case13(data):
    data_copy = data.copy()
    data_copy["jwt"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0Zk9wZXJhdG9ySWQiOiJ0LXRlc3QzIiwidGZPcGVyYXRvck5hbWUiOiJcdTMwZWFcdTMwYmJcdTMwYzNcdTMwYzhcdTMwYzZcdTMwYjlcdTMwYzgiLCJ0Zk9wZXJhdG9yUGFzc3dvcmRSZXNldEZsZyI6dHJ1ZSwiYWNjZXNzVG9rZW4iOiI5MDA3ZTY5NjI3ZWQ0NmMyZWVmZTcyNzBiMWFmMzk5YjUxNDU4MzY4NjkxYjc5NzMwMWNhODMxZDQzYzMyNDI4NmM2M2I2YmJiMzgwYzA4YjZlOWUzYmYxNTgzZTdmZjE2ZDZkMmM3M2RjN2NhYjIwZmE0NzRkOGM5OTExYTM5MDcwNzNjNDBkZTcxNWRiN2NiNTg5ZGZjNTYxZTY5ZTUzMzVjMTM1OWZlZDAyOGVlNTI4ODUxMGY2NTEzYjY0MDgyMDJhM2IxYyIsImV4cCI6MTY2MjQwODk4Nn0.Iqg4LKqpVX3chjkBtyFbhphHt-zPUu98VpJtWHIR-CE"
    response = token_util.verify_token_closed(accessToken=data_copy["accessToken"], jwt=data_copy["jwt"])
    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "010007",
            "message": logUtil.message_build(MessageConstClass.ERRORS["010007"]["message"])
        }
    }


# 正常系
# No14.JWT検証処理処理が成功する
def test_verify_token_closed_case14(data):
    data_copy = data.copy()
    response = token_util.verify_token_closed(accessToken=data_copy["accessToken"], jwt=data_copy["jwt"])
    assert response == {
        "result": True,
        "payload": {
            "tfOperatorId": HEADER["tfOperatorId"],
            "tfOperatorName": HEADER["tfOperatorName"],
            "accessToken": response["payload"]["accessToken"]
        }
    }
    print(response)


# 07.JWT検証チェック処理
# 正常系
# No15.「変数．エラー情報」が設定されていない場合、「09.終了処理」に遷移する
def test_verify_token_closed_case15(data):
    data_copy = data.copy()
    response = token_util.verify_token_closed(accessToken=data_copy["accessToken"], jwt=data_copy["jwt"])
    assert response == {
        "result": True,
        "payload": {
            "tfOperatorId": HEADER["tfOperatorId"],
            "tfOperatorName": HEADER["tfOperatorName"],
            "accessToken": response["payload"]["accessToken"]
        }
    }
    print(response)


# 正常系
# No16.「変数．エラー情報」が設定されている場合、「08.JWT検証エラー処理」に遷移する
def test_verify_token_closed_case16(data):
    data_copy = data.copy()
    data_copy["jwt"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0Zk9wZXJhdG9ySWQiOiJ0LXRlc3QzIiwidGZPcGVyYXRvck5hbWUiOiJcdTMwZWFcdTMwYmJcdTMwYzNcdTMwYzhcdTMwYzZcdTMwYjlcdTMwYzgiLCJ0Zk9wZXJhdG9yUGFzc3dvcmRSZXNldEZsZyI6dHJ1ZSwiYWNjZXNzVG9rZW4iOiI5MDA3ZTY5NjI3ZWQ0NmMyZWVmZTcyNzBiMWFmMzk5YjUxNDU4MzY4NjkxYjc5NzMwMWNhODMxZDQzYzMyNDI4NmM2M2I2YmJiMzgwYzA4YjZlOWUzYmYxNTgzZTdmZjE2ZDZkMmM3M2RjN2NhYjIwZmE0NzRkOGM5OTExYTM5MDcwNzNjNDBkZTcxNWRiN2NiNTg5ZGZjNTYxZTY5ZTUzMzVjMTM1OWZlZDAyOGVlNTI4ODUxMGY2NTEzYjY0MDgyMDJhM2IxYyIsImV4cCI6MTY2MjQwODk4Nn0.Iqg4LKqpVX3chjkBtyFbhphHt-zPUu98VpJtWHIR-CE"
    response = token_util.verify_token_closed(accessToken=data_copy["accessToken"], jwt=data_copy["jwt"])
    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "010007",
            "message": logUtil.message_build(MessageConstClass.ERRORS["010007"]["message"])
        }
    }


# 08.JWT検証エラー処理
# 正常系
# No17.レスポンス情報を作成し、返却する
def test_verify_token_closed_case17(data):
    data_copy = data.copy()
    data_copy["jwt"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0Zk9wZXJhdG9ySWQiOiJ0LXRlc3QzIiwidGZPcGVyYXRvck5hbWUiOiJcdTMwZWFcdTMwYmJcdTMwYzNcdTMwYzhcdTMwYzZcdTMwYjlcdTMwYzgiLCJ0Zk9wZXJhdG9yUGFzc3dvcmRSZXNldEZsZyI6dHJ1ZSwiYWNjZXNzVG9rZW4iOiI5MDA3ZTY5NjI3ZWQ0NmMyZWVmZTcyNzBiMWFmMzk5YjUxNDU4MzY4NjkxYjc5NzMwMWNhODMxZDQzYzMyNDI4NmM2M2I2YmJiMzgwYzA4YjZlOWUzYmYxNTgzZTdmZjE2ZDZkMmM3M2RjN2NhYjIwZmE0NzRkOGM5OTExYTM5MDcwNzNjNDBkZTcxNWRiN2NiNTg5ZGZjNTYxZTY5ZTUzMzVjMTM1OWZlZDAyOGVlNTI4ODUxMGY2NTEzYjY0MDgyMDJhM2IxYyIsImV4cCI6MTY2MjQwODk4Nn0.Iqg4LKqpVX3chjkBtyFbhphHt-zPUu98VpJtWHIR-CE"
    response = token_util.verify_token_closed(accessToken=data_copy["accessToken"], jwt=data_copy["jwt"])
    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "010007",
            "message": logUtil.message_build(MessageConstClass.ERRORS["010007"]["message"])
        }
    }


# 09.終了処理
# No18.変数．エラー情報がない
def test_verify_token_closed_case18(data):
    data_copy = data.copy()
    response = token_util.verify_token_closed(accessToken=data_copy["accessToken"], jwt=data_copy["jwt"])
    assert response == {
        "result": True,
        "payload": {
            "tfOperatorId": HEADER["tfOperatorId"],
            "tfOperatorName": HEADER["tfOperatorName"],
            "accessToken": response["payload"]["accessToken"]
        }
    }
    print(response)


# 06.JWT検証処理
# No19.JWT検証処理が失敗する※不正なJWT
def test_verify_token_closed_case19(mocker: MockerFixture, data):
    data_copy = data.copy()
    mocker.patch("util.postgresDbUtil.PostgresDbUtilClass.select_tuple_one").return_value = {"result": True, "rowcount": 1, "query_results": ('8b8bb7fda6a04d28a9c3801906cf43cc', 't-test5')}
    response = token_util.verify_token_closed(accessToken=data_copy["accessToken"], jwt=data_copy["jwt"])
    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "010007",
            "message": logUtil.message_build(MessageConstClass.ERRORS["010007"]["message"])
        }
    }
    print(response)
