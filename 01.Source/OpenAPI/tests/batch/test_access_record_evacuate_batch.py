from fastapi.testclient import TestClient
from const.systemConst import SystemConstClass
from util.commonUtil import CommonUtilClass
import util.commonUtil as commonUtil
from app import app
from fastapi import Request
import util.logUtil as logUtil
import pytest
from pytest_mock.plugin import MockerFixture
from const.sqlConst import SqlConstClass
from util.postgresDbUtil import PostgresDbUtilClass

client = TestClient(app)
trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
common_util = CommonUtilClass(trace_logger)
# 共通DB接続準備処理
common_db_info_response = common_util.get_common_db_info_and_connection()


TEST_INSERT_DATA_1 = {
    "execId": "20221006161135053ZpT3CcLT4IKLE",
    "pdsUserId": "C5100011",
    "apiType": "2",
    "pathParamPdsUserDomainName": "toppan-f",
    "execPath": "http://127.0.0.1:8000/api/2.0/toppan-f/transaction?tid=transaction100",
    "execParam": "",
    "execStatus": True,
    "execUserId": None,
    "registerDatetime": commonUtil.get_str_datetime()
}
TEST_INSERT_DATA_2 = {
    "execId": "20221006161135053ZpT3CcLT4IKKK",
    "pdsUserId": "C5100011",
    "apiType": "2",
    "pathParamPdsUserDomainName": "toppan-f",
    "execPath": "http://127.0.0.1:8000/api/2.0/toppan-f/transaction?tid=transaction100",
    "execParam": "",
    "execStatus": True,
    "execUserId": None,
    "registerDatetime": commonUtil.get_str_datetime_in_X_month(-6)
}
TEST_INSERT_DATA_3 = {
    "execId": "20221006161135053ZpT3CcLT4IELT",
    "pdsUserId": "C5100011",
    "apiType": "2",
    "pathParamPdsUserDomainName": "toppan-f",
    "execPath": "http://127.0.0.1:8000/api/2.0/toppan-f/transaction?tid=transaction100",
    "execParam": "",
    "execStatus": True,
    "execUserId": None,
    "registerDatetime": commonUtil.get_str_datetime_in_X_month(-7)
}
# アクセス記録退避バッチ
# アクセス記録取得処理
EXEC_API_HISTORY_SELECT_SQL = """
    SELECT
        t_exec_api_history.exec_id
    FROM
        t_exec_api_history
    WHERE
        t_exec_api_history.exec_id = %s;
"""
# API実行履歴テーブル削除SQL
EXEC_API_HISTORY_DELETE_SQL = """
    DELETE FROM t_exec_api_history
    WHERE
        t_exec_api_history.execId = %s;
"""


# テスト用のAPI実行履歴クラス
class testExecApiHistory:
    def __init__(self):
        pass

    def insert(self, data: list):
        common_db_connection_resource: PostgresDbUtilClass = None
        common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
        common_db_connection = common_db_info_response["common_db_connection"]

        exec_api_history_result = common_db_connection_resource.select_tuple_one(
            common_db_connection,
            EXEC_API_HISTORY_SELECT_SQL,
            data["execId"]
        )
        print(exec_api_history_result)

        if exec_api_history_result["rowcount"] == 0:
            response = common_db_connection_resource.insert(
                common_db_connection,
                SqlConstClass.API_HISTORY_INSERT_SQL,
                data["execId"],
                data["pdsUserId"],
                data["apiType"],
                data["pathParamPdsUserDomainName"],
                data["execPath"],
                data["execParam"],
                data["execStatus"],
                data["execUserId"],
                data["registerDatetime"]
            )
            print(response)
            # トランザクションコミット処理
            common_db_connection_resource.commit_transaction(common_db_connection)

    def selectExecApiHistory(self, execId: str):
        common_db_connection_resource: PostgresDbUtilClass = None
        common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
        common_db_connection = common_db_info_response["common_db_connection"]

        exec_api_history_result = common_db_connection_resource.select_tuple_one(
            common_db_connection,
            EXEC_API_HISTORY_SELECT_SQL,
            execId
        )
        print(exec_api_history_result)

        if exec_api_history_result["rowcount"] == 0:
            return {
                "rowcount": exec_api_history_result["rowcount"]
            }

        exec_api_history_column_list = [
            "exec_id"
        ]
        exec_api_history_data_list = exec_api_history_result["query_results"]
        exec_api_history_dict = {column: data for column, data in zip(exec_api_history_column_list, exec_api_history_data_list)}
        return {
            "rowcount": exec_api_history_result["rowcount"],
            "execApiHistory": exec_api_history_dict
        }

    def delete(self, execId: str):
        common_db_connection_resource: PostgresDbUtilClass = None
        common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
        common_db_connection = common_db_info_response["common_db_connection"]

        responseExecApiHistory = common_db_connection_resource.delete(
            common_db_connection,
            EXEC_API_HISTORY_DELETE_SQL,
            execId
        )
        print(responseExecApiHistory)

        # トランザクションコミット処理
        common_db_connection_resource.commit_transaction(common_db_connection)


@pytest.fixture
def create_header():
    yield {
        "header": {
            "Content-Type": "application/json",
            "timeStamp": "2022/08/23 15:12:01.690"
        }
    }


@pytest.fixture
def db():
    test = testExecApiHistory()
    return test


# No1.メイン処理_01.共通DB接続準備処理　異常系　接続に失敗する　設定値を異常な値に変更する
def test_access_record_evacuate_batch_case1(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.commonUtil.CommonUtilClass.get_secret_info").return_value = {"host": "test", "port": "test", "username": "test", "password": "test"}
    header = create_header["header"]
    client.post("/api/2.0/batch/accessrecordevacuate", headers=header)


# No2.メイン処理_01.共通DB接続準備処理　正常系　接続に成功する
# No6.メイン処理_02.アクセス記録取得処理　正常系　PDSユーザ取得処理で取得結果が1件
# No7.メイン処理_04. CSVファイル作成処理　正常系　PDSユーザ取得処理で取得結果が1件
# No13.メイン処理_05. アクセス記録退避処理　正常系　アクセス記録退避処理に1回で成功すること
# No17.メイン処理_08. API実行履歴削除処理　正常系　API実行履歴削除処理が成功する
# No18.メイン処理_10.トランザクションコミット処理　正常系
# No19.メイン処理_11. TF公開鍵通知ファイル削除処理　正常系
# No20.メイン処理_12.終了処理　正常系
def test_access_record_evacuate_batch_case2(db: testExecApiHistory, create_header):
    # テストデータ作成
    db.insert(TEST_INSERT_DATA_1)
    db.insert(TEST_INSERT_DATA_3)

    header = create_header["header"]
    client.post("/api/2.0/batch/accessrecordevacuate", headers=header)

    # 最後にテストデータを削除する
    db.delete(TEST_INSERT_DATA_1["execId"])


# No3.メイン処理_02.アクセス記録取得処理_03.共通エラーチェック処理　正常系　postgresqlのエラーが発生
def test_access_record_evacuate_batch_case3(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "API_HISTORY_EVACUTATE_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    client.post("/api/2.0/batch/accessrecordevacuate", headers=header)


# No4.メイン処理_02.アクセス記録取得処理　正常系　PDSユーザ取得処理で取得結果が0件
# No5.メイン処理_04. CSVファイル作成処理　正常系　PDSユーザ取得処理で取得結果が0件
def test_access_record_evacuate_batch_case4(db: testExecApiHistory, create_header):
    # テストデータ作成
    db.insert(TEST_INSERT_DATA_1)

    header = create_header["header"]
    client.post("/api/2.0/batch/accessrecordevacuate", headers=header)

    # 最後にテストデータを削除する
    db.delete(TEST_INSERT_DATA_1["execId"])


# No8.メイン処理_02.アクセス記録取得処理　正常系　PDSユーザ取得処理で取得結果が2件
# No9.メイン処理_04. CSVファイル作成処理　正常系　PDSユーザ取得処理で取得結果が2件
def test_access_record_evacuate_batch_case8(db: testExecApiHistory, create_header):
    # テストデータ作成
    db.insert(TEST_INSERT_DATA_1)
    db.insert(TEST_INSERT_DATA_2)
    db.insert(TEST_INSERT_DATA_3)

    header = create_header["header"]
    client.post("/api/2.0/batch/accessrecordevacuate", headers=header)

    # 最後にテストデータを削除する
    db.delete(TEST_INSERT_DATA_1["execId"])
    db.delete(TEST_INSERT_DATA_2["execId"])
    db.delete(TEST_INSERT_DATA_3["execId"])


# No10.メイン処理_04. CSVファイル作成処理　異常系　CSVファイル作成処理に失敗する
def test_access_record_evacuate_batch_case10(db: testExecApiHistory, create_header):
    # テストデータ作成
    db.insert(TEST_INSERT_DATA_1)
    db.insert(TEST_INSERT_DATA_2)
    db.insert(TEST_INSERT_DATA_3)

    header = create_header["header"]
    client.post("/api/2.0/batch/accessrecordevacuate", headers=header)

    # 最後にテストデータを削除する
    db.delete(TEST_INSERT_DATA_1["execId"])
    db.delete(TEST_INSERT_DATA_2["execId"])
    db.delete(TEST_INSERT_DATA_3["execId"])


# No11.メイン処理_05. アクセス記録退避処理_06.共通エラーチェック処理　異常系　アクセス記録退避処理に失敗すること
# No12.メイン処理_05. アクセス記録退避処理_06.共通エラーチェック処理　異常系　アクセス記録退避処理に6回失敗すること
def test_access_record_evacuate_batch_case11(db: testExecApiHistory, create_header):
    # テストデータ作成
    db.insert(TEST_INSERT_DATA_1)
    db.insert(TEST_INSERT_DATA_2)
    db.insert(TEST_INSERT_DATA_3)

    header = create_header["header"]
    client.post("/api/2.0/batch/accessrecordevacuate", headers=header)

    # 最後にテストデータを削除する
    db.delete(TEST_INSERT_DATA_1["execId"])
    db.delete(TEST_INSERT_DATA_2["execId"])
    db.delete(TEST_INSERT_DATA_3["execId"])


# No14.メイン処理_05. アクセス記録退避処理_06.共通エラーチェック処理　異常系　アクセス記録退避処理に4回失敗し、5回目で成功すること
def test_access_record_evacuate_batch_case14(mocker: MockerFixture, db: testExecApiHistory, create_header):
    # テストデータ作成
    db.insert(TEST_INSERT_DATA_1)
    db.insert(TEST_INSERT_DATA_2)
    db.insert(TEST_INSERT_DATA_3)
    mocker.patch("util.s3AioUtil.s3AioUtilClass.async_put_file").side_effect = [False, False, False, False, True]

    header = create_header["header"]
    client.post("/api/2.0/batch/accessrecordevacuate", headers=header)

    # 最後にテストデータを削除する
    db.delete(TEST_INSERT_DATA_1["execId"])
    db.delete(TEST_INSERT_DATA_2["execId"])


# No16.メイン処理_08. API実行履歴削除処理_09.共通エラーチェック処理　異常系　API実行履歴削除処理が失敗する
# No22.ロールバック処理_01.ロールバック処理　ロールバック処理が成功すること
# No23.S3ファイル削除処理_01.S3ファイルの削除処理　正常系　S3のファイル削除処理に成功すること
def test_access_record_evacuate_batch_case16(mocker: MockerFixture, db: testExecApiHistory, create_header):
    # テストデータ作成
    db.insert(TEST_INSERT_DATA_1)
    db.insert(TEST_INSERT_DATA_3)

    # Exception
    mocker.patch.object(SqlConstClass, "API_HISTORY_EVACUTATE_DELETE_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    client.post("/api/2.0/batch/accessrecordevacuate", headers=header)

    # 最後にテストデータを削除する
    db.delete(TEST_INSERT_DATA_1["execId"])
    db.delete(TEST_INSERT_DATA_3["execId"])


# No21.ロールバック処理_01.ロールバック処理_02.共通エラーチェック処理　ロールバック処理が失敗すること
def test_access_record_evacuate_batch_case21(mocker: MockerFixture, db: testExecApiHistory, create_header):
    # テストデータ作成
    db.insert(TEST_INSERT_DATA_1)

    # Exception
    mocker.patch.object(SqlConstClass, "API_HISTORY_EVACUTATE_DELETE_SQL", """ SELECT * FROM AAAAAA; """)
    # Exception
    mocker.patch.object(PostgresDbUtilClass, "rollback_transaction", side_effect=Exception('testException'))
    header = create_header["header"]
    client.post("/api/2.0/batch/accessrecordevacuate", headers=header)

    # 最後にテストデータを削除する
    db.delete(TEST_INSERT_DATA_1["execId"])
