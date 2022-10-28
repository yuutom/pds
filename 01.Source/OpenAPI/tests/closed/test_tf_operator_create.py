from fastapi.testclient import TestClient
from const.sqlConst import SqlConstClass
from app import app
from fastapi import Request
import pytest
from util.commonUtil import get_str_datetime_in_X_days
from pytest_mock.plugin import MockerFixture
from util.tokenUtil import TokenUtilClass
import util.logUtil as logUtil
import json
from const.systemConst import SystemConstClass
from util.postgresDbUtil import PostgresDbUtilClass
from const.wbtConst import wbtConstClass
from const.fileNameConst import FileNameConstClass
from util.commonUtil import CommonUtilClass
from util.fileUtil import NoHeaderOneItemCsvStringClass

client = TestClient(app)

BEARER = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0Zk9wZXJhdG9ySWQiOiJsLXRlc3QiLCJ0Zk9wZXJhdG9yTmFtZSI6Ilx1MzBlZFx1MzBiMFx1MzBhNFx1MzBmM1x1MzBjNlx1MzBiOVx1MzBjOCIsInRmT3BlcmF0b3JQYXNzd29yZFJlc2V0RmxnIjpmYWxzZSwiYWNjZXNzVG9rZW4iOiJiZGE4ZGY3OThiYzViZGZhMWZkODIyNmRiYmQ0OTMyMTY5ZmY5MjAzNWM0YzFlY2FjZjY2OGUyYzk2ZjAwZThlZTUxNTBiNGM0NTc0NjlkN2I4YmY1NzIxZDZlM2NiNzFiY2RiYzA3ODRiYzcyZWVlNjk1OGE3NTBiMWJkMWEzZWFmZWQ0OWFhNWU0ODZjYzQyZmM3OWNhMWY3MGQzZmM3Yzc0YzE5NjM3ODUzMjRhZDRhNGM0NjkxOGE4NjQ1N2ZiODE3NDU1MCIsImV4cCI6MTY2MTc0NjY3MX0.LCRjPEqKMkRQ_phaYnO7S7pd3SU_rgon-wsX14DBsPA"
ACCESS_TOKEN = "bda8df798bc5bdfa1fd8226dbbd4932169ff92035c4c1ecacf668e2c96f00e8ee5150b4c457469d7b8bf5721d6e3cb71bcdbc0784bc72eee6958a750b1bd1a3eafed49aa5e486cc42fc79ca1f70d3fc7c74c1963785324ad4a4c46918a86457fb8174550"
HEADER = {"Content-Type": "application/json", "timeStamp": "2022/08/23 15:12:01.690", "accessToken": ACCESS_TOKEN, "Authorization": "Bearer " + BEARER}
DATA = {
    "tfOperatorId": "create-unit-test",
    "tfOperatorName": "単体登録",
    "tfOperatorMail": "touroku@trk.co.jp"
}
TF_OPERATOR_INFO = {
    "tfOperatorId": "pc-test",
    "tfOperatorName": "変更太郎"
}


@pytest.fixture
def create_header():
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_closed(tfOperatorInfo=TF_OPERATOR_INFO, accessToken=None)
    yield {
        "header": {
            "Content-Type": "application/json",
            "accessToken": token_result["accessToken"],
            "timeStamp": "2022/08/23 15:12:01.690",
            "Authorization": "Bearer " + token_result["jwt"]
        }
    }


# No1.01.メイン処理_01.アクセストークン検証処理　異常系　アクセストークン検証処理が失敗する
def test_tf_operator_create_case1(create_header):
    header = create_header["header"]
    header["accessToken"] = None
    response = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020001",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020014",
                "message": response.json()["errorInfo"][1]["message"]
            },
            {
                "errorCode": "020003",
                "message": response.json()["errorInfo"][2]["message"]
            }
        ]
    }
    print(response.json())


# No2.01.メイン処理_01.アクセストークン検証処理　正常系　アクセストークン検証処理が成功する
# No5.01.メイン処理_03.パラメータ検証処理　正常系　パラメータ検証処理が成功する
# No8.01.メイン処理_05.DB接続準備処理　正常系　接続に成功する
# No11.01.メイン処理_06.TFオペレータ取得処理　正常系　TFオペレータ取得処理のカウントが0件
# No13.01.メイン処理_08.仮パスワード生成処理　正常系　仮パスワード生成処理に成功する
# No15.01.メイン処理_09.CSVファイル作成処理　正常系　CSVファイル作成処理に成功する
# No17.01.メイン処理_10.トランザクション作成処理 正常系 トランザクション作成処理が成功する
# No19.01.メイン処理_11.TFオペレータ登録処理　正常系　TFオペレータ登録処理が成功する
# No22.01.メイン処理_13.WBT新規メール情報登録API実行処理　正常系　WBT新規メール情報登録API実行処理が成功する
# No25.01.メイン処理_15.WBTファイル登録API実行処理　正常系　WBTファイル登録API実行処理が成功する
# No28.01.メイン処理_17.トランザクションコミット処理　正常系　トランザクションコミット処理が成功する
# No30.01.メイン処理_18.パスワード通知CSVの削除処理　正常系　パスワード通知CSVの削除処理が成功する
# No31.01.メイン処理_18.パスワード通知CSVの削除処理　正常系　パスワード通知CSVの削除処理が成功する
# No33.01.メイン処理_19.アクセストークン発行処理　正常系　アクセストークン発行処理が成功する
# No36.01.メイン処理_21.終了処理　正常系　変数．エラー情報がない
# No37.02.パラメータ検証処理_01.パラメータ検証処理 タイムスタンプが正常な値
# No37.02.パラメータ検証処理_01.パラメータ検証処理 アクセストークンが正常な値
# No37.02.パラメータ検証処理_01.パラメータ検証処理 TFオペレータIDが正常な値
# No37.02.パラメータ検証処理_01.パラメータ検証処理 TFオペレータ名が正常な値
# No37.02.パラメータ検証処理_01.パラメータ検証処理 TFオペレータメールアドレスが正常な値
# No37.02.パラメータ検証処理_02.終了処理 変数．エラー情報がない
# No38.02.パラメータ検証処理_02.終了処理 変数．エラー情報がない
# No43.03.ロールバック処理_03.終了処理 正常系 変数．エラー情報がない
def test_tf_operator_create_case2(create_header):
    header = create_header["header"]
    response = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 02.共通エラーチェック処理
# No03.共通エラーチェック処理が成功
def test_tf_operator_create_case3(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    header["accessToken"] = "518302174323385ee79afc2e37e3783f15e48e43d75f004a83e41667996087770c5e474023c0d6969529b49a8fd553ca454e54adbf473ac1a129fd4b0314abc4d4f33e4349749110f5b1774db69d5f87944e3a86c7d3ee10390a825f8bf35f1813774c94"
    response = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "010004",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# 03.パラメータ検証処理
# No04.パラメータ検証処理が失敗する
def test_tf_operator_create_case4(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfOperatorId"] = ""
    response = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020001",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020016",
                "message": response.json()["errorInfo"][1]["message"]
            }
        ]
    }
    print(response.json())


# 04.共通エラーチェック処理
# No06.共通エラーチェック処理が成功（エラー情報有り）
def test_tf_operator_create_case6(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfOperatorId"] = ""
    response = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020001",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020016",
                "message": response.json()["errorInfo"][1]["message"]
            }
        ]
    }
    print(response.json())


# 05.DB接続準備処理
# No07.接続に失敗する
# 設定値を異常な値に変更する
def test_tf_operator_create_case7(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    # Exception
    mocker.patch("util.commonUtil.CommonUtilClass.get_secret_info").return_value = {"host": "test", "port": "test", "username": "test", "password": "test"}
    response = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "999999",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# 06.TFオペレータ取得処理
# No09.TFオペレータ取得処理の、カウントが1件
def test_tf_operator_create_case9(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["tfOperatorId"] = "TF-create-test"
    response = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(data_copy))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "030001",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No10.TFオペレータ取得処理が失敗する
def test_tf_operator_create_case10(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "TF_OPERATOR_REGISTER_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    response = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "991028",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# 07.共通エラーチェック処理
# No12.共通エラーチェック処理が成功（エラー情報有り）
def test_tf_operator_create_case12(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "TF_OPERATOR_REGISTER_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    response = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "991028",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# 09.CSVファイル作成処理
# No14.CSVファイル作成処理に失敗する
def test_tf_operator_create_case14(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(NoHeaderOneItemCsvStringClass, "__init__", side_effect=Exception('testException'))
    header = create_header["header"]
    response = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "999999",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# 10.トランザクション作成処理
# No16.トランザクション作成処理が失敗する
# →検証不可


# 11.TFオペレータ登録処理
# No18.TFオペレータ登録処理が失敗する
def test_tf_operator_create_case18(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "TF_OPERATOR_REGISTER_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    response = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "991028",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# 12.共通エラーチェック処理
# No20.共通エラーチェック処理が成功（エラー情報有り）
def test_tf_operator_create_case20(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "TF_OPERATOR_REGISTER_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    response = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "991028",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# 13.WBT新規メール情報登録API実行処理
# No21.WBT新規メール情報登録API実行処理が失敗する
def test_tf_operator_create_case21(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.commonUtil.CommonUtilClass.wbt_mails_add_api_exec").return_value = {"result": False}
    response = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "990011",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# 14.共通エラーチェック処理
# No23.共通エラーチェック処理が成功（エラー情報有り）
def test_tf_operator_create_case23(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.commonUtil.CommonUtilClass.wbt_mails_add_api_exec").return_value = {"result": False}
    response = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "990011",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# 15.WBTファイル登録API実行処理
# No24.WBTファイル登録API実行処理が失敗する
def test_tf_operator_create_case24(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.commonUtil.CommonUtilClass.wbt_file_add_api_exec").return_value = {"result": False}
    response = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "990013",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# 16.共通エラーチェック処理
# No26.WBTファイル登録API実行処理が失敗する
def test_tf_operator_create_case26(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.commonUtil.CommonUtilClass.wbt_file_add_api_exec").return_value = {"result": False}
    response = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "990013",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# 17.トランザクションコミット処理
# No27.トランザクションコミット処理が失敗する
def test_tf_operator_create_case27(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(PostgresDbUtilClass, "commit_transaction", side_effect=Exception('testException'))
    header = create_header["header"]
    response = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "999999",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# 18.パスワード通知CSVの削除処理
# No29.パスワード通知CSVの削除処理が失敗する
# →検証不可


# 19.アクセストークン発行処理
# No32.アクセストークン発行処理が失敗する
def test_tf_operator_create_case32(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.tokenUtil.TokenUtilClass.create_token_closed").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    response = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "999999",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# 20.共通エラーチェック処理
# No34.共通エラーチェック処理が成功（エラー情報有り）
def test_tf_operator_create_case34(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.tokenUtil.TokenUtilClass.create_token_closed").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    response = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "999999",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# 21.終了処理
# No35.変数．エラー情報がある(No.35でエラー）
def test_tf_operator_create_case35(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.tokenUtil.TokenUtilClass.create_token_closed").return_value = {"result": False, "errorInfo": {"errorCode": "999999", "message": "test-exception"}}
    response = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "999999",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No37.パラメータ検証処理_01.パラメータ検証処理　異常系　引数．ヘッダパラメータ．タイムスタンプ　値が設定されていない（空値）
def test_tf_operator_create_case37_1_1(create_header):
    header = create_header["header"]
    header["timeStamp"] = ""
    response = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020001",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020014",
                "message": response.json()["errorInfo"][1]["message"]
            },
            {
                "errorCode": "020003",
                "message": response.json()["errorInfo"][2]["message"]
            }
        ]
    }
    print(response.json())


# No37.パラメータ検証処理_01.パラメータ検証処理　異常系　引数．ヘッダパラメータ．タイムスタンプ　値が設定されている　文字列型である　24桁である
def test_tf_operator_create_case37_1_2(create_header):
    header = create_header["header"]
    header["timeStamp"] = "2022/08/23 15:12:01.6900"
    response = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020014",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020003",
                "message": response.json()["errorInfo"][1]["message"]
            }
        ]
    }
    print(response.json())


# No37.パラメータ検証処理_01.パラメータ検証処理　異常系　引数．ヘッダパラメータ．タイムスタンプ　値が設定されている　文字列型である　２４桁である
def test_tf_operator_create_case37_1_3(create_header):
    header = create_header["header"]
    header["timeStamp"] = "2022/08/23 15:12:01.6900"
    response = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020014",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020003",
                "message": response.json()["errorInfo"][1]["message"]
            }
        ]
    }
    print(response.json())


# No37.パラメータ検証処理_01.パラメータ検証処理　異常系　引数．ヘッダパラメータ．アクセストークン　値が設定されていない（空値）
def test_tf_operator_create_case37_2_1(create_header):
    header = create_header["header"]
    header["accessToken"] = ""
    response = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020001",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020014",
                "message": response.json()["errorInfo"][1]["message"]
            },
            {
                "errorCode": "020003",
                "message": response.json()["errorInfo"][2]["message"]
            }
        ]
    }
    print(response.json())


# No37.パラメータ検証処理_01.パラメータ検証処理　正常系　引数．ヘッダパラメータ．アクセストークン　値が設定されている　文字列型である　201桁である 入力可能文字以外が含まれる(全角)
def test_tf_operator_create_case37_2_2(create_header):
    header = create_header["header"]
    header["accessToken"] = "ＡＢＣＤＥＦＧＨＩＪ" * 20 + "Ｋ"
    response = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020014",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020003",
                "message": response.json()["errorInfo"][1]["message"]
            }
        ]
    }
    print(response.json())


# No37.パラメータ検証処理_01.パラメータ検証処理　異常系　引数．リクエストボディ．TFオペレータID　値が設定されていない（空値）
def test_tf_operator_create_case37_3_1(create_header):
    header = create_header["header"]
    DATA["tfOperatorId"] = ""
    response = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020001",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020016",
                "message": response.json()["errorInfo"][1]["message"]
            }
        ]
    }
    print(response.json())


# No37.パラメータ検証処理_01.パラメータ検証処理　異常系　引数．リクエストボディ．TFオペレータパスワード　値が設定されている　文字列型ではない　2桁である
def test_tf_operator_create_case37_3_2(create_header):
    header = create_header["header"]
    DATA["tfOperatorId"] = 12
    response = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020019",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020016",
                "message": response.json()["errorInfo"][1]["message"]
            }
        ]
    }
    print(response.json())


# No37.パラメータ検証処理_01.パラメータ検証処理　異常系　引数．リクエストボディ．TFオペレータパスワード　値が設定されている　文字列型ではない　17桁である
def test_tf_operator_create_case37_3_3(create_header):
    header = create_header["header"]
    DATA["tfOperatorId"] = 12345678901234567
    response = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020019",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020002",
                "message": response.json()["errorInfo"][1]["message"]
            }
        ]
    }
    print(response.json())


# No37.パラメータ検証処理_01.パラメータ検証処理　異常系　引数．リクエストボディ．TFオペレータパスワード　値が設定されている　文字列型である　3桁である　入力可能文字以外が含まれる（全角）
def test_tf_operator_create_case37_3_4(create_header):
    header = create_header["header"]
    DATA["tfOperatorId"] = "ＸＹＺ"
    response = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020020",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No37.パラメータ検証処理_01.パラメータ検証処理　異常系　引数．リクエストボディ．TFオペレータ名　値が設定されていない（空値）
def test_tf_operator_create_case37_4_1(create_header):
    header = create_header["header"]
    DATA["tfOperatorName"] = ""
    response = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020001",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020016",
                "message": response.json()["errorInfo"][1]["message"]
            }
        ]
    }
    print(response.json())


# No37.パラメータ検証処理_01.パラメータ検証処理　異常系　引数．リクエストボディ．TFオペレータ名　値が設定されている　文字列型ではない　1桁である
def test_tf_operator_create_case37_4_2(create_header):
    header = create_header["header"]
    DATA["tfOperatorName"] = 1
    response = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020019",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020016",
                "message": response.json()["errorInfo"][1]["message"]
            }
        ]
    }
    print(response.json())


# No37.パラメータ検証処理_01.パラメータ検証処理　異常系　引数．リクエストボディ．TFオペレータ名　値が設定されている　文字列型ではない　13桁である　英大文字、英小文字、数字、記号のうち３種類未満
def test_tf_operator_create_case37_4_3(create_header):
    header = create_header["header"]
    DATA["tfOperatorName"] = 1234567890123
    response = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020019",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020002",
                "message": response.json()["errorInfo"][1]["message"]
            }
        ]
    }
    print(response.json())


# No37.パラメータ検証処理_01.パラメータ検証処理　正常系　引数．リクエストボディ．TFオペレータ名　値が設定されている　文字列型である　2桁である　入力可能文字のみ
def test_tf_operator_create_case37_4_4(create_header):
    header = create_header["header"]
    DATA["tfOperatorName"] = "ab"
    response = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No37.パラメータ検証処理_01.パラメータ検証処理　正常系　引数．リクエストボディ．TFオペレータ名　値が設定されている　文字列型である　12桁である　入力可能文字のみ
def test_tf_operator_create_case37_4_5(create_header):
    header = create_header["header"]
    DATA["tfOperatorName"] = "abcdefghijkl"
    response = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No37.パラメータ検証処理_01.パラメータ検証処理　異常系　引数．リクエストボディ．TFオペレータメールアドレス　値が設定されていない（空値）
def test_tf_operator_create_case37_5_1(create_header):
    header = create_header["header"]
    DATA["tfOperatorMail"] = ""
    response = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020001",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020016",
                "message": response.json()["errorInfo"][1]["message"]
            },
            {
                "errorCode": "020003",
                "message": response.json()["errorInfo"][2]["message"]
            }
        ]
    }
    print(response.json())


# No37.パラメータ検証処理_01.パラメータ検証処理　異常系　引数．リクエストボディ．TFオペレータメールアドレス　値が設定されている　文字列型ではない　4桁である
def test_tf_operator_create_case37_5_2(create_header):
    header = create_header["header"]
    DATA["tfOperatorMail"] = 1234
    response = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020019",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020016",
                "message": response.json()["errorInfo"][1]["message"]
            }
        ]
    }
    print(response.json())


# No37.パラメータ検証処理_01.パラメータ検証処理　異常系　引数．リクエストボディ．TFオペレータメールアドレス　値が設定されている　文字列型ではない　257桁である
def test_tf_operator_create_case37_5_3(create_header):
    header = create_header["header"]
    DATA["tfOperatorMail"] = int("1" * 257)
    response = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020019",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020002",
                "message": response.json()["errorInfo"][1]["message"]
            }
        ]
    }
    print(response.json())


# No37.パラメータ検証処理_01.パラメータ検証処理　正常系　引数．リクエストボディ．TFオペレータメールアドレス　値が設定されている　文字列型である　5桁である　入力可能文字のみ
def test_tf_operator_create_case37_5_4(create_header):
    header = create_header["header"]
    DATA["tfOperatorMail"] = "a@b.c"
    response = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# No37.パラメータ検証処理_01.パラメータ検証処理　正常系　引数．リクエストボディ．TFオペレータメールアドレス　値が設定されている　文字列型である　256桁である　入力可能文字のみ
def test_tf_operator_create_case37_5_5(create_header):
    header = create_header["header"]
    DATA["tfOperatorMail"] = "a" * 250 + "@tf.jp"
    response = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 200
    assert response.json() == {
        "status": "OK",
        "accessToken": response.json()["accessToken"]
    }
    print(response.json())


# 02.終了処理
# No.39 変数．エラー情報がある
def test_tf_operator_create_case39(create_header):
    header = create_header["header"]
    DATA["tfOperatorMail"] = int("1" * 257)
    response = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 400
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "020019",
                "message": response.json()["errorInfo"][0]["message"]
            },
            {
                "errorCode": "020002",
                "message": response.json()["errorInfo"][1]["message"]
            }
        ]
    }
    print(response.json())


# No40.ロールバック処理_01.ロールバック処理　異常系　ロールバック処理が失敗する
def test_tf_operator_create_case40(mocker: MockerFixture, create_header):
    header = create_header["header"]
    # Exception
    mocker.patch.object(SqlConstClass, "TF_OPERATOR_REGISTER_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    # Exception
    mocker.patch.object(PostgresDbUtilClass, "rollback_transaction", side_effect=Exception('testException'))
    response = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "999999",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# No41.ロールバック処理_01.ロールバック処理　正常系　ロールバック処理が成功する
def test_tf_operator_create_case41(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "TF_OPERATOR_REGISTER_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "991028",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())


# 機能内結合テスト用テストコード1
def test_tf_operator_create_ex_case1(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.commonUtil.CommonUtilClass.wbt_mails_add_api_exec").side_effect = Exception('testException')
    response = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": response.json()["errorInfo"]
    }
    print(response.json())


# 機能内結合テスト用テストコード2
def test_tf_operator_create_ex_case2():
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    common_util = CommonUtilClass(trace_logger)
    response = common_util.wbt_mails_add_api_exec(
        repositoryType=wbtConstClass.REPOSITORY_TYPE["RETURN"],
        fileName=FileNameConstClass.PASSWORD_NOTIFICATION,
        downloadDeadline=get_str_datetime_in_X_days(7),
        replyDeadline=None,
        comment=wbtConstClass.MESSAGE["TF_OPERATOR_CREATE"],
        mailAddressTo=None,
        mailAddressCc=None,
        title=wbtConstClass.TITLE["TF_OPERATOR_CREATE"]
    )
    print(response)


# 機能内結合テスト用テストコード3
def test_tf_operator_create_ex_case3(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.commonUtil.CommonUtilClass.wbt_mails_add_api_exec").return_value = {"result": False}
    response = client.post("/api/2.0/tfoperator/regist", headers=header, data=json.dumps(DATA))
    assert response.status_code == 500
    assert response.json() == {
        "status": "NG",
        "errorInfo": [
            {
                "errorCode": "990011",
                "message": response.json()["errorInfo"][0]["message"]
            }
        ]
    }
    print(response.json())
