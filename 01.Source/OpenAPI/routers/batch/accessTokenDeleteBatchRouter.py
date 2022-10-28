import traceback
import json
# Security
from fastapi.security import OAuth2PasswordBearer

# 自作クラス
## 業務ロジッククラス
from models.batch.accessTokenDeleteBatchModel import accessTokenDeleteBatchModelClass
## utilクラス
import util.logUtil as logUtil
# FastApi
from fastapi import APIRouter, Request
## 固定値クラス
from const.messageConst import MessageConstClass
from const.systemConst import SystemConstClass
# Exception
from exceptionClass.PDSException import PDSException

# Bearerトークン設定
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="bearerToken")

# 処理名
EXEC_NAME: str = "accessTokenDeleteBatch"
EXEC_NAME_JP: str = "アクセストークン削除バッチ"

# ルータ作成
router = APIRouter()


# アクセストークン削除バッチ
@router.post("/api/2.0/batch/accessTokenDelete")
async def access_token_delete(
    request: Request
):
    """
    アクセストークン削除バッチ

    """
    # ロガー作成
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", request)

    try:
        in_logger.info(logUtil.message_build(MessageConstClass.IN_LOG["000000"]["logMessage"], EXEC_NAME_JP))
        # モデルオブジェクト作成
        access_token_delete_model = accessTokenDeleteBatchModelClass(trace_logger)

        # main関数実行
        access_token_delete_model.main()

        # 06.終了処理
        # 06-01.正常終了をCloudWatchへログ出力する
        out_logger.info(logUtil.message_build(MessageConstClass.OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP, json.dumps({})))
        # 06-02.処理を終了する

    # 例外処理(PDSException)
    except PDSException:
        pass

    # 例外処理
    except Exception as e:
        trace_logger.error(logUtil.message_build(MessageConstClass.ERRORS["999999"]["logMessage"], str(e), traceback.format_exc()))
