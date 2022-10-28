import traceback
import json
# FastApi
from fastapi import APIRouter, Request
# Security
from fastapi.security import OAuth2PasswordBearer

# 自作クラス
## 業務ロジッククラス
from models.batch.pdsUserNoticeUseCountBatchModel import pdsUserNoticeUseCountBatchModelClass
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
EXEC_NAME: str = "pdsUserNoticeUseCountBatch"
EXEC_NAME_JP: str = "PDSユーザ利用回数通知バッチ"

# ルータ作成
router = APIRouter()


# 検索用 水野担当ファイル
# PDSユーザ利用回数通知バッチ
@router.post("/api/2.0/batch/pdsUserNoticeUseCountBatch")
async def pds_user_notice_use_count_batch(
    request: Request
):
    """
    PDSユーザ利用回数通知バッチ

    """
    # ロガー作成
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", request)
    try:
        in_logger.info(logUtil.message_build(MessageConstClass.IN_LOG["000000"]["logMessage"], EXEC_NAME_JP))
        # モデルオブジェクト作成
        get_pds_user_use_count_model = pdsUserNoticeUseCountBatchModelClass(trace_logger)

        # main関数実行
        get_pds_user_use_count_model.main()

        # 20.終了処理
        # 20-01. 正常終了をCloudWatchへログ出力する
        out_logger.info(logUtil.message_build(MessageConstClass.OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP, json.dumps({})))

    # 例外処理(PDSException)
    except PDSException:
        pass

    # 例外処理
    except Exception as e:
        trace_logger.error(logUtil.message_build(MessageConstClass.ERRORS["999999"]["logMessage"], str(e), traceback.format_exc()))
