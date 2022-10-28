import os
import shutil
from fastapi.testclient import TestClient
from util.commonUtil import CommonUtilClass
from app import app
from fastapi import Request
import pytest
from pytest_mock.plugin import MockerFixture
import util.logUtil as logUtil
import json
from const.sqlConst import SqlConstClass
from const.systemConst import SystemConstClass
from const.messageConst import MessageConstClass
from util.mongoDbUtil import MongoDbClass
from util.postgresDbUtil import PostgresDbUtilClass
from pymongo.collection import Collection
from pymongo.client_session import ClientSession
from pymongo.errors import PyMongoError
from models.batch.transactionMultiCreateBatchModel import transactionMultiCreateBatchModelClass
from models.batch.transactionMultiCreateBatchModel import requestBody as modelRequestBody
from exceptionClass.PDSException import PDSException

client = TestClient(app)
EXEC_NAME: str = "transactionMultiCreateBatch"
EXEC_NAME_JP: str = "個人情報一括登録バッチ"

BEARER = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0Zk9wZXJhdG9ySWQiOiJsLXRlc3QiLCJ0Zk9wZXJhdG9yTmFtZSI6Ilx1MzBlZFx1MzBiMFx1MzBhNFx1MzBmM1x1MzBjNlx1MzBiOVx1MzBjOCIsInRmT3BlcmF0b3JQYXNzd29yZFJlc2V0RmxnIjpmYWxzZSwiYWNjZXNzVG9rZW4iOiJiZGE4ZGY3OThiYzViZGZhMWZkODIyNmRiYmQ0OTMyMTY5ZmY5MjAzNWM0YzFlY2FjZjY2OGUyYzk2ZjAwZThlZTUxNTBiNGM0NTc0NjlkN2I4YmY1NzIxZDZlM2NiNzFiY2RiYzA3ODRiYzcyZWVlNjk1OGE3NTBiMWJkMWEzZWFmZWQ0OWFhNWU0ODZjYzQyZmM3OWNhMWY3MGQzZmM3Yzc0YzE5NjM3ODUzMjRhZDRhNGM0NjkxOGE4NjQ1N2ZiODE3NDU1MCIsImV4cCI6MTY2MTc0NjY3MX0.LCRjPEqKMkRQ_phaYnO7S7pd3SU_rgon-wsX14DBsPA"
ACCESS_TOKEN = "bda8df798bc5bdfa1fd8226dbbd4932169ff92035c4c1ecacf668e2c96f00e8ee5150b4c457469d7b8bf5721d6e3cb71bcdbc0784bc72eee6958a750b1bd1a3eafed49aa5e486cc42fc79ca1f70d3fc7c74c1963785324ad4a4c46918a86457fb8174550"
HEADER = {"pdsUserId": "C9876543", "Content-Type": "application/json", "timeStamp": "2022/08/23 15:12:01.690", "accessToken": ACCESS_TOKEN, "Authorization": "Bearer " + BEARER}

REQUEST_BODY = {
    "pdsUserId": "C9876543"
}

KMS_ID = "fdb4c6aa-50b0-4ed1-bdad-32c21e0a0387"
BUCKET_NAME = "pds-c0000000-bucket"


PDS_USER_INFO_DICT = {
    "tokyo_a_mongodb_secret_name": "pds-c0000000-mongo-tokyo-a-sm",
    "tokyo_c_mongodb_secret_name": "pds-c0000000-mongo-tokyo-c-sm",
    "osaka_a_mongodb_secret_name": "pds-c0000000-mongo-osaka-a-sm",
    "osaka_c_mongodb_secret_name": "pds-c0000000-mongo-osaka-c-sm"
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


# No1.AWS SQSからのパラメータ取得処理に失敗する
#     RequestBodyは勝手に取得するので基本的に失敗はない
# No4.入力パラメータチェック処理が失敗する
def test_transaction_multi_create_case1(monkeypatch, mocker: MockerFixture, create_header):
    # 標準出力をモック
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy = {}
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No2.AWS SQSからのパラメータ取得処理に成功する
# No5.入力パラメータチェック処理が成功する
# No7.接続に成功する
# No11.PDSユーザ情報取得処理で取得結果が1件
# No13.zipファイルチェック処理が成功する
# No15.zipファイルダウンロード処理が成功する
# No16.zipファイル解凍処理が成功する
# No19.CSVファイルの内容チェック処理で成功する
# No21.接続に成功する
# No24.個人情報取得処理で取得結果が0件 個人情報取得処理が成功する
# No25.個人情報登録処理リスト初期化処理が成功する
# No26.Insert.csvから取得した行数が2件
# No27.個人情報登録処理リスト作成処理が成功する
# No29.個人情報登録処理実行処理が成功する
# No31.「変数．個人情報登録処理実行結果リスト」内を検索して、処理結果がfalseのデータが存在しない
# No37.個人情報更新処理が成功する
# No38.「個人情報更新トランザクション」のコミット処理が成功する
# No40.zipファイル削除処理が成功する
# No42.zipファイル解凍フォルダ削除処理が成功する
# No46.S3のzipファイルダウンロード元ファイル削除処理が1回で成功する
# No47.終了処理 正常終了
def test_transaction_multi_create_case2(monkeypatch, create_header):
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No3-1.PDSユーザID 値が設定されていない（空値）
def test_transaction_multi_create_case3_1(monkeypatch, create_header):
    # 標準出力をモック
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["pdsUserId"] = None
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No3-2.PDSユーザID 文字列型ではない、7桁である、C以外の文字から始まる
def test_transaction_multi_create_case3_2(monkeypatch, create_header):
    # 標準出力をモック
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["pdsUserId"] = 1234567
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No3-3.PDSユーザID 文字列型、9桁である、C+数値8桁
def test_transaction_multi_create_case3_3(monkeypatch, create_header):
    # 標準出力をモック
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["pdsUserId"] = "C12345678"
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No3-4.PDSユーザID 文字列型、8桁である、C+数値7桁
def test_transaction_multi_create_case3_4(monkeypatch, create_header):
    # 標準出力をモック
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["pdsUserId"] = "C9876543"
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No6.接続に失敗する。設定値を異常な値に変更する
@pytest.mark.asyncio
async def test_transaction_multi_create_case6(monkeypatch, mocker: MockerFixture, create_header):
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    mocker.patch.object(SystemConstClass, "PDS_COMMON_DB_SECRET_INFO", {"SECRET_NAME": "pds-common-sm-ng"})
    request_body_copy = REQUEST_BODY.copy()
    model = transactionMultiCreateBatchModelClass(trace_logger)
    model_request_body = modelRequestBody(**request_body_copy)
    with pytest.raises(PDSException) as e:
        await model.main(model_request_body)

    assert e.value.args[0] == {
        "errorCode": "999999",
        "message": e.value.args[0]["message"]
    }
    print(e)


# No8.PDSユーザ情報取得処理が失敗する
def test_transaction_multi_create_case8(monkeypatch, mocker: MockerFixture, create_header):
    # 標準出力をモック
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "MULTI_CREATE_BATCH_PDS_USER_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No9.PDSユーザ情報取得処理の取得件数が2件
def test_transaction_multi_create_case9(monkeypatch, mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch("util.postgresDbUtil.PostgresDbUtilClass.select_tuple_one").return_value = {"result": True, "rowcount": 2, "query_results": ("C9876543")}
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No10.PDSユーザ情報取得処理で取得結果が0件
def test_transaction_multi_create_case10(monkeypatch, mocker: MockerFixture, create_header):
    # 標準出力をモック
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["pdsUserId"] = "C3333333"
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No12.zipファイルチェック処理が失敗する
def test_transaction_multi_create_case12(monkeypatch, mocker: MockerFixture, create_header):
    # 標準出力をモック
    header = create_header["header"]
    mocker.patch.object(SystemConstClass, "USER_PROFILE_MULTI_CREATE_BUCKET", "aaaaa")
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No14.zipファイルダウンロード処理が失敗する
def test_transaction_multi_create_case14(monkeypatch, mocker: MockerFixture, create_header):
    # 標準出力をモック
    header = create_header["header"]
    mocker.patch("util.s3Util.s3UtilClass.get_zip_file").return_value = {"result": False, "errorInfo": {"errorCode": "990024", "message": logUtil.message_build(MessageConstClass.ERRORS["990024"]["message"], "990024")}}
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No17-1.TID 値が設定されていない
def test_transaction_multi_create_case17_1(monkeypatch, mocker: MockerFixture, create_header):
    # 標準出力をモック
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["pdsUserId"] = "C9000001"
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No17-2.TID 文字列型ではない、37桁、入力可能文字のみ
def test_transaction_multi_create_case17_2(monkeypatch, mocker: MockerFixture, create_header):
    # 標準出力をモック
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["pdsUserId"] = "C9000002"
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No17-3.TID 文字列型、37桁、入力可能文字以外が含まれる、値が重複している
def test_transaction_multi_create_case17_3(monkeypatch, mocker: MockerFixture, create_header):
    # 標準出力をモック
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["pdsUserId"] = "C9000003"
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No17-4.TID 文字列型、36桁、入力可能文字のみ、値が重複していない
def test_transaction_multi_create_case17_4(monkeypatch, mocker: MockerFixture, create_header):
    # 標準出力をモック
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["pdsUserId"] = "C9000004"
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No17-5.UserID 値が設定されていない
def test_transaction_multi_create_case17_5(monkeypatch, mocker: MockerFixture, create_header):
    # 標準出力をモック
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["pdsUserId"] = "C9000005"
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No17-6.UserID 文字列型ではない、37桁
def test_transaction_multi_create_case17_6(monkeypatch, mocker: MockerFixture, create_header):
    # 標準出力をモック
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["pdsUserId"] = "C9000006"
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No17-7.TID 文字列型、36桁
def test_transaction_multi_create_case17_7(monkeypatch, mocker: MockerFixture, create_header):
    # 標準出力をモック
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["pdsUserId"] = "C9000007"
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No17-8.DataKeyとDataValueヘッダ相関 〇番がペアになっていない、ヘッダのペアが1から順番に並んでいない、DataValue〇番に紐づくDataKeyに入力されていない、DataKey、DataValueをJSON変換した後の合計文字数が5000文字を超過している
def test_transaction_multi_create_case17_8(monkeypatch, mocker: MockerFixture, create_header):
    # 標準出力をモック
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["pdsUserId"] = "C9000008"
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No17-9.DataKeyとDataValueヘッダ相関 〇番がペアになっている、ヘッダのペアが1から順番に並んでいる、DataValue〇番に紐づくDataKeyに入力されている、DataKey、DataValueをJSON変換した後の合計文字数が5000文字を超過していない
def test_transaction_multi_create_case17_9(monkeypatch, mocker: MockerFixture, create_header):
    # 標準出力をモック
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["pdsUserId"] = "C9000009"
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No17-10.バイナリデータの格納フォルダが連番になっていない、バイナリデータ格納フォルダにファイルが配置されていない、バイナリデータ格納フォルダにファイルが複数配置されている。バイナリデータ格納フォルダに10MBを超過するファイルが配置されている、バイナリデータ格納フォルダに配置された合計ファイルサイズが100MBを超過している
def test_transaction_multi_create_case17_10(monkeypatch, mocker: MockerFixture, create_header):
    # 標準出力をモック
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["pdsUserId"] = "C9000010"
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No17-11.バイナリデータの格納フォルダが連番になっている、バイナリデータ格納フォルダにファイルが配置されている、バイナリデータ格納フォルダにファイルが複数配置されていない、バイナリデータ格納フォルダに10MBを超過するファイルが配置されていない、バイナリデータ格納フォルダに配置された合計ファイルサイズが100MBを超過していない
def test_transaction_multi_create_case17_11(monkeypatch, mocker: MockerFixture, create_header):
    # 標準出力をモック
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["pdsUserId"] = "C9000011"
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No17-12.セキュリティレベル 文字列型以外、3桁
def test_transaction_multi_create_case17_12(monkeypatch, mocker: MockerFixture, create_header):
    # 標準出力をモック
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["pdsUserId"] = "C9000012"
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No17-13.セキュリティレベル 文字列型、3桁、入力可能文字以外が含まれる
def test_transaction_multi_create_case17_13(monkeypatch, mocker: MockerFixture, create_header):
    # 標準出力をモック
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["pdsUserId"] = "C9000013"
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No17-14.セキュリティレベル 文字列型、2桁、入力可能文字のみ
def test_transaction_multi_create_case17_14(monkeypatch, mocker: MockerFixture, create_header):
    # 標準出力をモック
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["pdsUserId"] = "C9000014"
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No18.CSVファイルの内容チェック処理で失敗する
def test_transaction_multi_create_case18(monkeypatch, mocker: MockerFixture, create_header):
    # 標準出力をモック
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No20.接続に失敗する。設定値を異常な値に変更する
def test_transaction_multi_create_case20(monkeypatch, mocker: MockerFixture, create_header):
    # 標準出力をモック
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["pdsUserId"] = "C5000000"
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No22.個人情報取得処理が失敗する
def test_transaction_multi_create_case22(monkeypatch, mocker: MockerFixture, create_header):
    # 標準出力をモック
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "MULTI_CREATE_BATCH_USER_PROFILE_SELECT_SQL", """ SELECT * FROM AAAAAA; """)
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No23.個人情報取得処理の取得件数が0件以外(1件)
def test_transaction_multi_create_case23(monkeypatch, mocker: MockerFixture, create_header):
    # 標準出力をモック
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No28.個人情報登録処理実行処理が失敗する
# No30.「変数．個人情報登録処理実行結果リスト」内を検索して、処理結果がfalseのデータが存在する
# No32.Insert.csvから取得した行数が2件
# No34.個人情報バッチキュー発行処理が成功する
def test_transaction_multi_create_case28(monkeypatch, mocker: MockerFixture, create_header):
    # 標準出力をモック
    mocker.patch.object(SqlConstClass, "USER_PROFILE_BINARY_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No33.個人情報バッチキュー発行処理が失敗する
def test_transaction_multi_create_case33(monkeypatch, mocker: MockerFixture, create_header):
    # 標準出力をモック
    mocker.patch.object(SqlConstClass, "USER_PROFILE_BINARY_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    mocker.patch.object(SystemConstClass, "SQS_QUEUE_NAME", "aaaaaaa")
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No35.「個人情報更新トランザクション」を作成する
#       コネクション作成時に自動で作成されるので検証不可


# No36.個人情報更新処理が失敗する
def test_transaction_multi_create_case36(monkeypatch, mocker: MockerFixture, create_header):
    # 標準出力をモック
    mocker.patch.object(SqlConstClass, "MULTI_CREATE_BATCH_USER_PROFILE_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No39.zipファイル削除処理が失敗する
def test_transaction_multi_create_case39(monkeypatch, mocker: MockerFixture, create_header):
    # 標準出力をモック
    header = create_header["header"]
    # os.removeはBoto3内部で利用されており到達できないので対応方法検討
    # エラーの発生はzipファイル削除処理で確認するので、エラー発生時の挙動のみ確認するための対応とする
    mocker.patch.object(transactionMultiCreateBatchModelClass, "delete_zip_file", return_value={"result": False, "errorInfo": {"errorCode": "990031", "message": logUtil.message_build(MessageConstClass.ERRORS["990031"]["message"], "990031")}})
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No41.zipファイル解凍フォルダ削除処理が失敗する
def test_transaction_multi_create_case41(monkeypatch, mocker: MockerFixture, create_header):
    # 標準出力をモック
    header = create_header["header"]
    # os.removeはBoto3内部で利用されており到達できないので対応方法検討
    # エラーの発生はzipファイル削除処理で確認するので、エラー発生時の挙動のみ確認するための対応とする
    mocker.patch("shutil.rmtree").side_effect = Exception("test-exception")
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No43.S3のzipファイルダウンロード元ファイル削除処理に5回失敗する
def test_transaction_multi_create_case43(monkeypatch, mocker: MockerFixture, create_header):
    # 標準出力をモック
    header = create_header["header"]
    mocker.patch("util.s3Util.s3UtilClass.deleteFile").return_value = False
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No44.S3のzipファイルダウンロード元ファイル削除処理に4回失敗し、5回目で成功する
def test_transaction_multi_create_case44(monkeypatch, mocker: MockerFixture, create_header):
    # 標準出力をモック
    header = create_header["header"]
    mocker.patch("util.s3Util.s3UtilClass.deleteFile").side_effect = [False, False, False, False, True]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No45.S3のzipファイルダウンロード元ファイル削除処理が失敗する
def test_transaction_multi_create_case45(monkeypatch, mocker: MockerFixture, create_header):
    # 標準出力をモック
    header = create_header["header"]
    mocker.patch("util.s3Util.s3UtilClass.deleteFile").return_value = False
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No48.DataKeyとDataValueがともに空である
# No50.個人情報バイナリデータ登録処理リスト初期化処理が成功する
# No52.解凍したファイルの「ルートフォルダ\{引数．個人情報レコード．UserID}」のフォルダが存在しない場合
# No64.MongoDBトランザクション作成処理実行 「MongoDB個人情報登録トランザクション」を作成する
def test_transaction_multi_create_case48(monkeypatch, mocker: MockerFixture, create_header):
    # 標準出力をモック
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No49.DataKeyとDataValueがともに空ではない
# No51.解凍したファイルの「ルートフォルダ\{引数．個人情報レコード．UserID}」のフォルダが存在する場合
# No53.1からの連番フォルダの数が2件
# No54.バイナリデータ読込処理が成功する
# No55.Base64ハッシュ化処理が成功する
# No56.バイナリデータ情報作成処理が成功する
# No57.個人情報バイナリデータ登録処理リスト作成処理が成功する
def test_transaction_multi_create_case49(monkeypatch, mocker: MockerFixture, create_header):
    # 標準出力をモック
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No58.接続に失敗する。設定値を異常な値に変更する
def test_transaction_multi_create_case58(monkeypatch, mocker: MockerFixture, create_header):
    # 標準出力をモック
    header = create_header["header"]
    # 存在しないMongoDB接続情報を持ったPDSユーザを設定する
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["pdsUserId"] = "C5000005"
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No59.接続に成功する。プログラムが配置されたリージョンが東京リージョンaの場合
def test_transaction_multi_create_case59(monkeypatch, mocker: MockerFixture, create_header):
    # 標準出力をモック
    header = create_header["header"]
    # 存在しないMongoDB接続情報を持ったPDSユーザを設定する
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["pdsUserId"] = "C5000001"
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No60.接続に成功する。プログラムが配置されたリージョンが東京リージョンcの場合
def test_transaction_multi_create_case60(monkeypatch, mocker: MockerFixture, create_header):
    # 標準出力をモック
    header = create_header["header"]
    # 存在しないMongoDB接続情報を持ったPDSユーザを設定する
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["pdsUserId"] = "C5000002"
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No61.接続に成功する。プログラムが配置されたリージョンが大阪リージョンaの場合
def test_transaction_multi_create_case61(monkeypatch, mocker: MockerFixture, create_header):
    # 標準出力をモック
    header = create_header["header"]
    # 存在しないMongoDB接続情報を持ったPDSユーザを設定する
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["pdsUserId"] = "C5000003"
    mocker.patch.object(SystemConstClass, "REGION", {"TOKYO": "ap-northeast-3", "OSAKA": "ap-northeast-1"})
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No62.接続に成功する。プログラムが配置されたリージョンが大阪リージョンcの場合
def test_transaction_multi_create_case62(monkeypatch, mocker: MockerFixture, create_header):
    # 標準出力をモック
    header = create_header["header"]
    # 存在しないMongoDB接続情報を持ったPDSユーザを設定する
    request_body_copy = REQUEST_BODY.copy()
    request_body_copy["pdsUserId"] = "C5000004"
    mocker.patch.object(SystemConstClass, "REGION", {"TOKYO": "ap-northeast-3", "OSAKA": "ap-northeast-1"})
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No63.MongoDBトランザクション作成処理実行 「MongoDB個人情報登録トランザクション」を作成に失敗する
def test_transaction_multi_create_case63(monkeypatch, mocker: MockerFixture, create_header):
    # 標準出力をモック
    header = create_header["header"]
    # 存在しないMongoDB接続情報を持ったPDSユーザを設定する
    request_body_copy = REQUEST_BODY.copy()
    mocker.patch.object(MongoDbClass, "create_transaction", side_effect=Exception('testException'))
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No65.「変数．個人情報データ」が存在する場合
def test_transaction_multi_create_case65(monkeypatch, mocker: MockerFixture, create_header):
    # 標準出力をモック
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No66.「変数．個人情報データ」が存在しない場合
def test_transaction_multi_create_case66(monkeypatch, mocker: MockerFixture, create_header):
    # 標準出力をモック
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No67.MongoDB登録処理に失敗する
# No70.「変数．MongoDB登録実行結果．処理結果」がfalse
# No72.MongoDBロールバック処理に成功する
# No73.MongoDB登録エラー処理に成功する
def test_transaction_multi_create_case67(monkeypatch, mocker: MockerFixture, create_header):
    # 標準出力をモック
    header = create_header["header"]
    mocker.patch.object(Collection, "insert_one", side_effect=PyMongoError('testException'))
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No68.MongoDB登録処理に成功する
# No69.「変数．MongoDB登録実行結果．処理結果」がtrue
def test_transaction_multi_create_case68(monkeypatch, mocker: MockerFixture, create_header):
    # 標準出力をモック
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No71.MongoDBロールバック処理に失敗する
def test_transaction_multi_create_case71(monkeypatch, mocker: MockerFixture, create_header):
    # 標準出力をモック
    header = create_header["header"]
    mocker.patch.object(Collection, "insert_one", side_effect=PyMongoError('testException'))
    mocker.patch.object(ClientSession, "abort_transaction", side_effect=PyMongoError('testException'))
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No74.接続に失敗する 設定値を異常な値に変更する
@pytest.mark.asyncio
async def test_transaction_multi_create_case74(monkeypatch, mocker: MockerFixture, create_header, create_pds_user_db_info):
    # 標準出力をモック
    csv_header = ["TID", "UserID", "DataKey1", "DataValue1", "DataKey2", "DataValue2", "SecureLevel"]
    csv_row = {"TID": "transaction5000", "UserID": "user5000", "DataKey1": "datakey1_5000", "DataValue1": "datavalue1_5000", "DataKey2": "datakey2_5000", "DataValue2": "datavalue2_5000", "SecureLevel": "2"}
    pds_user_db_info: dict = create_pds_user_db_info
    pds_user_db_info["host"] = "aaaaaaaaaaaaa"
    request_body_copy = REQUEST_BODY.copy()
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    transaction_multi_create_batch_moodel = transactionMultiCreateBatchModelClass(trace_logger)
    with pytest.raises(PDSException) as e:
        await transaction_multi_create_batch_moodel.user_profile_insert_exec(
            transaction_id="transaction5000",
            csv_header=csv_header,
            user_profile_row=csv_row,
            kms_id=KMS_ID,
            bucket_name=BUCKET_NAME,
            pds_user_db_secret_info=pds_user_db_info,
            pds_user_info=PDS_USER_INFO_DICT,
            # PDSユーザIDの名前のフォルダを配置すること
            dir_name=request_body_copy["pdsUserId"]
        )

    assert e.value.args[0] == {
        "errorCode": "999999",
        "message": e.value.args[0]["message"]
    }
    print(e)


# No75.接続に成功する
def test_transaction_multi_create_case75(monkeypatch, mocker: MockerFixture, create_header, create_pds_user_db_info):
    # 標準出力をモック
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No76.「個人情報登録トランザクション」を作成する
#       コネクション作成時に自動で作成されるので検証不可


# No77.個人情報登録処理が失敗する
# No80.「変数．エラー情報」がNull以外
# No82.ロールバック処理が成功する
# No84.ロールバック処理が成功する
# No85.個人情報登録エラー処理が成功する
def test_transaction_multi_create_case77(monkeypatch, mocker: MockerFixture, create_header, create_pds_user_db_info):
    # 標準出力をモック
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "USER_PROFILE_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No78.個人情報登録処理が成功する
# No79.「変数．エラー情報」がNull
# No87.「MongoDB個人情報登録トランザクション」のコミット処理が成功する
# No89.「個人情報登録トランザクション」のコミット処理が成功する
def test_transaction_multi_create_case78(monkeypatch, mocker: MockerFixture, create_header, create_pds_user_db_info):
    # 標準出力をモック
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No81.ロールバック処理が失敗する
@pytest.mark.asyncio
async def test_transaction_multi_create_case81(monkeypatch, mocker: MockerFixture, create_header, create_pds_user_db_info):
    # 標準出力をモック
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "USER_PROFILE_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    mocker.patch.object(PostgresDbUtilClass, "rollback_transaction", side_effect=Exception('testException'))
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No83.Mongoロールバック処理が失敗する
@pytest.mark.asyncio
async def test_transaction_multi_create_case83(monkeypatch, mocker: MockerFixture, create_header, create_pds_user_db_info):
    # 標準出力をモック
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "USER_PROFILE_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    mocker.patch.object(ClientSession, "abort_transaction", side_effect=PyMongoError('testException'))
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No86.「MongoDB個人情報登録トランザクション」のコミット処理が失敗する
@pytest.mark.asyncio
async def test_transaction_multi_create_case86(monkeypatch, mocker: MockerFixture, create_header, create_pds_user_db_info):
    # 標準出力をモック
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    mocker.patch.object(ClientSession, "commit_transaction", side_effect=PyMongoError('testException'))
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No88.「個人情報登録トランザクション」のコミット処理が失敗する
@pytest.mark.asyncio
async def test_transaction_multi_create_case88(monkeypatch, mocker: MockerFixture, create_header, create_pds_user_db_info):
    # 標準出力をモック
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    mocker.patch.object(PostgresDbUtilClass, "commit_transaction", side_effect=Exception('testException'))
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No90.「変数．個人情報バイナリデータ登録処理リストが空の場合
@pytest.mark.asyncio
async def test_transaction_multi_create_case90(monkeypatch, mocker: MockerFixture, create_header, create_pds_user_db_info):
    # 標準出力をモック
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No91.「変数．個人情報バイナリデータ登録処理リストが空以外の場合
# No93.個人情報バイナリデータ登録処理実行処理が成功する
# No95.「変数．個人情報バイナリデータ登録処理実行結果リスト」内を検索して、処理結果がfalseのデータが存在しない
# No98.終了処理 レスポンス返却
@pytest.mark.asyncio
async def test_transaction_multi_create_case91(monkeypatch, mocker: MockerFixture, create_header, create_pds_user_db_info):
    # 標準出力をモック
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No92.個人情報バイナリデータ登録処理実行処理が失敗する
# No94.「変数．個人情報バイナリデータ登録処理実行結果リスト」内を検索して、処理結果がfalseのデータが存在する
# No96.個人情報バイナリデータ登録エラー処理が成功する
# 条件
# 変数．個人情報バイナリデータ登録処理実行結果リスト．処理結果 = false
# No97.レスポンスを返却する
@pytest.mark.asyncio
async def test_transaction_multi_create_case92(monkeypatch, mocker: MockerFixture, create_header, create_pds_user_db_info):
    # 標準出力をモック
    header = create_header["header"]
    request_body_copy = REQUEST_BODY.copy()
    mocker.patch.object(SqlConstClass, "USER_PROFILE_BINARY_UNIQUE_CHECK_SAVE_IMAGE_DATA_ID_SQL", """ SELECT * FROM AAAAAA; """)
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No99.zipファイル削除処理に5回失敗する
# No102.zipファイル削除処理が失敗する 引数．共通エラーチェックフラグがFalseの場合
# No104.終了処理 レスポンス返却
def test_transaction_multi_create_case99(monkeypatch, mocker: MockerFixture, create_header, create_pds_user_db_info):
    # 標準出力をモック
    request_body_copy = REQUEST_BODY.copy()
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    mocker.patch("os.remove").side_effect = Exception("test-exception")
    transaction_multi_create_batch_moodel = transactionMultiCreateBatchModelClass(trace_logger)
    response = transaction_multi_create_batch_moodel.delete_zip_file(
        # PDSユーザ名のファイルを配置すること
        'download/' + request_body_copy["pdsUserId"] + ".zip",
        False
    )

    assert response == {
        "result": False,
        "errorInfo": {"errorCode": "990031", "message": logUtil.message_build(MessageConstClass.ERRORS["990031"]["message"], "990031")}
    }
    print(response)


# No100.zipファイル削除処理に4回失敗し、5回目で成功する
def test_transaction_multi_create_case100(monkeypatch, mocker: MockerFixture, create_header, create_pds_user_db_info):
    # 標準出力をモック
    request_body_copy = REQUEST_BODY.copy()
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    mocker.patch("os.remove").side_effect = [Exception("test-exception"), Exception("test-exception"), Exception("test-exception"), Exception("test-exception"), os.remove('download/' + request_body_copy["pdsUserId"] + ".zip")]
    transaction_multi_create_batch_moodel = transactionMultiCreateBatchModelClass(trace_logger)
    response = transaction_multi_create_batch_moodel.delete_zip_file(
        # PDSユーザ名のファイルを配置すること
        'download/' + request_body_copy["pdsUserId"] + ".zip",
        False
    )

    assert response == {
        "result": True
    }
    print(response)


# No101.zipファイル削除処理が失敗する 引数．共通エラーチェックフラグがtrueの場合
def test_transaction_multi_create_case101(monkeypatch, mocker: MockerFixture, create_header, create_pds_user_db_info):
    # 標準出力をモック
    request_body_copy = REQUEST_BODY.copy()
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    mocker.patch("os.remove").side_effect = Exception("test-exception")
    transaction_multi_create_batch_moodel = transactionMultiCreateBatchModelClass(trace_logger)
    with pytest.raises(PDSException) as e:
        transaction_multi_create_batch_moodel.delete_zip_file(
            # PDSユーザ名のファイルを配置すること
            'download/' + request_body_copy["pdsUserId"] + ".zip",
            True
        )

    assert e.value.args[0] == {
        "errorCode": "990031",
        "message": e.value.args[0]["message"]
    }
    print(e)


# No103.zipファイル削除処理が1回目で成功する
def test_transaction_multi_create_case103(monkeypatch, mocker: MockerFixture, create_header, create_pds_user_db_info):
    # 標準出力をモック
    request_body_copy = REQUEST_BODY.copy()
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    transaction_multi_create_batch_moodel = transactionMultiCreateBatchModelClass(trace_logger)
    response = transaction_multi_create_batch_moodel.delete_zip_file(
        # PDSユーザ名のファイルを配置すること
        'download/' + request_body_copy["pdsUserId"] + ".zip",
        False
    )

    assert response == {
        "result": True
    }
    print(response)


# No105.zipファイル解凍フォルダ削除処理に5回失敗する
# No108.zipファイル解凍フォルダ削除処理が失敗する 引数．共通エラーチェックフラグがfalseの場合
# No110.終了処理 レスポンス返却
def test_transaction_multi_create_case105(monkeypatch, mocker: MockerFixture, create_header, create_pds_user_db_info):
    # 標準出力をモック
    request_body_copy = REQUEST_BODY.copy()
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    mocker.patch("shutil.rmtree").side_effect = Exception("test-exception")
    transaction_multi_create_batch_moodel = transactionMultiCreateBatchModelClass(trace_logger)
    response = transaction_multi_create_batch_moodel.delete_unzip_folder(
        # PDSユーザ名のファイルを配置すること
        'out_dir/' + request_body_copy["pdsUserId"],
        False
    )

    assert response == {
        "result": False,
        "errorInfo": {"errorCode": "990032", "message": logUtil.message_build(MessageConstClass.ERRORS["990032"]["message"], "990032")}
    }
    print(response)


# No106.zipファイル解凍フォルダ削除処理に4回失敗し、5回目で成功する
def test_transaction_multi_create_case106(monkeypatch, mocker: MockerFixture, create_header, create_pds_user_db_info):
    # 標準出力をモック
    request_body_copy = REQUEST_BODY.copy()
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    mocker.patch("shutil.rmtree").side_effect = [Exception("test-exception"), Exception("test-exception"), Exception("test-exception"), Exception("test-exception"), shutil.rmtree('out_dir/' + request_body_copy["pdsUserId"])]
    transaction_multi_create_batch_moodel = transactionMultiCreateBatchModelClass(trace_logger)
    response = transaction_multi_create_batch_moodel.delete_unzip_folder(
        # PDSユーザ名のファイルを配置すること
        'out_dir/' + request_body_copy["pdsUserId"],
        False
    )

    assert response == {
        "result": True
    }
    print(response)


# No107.zipファイル解凍フォルダ削除処理が失敗する 引数．共通エラーチェックフラグがtrueの場合
def test_transaction_multi_create_case107(monkeypatch, mocker: MockerFixture, create_header, create_pds_user_db_info):
    # 標準出力をモック
    request_body_copy = REQUEST_BODY.copy()
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    mocker.patch("shutil.rmtree").side_effect = Exception("test-exception")
    transaction_multi_create_batch_moodel = transactionMultiCreateBatchModelClass(trace_logger)
    with pytest.raises(PDSException) as e:
        transaction_multi_create_batch_moodel.delete_unzip_folder(
            # PDSユーザ名のファイルを配置すること
            'out_dir/' + request_body_copy["pdsUserId"],
            True
        )

    assert e.value.args[0] == {
        "errorCode": "990032",
        "message": e.value.args[0]["message"]
    }
    print(e)


# No109.zipファイル解凍フォルダ削除処理が1回目で成功する
def test_transaction_multi_create_case109(monkeypatch, mocker: MockerFixture, create_header, create_pds_user_db_info):
    # 標準出力をモック
    request_body_copy = REQUEST_BODY.copy()
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", Request({"type": "http", "headers": {}, "method": "post", "path": ""}))
    transaction_multi_create_batch_moodel = transactionMultiCreateBatchModelClass(trace_logger)
    response = transaction_multi_create_batch_moodel.delete_unzip_folder(
        # PDSユーザ名のファイルを配置すること
        'out_dir/' + request_body_copy["pdsUserId"],
        False
    )

    assert response == {
        "result": True
    }
    print(response)


# No111.ロールバック処理が失敗すること
def test_transaction_multi_create_case111(monkeypatch, mocker: MockerFixture, create_header, create_pds_user_db_info):
    # 標準出力をモック
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "USER_PROFILE_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    mocker.patch("util.postgresDbUtil.PostgresDbUtilClass.rollback_transaction").side_effect = Exception("test-exception")
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No112.ロールバック処理が成功すること
# No113.正常終了すること
def test_transaction_multi_create_case112(monkeypatch, mocker: MockerFixture, create_header, create_pds_user_db_info):
    # 標準出力をモック
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "USER_PROFILE_INSERT_SQL", """ SELECT * FROM AAAAAA; """)
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No114.ロールバック処理が失敗すること
def test_transaction_multi_create_case114(monkeypatch, mocker: MockerFixture, create_header, create_pds_user_db_info):
    # 標準出力をモック
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "MULTI_CREATE_BATCH_USER_PROFILE_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    mocker.patch("util.postgresDbUtil.PostgresDbUtilClass.rollback_transaction").side_effect = Exception("test-exception")
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No115.ロールバック処理が成功すること
# No116.正常終了すること
def test_transaction_multi_create_case115(monkeypatch, mocker: MockerFixture, create_header, create_pds_user_db_info):
    # 標準出力をモック
    header = create_header["header"]
    mocker.patch.object(SqlConstClass, "MULTI_CREATE_BATCH_USER_PROFILE_UPDATE_SQL", """ SELECT * FROM AAAAAA; """)
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No117.ロールバック処理が失敗すること
def test_transaction_multi_create_case117(monkeypatch, mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(Collection, "insert_one", side_effect=PyMongoError('testException'))
    mocker.patch.object(ClientSession, "abort_transaction", side_effect=PyMongoError('testException'))
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())


# No118.MongoDBロールバック処理が成功すること
# No119.正常終了すること
def test_transaction_multi_create_case118(monkeypatch, mocker: MockerFixture, create_header):
    header = create_header["header"]
    mocker.patch.object(Collection, "insert_one", side_effect=PyMongoError('testException'))
    request_body_copy = REQUEST_BODY.copy()
    response = client.post("/api/2.0/batch/transactionMultiCreateBatch", headers=header, data=json.dumps(request_body_copy))
    print(response.json())
