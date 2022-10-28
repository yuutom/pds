from logging import Logger
import util.checkUtil as checkUtil
import traceback

import util.logUtil as logUtil
## 固定値クラス
from const.messageConst import MessageConstClass

from exceptionClass.PDSException import PDSException


class CheckAccessToken:
    """
    アクセストークン検証処理

    """
    def __init__(self, logger: Logger, accessToken: str, requireCheckFlg: bool = True):
        """
        パラメータ検証処理

        Args:
            logger (Logger): ロガー
            accessToken (str): アクセストークン
            require_check_flg (bool, optional): 必須チェックフラグ. Defaults to True.

        Raises:
            e: 例外
            PDSException: PDSシステムエラー
        """
        self.logger = None
        self.error_info_list = []
        try:
            self.logger = logger
            # 01.アクセストークン検証処理
            # 01-01.「引数．アクセストークン」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if requireCheckFlg and not checkUtil.check_require(accessToken):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "アクセストークン"))
                self.error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "アクセストークン")
                    }
                )

            # 01-02.「引数．アクセストークン」に値が設定されており、型が文字列型ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_type(accessToken, str):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "アクセストークン", "文字列"))
                self.error_info_list.append(
                    {
                        "errorCode": "020019",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "アクセストークン", "文字列")
                    }
                )

            # 01-03.「引数．アクセストークン」に値が設定されており、値の桁数が200桁ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_length(accessToken, 200):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020014"]["logMessage"], "アクセストークン", "200"))
                self.error_info_list.append(
                    {
                        "errorCode": "020014",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020014"]["message"], "アクセストークン", "200")
                    }
                )

            # 01-04.「引数．アクセストークン」に値が設定されており、値が入力規則に違反している場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_enterable_characters_access_token(accessToken):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020003"]["logMessage"], "アクセストークン"))
                self.error_info_list.append(
                    {
                        "errorCode": "020003",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020003"]["message"], "アクセストークン")
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
        # 02.アクセストークン検証チェック処理
        # 02-01.「変数．エラー情報リスト」が空の場合、「04.終了処理」に遷移する
        # 02-02.「変数．エラー情報リスト」が空以外の場合、「03.アクセストークン検証エラー処理」に遷移する
        if not len(self.error_info_list) == 0:
            # 03.アクセストークン検証エラー処理
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
