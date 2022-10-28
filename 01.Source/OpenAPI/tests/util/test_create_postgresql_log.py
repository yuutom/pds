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
    "e": PDSException({"errorCode": "999999", "message": "test_message"}),
    "param": None,
    "value": None,
    "stackTrace": ""
}

trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
token_util = TokenUtilClass(trace_logger)


@pytest.fixture
def create_auth():
    token_result = token_util.create_token_public(HEADER["pdsUserId"], HEADER["pdsUserName"], None)
    print(token_result["accessToken"], token_result["jwt"])
    yield {"accessToken": token_result["accessToken"], "jwt": token_result["jwt"]}


# 01.引数検証処理チェック処理
# No1_1.引数．例外オブジェクト_値が設定されていない（空値）
def test_create_postgresql_log_case1_1():
    data_copy = DATA.copy()
    data_copy["e"] = ""
    common_util = CommonUtilClass(trace_logger)
    with pytest.raises(PDSException) as e:
        common_util.create_postgresql_log(
            data_copy["e"],
            data_copy["param"],
            data_copy["value"],
            data_copy["stackTrace"]
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "例外オブジェクト")
    }
    print(e)


# No1_2.引数．例外オブジェクト_値が設定されている
def test_create_postgresql_log_case1_2():
    data_copy = DATA.copy()
    data_copy["e"].setter("TT000", "test_error")
    common_util = CommonUtilClass(trace_logger)
    response = common_util.create_postgresql_log(
        data_copy["e"],
        data_copy["param"],
        data_copy["value"],
        data_copy["stackTrace"]
    )
    assert response == {
        "errorInfo": {
            "errorCode": "999999",
            "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
        }
    }
    print(response)


# 02.postgresql例外処理
# No2.「引数．例外オブジェクト．エラーコード」の前2桁=03（03クラス — SQL文の未完了）の場合
def test_create_postgresql_log_case2():
    data_copy = DATA.copy()
    data_copy["e"].setter("03000", "test_error")
    common_util = CommonUtilClass(trace_logger)
    response = common_util.create_postgresql_log(
        data_copy["e"],
        data_copy["param"],
        data_copy["value"],
        data_copy["stackTrace"]
    )
    assert response == {
        "errorInfo": {
            "errorCode": "991001",
            "message": logUtil.message_build(MessageConstClass.ERRORS["991001"]["message"], "991001")
        }
    }
    print(response)


# No3.「引数．例外オブジェクト．エラーコード」の前2桁=08（08 クラス — 接続の例外）の場合
def test_create_postgresql_log_case3():
    data_copy = DATA.copy()
    data_copy["e"].setter("08000", "test_error")
    common_util = CommonUtilClass(trace_logger)
    response = common_util.create_postgresql_log(
        data_copy["e"],
        data_copy["param"],
        data_copy["value"],
        data_copy["stackTrace"]
    )
    assert response == {
        "errorInfo": {
            "errorCode": "991002",
            "message": logUtil.message_build(MessageConstClass.ERRORS["991002"]["message"], "991002")
        }
    }
    print(response)


# No4.「引数．例外オブジェクト．エラーコード」の前2桁=09（09 クラス — トリガによるアクションの例外）の場合
def test_create_postgresql_log_case4():
    data_copy = DATA.copy()
    data_copy["e"].setter("09000", "test_error")
    common_util = CommonUtilClass(trace_logger)
    response = common_util.create_postgresql_log(
        data_copy["e"],
        data_copy["param"],
        data_copy["value"],
        data_copy["stackTrace"]
    )
    assert response == {
        "errorInfo": {
            "errorCode": "991003",
            "message": logUtil.message_build(MessageConstClass.ERRORS["991003"]["message"], "991003")
        }
    }
    print(response)


# No5.「引数．例外オブジェクト．エラーコード」の前2桁=0A（0A クラス — サポートされない機能）の場合
def test_create_postgresql_log_case5():
    data_copy = DATA.copy()
    data_copy["e"].setter("0A000", "test_error")
    common_util = CommonUtilClass(trace_logger)
    response = common_util.create_postgresql_log(
        data_copy["e"],
        data_copy["param"],
        data_copy["value"],
        data_copy["stackTrace"]
    )
    assert response == {
        "errorInfo": {
            "errorCode": "991004",
            "message": logUtil.message_build(MessageConstClass.ERRORS["991004"]["message"], "991004")
        }
    }
    print(response)


# No6.「引数．例外オブジェクト．エラーコード」の前2桁=0B（0Bクラス — 無効なトランザクションの初期）の場合
def test_create_postgresql_log_case6():
    data_copy = DATA.copy()
    data_copy["e"].setter("0B000", "test_error")
    common_util = CommonUtilClass(trace_logger)
    response = common_util.create_postgresql_log(
        data_copy["e"],
        data_copy["param"],
        data_copy["value"],
        data_copy["stackTrace"]
    )
    assert response == {
        "errorInfo": {
            "errorCode": "991005",
            "message": logUtil.message_build(MessageConstClass.ERRORS["991005"]["message"], "991005")
        }
    }
    print(response)


# No7.「引数．例外オブジェクト．エラーコード」の前2桁=0F（0F クラス — ロケータの例外）の場合
def test_create_postgresql_log_case7():
    data_copy = DATA.copy()
    data_copy["e"].setter("0F000", "test_error")
    common_util = CommonUtilClass(trace_logger)
    response = common_util.create_postgresql_log(
        data_copy["e"],
        data_copy["param"],
        data_copy["value"],
        data_copy["stackTrace"]
    )
    assert response == {
        "errorInfo": {
            "errorCode": "991006",
            "message": logUtil.message_build(MessageConstClass.ERRORS["991006"]["message"], "991006")
        }
    }
    print(response)


# No8.「引数．例外オブジェクト．エラーコード」の前2桁=0L（0L クラス — 無効な権限付与）の場合
def test_create_postgresql_log_case8():
    data_copy = DATA.copy()
    data_copy["e"].setter("0L000", "test_error")
    common_util = CommonUtilClass(trace_logger)
    response = common_util.create_postgresql_log(
        data_copy["e"],
        data_copy["param"],
        data_copy["value"],
        data_copy["stackTrace"]
    )
    assert response == {
        "errorInfo": {
            "errorCode": "991007",
            "message": logUtil.message_build(MessageConstClass.ERRORS["991007"]["message"], "991007")
        }
    }
    print(response)


# No9.「引数．例外オブジェクト．エラーコード」の前2桁=0P（0P クラス — 無効なロールの指定）の場合
def test_create_postgresql_log_case9():
    data_copy = DATA.copy()
    data_copy["e"].setter("0P000", "test_error")
    common_util = CommonUtilClass(trace_logger)
    response = common_util.create_postgresql_log(
        data_copy["e"],
        data_copy["param"],
        data_copy["value"],
        data_copy["stackTrace"]
    )
    assert response == {
        "errorInfo": {
            "errorCode": "991008",
            "message": logUtil.message_build(MessageConstClass.ERRORS["991008"]["message"], "991008")
        }
    }
    print(response)


# No10.「引数．例外オブジェクト．エラーコード」の前2桁=20（20 クラス — Caseが存在しない）の場合
def test_create_postgresql_log_case10():
    data_copy = DATA.copy()
    data_copy["e"].setter("20000", "test_error")
    common_util = CommonUtilClass(trace_logger)
    response = common_util.create_postgresql_log(
        data_copy["e"],
        data_copy["param"],
        data_copy["value"],
        data_copy["stackTrace"]
    )
    assert response == {
        "errorInfo": {
            "errorCode": "991009",
            "message": logUtil.message_build(MessageConstClass.ERRORS["991009"]["message"], "991009")
        }
    }
    print(response)


# No11.「引数．例外オブジェクト．エラーコード」の前2桁=21（21クラス — 次数違反）の場合
def test_create_postgresql_log_case11():
    data_copy = DATA.copy()
    data_copy["e"].setter("21000", "test_error")
    common_util = CommonUtilClass(trace_logger)
    response = common_util.create_postgresql_log(
        data_copy["e"],
        data_copy["param"],
        data_copy["value"],
        data_copy["stackTrace"]
    )
    assert response == {
        "errorInfo": {
            "errorCode": "991010",
            "message": logUtil.message_build(MessageConstClass.ERRORS["991010"]["message"], "991010")
        }
    }
    print(response)


# No12.「引数．例外オブジェクト．エラーコード」の前2桁=22（22 クラス — データ例外）の場合
def test_create_postgresql_log_case12():
    data_copy = DATA.copy()
    data_copy["e"].setter("22000", "test_error")
    common_util = CommonUtilClass(trace_logger)
    response = common_util.create_postgresql_log(
        data_copy["e"],
        data_copy["param"],
        data_copy["value"],
        data_copy["stackTrace"]
    )
    assert response == {
        "errorInfo": {
            "errorCode": "991011",
            "message": logUtil.message_build(MessageConstClass.ERRORS["991011"]["message"], "991011")
        }
    }
    print(response)


# No13.「引数．例外オブジェクト．エラーコード」の前2桁=23（23 クラス — 整合性制約違反）の場合　かつ引数．例外オブジェクト．エラーコード=23505以外の場合
def test_create_postgresql_log_case13():
    data_copy = DATA.copy()
    data_copy["e"].setter("23000", "test_error")
    common_util = CommonUtilClass(trace_logger)
    response = common_util.create_postgresql_log(
        data_copy["e"],
        data_copy["param"],
        data_copy["value"],
        data_copy["stackTrace"]
    )
    assert response == {
        "errorInfo": {
            "errorCode": "991012",
            "message": logUtil.message_build(MessageConstClass.ERRORS["991012"]["message"], "991012")
        }
    }
    print(response)


# No14.「引数．例外オブジェクト．エラーコード」の前2桁=23（23 クラス — 整合性制約違反）の場合　かつ引数．例外オブジェクト．エラーコード=23505の場合
def test_create_postgresql_log_case14():
    data_copy = DATA.copy()
    data_copy["param"] = "test_param"
    data_copy["value"] = "test_value"
    data_copy["e"].setter("23505", "test_error")
    common_util = CommonUtilClass(trace_logger)
    response = common_util.create_postgresql_log(
        data_copy["e"],
        data_copy["param"],
        data_copy["value"],
        data_copy["stackTrace"]
    )
    assert response == {
        "errorInfo": {
            "errorCode": "030001",
            "message": logUtil.message_build(MessageConstClass.ERRORS["030001"]["message"], data_copy["param"], data_copy["value"])
        }
    }
    print(response)


# No15.「引数．例外オブジェクト．エラーコード」の前2桁=24（24 クラス — 無効なカーソル状態）の場合
def test_create_postgresql_log_case15():
    data_copy = DATA.copy()
    data_copy["e"].setter("24000", "test_error")
    common_util = CommonUtilClass(trace_logger)
    response = common_util.create_postgresql_log(
        data_copy["e"],
        data_copy["param"],
        data_copy["value"],
        data_copy["stackTrace"]
    )
    assert response == {
        "errorInfo": {
            "errorCode": "991013",
            "message": logUtil.message_build(MessageConstClass.ERRORS["991013"]["message"], "991013")
        }
    }
    print(response)


# No16.「引数．例外オブジェクト．エラーコード」の前2桁=25（25 クラス — 無効なトランザクション状態）の場合
def test_create_postgresql_log_case16():
    data_copy = DATA.copy()
    data_copy["e"].setter("25000", "test_error")
    common_util = CommonUtilClass(trace_logger)
    response = common_util.create_postgresql_log(
        data_copy["e"],
        data_copy["param"],
        data_copy["value"],
        data_copy["stackTrace"]
    )
    assert response == {
        "errorInfo": {
            "errorCode": "991014",
            "message": logUtil.message_build(MessageConstClass.ERRORS["991014"]["message"], "991014")
        }
    }
    print(response)


# No17.「引数．例外オブジェクト．エラーコード」の前2桁=26（26 クラス — 無効なSQL文の名前）の場合
def test_create_postgresql_log_case17():
    data_copy = DATA.copy()
    data_copy["e"].setter("26000", "test_error")
    common_util = CommonUtilClass(trace_logger)
    response = common_util.create_postgresql_log(
        data_copy["e"],
        data_copy["param"],
        data_copy["value"],
        data_copy["stackTrace"]
    )
    assert response == {
        "errorInfo": {
            "errorCode": "991015",
            "message": logUtil.message_build(MessageConstClass.ERRORS["991015"]["message"], "991015")
        }
    }
    print(response)


# No18.「引数．例外オブジェクト．エラーコード」の前2桁=27（27クラス — トリガによるデータ変更違反）の場合
def test_create_postgresql_log_case18():
    data_copy = DATA.copy()
    data_copy["e"].setter("27000", "test_error")
    common_util = CommonUtilClass(trace_logger)
    response = common_util.create_postgresql_log(
        data_copy["e"],
        data_copy["param"],
        data_copy["value"],
        data_copy["stackTrace"]
    )
    assert response == {
        "errorInfo": {
            "errorCode": "991016",
            "message": logUtil.message_build(MessageConstClass.ERRORS["991016"]["message"], "991016")
        }
    }
    print(response)


# No19.「引数．例外オブジェクト．エラーコード」の前2桁=28（28 クラス — 無効な認証指定）の場合
def test_create_postgresql_log_case19():
    data_copy = DATA.copy()
    data_copy["e"].setter("28000", "test_error")
    common_util = CommonUtilClass(trace_logger)
    response = common_util.create_postgresql_log(
        data_copy["e"],
        data_copy["param"],
        data_copy["value"],
        data_copy["stackTrace"]
    )
    assert response == {
        "errorInfo": {
            "errorCode": "991017",
            "message": logUtil.message_build(MessageConstClass.ERRORS["991017"]["message"], "991017")
        }
    }
    print(response)


# No20.「引数．例外オブジェクト．エラーコード」の前2桁=2B（2B クラス — 依存する権限記述子がまだ存在する）の場合
def test_create_postgresql_log_case20():
    data_copy = DATA.copy()
    data_copy["e"].setter("2B000", "test_error")
    common_util = CommonUtilClass(trace_logger)
    response = common_util.create_postgresql_log(
        data_copy["e"],
        data_copy["param"],
        data_copy["value"],
        data_copy["stackTrace"]
    )
    assert response == {
        "errorInfo": {
            "errorCode": "991018",
            "message": logUtil.message_build(MessageConstClass.ERRORS["991018"]["message"], "991018")
        }
    }
    print(response)


# No21.「引数．例外オブジェクト．エラーコード」の前2桁=2D（2D クラス — 無効なトランザクションの終了）の場合
def test_create_postgresql_log_case21():
    data_copy = DATA.copy()
    data_copy["e"].setter("2D000", "test_error")
    common_util = CommonUtilClass(trace_logger)
    response = common_util.create_postgresql_log(
        data_copy["e"],
        data_copy["param"],
        data_copy["value"],
        data_copy["stackTrace"]
    )
    assert response == {
        "errorInfo": {
            "errorCode": "991019",
            "message": logUtil.message_build(MessageConstClass.ERRORS["991019"]["message"], "991019")
        }
    }
    print(response)


# No22.「引数．例外オブジェクト．エラーコード」の前2桁=2F（2F クラス — SQL関数例外）の場合
def test_create_postgresql_log_case22():
    data_copy = DATA.copy()
    data_copy["e"].setter("2F000", "test_error")
    common_util = CommonUtilClass(trace_logger)
    response = common_util.create_postgresql_log(
        data_copy["e"],
        data_copy["param"],
        data_copy["value"],
        data_copy["stackTrace"]
    )
    assert response == {
        "errorInfo": {
            "errorCode": "991020",
            "message": logUtil.message_build(MessageConstClass.ERRORS["991020"]["message"], "991020")
        }
    }
    print(response)


# No23.「引数．例外オブジェクト．エラーコード」の前2桁=34（34クラス — 無効なカーソル名称）の場合
def test_create_postgresql_log_case23():
    data_copy = DATA.copy()
    data_copy["e"].setter("34000", "test_error")
    common_util = CommonUtilClass(trace_logger)
    response = common_util.create_postgresql_log(
        data_copy["e"],
        data_copy["param"],
        data_copy["value"],
        data_copy["stackTrace"]
    )
    assert response == {
        "errorInfo": {
            "errorCode": "991021",
            "message": logUtil.message_build(MessageConstClass.ERRORS["991021"]["message"], "991021")
        }
    }
    print(response)


# No24.「引数．例外オブジェクト．エラーコード」の前2桁=38（38 クラス — 外部関数例外）の場合
def test_create_postgresql_log_case24():
    data_copy = DATA.copy()
    data_copy["e"].setter("38000", "test_error")
    common_util = CommonUtilClass(trace_logger)
    response = common_util.create_postgresql_log(
        data_copy["e"],
        data_copy["param"],
        data_copy["value"],
        data_copy["stackTrace"]
    )
    assert response == {
        "errorInfo": {
            "errorCode": "991022",
            "message": logUtil.message_build(MessageConstClass.ERRORS["991022"]["message"], "991022")
        }
    }
    print(response)


# No25.「引数．例外オブジェクト．エラーコード」の前2桁=39（39 クラス — 外部関数呼び出し例外）の場合
def test_create_postgresql_log_case25():
    data_copy = DATA.copy()
    data_copy["e"].setter("39000", "test_error")
    common_util = CommonUtilClass(trace_logger)
    response = common_util.create_postgresql_log(
        data_copy["e"],
        data_copy["param"],
        data_copy["value"],
        data_copy["stackTrace"]
    )
    assert response == {
        "errorInfo": {
            "errorCode": "991023",
            "message": logUtil.message_build(MessageConstClass.ERRORS["991023"]["message"], "991023")
        }
    }
    print(response)


# No26.「引数．例外オブジェクト．エラーコード」の前2桁=3B（3B クラス — セーブポイント例外）の場合
def test_create_postgresql_log_case26():
    data_copy = DATA.copy()
    data_copy["e"].setter("3B000", "test_error")
    common_util = CommonUtilClass(trace_logger)
    response = common_util.create_postgresql_log(
        data_copy["e"],
        data_copy["param"],
        data_copy["value"],
        data_copy["stackTrace"]
    )
    assert response == {
        "errorInfo": {
            "errorCode": "991024",
            "message": logUtil.message_build(MessageConstClass.ERRORS["991024"]["message"], "991024")
        }
    }
    print(response)


# No27.「引数．例外オブジェクト．エラーコード」の前2桁=3D（3Dクラス — 無効なカタログ名称）の場合
def test_create_postgresql_log_case27():
    data_copy = DATA.copy()
    data_copy["e"].setter("3D000", "test_error")
    common_util = CommonUtilClass(trace_logger)
    response = common_util.create_postgresql_log(
        data_copy["e"],
        data_copy["param"],
        data_copy["value"],
        data_copy["stackTrace"]
    )
    assert response == {
        "errorInfo": {
            "errorCode": "991025",
            "message": logUtil.message_build(MessageConstClass.ERRORS["991025"]["message"], "991025")
        }
    }
    print(response)


# No28.「引数．例外オブジェクト．エラーコード」の前2桁=3F（3F クラス — 無効なスキーマ名称）の場合
def test_create_postgresql_log_case28():
    data_copy = DATA.copy()
    data_copy["e"].setter("3F000", "test_error")
    common_util = CommonUtilClass(trace_logger)
    response = common_util.create_postgresql_log(
        data_copy["e"],
        data_copy["param"],
        data_copy["value"],
        data_copy["stackTrace"]
    )
    assert response == {
        "errorInfo": {
            "errorCode": "991026",
            "message": logUtil.message_build(MessageConstClass.ERRORS["991026"]["message"], "991026")
        }
    }
    print(response)


# No29.「引数．例外オブジェクト．エラーコード」の前2桁=40（40 クラス — トランザクションロールバック）の場合
def test_create_postgresql_log_case29():
    data_copy = DATA.copy()
    data_copy["e"].setter("40000", "test_error")
    common_util = CommonUtilClass(trace_logger)
    response = common_util.create_postgresql_log(
        data_copy["e"],
        data_copy["param"],
        data_copy["value"],
        data_copy["stackTrace"]
    )
    assert response == {
        "errorInfo": {
            "errorCode": "991027",
            "message": logUtil.message_build(MessageConstClass.ERRORS["991027"]["message"], "991027")
        }
    }
    print(response)


# No30.「引数．例外オブジェクト．エラーコード」の前2桁=42（42 クラス — 構文エラー、もしくはアクセスロール違反）の場合
def test_create_postgresql_log_case30():
    data_copy = DATA.copy()
    data_copy["e"].setter("42000", "test_error")
    common_util = CommonUtilClass(trace_logger)
    response = common_util.create_postgresql_log(
        data_copy["e"],
        data_copy["param"],
        data_copy["value"],
        data_copy["stackTrace"]
    )
    assert response == {
        "errorInfo": {
            "errorCode": "991028",
            "message": logUtil.message_build(MessageConstClass.ERRORS["991028"]["message"], "991028")
        }
    }
    print(response)


# No31.「引数．例外オブジェクト．エラーコード」の前2桁=44（44 クラス — 検査オプションに伴う違反）の場合
def test_create_postgresql_log_case31():
    data_copy = DATA.copy()
    data_copy["e"].setter("44000", "test_error")
    common_util = CommonUtilClass(trace_logger)
    response = common_util.create_postgresql_log(
        data_copy["e"],
        data_copy["param"],
        data_copy["value"],
        data_copy["stackTrace"]
    )
    assert response == {
        "errorInfo": {
            "errorCode": "991029",
            "message": logUtil.message_build(MessageConstClass.ERRORS["991029"]["message"], "991029")
        }
    }
    print(response)


# No32.「引数．例外オブジェクト．エラーコード」の前2桁=53（53クラス — リソース不足）の場合
def test_create_postgresql_log_case32():
    data_copy = DATA.copy()
    data_copy["e"].setter("53000", "test_error")
    common_util = CommonUtilClass(trace_logger)
    response = common_util.create_postgresql_log(
        data_copy["e"],
        data_copy["param"],
        data_copy["value"],
        data_copy["stackTrace"]
    )
    assert response == {
        "errorInfo": {
            "errorCode": "991030",
            "message": logUtil.message_build(MessageConstClass.ERRORS["991030"]["message"], "991030")
        }
    }
    print(response)


# No33.「引数．例外オブジェクト．エラーコード」の前2桁=54（54 クラス — プログラム制限の超過）の場合
def test_create_postgresql_log_case33():
    data_copy = DATA.copy()
    data_copy["e"].setter("54000", "test_error")
    common_util = CommonUtilClass(trace_logger)
    response = common_util.create_postgresql_log(
        data_copy["e"],
        data_copy["param"],
        data_copy["value"],
        data_copy["stackTrace"]
    )
    assert response == {
        "errorInfo": {
            "errorCode": "991031",
            "message": logUtil.message_build(MessageConstClass.ERRORS["991031"]["message"], "991031")
        }
    }
    print(response)


# No34.「引数．例外オブジェクト．エラーコード」の前2桁=55（55 クラス — 必要条件を満たさないオブジェクト）の場合
def test_create_postgresql_log_case34():
    data_copy = DATA.copy()
    data_copy["e"].setter("55000", "test_error")
    common_util = CommonUtilClass(trace_logger)
    response = common_util.create_postgresql_log(
        data_copy["e"],
        data_copy["param"],
        data_copy["value"],
        data_copy["stackTrace"]
    )
    assert response == {
        "errorInfo": {
            "errorCode": "991032",
            "message": logUtil.message_build(MessageConstClass.ERRORS["991032"]["message"], "991032")
        }
    }
    print(response)


# No35.「引数．例外オブジェクト．エラーコード」の前2桁=57（57 クラス — 操作の介入）の場合かつ引数．例外オブジェクト．エラーコード=57014の場合
def test_create_postgresql_log_case35():
    data_copy = DATA.copy()
    data_copy["e"].setter("57014", "test_error")
    common_util = CommonUtilClass(trace_logger)
    response = common_util.create_postgresql_log(
        data_copy["e"],
        data_copy["param"],
        data_copy["value"],
        data_copy["stackTrace"]
    )
    assert response == {
        "errorInfo": {
            "errorCode": "991101",
            "message": logUtil.message_build(MessageConstClass.ERRORS["991101"]["message"], "991101")
        }
    }
    print(response)


# No36.「引数．例外オブジェクト．エラーコード」の前2桁=57（57 クラス — 操作の介入）の場合かつ引数．例外オブジェクト．エラーコード=57014以外の場合
def test_create_postgresql_log_case36():
    data_copy = DATA.copy()
    data_copy["e"].setter("57000", "test_error")
    common_util = CommonUtilClass(trace_logger)
    response = common_util.create_postgresql_log(
        data_copy["e"],
        data_copy["param"],
        data_copy["value"],
        data_copy["stackTrace"]
    )
    assert response == {
        "errorInfo": {
            "errorCode": "991033",
            "message": logUtil.message_build(MessageConstClass.ERRORS["991033"]["message"], "991033")
        }
    }
    print(response)


# No37.「引数．例外オブジェクト．エラーコード」の前2桁=58（58 クラス — システムエラー（外部原因によるPostgreSQL自体のエラー））の場合
def test_create_postgresql_log_case37():
    data_copy = DATA.copy()
    data_copy["e"].setter("58000", "test_error")
    common_util = CommonUtilClass(trace_logger)
    response = common_util.create_postgresql_log(
        data_copy["e"],
        data_copy["param"],
        data_copy["value"],
        data_copy["stackTrace"]
    )
    assert response == {
        "errorInfo": {
            "errorCode": "991034",
            "message": logUtil.message_build(MessageConstClass.ERRORS["991034"]["message"], "991034")
        }
    }
    print(response)


# No38.「引数．例外オブジェクト．エラーコード」の前2桁=F0（F0クラス — 設定ファイルエラー）の場合
def test_create_postgresql_log_case38():
    data_copy = DATA.copy()
    data_copy["e"].setter("F0000", "test_error")
    common_util = CommonUtilClass(trace_logger)
    response = common_util.create_postgresql_log(
        data_copy["e"],
        data_copy["param"],
        data_copy["value"],
        data_copy["stackTrace"]
    )
    assert response == {
        "errorInfo": {
            "errorCode": "991035",
            "message": logUtil.message_build(MessageConstClass.ERRORS["991035"]["message"], "991035")
        }
    }
    print(response)


# No39.「引数．例外オブジェクト．エラーコード」の前2桁=P0（P0 クラス — PL/pgSQLエラー）の場合
def test_create_postgresql_log_case39():
    data_copy = DATA.copy()
    data_copy["e"].setter("P0000", "test_error")
    common_util = CommonUtilClass(trace_logger)
    response = common_util.create_postgresql_log(
        data_copy["e"],
        data_copy["param"],
        data_copy["value"],
        data_copy["stackTrace"]
    )
    assert response == {
        "errorInfo": {
            "errorCode": "991036",
            "message": logUtil.message_build(MessageConstClass.ERRORS["991036"]["message"], "991036")
        }
    }
    print(response)


# No40.「引数．例外オブジェクト．エラーコード」の前2桁=XX（XX クラス — 内部エラー）の場合
def test_create_postgresql_log_case40():
    data_copy = DATA.copy()
    data_copy["e"].setter("XX000", "test_error")
    common_util = CommonUtilClass(trace_logger)
    response = common_util.create_postgresql_log(
        data_copy["e"],
        data_copy["param"],
        data_copy["value"],
        data_copy["stackTrace"]
    )
    assert response == {
        "errorInfo": {
            "errorCode": "991037",
            "message": logUtil.message_build(MessageConstClass.ERRORS["991037"]["message"], "991037")
        }
    }
    print(response)


# No41.上記のすべてに当てはまらない場合
def test_create_postgresql_log_case41():
    data_copy = DATA.copy()
    data_copy["e"].setter("TT000", "test_error")
    common_util = CommonUtilClass(trace_logger)
    response = common_util.create_postgresql_log(
        data_copy["e"],
        data_copy["param"],
        data_copy["value"],
        data_copy["stackTrace"]
    )
    assert response == {
        "errorInfo": {
            "errorCode": "999999",
            "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
        }
    }
    print(response)


# 03.終了処理
# No42.正常系
def test_create_postgresql_log_case42():
    data_copy = DATA.copy()
    data_copy["e"].setter("TT000", "test_error")
    common_util = CommonUtilClass(trace_logger)
    response = common_util.create_postgresql_log(
        data_copy["e"],
        data_copy["param"],
        data_copy["value"],
        data_copy["stackTrace"]
    )
    assert response == {
        "errorInfo": {
            "errorCode": "999999",
            "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
        }
    }
    print(response)
