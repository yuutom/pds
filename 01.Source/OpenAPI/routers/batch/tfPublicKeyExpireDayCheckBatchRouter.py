import traceback
import json
# FastApi
from fastapi import APIRouter, Request
# Security
from fastapi.security import OAuth2PasswordBearer
# 自作クラス
## 業務ロジッククラス
from models.batch.tfPublicKeyExpireDayCheckBatchModel import tfPublicKeyExpireDayCheckBatchModelClass
## utilクラス
import util.logUtil as logUtil
## 固定値クラス
from const.messageConst import MessageConstClass
from const.systemConst import SystemConstClass
# Exception
from exceptionClass.PDSException import PDSException

# Bearerトークン設定
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="bearerToken")

# 処理名
EXEC_NAME: str = "tfPublicKeyExpireDayCheckBatch"
EXEC_NAME_JP: str = "TF公開鍵有効期限確認バッチ"

# ルータ作成
router = APIRouter()


# 検索用 水野担当ファイル
# TF公開鍵有効期限確認バッチ
@router.post("/api/2.0/batch/tfPublicKeyExpireDayCheck")
async def check_tf_public_key_expire_day(
    request: Request
):
    """
    TF公開鍵有効期限確認バッチ

    """
    # ロガー作成
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", request)

    try:
        in_logger.info(logUtil.message_build(MessageConstClass.IN_LOG["000000"]["logMessage"], EXEC_NAME_JP))
        # モデルオブジェクト作成
        tf_public_key_expire_day_check_batch_model = tfPublicKeyExpireDayCheckBatchModelClass(trace_logger)

        # main関数実行
        tf_public_key_expire_day_check_batch_model.main()

        # 25.終了処理
        # 25-01.正常終了をCloudWatchへログ出力する
        # 25-02. 処理を終了する
        out_logger.info(logUtil.message_build(MessageConstClass.OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP, json.dumps({})))

    # 例外処理(PDSException)
    except PDSException:
        pass

    # 例外処理
    except Exception as e:
        trace_logger.error(logUtil.message_build(MessageConstClass.ERRORS["999999"]["logMessage"], str(e), traceback.format_exc()))
