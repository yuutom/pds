class multiDownloadStatusConst:

    MULTI_Download_STATUS = {
        "STATUS_CODE": {
            "DATA_EXTRACTION": "1",
            "WBT_PROCESSING": "2",
            "FINISHED": "3",
            "ERROR": "9"
        },
        "STATUS_NAME": {
            "DATA_EXTRACTION": "データ抽出処理中",
            "WBT_PROCESSING": "WebBureauTransfer処理中",
            "FINISHED": "正常終了",
            "ERROR": "エラー"
        }
    }

    WBT_STATUS = {
        "STATUS_CODE": {
            "PROCESSING": "PROCESSING",
            "FINISHED": "FINISHED",
            "ERROR_HAPPEND": "ERROR_HAPPEND"
        },
        "STATUS_NAME": {
            "PROCESSING": "WebBureauTransfer処理中",
            "FINISHED": "完了",
            "ERROR_HAPPEND": "エラー終了"
        }
    }
