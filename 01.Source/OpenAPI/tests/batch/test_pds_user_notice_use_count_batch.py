from fastapi.testclient import TestClient
from const.sqlConst import SqlConstClass
from app import app
from fastapi import Request
import pytest
from pytest_mock.plugin import MockerFixture
from util.tokenUtil import TokenUtilClass
import util.logUtil as logUtil
from util.billUtil import BillUtilClass
from const.systemConst import SystemConstClass
from util.fileUtil import HeaderDictItemCsvStringClass

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
def test_pds_user_notice_use_count_batch_case1(mocker: MockerFixture, create_header):
    # Exception
    mocker.patch("util.commonUtil.CommonUtilClass.get_secret_info").return_value = {"host": "test", "port": "test", "username": "test", "password": "test"}
    header = create_header["header"]
    client.post("/api/2.0/batch/pdsUserNoticeUseCountBatch", headers=header)


# No2.接続に成功する
def test_pds_user_notice_use_count_batch_case2(create_header):
    header = create_header["header"]
    client.post("/api/2.0/batch/pdsUserNoticeUseCountBatch", headers=header)


# 02.PDSユーザ情報取得処理
# 03.共通エラーチェック処理
# No3.postgresqlのエラーが発生
def test_pds_user_notice_use_count_batch_case3(mocker: MockerFixture, create_header):
    # Exception
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "PDS_USER_VALID_FLG_TRUE_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    client.post("/api/2.0/batch/pdsUserNoticeUseCountBatch", headers=header)


# 02.PDSユーザ情報取得処理
# No04.PDSユーザ情報取得処理で取得結果が0件
def test_pds_user_notice_use_count_batch_case4(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass,
                        "PDS_USER_VALID_FLG_TRUE_SELECT_SQL",
                        """ SELECT m_pds_user.pds_user_id, m_pds_user.pds_user_name, m_pds_user.sales_address FROM m_pds_user WHERE m_pds_user.valid_flg = True AND m_pds_user.pds_user_id = 'X0000005'; """
                        )
    client.post("/api/2.0/batch/pdsUserNoticeUseCountBatch", headers=header)


# No05.PDSユーザ情報取得処理で取得結果が2件
def test_pds_user_notice_use_count_batch_case5(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass,
                        "PDS_USER_VALID_FLG_TRUE_SELECT_SQL",
                        """ SELECT m_pds_user.pds_user_id, m_pds_user.pds_user_name, m_pds_user.sales_address FROM m_pds_user WHERE m_pds_user.valid_flg = True AND m_pds_user.pds_user_id IN ('C0000002', 'C0000003'); """
                        )
    client.post("/api/2.0/batch/pdsUserNoticeUseCountBatch", headers=header)


# 「変数．PDSユーザ情報取得結果リスト」の要素数分繰り返す
# No06.PDSユーザ情報取得処理で取得結果が0件
def test_pds_user_notice_use_count_batch_case6(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass,
                        "PDS_USER_VALID_FLG_TRUE_SELECT_SQL",
                        """ SELECT m_pds_user.pds_user_id, m_pds_user.pds_user_name, m_pds_user.sales_address FROM m_pds_user WHERE m_pds_user.valid_flg = True AND m_pds_user.pds_user_id = 'X0000005'; """
                        )
    client.post("/api/2.0/batch/pdsUserNoticeUseCountBatch", headers=header)


# 「変数．PDSユーザ情報取得結果リスト」の要素数分繰り返す
# 04. API実行履歴取得処理
# 05.共通エラーチェック処理
# No7.PDSユーザ情報取得処理で取得結果が2件
#      API実行履歴取得処理が失敗する
def test_pds_user_notice_use_count_batch_case7(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass,
                        "PDS_USER_VALID_FLG_TRUE_SELECT_SQL",
                        """ SELECT m_pds_user.pds_user_id, m_pds_user.pds_user_name, m_pds_user.sales_address FROM m_pds_user WHERE m_pds_user.valid_flg = True AND m_pds_user.pds_user_id IN ('C0000002', 'C0000003'); """
                        )
    mocker.patch.object(SqlConstClass, "API_HISTORY_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    client.post("/api/2.0/batch/pdsUserNoticeUseCountBatch", headers=header)


# No08.PDSユーザ情報取得処理で取得結果が2件
#       API実行履歴取得処理が成功する
def test_pds_user_notice_use_count_batch_case8(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass,
                        "PDS_USER_VALID_FLG_TRUE_SELECT_SQL",
                        """ SELECT m_pds_user.pds_user_id, m_pds_user.pds_user_name, m_pds_user.sales_address FROM m_pds_user WHERE m_pds_user.valid_flg = True AND m_pds_user.pds_user_id IN ('C0000002', 'C0000003'); """
                        )
    client.post("/api/2.0/batch/pdsUserNoticeUseCountBatch", headers=header)


# 06.API種別カウント作成処理
# No09.変数が初期化されている
def test_pds_user_notice_use_count_batch_case9(create_header):
    header = create_header["header"]
    client.post("/api/2.0/batch/pdsUserNoticeUseCountBatch", headers=header)


# 「変数．API実行履歴取得結果リスト」の要素数分繰り返す
# No10.API実行履歴取得処理で取得結果が0件
def test_pds_user_notice_use_count_batch_case10(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass,
                        "PDS_USER_VALID_FLG_TRUE_SELECT_SQL",
                        """ SELECT m_pds_user.pds_user_id, m_pds_user.pds_user_name, m_pds_user.sales_address FROM m_pds_user WHERE m_pds_user.valid_flg = True AND m_pds_user.pds_user_id IN ('C0000002', 'C0000003'); """
                        )
    client.post("/api/2.0/batch/pdsUserNoticeUseCountBatch", headers=header)


# 「変数．API実行履歴取得結果リスト」の要素数分繰り返す
# 07. 請求金額取得処理
# 08.共通エラーチェック処理
# No11.API実行履歴取得処理で取得結果がAPI種別ごとに複数件
#       請求金額取得処理が失敗する
def test_pds_user_notice_use_count_batch_case11(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass,
                        "API_HISTORY_SELECT_SQL",
                        """ SELECT m_pds_user.pds_user_id, m_pds_user.pds_user_name, m_pds_user.sales_address FROM m_pds_user WHERE m_pds_user.valid_flg = True AND m_pds_user.pds_user_id = 'C0000002'; """
                        )
    mocker.patch.object(SqlConstClass,
                        "PDS_USER_VALID_FLG_TRUE_SELECT_SQL",
                        """ SELECT m_pds_user.pds_user_id, m_pds_user.pds_user_name, m_pds_user.sales_address FROM m_pds_user WHERE m_pds_user.valid_flg = True AND m_pds_user.pds_user_id IN ('C0000002', 'C0000003'); """
                        )
    mocker.patch.object(SqlConstClass, "BILLING_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    client.post("/api/2.0/batch/pdsUserNoticeUseCountBatch", headers=header)


# No12.API実行履歴取得処理で取得結果がAPI種別ごとに複数件
#       請求金額取得処理が成功する（複数件取得）
def test_pds_user_notice_use_count_batch_case12(mocker: MockerFixture, create_header):
    header = create_header["header"]
    client.post("/api/2.0/batch/pdsUserNoticeUseCountBatch", headers=header)


# 09.累進請求金額計算処理
# No13.累進請求金額計算処理が失敗する
def test_pds_user_notice_use_count_batch_case13(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(BillUtilClass, "progressive_billing_exec", side_effect=Exception('testException'))
    client.post("/api/2.0/batch/pdsUserNoticeUseCountBatch", headers=header)


# No14.累進請求金額計算処理が成功する
# No15.正しく請求金額が計算されること
# No16~23.正しくカウントが加算されること
def test_pds_user_notice_use_count_batch_case14(create_header):
    header = create_header["header"]
    client.post("/api/2.0/batch/pdsUserNoticeUseCountBatch", headers=header)


# 12.リソース請求金額計算処理
# No24.リソース請求金額計算処理が失敗する
def test_pds_user_notice_use_count_batch_case24(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(BillUtilClass, "resource_billing_exec", side_effect=Exception('testException'))
    client.post("/api/2.0/batch/pdsUserNoticeUseCountBatch", headers=header)


# No25.リソース請求金額計算処理が成功する
# No26.「変数．請求金額」に「変数．リソース請求金額計算処理結果．リソース請求金額」を加算する
def test_pds_user_notice_use_count_batch_case25(create_header):
    header = create_header["header"]
    client.post("/api/2.0/batch/pdsUserNoticeUseCountBatch", headers=header)


# 14. CSVファイル作成処理
# No27.CSVファイル作成処理が失敗する
def test_pds_user_notice_use_count_batch_case27(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(HeaderDictItemCsvStringClass, "__init__", side_effect=Exception('testException'))
    client.post("/api/2.0/batch/pdsUserNoticeUseCountBatch", headers=header)


# No28.CSVファイル作成処理が成功する（０件）
# No29.CSVファイル作成処理が成功する（複数件）
def test_pds_user_notice_use_count_batch_case28(create_header):
    header = create_header["header"]
    client.post("/api/2.0/batch/pdsUserNoticeUseCountBatch", headers=header)


# 15.WBT新規メール情報登録API実行処理
# 16.共通エラーチェック処理
# No30.WBT新規メール情報登録API実行処理が失敗する
def test_pds_user_notice_use_count_batch_case30(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.commonUtil.CommonUtilClass.wbt_mails_add_api_exec").return_value = {"result": False}
    client.post("/api/2.0/batch/pdsUserNoticeUseCountBatch", headers=header)


# No31.WBT新規メール情報登録API実行処理が成功する
# No33.WBTファイル登録API実行処理が成功する
# No34.「変数．PDSユーザ利用回数ファイル」をNullにする
# No35.正常
def test_pds_user_notice_use_count_batch_case31(create_header):
    header = create_header["header"]
    client.post("/api/2.0/batch/pdsUserNoticeUseCountBatch", headers=header)


# 17.WBTファイル登録API実行処理
# 18.共通エラーチェック処理
# No32.WBTファイル登録API実行処理が失敗する
def test_pds_user_notice_use_count_batch_case32(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.commonUtil.CommonUtilClass.wbt_file_add_api_exec").return_value = {"result": False}
    client.post("/api/2.0/batch/pdsUserNoticeUseCountBatch", headers=header)


# 機能内結合テスト用テストコード
def test_pds_user_notice_use_count_batch_case(mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(SqlConstClass,
                        "PDS_USER_VALID_FLG_TRUE_SELECT_SQL",
                        """ SELECT m_pds_user.pds_user_id, m_pds_user.pds_user_name, m_pds_user.sales_address FROM m_pds_user WHERE m_pds_user.valid_flg = True AND m_pds_user.pds_user_id = 'C0000011'; """
                        )
    client.post("/api/2.0/batch/pdsUserNoticeUseCountBatch", headers=header)
