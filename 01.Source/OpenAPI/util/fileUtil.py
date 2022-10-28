import io


class NoHeaderOneItemCsvStringClass:
    """
    単一項目のCSV文字列クラス（ヘッダなし）
    """
    def __init__(self, list_string: list):
        """
        コンストラクタ

        Args:
            list_string (list): CSVにしたい配列（文字列）
        """
        self.csv_string = self.__formatCsv(list_string)

    def __formatCsv(self, list_string: list):
        """
        CSVフォーマット整形（ヘッダなし、単一項目）

        Args:
            list_string (list): CSVにしたい配列（文字列）

        Returns:
            str: CSV文字列
        """
        csv_string = "\r\n".join(list_string)
        return csv_string

    def get_csv_string(self):
        """
        CSV文字列取得

        Returns:
            str: CSV文字列
        """
        return self.csv_string


class CsvStreamClass:
    """
    単一項目のCSVファイルクラス（ヘッダなし）
    """
    def __init__(self, csv_string: NoHeaderOneItemCsvStringClass):
        """
        コンストラクタ

        Args:
            csv_string (NoHeaderOneItemCsvStringClass): CSV文字列クラス
        """
        self.csv_string = csv_string
        self.csv_binary = self.__encode_csv(csv_string)
        self.temp_csv = self.__create_temp_csv(self.csv_binary)

    def get_temp_csv(self):
        """
        CSVストリーム取得

        Returns:
            Object: CSVストリーム
        """
        return self.temp_csv

    def __create_temp_csv(self, csv_binary: bytes):
        """
        CSVストリーム作成

        Args:
            csv_binary (bytes): エンコードしたCSV文字列

        Returns:
            Object: CSVストリーム
        """
        temp_file_object = io.BytesIO(csv_binary)
        return temp_file_object

    def __encode_csv(self, csv_string: NoHeaderOneItemCsvStringClass):
        """
        CSV文字列エンコード

        Args:
            csv_string (NoHeaderOneItemCsvStringClass): CSV文字列クラス

        Returns:
            bytes: エンコードしたCSV文字列
        """
        string = csv_string.get_csv_string()
        csv_binary = string.encode("utf_8_sig")
        return csv_binary


class BinaryStreamClass:
    """
    分割バイナリデータファイルクラス
    """
    def __init__(self, binary_data: bytes):
        """
        コンストラクタ

        Args:
            binary_data (bytes): CSV文字列クラス
        """
        self.temp_binary = self.__create_temp_binary(binary_data)

    def get_temp_binary(self):
        """
        CSVストリーム取得

        Returns:
            Object: CSVストリーム
        """
        return self.temp_binary

    def __create_temp_binary(self, csv_binary: bytes):
        """
        CSVストリーム作成

        Args:
            csv_binary (bytes): エンコードしたCSV文字列

        Returns:
            Object: CSVストリーム
        """
        temp_file_object = io.BytesIO(csv_binary)
        return temp_file_object


class HeaderDictItemCsvStringClass:
    """
    複数項目のCSV文字列クラス（ヘッダあり）
    """
    def __init__(self, header_list: list, dict_list: list, none_replacement_string: str = ""):
        """
        コンストラクタ

        Args:
            header_list (list): CSVのヘッダにしたい配列（文字列）
            dict_list (list): CSVの内容にしたい辞書を配列にしたもの
            none_replacement_string (str): 項目が見つからなかった場合 or Noneを置換する文字列
        """
        self.none_replacement_string = none_replacement_string
        self.csv_string = self.__formatHeader(header_list)
        self.__formatCsv(header_list, dict_list)

    def __formatHeader(self, header_list: list):
        """
        CSVヘッダフォーマット整形

        Args:
            header_list (list): CSVのヘッダにしたい配列（文字列）

        Returns:
            str: CSV文字列
        """
        csv_string = ",".join(header_list)
        return csv_string

    def __formatCsv(self, header_list: list, dict_list: list):
        """
        CSVフォーマット整形（ヘッダなし、単一項目）

        Args:
            header_list (list): CSVのヘッダにしたい配列
            dict_list (list): CSVの内容にしたい辞書を配列にしたもの

        Returns:
            str: CSV文字列
        """
        for str_dict in dict_list:
            # CSV改行の挿入
            self.csv_string = self.csv_string + "\r\n"
            for idx, header in enumerate(header_list):
                # CSV内容の挿入
                if not str_dict.get(header):
                    self.csv_string = self.csv_string + self.none_replacement_string
                elif str_dict[header] is None:
                    self.csv_string = self.csv_string + self.none_replacement_string
                else:
                    self.csv_string = self.csv_string + str(str_dict[header])

                # CSV区切り文字の挿入
                if idx != len(header_list) - 1:
                    self.csv_string = self.csv_string + ","

    def get_csv_string(self):
        """
        CSV文字列取得

        Returns:
            str: CSV文字列
        """
        return self.csv_string


class HeaderDictItemCsvStreamClass:
    """
    複数項目のCSVファイルクラス（ヘッダあり）
    """
    def __init__(self, csv_string: HeaderDictItemCsvStringClass):
        """
        コンストラクタ

        Args:
            csv_string (HeaderDictItemCsvStringClass): CSV文字列クラス
        """
        self.csv_string = csv_string
        self.csv_binary = self.__encode_csv(csv_string)
        self.temp_csv = self.__create_temp_csv(self.csv_binary)

    def get_temp_csv(self):
        """
        CSVストリーム取得

        Returns:
            Object: CSVストリーム
        """
        return self.temp_csv

    def __create_temp_csv(self, csv_binary: bytes):
        """
        CSVストリーム作成

        Args:
            csv_binary (bytes): エンコードしたCSV文字列

        Returns:
            Object: CSVストリーム
        """
        temp_file_object = io.BytesIO(csv_binary)
        return temp_file_object

    def __encode_csv(self, csv_string: HeaderDictItemCsvStringClass):
        """
        CSV文字列エンコード

        Args:
            csv_string (HeaderDictItemCsvStringClass): CSV文字列クラス

        Returns:
            bytes: エンコードしたCSV文字列
        """
        string = csv_string.get_csv_string()
        csv_binary = string.encode("utf_8_sig")
        return csv_binary


class HeaderListItemCsvStringClass:
    """
    複数項目のCSV文字列クラス（ヘッダあり）
    """
    def __init__(self, header_list: list, tuple_list: list):
        """
        コンストラクタ

        Args:
            header_list (list): CSVのヘッダにしたい配列（文字列）
            tuple_list (list): CSVの内容にしたいタプルの配列
        """
        self.csv_string = self.__formatHeader(header_list)
        self.__formatCsv(tuple_list)

    def __formatHeader(self, header_list: list):
        """
        CSVヘッダフォーマット整形

        Args:
            header_list (list): CSVのヘッダにしたい配列（文字列）

        Returns:
            str: CSV文字列
        """
        csv_string = ",".join(header_list)
        return csv_string

    def __formatCsv(self, item_list: list):
        """
        CSVフォーマット整形

        Args:
            item_list (list): CSVの内容にしたい2次元配列

        Returns:
            str: CSV文字列
        """
        for row_data in item_list:
            # CSV改行の挿入
            self.csv_string = self.csv_string + "\r\n"
            for idx, item in enumerate(row_data):
                # CSV内容の挿入
                self.csv_string = self.csv_string + str(item)

                # CSV区切り文字の挿入
                if idx != len(row_data) - 1:
                    self.csv_string = self.csv_string + ","

    def get_csv_string(self):
        """
        CSV文字列取得

        Returns:
            str: CSV文字列
        """
        return self.csv_string


class HeaderListItemCsvStreamClass:
    """
    複数項目のCSVファイルクラス（ヘッダあり）
    """
    def __init__(self, csv_string: HeaderListItemCsvStringClass):
        """
        コンストラクタ

        Args:
            csv_string (HeaderDictItemCsvStringClass): CSV文字列クラス
        """
        self.csv_string = csv_string
        self.csv_binary = self.__encode_csv(csv_string)
        self.temp_csv = self.__create_temp_csv(self.csv_binary)

    def get_temp_csv(self):
        """
        CSVストリーム取得

        Returns:
            Object: CSVストリーム
        """
        return self.temp_csv

    def __create_temp_csv(self, csv_binary: bytes):
        """
        CSVストリーム作成

        Args:
            csv_binary (bytes): エンコードしたCSV文字列

        Returns:
            Object: CSVストリーム
        """
        temp_file_object = io.BytesIO(csv_binary)
        return temp_file_object

    def __encode_csv(self, csv_string: HeaderDictItemCsvStringClass):
        """
        CSV文字列エンコード

        Args:
            csv_string (HeaderDictItemCsvStringClass): CSV文字列クラス

        Returns:
            bytes: エンコードしたCSV文字列
        """
        string = csv_string.get_csv_string()
        csv_binary = string.encode("utf_8_sig")
        return csv_binary
