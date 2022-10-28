from fastapi.testclient import TestClient
from app import app
import pytest
from pytest_mock.plugin import MockerFixture
from const.sqlConst import SqlConstClass
from util.postgresDbUtil import PostgresDbUtilClass

client = TestClient(app)


@pytest.fixture
def create_header():
    yield {
        "header": {
            "Content-Type": "application/json",
            "timeStamp": "2022/08/23 15:12:01.690"
        }
    }


# 01.共通DB接続準備処理
# No1.接続に失敗する
# 設定値を異常な値に変更する
def test_access_token_delete_batch_case1(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.commonUtil.CommonUtilClass.get_secret_info").return_value = {"host": "test", "port": "test", "username": "test", "password": "test"}
    header = create_header["header"]
    client.post("/api/2.0/batch/accessTokenDelete", headers=header)


# No2.接続に成功する
def test_access_token_delete_batch_case2(create_header):
    header = create_header["header"]
    client.post("/api/2.0/batch/accessTokenDelete", headers=header)


# 02.トランザクション作成処理
# No3.トランザクション作成処理実行
def test_access_token_delete_batch_case3(create_header):
    header = create_header["header"]
    client.post("/api/2.0/batch/accessTokenDelete", headers=header)


# 03．アクセストークン削除処理
# 04. 共通エラーチェック処理
# No4.アクセストークン削除処理が失敗する
def test_access_token_delete_batch_case4(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "ACCESS_TOKEN_BATCH_DELETE_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    client.post("/api/2.0/batch/accessTokenDelete", headers=header)


# No.5.アクセストークン削除処理が成功する
# アクセストークン．有効期限日時 < バッチ実行日時（YYYY/MM/DD hh:mm:ss:iii）
# 上記の条件の境界値のデータを用意して削除されるもの、削除されないものを確認
def test_access_token_delete_batch_case5(create_header):
    header = create_header["header"]
    client.post("/api/2.0/batch/accessTokenDelete", headers=header)


# 05.トランザクションコミット処理
# 06.終了処理
def test_access_token_delete_batch_case6(create_header):
    header = create_header["header"]
    client.post("/api/2.0/batch/accessTokenDelete", headers=header)


# ロールバック処理
# 01.ロールバック処理
# 02.共通エラーチェック処理
# ロールバック処理が失敗すること
def test_access_token_delete_batch_case7(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "ACCESS_TOKEN_BATCH_DELETE_SQL", """ SELECT * FROM AAAAAA; """)
    # Exception
    mocker.patch.object(PostgresDbUtilClass, "rollback_transaction", side_effect=Exception('testException'))
    header = create_header["header"]
    client.post("/api/2.0/batch/accessTokenDelete", headers=header)


# ロールバック処理が成功すること
def test_access_token_delete_batch_case8(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "ACCESS_TOKEN_BATCH_DELETE_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    client.post("/api/2.0/batch/accessTokenDelete", headers=header)
