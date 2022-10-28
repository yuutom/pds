from logging import Logger
import util.checkUtil as checkUtil
import traceback

import util.logUtil as logUtil
## 固定値クラス
from const.messageConst import MessageConstClass

from exceptionClass.PDSException import PDSException


class CheckImageHashTo:
    """
    保存したいバイナリデータハッシュ値検証処理

    """
    def __init__(self, logger: Logger, imageHash, mode: int):
        """
        パラメータ検証処理

        Args:
            logger (Logger): ロガー
            imageHash (str or array): 保存したいバイナリデータハッシュ値
            mode (int): 検証モード（個人情報登録：1、個人情報更新：2）

        Raises:
            e: 例外
            PDSException: PDSシステムエラー
        """
        self.logger = None
        self.error_info_list = []
        try:
            self.logger = logger
            # 01.保存したいバイナリデータハッシュ値検証処理
            # 01-01.「引数．保存したいバイナリデータハッシュ値」に値が設定されており、型が文字列型か配列型ではない場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_type_list_image(imageHash, mode):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020019"]["logMessage"], "保存したいバイナリデータハッシュ値", "文字列,配列"))
                self.error_info_list.append(
                    {
                        "errorCode": "020019",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020019"]["message"], "保存したいバイナリデータハッシュ値", "文字列,配列")
                    }
                )

            # 01-02.「引数．保存したいバイナリデータハッシュ値」に値が設定されており、値に入力可能文字以外が含まれている場合、「変数．エラー情報リスト」にエラー情報を追加する
            if not checkUtil.check_image_hash_to(imageHash, mode):
                self.logger.warning(logUtil.message_build(MessageConstClass.ERRORS["020020"]["logMessage"], "保存したいバイナリデータハッシュ値"))
                self.error_info_list.append(
                    {
                        "errorCode": "020020",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["020020"]["message"], "保存したいバイナリデータハッシュ値")
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
        # 02.保存したいバイナリデータハッシュ値検証チェック処理
        # 02-01.「変数．エラー情報リスト」が空の場合、「04.終了処理」に遷移する
        # 02-02.「変数．エラー情報リスト」が空以外の場合、「03.保存したいバイナリデータハッシュ値検証エラー処理」に遷移する
        if not len(self.error_info_list) == 0:
            # 03.保存したいバイナリデータハッシュ値検証エラー処理
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
