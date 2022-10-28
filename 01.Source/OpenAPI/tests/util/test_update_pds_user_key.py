from fastapi.testclient import TestClient
from util.commonUtil import CommonUtilClass
from app import app
from fastapi import Request
import pytest
from pytest_mock.plugin import MockerFixture
from util.tokenUtil import TokenUtilClass
import util.logUtil as logUtil
# import json
from exceptionClass.PDSException import PDSException
from const.messageConst import MessageConstClass
from util.postgresDbUtil import PostgresDbUtilClass
from const.systemConst import SystemConstClass

# 定数クラス
from const.sqlConst import SqlConstClass

client = TestClient(app)

BEARER = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0Zk9wZXJhdG9ySWQiOiJsLXRlc3QiLCJ0Zk9wZXJhdG9yTmFtZSI6Ilx1MzBlZFx1MzBiMFx1MzBhNFx1MzBmM1x1MzBjNlx1MzBiOVx1MzBjOCIsInRmT3BlcmF0b3JQYXNzd29yZFJlc2V0RmxnIjpmYWxzZSwiYWNjZXNzVG9rZW4iOiJiZGE4ZGY3OThiYzViZGZhMWZkODIyNmRiYmQ0OTMyMTY5ZmY5MjAzNWM0YzFlY2FjZjY2OGUyYzk2ZjAwZThlZTUxNTBiNGM0NTc0NjlkN2I4YmY1NzIxZDZlM2NiNzFiY2RiYzA3ODRiYzcyZWVlNjk1OGE3NTBiMWJkMWEzZWFmZWQ0OWFhNWU0ODZjYzQyZmM3OWNhMWY3MGQzZmM3Yzc0YzE5NjM3ODUzMjRhZDRhNGM0NjkxOGE4NjQ1N2ZiODE3NDU1MCIsImV4cCI6MTY2MTc0NjY3MX0.LCRjPEqKMkRQ_phaYnO7S7pd3SU_rgon-wsX14DBsPA"
ACCESS_TOKEN = "bda8df798bc5bdfa1fd8226dbbd4932169ff92035c4c1ecacf668e2c96f00e8ee5150b4c457469d7b8bf5721d6e3cb71bcdbc0784bc72eee6958a750b1bd1a3eafed49aa5e486cc42fc79ca1f70d3fc7c74c1963785324ad4a4c46918a86457fb8174550"
HEADER = {"pdsUserId": "C5100001", "pdsKeyIdx": "1", "pdsUserDomainName": "pds-user-create", "Content-Type": "application/json", "timeStamp": "2022/08/23 15:12:01.690", "accessToken": ACCESS_TOKEN, "Authorization": "Bearer " + BEARER}
# 検証に使用するデータ
# pdsKeyが存在する
DATA_PDS_KEY_EXIST = {
    "pdsUserId": HEADER["pdsUserId"],
    "pdsKeyIdx": HEADER["pdsKeyIdx"],
    "pdsKey": "key",
    "endDate": None
}
# endDateが存在する
# "endDate": "2022-12-31T00:30:00.000Z"
DATA_END_DATE_EXIST = {
    "pdsUserId": HEADER["pdsUserId"],
    "pdsKeyIdx": HEADER["pdsKeyIdx"],
    "pdsKey": None,
    "endDate": "2022-12-31"
}
# テスト挿入用データ
TEST_INSERT_DATA = {
    "pdsUserId": HEADER["pdsUserId"],
    "pdsKeyIdx": HEADER["pdsKeyIdx"],
    "pdsKey": "+JpVou7KdEMg226QOplCEAYJD0=",
    "tfKeyKmsId": "441110cd-1a08-4f71-980b-9c3ee8d86747",
    "startDate": "2022/08/22",
    "updateDate": "2023/08/22",
    "endDate": None,
    "wbtSendMailId": "",
    "wbtReplyDeadlineDate": None,
    "wbtReplyDeadlineCheckFlg": False,
    "wbtSendMailTitle": "",
    "validFlg": True
}
# PDSユーザ公開鍵テーブル検索処理
PDS_USER_KEY_SELECT_SQL = """
    SELECT
        pds_user_id
        , pds_key_idx
        , pds_key
        , tf_key_kms_id
        , start_date
        , update_date
        , end_date
        , wbt_send_mail_id
        , wbt_reply_deadline_date
        , wbt_reply_deadline_check_flg
        , wbt_send_mail_title
        , valid_flg
    FROM
        m_pds_user_key
    WHERE
        m_pds_user_key.pds_user_id = %s
        AND m_pds_user_key.pds_key_idx = %s;
"""
# PDSユーザ公開鍵テーブル削除SQL
PDS_USER_PUBLIC_KEY_DELETE_SQL = """
    DELETE FROM m_pds_user_key
    WHERE
        m_pds_user_key.pds_user_id = %s
        AND m_pds_user_key.pds_key_idx = %s;
"""


trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, "Test", "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
token_util = TokenUtilClass(trace_logger)
common_util = CommonUtilClass(trace_logger)
# 共通DB接続準備処理
common_db_info_response = common_util.get_common_db_info_and_connection()


# テスト用のPDSユーザ公開鍵更新クラス
class testUpdatePdsUser:
    def __init__(self):
        pass

    def insert(self):
        common_db_connection_resource: PostgresDbUtilClass = None
        common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
        common_db_connection = common_db_info_response["common_db_connection"]

        response = common_db_connection_resource.insert(
            common_db_connection,
            SqlConstClass.PDS_USER_KEY_INSERT_SQL,
            TEST_INSERT_DATA["pdsUserId"],
            TEST_INSERT_DATA["pdsKeyIdx"],
            TEST_INSERT_DATA["pdsKey"],
            TEST_INSERT_DATA["tfKeyKmsId"],
            TEST_INSERT_DATA["startDate"],
            TEST_INSERT_DATA["updateDate"],
            TEST_INSERT_DATA["endDate"],
            TEST_INSERT_DATA["wbtReplyDeadlineDate"],
            TEST_INSERT_DATA["wbtReplyDeadlineCheckFlg"],
            TEST_INSERT_DATA["wbtSendMailId"],
            TEST_INSERT_DATA["wbtSendMailTitle"],
            TEST_INSERT_DATA["validFlg"]
        )
        print(response)
        # トランザクションコミット処理
        common_db_connection_resource.commit_transaction(common_db_connection)

    def select(self):
        common_db_connection_resource: PostgresDbUtilClass = None
        common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
        common_db_connection = common_db_info_response["common_db_connection"]

        pds_user_key_result = common_db_connection_resource.select_tuple_one(
            common_db_connection,
            PDS_USER_KEY_SELECT_SQL,
            HEADER["pdsUserId"],
            HEADER["pdsKeyIdx"]
        )
        print(pds_user_key_result)

        if pds_user_key_result["rowcount"] == 0:
            return {
                "rowcount": pds_user_key_result["rowcount"]
            }

        pds_user_key_column_list = [
            "pdsUserId",
            "pdsKeyIdx",
            "pdsKey",
            "tfKeyKmsId",
            "startDate",
            "updateDate",
            "endDate",
            "wbtSendMailId",
            "wbtReplyDeadlineDate",
            "wbtReplyDeadlineCheckFlg",
            "wbtSendMailTitle",
            "validFlg"
        ]
        ppds_user_key_data_list = pds_user_key_result["query_results"]
        pds_user_key_dict = {column: data for column, data in zip(pds_user_key_column_list, ppds_user_key_data_list)}
        return {
            "rowcount": pds_user_key_result["rowcount"],
            "pdsUserKey": pds_user_key_dict
        }

    def delete(self):
        common_db_connection_resource: PostgresDbUtilClass = None
        common_db_connection_resource = common_db_info_response["common_db_connection_resource"]
        common_db_connection = common_db_info_response["common_db_connection"]

        response = common_db_connection_resource.delete(
            common_db_connection,
            PDS_USER_PUBLIC_KEY_DELETE_SQL,
            HEADER["pdsUserId"],
            HEADER["pdsKeyIdx"]
        )
        print(response)

        # トランザクションコミット処理
        common_db_connection_resource.commit_transaction(common_db_connection)


@pytest.fixture
def db():
    test = testUpdatePdsUser()
    result = test.select()
    if result["rowcount"] == 0:
        test.insert()
    return test


# No1.PDSユーザ公開鍵更新処理_01.引数検証処理チェック　異常系　引数．PDSユーザID　値が設定されていない（空値）
# No2.PDSユーザ公開鍵更新処理_01.引数検証処理チェック　異常系　PDSユーザIDが異常な値
def test_update_pds_user_key_case1_1_1():
    data_copy = DATA_PDS_KEY_EXIST.copy()
    data_copy["pdsUserId"] = ""
    with pytest.raises(PDSException) as e:
        common_util.update_pds_user_key(
            pdsUserId=data_copy["pdsUserId"],
            pdsKeyIdx=data_copy["pdsKeyIdx"],
            pdsKey=data_copy["pdsKey"],
            endDate=data_copy["endDate"],
            common_db_info=common_db_info_response
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "PDSユーザID")
    }
    print(e)


# No1.PDSユーザ公開鍵更新処理_01.引数検証処理チェック　異常系　引数．PDSユーザ公開鍵インデックス　値が設定されていない（空値）
# No4.PDSユーザ公開鍵更新処理_01.引数検証処理チェック　異常系　PDSユーザ公開鍵インデックスが異常な値
def test_update_pds_user_key_case1_2_1():
    data_copy = DATA_PDS_KEY_EXIST.copy()
    data_copy["pdsKeyIdx"] = ""
    with pytest.raises(PDSException) as e:
        common_util.update_pds_user_key(
            pdsUserId=data_copy["pdsUserId"],
            pdsKeyIdx=data_copy["pdsKeyIdx"],
            pdsKey=data_copy["pdsKey"],
            endDate=data_copy["endDate"],
            common_db_info=common_db_info_response
        )
    assert e.type == PDSException
    assert e.value.args[0] == {
        "errorCode": "020001",
        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "PDSユーザ公開鍵インデックス")
    }
    print(e)


# No1.PDSユーザ公開鍵更新処理_01.引数検証処理チェック　正常系　引数．PDSユーザID　値が設定されている
# No1.PDSユーザ公開鍵更新処理_01.引数検証処理チェック　正常系　引数．PDSユーザ公開鍵インデックス　値が設定されている
# No3.PDSユーザ公開鍵更新処理_01.引数検証処理チェック　正常系　PDSユーザIDが正常な値
# No5.PDSユーザ公開鍵更新処理_01.引数検証処理チェック　正常系　PDSユーザ公開鍵インデックスが正常な値
# No9.PDSユーザ公開鍵更新処理_03.終了処理　正常系　変数．エラー情報がない
def test_update_pds_user_key_case1_1_2(db: testUpdatePdsUser):
    data_copy = DATA_PDS_KEY_EXIST.copy()
    response = common_util.update_pds_user_key(
        pdsUserId=data_copy["pdsUserId"],
        pdsKeyIdx=data_copy["pdsKeyIdx"],
        pdsKey=data_copy["pdsKey"],
        endDate=data_copy["endDate"],
        common_db_info=common_db_info_response
    )
    assert response == {
        "result": True
    }
    print(response)

    # 最後にテスト用に挿入したデータを削除する
    db.delete()


# No6.PDSユーザ公開鍵更新処理_02.PDSユーザ公開鍵更新処理　異常系　postgresqlのエラーが発生
# PDSユーザ公開鍵更新処理(PDSユーザ公開鍵存在)
def test_update_pds_user_key_case6_1(mocker: MockerFixture):
    data_copy = DATA_PDS_KEY_EXIST.copy()
    mocker.patch.object(SqlConstClass, "PDS_USER_UPDATE_SQL_PDS_USER_KEY_CONDITION", """ SELECT * FROM AAAAAA; """)
    response = common_util.update_pds_user_key(
        pdsUserId=data_copy["pdsUserId"],
        pdsKeyIdx=data_copy["pdsKeyIdx"],
        pdsKey=data_copy["pdsKey"],
        endDate=data_copy["endDate"],
        common_db_info=common_db_info_response
    )
    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "999999",
            "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
        }
    }
    print(response)


# No6.PDSユーザ公開鍵更新処理_02.PDSユーザ公開鍵更新処理　異常系　postgresqlのエラーが発生
# PDSユーザ公開鍵更新処理(終了日存在)
def test_update_pds_user_key_case6_2(mocker: MockerFixture):
    data_copy = DATA_END_DATE_EXIST.copy()
    mocker.patch.object(SqlConstClass, "PDS_USER_UPDATE_SQL_END_DATE_CONDITION", """ SELECT * FROM AAAAAA; """)
    response = common_util.update_pds_user_key(
        pdsUserId=data_copy["pdsUserId"],
        pdsKeyIdx=data_copy["pdsKeyIdx"],
        pdsKey=data_copy["pdsKey"],
        endDate=data_copy["endDate"],
        common_db_info=common_db_info_response
    )
    assert response == {
        "result": False,
        "errorInfo": {
            "errorCode": "999999",
            "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
        }
    }
    print(response)


# No7.PDSユーザ公開鍵更新処理_02.PDSユーザ公開鍵更新処理　正常系　PDSユーザ公開鍵更新処理が成功する
# PDSユーザ公開鍵更新処理(PDSユーザ公開鍵存在)
def test_update_pds_user_key_case7(db: testUpdatePdsUser):
    data_copy = DATA_PDS_KEY_EXIST.copy()
    response = common_util.update_pds_user_key(
        pdsUserId=data_copy["pdsUserId"],
        pdsKeyIdx=data_copy["pdsKeyIdx"],
        pdsKey=data_copy["pdsKey"],
        endDate=data_copy["endDate"],
        common_db_info=common_db_info_response
    )
    assert response == {
        "result": True
    }
    print(response)

    # データ検証
    result = db.select()
    # PDSユーザ公開鍵．PDSユーザ公開鍵=引数.PDSユーザ公開鍵
    assert data_copy["pdsKey"] == result["pdsUserKey"]["pdsKey"]
    # PDSユーザ公開鍵．WBT返信期限確認=true
    assert result["pdsUserKey"]["wbtReplyDeadlineCheckFlg"]

    # 最後にテスト用に挿入したデータを削除する
    db.delete()


# No8.PDSユーザ公開鍵更新処理_02.PDSユーザ公開鍵更新処理　正常系　PDSユーザ公開鍵更新処理が成功する
# PDSユーザ公開鍵更新処理(終了日存在)
def test_update_pds_user_key_case8(db: testUpdatePdsUser):
    data_copy = DATA_END_DATE_EXIST.copy()
    response = common_util.update_pds_user_key(
        pdsUserId=data_copy["pdsUserId"],
        pdsKeyIdx=data_copy["pdsKeyIdx"],
        pdsKey=data_copy["pdsKey"],
        endDate=data_copy["endDate"],
        common_db_info=common_db_info_response
    )
    assert response == {
        "result": True
    }
    print(response)

    # データ検証
    result = db.select()
    # PDSユーザ公開鍵．終了日=引数.PDSユーザ公開鍵終了日
    # TODO:result["pdsUserKey"]["endDate"]の戻り値がdatetime.dateなので.strftime('%Y-%m-%d')で変換
    assert data_copy["endDate"] == result["pdsUserKey"]["endDate"].strftime('%Y-%m-%d')
    # PDSユーザ公開鍵．有効フラグ=false
    assert not result["pdsUserKey"]["validFlg"]

    # 最後にテスト用に挿入したデータを削除する
    db.delete()
