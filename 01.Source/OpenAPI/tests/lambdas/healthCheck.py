import json
import boto3
import requests
import logging
import re
import psycopg2
from datetime import datetime, timedelta
import traceback
from exceptionClass.PDSException import PDSException


REGION = "ap-northeast-1"


def lambda_handler(event, context):
    """
    メイン処理

    Args:
        event (object): イベントオブジェクト
        context (object): コンテキストオブジェクト

    """
    # ロガー作成
    logger = logging.getLogger()

    try:
        # 01.共通DB接続準備処理
        session = boto3.session.Session(
            aws_access_key_id="AKIA4MTGFKNZVSWNZP7R",
            aws_secret_access_key="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"
        )
        client = session.client(
            service_name="secretsmanager",
            region_name=REGION
        )
        # 01-01.共通DB接続情報取得処理
        common_db_secret_info = client.get_secret_value(SecretId="pds-common-sm")
        common_db_secret_info = json.loads(common_db_secret_info["SecretString"])

        # 02.URL取得処理
        # 02-01.Parameter StoreにhealthCheckUrlNorthEast1(ヘルスチェックURL東京用キー名)で問い合わせ
        health_check_tokyo_api_url = get_parameters(logger, "healthCheckUrlNorthEast1")
        # 02-02.Parameter StoreにhealthCheckUrlNorthEast3(ヘルスチェックURL大阪用キー名)で問い合わせ
        health_check_osaka_api_url = get_parameters(logger, "healthCheckUrlNorthEast3")

        # 03.ヘルスチェックAPI実行処理 (ヘルスチェックAPI（東京）)
        exec_health_check_api(logger, health_check_tokyo_api_url, "ap-northeast-1", common_db_secret_info)

        # 04.ヘルスチェックAPI実行処理(ヘルスチェックAPI（大阪）)
        exec_health_check_api(logger, health_check_osaka_api_url, "ap-northeast-3", common_db_secret_info)

        # 05.終了処理
        # 05-01.正常終了をCloudWatchへのログ出力する
        logger.info('Code:[000000] Message:[処理が正常終了しました。]')

    # 例外処理(PDSException)
    except PDSException as e:
        pass

    # 例外処理
    except Exception as e:
        logger.error('Code:[999999] Message:[想定外のエラーが発生しました。]')


def get_parameters(logger, param_key):
    """
    URL取得処理

    Args:
        param_key (str): パラメーターキー

    Returns:
        str: URL
    """
    try:
        ssm = boto3.client('ssm', region_name="ap-northeast-1")
        response = ssm.get_parameters(
            Names=[
                param_key,
            ],
            WithDecryption=True
        )
        return response['Parameters'][0]['Value']

    # 例外処理(PDSException)
    except PDSException as e:
        raise e

    # 例外処理
    except Exception as e:
        logger.error('Code:[999999] Message:[想定外のエラーが発生しました。]')
        raise PDSException(
            {
                "errorCode": "999999",
                "messag": "予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：999999）"
            }
        )


def exec_health_check_api(logger, api_url, region, common_db_secret_info):
    """
    ヘルスチェックAPI実行処理

    Args:
        logger (Logger): ロガー
        api_url (str): APIのURL
        region (str): リージョン名
        common_db_secret_info (dict): DB接続情報
    """
    try:
        # 01.ヘルスチェックAPI呼び出し処理
        # 01-01.「引数．ヘルスチェックAPIURL」のAPIを実行する
        # 01-02.ヘルスチェックAPIからのレスポンスを、「変数．ヘルスチェックAPI実行結果」に格納する
        health_check_api_exec_result = requests.get(api_url)
        status_code = re.search('[0-9]+', str(health_check_api_exec_result)).group()

        # 02.実行ステータス決定処理
        # 02-01.「変数．ヘルスチェックAPI実行結果．HTTPステータスコード」が200の場合、「変数．実行ステータス」にtrueを格納する
        if status_code == '200':
            exec_status = True
        # 02-02.「変数．ヘルスチェックAPI実行結果．HTTPステータスコード」が500の場合、「変数．実行ステータス」にfalseを格納する
        if status_code == '500' or status_code == '403':
            exec_status = False

        # 03.実行ステータス決定チェック処理
        # 03-01.「変数．ヘルスチェックAPI実行結果．HTTPステータスコード」が500の場合、「04. 実行ステータス決定エラー出力処理」に遷移する
        # 03-02.「変数．ヘルスチェックAPI実行結果．HTTPステータスコード」が200の場合、「05. ヘルスチェック実行履歴登録処理」に遷移する
        if not exec_status:

            # 04.実行ステータス決定エラー出力処理
            logger.error('Code:[999999] Message:[想定外のエラーが発生しました。]')
 
        # 05.ヘルスチェック実行履歴登録処理
        exec_datetime = str(datetime.utcnow() + timedelta(hours=9)).replace("-", "/")[:23]
        # 05-01.以下の引数でヘルスチェック実行履歴登録処理を呼び出す
        register_health_check_history(logger, region, exec_datetime, exec_status, common_db_secret_info)

    # 例外処理(PDSException)
    except PDSException as e:
        raise e

    # 例外処理
    except Exception as e:
        logger.error('Code:[999999] Message:[想定外のエラーが発生しました。]')
        raise PDSException(
            {
                "errorCode": "999999",
                "messag": "予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：999999）"
            }
        )


def register_health_check_history(logger, region, exec_datetime, exec_status, common_db_secret_info):
    """
    ヘルスチェック実行履歴登録処理

    Args:
        logger (Logger): ロガー
        region (str): リージョン名
        exec_datetime (str): 実行日時
        exec_status (bool): 実行ステータス
        common_db_secret_info (dict): DB接続情報
    """
    try:
        # 01.「引数．共通DB接続情報」を利用して、共通DBに対してのコネクションを作成する
        # 02.トランザクション作成処理
        health_check_history_register_transaction = psycopg2.connect(
            host=common_db_secret_info["host"],
            port=common_db_secret_info["port"],
            database="pds_common_db",
            user=common_db_secret_info["username"],
            password=common_db_secret_info["password"]
        )

        # 03.ヘルスチェック実行履歴登録処理
        if region == "ap-northeast-1":
            region_code = "1"
        if region == "ap-northeast-3":
            region_code = "2"
        # 03-01.ヘルスチェック実行履歴テーブルに以下の情報を登録する
        insert_exec_result = insert_exec(health_check_history_register_transaction, region_code, exec_datetime, exec_status)
        # 03-02.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
        insert_exec_error_info = None
        if not insert_exec_result["result"]:
            insert_exec_error_info = create_postgresql_log(
                insert_exec_result["errorObject"],
                None,
                None,
                insert_exec_result["stackTrace"]
            ).get("errorInfo")

        # 04.共通エラーチェック処理
        # 04-01.共通エラーチェック処理を実行する
        # 04-02.例外が発生した場合、例外処理に遷移
        if insert_exec_error_info is not None:
            health_check_history_register_transaction.rollback()
            raise PDSException(insert_exec_error_info)

        # 05.終了処理
        health_check_history_register_transaction.commit()

    # 例外処理(PDSException)
    except PDSException as e:
        raise e

    # 例外処理
    except Exception as e:
        logger.error('Code:[999999] Message:[想定外のエラーが発生しました。]')
        raise PDSException(
            {
                "errorCode": "999999",
                "messag": "予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：999999）"
            }
        )


# ヘルスチェック実行履歴登録処理
def insert_exec(conn, region_code, exec_datetime, exec_status):
    """
    ヘルスチェック実行履歴登録処理

    Args:
        conn (Object): DBコネクションオブジェクト
        region_code (str): リージョン名
        exec_datetime (str): 実行日時
        exec_status (bool): 実行ステータス

    Returns:
        dict: 処理結果
    """
    try:
        SQL = "INSERT INTO t_health_check_history (region, exec_datetime, exec_status) VALUES (%s, %s, %s)"
        cur = conn.cursor()
        cur.execute(SQL, (region_code, exec_datetime, exec_status))
        cur.close()
        return {
            "result": True
        }
    except psycopg2.Error as e:
        return {
            "result": False,
            "errorObject": e,
            "stackTrace": traceback.format_exc()
        }
    except Exception as e:
        return {
            "result": False,
            "errorObject": e,
            "stackTrace": traceback.format_exc()
        }


def create_postgresql_log(e, param: str, value: str, stackTrace: str):
    """
    postgresqlエラー処理

    Args:
        e (Object): 例外オブジェクト
        param (str): パラメータ名
        value (str): パラメータ値
        stackTrace (str): スタックトレース

    Returns:
        dict: エラー情報
    """
    logger = logging.getLogger()
    # 01.postgresql例外処理
    error_info = None
    # 01-01.引数．例外オブジェクト．エラーコードの前2桁で判定し、変数．エラー情報を作成し、エラーログをCloudWatchにログ出力する
    if isinstance(e, psycopg2.Error):
        # PostgreSQL由来のエラーの場合のみ、pgcodeが取得可能
        if e.pgcode[0:2] == "03":
            error_info = {
                "errorCode": "991001",
                "message": message_build("予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：%0）", "991001")
            }
            logger.error(message_build("Code:[991001] Message:[PostgreSQLのSQL文の未完了エラーが発生しました。(code %0 message %1)]", e.pgcode, e.pgerror))
        elif e.pgcode[0:2] == "08":
            error_info = {
                "errorCode": "991002",
                "message": message_build("予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：%0）", "991002")
            }
            logger.error(message_build("Code:[991002] Message:[PostgreSQLの接続の例外エラーが発生しました。(code %0 message %1)]", e.pgcode, e.pgerror))
        elif e.pgcode[0:2] == "09":
            error_info = {
                "errorCode": "991003",
                "message": message_build("予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：%0）", "991003")
            }
            logger.error(message_build("Code:[991003] Message:[PostgreSQLのトリガによるアクションの例外エラーが発生しました。(code %0 message %1)]", e.pgcode, e.pgerror))
        elif e.pgcode[0:2] == "0A":
            error_info = {
                "errorCode": "991004",
                "message": message_build("予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：%0）", "991004")
            }
            logger.error(message_build("Code:[991004] Message:[PostgreSQLのサポートされない機能エラーが発生しました。(code %0 message %1)]", e.pgcode, e.pgerror))
        elif e.pgcode[0:2] == "0B":
            error_info = {
                "errorCode": "991005",
                "message": message_build("予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：%0）", "991005")
            }
            logger.error(message_build("Code:[991005] Message:[PostgreSQLの無効なトランザクションの初期エラーが発生しました。(code %0 message %1)]", e.pgcode, e.pgerror))
        elif e.pgcode[0:2] == "0F":
            error_info = {
                "errorCode": "991006",
                "message": message_build("予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：%0）", "991006")
            }
            logger.error(message_build("Code:[991006] Message:[PostgreSQLのロケータの例外エラーが発生しました。(code %0 message %1)]", e.pgcode, e.pgerror))
        elif e.pgcode[0:2] == "0L":
            error_info = {
                "errorCode": "991007",
                "message": message_build("予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：%0）", "991007")
            }
            logger.error(message_build("Code:[991007] Message:[PostgreSQLの無効な権限付与エラーが発生しました。(code %0 message %1)]", e.pgcode, e.pgerror))
        elif e.pgcode[0:2] == "0P":
            error_info = {
                "errorCode": "991008",
                "message": message_build("予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：%0）", "991008")
            }
            logger.error(message_build("Code:[991008] Message:[PostgreSQLの無効なロールの指定エラーが発生しました。(code %0 message %1)]", e.pgcode, e.pgerror))
        elif e.pgcode[0:2] == "20":
            error_info = {
                "errorCode": "991009",
                "message": message_build("予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：%0）", "991009")
            }
            logger.error(message_build("Code:[991009] Message:[PostgreSQLのCaseが存在しないエラーが発生しました。(code %0 message %1)]", e.pgcode, e.pgerror))
        elif e.pgcode[0:2] == "21":
            error_info = {
                "errorCode": "991010",
                "message": message_build("予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：%0）", "991010")
            }
            logger.error(message_build("Code:[991010] Message:[PostgreSQLの次数違反エラーが発生しました。(code %0 message %1)]", e.pgcode, e.pgerror))
        elif e.pgcode[0:2] == "22":
            error_info = {
                "errorCode": "991011",
                "message": message_build("予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：%0）", "991011")
            }
            logger.error(message_build("Code:[991011] Message:[PostgreSQLのデータ例外エラーが発生しました。(code %0 message %1)]", e.pgcode, e.pgerror))
        elif e.pgcode[0:2] == "23":
            if e.pgcode == "23505":
                error_info = {
                    "errorCode": "030001",
                    "message": message_build("データベースへの登録実行に失敗しました。%0：%1は既に登録されています。", param, value)
                }
                logger.warn(message_build("Code:[030001] Message:[データベースへの登録実行に失敗しました。%0：%1は既に登録されています。]", param, value))
            else:
                error_info = {
                    "errorCode": "991012",
                    "message": message_build("予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：%0）", "991012")
                }
                logger.error(message_build("Code:[991012] Message:[PostgreSQLの整合性制約違反エラーが発生しました。(code %0 message %1)]", e.pgcode, e.pgerror))
        elif e.pgcode[0:2] == "24":
            error_info = {
                "errorCode": "991013",
                "message": message_build("予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：%0）", "991013")
            }
            logger.error(message_build("Code:[991013] Message:[PostgreSQLの無効なカーソル状態エラーが発生しました。(code %0 message %1)]", e.pgcode, e.pgerror))
        elif e.pgcode[0:2] == "25":
            error_info = {
                "errorCode": "991014",
                "message": message_build("予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：%0）", "991014")
            }
            logger.error(message_build("Code:[991014] Message:[PostgreSQLの無効なトランザクション状態エラーが発生しました。(code %0 message %1)]", e.pgcode, e.pgerror))
        elif e.pgcode[0:2] == "26":
            error_info = {
                "errorCode": "991015",
                "message": message_build("予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：%0）", "991015")
            }
            logger.error(message_build("Code:[991015] Message:[PostgreSQLの無効なSQL文の名前エラーが発生しました。(code %0 message %1)]", e.pgcode, e.pgerror))
        elif e.pgcode[0:2] == "27":
            error_info = {
                "errorCode": "991016",
                "message": message_build("予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：%0）", "991016")
            }
            logger.error(message_build("Code:[991016] Message:[PostgreSQLのトリガによるデータ変更違反エラーが発生しました。(code %0 message %1)]", e.pgcode, e.pgerror))
        elif e.pgcode[0:2] == "28":
            error_info = {
                "errorCode": "991017",
                "message": message_build("予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：%0）", "991017")
            }
            logger.error(message_build("Code:[991017] Message:[PostgreSQLの無効な認証指定エラーが発生しました。(code %0 message %1)]", e.pgcode, e.pgerror))
        elif e.pgcode[0:2] == "2B":
            error_info = {
                "errorCode": "991018",
                "message": message_build("予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：%0）", "991018")
            }
            logger.error(message_build("Code:[991018] Message:[PostgreSQLの依存する権限記述子がまだ存在するエラーが発生しました。(code %0 message %1)]", e.pgcode, e.pgerror))
        elif e.pgcode[0:2] == "2D":
            error_info = {
                "errorCode": "991019",
                "message": message_build("予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：%0）", "991019")
            }
            logger.error(message_build("Code:[991019] Message:[PostgreSQLの無効なトランザクションの終了エラーが発生しました。(code %0 message %1)]", e.pgcode, e.pgerror))
        elif e.pgcode[0:2] == "2F":
            error_info = {
                "errorCode": "991020",
                "message": message_build("予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：%0）", "991020")
            }
            logger.error(message_build("Code:[991020] Message:[PostgreSQLのSQL関数例外エラーが発生しました。(code %0 message %1)]", e.pgcode, e.pgerror))
        elif e.pgcode[0:2] == "34":
            error_info = {
                "errorCode": "991021",
                "message": message_build("予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：%0）", "991021")
            }
            logger.error(message_build("Code:[991021] Message:[PostgreSQLの無効なカーソル名称エラーが発生しました。(code %0 message %1)]", e.pgcode, e.pgerror))
        elif e.pgcode[0:2] == "38":
            error_info = {
                "errorCode": "991022",
                "message": message_build("予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：%0）", "991022")
            }
            logger.error(message_build("Code:[991022] Message:[PostgreSQLの外部関数例外エラーが発生しました。(code %0 message %1)]", e.pgcode, e.pgerror))
        elif e.pgcode[0:2] == "39":
            error_info = {
                "errorCode": "991023",
                "message": message_build("予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：%0）", "991023")
            }
            logger.error(message_build("Code:[991023] Message:[PostgreSQLの外部関数呼び出し例外エラーが発生しました。(code %0 message %1)]", e.pgcode, e.pgerror))
        elif e.pgcode[0:2] == "3B":
            error_info = {
                "errorCode": "991024",
                "message": message_build("予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：%0）", "991024")
            }
            logger.error(message_build("Code:[991024] Message:[PostgreSQLのセーブポイント例外エラーが発生しました。(code %0 message %1)]", e.pgcode, e.pgerror))
        elif e.pgcode[0:2] == "3D":
            error_info = {
                "errorCode": "991025",
                "message": message_build("予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：%0）", "991025")
            }
            logger.error(message_build("Code:[991025] Message:[PostgreSQLの無効なカタログ名称エラーが発生しました。(code %0 message %1)]", e.pgcode, e.pgerror))
        elif e.pgcode[0:2] == "3F":
            error_info = {
                "errorCode": "991026",
                "message": message_build("予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：%0）", "991026")
            }
            logger.error(message_build("Code:[991026] Message:[PostgreSQLの無効なスキーマ名称エラーが発生しました。(code %0 message %1)]", e.pgcode, e.pgerror))
        elif e.pgcode[0:2] == "40":
            error_info = {
                "errorCode": "991027",
                "message": message_build("予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：%0）", "991027")
            }
            logger.error(message_build("Code:[991027] Message:[PostgreSQLのトランザクションロールバックエラーが発生しました。(code %0 message %1)]", e.pgcode, e.pgerror))
        elif e.pgcode[0:2] == "42":
            error_info = {
                "errorCode": "991028",
                "message": message_build("予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：%0）", "991028")
            }
            logger.error(message_build("Code:[991028] Message:[PostgreSQLの構文エラー、もしくはアクセスロール違反エラーが発生しました。(code %0 message %1)]", e.pgcode, e.pgerror))
        elif e.pgcode[0:2] == "44":
            error_info = {
                "errorCode": "991029",
                "message": message_build("予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：%0）", "991029")
            }
            logger.error(message_build("Code:[991029] Message:[PostgreSQLの検査オプションに伴う違反エラーが発生しました。(code %0 message %1)]", e.pgcode, e.pgerror))
        elif e.pgcode[0:2] == "53":
            error_info = {
                "errorCode": "991030",
                "message": message_build("予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：%0）", "991030")
            }
            logger.error(message_build("Code:[991030] Message:[PostgreSQLのリソース不足エラーが発生しました。(code %0 message %1)]", e.pgcode, e.pgerror))
        elif e.pgcode[0:2] == "54":
            error_info = {
                "errorCode": "991031",
                "message": message_build("予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：%0）", "991031")
            }
            logger.error(message_build("Code:[991031] Message:[PostgreSQLのプログラム制限の超過エラーが発生しました。(code %0 message %1)]", e.pgcode, e.pgerror))
        elif e.pgcode[0:2] == "55":
            error_info = {
                "errorCode": "991032",
                "message": message_build("予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：%0）", "991032")
            }
            logger.error(message_build("Code:[991032] Message:[PostgreSQLの必要条件を満たさないオブジェクトエラーが発生しました。(code %0 message %1)]", e.pgcode, e.pgerror))
        elif e.pgcode[0:2] == "57":
            if e.pgcode == "57014":
                error_info = {
                    "errorCode": "991101",
                    "message": message_build("予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：%0）", "991101")
                }
                logger.warn(message_build("Code:[991101] Message:[PostgreSQLのタイムアウトエラーが発生しました。(code %0 message %1)]", param, value))
            else:
                error_info = {
                    "errorCode": "991033",
                    "message": message_build("予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：%0）", "991033")
                }
                logger.error(message_build("Code:[991033] Message:[PostgreSQLの操作の介入エラーが発生しました。(code %0 message %1)]", e.pgcode, e.pgerror))
        elif e.pgcode[0:2] == "58":
            error_info = {
                "errorCode": "991034",
                "message": message_build("予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：%0）", "991034")
            }
            logger.error(message_build("Code:[991034] Message:[PostgreSQLのシステムエラー（外部原因によるPostgreSQL自体のエラー）が発生しました。(code %0 message %1)]", e.pgcode, e.pgerror))
        elif e.pgcode[0:2] == "F0":
            error_info = {
                "errorCode": "991035",
                "message": message_build("予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：%0）", "991035")
            }
            logger.error(message_build("Code:[991935] Message:[PostgreSQLの設定ファイルエラーが発生しました。(code %0 message %1)]", e.pgcode, e.pgerror))
        elif e.pgcode[0:2] == "P0":
            error_info = {
                "errorCode": "991036",
                "message": message_build("予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：%0）", "991036")
            }
            logger.error(message_build("Code:[991036] Message:[PostgreSQLのPL/pgSQLエラーが発生しました。(code %0 message %1)]", e.pgcode, e.pgerror))
        elif e.pgcode[0:2] == "XX":
            error_info = {
                "errorCode": "991037",
                "message": message_build("予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：%0）", "991037")
            }
            logger.error(message_build("Code:[991037] Message:[PostgreSQLの内部エラーが発生しました。(code %0 message %1)]", e.pgcode, e.pgerror))
        else:
            error_info = {
                "errorCode": "999999",
                "message": message_build("予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：%0）", "999999")
            }
            logger.error(message_build("Code:[999999] Message:[想定外のエラーが発生しました。(%0)]  StackTrace:[%1]", str(e), stackTrace))
    else:
        error_info = {
            "errorCode": "999999",
            "message": message_build("予期せぬエラーが発生しました。システム管理者へご連絡ください（エラーコード：%0）", "999999")
        }
        logger.error(message_build("Code:[999999] Message:[想定外のエラーが発生しました。(%0)]  StackTrace:[%1]", str(e), stackTrace))

    # 02.終了処理
    # 02-01.レスポンス情報を作成し、返却する
    return {"errorInfo": error_info}


def message_build(message: str, *args):
    """
    メッセージ作成処理

    Args:
        message (str): メッセージ
        args: 置換パラメータ

    Returns:
        str: メッセージ
    """
    if args:
        for index, item in enumerate(args):
            str_index = str(index)
            message = message.replace(f"%{str_index}", item)
    return message