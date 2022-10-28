from fastapi.testclient import TestClient
from app import app
from pytest_mock.plugin import MockerFixture
import tests.lambdas.healthCheck as healthCheck


client = TestClient(app)
EXEC_NAME: str = "health_check"


def test_case():
    response = healthCheck.lambda_handler(None, None)
    assert response is None


# 01.共通DB接続準備処理
# No01.接続に失敗する
#      設定値を異常な値に変更する
def test_health_check_case1(mocker: MockerFixture):
    healthCheck.lambda_handler(None, None)


# No02.接続に成功する
def test_health_check_case2(mocker: MockerFixture):
    healthCheck.lambda_handler(None, None)


# 02.URL取得処理
# No03.URL取得処理に失敗する（東京）
def test_health_check_case3(mocker: MockerFixture):
    mocker.patch("tests.lambdas.healthCheck.get_parameters").return_value = "test_url"
    healthCheck.lambda_handler(None, None)


# No04.URL取得処理に成功する（東京）
def test_health_check_case4():
    healthCheck.lambda_handler(None, None)


# No05.URL取得処理に失敗する（大阪）
def test_health_check_case5(mocker: MockerFixture):
    mocker.patch("tests.lambdas.healthCheck.get_parameters").return_value = "test_url"
    healthCheck.lambda_handler(None, None)


# No06.URL取得処理に成功する（大阪）
def test_health_check_case6():
    healthCheck.lambda_handler(None, None)


# 03. ヘルスチェックAPI実行処理
# No07.ヘルスチェックAPI実行処理 (ヘルスチェックAPI（東京）)が失敗する
def test_health_check_case7(mocker: MockerFixture):
    mocker.patch("tests.lambdas.healthCheck.exec_health_check_api").side_effect = Exception('testException')
    healthCheck.lambda_handler(None, None)


# No08.ヘルスチェックAPI実行処理 (ヘルスチェックAPI（東京）)が成功する
def test_health_check_case8():
    healthCheck.lambda_handler(None, None)


# 04. ヘルスチェックAPI実行処理
# No09.ヘルスチェックAPI実行処理(ヘルスチェックAPI（大阪）)が失敗する
def test_health_check_case9(mocker: MockerFixture):
    mocker.patch("tests.lambdas.healthCheck.exec_health_check_api").side_effect = Exception('testException')
    healthCheck.lambda_handler(None, None)


# No10.ヘルスチェックAPI実行処理 (ヘルスチェックAPI（大阪）)が成功する
def test_health_check_case10():
    healthCheck.lambda_handler(None, None)


# 05.終了処理
# No11.エラー情報がない
def test_health_check_case11():
    healthCheck.lambda_handler(None, None)


# ヘルスチェックAPI実行処理
# 01. ヘルスチェックAPI呼び出し処理
# No12.ヘルスチェックAPI呼び出し処理に失敗する(※URLが不正)
def test_health_check_case12(mocker: MockerFixture):
    mocker.patch("tests.lambdas.healthCheck.get_parameters").return_value = "test_url"
    healthCheck.lambda_handler(None, None)


# No13.ヘルスチェックAPI呼び出し処理に成功する(HTTPステータスコードが200)
def test_health_check_case13():
    healthCheck.lambda_handler(None, None)


# No14.ヘルスチェックAPI呼び出し処理に成功する(HTTPステータスコードが500)
def test_health_check_case14(mocker: MockerFixture):
    mocker.patch("requests.get").return_value = "500"
    healthCheck.lambda_handler(None, None)


# No15.ヘルスチェックAPI呼び出し処理に成功する(HTTPステータスコードが500)
def test_health_check_case15(mocker: MockerFixture):
    mocker.patch("requests.get").return_value = "500"
    healthCheck.lambda_handler(None, None)


# 05. ヘルスチェック実行履歴登録処理
# No16.ヘルスチェック実行履歴登録処理が失敗すること
def test_health_check_case16(mocker: MockerFixture):
    mocker.patch("tests.lambdas.healthCheck.insert_exec").return_value = {
        "result": False,
        "errorObject": Exception("test-exception"),
        "stackTrace": "test-trace"
    }
    healthCheck.lambda_handler(None, None)


# No17.ヘルスチェック実行履歴登録処理が成功すること
def test_health_check_case17():
    healthCheck.lambda_handler(None, None)


# ヘルスチェック実行履歴登録処理
# 01.共通DB接続準備処理
# No18.接続に失敗する(設定値を異常な値に変更する)
def test_health_check_case18(mocker: MockerFixture):
    mocker.patch("psycopg2.connect").return_value = {"host": "test", "port": "test", "username": "test", "password": "test"}
    healthCheck.lambda_handler(None, None)


# No19.接続に成功する
def test_health_check_case19():
    healthCheck.lambda_handler(None, None)


# 02.トランザクション作成処理
# No20.トランザクションが作成される
def test_health_check_case20():
    healthCheck.lambda_handler(None, None)


# 03.ヘルスチェック実行履歴登録処理
# 04.共通エラーチェック処理
# No21.ヘルスチェック実行履歴登録処理が失敗する
def test_health_check_case21(mocker: MockerFixture):
    mocker.patch("tests.lambdas.healthCheck.insert_exec").return_value = {
        "result": False,
        "errorObject": Exception("test-exception"),
        "stackTrace": "test-trace"
    }
    healthCheck.lambda_handler(None, None)


# No22.ヘルスチェック実行履歴登録処理が成功する
def test_health_check_case22():
    healthCheck.lambda_handler(None, None)


# 05.終了処理
# No23.エラー情報がない
def test_health_check_case23():
    healthCheck.lambda_handler(None, None)


# 02.ロールバック処理
# No24.ロールバック処理が失敗すること
def test_health_check_case24(mocker: MockerFixture):
    mocker.patch("tests.lambdas.healthCheck.insert_exec").return_value = {
        "result": False,
        "errorObject": Exception("test-exception"),
        "stackTrace": "test-trace"
    }
    healthCheck.lambda_handler(None, None)


# No25.ロールバック処理が成功すること
def test_health_check_case25(mocker: MockerFixture):
    mocker.patch("tests.lambdas.healthCheck.insert_exec").return_value = {
        "result": False,
        "errorObject": Exception("test-exception"),
        "stackTrace": "test-trace"
    }
    healthCheck.lambda_handler(None, None)
