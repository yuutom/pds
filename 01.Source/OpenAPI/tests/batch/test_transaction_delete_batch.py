from fastapi.testclient import TestClient
from app import app
import pytest
from pytest_mock.plugin import MockerFixture
from util.tokenUtil import TokenUtilClass
from const.sqlConst import SqlConstClass
from util.commonUtil import CommonUtilClass
from const.systemConst import SystemConstClass
from util.postgresDbUtil import PostgresDbUtilClass
from const.messageConst import MessageConstClass
from fastapi import Request
import util.logUtil as logUtil
import json


client = TestClient(app)
EXEC_NAME: str = "transactionDeleteBatch"
EXEC_NAME_JP: str = "個人情報削除バッチ"

PDS_USER = {
    "pdsUserId": "C0000015",
    "pdsUserName": "個人情報削除テスト"
}

DATA = {
    "pdsUserId": PDS_USER["pdsUserId"],
    "transactionId": "transaction130012"
}
DATA2 = {
    "tid": "transaction130012",
    "info": {
        "userId": PDS_USER["pdsUserId"],
        "saveDate": "2022/09/26 10:00:00.000",
        "data": "{\"aaa\": \"bbb\"}",
        "image": ["abcde"],
        "imageHash": "abc",
        "secureLevel": "2"
    }
}


@pytest.fixture
def create_header():
    yield {"header": {"Content-Type": "application/json"}}


@pytest.fixture
def create_pds_user_db_info():
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    common_util = CommonUtilClass(trace_logger)
    pds_user_db_info = common_util.get_secret_info("pds-c0000000-sm")
    yield pds_user_db_info


def test_delete_case():
    data_copy = DATA.copy()
    data_copy2 = DATA2.copy()
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    for i in range(70):
        header = {
            "pdsUserId": PDS_USER["pdsUserId"],
            "Content-Type": "application/json",
            "timeStamp": "2022/08/23 15:12:01.690",
            "accessToken": token_result["accessToken"],
            "Authorization": "Bearer " + token_result["jwt"]
        }
        data_copy["transactionId"] = DATA["transactionId"] + f'{i:02}'
        data_copy2["tid"] = DATA["transactionId"] + f'{i:02}'
        data_copy2["info"]["userId"] = "個人情報削除バッチテスト" + f'{i:02}'
        response = client.post("/api/2.0/delete-profile/transaction", headers=header, data=json.dumps(data_copy2))
        trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
        token_util = TokenUtilClass(trace_logger)
        token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
        tid = data_copy["transactionId"]
        header["accessToken"] = token_result["accessToken"]
        header["Authorization"] = "Bearer " + token_result["jwt"]
        response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
        print(response.json())


def test_delete_case2():
    data_copy = DATA.copy()
    data_copy2 = DATA2.copy()
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    for i in range(3):
        header = {
            "pdsUserId": PDS_USER["pdsUserId"],
            "Content-Type": "application/json",
            "timeStamp": "2022/08/23 15:12:01.690",
            "accessToken": token_result["accessToken"],
            "Authorization": "Bearer " + token_result["jwt"]
        }
        data_copy["transactionId"] = DATA["transactionId"] + "5" + f'{i:02}'
        data_copy2["tid"] = DATA["transactionId"] + "5" + f'{i:02}'
        data_copy2["info"]["userId"] = "個人情報削除バッチテスト" + "5" + f'{i:02}'
        response = client.post("/api/2.0/delete-profile/transaction", headers=header, data=json.dumps(data_copy2))
        trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
        token_util = TokenUtilClass(trace_logger)
        token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
        tid = data_copy["transactionId"]
        header["accessToken"] = token_result["accessToken"]
        header["Authorization"] = "Bearer " + token_result["jwt"]
        response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
        print(response.json())


def test_delete_case3():
    data_copy = DATA.copy()
    data_copy2 = DATA2.copy()
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    i = 51
    header = {
        "pdsUserId": PDS_USER["pdsUserId"],
        "Content-Type": "application/json",
        "timeStamp": "2022/08/23 15:12:01.690",
        "accessToken": token_result["accessToken"],
        "Authorization": "Bearer " + token_result["jwt"]
    }
    data_copy["transactionId"] = DATA["transactionId"] + "0" + f'{i:02}'
    data_copy2["tid"] = DATA["transactionId"] + "0" + f'{i:02}'
    data_copy2["info"]["userId"] = "個人情報削除バッチテスト" + "0" + f'{i:02}'
    response = client.post("/api/2.0/delete-profile/transaction", headers=header, data=json.dumps(data_copy2))
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    token_util = TokenUtilClass(trace_logger)
    token_result = token_util.create_token_public(pdsUserId=PDS_USER["pdsUserId"], pdsUserName=PDS_USER["pdsUserName"], accessToken=None)
    tid = data_copy["transactionId"]
    header["accessToken"] = token_result["accessToken"]
    header["Authorization"] = "Bearer " + token_result["jwt"]
    response = client.delete("/api/2.0/delete-profile/transaction?tid=" + tid, headers=header)
    print(response.json())


# メイン処理
# 01.パラメータ取得処理
# No.1 ◆異常系AWS SQSからの取得に失敗
def test_transaction_delete_batch_case1(create_header):
    header = create_header["header"]
    DATA = {
        "pdsUserId": "C9876543",
        "transactionId": "transaction13002000"
    }
    data_copy = DATA.copy()
    data_copy["transactionId"] = "transaction13002000"
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# ◆正常系 個人情報削除バッチ_01.引数検証処理チェック　参照
# No.2_1 PDSユーザIDが空値 (None)
def test_transaction_delete_batch_case2_1(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserId"] = None
    data_copy["transactionId"] = DATA["transactionId"] + "021"
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# No.2_2 PDSユーザIDが文字列型ではない
def test_transaction_delete_batch_case2_2(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserId"] = 1234567
    data_copy["transactionId"] = DATA["transactionId"] + "022"
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# No.2_3 PDSユーザIDが正常値
def test_transaction_delete_batch_case2_3(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "023"
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# 02.共通エラーチェック処理
# No.3 ◆正常系 共通エラーチェック処理が成功（エラー情報有り）
def test_transaction_delete_batch_case3(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["pdsUserId"] = None
    data_copy["transactionId"] = DATA["transactionId"] + "03"
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# 03.共通DB接続準備処理
# No.4 ◆異常系 接続に失敗する 設定値を異常な値に変更する
def test_transaction_delete_batch_case4(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "04"
    # Exception
    mocker.patch("util.commonUtil.CommonUtilClass.get_secret_info").return_value = {"host": "test", "port": "test", "username": "test", "password": "test"}
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# No.5 ◆正常系 接続に成功する
def test_transaction_delete_batch_case5(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "05"
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# 04.PDSユーザデータ取得処理
# No.6 ◆異常系 PDSユーザデータ取得処理に失敗する
def test_transaction_delete_batch_case6(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "06"
    # Exception
    mocker.patch.object(SqlConstClass, "TRANSACTION_DELETE_PDS_USER_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# No.7 ◆正常系 PDSユーザデータ取得処理に成功する 取得件数が1件
def test_transaction_delete_batch_case7(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "07"
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# 05.共通エラーチェック処理
# No.8 ◆正常系 共通エラーチェック処理が成功（エラー情報有り）
def test_transaction_delete_batch_case8(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "08"
    # Exception
    mocker.patch.object(SqlConstClass, "TRANSACTION_DELETE_PDS_USER_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# 06.PDSユーザDB接続準備処理
# No.9 ◆異常系 接続に失敗する 設定値を異常な値に変更する
def test_transaction_delete_batch_case9(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "09"
    # Exception
    mocker.patch.object(SystemConstClass, "PDS_USER_DB_NAME", "pds_user_db2")
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# No.10 ◆正常系 接続に成功する
def test_transaction_delete_batch_case10(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "10"
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# 07.個人情報削除対象データ一括取得処理
# No.11 ◆異常系 個人情報削除対象データ一括取得処理が失敗する
def test_transaction_delete_batch_case11(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "11"
    # Exception
    mocker.patch.object(SqlConstClass, "TRANSACTION_DELETE_DATA_TO_DELETE_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# Mo.12 ◆正常系 個人情報削除対象データ一括取得処理が成功する 取得件数が2件
def test_transaction_delete_batch_case12(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "12"
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# 08.共通エラーチェック処理
# No.13 ◆正常系 共通エラーチェック処理が成功（エラー情報有り）
def test_transaction_delete_batch_case13(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "13"
    # Exception
    mocker.patch.object(SqlConstClass, "TRANSACTION_DELETE_DATA_TO_DELETE_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# 09.削除対象リスト作成処理
# No.14 ◆異常系 削除対象リスト作成処理が失敗する
def test_transaction_delete_batch_case14(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "14"
    # Exception
    mocker.patch("models.batch.transactionDeleteBatchModel.transactionDeleteBatchModelClass.data_to_delete_list_create").side_effect = Exception('testException')
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(DATA))


# No.15 ◆正常系 削除対象リスト作成処理が成功する
def test_transaction_delete_batch_case15(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "15"
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# 10.分割バイナリファイル削除処理リスト初期化処理
# No.16 ◆正常系 分割バイナリファイル削除処理リスト初期化処理が成功する
def test_transaction_delete_batch_case16(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "16"
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# 「変数．削除対象リスト作成処理結果．個人情報バイナリファイル削除対象リスト」の要素分だけ繰り返す
# No.17 ◆正常系 繰り返す要素数が0件
def test_transaction_delete_batch_case17(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "17"
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# 「変数．削除対象リスト作成処理結果．個人情報バイナリファイル削除対象リスト」の要素分だけ繰り返す
# No.18 ◆正常系 繰り返す要素数が2件
def test_transaction_delete_batch_case18(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "18"
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# 11.S3ファイル削除処理リスト作成処理
# No.19 ◆正常系 S3ファイル削除処理リスト作成処理が成功する
def test_transaction_delete_batch_case19(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "19"
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# 12.分割バイナリファイル削除処理実行処理
# No.20 ◆異常系 分割バイナリファイル削除処理実行処理が失敗する
def test_transaction_delete_batch_case20(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "20"
    # Exception
    mocker.patch("models.batch.transactionDeleteBatchModel.transactionDeleteBatchModelClass.split_binary_file_delete").return_value = {
        "result": False,
        "errorInfo": {
            "errorCode": "990022",
            "message": logUtil.message_build(MessageConstClass.ERRORS["990022"]["message"], "990022")
        }
    }
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# No.21 ◆正常系 分割バイナリファイル削除処理実行処理が成功する
def test_transaction_delete_batch_case21(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "21"
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# 13.共通エラーチェック処理
# No.22 ◆正常系 共通エラーチェック処理が成功（エラー情報有り）
def test_transaction_delete_batch_case22(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "22"
    # Exception
    mocker.patch("models.batch.transactionDeleteBatchModel.transactionDeleteBatchModelClass.split_binary_file_delete").return_value = {
        "result": False,
        "errorInfo": {
            "errorCode": "990022",
            "message": logUtil.message_build(MessageConstClass.ERRORS["990022"]["message"], "990022")
        }
    }
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))

# 14.トランザクション作成処理
# No.23 トランザクション作成処理実行 「個人情報削除トランザクション」を作成する


# 15.個人情報バイナリ分割データ削除処理
# No.24 ◆異常系 個人情報バイナリ分割データ削除処理が失敗する
def test_transaction_delete_batch_case24(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "24"
    # Exception
    mocker.patch.object(SqlConstClass, "TRANSACTION_DELETE_BINARY_SPLIT_DELETE_SQL", """ SELECT * FROM AAAAAA; """)
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# No.25 ◆正常系 個人情報バイナリ分割データ削除処理が成功する
def test_transaction_delete_batch_case25(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "25"
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# 16.共通エラーチェック処理
# No.26 ◆正常系 共通エラーチェック処理が成功（エラー情報有り）
def test_transaction_delete_batch_case26(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "26"
    # Exception
    mocker.patch.object(SqlConstClass, "TRANSACTION_DELETE_BINARY_SPLIT_DELETE_SQL", """ SELECT * FROM AAAAAA; """)
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# 17.個人情報バイナリデータ削除処理
# No.27 ◆異常系 個人情報バイナリデータ削除処理が失敗する
def test_transaction_delete_batch_case27(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "27"
    # Exception
    mocker.patch.object(SqlConstClass, "TRANSACTION_DELETE_BINARY_DELETE_SQL", """ SELECT * FROM AAAAAA; """)
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# No.28 ◆正常系 個人情報バイナリデータ削除処理が成功する
def test_transaction_delete_batch_case28(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "28"
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# 18.共通エラーチェック処理
# No.29 ◆正常系 共通エラーチェック処理が成功（エラー情報有り）
def test_transaction_delete_batch_case29(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "29"
    # Exception
    mocker.patch.object(SqlConstClass, "TRANSACTION_DELETE_BINARY_DELETE_SQL", """ SELECT * FROM AAAAAA; """)
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# 19.個人情報削除判定処理
# No.30 ◆正常系 「変数．個人情報削除対象データ[個人情報有効フラグ][0]」がfalse
def test_transaction_delete_batch_case30(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "30"
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# No.31 ◆正常系 「変数．個人情報削除対象データ[個人情報有効フラグ][0]」がtrue
def test_transaction_delete_batch_case31(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "31"
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# 20.個人情報削除処理
# No.32 ◆異常系 個人情報削除処理が失敗する
def test_transaction_delete_batch_case32(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "32"
    # Exception
    mocker.patch.object(SqlConstClass, "TRANSACTION_DELETE_DATA_DELETE_SQL", """ SELECT * FROM AAAAAA; """)
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# No.33 ◆正常系 個人情報削除処理が成功する
def test_transaction_delete_batch_case33(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "33"
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# 21.トランザクションコミット処理
# No.34 ◆正常系 「個人情報削除トランザクション」のコミット処理が成功する
def test_transaction_delete_batch_case34(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "34"
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# 22.終了処理
# No.35 ◆正常系
def test_transaction_delete_batch_case35(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "35"
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# 削除対象リスト作成処理
# 01.個人情報削除フラグ作成処理
# No.36 ◆正常系
def test_transaction_delete_batch_case36(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "36"
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# 02.削除対象データリスト作成処理
# No.37 ◆正常系
def test_transaction_delete_batch_case37(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "37"
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# 03.終了処理
# No.38 ◆正常系
def test_transaction_delete_batch_case38(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "38"
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# 分割バイナリファイル削除処理
# 失敗した場合5回まで繰り返す
# 01.S3のファイル削除処理
# No.39 ◆異常系 S3のファイル削除処理に6回失敗する
def test_transaction_delete_batch_case39(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "39"
    # Exception
    mocker.patch("util.s3Util.s3UtilClass.deleteFile").return_value = False
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# No.40 ◆正常系 S3のファイル削除処理に4回失敗し、5回目で成功する
def test_transaction_delete_batch_case40(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "40"
    # Exception
    mocker.patch.object(SqlConstClass, "TRANSACTION_DELETE_BINARY_SPLIT_DELETE_SQL", """ SELECT * FROM AAAAAA; """)
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# No.41 ◆異常系 S3のファイル削除処理が失敗する
def test_transaction_delete_batch_case41(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "41"
    # Exception
    mocker.patch("util.s3Util.s3UtilClass.deleteFile").side_effect = Exception('testException')
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# No.42 ◆正常系 S3のファイル削除処理が1回目で成功する
def test_transaction_delete_batch_case42(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "42"
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# 02.S3のファイル削除チェック処理
# No.43 ◆正常系 「変数．エラー情報」がNull以外
def test_transaction_delete_batch_case43(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "43"
    # Exception
    mocker.patch("util.s3Util.s3UtilClass.deleteFile").return_value = False
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# No.44 ◆正常系 「変数．エラー情報」がNull
def test_transaction_delete_batch_case44(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "44"
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# 03.S3のファイル削除エラー処理
# No.45 ◆正常系
def test_transaction_delete_batch_case45(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "45"
    # Exception
    mocker.patch("util.s3Util.s3UtilClass.deleteFile").return_value = False
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# 04.終了処理
# No.46 ◆正常系
def test_transaction_delete_batch_case46(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "46"
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# 個人情報削除処理
# 01.MongoDB接続準備処理
# No.47 ◆異常系 接続に失敗する 設定値を異常な値に変更する
def test_transaction_delete_batch_case47(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "47"
    # Exception
    mocker.patch("util.commonUtil.CommonUtilClass.get_mongo_db_info_and_connection").side_effect = Exception('testException')
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# No.48 ◆正常系 接続に成功する プログラムが配置されたリージョンが東京リージョンaの場合
def test_transaction_delete_batch_case48(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "48"
    # Exception
    mocker.patch.object(SystemConstClass, "AWS_CONST", {"REGION": "ap-northeast-1"})
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# No.49 ◆正常系 接続に成功する プログラムが配置されたリージョンが大阪リージョンaの場合
def test_transaction_delete_batch_case49(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "49"
    # Exception
    mocker.patch.object(SystemConstClass, "AWS_CONST", {"REGION": "ap-northeast-3"})
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# No.50 ◆正常系 接続に成功する プログラムが配置されたリージョンが東京リージョンcの場合
def test_transaction_delete_batch_case50(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "50"
    # Exception
    mocker.patch.object(SystemConstClass, "AWS_CONST", {"REGION": "ap-northeast-1"})
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# No.51 ◆正常系 接続に成功する プログラムが配置されたリージョンが大阪リージョンcの場合
def test_transaction_delete_batch_case51(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "51"
    # Exception
    mocker.patch.object(SystemConstClass, "AWS_CONST", {"REGION": "ap-northeast-3"})
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# 02.MongoDBトランザクション作成処理
# No.52 トランザクション作成処理実行 「MongoDB個人情報削除トランザクション」を作成する


# 03.MongoDB削除判定処理
# No.53 ◆正常系 「引数．MongoDBデータ削除フラグ」がtrue
def test_transaction_delete_batch_case53(create_header):
    # 条件を満たすレコードを用意すること
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "53"
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# No.54 ◆正常系 「引数．MongoDBデータ削除フラグ」がtrue以外
def test_transaction_delete_batch_case54(create_header):
    # 条件を満たすレコードを用意すること
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "54"
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# 04.MongoDBデータ削除処理
# 05.共通エラーチェック処理
# No.55 ◆異常系 MongoDBデータ削除処理が失敗する
def test_transaction_delete_batch_case55(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "55"
    # Exception
    mocker.patch("util.mongoDbUtil.MongoDbClass.delete_object_id").return_value = {
        "result": False,
        "errorCode": "999999",
        "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
    }
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# 04.MongoDBデータ削除処理
# No.56 ◆正常系 MongoDBデータ削除処理が成功する
def test_transaction_delete_batch_case56(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "56"
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# 06.個人情報削除処理
# 07.共通エラーチェック処理
# No.57 ◆異常系 個人情報削除処理が失敗する
def test_transaction_delete_batch_case57(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "57"
    # Exception
    mocker.patch.object(SqlConstClass, "TRANSACTION_DELETE_DATA_DELETE_SQL", """ SELECT * FROM AAAAAA; """)
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# 06.個人情報削除処理
# No.58 ◆正常系 個人情報削除処理が成功する
def test_transaction_delete_batch_case58(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "58"
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# 08.MongoDBトランザクションコミット処理
# No.59 ◆正常系 「MongoDB個人情報削除トランザクション」のコミット処理が成功する
def test_transaction_delete_batch_case59(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "59"
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# 09.終了処理
# No.60 正常系
def test_transaction_delete_batch_case60(create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "60"
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# ロールバック処理
# 個人情報削除トランザクション
# 01.ロールバック処理
# 02.共通エラーチェック処理
# No.61 ロールバック処理が失敗すること
def test_transaction_delete_batch_case61(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "61"
    # Exception
    mocker.patch.object(SqlConstClass, "TRANSACTION_DELETE_BINARY_SPLIT_DELETE_SQL", """ SELECT * FROM AAAAAA; """)
    mocker.patch.object(PostgresDbUtilClass, "rollback_transaction", side_effect=Exception('testException'))
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# 01.ロールバック処理
# No.62 ロールバック処理が成功すること
def test_transaction_delete_batch_case62(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "62"
    # Exception
    mocker.patch.object(SqlConstClass, "TRANSACTION_DELETE_BINARY_SPLIT_DELETE_SQL", """ SELECT * FROM AAAAAA; """)
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# 03.終了処理
# No.63 ◆正常系
def test_transaction_delete_batch_case63(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "63"
    # Exception
    mocker.patch.object(SqlConstClass, "TRANSACTION_DELETE_BINARY_SPLIT_DELETE_SQL", """ SELECT * FROM AAAAAA; """)
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# MongoDBロールバック処理
# 01.MongoDBロールバック処理
# 02.共通エラーチェック処理
# No.64 MongoDBロールバック処理が失敗すること
def test_transaction_delete_batch_case64(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "64"
    # Exception
    mocker.patch("util.mongoDbUtil.MongoDbClass.delete_object_id").return_value = {"result": False, "errorCode": "999999", "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")}
    mocker.patch.object(PostgresDbUtilClass, "rollback_transaction", side_effect=Exception('testException'))
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# 01.MongoDBロールバック処理
# No.65 MongoDBロールバック処理が成功すること
def test_transaction_delete_batch_case65(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "65"
    # Exception
    mocker.patch("util.mongoDbUtil.MongoDbClass.delete_object_id").return_value = {"result": False, "errorCode": "999999", "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")}
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))


# 03.終了処理
# No.66 ◆正常系
def test_transaction_delete_batch_case66(mocker: MockerFixture, create_header):
    header = create_header["header"]
    data_copy = DATA.copy()
    data_copy["transactionId"] = DATA["transactionId"] + "66"
    # Exception
    mocker.patch("util.mongoDbUtil.MongoDbClass.delete_object_id").return_value = {"result": False, "errorCode": "999999", "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")}
    client.post("/api/2.0/batch/transactionDelete", headers=header, data=json.dumps(data_copy))
