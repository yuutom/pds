from fastapi.testclient import TestClient
from app import app
from fastapi import Request
import pytest
import util.logUtil as logUtil
from util.commonUtil import CommonUtilClass
from util.postgresDbUtil import PostgresDbUtilClass
from util.billUtil import BillUtilClass
from exceptionClass.PDSException import PDSException
from const.messageConst import MessageConstClass
from const.systemConst import SystemConstClass

client = TestClient(app)


trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
common_util = CommonUtilClass(trace_logger)
bill_util = BillUtilClass(trace_logger)

common_db_connection_resource: PostgresDbUtilClass = None
common_db_info_response = common_util.get_common_db_info_and_connection()

DATA = {
    "apiType": "1",
    "execStatus": True,
    "count": 600,
    "chargeBillList": [
        (5, 100, 1000),
        (1, 500, 2000)
    ]
}


# 01.引数検証処理チェック処理
# 累進請求金額計算処理_01.引数検証処理チェック　シート参照
# No1_1.引数．API種別の値が設定されていない(空値)
def test_progressive_billing_exec_case1_1():
    data_copy = DATA.copy()
    data_copy["apiType"] = None
    with pytest.raises(PDSException) as e:
        bill_util.progressive_billing_exec(apiType=data_copy["apiType"], execStatus=data_copy["execStatus"], count=data_copy["count"], chargeBillList=data_copy["chargeBillList"])

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "API種別")
    }
    print(e)


# No1_2.引数．API種別の値が設定されている
def test_progressive_billing_exec_case1_2():
    data_copy = DATA.copy()
    response = bill_util.progressive_billing_exec(apiType=data_copy["apiType"], execStatus=data_copy["execStatus"], count=data_copy["count"], chargeBillList=data_copy["chargeBillList"])
    assert response == {
        "result": True,
        "progressiveBilling": response["progressiveBilling"]
    }
    print(response)


# No1_3.引数．実行ステータスの値が設定されていない(空値)
def test_progressive_billing_exec_case1_3():
    data_copy = DATA.copy()
    data_copy["execStatus"] = None
    with pytest.raises(PDSException) as e:
        bill_util.progressive_billing_exec(apiType=data_copy["apiType"], execStatus=data_copy["execStatus"], count=data_copy["count"], chargeBillList=data_copy["chargeBillList"])

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "実行ステータス")
    }
    print(e)


# No1_4.引数．実行ステータスの値が設定されている
def test_progressive_billing_exec_case1_4():
    data_copy = DATA.copy()
    response = bill_util.progressive_billing_exec(apiType=data_copy["apiType"], execStatus=data_copy["execStatus"], count=data_copy["count"], chargeBillList=data_copy["chargeBillList"])
    assert response == {
        "result": True,
        "progressiveBilling": response["progressiveBilling"]
    }
    print(response)


# No1_5.引数．カウントの値が設定されていない(空値)
def test_progressive_billing_exec_case1_5():
    data_copy = DATA.copy()
    data_copy["count"] = None
    with pytest.raises(PDSException) as e:
        bill_util.progressive_billing_exec(apiType=data_copy["apiType"], execStatus=data_copy["execStatus"], count=data_copy["count"], chargeBillList=data_copy["chargeBillList"])

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "カウント")
    }
    print(e)


# No1_6.引数．カウントの値が設定されている
def test_progressive_billing_exec_case1_6():
    data_copy = DATA.copy()
    response = bill_util.progressive_billing_exec(apiType=data_copy["apiType"], execStatus=data_copy["execStatus"], count=data_copy["count"], chargeBillList=data_copy["chargeBillList"])
    assert response == {
        "result": True,
        "progressiveBilling": response["progressiveBilling"]
    }
    print(response)


# No1_7.引数．請求金額取得結果リスト．金額の値が設定されていない(空値)
def test_progressive_billing_exec_case1_7():
    data_copy = DATA.copy()
    data_copy["chargeBillList"] = [
        (5, 100, 1000),
        (None, 500, 2000)
    ]
    with pytest.raises(PDSException) as e:
        bill_util.progressive_billing_exec(apiType=data_copy["apiType"], execStatus=data_copy["execStatus"], count=data_copy["count"], chargeBillList=data_copy["chargeBillList"])

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "請求金額取得結果リスト．金額")
    }
    print(e)


# No1_8.引数．請求金額取得結果リスト．金額の値が設定されている
def test_progressive_billing_exec_case1_8():
    data_copy = DATA.copy()
    response = bill_util.progressive_billing_exec(apiType=data_copy["apiType"], execStatus=data_copy["execStatus"], count=data_copy["count"], chargeBillList=data_copy["chargeBillList"])
    assert response == {
        "result": True,
        "progressiveBilling": response["progressiveBilling"]
    }
    print(response)


# No1_9.引数．請求金額取得結果リスト．料金実行回数幅Fromの値が設定されていない(空値)
def test_progressive_billing_exec_case1_9():
    data_copy = DATA.copy()
    data_copy["chargeBillList"] = [
        (5, 100, 1000),
        (10, None, 2000)
    ]
    with pytest.raises(PDSException) as e:
        bill_util.progressive_billing_exec(apiType=data_copy["apiType"], execStatus=data_copy["execStatus"], count=data_copy["count"], chargeBillList=data_copy["chargeBillList"])

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "請求金額取得結果リスト．料金実行回数幅From")
    }
    print(e)


# No1_10.引数．請求金額取得結果リスト．料金実行回数幅Fromの値が設定されている
def test_progressive_billing_exec_case1_10():
    data_copy = DATA.copy()
    response = bill_util.progressive_billing_exec(apiType=data_copy["apiType"], execStatus=data_copy["execStatus"], count=data_copy["count"], chargeBillList=data_copy["chargeBillList"])
    assert response == {
        "result": True,
        "progressiveBilling": response["progressiveBilling"]
    }
    print(response)


# No1_11.引数．請求金額取得結果リスト．料金実行回数幅Toの値が設定されていない(空値)
def test_progressive_billing_exec_case1_11():
    data_copy = DATA.copy()
    data_copy["chargeBillList"] = [
        (5, 100, 1000),
        (10, 200, None)
    ]
    with pytest.raises(PDSException) as e:
        bill_util.progressive_billing_exec(apiType=data_copy["apiType"], execStatus=data_copy["execStatus"], count=data_copy["count"], chargeBillList=data_copy["chargeBillList"])

    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "請求金額取得結果リスト．料金実行回数幅To")
    }
    print(e)


# No1_12.引数．請求金額取得結果リスト．料金実行回数幅Toの値が設定されている
def test_progressive_billing_exec_case1_12():
    data_copy = DATA.copy()
    response = bill_util.progressive_billing_exec(apiType=data_copy["apiType"], execStatus=data_copy["execStatus"], count=data_copy["count"], chargeBillList=data_copy["chargeBillList"])
    assert response == {
        "result": True,
        "progressiveBilling": response["progressiveBilling"]
    }
    print(response)


# 02.請求金額初期化
# 正常系
# No2.「変数．累進請求金額」を初期化する
def test_progressive_billing_exec_case2():
    data_copy = DATA.copy()
    response = bill_util.progressive_billing_exec(apiType=data_copy["apiType"], execStatus=data_copy["execStatus"], count=data_copy["count"], chargeBillList=data_copy["chargeBillList"])
    assert response == {
        "result": True,
        "progressiveBilling": response["progressiveBilling"]
    }
    print(response)


# 03.実行ステータスチェック処理
# 正常系
# No3.「引数．実行ステータス」がtrueの場合、「04.料金実行回数幅チェック処理」に遷移する
def test_progressive_billing_exec_case3():
    data_copy = DATA.copy()
    data_copy["execStatus"] = True
    response = bill_util.progressive_billing_exec(apiType=data_copy["apiType"], execStatus=data_copy["execStatus"], count=data_copy["count"], chargeBillList=data_copy["chargeBillList"])
    assert response == {
        "result": True,
        "progressiveBilling": response["progressiveBilling"]
    }
    print(response)


# 正常系
# No4.「引数．実行ステータス」がfalseの場合、「09.終了処理」に遷移する
def test_progressive_billing_exec_case4():
    data_copy = DATA.copy()
    data_copy["execStatus"] = False
    response = bill_util.progressive_billing_exec(apiType=data_copy["apiType"], execStatus=data_copy["execStatus"], count=data_copy["count"], chargeBillList=data_copy["chargeBillList"])
    assert response == {
        "result": True,
        "progressiveBilling": response["progressiveBilling"]
    }
    print(response)


# 「請求金額取得結果リスト」の要素数分繰り返す
# 「請求金額取得結果リスト」の要素数が0の場合
def test_progressive_billing_exec_case5():
    data_copy = DATA.copy()
    data_copy["chargeBillList"] = []
    response = bill_util.progressive_billing_exec(apiType=data_copy["apiType"], execStatus=data_copy["execStatus"], count=data_copy["count"], chargeBillList=data_copy["chargeBillList"])
    assert response == {
        "result": True,
        "progressiveBilling": response["progressiveBilling"]
    }
    print(response)


# 「請求金額取得結果リスト」の要素数が1以上の場合
def test_progressive_billing_exec_case6():
    data_copy = DATA.copy()
    data_copy["chargeBillList"] = [
        (5, 100, 1000),
        (10, 200, 2000),
        (15, 300, 5000),
    ]
    response = bill_util.progressive_billing_exec(apiType=data_copy["apiType"], execStatus=data_copy["execStatus"], count=data_copy["count"], chargeBillList=data_copy["chargeBillList"])
    assert response == {
        "result": True,
        "progressiveBilling": response["progressiveBilling"]
    }
    print(response)


# 04.料金実行回数幅チェック処理
# 「引数．カウント」が「請求金額取得結果リスト[変数．累進金額ループ数]．料金実行回数幅To」を超過する場合、「05.累進金額回数取得処理（To超過）」に遷移する
def test_progressive_billing_exec_case7():
    data_copy = DATA.copy()
    data_copy["chargeBillList"] = [(5, 100, DATA["count"] - 1)]
    response = bill_util.progressive_billing_exec(apiType=data_copy["apiType"], execStatus=data_copy["execStatus"], count=data_copy["count"], chargeBillList=data_copy["chargeBillList"])
    assert response == {
        "result": True,
        "progressiveBilling": response["progressiveBilling"]
    }
    print(response)


# 「引数．カウント」が「請求金額取得結果リスト[変数．累進金額ループ数]．料金実行回数幅To」以下の場合、「06.累進金額回数取得処理（To以下）」に遷移する
def test_progressive_billing_exec_case8():
    data_copy = DATA.copy()
    data_copy["chargeBillList"] = [(5, 100, DATA["count"] + 1)]
    response = bill_util.progressive_billing_exec(apiType=data_copy["apiType"], execStatus=data_copy["execStatus"], count=data_copy["count"], chargeBillList=data_copy["chargeBillList"])
    assert response == {
        "result": True,
        "progressiveBilling": response["progressiveBilling"]
    }
    print(response)


# 05.累進金額回数取得処理（To超過）
# 「引数．請求金額取得結果リスト」をもとに、「変数．累進金額回数」を計算して格納する
def test_progressive_billing_exec_case9():
    data_copy = DATA.copy()
    data_copy["chargeBillList"] = [(5, 100, DATA["count"] - 1)]
    response = bill_util.progressive_billing_exec(apiType=data_copy["apiType"], execStatus=data_copy["execStatus"], count=data_copy["count"], chargeBillList=data_copy["chargeBillList"])
    assert response == {
        "result": True,
        "progressiveBilling": response["progressiveBilling"]
    }
    print(response)


# 06.累進金額回数取得処理（To以下）
# 「引数．請求金額取得結果リスト」と「引数．カウント」をもとに、「変数．累進金額回数」を計算して格納する
def test_progressive_billing_exec_case10():
    data_copy = DATA.copy()
    data_copy["chargeBillList"] = [(5, 100, DATA["count"] + 1)]
    response = bill_util.progressive_billing_exec(apiType=data_copy["apiType"], execStatus=data_copy["execStatus"], count=data_copy["count"], chargeBillList=data_copy["chargeBillList"])
    assert response == {
        "result": True,
        "progressiveBilling": response["progressiveBilling"]
    }
    print(response)


# 07.累進金額計算処理
# 引数．請求金額取得結果リスト」と「変数．累進金額回数」をもとに、「変数．累進金額」を計算して格納する
def test_progressive_billing_exec_case11():
    data_copy = DATA.copy()
    data_copy["chargeBillList"] = [
        (5, 100, 1000),
        (10, 200, 2000),
        (15, 300, 5000),
    ]
    response = bill_util.progressive_billing_exec(apiType=data_copy["apiType"], execStatus=data_copy["execStatus"], count=data_copy["count"], chargeBillList=data_copy["chargeBillList"])
    assert response == {
        "result": True,
        "progressiveBilling": response["progressiveBilling"]
    }
    print(response)


# 08.累進金額計算処理
# 「変数．累進請求金額」に「変数．累進金額」を加算する
# 境界値のテストや複数の金額にまたぐテストなどパターンを作成して実施する
# ※金額計算なので、パターン洗い出しから実施。
# すべての要素でcount <= chargeBillElement[2]である場合
def test_progressive_billing_exec_case12_1():
    data_copy = DATA.copy()
    data_copy["count"] = 600
    data_copy["chargeBillList"] = [
        (5, 100, 1000),
        (10, 200, 2000),
        (15, 300, 5000),
    ]
    response = bill_util.progressive_billing_exec(apiType=data_copy["apiType"], execStatus=data_copy["execStatus"], count=data_copy["count"], chargeBillList=data_copy["chargeBillList"])
    assert response == {
        "result": True,
        "progressiveBilling": response["progressiveBilling"]
    }
    print(response)


# count > chargeBillElement[2]とcount <= chargeBillElement[2]の要素が混じっている場合
def test_progressive_billing_exec_case12_2():
    data_copy = DATA.copy()
    data_copy["count"] = 600
    data_copy["chargeBillList"] = [
        (5, 100, 200),
        (20, 200, 700),
        (15, 300, 500),
    ]
    response = bill_util.progressive_billing_exec(apiType=data_copy["apiType"], execStatus=data_copy["execStatus"], count=data_copy["count"], chargeBillList=data_copy["chargeBillList"])
    assert response == {
        "result": True,
        "progressiveBilling": response["progressiveBilling"]
    }
    print(response)


# すべての要素でcount > chargeBillElement[2]である場合
def test_progressive_billing_exec_case12_3():
    data_copy = DATA.copy()
    data_copy["count"] = 1000
    data_copy["chargeBillList"] = [
        (5, 100, 100),
        (20, 200, 400),
        (15, 300, 300),
    ]
    response = bill_util.progressive_billing_exec(apiType=data_copy["apiType"], execStatus=data_copy["execStatus"], count=data_copy["count"], chargeBillList=data_copy["chargeBillList"])
    assert response == {
        "result": True,
        "progressiveBilling": response["progressiveBilling"]
    }
    print(response)


# 09.終了処理
# 正常系
def test_progressive_billing_exec_case13():
    data_copy = DATA.copy()
    response = bill_util.progressive_billing_exec(apiType=data_copy["apiType"], execStatus=data_copy["execStatus"], count=data_copy["count"], chargeBillList=data_copy["chargeBillList"])
    assert response == {
        "result": True,
        "progressiveBilling": response["progressiveBilling"]
    }
    print(response)
