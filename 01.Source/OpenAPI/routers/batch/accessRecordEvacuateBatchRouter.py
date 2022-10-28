import traceback
import json
# 自作クラス
## 業務ロジッククラス
from models.batch.accessRecordEvacuateBatchModel import AccessRecordEvacuateBatchModel
## utilクラス
import util.logUtil as logUtil
# FastApi
from fastapi import APIRouter, Request
## 固定値クラス
from const.messageConst import MessageConstClass
from const.systemConst import SystemConstClass
# Exception
from exceptionClass.PDSException import PDSException

# 処理名
EXEC_NAME: str = "accessRecordEvacuateBatch"
EXEC_NAME_JP: str = "アクセス記録退避バッチ"

# ルータ作成
router = APIRouter()


# アクセス記録退避バッチ
@router.post("/api/2.0/batch/accessrecordevacuate")
async def access_record_evacuate(
    request: Request
):
    """
    アクセス記録退避バッチ

    """
    # ロガー作成
    trace_logger, in_logger, out_logger, guid = logUtil.getLogger(SystemConstClass.SYSTEM_NAME, EXEC_NAME, "", "", "", request)

    try:
        in_logger.info(logUtil.message_build(MessageConstClass.IN_LOG["000000"]["logMessage"], EXEC_NAME_JP))
        # モデルオブジェクト作成
        access_record_evacuate_model = AccessRecordEvacuateBatchModel(trace_logger)

        # main関数実行
        access_record_evacuate_model.main()

        # 12.終了処理
        # 12-01.正常終了をCloudWatchへログ出力する
        out_logger.info(logUtil.message_build(MessageConstClass.OUT_LOG["000000"]["logMessage"], EXEC_NAME_JP, json.dumps({})))
        # 12-02.処理を終了する

    # 例外処理(PDSException)
    except PDSException:
        pass

    # 例外処理
    except Exception as e:
        trace_logger.error(logUtil.message_build(MessageConstClass.ERRORS["999999"]["logMessage"], str(e), traceback.format_exc()))
