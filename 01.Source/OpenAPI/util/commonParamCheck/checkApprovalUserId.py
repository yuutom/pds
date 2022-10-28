from logging import Logger
import util.checkUtil as checkUtil
import traceback

import util.logUtil as logUtil
## 固定値クラス
from const.messageConst import MessageConstClass

from exceptionClass.PDSException import PDSException


class CheckApprovalUserId:
    """
    承認TFオペレータID検証処理

    """
    def __init__(self, logger: Logger, approvalUserId: str):
        """
        パラメータ検証処理

        Args:
            logger (Logger): ロガー
            approvalUserId (str): 承認TFオペレータID

        Raises:
            e: 例外
            PDSException: PDSシステムエラー
        """
        self.logger = None
        self.error_info_list = []
        try:
            self.logger = logger
            # 01.承認TFオペレータID検証処理
            # 01-01.「引数．承認TFオペレータID」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(approvalUserId):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "承認TFオペレータID"))
                self.error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "承認TFオペレータID")
                    }
                )

            # 01-02.「引数．承認TFオペレータID」に値が設定されており、型が文字列型ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_type(approvalUserId, str):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "承認TFオペレータID", "文字列"))
                self.error_info_list.append(
                    {
                        "errorCode": "020019",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "承認TFオペレータID", "文字列")
                    }
                )

            # 01-03.「引数．承認TFオペレータID」に値が設定されており、値の桁数が3桁未満の場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_min_length(approvalUserId, 3):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020016"]["logMessage"], "承認TFオペレータID", "3"))
                self.error_info_list.append(
                    {
                        "errorCode": "020016",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020016"]["message"], "承認TFオペレータID", "3")
                    }
                )

            # 01-04.「引数．承認TFオペレータID」に値が設定されており、値の桁数が16桁を超過する場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_max_length(approvalUserId, 16):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020002"]["logMessage"], "承認TFオペレータID", "16"))
                self.error_info_list.append(
                    {
                        "errorCode": "020002",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020002"]["message"], "承認TFオペレータID", "16")
                    }
                )
            # 01-05.「引数．承認TFオペレータID」に値が設定されており、値に入力可能文字以外が含まれている場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_tf_operator_id(approvalUserId):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020020"]["logMessage"], "承認TFオペレータID"))
                self.error_info_list.append(
                    {
                        "errorCode": "020020",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020020"]["message"], "承認TFオペレータID")
                    }
                )

        # 例外処理(PDSException)
        except PDSException as e:
            raise e

        # 例外処理
        except Exception as e:
            self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["999999"]["logMessage"], str(e), traceback.format_exc()))
            raise PDSException(
                {
                    "errorCode": "999999",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["999999"]["message"], "999999")
                }
            )

    def get_result(self) -> dict:
        """
        パラメータ検証結果取得処理

        Returns:
            dict: 処理結果
        """
        # 02.承認TFオペレータID検証チェック処理
        # 02-01.「変数．エラー情報リスト」が空の場合、「04.終了処理」に遷移する
        # 02-02.「変数．エラー情報リスト」が空以外の場合、「03.承認TFオペレータID検証エラー処理」に遷移する
        if not len(self.error_info_list) == 0:
            # 03.承認TFオペレータID検証エラー処理
            # 03-01.レスポンス情報整形処理
            # 03-01-01.以下をレスポンスとして返却する
            # 03-02.処理を終了する
            return {
                "result": False,
                "errorInfo": self.error_info_list
            }
        else:
            # 04.終了処理
            # 04-01.レスポンス情報整形処理
            # 04-01-01.以下をレスポンスとして返却する
            # 04-02.処理を終了する
            return {
                "result": True
            }