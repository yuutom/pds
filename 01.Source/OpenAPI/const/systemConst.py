class SystemConstClass:
    # システム共通定数

    # システム名
    SYSTEM_NAME = "PDS"

    ### AWS関連の定数
    ## リージョンごとに変更する必要がある？（リージョン名）
    AWS_CONST = {
        "REGION": "ap-northeast-1"
    }

    ### 共通DB関連の定数
    PDS_COMMON_DB_SECRET_INFO = {
        "SECRET_NAME": "pds-sm-rds-common-dev"
    }
    PDS_COMMON_DB_NAME = "pds_common_db"
    PDS_USER_DB_NAME = "pds_user_db"

    ### KMS関連の定数
    ## TODO:リージョンごとに変更する必要がある？（アクセスできるロールの設定）
    # TODO:アカウント設定が必要
    KMS_POLICY_TEMP = {
        "Id": "key-consolepolicy-3",
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "Enable IAM User Permissions",
                "Effect": "Allow",
                "Principal": {
                    "AWS": "arn:aws:iam::851691524979:root"
                },
                "Action": "kms:*",
                "Resource": "*"
            },
            {
                "Sid": "Allow access for Key Administrators",
                "Effect": "Allow",
                "Principal": {
                    "AWS": "arn:aws:iam::851691524979:user/t.ii@lincrea.co.jp"
                },
                "Action": [
                    "kms:Create*",
                    "kms:Describe*",
                    "kms:Enable*",
                    "kms:List*",
                    "kms:Put*",
                    "kms:Update*",
                    "kms:Revoke*",
                    "kms:Disable*",
                    "kms:Get*",
                    "kms:Delete*",
                    "kms:TagResource",
                    "kms:UntagResource",
                    "kms:ScheduleKeyDeletion",
                    "kms:CancelKeyDeletion"
                ],
                "Resource": "*"
            },
            {
                "Sid": "Allow use of the key",
                "Effect": "Allow",
                "Principal": {
                    "AWS": [
                        "arn:aws:iam::851691524979:user/t.ii@lincrea.co.jp",
                        "arn:aws:iam::851691524979:role/service-role/putS3-role-zzxuk077"
                    ]
                },
                "Action": [
                    "kms:Encrypt",
                    "kms:Decrypt",
                    "kms:ReEncrypt*",
                    "kms:GenerateDataKey*",
                    "kms:DescribeKey"
                ],
                "Resource": "*"
            },
            {
                "Sid": "Allow attachment of persistent resources",
                "Effect": "Allow",
                "Principal": {
                    "AWS": [
                        "arn:aws:iam::851691524979:user/t.ii@lincrea.co.jp",
                        "arn:aws:iam::851691524979:role/service-role/putS3-role-zzxuk077"
                    ]
                },
                "Action": [
                    "kms:CreateGrant",
                    "kms:ListGrants",
                    "kms:RevokeGrant"
                ],
                "Resource": "*",
                "Condition": {
                    "Bool": {
                        "kms:GrantIsForAWSResource": "true"
                    }
                }
            }
        ]
    }

    ## TODO:リージョンごとに変更する必要がある？（アクセスできるロールの設定）
    # TODO:アカウント設定が必要
    KMS_POLICY_TEMP_REPLICA = {
        "Id": "key-consolepolicy-3",
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "Enable IAM User Permissions",
                "Effect": "Allow",
                "Principal": {
                    "AWS": "arn:aws:iam::851691524979:root"
                },
                "Action": "kms:*",
                "Resource": "*"
            },
            {
                "Sid": "Allow access for Key Administrators",
                "Effect": "Allow",
                "Principal": {
                    "AWS": "arn:aws:iam::851691524979:user/t.ii@lincrea.co.jp"
                },
                "Action": [
                    "kms:Create*",
                    "kms:Describe*",
                    "kms:Enable*",
                    "kms:List*",
                    "kms:Put*",
                    "kms:Update*",
                    "kms:Revoke*",
                    "kms:Disable*",
                    "kms:Get*",
                    "kms:Delete*",
                    "kms:TagResource",
                    "kms:UntagResource",
                    "kms:ScheduleKeyDeletion",
                    "kms:CancelKeyDeletion"
                ],
                "Resource": "*"
            },
            {
                "Sid": "Allow use of the key",
                "Effect": "Allow",
                "Principal": {
                    "AWS": [
                        "arn:aws:iam::851691524979:user/t.ii@lincrea.co.jp",
                        "arn:aws:iam::851691524979:role/service-role/putS3-role-zzxuk077"
                    ]
                },
                "Action": [
                    "kms:Encrypt",
                    "kms:Decrypt",
                    "kms:ReEncrypt*",
                    "kms:GenerateDataKey*",
                    "kms:DescribeKey"
                ],
                "Resource": "*"
            },
            {
                "Sid": "Allow attachment of persistent resources",
                "Effect": "Allow",
                "Principal": {
                    "AWS": [
                        "arn:aws:iam::851691524979:user/t.ii@lincrea.co.jp",
                        "arn:aws:iam::851691524979:role/service-role/putS3-role-zzxuk077"
                    ]
                },
                "Action": [
                    "kms:CreateGrant",
                    "kms:ListGrants",
                    "kms:RevokeGrant"
                ],
                "Resource": "*",
                "Condition": {
                    "Bool": {
                        "kms:GrantIsForAWSResource": "true"
                    }
                }
            }
        ]
    }

    KMS_REPLICA_REGION = "ap-northeast-3"

    ### アクセストークン関連の定数
    ACCESS_TOKEN_CLOSED_EXPIRE_MINUTES = 30
    ACCESS_TOKEN_PUBLIC_EXPIRE_MINUTES = 1
    ACCESS_TOKEN_ALGORISHMS = "HS256"

    ### PDSユーザ登録
    GROUP_ID = "G0000001"

    ### CloudFormation関連の定数
    ## リージョンごとに変更する必要がある？（バケットはリージョンに紐づく？）
    # CFN_TEMPLATE_BUCKET_NAME="pds-cfn-template-bucket"
    # CFN_PREFIX="/pds-user-resource/pds-user-resource.yaml"
    CFN_TEMPLATE_BUCKET_NAME = "pds-cfn-template-bucket-dev"
    CFN_PREFIX = "/pds-user-resource/pds-user-resource.yaml"

    # アクセス履歴退避ファイル格納先バケット
    # ACCESS_RECORD_EVACUATE_BUCKET = "pds_api_history_backup_bucket"
    # TODO：バケットを新しく作成するのがもったいないのでCFNを間借りしてます
    ACCESS_RECORD_EVACUATE_BUCKET = "pds-cfn-template-bucket-dev"
    ACCESS_RECORD_EVACUATE_FILE_PREFIX = "t_api_history_backup_"
    ACCESS_RECORD_EVACUATE_FILE_EXTENSION = ".csv"

    # 個人情報検索
    # TIDリストファイル
    TID_LIST_FILE_PREFIX = "tidList_"
    TID_LIST_FILE_EXTENSION = ".csv"

    # MongoDB接続先確認用
    REGION = {
        "TOKYO": "ap-northeast-1",
        "OSAKA": "ap-northeast-3"
    }

    # 検索条件
    MATCH_MODE = {
        "PREFIX": "前方一致",
        "BACKWARD": "後方一致",
        "PARTIAL": "部分一致"
    }

    # SQSのURL
    SQS_QUEUE_NAME = "transactionDeleteBatchQueue"
    SQS_MULTI_DOWNLOAD_QUEUE_NAME = "multiDownloadBatchQueue"
    SQS_MULTI_DELETE_QUEUE_NAME = "transactionDeleteBatchQueue"

    # 分割バイトサイズ
    SPLIT_BYTE_CHUNK_SIZE = 2097152
    CHUNK_SIZE = 2097152

    # 個人情報一括DL処理タイプ
    USER_PROFILE_DL_EXEC_TYPE = "1"

    # 個人情報一括DL実行ステータス
    USER_PROFILE_DL_EXEC_GET_DATA_STATUS = "1"
    USER_PROFILE_DL_EXEC_WBT_EXEC_STATUS = "2"
    USER_PROFILE_DL_EXEC_END_STATUS = "3"
    USER_PROFILE_DL_EXEC_ERROR_STATUS = "9"

    # 個人情報一括DLファイル分割バイトサイズ
    USER_PROFILE_DL_FILE_CHUNK_SIZE = 2147483648

    # 個人情報一括登録バッチバケット
    USER_PROFILE_MULTI_CREATE_BUCKET = "multi-register-bucket-dev"
    USER_PROFILE_MULTI_CREATE_FILE_REGIX = r'\.zip$'

    # 個人情報一括登録ファイルサイズ
    USER_PROFILE_BINARY_FILE_SOLO = 10485760
    USER_PROFILE_BINARY_FILE_TOTAL = 104857600

    # 個人情報バイナリ登録上限ファイルサイズ
    USER_PROFILE_BINARY_FILE_BASE64_SOLO = 14680064
    USER_PROFILE_BINARY_FILE_BASE64_TOTAL = 146800640

    # 作成する負荷テスト用個人情報の量
    STRESS_TEST_USER_PROFILE_LOOP = 2

    # CloudFormationスタック状態確認
    CFN_ROLLBACK_STACK_STATUS = "ROLLBACK_COMPLETE"
    CFN_DELETE_STACK_STATUS = "DELETE_COMPLETE"

    # CloudFormationのStackSetの実施先
    CFN_STACK_SET_REGIONS = [REGION["TOKYO"], REGION["OSAKA"]]
    CFN_STACK_SET_SUCCESS = "SUCCEEDED"
