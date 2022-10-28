class SqlConstClass:
    # システムで利用するSQLの一括管理クラス

    # TFオペレータ検索・参照
    # TFオペレータ全件検索処理
    TF_OPERATOR_SELECT_SQL = """
        SELECT
            m_tf_operator.tf_operator_id
            , m_tf_operator.tf_operator_name
            , m_tf_operator.tf_operator_disable_flg
            , m_tf_operator.tf_operator_mail
        FROM
            m_tf_operator;
    """

    # TFオペレータ無効化
    # TFオペレータID無効化検証処理
    TF_OPERATOR_INVALID_VERIF_SQL = """
        SELECT
            m_tf_operator.tf_operator_disable_flg
        FROM
            m_tf_operator
        WHERE
            m_tf_operator.tf_operator_id = %s;
    """

    # TFオペレータ無効化
    # TFオペレータID無効化更新処理
    TF_OPERATOR_INVALID_UPDATE_SQL = """
        UPDATE m_tf_operator
        SET
            tf_operator_disable_flg = True
        WHERE
            tf_operator_id = %s;
    """

    # TFオペレータパスワード変更
    # TFオペレータ取得処理
    TF_OPERATOR_CHANGE_PASSWORD_SELECT_SQL = """
        SELECT
            m_tf_operator.tf_operator_id
            , m_tf_operator.password
            , m_tf_operator.password_first_generation
            , m_tf_operator.password_second_generation
            , m_tf_operator.password_third_generation
            , m_tf_operator.password_fourth_generation
            , m_tf_operator.password_expire
            , m_tf_operator.password_reset_flg
            , m_tf_operator.tf_operator_disable_flg
        FROM
            m_tf_operator
        WHERE
            m_tf_operator.tf_operator_id = %s;
    """

    # TFオペレータパスワード変更
    # TFオペレータ更新処理
    TF_OPERATOR_CHANGE_PASSWORD_UPDATE_SQL = """
        UPDATE
            m_tf_operator
        SET
            password                     = %s
            , password_first_generation  = %s
            , password_second_generation = %s
            , password_third_generation  = %s
            , password_fourth_generation = %s
            , password_expire            = %s
            , password_reset_flg         = false
        WHERE
            m_tf_operator.tf_operator_id = %s;
    """

    # TFオペレータパスワードリセット
    # TFオペレータパスワードリセット取得処理
    TF_OPERATOR_RESET_PASSWORD_SELECT_SQL = """
        SELECT
            m_tf_operator.tf_operator_disable_flg
            , m_tf_operator.password
            , m_tf_operator.password_first_generation
            , m_tf_operator.password_second_generation
            , m_tf_operator.password_third_generation
            , m_tf_operator.tf_operator_mail
        FROM
            m_tf_operator
        WHERE
            m_tf_operator.tf_operator_id = %s;
    """

    # TFオペレータパスワードリセット
    # TFオペレータパスワードリセット更新処理
    TF_OPERATOR_RESET_PASSWORD_UPDATE_SQL = """
        UPDATE m_tf_operator
        SET
            password                     = %s
            , password_first_generation  = %s
            , password_second_generation = %s
            , password_third_generation  = %s
            , password_fourth_generation = %s
            , password_expire            = %s
            , password_reset_flg         = true
        WHERE
            m_tf_operator.tf_operator_id = %s;
    """

    # TFオペレータログイン
    # TFオペレータ取得処理
    TF_OPERATOR_LOGIN_SELECT_SQL = """
        SELECT
            m_tf_operator.tf_operator_name
            , m_tf_operator.password_reset_flg
        FROM
            m_tf_operator
        WHERE
            m_tf_operator.tf_operator_id = %s
            AND m_tf_operator.password = %s
            AND m_tf_operator.tf_operator_disable_flg = false
            AND m_tf_operator.password_expire >= %s;
    """

    # TFオペレータ登録
    # TFオペレータ取得処理
    TF_OPERATOR_REGISTER_SELECT_SQL = """
        SELECT
            COUNT(m_tf_operator.tf_operator_id)
        FROM
            m_tf_operator
        WHERE
            m_tf_operator.tf_operator_id = %s
    """

    # TFオペレータ登録
    # TFオペレータ登録処理
    TF_OPERATOR_REGISTER_INSERT_SQL = """
        INSERT INTO m_tf_operator (
            tf_operator_id,
            tf_operator_name,
            tf_operator_mail,
            password,
            password_reset_flg,
            tf_operator_disable_flg,
            password_expire,
            password_first_generation,
            password_second_generation,
            password_third_generation,
            password_fourth_generation
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        );
    """

    # PDSユーザ登録API
    # PDSユーザ取得処理
    PDS_USER_EXIST_SELECT_SQL = """
        SELECT
            COUNT(pds_user_id)
        FROM
            m_pds_user
        where
            m_pds_user.pds_user_id = %s;
    """

    # PDSユーザ利用回数通知バッチ
    # PDSユーザ情報取得処理
    PDS_USER_VALID_FLG_TRUE_SELECT_SQL = """
        SELECT
            m_pds_user.pds_user_id
            , m_pds_user.pds_user_name
            , m_pds_user.sales_address
        FROM
            m_pds_user
        WHERE
            m_pds_user.valid_flg = True;
    """

    # PDSユーザ利用回数通知バッチ
    # API実行履歴取得処理
    API_HISTORY_SELECT_SQL = """
        SELECT
            t_exec_api_history.api_type
            , t_exec_api_history.exec_status
            , COUNT(t_exec_api_history.api_type)
        FROM
            t_exec_api_history
        WHERE
            t_exec_api_history.pds_user_id = %s
            AND t_exec_api_history.register_datetime >= %s
            AND t_exec_api_history.register_datetime <= %s
            AND t_exec_api_history.api_type NOT IN ('1', '7', '8')
        GROUP BY
            t_exec_api_history.api_type
            , t_exec_api_history.exec_status
        ORDER BY
            t_exec_api_history.api_type;
    """

    # アクセス記録退避バッチ
    # アクセス記録取得処理
    API_HISTORY_EVACUTATE_SELECT_SQL = """
        SELECT
            t_exec_api_history.exec_id
            , t_exec_api_history.pds_user_id
            , t_exec_api_history.api_type
            , t_exec_api_history.path_param_pds_user_domain_name
            , t_exec_api_history.exec_path
            , t_exec_api_history.exec_param
            , t_exec_api_history.exec_status
            , t_exec_api_history.exec_user_id
            , t_exec_api_history.register_datetime
        FROM
            t_exec_api_history
        WHERE
            t_exec_api_history.register_datetime < %s
    """

    # アクセス記録退避バッチ
    # アクセス記録削除処理
    API_HISTORY_EVACUTATE_DELETE_SQL = """
        DELETE
        FROM
            t_exec_api_history
        WHERE
            t_exec_api_history.register_datetime < %s
    """

    # PDSユーザ利用回数通知バッチ
    # 請求金額取得処理
    BILLING_SELECT_SQL = """
        SELECT
            m_billing.billing_yen
            , m_billing.billing_exec_count_width_from
            , m_billing.billing_exec_count_width_to
        FROM
            m_billing
        WHERE
            m_billing.api_type = %s
            AND m_billing.billing_exec_count_width_from >= %s;
    """

    # TF公開鍵有効期限確認バッチ
    # PDSユーザPDSユーザ公開鍵情報取得処理
    PDS_USER_PDS_USER_PUBLIC_KEY_SELECT_SQL = """
        SELECT
            pds_user_key.pds_key_idx
            , m_pds_user.pds_user_id
            , m_pds_user.pds_user_name
            , m_pds_user.credential_notice_address_to
            , m_pds_user.credential_notice_address_cc
            , pds_user_key.pds_key
            , pds_user_key.update_date
        FROM
            m_pds_user INNER JOIN (
                SELECT
                    pds_user_key_A.pds_user_id
                    , pds_user_key_A.pds_key_idx
                    , pds_user_key_A.pds_key
                    , pds_user_key_A.update_date
                FROM
                    m_pds_user_key AS pds_user_key_A INNER JOIN (
                        SELECT
                            pds_user_id
                            , MAX(pds_key_idx) AS max_pds_key_idx
                        FROM
                            m_pds_user_key
                        WHERE
                            update_date < %s
                            AND valid_flg = True
                        GROUP BY
                            pds_user_id
                    ) AS pds_user_key_B
                        ON pds_user_key_A.pds_user_id = pds_user_key_B.pds_user_id
                        AND pds_user_key_A.pds_key_idx = pds_user_key_B.max_pds_key_idx
            ) AS pds_user_key
                ON m_pds_user.pds_user_id = pds_user_key.pds_user_id;
    """

    # PDSユーザ公開鍵ダウンロード格納バッチ
    # PDSユーザPDSユーザ公開鍵情報取得処理
    PDS_USER_PDS_USER_PUBLIC_KEY_SELECT_WBT_SENDER_SQL = """
        SELECT
            m_pds_user.pds_user_id
            , m_pds_user_key.pds_key_idx
            , m_pds_user_key.wbt_send_mail_id
            , m_pds_user_key.wbt_send_mail_title
        FROM
            m_pds_user
            INNER JOIN m_pds_user_key
                ON m_pds_user.pds_user_id = m_pds_user_key.pds_user_id
        WHERE
            m_pds_user.valid_flg = True
            AND m_pds_user_key.wbt_reply_deadline_check_flg = False
            AND m_pds_user_key.wbt_reply_deadline_date <= %s
    """

    # PDSユーザ公開鍵ダウンロード格納バッチ
    # PDSユーザ公開鍵テーブル更新処理
    PDS_USER_PUBLIC_KEY_UPDATE_SQL = """
        UPDATE m_pds_user_key
        SET
            pds_key = %s
            , wbt_reply_deadline_check_flg = True
        WHERE
            m_pds_user_key.pds_user_id = %s
            AND m_pds_user_key.pds_key_idx = %s
    """

    # 個人情報削除バッチ
    # PDSユーザデータ取得処理
    TRANSACTION_DELETE_PDS_USER_SELECT_SQL = """
        SELECT
            m_pds_user.pds_user_instance_secret_name
            , m_pds_user.s3_image_data_bucket_name
            , m_pds_user.tokyo_a_mongodb_secret_name
            , m_pds_user.tokyo_c_mongodb_secret_name
            , m_pds_user.osaka_a_mongodb_secret_name
            , m_pds_user.osaka_c_mongodb_secret_name
        FROM
            m_pds_user
        WHERE
            m_pds_user.pds_user_id = %s
            AND m_pds_user.valid_flg = True
    """

    # 個人情報削除バッチ
    # 個人情報削除対象データ一括取得処理
    TRANSACTION_DELETE_DATA_TO_DELETE_SELECT_SQL = """
        SELECT
            t_user_profile.transaction_id
            , t_user_profile.valid_flg
            , t_user_profile.json_data_flg
            , t_user_profile.save_data_mongodb_key
            , t_user_profile_binary.save_image_idx
            , t_user_profile_binary.save_image_data_id
            , t_user_profile_binary.valid_flg
            , t_user_profile_binary_split.file_save_path
        FROM
            t_user_profile
            INNER JOIN t_user_profile_binary
                ON (
                    t_user_profile.transaction_id = t_user_profile_binary.transaction_id
                )
            INNER JOIN t_user_profile_binary_split
                ON (
                    t_user_profile_binary.save_image_data_id = t_user_profile_binary_split.save_image_data_id
                )
        WHERE
            t_user_profile.transaction_id = %s
            AND t_user_profile.valid_flg = false
        UNION
        SELECT
            t_user_profile.transaction_id
            , t_user_profile.valid_flg
            , t_user_profile.json_data_flg
            , t_user_profile.save_data_mongodb_key
            , t_user_profile_binary.save_image_idx
            , t_user_profile_binary.save_image_data_id
            , t_user_profile_binary.valid_flg
            , t_user_profile_binary_split.file_save_path
        FROM
            t_user_profile
            INNER JOIN t_user_profile_binary
                ON (
                    t_user_profile.transaction_id = t_user_profile_binary.transaction_id
                )
            INNER JOIN t_user_profile_binary_split
                ON (
                    t_user_profile_binary.save_image_data_id = t_user_profile_binary_split.save_image_data_id
                )
        WHERE
            t_user_profile.transaction_id = %s
            AND t_user_profile.valid_flg = true
            AND t_user_profile_binary.valid_flg = false;
    """

    # 個人情報削除バッチ
    # 個人情報バイナリ分割データ削除処理
    TRANSACTION_DELETE_BINARY_SPLIT_DELETE_SQL = """
        DELETE
        FROM
            t_user_profile_binary_split
        WHERE
            t_user_profile_binary_split.save_image_data_id IN %s
    """

    # 個人情報削除バッチ
    # 個人情報バイナリデータ削除処理
    TRANSACTION_DELETE_BINARY_DELETE_SQL = """
        DELETE
        FROM
            t_user_profile_binary
        WHERE
            t_user_profile_binary.transaction_id = %s
            AND t_user_profile_binary.save_image_idx IN %s
    """

    # 個人情報削除バッチ
    # 個人情報削除処理
    TRANSACTION_DELETE_DATA_DELETE_SQL = """
        DELETE
        FROM
            t_user_profile
        WHERE
            t_user_profile.transaction_id = %s
            AND t_user_profile.valid_flg = false
    """

    # PDSユーザ登録API
    # PDSユーザ登録処理
    PDS_USER_INSERT_SQL = """
        INSERT INTO m_pds_user (
            pds_user_id,
            group_id,
            pds_user_name,
            pds_user_domain_name,
            api_key,
            pds_user_instance_secret_name,
            s3_image_data_bucket_name,
            tokyo_a_mongodb_secret_name,
            tokyo_c_mongodb_secret_name,
            osaka_a_mongodb_secret_name,
            osaka_c_mongodb_secret_name,
            user_profile_kms_id,
            valid_flg,
            sales_address,
            download_notice_address_to,
            download_notice_address_cc,
            delete_notice_address_to,
            delete_notice_address_cc,
            credential_notice_address_to,
            credential_notice_address_cc
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        );
    """

    # PDSユーザアクセス記録閲覧API
    # PDS利用状況取得処理
    PDS_USER_USAGE_SITUATION_SQL = """
        SELECT
            t_exec_api_history.register_datetime
            , t_exec_api_history.exec_user_id
            , t_exec_api_history.api_type
            , t_exec_api_history.exec_param
            , t_exec_api_history.exec_status
        FROM
            t_exec_api_history
        WHERE
            t_exec_api_history.pds_user_id = %s
            AND t_exec_api_history.register_datetime >= %s
            AND t_exec_api_history.register_datetime <= %s
        ORDER BY
            t_exec_api_history.register_datetime DESC;
    """

    # PDSユーザ登録API
    # PDSユーザ認証情報発行API
    # TF公開鍵有効期限確認バッチ
    # PDSユーザ公開鍵登録処理
    PDS_USER_KEY_INSERT_SQL = """
        INSERT
        INTO m_pds_user_key(
            pds_user_id
            , pds_key_idx
            , pds_key
            , tf_key_kms_id
            , start_date
            , update_date
            , end_date
            , wbt_reply_deadline_date
            , wbt_reply_deadline_check_flg
            , wbt_send_mail_id
            , wbt_send_mail_title
            , valid_flg
        )
        VALUES (
            %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
        );
    """

    # PDSユーザ登録API
    # PDSユーザ認証情報発行API
    # WBT送信メールID更新処理
    PDS_USER_KEY_UPDATE_SQL = """
        UPDATE m_pds_user_key
        SET
            wbt_send_mail_id = %s
        WHERE
            m_pds_user_key.pds_user_id = %s
            AND m_pds_user_key.pds_key_idx = %s;
    """

    # PDSユーザ利用回数確認API
    # API実行履歴取得処理
    PDS_USER_GET_USE_COUNT_API_HISTORY_SELECT_SQL = """
        SELECT
            t_exec_api_history.api_type
            , t_exec_api_history.exec_status
            , COUNT(t_exec_api_history.api_type)
        FROM
            t_exec_api_history
        WHERE
            t_exec_api_history.pds_user_id = %s
    """

    # PDSユーザ認証情報発行API
    # PDSユーザ取得処理
    PDS_USER_AUTH_CREATE_SELECT_SQL = """
        SELECT
            m_pds_user.pds_user_name
            , m_pds_user.valid_flg
            , m_pds_user.credential_notice_address_to
            , m_pds_user.credential_notice_address_cc
        FROM
            m_pds_user
        WHERE
            m_pds_user.pds_user_id = %s;
    """

    # PDSユーザ認証情報発行API
    # PDSユーザ取得処理
    PDS_USER_AUTH_CREATE_MAX_INDEX_SELECT_SQL = """
        SELECT
            MAX(m_pds_user_key.pds_key_idx)
        FROM
            m_pds_user_key
        WHERE
            m_pds_user_key.pds_user_id = %s;
    """

    # 共通処理 アクセストークン発行
    # アクセストークン登録処理
    ACCESS_TOKEN_INSERT_SQL = """
        INSERT
        INTO t_access_token(
            access_token
            , tf_operator_id
            , pds_user_id
            , valid_flg
            , period_datetime
            , jwt_secret_key
        )
        VALUES (
            %s
            , %s
            , %s
            , %s
            , %s
            , %s
        );
    """

    # 共通処理 アクセストークン発行
    # TFオペレータ取得処理
    ACCESS_TOKEN_CLOSED_TF_OPERATOR_VERIF_SQL = """
        SELECT
            m_tf_operator.password_reset_flg
        FROM
            m_tf_operator
        WHERE
            m_tf_operator.tf_operator_id = %s
            AND m_tf_operator.tf_operator_disable_flg = %s;
    """

    # 共通処理 アクセストークン発行（公開用）
    # PDSユーザテーブル取得処理
    ACCESS_TOKEN_PUBLIC_PDS_USER_TOKEN_ISSUANCE_SQL = """
        SELECT
            m_pds_user.pds_user_id
        FROM
            m_pds_user
        WHERE
            m_pds_user.pds_user_id = %s
            AND m_pds_user.pds_user_name = %s
            AND m_pds_user.valid_flg = %s;
    """

    # 共通処理 アクセストークン検証処理（公開用）
    # アクセストークンテーブル取得処理
    ACCESS_TOKEN_PUBLIC_SELECT_SQL = """
        SELECT
            t_access_token.jwt_secret_key
        FROM
            t_access_token
        WHERE
            t_access_token.access_token = %s
            AND t_access_token.pds_user_id = %s
            AND t_access_token.period_datetime >= %s
            AND t_access_token.valid_flg = %s;
    """

    # 共通処理 アクセストークン検証処理（非公開用）
    # アクセストークンテーブル取得処理
    ACCESS_TOKEN_CLOSED_SELECT_SQL = """
        SELECT
            t_access_token.jwt_secret_key
            , t_access_token.tf_operator_id
        FROM
            t_access_token
        WHERE
            t_access_token.access_token = %s
            AND t_access_token.period_datetime >= %s
            AND t_access_token.valid_flg = true;
    """

    ACCESS_TOKEN_CLOSED_DELETE_SQL = """
        DELETE FROM t_access_token WHERE access_token = %s;
    """

    # アクセストークン削除バッチ
    # アクセストークン削除処理
    ACCESS_TOKEN_BATCH_DELETE_SQL = """
        DELETE
        FROM
            t_access_token
        WHERE
            t_access_token.period_datetime < %s;
    """

    # 共通処理 アクセストークン発行処理（非公開用）
    # アクセストークン無効処理
    ACCESS_TOKEN_CLOSED_UPDATE_SQL = """
        UPDATE t_access_token
        SET
            valid_flg = false
        WHERE
            t_access_token.tf_operator_id = %s
            AND t_access_token.access_token = %s
            AND t_access_token.valid_flg = %s;
    """

    # 共通処理 アクセストークン発行処理（非公開用）
    # アクセストークン無効処理
    ACCESS_TOKEN_PUBLIC_UPDATE_SQL = """
        UPDATE t_access_token
        SET
            valid_flg = false
        WHERE
            t_access_token.pds_user_id = %s
            AND t_access_token.access_token = %s
            AND t_access_token.valid_flg = %s;
    """

    # PDSユーザドメイン検証処理
    # PDSユーザ取得処理
    PDS_USER_DOMAIN_NAME_SELECT_SQL = """
        SELECT
            m_pds_user.pds_user_id
            , m_pds_user.group_id
            , m_pds_user.pds_user_name
            , m_pds_user.pds_user_domain_name
            , m_pds_user.api_key
            , m_pds_user.pds_user_instance_secret_name
            , m_pds_user.s3_image_data_bucket_name
            , m_pds_user.user_profile_kms_id
            , m_pds_user.valid_flg
            , m_pds_user.tokyo_a_mongodb_secret_name
            , m_pds_user.tokyo_c_mongodb_secret_name
            , m_pds_user.osaka_a_mongodb_secret_name
            , m_pds_user.osaka_c_mongodb_secret_name
            , m_pds_user.sales_address
            , m_pds_user.download_notice_address_to
            , m_pds_user.download_notice_address_cc
            , m_pds_user.delete_notice_address_to
            , m_pds_user.delete_notice_address_cc
            , m_pds_user.credential_notice_address_to
            , m_pds_user.credential_notice_address_cc
        FROM
            m_pds_user
        WHERE
            m_pds_user.pds_user_domain_name = %s
            AND m_pds_user.pds_user_id = %s
            AND m_pds_user.valid_flg = true;
    """

    # 共通処理用SQL（API実行履歴登録）
    API_HISTORY_INSERT_SQL = """
        INSERT
        INTO t_exec_api_history(
            exec_id
            , pds_user_id
            , api_type
            , path_param_pds_user_domain_name
            , exec_path
            , exec_param
            , exec_status
            , exec_user_id
            , register_datetime
        )
        VALUES (
            %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
        );
    """

    # 共通処理 PDSユーザ公開鍵更新処理
    # PDSユーザ公開鍵更新処理(PDSユーザ公開鍵存在)
    PDS_USER_UPDATE_SQL_PDS_USER_KEY_CONDITION = """
        UPDATE m_pds_user_key
        SET
            pds_key                        = %s
            , wbt_reply_deadline_check_flg = True
        WHERE
            m_pds_user_key.pds_user_id     = %s
            AND m_pds_user_key.pds_key_idx = %s;
    """

    # 共通処理 PDSユーザ公開鍵更新処理
    # PDSユーザ公開鍵更新処理(終了日存在)
    PDS_USER_UPDATE_SQL_END_DATE_CONDITION = """
        UPDATE m_pds_user_key
        SET
            end_date    = %s
            , valid_flg = False
        WHERE
            m_pds_user_key.pds_user_id     = %s
            AND m_pds_user_key.pds_key_idx = %s;
    """

    # 共通処理 リソース請求金額計算処理
    PDS_USER_RESOURCE_BILLING_SELECT_SQL = """
        SELECT
            m_pds_user.pds_user_instance_secret_name
        FROM
            m_pds_user
        WHERE
            m_pds_user.pds_user_id = %s
            AND m_pds_user.valid_flg = True
    """

    # 共通処理 承認者情報確認処理
    CHECK_APPROVAL_USER_SELECT_SQL = """
        SELECT
            COUNT(m_tf_operator.tf_operator_id)
        FROM
            m_tf_operator
        WHERE
            m_tf_operator.tf_operator_id = %s
            AND m_tf_operator.password = %s
            AND m_tf_operator.password_reset_flg = false
            AND m_tf_operator.password_expire >= %s;
    """

    # 共通処理 PDSユーザ鍵存在検証処理
    # PDSユーザ取得処理
    PDS_USER_JOIN_PDS_USER_KEY_SELECT_SQL = """
        SELECT
            COUNT(m_pds_user_key.pds_key_idx)
        FROM
            m_pds_user
            INNER JOIN m_pds_user_key
                ON (
                    m_pds_user.pds_user_id = m_pds_user_key.pds_user_id
                )
        WHERE
            m_pds_user.pds_user_id = %s
            AND m_pds_user.valid_flg = true
            AND m_pds_user_key.pds_user_id = %s
            AND m_pds_user_key.pds_key_idx = %s
            AND m_pds_user_key.valid_flg = true;
    """

    # 共通処理 個人情報検索処理
    # 個人情報取得処理
    USER_PROFILE_SELECT_SQL = """
        SELECT
            t_user_profile.transaction_id
            , t_user_profile.user_id
            , t_user_profile.save_datetime
            , t_user_profile.save_data
            , t_user_profile_binary.save_image_data_hash
        FROM
            t_user_profile
            INNER JOIN t_user_profile_binary
                ON (
                    t_user_profile.transaction_id = t_user_profile_binary.transaction_id
                )
        WHERE
            t_user_profile.valid_flg = true
            AND t_user_profile_binary.valid_flg = true
    """

    # 個人情報登録API
    # 個人情報取得処理（存在確認）
    USER_PROFILE_SELECT_CHECK_SQL = """
        SELECT
            t_user_profile.transaction_id
        FROM
            t_user_profile
        WHERE
            t_user_profile.transaction_id = %s
    """

    # 個人情報登録API
    # 個人情報登録処理
    USER_PROFILE_INSERT_SQL = """
        INSERT
        INTO t_user_profile(
            transaction_id
            , user_id
            , save_datetime
            , json_data_flg
            , save_data_mongodb_key
            , save_data
            , secure_level
            , valid_flg
            , register_datetime
        )
        VALUES (
            %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
        );
    """

    # 個人情報バイナリデータ登録処理
    # 個人情報バイナリデータ登録処理
    USER_PROFILE_BINARY_INSERT_SQL = """
        INSERT
        INTO t_user_profile_binary(
            transaction_id
            , save_image_idx
            , save_image_data_id
            , save_image_data_hash
            , split_count
            , chunk_size
            , valid_flg
            , save_image_data_array_index
            , byte_size
        )
        VALUES (
            %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
        );
    """

    # 個人情報バイナリ分割データ登録処理
    # 個人情報バイナリ分割データ登録処理
    USER_PROFILE_BINARY_SEPARATE_INSERT_SQL = """
        INSERT
        INTO t_user_profile_binary_split(
            save_image_data_id
            , split_no
            , file_save_path
            , kms_data_key
            , chiper_nonce
        )
        VALUES (
            %s
            , %s
            , %s
            , %s
            , %s
        );
    """

    # 個人情報登録API
    # 個人情報有効フラグ更新処理
    USER_PROFILE_VALID_FLG_UPDATE_SQL = """
        UPDATE t_user_profile
        SET
            valid_flg = true
        WHERE
            t_user_profile.transaction_id = %s
            AND t_user_profile.valid_flg = %s;
    """

    # 個人情報参照API
    # 個人情報取得処理
    USER_PROFILE_READ_SQL = """
        SELECT
            t_user_profile.transaction_id
            , t_user_profile.user_id
            , t_user_profile.save_datetime
            , t_user_profile.save_data
            , t_user_profile.secure_level
            , t_user_profile.json_data_flg
        FROM
            t_user_profile
        WHERE
            t_user_profile.transaction_id = %s
            AND t_user_profile.valid_flg = %s;
    """

    # 個人情報参照API
    # 個人バイナリ情報取得処理
    # 個人情報一括DLAPI
    # 個人バイナリ情報取得処理
    USER_PROFILE_BINARY_GET_READ_TARGET_SQL = """
        SELECT
            t_user_profile_binary.transaction_id
            , t_user_profile_binary.save_image_idx
            , t_user_profile_binary.save_image_data_id
            , t_user_profile_binary.save_image_data_hash
            , t_user_profile_binary_split.split_no
            , t_user_profile_binary_split.file_save_path
            , t_user_profile_binary_split.kms_data_key
            , t_user_profile_binary_split.chiper_nonce
        FROM
            t_user_profile_binary
            INNER JOIN t_user_profile_binary_split
                ON (
                    t_user_profile_binary.save_image_data_id = t_user_profile_binary_split.save_image_data_id
                )
        WHERE
            t_user_profile_binary.transaction_id = %s
            AND t_user_profile_binary.valid_flg = %s
        ORDER BY
            t_user_profile_binary.save_image_data_array_index
            , t_user_profile_binary_split.split_no;
    """

    # PDSユーザ登録API
    # 個人情報テーブル作成処理
    USER_PROFILE_TABLE_CREATE = """
        CREATE TABLE t_user_profile(
            transaction_id varchar(36) PRIMARY KEY,
            user_id varchar(36),
            save_datetime timestamp,
            json_data_flg boolean,
            save_data_mongodb_key text,
            save_data text,
            secure_level varchar(2),
            valid_flg boolean,
            register_datetime timestamp
        );
    """

    # PDSユーザ登録API
    # 個人情報バイナリテーブル作成処理
    USER_PROFILE_BINARY_TABLE_CREATE = """
        CREATE TABLE t_user_profile_binary(
            transaction_id varchar(36),
            save_image_idx integer,
            save_image_data_id varchar(32),
            save_image_data_hash varchar(128),
            split_count integer,
            chunk_size integer,
            valid_flg boolean,
            save_image_data_array_index integer,
            PRIMARY KEY(transaction_id,save_image_idx)
        );
    """

    # PDSユーザ登録API
    # 個人情報バイナリ分割テーブル作成処理
    USER_PROFILE_BINARY_SPLIT_TABLE_CREATE = """
        CREATE TABLE t_user_profile_binary_split(
            save_image_data_id varchar(32),
            split_no integer,
            file_save_path varchar(255),
            kms_data_key text,
            chiper_nonce text,
            PRIMARY KEY(save_image_data_id, split_no)
        );
    """

    # PDSユーザ検索・参照API
    # PDSユーザ検索処理
    PDS_USER_SEARCH_SELECT_SQL = """
        SELECT
            m_pds_user.pds_user_id
            , m_pds_user.pds_user_name
            , m_pds_user.api_key
            , m_pds_user_key.pds_key_idx
            , m_pds_user_key.valid_flg
            , m_pds_user_key.start_date
            , m_pds_user_key.update_date
            , m_pds_user_key.end_date
            , m_pds_user.sales_address
            , m_pds_user.download_notice_address_to
            , m_pds_user.download_notice_address_cc
            , m_pds_user.delete_notice_address_to
            , m_pds_user.delete_notice_address_cc
        FROM
            m_pds_user
            INNER JOIN m_pds_user_key
                ON (
                    m_pds_user.pds_user_id = m_pds_user_key.pds_user_id
                )
    """

    # 個人情報一括DL状況確認API
    # 個人情報一括DL状態管理取得処理
    MULTI_DOWUNLOAD_STATUS_UNION_SELECT_SQL = """
        SELECT
            t_multi_download_status_manage.request_no
            , t_multi_download_status_manage.exec_status
            , t_multi_download_status_manage.mail_id
            , t_multi_download_status_manage.start_datetime
            , t_multi_download_status_manage.end_datetime
        FROM
            t_multi_download_status_manage
        WHERE
            t_multi_download_status_manage.pds_user_id = %s
            AND t_multi_download_status_manage.start_datetime > %s
        UNION
        SELECT
            t_multi_download_status_manage.request_no
            , t_multi_download_status_manage.exec_status
            , t_multi_download_status_manage.mail_id
            , t_multi_download_status_manage.start_datetime
            , t_multi_download_status_manage.end_datetime
        FROM
            t_multi_download_status_manage
        WHERE
            t_multi_download_status_manage.pds_user_id = %s
            AND t_multi_download_status_manage.exec_status IN ('1', '2')
        ORDER BY
            start_datetime DESC;
    """

    # 個人情報削除API (公開側)
    # 個人情報取得処理
    USER_PROFILE_DELETE_SELECT_SQL = """
        SELECT
            t_user_profile.transaction_id
            , t_user_profile.json_data_flg
            , t_user_profile.save_data_mongodb_key
            , t_user_profile.save_data
        FROM
            t_user_profile
        WHERE
            t_user_profile.transaction_id = %s
            AND t_user_profile.valid_flg = true;
    """

    # 個人情報削除API (公開側)
    # 個人情報バイナリデータ取得処理
    USER_PROFILE_DELETE_BINARY_DATA_SELECT_SQL = """
        SELECT
            t_user_profile_binary.transaction_id
            , t_user_profile_binary.save_image_idx
        FROM
            t_user_profile_binary
        WHERE
            t_user_profile_binary.transaction_id = %s
            AND t_user_profile_binary.valid_flg = true
        ORDER BY
            t_user_profile_binary.save_image_idx;
    """

    # 個人情報削除API (公開側)
    # 個人情報バイナリデータ更新処理
    USER_PROFILE_DELETE_BINARY_DATA_UPDATE_SQL = """
        UPDATE t_user_profile_binary
        SET
            valid_flg = false
        WHERE
            t_user_profile_binary.transaction_id = %s;
    """

    # 個人情報削除API (公開側)
    # 個人情報論理削除処理
    USER_PROFILE_DELETE_DATA_UPDATE_SQL = """
        UPDATE t_user_profile
        SET
            valid_flg = false
        WHERE
            t_user_profile.transaction_id = %s;
    """

    # 個人情報削除バッチ
    # 削除対象取得処理
    DELETE_PROFILE_DATA_SEARCH_SQL = """
        SELECT
            t_user_profile.transaction_id
            , t_user_profile.valid_flg
            , t_user_profile.json_data_flg
            , t_user_profile.save_data_mongodb_key
            , t_user_profile_binary.save_image_idx
            , t_user_profile_binary.save_image_data_id
            , t_user_profile_binary.valid_flg
            , t_user_profile_binary_split.file_save_path
        FROM
            t_user_profile
            INNER JOIN t_user_profile_binary
                ON (
                    t_user_profile.transaction_id = t_user_profile_binary.transaction_id
                )
            INNER JOIN t_user_profile_binary_split
                ON (
                    t_user_profile_binary.save_image_data_id = t_user_profile_binary_split.save_image_data_id
                )
        WHERE
            t_user_profile.transaction_id = %s
            AND t_user_profile.valid_flg = false
        UNION
        SELECT
            t_user_profile.transaction_id
            , t_user_profile.valid_flg
            , t_user_profile.json_data_flg
            , t_user_profile.save_data_mongodb_key
            , t_user_profile_binary.save_image_idx
            , t_user_profile_binary.save_image_data_id
            , t_user_profile_binary.valid_flg
            , t_user_profile_binary_split.file_save_path
        FROM
            t_user_profile
            INNER JOIN t_user_profile_binary
                ON (
                    t_user_profile.transaction_id = t_user_profile_binary.transaction_id
                )
            INNER JOIN t_user_profile_binary_split
                ON (
                    t_user_profile_binary.save_image_data_id = t_user_profile_binary_split.save_image_data_id
                )
        WHERE
            t_user_profile.transaction_id = %s
            AND t_user_profile.valid_flg = true
            AND t_user_profile_binary.valid_flg = false;
    """

    # PDSユーザ更新処理
    # PDSユーザ更新処理
    PDS_USER_UPDATE_SQL = """
        UPDATE m_pds_user
        SET
            sales_address = %s
            , download_notice_address_to = %s
            , download_notice_address_cc = %s
            , delete_notice_address_to = %s
            , delete_notice_address_cc = %s
            , credential_notice_address_to = %s
            , credential_notice_address_cc = %s
        WHERE
            m_pds_user.pds_user_id = %s;
    """

    # アクセストークン発行処理
    # PDSユーザPDSユーザ公開鍵情報取得処理
    PDS_USER_PDS_USER_PUBLIC_KEY_TOKEN_SELECT_SQL = """
    SELECT
        m_pds_user.api_key
        , m_pds_user_key.tf_key_kms_id
        , m_pds_user_key.pds_key
    FROM
        m_pds_user
        INNER JOIN m_pds_user_key
            ON m_pds_user.pds_user_id = m_pds_user_key.pds_user_id
    WHERE
        m_pds_user.pds_user_id = %s
        AND m_pds_user_key.pds_key IS NOT NULL
        AND m_pds_user_key.valid_flg = True;
    """

    # 個人情報更新API
    # 個人情報検索処理
    USER_PROFILE_SEARCH_SELECT_SQL = """
        SELECT
            t_user_profile.save_data
            , t_user_profile.save_data_mongodb_key
            , t_user_profile.json_data_flg
            , t_user_profile.valid_flg
        FROM
            t_user_profile
        WHERE
            t_user_profile.transaction_id = %s
    """

    # 個人情報更新API
    # 個人情報バイナリ情報取得処理
    USER_PROFILE_BINARY_SEARCH_SELECT_SQL = """
        SELECT
            t_user_profile_binary.save_image_idx
            , t_user_profile_binary.save_image_data_id
            , t_user_profile_binary.save_image_data_hash
            , t_user_profile_binary.byte_size
        FROM
            t_user_profile_binary
        WHERE
            t_user_profile_binary.transaction_id = %s
            AND t_user_profile_binary.valid_flg = %s
        ORDER BY
            t_user_profile_binary.save_image_data_array_index;
    """

    # 個人情報更新API
    # 個人情報バイナリ情報最大値取得処理
    USER_PROFILE_BINARY_SEARCH_MAX_SELECT_SQL = """
        SELECT
            max(t_user_profile_binary.save_image_idx)
        FROM
            t_user_profile_binary
        WHERE
            t_user_profile_binary.transaction_id = %s;
    """

    # 個人情報更新API
    # 個人情報バイナリ情報取得処理
    GET_USER_PROFILE_BINARY_LOGICAL_DELETE_SELECT_SQL = """
        SELECT
            t_user_profile_binary.save_image_idx
            , t_user_profile_binary.save_image_data_id
            , t_user_profile_binary.save_image_data_hash
        FROM
            t_user_profile_binary
        WHERE
            t_user_profile_binary.transaction_id = %s
            AND t_user_profile_binary.valid_flg = %s
        ORDER BY
            t_user_profile_binary.save_image_data_array_index;
    """

    # 個人情報更新API
    # 個人情報バイナリ情報更新処理
    UPDATE_USER_PROFILE_BINARY_VALID_FLG_SQL = """
        UPDATE t_user_profile_binary
        SET
            valid_flg = true
        WHERE
            t_user_profile_binary.transaction_id = %s
            AND t_user_profile_binary.save_image_idx IN %s
            AND t_user_profile_binary.valid_flg = %s;
    """

    # 個人情報更新API
    # 個人情報テーブル更新処理
    UPDATE_USER_PROFILE_SQL_PREFIX = """
        UPDATE t_user_profile
        SET
    """
    UPDATE_USER_PROFILE_SQL_SUFFIX = """
        WHERE
            t_user_profile.transaction_id = %s;
    """

    # 個人情報更新API
    # 個人情報バイナリデータスキップ処理
    UPDATE_USER_PROFILE_BINARY_SKIP_SQL = """
        UPDATE t_user_profile_binary
        SET
            save_image_data_array_index = %s
        WHERE
            t_user_profile_binary.transaction_id = %s
            AND t_user_profile_binary.save_image_idx = %s;
    """

    # 個人情報更新API
    # 個人情報バイナリ論理削除処理
    UPDATE_USER_PROFILE_BINARY_LOGICAL_DELETE_SQL = """
        UPDATE t_user_profile_binary
        SET
            valid_flg = False
        WHERE
            t_user_profile_binary.transaction_id = %s
            AND t_user_profile_binary.save_image_idx = %s;
    """

    # 個人情報一括DLAPI
    # 個人情報検索API
    # PDSユーザデータ取得処理
    MONGODB_SECRET_NAME_SELECT_SQL = """
        SELECT
            m_pds_user.pds_user_instance_secret_name
            , m_pds_user.tokyo_a_mongodb_secret_name
            , m_pds_user.tokyo_c_mongodb_secret_name
            , m_pds_user.osaka_a_mongodb_secret_name
            , m_pds_user.osaka_c_mongodb_secret_name
        FROM
            m_pds_user
        WHERE
            m_pds_user.pds_user_id = %s
            AND m_pds_user.valid_flg = True;
    """

    # 個人情報一括DLAPI
    # PDSユーザデータ取得処理
    MONGODB_SECRET_NAME_BUCKET_NAME_SELECT_SQL = """
        SELECT
            m_pds_user.pds_user_instance_secret_name
            , m_pds_user.tokyo_a_mongodb_secret_name
            , m_pds_user.tokyo_c_mongodb_secret_name
            , m_pds_user.osaka_a_mongodb_secret_name
            , m_pds_user.osaka_c_mongodb_secret_name
            , m_pds_user.s3_image_data_bucket_name
        FROM
            m_pds_user
        WHERE
            m_pds_user.pds_user_id = %s
            AND m_pds_user.valid_flg = True;
    """

    # 個人情報一括DLAPI
    # 個人情報一括DL状態管理テーブル登録処理
    MULTI_DOWUNLOAD_STATUS_MANAGE_INSERT_SQL = """
        INSERT
        INTO t_multi_download_status_manage(
            request_no
            , pds_user_id
            , exec_type
            , address_to
            , address_cc
            , exec_status
            , mail_id
            , start_datetime
            , end_datetime
            , tf_operator_id
        )
        VALUES (
            %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
            , %s
        );
    """

    # 個人情報一括DLAPI
    # 個人情報一括DL状態管理取得処理
    MULTI_DOWUNLOAD_TARGET_TRANSACTION_ID_SELECT_SQL = """
        SELECT
            t_multi_download_status_manage.tf_operator_id
            , t_multi_download_status_manage.pds_user_id
            , t_multi_download_target_transaction_id.transaction_id
            , t_multi_download_status_manage.address_to
            , t_multi_download_status_manage.address_cc
        FROM
            t_multi_download_status_manage
            INNER JOIN t_multi_download_target_transaction_id
                ON (
                    t_multi_download_status_manage.request_no = t_multi_download_target_transaction_id.request_no
                    AND t_multi_download_status_manage.pds_user_id = t_multi_download_target_transaction_id.pds_user_id
                )
        WHERE
            t_multi_download_status_manage.request_no = %s
            AND t_multi_download_status_manage.pds_user_id = %s;
    """

    # 個人情報一括DLAPI
    # 個人情報一括DL対象個人情報IDテーブル登録処理
    MULTI_DOWUNLOAD_TARGET_TRANSACTION_ID_BULK_INSERT_SQL = """
        INSERT
        INTO t_multi_download_target_transaction_id(
            request_no
            , pds_user_id
            , transaction_id
        )
        VALUES (
            %s
            , %s
            , %s
        );
    """

    # 個人情報一括DLAPI
    # 個人情報更新処理
    MULTI_DOWUNLOAD_STATUS_MANAGE_WBT_EXEC_UPDATE_SQL = """
        UPDATE
            t_multi_download_status_manage
        SET
            exec_status = %s
        WHERE
            t_multi_download_status_manage.request_no = %s
            AND t_multi_download_status_manage.pds_user_id = %s;
    """

    # 個人情報一括DLAPI
    # 個人情報一括DL状態管理テーブル更新処理
    MULTI_DOWUNLOAD_STATUS_MANAGE_MAIL_ID_UPDATE_SQL = """
        UPDATE
            t_multi_download_status_manage
        SET
            mail_id = %s
        WHERE
            t_multi_download_status_manage.request_no = %s
            AND t_multi_download_status_manage.pds_user_id = %s;
    """

    # 個人情報一括DLAPI
    # 個人情報更新処理
    MULTI_DOWUNLOAD_STATUS_MANAGE_EXIT_UPDATE_SQL = """
        UPDATE
            t_multi_download_status_manage
        SET
            exec_status = %s
            , end_datetime = %s
        WHERE
            t_multi_download_status_manage.request_no = %s;
    """

    # 個人情報一括DLAPI
    # 個人情報取得処理
    USER_PROFILE_MULTI_DOWNLOAD_SELECT_SQL = """
        SELECT
            t_user_profile.transaction_id
            , t_user_profile.user_id
            , t_user_profile.save_datetime
            , t_user_profile.save_data
            , t_user_profile.secure_level
        FROM
            t_user_profile
        WHERE
            t_user_profile.transaction_id IN %s
            AND t_user_profile.valid_flg = %s;
    """

    # 個人情報一括削除API
    # PDSユーザデータ取得処理
    MONGODB_SECRET_NAME_AND_S3_SELECT_SQL = """
        SELECT
            m_pds_user.pds_user_instance_secret_name
            , m_pds_user.tokyo_a_mongodb_secret_name
            , m_pds_user.tokyo_c_mongodb_secret_name
            , m_pds_user.osaka_a_mongodb_secret_name
            , m_pds_user.osaka_c_mongodb_secret_name
            , m_pds_user.s3_image_data_bucket_name
            , m_pds_user.pds_user_name
        FROM
            m_pds_user
        WHERE
            m_pds_user.pds_user_id = %s
            AND m_pds_user.valid_flg = True;
    """

    # 個人情報一括削除API
    # 個人情報取得処理
    USER_PROFILE_TRANSACTION_ID_SELECT_SQL = """
        SELECT
            t_user_profile.transaction_id
            , t_user_profile.json_data_flg
            , t_user_profile.save_data_mongodb_key
        FROM
            t_user_profile
        WHERE
            t_user_profile.transaction_id IN %s
            AND valid_flg = True;
    """

    # 個人情報一括削除API
    # 個人情報バイナリデータ更新処理
    USER_PROFILE_DELETE_BINARY_DATA_MULTI_UPDATE_SQL = """
        UPDATE t_user_profile_binary
        SET
            valid_flg = false
        WHERE
            t_user_profile_binary.transaction_id IN %s;
    """

    # 個人情報一括削除API
    # 個人情報論理削除処理
    USER_PROFILE_DELETE_DATA_MULTI_UPDATE_SQL = """
        UPDATE
            t_user_profile
        SET
            valid_flg = false
        WHERE
            t_user_profile.transaction_id IN %s;
    """

    # 個人情報一括登録バッチ
    # PDSユーザ情報取得処理
    MULTI_CREATE_BATCH_PDS_USER_SELECT_SQL = """
        SELECT
            m_pds_user.pds_user_id
            , m_pds_user.group_id
            , m_pds_user.pds_user_name
            , m_pds_user.pds_user_domain_name
            , m_pds_user.api_key
            , m_pds_user.pds_user_instance_secret_name
            , m_pds_user.s3_image_data_bucket_name
            , m_pds_user.user_profile_kms_id
            , m_pds_user.valid_flg
            , m_pds_user.tokyo_a_mongodb_secret_name
            , m_pds_user.tokyo_c_mongodb_secret_name
            , m_pds_user.osaka_a_mongodb_secret_name
            , m_pds_user.osaka_c_mongodb_secret_name
            , m_pds_user.sales_address
            , m_pds_user.download_notice_address_to
            , m_pds_user.download_notice_address_cc
            , m_pds_user.delete_notice_address_to
            , m_pds_user.delete_notice_address_cc
            , m_pds_user.credential_notice_address_to
            , m_pds_user.credential_notice_address_cc
        FROM
            m_pds_user
        WHERE
            m_pds_user.pds_user_id = %s
            AND m_pds_user.valid_flg = True;
    """

    # 個人情報一括登録バッチ
    # 個人情報取得処理
    MULTI_CREATE_BATCH_USER_PROFILE_SELECT_SQL = """
        SELECT
            t_user_profile.transaction_id
        FROM
            t_user_profile
        WHERE
            t_user_profile.transaction_id IN %s
    """

    # 個人情報一括登録バッチ
    # 個人情報取得処理
    MULTI_CREATE_BATCH_USER_PROFILE_UPDATE_SQL = """
        UPDATE t_user_profile
        SET
            valid_flg = true
        WHERE
            t_user_profile.transaction_id IN %s
            AND t_user_profile.valid_flg = %s;
    """

    # 個人情報バイナリ登録処理
    # 保存画像ID重複チェック処理
    USER_PROFILE_BINARY_UNIQUE_CHECK_SAVE_IMAGE_DATA_ID_SQL = """
        SELECT
            t_user_profile_binary.save_image_data_id
        FROM
            t_user_profile_binary
        WHERE
            t_user_profile_binary.save_image_data_id = %s
        UNION
        SELECT
            t_user_profile_binary_split.save_image_data_id
        FROM
            t_user_profile_binary_split
        WHERE
            t_user_profile_binary_split.save_image_data_id = %s
    """
