from logging import Logger
import util.checkUtil as checkUtil
import traceback

import util.logUtil as logUtil
## 固定値クラス
from const.messageConst import MessageConstClass

from exceptionClass.PDSException import PDSException


class CheckPdsUserPublicKeyIdx:
    """
    PDSユーザ公開鍵インデックス検証処理

    """
    def __init__(self, logger: Logger, pdsUserPublicKeyIdx: str):
        """
        パラメータ検証処理

        Args:
            logger (Logger): ロガー
            pdsUserPublicKeyIdx (str): PDSユーザ公開鍵インデックス

        Raises:
            e: 例外
            PDSException: PDSシステムエラー
        """
        self.logger = None
        self.error_info_list = []
        try:
            self.logger = logger
            # 01.PDSユーザ公開鍵インデックス検証処理
            # 01-01.「引数．PDSユーザ公開鍵インデックス」の値が設定されていない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_require(pdsUserPublicKeyIdx):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020001"]["logMessage"], "PDSユーザ公開鍵インデックス"))
                self.error_info_list.append(
                    {
                        "errorCode": "020001",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020001"]["message"], "PDSユーザ公開鍵インデックス")
                    }
                )

            # 01-02.「引数．PDSユーザ公開鍵インデックス」に値が設定されており、型が数値型ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_type(pdsUserPublicKeyIdx, int):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "PDSユーザ公開鍵インデックス", "数値"))
                self.error_info_list.append(
                    {
                        "errorCode": "020019",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "PDSユーザ公開鍵インデックス", "数値")
                    }
                )

            # 01-03.「引数．PDSユーザ公開鍵インデックス」に値が設定されており、値に入力可能文字以外が含まれている場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_pds_user_public_key_idx(pdsUserPublicKeyIdx):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020020"]["logMessage"], "PDSユーザ公開鍵インデックス"))
                self.error_info_list.append(
                    {
                        "errorCode": "020020",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020020"]["message"], "PDSユーザ公開鍵インデックス")
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
        # 02.PDSユーザ公開鍵インデックス検証チェック処理
        # 02-01.「変数．エラー情報リスト」が空の場合、「04.終了処理」に遷移する
        # 02-02.「変数．エラー情報リスト」が空以外の場合、「03.PDSユーザ公開鍵インデックス検証エラー処理」に遷移する
        if not len(self.error_info_list) == 0:
            # 03.PDSユーザ公開鍵インデックス検証エラー処理
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
