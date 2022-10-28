import aioboto3
import re

import util.logUtil as logUtil
from const.messageConst import MessageConstClass


class s3AioUtilClass:
    def __init__(self, logger, bucket_name: str):
        self.logger = logger
        self.bucket_name = bucket_name

    def check_file(self, file_prefix: str, is_allowed_zero_byte: bool):
        """
        ファイル存在チェック

        Args:
            file_prefix (str): ファイル名
            is_allowed_zero_byte (bool): ゼロバイト許容フラグ

        Returns:
            dict: 処理結果
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=file_prefix
            )
            contents = response["Contents"]
            for content in contents:
                if content.get("Key") == file_prefix:
                    if not is_allowed_zero_byte and content.get("Size") == 0:
                        self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990023"]["logMessage"], self.bucket_name, file_prefix))
                        return {
                            "result": False,
                            "errorInfo": {
                                "errorCode": "990023",
                                "message": logUtil.message_build(MessageConstClass.ERRORS["990023"]["message"], "990023")
                            }
                        }
                    return {
                        "result": True
                    }

            self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990023"]["logMessage"], self.bucket_name, file_prefix))
            return {
                "result": False,
                "errorInfo": {
                    "errorCode": "990023",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["990023"]["message"], "990023")
                }
            }
        except Exception:
            return {
                "result": False,
                "errorInfo": {
                    "errorCode": "990023",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["990023"]["message"], "990023")
                }
            }

    def check_zip_file(self, file_prefix: str, file_suffix: str):
        """
        ファイル存在チェック

        Args:
            file_prefix (str): プレフィックス
            file_suffix (str): サフィックス

        Returns:
            dict: 処理結果
        """
        try:
            for result_count in range(5):
                try:
                    # フォルダ情報取得
                    response = self.s3_client.list_objects_v2(
                        Bucket=self.bucket_name,
                        Prefix=file_prefix
                    )
                    break
                except Exception:
                    if result_count == 4:
                        self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990023"]["logMessage"], self.bucket_name, file_prefix))
                        return {
                            "result": False,
                            "errorInfo": {
                                "errorCode": "990023",
                                "message": logUtil.message_build(MessageConstClass.ERRORS["990023"]["message"], "990023")
                            }
                        }

            contents = response["Contents"]
            obj_list = list(filter(lambda x: re.compile(file_suffix).search(x["Key"]), contents))
            if len(obj_list) == 0:
                # フォルダが空の場合エラー情報作成
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990023"]["logMessage"], self.bucket_name, file_prefix))
                return {
                    "result": False,
                    "errorInfo": {
                        "errorCode": "990023",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["990023"]["message"], "990023")
                    }
                }
            elif len(obj_list) > 1:
                # フォルダに2つ以上のファイルが存在する場合エラー情報作成
                self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990023"]["logMessage"], self.bucket_name, file_prefix))
                return {
                    "result": False,
                    "errorInfo": {
                        "errorCode": "990023",
                        "message": logUtil.message_build(MessageConstClass.ERRORS["990023"]["message"], "990023")
                    }
                }
            else:
                if obj_list[0].get("Size") == 0:
                    # ファイルサイズが0バイトの場合エラー情報作成
                    self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990023"]["logMessage"], self.bucket_name, file_prefix))
                    return {
                        "result": False,
                        "errorInfo": {
                            "errorCode": "990023",
                            "message": logUtil.message_build(MessageConstClass.ERRORS["990023"]["message"], "990023")
                        }
                    }
                else:
                    return {
                        "result": True,
                        "key": obj_list[0].get("Key")
                    }

        except Exception:
            return {
                "result": False,
                "errorInfo": {
                    "errorCode": "990023",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["990023"]["message"], "990023")
                }
            }

    def put_file(self, file_name: str, data: bytes):
        """
        ファイルアップロード

        Args:
            file_name (str): ファイル名
            data (bytes): ファイル内容
        """
        try:
            self.s3_client.put_object(Bucket=self.bucket_name, Key=file_name, Body=data)
            return True
        except Exception:
            return False

    async def async_put_file(self, file_name: str, data: bytes):
        """
        ファイルアップロード(非同期用)

        Args:
            file_name (str): ファイル名
            data (bytes): ファイル内容
        """
        try:
            session = aioboto3.Session()
            async with session.client(service_name="s3") as s3:
                try:
                    await s3.put_object(Bucket=self.bucket_name, Key=file_name, Body=data)
                    return True
                except Exception:
                    return False
        except Exception:
            return False

    def deleteFile(self, file_name: str):
        """
        ファイル削除

        Args:
            file_name (str): ファイル名
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_name)
            return True
        except Exception:
            return False

    async def get_file(self, file_name: str):
        """
        ファイル取得処理

        Args:
            file_name (str): ファイルパス
        """
        session = aioboto3.Session()
        async with session.client(service_name="s3") as s3:
            try:
                response = await s3.get_object(Bucket=self.bucket_name, Key=file_name)
                return await response["Body"].read()
            except Exception as e:
                raise e

    def get_zip_file(self, file_path: str, file_name: str):
        """
        Zipファイルダウンロード処理

        Args:
            file_path (str): ファイルパス
            file_name (str): ファイル名

        Returns:
            dict: 処理結果
        """
        try:
            for result_count in range(5):
                try:
                    self.s3_client.download_file(self.bucket_name, file_path, file_name)
                    break
                except Exception:
                    if result_count == 4:
                        self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990024"]["logMessage"], self.bucket_name, file_path))
                        return {
                            "result": False,
                            "errorInfo": {
                                "errorCode": "990024",
                                "message": logUtil.message_build(MessageConstClass.ERRORS["990024"]["message"], "990024")
                            }
                        }
            return {
                "result": True
            }
        except Exception:
            self.logger.error(logUtil.message_build(MessageConstClass.ERRORS["990024"]["logMessage"], self.bucket_name, file_path))
            return {
                "result": False,
                "errorInfo": {
                    "errorCode": "990024",
                    "message": logUtil.message_build(MessageConstClass.ERRORS["990024"]["message"], "990024")
                }
            }
