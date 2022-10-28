class wbtConstClass:

    # WBT新規メール情報登録API

    REPOSITORY_TYPE = {
        "ROUND": "0",       # 往復便
        "OUTWARD": "1",     # 引き取り便
        "RETURN": "2"       # お届け便
    }

    TITLE = {
        "BILLING_DATA_NOTIFICATION": "【VRM/PDS v2.0】 PDSユーザ請求データ通知メール",
        "PDS_USER_CREATE": "【VRM/PDS v2.0】 PDSユーザ公開鍵通知・確認メール",
        "TF_PUBLIC_KEY_EXPIRE_DAY_CHECK": "【VRM/PDS v2.0】TF公開鍵有効期限確認メール",
        "TF_OPERATOR_CREATE": "【VRM/PDS v2.0】TFオペレータ登録仮パスワード通知メール",
        "TF_OPERATOR_PASSWORD_RESET": "【VRM/PDS v2.0】 TFオペレータパスワードリセット 仮パスワード通知メール",
        "USER_PROFILE_MULTI_DOWNLOAD": "【VRM/PDS v2.0】 個人情報一括DL通知メール",
        "USER_PROFILE_MULTI_DELETE": "【VRM/PDS v2.0】 個人情報一括削除通知メール"
    }

    MESSAGE = {
        "BILLING_DATA_NOTIFICATION": "PDSユーザの請求データを送付します\r\n期間内に引き取りをお願いします",
        "PDS_USER_CREATE": "PDSユーザの登録が完了しました\r\nTF公開鍵情報を送付しますので、PDSユーザ公開鍵の返信をお願いします\r\n返信の際には、ファイルの引き取り期限を変更しないようお願いいたします",
        "TF_PUBLIC_KEY_EXPIRE_DAY_CHECK": "有効期限が近いTF公開鍵がございます。\r\nTF公開鍵情報を送付しますので、お手数ですがPDSユーザ公開鍵の返信をお願い申し上げます。\r\n返信の際には、ファイルの引き取り期限を変更しないようお願いいたします。",
        "TF_OPERATOR_CREATE": "TFオペレータの登録が完了しました\r\n仮パスワードを送付しますので、ログイン後パスワード変更をお願いします",
        "TF_OPERATOR_PASSWORD_RESET": "TFオペレータのパスワードリセットが完了しました\r\n仮パスワードを送付しますので、ログイン後パスワード変更をお願いします",
        "PDS_USER_AUTH_INFO_CREATE": "PDSユーザの認証情報発行が完了したことをご報告いたします。\r\nTF公開鍵情報を送付しますので、お手数ですがPDSユーザ公開鍵の返信をお願い申し上げます。\r\n返信の際には、ファイルの引き取り期限を変更しないようお願いいたします。",
        "USER_PROFILE_MULTI_DOWNLOAD": "個人情報の一括DLが完了したことをご報告いたします\r\n対象のTIDのリストを送付しますので、お手数ですが期間内に引き取りをお願いいたします",
        "USER_PROFILE_MULTI_DELETE": "個人情報の一括削除が完了したことをご報告いたします\r\n対象のTIDのリストおよび削除証明書を送付しますので、お手数ですが期間内に引き取りをお願いいたします"
    }
