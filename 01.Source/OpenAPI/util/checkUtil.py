import re
import json
import regex
from typing import Any


### 未入力判定
def check_require(check_val: Any):
    """
    未入力判定

    Args:
        check_val (Any): チェックしたい変数

    Returns:
        bool: 判定結果
    """
    return check_val is not None and len(str(check_val)) != 0


### 未入力判定
def check_require_tuple_int(check_list: list, idx: int):
    """
    未入力判定

    Args:
        check_int (int): チェックしたい数値列

    Returns:
        bool: 判定結果
    """
    if check_list is None:
        return False

    result_list = [list(tup) for tup in zip(*check_list)]

    return None not in result_list[idx]


### 未入力判定
def check_require_list_str(check_target):
    """
    未入力判定

    Args:
        check_target (str or list): チェック対象

    Returns:
        bool: 判定結果
    """
    if check_target is None:
        return False
    elif type(check_target) is list:
        for check_str in check_target:
            if check_str is None:
                return False
            if len(str(check_str)) == 0:
                return False
        return True
    else:
        if len(check_target) == 0:
            return False
        else:
            return True


### 型判定
def check_type(check_str: str, *type_class: type):
    """
    型判定

    Args:
        check_str (str): チェックしたい文字列
        type_class (type): 型

    Returns:
        bool: 判定結果
    """
    if check_str is None:
        return True

    return type(check_str) in type_class


### 型判定
def check_type_list(check_list: list, *type_class: type):
    """
    型判定

    Args:
        check_list (list): チェックしたい配列
        type_class (type): 型

    Returns:
        bool: 判定結果
    """
    if check_list is None:
        return True

    if type(check_list) is not list:
        return False

    for check_str in check_list:
        if type(check_str) not in type_class:
            return False
    return True


### 型判定
def check_type_list_image(check_target: list, mode: int):
    """
    型判定

    Args:
        check_target (list): チェックしたい配列
        type_class (type): 型
        mode (int): 検証モード（個人情報登録：1、個人情報更新：2）

    Returns:
        bool: 判定結果
    """
    if check_target is None:
        return True

    if mode == 2 and type(check_target) is bool:
        return True

    if type(check_target) is str:
        if len(check_target) == 0:
            return True
        return True

    elif type(check_target) is list:
        for check_str in check_target:
            if mode == 1 and type(check_str) is not str:
                return False
            elif mode == 2 and (check_str is not None and type(check_str) not in (str, bool)):
                return False
        return True

    else:
        return False


### 文字数・桁判定
def check_max_length(check_str: str, max_num: int):
    """
    上限桁数判定

    Args:
        check_str (str): チェックしたい文字列
        max_num (int): 最大桁数

    Returns:
        bool: 判定結果
    """
    if check_str is None:
        return True

    cur_num = len(str(check_str))
    if cur_num == 0:
        return True
    return cur_num <= max_num


def check_min_length(check_str: str, min_num: int):
    """
    下限桁数判定

    Args:
        check_str (str): チェックしたい文字列
        min_num (int): 最小桁数

    Returns:
        bool: 判定結果
    """
    if check_str is None:
        return True

    cur_num = len(str(check_str))
    if cur_num == 0:
        return True
    return cur_num >= min_num


def check_length(check_str: str, length_num: int):
    """
    桁数一致判定

    Args:
        check_str (str): チェックしたい文字列
        max_num (int): チェックしたい桁数

    Returns:
        bool: 判定結果
    """
    if check_str is None:
        return True

    cur_num = len(str(check_str))
    if cur_num == 0:
        return True
    return cur_num == length_num


def check_min_length_list_str(check_target, min_num: int):
    """
    上限桁数判定

    Args:
        check_str (str or list): チェック対象
        min_num (int): 最大桁数

    Returns:
        bool: 判定結果
    """
    if check_target is None:
        return True

    if type(check_target) is list:
        for check_str in check_target:
            if check_str is None:
                continue
            if len(str(check_str)) < min_num:
                return False
        else:
            return True
    else:
        if len(str(check_target)) < min_num:
            return False
        else:
            return True


def check_max_length_list_str(check_target, max_num: int):
    """
    上限桁数判定

    Args:
        check_str (str or list): チェック対象
        max_num (int): 最大桁数

    Returns:
        bool: 判定結果
    """
    if check_target is None:
        return True

    if type(check_target) is list:
        for check_str in check_target:
            if check_str is None:
                continue
            if len(str(check_str)) > max_num:
                return False
        else:
            return True
    else:
        if len(str(check_target)) > max_num:
            return False
        else:
            return True


def check_max_length_list_total_str(check_target, max_num: int):
    """
    上限桁数判定

    Args:
        check_str (str or list): チェック対象
        max_num (int): 最大桁数

    Returns:
        bool: 判定結果
    """
    if check_target is None:
        return True

    total_length = 0
    if type(check_target) is list:
        for check_str in check_target:
            if check_str is None:
                continue
            else:
                total_length += len(str(check_str))
        if total_length > max_num:
            return False
        else:
            return True
    else:
        if len(str(check_target)) > max_num:
            return False
        else:
            return True


def check_max_length_dict_str(check_target, max_num: int):
    """
    上限桁数判定

    Args:
        check_target (str or dict): チェック対象
        max_num (int): 最大桁数

    Returns:
        bool: 判定結果
    """
    if check_target is None:
        return True

    if type(check_target) is dict:
        check_str = (json.dumps(check_target.copy()))
        cur_num = len(str(check_str))
        return cur_num <= max_num
    else:
        cur_num = len(str(check_target))
        return cur_num <= max_num


### 使用可能文字判定
## 汎用値判定
def check_enterable_characters_base64(check_str: str):
    """
    Base64判定

    Args:
        check_str (str): チェックしたい文字列

    Returns:
        bool: 判定結果
    """
    if check_str is None:
        return True

    if type(check_str) is not str:
        return True

    if len(check_str) == 0:
        return True

    base64_reg = re.compile(r'^[a-zA-Z0-9=+/:;,]+$')
    return base64_reg.match(check_str) is not None


def check_enterable_characters_general_purpose_characters(check_str: str):
    """
    汎用文字判定

    Args:
        check_str (str): チェックしたい文字列

    Returns:
        bool: 判定結果
    """
    if check_str is None:
        return True

    if type(check_str) is not str:
        return True

    if len(check_str) == 0:
        return True

    return regex.search(r'^[^a-zA-Zぁ-んァ-ヶ\p{Han}&,.\-・]+$', check_str) is None


def check_file_name_characters(check_sbj: str):
    """
    送信するファイル名判定

    Args:
        check_str (str): チェックしたい文字列

    Returns:
        bool: 判定結果
    """
    if check_sbj is None:
        return True

    if type(check_sbj) is str:
        if len(check_sbj) == 0:
            return True
        return regex.search(r'^[^a-zA-Zぁ-んァ-ヶ\p{Han}&,.\-・]+$', check_sbj) is None

    if type(check_sbj) is list:
        for check_str in check_sbj:
            if check_str is None:
                continue
            if regex.search(r'^[^a-zA-Zぁ-んァ-ヶ\p{Han}&,.\-・]+$', check_str) is None:
                return True
        else:
            return False


def check_secure_level_characters(check_sbj: str):
    """
    セキュリティレベル判定

    Args:
        check_str (str): チェックしたい文字列

    Returns:
        bool: 判定結果
    """
    if check_sbj is None:
        return True

    if type(check_sbj) is str and len(check_sbj) > 0:
        return regex.search(r'^[^a-zA-Z0-9ぁ-んァ-ヶ\p{Han}&,.-・]+$', check_sbj) is None

    if type(check_sbj) is list:
        for check_str in check_sbj:
            if check_str is None and len(str(check_str)) == 0:
                continue
            if regex.search(r'^[^a-zA-Z0-9ぁ-んァ-ヶ\p{Han}&,.-・]+$', check_str) is None:
                return True
        else:
            return False


def check_enterable_characters_code(check_str: str):
    """
    汎用文字判定

    Args:
        check_str (str): チェックしたい文字列

    Returns:
        bool: 判定結果
    """
    if check_str is None:
        return True

    if type(check_str) is not str:
        return True

    if len(check_str) == 0:
        return True

    return re.search(r'^[^a-zA-Z0-9%]+$', check_str) is None


def check_alpha_num_characters(check_str: str):
    """
    汎用文字判定

    Args:
        check_str (str): チェックしたい文字列

    Returns:
        bool: 判定結果
    """
    if check_str is None:
        return True

    if type(check_str) is not str:
        return True

    if len(check_str) == 0:
        return True

    return re.search(r'^[^a-zA-Z0-9]+$', check_str) is None


def check_number(check_str: str):
    if check_str is None:
        return True

    if type(check_str) is not str:
        return True

    if len(check_str) == 0:
        return True

    number_reg = re.compile(r'^[0-9]+$')
    return number_reg.match(check_str) is not None


## システム固有値判定
def check_enterable_characters_access_token(check_str: str):
    """
    アクセストークン判定

    Args:
        check_str (str): チェックしたい文字列

    Returns:
        bool: 判定結果
    """
    if check_str is None:
        return True

    if type(check_str) is not str:
        return True

    if len(check_str) == 0:
        return True

    access_token_reg = re.compile(r'^[a-fA-F0-9]+$')
    return access_token_reg.match(check_str) is not None


def check_enterable_characters_pds_user_id(check_str: str):
    """
    PDSユーザID判定

    Args:
        check_str (str): チェックしたい文字列

    Returns:
        bool: 判定結果
    """
    if check_str is None:
        return True

    if type(check_str) is not str:
        return True

    if len(check_str) == 0:
        return True

    pds_user_id_reg = re.compile(r'^[C0-9]+$')
    return pds_user_id_reg.match(check_str) is not None


def check_enterable_characters_tf_operator_name(check_str: str):
    """
    TFオペレータ名入力可能文字判定

    Args:
        check_str (str): チェックしたい文字列

    Returns:
        bool: 判定結果
    """
    if check_str is None:
        return True

    if type(check_str) is not str:
        return True

    if len(check_str) == 0:
        return True

    tf_operator_name_reg = regex.compile(r'^[a-zA-Z0-9０-９ぁ-んァ-ヶ\p{Han}]+$')
    return tf_operator_name_reg.match(check_str) is not None


def check_enterable_characters_secure_level(check_str: str):
    """
    セキュリティレベル入力可能文字判定

    Args:
        check_str (str): チェックしたい文字列

    Returns:
        bool: 判定結果
    """
    if check_str is None:
        return True

    if type(check_str) is not str:
        return True

    if len(check_str) == 0:
        return True

    tf_secure_level_reg = regex.compile(r'^[a-zA-Z0-9ぁ-んァ-ヶ\p{Han}&,.-・]+$')
    return tf_secure_level_reg.match(check_str) is not None


def check_enterable_characters_file_name(check_str: str):
    """
    tidリストファイル名入力可能文字判定

    Args:
        check_str (str): チェックしたい文字列

    Returns:
        bool: 判定結果
    """
    if check_str is None:
        return True

    if type(check_str) is not str:
        return True

    if len(check_str) == 0:
        return True

    file_name_reg = regex.compile(r'^[a-zA-Z0-9ぁ-んァ-ヶ\p{Han} ,.!@#$%^&*_+\-=\(\)\[\]\{\}]+$')
    return file_name_reg.match(check_str) is not None


### 入力形式判定
def check_time_stamp(check_str: str):
    """
    タイムスタンプ判定

    Args:
        check_str (str): チェックしたい文字列

    Returns:
        bool: 判定決定
    """
    if check_str is None:
        return True

    if type(check_str) is not str:
        return True

    if len(check_str) == 0:
        return True

    time_stamp_reg = re.compile(
        r'^[0-9]{4}/[0-9]{2}/[0-9]{2}\s[0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3}$'
    )
    return time_stamp_reg.match(check_str) is not None


def check_date(check_str: str):
    """
    日付判定

    Args:
        check_str (str): チェックしたい文字列

    Returns:
        bool: 判定決定
    """
    if check_str is None:
        return True

    if type(check_str) is not str:
        return True

    if len(check_str) == 0:
        return True

    date_reg = re.compile(
        r'^[0-9]{4}/[0-9]{2}/[0-9]{2}$'
    )
    return date_reg.match(check_str) is not None


## システム固有値判定
def check_pds_user_id(check_str: str):
    """
    PDSユーザID判定

    Args:
        check_str (str): チェックしたい文字列

    Returns:
        bool: 判定決定
    """
    if check_str is None:
        return True

    if type(check_str) is not str:
        return True

    if len(check_str) == 0:
        return True

    date_reg = re.compile(
        r'^C[0-9]{7}$'
    )
    return date_reg.match(check_str) is not None


# システム固有値判定
def check_tf_operator_id(check_str: str):
    """
    TFオペレーターID入力可能文字判定

    Args:
        check_str (str): チェックしたい文字列

    Returns:
        bool: 判定結果
    """
    if check_str is None:
        return True

    if type(check_str) is not str:
        return True

    if len(check_str) == 0:
        return True

    return re.search(r'[^a-zA-Z0-9_.+-]+', check_str) is None


# システム固有値判定
def check_tf_operator_password(check_str: str):
    """
    TFオペレータパスワード入力可能文字判定

    Args:
        check_str (str): チェックしたい文字列

    Returns:
        bool: 判定結果
    """
    if check_str is None:
        return True

    if type(check_str) is not str:
        return True

    if len(check_str) == 0:
        return True

    return re.search(r'[^a-zA-Z0-9!@#$%^&*()_+-=\[\]{}|]+', check_str) is None


# システム固有値判定
def check_number_of_character_types(check_str: str):
    """
    英大文字、英小文字、数字、記号のうち３種類以上が使用されているか判定

    Args:
        check_str (str): チェックしたい文字列
    """
    if type(check_str) is not str:
        return True
    if len(check_str) == 0:
        return True
    character_type = 0
    if re.search(r'[a-z]', check_str) is not None:
        character_type += 1
    if re.search(r'[A-Z]', check_str) is not None:
        character_type += 1
    if re.search(r'[0-9]', check_str) is not None:
        character_type += 1
    if re.search(r'[!@#$%^&*()_+\-=\[\]{}|]', check_str) is not None:
        character_type += 1
    return character_type >= 3


# システム固有値判定
def check_pds_user_domain_name(check_str: str):
    """
    PDSユーザドメイン名入力規則判定

    Args:
        check_str (str): チェックしたい文字列

    Returns:
        bool: 判定結果
    """
    if check_str is None:
        return True

    if type(check_str) is not str:
        return True

    if len(check_str) == 0:
        return True

    pds_user_domain_name_reg = re.compile(
        r'^[a-z][a-z0-9\-_]{4,19}$'
    )
    return pds_user_domain_name_reg.match(check_str) is not None


def check_multi_delete_agreement_str(check_str: str):
    """
    一括削除同意テキスト入力規則判定

    Args:
        check_str (str): チェックしたい文字列

    Returns:
        bool: 判定結果
    """
    if check_str is None:
        return True

    if type(check_str) is not str:
        return True

    if len(check_str) == 0:
        return True

    pds_user_domain_name_reg = re.compile(
        r'^削除する$'
    )
    return pds_user_domain_name_reg.match(check_str) is not None


# システム固有値判定
def check_alpha_num(check_str: str):
    """
    トランザクションID入力可能文字判定

    Args:
        check_str (str): チェックしたい文字列

    Returns:
        bool: 判定結果
    """
    if check_str is None:
        return True

    if type(check_str) is not str:
        return True

    if len(check_str) == 0:
        return True

    return re.search(r'[^a-zA-Z0-9]+', check_str) is None


def check_alpha_num_pds_public_key(check_str: str):
    """
    PDSユーザ公開鍵入力可能文字判定

    Args:
        check_str (str): チェックしたい文字列

    Returns:
        bool: 判定結果
    """
    if check_str is None:
        return True

    if type(check_str) is not str:
        return True

    if len(check_str) == 0:
        return True

    return re.search(r'[^a-zA-Z0-9+/=]+', check_str) is None


def check_mail_address(check_str: str):
    """
    メールアドレス(単)入力規則判定

    Args:
        check_str (str): チェックしたい文字列

    Returns:
        bool: 判定結果
    """
    if check_str is None:
        return True

    if type(check_str) is not str:
        return True

    if len(check_str) == 0:
        return True

    mail_address_reg = re.compile(
        r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    )
    return mail_address_reg.match(check_str) is not None


def check_multi_mail_address(check_str: str):
    """
    メールアドレス(複)入力規則判定

    Args:
        check_str (str): チェックしたい文字列

    Returns:
        bool: 判定結果
    """
    if check_str is None:
        return True

    if type(check_str) is not str:
        return True

    if len(check_str) == 0:
        return True

    multi_mail_address_reg = re.compile(
        r'^([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)+(;[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)*$'
    )
    return multi_mail_address_reg.match(check_str) is not None


def check_search_mode(check_str: str):
    """
    検索モード入力可能文字判定

    Args:
        check_str (str): チェックしたい文字列

    Returns:
        bool: 判定結果
    """
    if check_str is None:
        return True

    if type(check_str) is not str:
        return True

    if len(check_str) == 0:
        return True

    return re.search(r'[^前方一致|後方一致|部分一致]+', check_str) is None


def check_image(check_sbj: str, mode: int):
    """
    保存したいバイナリデータ入力可能文字判定

    Args:
        check_str (str): チェックしたい文字列か配列
        mode (int): 検証モード（個人情報登録：1、個人情報更新：2）

    Returns:
        bool: 判定結果
    """
    if check_sbj is None:
        return True

    if mode == 2 and type(check_sbj) is bool:
        return True

    if type(check_sbj) is str:
        if len(check_sbj) == 0:
            return True
        return re.search(r'[^a-zA-Z0-9+/=]+', check_sbj) is None

    if type(check_sbj) is list:
        for check_str in check_sbj:
            if mode == 1 and type(check_str) is str and re.search(r'[^a-zA-Z0-9+/=]+', check_str) is not None:
                return False
            elif mode == 2:
                if type(check_str) is str and re.search(r'[^a-zA-Z0-9+/=]+', check_str) is not None:
                    return False
                elif check_str is not None and type(check_str) not in (str, bool):
                    return False
        else:
            return True
    else:
        return True


def check_image_hash(check_sbj: str):
    """
    保存されたバイナリデータハッシュ値入力可能文字判定

    Args:
        check_str (str): チェックしたい文字列か配列

    Returns:
        bool: 判定結果
    """
    if check_sbj is None:
        return True

    if type(check_sbj) is str:
        if len(check_sbj) == 0:
            return True
        return re.search(r'[^a-zA-Z0-9]+', check_sbj) is None

    if type(check_sbj) is list:
        for check_str in check_sbj:
            if type(check_str) is str and re.search(r'[^a-zA-Z0-9]+', check_str) is None:
                return True
        else:
            return False


def check_image_hash_to(check_sbj: str, mode: int):
    """
    保存したいバイナリデータハッシュ値入力可能文字判定

    Args:
        check_str (str): チェックしたい文字列か配列
        mode (int): 検証モード（個人情報登録：1、個人情報更新：2）

    Returns:
        bool: 判定結果
    """
    if check_sbj is None:
        return True

    if mode == 2 and type(check_sbj) is bool:
        return True

    if type(check_sbj) is str:
        if len(check_sbj) == 0:
            return True
        return re.search(r'[^a-zA-Z0-9]+', check_sbj) is None

    if type(check_sbj) is list:
        for check_str in check_sbj:
            if mode == 1 and type(check_str) is str and re.search(r'[^a-zA-Z0-9]+', check_str) is not None:
                return False
            elif mode == 2:
                if type(check_str) is str and re.search(r'[^a-zA-Z0-9]+', check_str) is not None:
                    return False
                elif check_str is not None and type(check_str) not in (str, bool):
                    return False
        else:
            return True
    else:
        return True


# システム固有値判定
def check_pds_user_public_key_idx(check_text: int):
    """
    PDSユーザ公開鍵インデックス入力可能文字判定

    Args:
        check_text (int): チェックしたいテキスト

    Returns:
        bool: 判定結果
    """
    if check_text is None:
        return True

    if type(check_text) is not str:
        return True

    if len(check_text) == 0:
        return True

    return re.search(r'[^0-9]+', str(check_text)) is None


# システム固有値判定
def check_api_type(check_text: str):
    """
    API種別入力可能文字判定

    Args:
        check_text (str): チェックしたいテキスト

    Returns:
        bool: 判定結果
    """
    if check_text is None:
        return True

    if type(check_text) is not str:
        return True

    if len(check_text) == 0:
        return True

    return re.search(r'[^1-9]+', check_text) is None


# システム固有値判定
def check_repository_type(check_text: str):
    """
    種別入力可能文字判定

    Args:
        check_text (str): チェックしたいテキスト

    Returns:
        bool: 判定結果
    """
    if check_text is None:
        return True

    if type(check_text) is not str:
        return True

    if len(check_text) == 0:
        return True

    return re.search(r'[^0-2]+', check_text) is None


def correlation_check_date(from_date: str, to_date: str):
    """
    日付の相関チェック

    Args:
        from_date (str): 形式は「yyyy/MM/dd」
        to_date (str): 形式は「yyyy/MM/dd」
    """
    if from_date is None or to_date is None:
        return True

    if type(from_date) is not str or type(to_date) is not str:
        return True

    if len(from_date) == 0 or len(to_date) == 0:
        return True

    return from_date <= to_date


def correlation_check_tf_operator_id(id_1: str, id_2: str):
    """
    日付の相関チェック

    Args:
        from_date (str): 形式は「yyyy/MM/dd」
        to_date (str): 形式は「yyyy/MM/dd」
    """
    if id_1 is None or id_2 is None:
        return True

    return id_1 != id_2
