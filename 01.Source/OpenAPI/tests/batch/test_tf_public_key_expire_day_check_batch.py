from fastapi.testclient import TestClient
from const.sqlConst import SqlConstClass
from app import app
from fastapi import Request
import pytest
import datetime
from pytest_mock.plugin import MockerFixture
from util.tokenUtil import TokenUtilClass
import util.logUtil as logUtil
from const.systemConst import SystemConstClass
from util.postgresDbUtil import PostgresDbUtilClass
from util.fileUtil import NoHeaderOneItemCsvStringClass

client = TestClient(app)

BEARER = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0Zk9wZXJhdG9ySWQiOiJsLXRlc3QiLCJ0Zk9wZXJhdG9yTmFtZSI6Ilx1MzBlZFx1MzBiMFx1MzBhNFx1MzBmM1x1MzBjNlx1MzBiOVx1MzBjOCIsInRmT3BlcmF0b3JQYXNzd29yZFJlc2V0RmxnIjpmYWxzZSwiYWNjZXNzVG9rZW4iOiJiZGE4ZGY3OThiYzViZGZhMWZkODIyNmRiYmQ0OTMyMTY5ZmY5MjAzNWM0YzFlY2FjZjY2OGUyYzk2ZjAwZThlZTUxNTBiNGM0NTc0NjlkN2I4YmY1NzIxZDZlM2NiNzFiY2RiYzA3ODRiYzcyZWVlNjk1OGE3NTBiMWJkMWEzZWFmZWQ0OWFhNWU0ODZjYzQyZmM3OWNhMWY3MGQzZmM3Yzc0YzE5NjM3ODUzMjRhZDRhNGM0NjkxOGE4NjQ1N2ZiODE3NDU1MCIsImV4cCI6MTY2MTc0NjY3MX0.LCRjPEqKMkRQ_phaYnO7S7pd3SU_rgon-wsX14DBsPA"
ACCESS_TOKEN = "bda8df798bc5bdfa1fd8226dbbd4932169ff92035c4c1ecacf668e2c96f00e8ee5150b4c457469d7b8bf5721d6e3cb71bcdbc0784bc72eee6958a750b1bd1a3eafed49aa5e486cc42fc79ca1f70d3fc7c74c1963785324ad4a4c46918a86457fb8174550"
HEADER = {"Content-Type": "application/json", "timeStamp": "2022/08/23 15:12:01.690", "accessToken": ACCESS_TOKEN, "Authorization": "Bearer " + BEARER}
DATA = {
    "pdsUserId": "C0000001",
    "fromDate": "2022/01/01",
    "toDate": "2022/12/31"
}
TF_OPERATOR_INFO = {
    "tfOperatorId": "l-test",
    "tfOperatorName": "ログインテスト"
}


@pytest.fixture
def create_header():
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_closed(tfOperatorInfo=TF_OPERATOR_INFO, accessToken=None)
    yield {
        "header": {
            "pdsUserId": DATA["pdsUserId"],
            "Content-Type": "application/json",
            "accessToken": token_result["accessToken"],
            "timeStamp": "2022/08/23 15:12:01.690",
            "Authorization": "Bearer " + token_result["jwt"]
        }
    }


# 01.共通DB接続準備処理
# No1.接続に失敗する
# 設定値を異常な値に変更する
def test_tf_public_key_expire_day_check_batch1(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.commonUtil.CommonUtilClass.get_secret_info").return_value = {"host": "test", "port": "test", "username": "test", "password": "test"}
    header = create_header["header"]
    client.post("/api/2.0/batch/tfPublicKeyExpireDayCheck", headers=header)


# No2.接続に成功する
def test_tf_public_key_expire_day_check_batch2(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.postgresDbUtil.PostgresDbUtilClass.select_tuple_list").return_value = {
        "result": True,
        "query_results": [(2, 'C0000011', 'テスト用1株式会社', 'test1@email.xxx.yyy', 'test2@email.xxx.yyy', 'uMYF4CgiBbeAqSDCZYIh...plCEAYJD0=', datetime.date(2022, 8, 10))]
    }
    client.post("/api/2.0/batch/tfPublicKeyExpireDayCheck", headers=header)


# 02.PDSユーザPDSユーザ公開鍵情報取得処理
# 03.共通エラーチェック処理
# No3.PDSユーザPDSユーザ公開鍵情報取得処理が失敗する
def test_tf_public_key_expire_day_check_batch3(mocker: MockerFixture, create_header):
    # Exception
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "PDS_USER_PDS_USER_PUBLIC_KEY_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    client.post("/api/2.0/batch/tfPublicKeyExpireDayCheck", headers=header)


# 02.PDSユーザPDSユーザ公開鍵情報取得処理
# No04.PDSユーザPDSユーザ公開鍵情報取得処理で取得結果が0件
def test_tf_public_key_expire_day_check_batch4(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.postgresDbUtil.PostgresDbUtilClass.select_tuple_list").return_value = {"result": True, "rowcount": 0, "query_results": ()}
    client.post("/api/2.0/batch/tfPublicKeyExpireDayCheck", headers=header)


# No05.PDSユーザPDSユーザ公開鍵情報取得処理で取得結果が2件
# No08.PDSユーザ情報取得処理で取得結果が2件 - PDSユーザ公開鍵テーブル登録処理が成功する
# No12.PDSユーザ情報取得処理で取得結果が2件 - キーペア作成処理が成功する
# No15.TF公開鍵通知ファイル作成処理が成功する
# No17.WBTメール件名作成処理が成功する
# No18.「PDSユーザ公開鍵トランザクション」を作成する
# No20.PDSユーザ公開鍵テーブル登録処理が成功する
# No22.WBT新規メール情報登録API実行処理が成功する
# No24.WBTファイル登録API実行処理が成功する
# No25.「PDSユーザ公開鍵トランザクション」のコミット処理が成功する
# No26.「WBT送信メールIDトランザクション」を作成する
# No28.WBT送信メールID更新処理が成功する
# No29.「WBT送信メールIDトランザクション」のコミット処理が成功する
# No30.TF公開鍵通知ファイル削除処理が成功する
# No31.正常
def test_tf_public_key_expire_day_check_batch5(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.postgresDbUtil.PostgresDbUtilClass.select_tuple_list").return_value = {
        "result": True,
        "query_results": [
            (2, 'C0000011', 'テスト用1株式会社', 'test1@email.xxx.yyy', 'test2@email.xxx.yyy', 'uMYF4CgiBbeAqSDCZYIh...plCEAYJD0=', datetime.date(2022, 8, 10)),
            (3, 'C0000100', 'PDSユーザ認証情報発行テスト', 'test1@email.xxx.yyy', 'test2@email.xxx.yyy', 'uMYF4CgiBbeAqSDCZYIhKINqYZGGSf/HgzO9WiJvPhY9JjqDrS4I5ROzGY3qOI8JjcQmVA+eDHZ1qwP0vRkrMjwXXRXZ6dXNyPVjIapSKEYa3S2tQGeR0Q6nXExygALX6wMn2bsk6oa8Nr89BJCyIloz6GSyRFYVCAPaXAGohYYVWZejKMQu4+KEBD+jnfizKFXx3ERBwHlxb0NucI56bnUHAggJ54hgDmA0vXjAGpA8CqEmzdAAXR9sw553DwcrNuf+s8yDseDm5Oln+J2Gp6P+4PYyC1D9urSo+P7KfstECuOTlgqaD79Boca3REf4j/9BcsAKQk3cWFBf/iYF9Vf5rc/6i103ce2N/D1uh/v9D/rarzFL6bdUrLFdEf+cn+yZmK/D55pezIbADsvMSepIv8FpXQ/z2caJrmR1zCKDXYKgfjY4LxLcaUx9q6+P1Cxt9YQC2TmKXFoHGGMBYwZ5Eg84lrVA8G8j+TvzwwDhRLLf3tSFxA351gjvOTZ+qDhbAMhCGl5kMUliNEVneqTFSiB2SbkY8kieC37KRumxkhvv5DgR/QA50ASLFuu3NjLGHRYgys1LnCsc5pJwgPKPpmKyLB6JwFMfIQ22s9z+ekmU1yqukOJUNzbNHZRrib7MveRmmZpjXB9Kd+JpVou7KdEMg226QOplCEAYJD0=', datetime.date(2022, 8, 10)),
        ]
    }
    client.post("/api/2.0/batch/tfPublicKeyExpireDayCheck", headers=header)


# 「変数．PDSユーザ情報取得結果リスト」の要素数分繰り返す
# No06.PDSユーザPDSユーザ公開鍵情報取得処理で取得結果が0件
def test_tf_public_key_expire_day_check_batch6(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.postgresDbUtil.PostgresDbUtilClass.select_tuple_list").return_value = {"result": True, "rowcount": 0, "query_results": ()}
    client.post("/api/2.0/batch/tfPublicKeyExpireDayCheck", headers=header)


# 「変数．PDSユーザPDSユーザ公開鍵取得結果リスト」の要素数分繰り返す
# 09.PDSユーザ公開鍵テーブル登録処理
# 10.共通エラーチェック処理
# No7.PDSユーザ情報取得処理で取得結果が2件
#      PDSユーザ公開鍵テーブル登録処理が失敗する
def test_tf_public_key_expire_day_check_batch7(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.postgresDbUtil.PostgresDbUtilClass.select_tuple_list").return_value = {
        "result": True,
        "query_results": [
            (2, 'C0000011', 'テスト用1株式会社', 'test1@email.xxx.yyy', 'test2@email.xxx.yyy', 'uMYF4CgiBbeAqSDCZYIh...plCEAYJD0=', datetime.date(2022, 8, 10)),
            (3, 'C0000100', 'PDSユーザ認証情報発行テスト', 'test1@email.xxx.yyy', 'test2@email.xxx.yyy', 'uMYF4CgiBbeAqSDCZYIhKINqYZGGSf/HgzO9WiJvPhY9JjqDrS4I5ROzGY3qOI8JjcQmVA+eDHZ1qwP0vRkrMjwXXRXZ6dXNyPVjIapSKEYa3S2tQGeR0Q6nXExygALX6wMn2bsk6oa8Nr89BJCyIloz6GSyRFYVCAPaXAGohYYVWZejKMQu4+KEBD+jnfizKFXx3ERBwHlxb0NucI56bnUHAggJ54hgDmA0vXjAGpA8CqEmzdAAXR9sw553DwcrNuf+s8yDseDm5Oln+J2Gp6P+4PYyC1D9urSo+P7KfstECuOTlgqaD79Boca3REf4j/9BcsAKQk3cWFBf/iYF9Vf5rc/6i103ce2N/D1uh/v9D/rarzFL6bdUrLFdEf+cn+yZmK/D55pezIbADsvMSepIv8FpXQ/z2caJrmR1zCKDXYKgfjY4LxLcaUx9q6+P1Cxt9YQC2TmKXFoHGGMBYwZ5Eg84lrVA8G8j+TvzwwDhRLLf3tSFxA351gjvOTZ+qDhbAMhCGl5kMUliNEVneqTFSiB2SbkY8kieC37KRumxkhvv5DgR/QA50ASLFuu3NjLGHRYgys1LnCsc5pJwgPKPpmKyLB6JwFMfIQ22s9z+ekmU1yqukOJUNzbNHZRrib7MveRmmZpjXB9Kd+JpVou7KdEMg226QOplCEAYJD0=', datetime.date(2022, 8, 10)),
        ]
    }
    mocker.patch.object(SqlConstClass, "PDS_USER_KEY_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    client.post("/api/2.0/batch/tfPublicKeyExpireDayCheck", headers=header)


# 失敗した場合5回まで繰り返す
# 04. キーペア作成処理
# No09.PDSユーザ情報取得処理で取得結果が2件
#       キーペア作成処理が失敗する（KMS登録処理に失敗）


# No10.PDSユーザ情報取得処理で取得結果が2件
#       キーペア作成処理が失敗する（KMSレプリケート処理に失敗）


# No11.PDSユーザ情報取得処理で取得結果が2件
#       キーペア作成処理が失敗する（KMS公開鍵取得処理に失敗）


# 05.共通エラーチェック処理
# No13.キーペア作成処理が失敗する


# 06.TF公開鍵通知ファイル作成処理
# No14.TF公開鍵通知ファイル作成処理が失敗する
def test_tf_public_key_expire_day_check_batch14(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(NoHeaderOneItemCsvStringClass, "__init__", side_effect=Exception('testException'))
    client.post("/api/2.0/batch/tfPublicKeyExpireDayCheck", headers=header)


# 07. WBTメール件名作成処理
# No16.WBTメール件名作成処理が失敗する


# 09.PDSユーザ公開鍵テーブル登録処理
# 10.共通エラーチェック処理
# No19.PDSユーザ公開鍵テーブル登録処理が失敗する
def test_tf_public_key_expire_day_check_batch19(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "PDS_USER_KEY_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    client.post("/api/2.0/batch/tfPublicKeyExpireDayCheck", headers=header)


# 11.WBT新規メール情報登録API実行処理
# 12.共通エラーチェック処理
# No21.WBT新規メール情報登録API実行処理が失敗する
def test_tf_public_key_expire_day_check_batch21(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.commonUtil.CommonUtilClass.wbt_mails_add_api_exec").return_value = {"result": False}
    client.post("/api/2.0/batch/tfPublicKeyExpireDayCheck", headers=header)


# 13.WBTファイル登録API実行処理
# 14.共通エラーチェック処理
# No23.WBTファイル登録API実行処理が失敗する
def test_tf_public_key_expire_day_check_batch23(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.commonUtil.CommonUtilClass.wbt_file_add_api_exec").return_value = {"result": False}
    client.post("/api/2.0/batch/tfPublicKeyExpireDayCheck", headers=header)


# 17.WBT送信メールID更新処理
# 18.共通エラーチェック処理
# No27.WBT送信メールID更新処理が失敗する
def test_tf_public_key_expire_day_check_batch27(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "PDS_USER_KEY_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    client.post("/api/2.0/batch/tfPublicKeyExpireDayCheck", headers=header)


# 02.ロールバック処理
#   「PDSユーザ公開鍵トランザクション」
# 01.ロールバック処理
# 02.共通エラーチェック処理
# No32.ロールバック処理が失敗すること
def test_tf_public_key_expire_day_check_batch32(mocker: MockerFixture, create_header):
    header = create_header["header"]
    # Exception
    mocker.patch.object(SqlConstClass, "PDS_USER_KEY_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    # Exception
    mocker.patch.object(PostgresDbUtilClass, "rollback_transaction", side_effect=Exception('testException'))
    client.post("/api/2.0/batch/tfPublicKeyExpireDayCheck", headers=header)


# No33.ロールバック処理が成功すること
def test_tf_public_key_expire_day_check_batch33(mocker: MockerFixture, create_header):
    header = create_header["header"]
    # Exception
    mocker.patch.object(SqlConstClass, "PDS_USER_KEY_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    client.post("/api/2.0/batch/tfPublicKeyExpireDayCheck", headers=header)


# 03.ロールバック処理
#   「WBT送信メールIDトランザクション」
# 01.ロールバック処理
# 02.共通エラーチェック処理
# No34.ロールバック処理が失敗すること
def test_tf_public_key_expire_day_check_batch34(mocker: MockerFixture, create_header):
    header = create_header["header"]
    # Exception
    mocker.patch.object(SqlConstClass, "PDS_USER_KEY_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    # Exception
    mocker.patch.object(PostgresDbUtilClass, "rollback_transaction", side_effect=Exception('testException'))
    client.post("/api/2.0/batch/tfPublicKeyExpireDayCheck", headers=header)


# No35.ロールバック処理が成功すること
def test_tf_public_key_expire_day_check_batch35(mocker: MockerFixture, create_header):
    header = create_header["header"]
    # Exception
    mocker.patch.object(SqlConstClass, "PDS_USER_KEY_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    client.post("/api/2.0/batch/tfPublicKeyExpireDayCheck", headers=header)


# 機能内結合テスト用コード
def test_tf_public_key_expire_day_check_batch(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.postgresDbUtil.PostgresDbUtilClass.select_tuple_list").return_value = {
        "result": True,
        "query_results": [(2, 'C0000011', 'テスト用1株式会社', 'test1@email.xxx.yyy', 'test2@email.xxx.yyy', 'uMYF4CgiBbeAqSDCZYIh...plCEAYJD0=', datetime.date(2022, 8, 10))]
    }
    client.post("/api/2.0/batch/tfPublicKeyExpireDayCheck", headers=header)
