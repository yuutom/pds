# 共通処理
import boto3
from datetime import datetime
from dateutil.relativedelta import relativedelta
from logging import Logger
import traceback

# Exceptionクラス
from exceptionClass.PDSException import PDSException

# Utilクラス
import util.logUtil as logUtil
import util.checkUtil as checkUtil
from util.postgresDbUtil import PostgresDbUtilClass
from util.commonUtil import CommonUtilClass

# 定数クラス
from const.messageConst import MessageConstClass
from const.sqlConst import SqlConstClass
from const.billConst import billConstClass


class BillUtilClass:
    def __init__(self, logger):
        self.logger: Logger = logger
        self.common_util = CommonUtilClass(logger)

    def progressive_billing_exec(self, apiType: str, execStatus: bool, count: int, chargeBillList: list):
        """
        累進請求金額計算処理

        Args:
            apiType (str): API種別
            execStatus (bool): 実行ステータス
            count (int): カウント
            chargeBillList (list): 請求金額取得結果リスト
                0. 金額
                1. 料金実行回数幅From
                2. 料金実行回数幅To

        Returns:
            result: 処理結果
            progressiveBilling: 累進請求金額
        """
        error_info_list = []
        EXEC_NAME_JP = "累進請求金額計算処理"
        try:
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_IN_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            # 01.引数検証処理 (入力チェック)
            # 01-01.「引数．API種別」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(apiType):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "API種別"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "API種別")
                    }
                )
            # 01-02.「引数．実行ステータス」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(execStatus):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "実行ステータス"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "実行ステータス")
                    }
                )

            # 01-03.「引数．カウント」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(count):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "カウント"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "カウント")
                    }
                )
            if len(chargeBillList) != 0:
                # 01-04.「引数．請求金額取得結果リスト．金額」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
                if not checkUtil.check_require_tuple_int(chargeBillList, 0):
                    self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "請求金額取得結果リスト．金額"))
                    error_info_list.append(
                        {
                            "errorCode": "020001",
                            "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "請求金額取得結果リスト．金額")
                        }
                    )
                # 01-05.「引数．請求金額取得結果リスト．料金実行回数幅From」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
                if not checkUtil.check_require_tuple_int(chargeBillList, 1):
                    self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "請求金額取得結果リスト．料金実行回数幅From"))
                    error_info_list.append(
                        {
                            "errorCode": "020001",
                            "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "請求金額取得結果リスト．料金実行回数幅From")
                        }
                    )
                # 01-06.「引数．請求金額取得結果リスト．料金実行回数幅To」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
                if not checkUtil.check_require_tuple_int(chargeBillList, 2):
                    self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "請求金額取得結果リスト．料金実行回数幅To"))
                    error_info_list.append(
                        {
                            "errorCode": "020001",
                            "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "請求金額取得結果リスト．料金実行回数幅To")
                        }
                    )
            # 01-07.「変数．エラー情報リスト」に値が設定されている場合、エラー作成処理を実施する
            # 01-07-01.下記のパラメータでPDSExceptionオブジェクトを作成する
            # 01-07-02.PDSExceptionオブジェクトをエラーとしてスローする
            if len(error_info_list) != 0:
                raise PDSException(*error_info_list)
            # 02.請求金額初期化処理
            # 02-01.「変数．累進請求金額」を初期化する
            progressive_charge_bill = 0

            # 03.実行ステータスチェック処理
            # 03-01.「引数．実行ステータス」がtrueの場合、「04.料金実行回数幅チェック処理」に遷移する
            # 03-02.「引数．実行ステータス」がfalseの場合、「09.終了処理」に遷移する
            if execStatus:

                for progressive_bill_loop, chargeBillElement in enumerate(chargeBillList):
                    # 04.料金実行回数幅チェック処理
                    # 04-01.「引数．カウント」が「請求金額取得結果リスト[変数．累進金額ループ数]．料金実行回数幅To」を超過する場合、「05.累進金額回数取得処理（To超過）」に遷移する
                    # 04-02.「引数．カウント」が「請求金額取得結果リスト[変数．累進金額ループ数]．料金実行回数幅To」以下の場合、「06.累進金額回数取得処理（To以下）」に遷移する
                    if count > chargeBillElement[2]:
                        # 05.累進金額回数取得処理（To超過）
                        # 05-01.「引数．請求金額取得結果リスト」をもとに、「変数．累進金額回数」を計算して格納する
                        progressive_bill_count = chargeBillElement[2] - chargeBillElement[1]

                    if count <= chargeBillElement[2]:
                        # 06.累進金額回数取得処理（To以下）
                        # 06-01.「引数．請求金額取得結果リスト」と「引数．カウント」をもとに、「変数．累進金額回数」を計算して格納する
                        progressive_bill_count = chargeBillElement[2] - count

                    # 07.累進金額計算処理
                    # 07-01.「引数．請求金額取得結果リスト」と「変数．累進金額回数」をもとに、「変数．累進金額」を計算して格納する
                    progressive_bill = chargeBillElement[0] * progressive_bill_count

                    # 08.請求金額加算処理
                    # 08-01.「変数．累進請求金額」に「変数．累進金額」を加算する
                    progressive_charge_bill = progressive_charge_bill + progressive_bill

            # 09.終了処理
            # 09-01.レスポンス情報を作成し、返却する
            # 09-01-01.「変数．エラー情報リスト」に値が設定されていない場合、下記のレスポンス情報を返却する
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            return {
                "result": True,
                "progressiveBilling": progressive_charge_bill
            }

        # 例外処理（PDSExceptionクラス）：
        except PDSException as e:
            # PDSExceptionオブジェクトをエラーとしてスローする
            raise e
        # 例外処理：
        except Exception as e:
            # エラー情報をCloudWatchへログ出力する
            self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["999999"]["logMessage"], str(e), traceback.format_exc()))
            # 下記のパラメータでPDSExceptionオブジェクトを作成する
            # PDSExceptionオブジェクトをエラーとしてスローする
            raise PDSException(
                {
                    "errorCode": "999999",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
                }
            )

    def resource_billing_exec(self, pdsUserId: str, common_db_info: object):
        """
        リソース請求金額計算処理

        Args:
            pdsUserId (str): PDSユーザID
            common_db_info (object): 共通DB接続情報

        Returns:
            result: 処理結果
            resourceBilling: リソース請求金額
        """
        error_info_list = []
        EXEC_NAME_JP = "リソース請求金額計算処理"
        try:
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_IN_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            # 01.引数検証処理 (入力チェック)
            # 01-01.「引数．PDSユーザID」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(pdsUserId):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "PDSユーザID"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "PDSユーザID")
                    }
                )
            # 01-02.「引数．共通DB接続情報」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(common_db_info):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "共通DB接続情報"))
                error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "共通DB接続情報")
                    }
                )
            # 01-03.「変数．エラー情報リスト」に値が設定されている場合、エラー作成処理を実施する
            # 01-03-01.下記のパラメータでPDSExceptionオブジェクトを作成する
            # 01-03-02.PDSExceptionオブジェクトをエラーとしてスローする
            if len(error_info_list) != 0:
                raise PDSException(*error_info_list)

            # 共通DB接続情報
            common_db_connection_resource: PostgresDbUtilClass = None
            common_db_connection_resource = common_db_info["common_db_connection_resource"]
            common_db_connection = common_db_info["common_db_connection"]

            # 02.PDSユーザ情報取得処理
            pds_user_select_error_info = None
            # 02-01.PDSユーザテーブルからデータを取得し、「変数．PDSユーザ情報取得結果」に1レコードをタプルとして格納する
            pds_user_result = common_db_connection_resource.select_tuple_one(
                common_db_connection,
                SqlConstClass.PDS_USER_RESOURCE_BILLING_SELECT_SQL,
                pdsUserId
            )
            # 02-02.「変数．PDSユーザ取得結果」が0件の場合、「変数．エラー情報」を作成する
            if pds_user_result["result"] and pds_user_result["rowcount"] == 0:
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020004"]["logMessage"], pdsUserId))
                pds_user_select_error_info = {
                    "errorCode": "020004",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["020004"]["message"], pdsUserId)
                }
            # 02-03.処理が失敗した場合は、以下の引数でpostgresqlエラー処理を実行する
            if not pds_user_result["result"]:
                pds_user_select_error_info = self.common_util.create_postgresql_log(
                    pds_user_result["errorObject"],
                    None,
                    None,
                    pds_user_result["stackTrace"]
                ).get("errorInfo")

            # 03.共通エラーチェック処理
            # 03-01.以下の引数で共通エラーチェック処理を実行する
            # 03-02.例外が発生した場合、例外処理に遷移
            if pds_user_select_error_info is not None:
                self.common_util.common_error_check(
                    pds_user_select_error_info
                )

            # 04.PDSユーザDB接続準備処理
            # 04-01.以下の引数でPDSユーザDBの接続情報をAWSのSecrets Managerから取得する
            # 04-02.取得したPDSユーザDBの接続情報を、「変数．PDSユーザDB接続情報」に格納する
            rds_db_secret_name = pds_user_result["query_results"][0]
            pds_user_db_connection_secret_info = self.common_util.get_secret_info(rds_db_secret_name)

            # 05.CloudWatchコスト監視実行処理
            # 05-01.CloudWatchの「VolumeBytesUsed」メトリクスから、RDSストレージ量を取得する
            cloud_watch = boto3.client(
                service_name="cloudwatch"
            )

            get_metric_statistics = cloud_watch.get_metric_statistics(
                Namespace='AWS/RDS',
                MetricName='VolumeBytesUsed',
                Dimensions=[
                    {
                        'Name': 'DBClusterIdentifier',
                        'Value': pds_user_db_connection_secret_info['dbClusterIdentifier']
                    }
                ],
                StartTime=datetime.today() - relativedelta(days=1),
                EndTime=datetime.today(),
                Period=300,
                Statistics=['Average']
            )

            # 05-02.レスポンスからストレージ容量を取得して、「変数．RDSストレージ容量」に格納する
            RDS_storage_volume = get_metric_statistics['Datapoints'][0]['Average']

            # 06.金額取得処理
            # 06-01.「変数．RDSストレージ容量」をもとに、「変数．金額」を計算して格納する
            if RDS_storage_volume > billConstClass.THRESHOLD['standard01']:
                bill = billConstClass.BILL['charge01']
            else:
                bill = billConstClass.BILL['charge02']

            # 07.終了処理
            # 07-01.レスポンス情報を作成し、返却する
            # 07-01-01.「変数．エラー情報リスト」に値が設定されていない場合、下記のレスポンス情報を返却する
            self.logger.info(logUtil.message_build(MessageConstClass.TRC_OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP))
            return {
                "result": True,
                "resourceBilling": bill
            }

        # 例外処理（PDSExceptionクラス）：
        except PDSException as e:
            # PDSExceptionオブジェクトをエラーとしてスローする
            raise e
        # 例外処理：
        except Exception as e:
            # エラー情報をCloudWatchへログ出力する
            self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["999999"]["logMessage"], str(e), traceback.format_exc()))
            # 下記のパラメータでPDSExceptionオブジェクトを作成する
            # PDSExceptionオブジェクトをエラーとしてスローする
            raise PDSException(
                {
                    "errorCode": "999999",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
                }
            )
