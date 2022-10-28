import hashlib
from logging import Logger


# 暗号化・複合化共通処理
# 例：Sha256の暗号化などを記載

class CryptUtilClass:

    def __init__(self, logger):
        self.logger: Logger = logger

    def hash_password(self, password: str):
        """
        パスワードハッシュ化

        Args:
            password (str): ハッシュ化したいパスワード

        Returns:
            str: ハッシュ化されたパスワード
        """
        return hashlib.sha512(password.encode()).hexdigest()
