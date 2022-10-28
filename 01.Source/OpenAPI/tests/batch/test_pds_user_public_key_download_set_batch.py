from fastapi.testclient import TestClient
from const.systemConst import SystemConstClass
from app import app
import pytest
from fastapi import Request
from util.commonUtil import CommonUtilClass
import util.commonUtil as commonUtil
from pytest_mock.plugin import MockerFixture
from const.sqlConst import SqlConstClass
from util.postgresDbUtil import PostgresDbUtilClass
import util.logUtil as logUtil

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
# PDSユーザテスト挿入用データ
TEST_PDS_USER_INSERT_DATA = {
    "pdsUserId": TEST_INSERT_DATA_1["pdsUserId"],
    "groupId": "G0000001",
    "pdsUserName": "PDSユーザテスト",
    "pdsUserDomainName": "token-create",
    "apiKey": None,
    "pdsUserInstanceSecretName": "pds-c0000000-sm",
    "s3ImageDataBucketName": "pds-c0000000-bucket",
    "tokyoAMongodbSecretName": "pds-c0000000-mongo-tokyo-a-sm",
    "tokyoCMongodbSecretName": "pds-c0000000-mongo-tokyo-c-sm",
    "osakaAMongodbSecretName": "pds-c0000000-mongo-osaka-a-sm",
    "osakaCMongodbSecretName": "pds-c0000000-mongo-osaka-c-sm",
    "userProfileKmsId": None,
    "validFlg": True,
    "salesAddress": "test1@gmail.com",
    "downloadNoticeAddressTo": None,
    "downloadNoticeAddressCc": None,
    "deleteNoticeAddressTo": None,
    "deleteNoticeAddressCc": None,
    "credentialNoticeAddressTo": None,
    "credentialNoticeAddressCc": None
}
# PDSユーザ公開鍵テスト挿入用データ
TEST_PDS_USER_KEY_INSERT_DATA = {
    "pdsUserId": TEST_INSERT_DATA_1["pdsUserId"],
    "pdsKeyIdx": 1,
    "pdsKey": "+JpVou7KdEMg226QOplCEAYJD0=",
    "tfKeyKmsId": "441110cd-1a08-4f71-980b-9c3ee8d86747",
    "startDate": "2022/08/23",
    "updateDate": "2022/08/23",
    "endDate": "2022/08/23",
    "wbtSendMailId": "test0001",
    "wbtReplyDeadlineDate": commonUtil.get_str_date(),
    "wbtReplyDeadlineCheckFlg": False,
    "wbtSendMailTitle": "【VRM/PDS v2.0】 PDSユーザ公開鍵通知・確認メール 1b5a05ee330f4b7ba62111e803f8de27",
    "validFlg": True
}
# PDSユーザPDSユーザ公開鍵テーブル検索処理
PDS_USER_PDS_USER_KEY_SELECT_SQL = """
    SELECT
        m_pds_user_key.pds_user_id
        , m_pds_user_key.pds_key_idx
    FROM
        m_pds_user
        INNER JOIN m_pds_user_key
        ON(m_pds_user.pds_user_id = m_pds_user_key.pds_user_id)
    WHERE
        m_pds_user_key.pds_user_id = %s
        AND m_pds_user_key.pds_key_idx = %s;
"""
# PDSユーザテーブル削除SQL
PDS_USER_DELETE_SQL = """
    DELETE FROM m_pds_user
    WHERE
        m_pds_user.pds_user_id = %s;
"""
# PDSユーザ公開鍵テーブル削除SQL
PDS_USER_KEY_DELETE_SQL = """
    DELETE FROM m_pds_user_key
    WHERE
        m_pds_user.pds_user_id = %s
        AND m_pds_user.pds_key_idx = %s;
"""


# テスト用のPDSユーザクラス
class testPdsUser:
    def __init__(self):
        pass

    def insert(self, data1: list, data2: list):
        common_db_connection_resource: PostgresDbUtilClass = None
        common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
        common_db_connection = common_db_info_response["common_db_connection"]

        pds_user_result = common_db_connection_resource.select_tuple_one(
            common_db_connection,
            PDS_USER_PDS_USER_KEY_SELECT_SQL,
            data2["pdsUserId"],
            data2["pdsKeyIdx"]
        )
        print(pds_user_result)

        if pds_user_result["rowcount"] == 0:
            # PDSユーザ登録
            response = common_db_connection_resource.insert(
                common_db_connection,
                SqlConstClass.PDS_USER_INSERT_SQL,
                data1["pdsUserId"],
                data1["groupId"],
                data1["pdsUserName"],
                data1["pdsUserDomainName"],
                data1["apiKey"],
                data1["pdsUserInstanceSecretName"],
                data1["s3ImageDataBucketName"],
                data1["tokyoAMongodbSecretName"],
                data1["tokyoCMongodbSecretName"],
                data1["osakaAMongodbSecretName"],
                data1["osakaCMongodbSecretName"],
                data1["userProfileKmsId"],
                data1["validFlg"],
                data1["salesAddress"],
                data1["downloadNoticeAddressTo"],
                data1["downloadNoticeAddressCc"],
                data1["deleteNoticeAddressTo"],
                data1["deleteNoticeAddressCc"],
                data1["credentialNoticeAddressTo"],
                data1["credentialNoticeAddressCc"]
            )
            print(response)
            # PDSユーザ公開鍵登録
            response = common_db_connection_resource.insert(
                common_db_connection,
                SqlConstClass.PDS_USER_KEY_INSERT_SQL,
                data2["pdsUserId"],
                data2["pdsKeyIdx"],
                data2["pdsKey"],
                data2["tfKeyKmsId"],
                data2["startDate"],
                data2["updateDate"],
                data2["endDate"],
                data2["wbtReplyDeadlineDate"],
                data2["wbtReplyDeadlineCheckFlg"],
                data2["wbtSendMailId"],
                data2["wbtSendMailTitle"],
                data2["validFlg"]
            )
            print(response)
            # トランザクションコミット処理
            common_db_connection_resource.commit_transaction(common_db_connection)

    def selectPdsUser(self, wbtReplyDeadlineDate: str):
        common_db_connection_resource: PostgresDbUtilClass = None
        common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
        common_db_connection = common_db_info_response["common_db_connection"]

        pds_user_result = common_db_connection_resource.select_tuple_one(
            common_db_connection,
            SqlConstClass.PDS_USER_PDS_USER_PUBLIC_KEY_SELECT_WBT_SENDER_SQL,
            wbtReplyDeadlineDate
        )
        print(pds_user_result)

        if pds_user_result["rowcount"] == 0:
            return {
                "rowcount": pds_user_result["rowcount"]
            }

        pds_user_column_list = [
            "pds_user_id",
            "pds_key_idx"
        ]
        pds_user_data_list = pds_user_result["query_results"]
        pds_user_dict = {column: data for column, data in zip(pds_user_column_list, pds_user_data_list)}
        return {
            "rowcount": pds_user_result["rowcount"],
            "pdsUser": pds_user_dict
        }

    def delete(self, pdsUserId: str, pdsKeyIdx: str):
        common_db_connection_resource: PostgresDbUtilClass = None
        common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
        common_db_connection = common_db_info_response["common_db_connection"]

        responsePdsUserKey = common_db_connection_resource.delete(
            common_db_connection,
            PDS_USER_KEY_DELETE_SQL,
            pdsUserId,
            pdsKeyIdx
        )
        print(responsePdsUserKey)
        responsePdsUser = common_db_connection_resource.delete(
            common_db_connection,
            PDS_USER_DELETE_SQL,
            pdsUserId
        )
        print(responsePdsUser)

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
    test = testPdsUser()
    return test


# No1.メイン処理_01.共通DB接続準備処理　異常系　接続に失敗する　設定値を異常な値に変更する
def test_pds_user_public_key_download_set_batch_case1(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.commonUtil.CommonUtilClass.get_secret_info").return_value = {"host": "test", "port": "test", "username": "test", "password": "test"}
    header = create_header["header"]
    client.post("/api/2.0/batch/pdsUserPublicKeyDownload", headers=header)


# No2.メイン処理_01.共通DB接続準備処理　正常系　接続に成功する
# No5.メイン処理_02.PDSユーザPDSユーザ公開鍵情報取得処理　正常系　PDSユーザPDSユーザ公開鍵情報取得処理で取得結果が2件
# No7.メイン処理_04.WBT送信詳細情報取得API実行処理　正常系　WBT受信一覧取得API実行処理で取得結果が2件　WBT送信詳細情報取得API実行処理が成功する
# No9.メイン処理_04.WBT送信詳細情報取得API実行処理　正常系　WBT送信詳細情報取得API実行処理が成功する
# No25.メイン処理_14.WBTダウンロードAPI実行処理　正常系　WBTダウンロードAPI実行処理が成功する
# No26.メイン処理_16.トランザクション作成処理　正常系　トランザクション作成処理実行
# No28.メイン処理_17.PDSユーザ公開鍵テーブル更新処理　正常系　PDSユーザ公開鍵テーブル更新処理が成功する
# No29.メイン処理_19.トランザクションコミット処理　正常系　「PDSユーザ公開鍵更新トランザクション」のコミット処理が成功する
# No30.メイン処理_20.ダウンロードファイル削除処理　正常系　ダウンロードファイル削除処理が成功する　「変数．ダウンロードファイル」にNullが格納されること
# No31.メイン処理_21.終了処理　正常系
def test_pds_user_public_key_download_set_batch_case2(db: testPdsUser, create_header):
    # テストデータ作成
    db.insert(TEST_PDS_USER_INSERT_DATA, TEST_PDS_USER_KEY_INSERT_DATA)
    header = create_header["header"]
    client.post("/api/2.0/batch/pdsUserPublicKeyDownload", headers=header)

    # 最後にテストデータを削除する
    db.delete(TEST_PDS_USER_KEY_INSERT_DATA["pdsUserId"], TEST_PDS_USER_KEY_INSERT_DATA["pdsKeyIdx"])


# No3.メイン処理_02.PDSユーザPDSユーザ公開鍵情報取得処理_03.共通エラーチェック処理　異常系　PDSユーザPDSユーザ公開鍵情報取得処理が失敗する
def test_pds_user_public_key_download_set_batch_case3(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "PDS_USER_PDS_USER_PUBLIC_KEY_SELECT_WBT_SENDER_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    client.post("/api/2.0/batch/pdsUserPublicKeyDownload", headers=header)


# No4.メイン処理_02.PDSユーザPDSユーザ公開鍵情報取得処理_03.共通エラーチェック処理　正常系　PDSユーザPDSユーザ公開鍵情報取得処理で取得結果が0件
def test_pds_user_public_key_download_set_batch_case4(mocker: MockerFixture, create_header):
    header = create_header["header"]
    client.post("/api/2.0/batch/pdsUserPublicKeyDownload", headers=header)


# No27.17.PDSユーザ公開鍵テーブル更新処理_18.共通エラーチェック処理　異常系　PDSユーザ公開鍵テーブル更新処理が失敗する
# No32.01.ロールバック処理_02.共通エラーチェック処理　ロールバック処理が失敗すること
def test_pds_user_public_key_download_set_batch_case27(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "PDS_USER_PUBLIC_KEY_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    # Exception
    mocker.patch.object(PostgresDbUtilClass, "rollback_transaction", side_effect=Exception('testException'))
    header = create_header["header"]
    client.post("/api/2.0/batch/pdsUserPublicKeyDownload", headers=header)


# No33.01.ロールバック処理　ロールバック処理が成功すること
def test_pds_user_public_key_download_set_batch_case33(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch.object(SqlConstClass, "PDS_USER_PUBLIC_KEY_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    client.post("/api/2.0/batch/pdsUserPublicKeyDownload", headers=header)
