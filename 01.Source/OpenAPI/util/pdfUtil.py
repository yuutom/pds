from logging import Logger
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, portrait
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
import io

import util.commonUtil as commonUtil

# フォント登録
pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))
pdfmetrics.registerFont(TTFont('IPAGothic', 'resource/font/ipaexg00401/ipaexg.ttf'))
pdfmetrics.registerFont(TTFont('BIZUDGothic-R', 'resource/font/BIZUDGothic-Regular.ttf'))


class PdfUtilClass():
    def __init__(self, logger: Logger) -> None:
        self.logger: Logger = logger
        self.pdf_file = io.BytesIO()
        self.page = canvas.Canvas(self.pdf_file, pagesize=portrait(A4))
        # self.page = canvas.Canvas(self.pdf_file, pagesize=landscape(A4))
        self.font_size = 10
        self.margin = 2
        self.delete_base_line = 75
        self.delete_base_line = 150
        self.half_next_row_count = 27
        self.next_page_row = 54
        self.page_no = 1
        self.__set_font()
        self.__get_page_size()

    def __set_font(self):
        # self.page.setFont("HeiseiKakuGo-W5", self.font_size)
        # self.page.setFont("IPAGothic", self.font_size)
        self.page.setFont("BIZUDGothic-R", self.font_size)

    def __get_page_size(self):
        page_size = self.page._pagesize
        self.max_width = page_size[0]
        self.max_height = page_size[1]

    def next_page_check(self, write_row_index: int):
        if write_row_index >= self.next_page_row:
            self.page.drawCentredString(x=self.max_width / 2, y=self.max_height - ((self.font_size + self.margin) * self.next_page_row) - self.delete_base_line, text="(次のページに続く)")
            self.page.drawCentredString(x=self.max_width / 2, y=((self.font_size + self.margin) * 1) - 5, text=str(self.page_no) + "ページ")
            self.page.showPage()
            self.__set_font()
            write_row_index = 1
            self.page_no += 1
        return write_row_index

    def create_pdf(
        self,
        pds_user_name: str,
        pds_user_id: str,
        transaction_id_setting_str: str,
        transaction_id_setting_file_str: str,
        user_id_str: str,
        user_id_match_mode: str,
        data_json_key: str,
        data_str: str,
        data_match_mode: str,
        image_hash: str,
        from_date: str,
        to_date: str,
        save_data_format_str: str,
        delete_count: int,
        file_name: str
    ):
        write_row_index = 1
        self.page.drawRightString(x=self.max_width - 10, y=self.max_height - ((self.font_size + self.margin) * 1) - 5, text=commonUtil.get_str_date())
        self.page.drawCentredString(x=self.max_width / 2, y=self.max_height - ((self.font_size + self.margin) * 1) - 30, text="一括削除完了レポート")
        self.page.drawString(x=30, y=self.max_height - ((self.font_size + self.margin) * 1) - self.delete_base_line, text="平素よりPDSをご利用いただきありがとうございます")
        pds_user_name_str = "{pdsUserName}様よりご依頼のあった下記の条件に当てはまる個人情報を一括削除しましたことをご報告致します".format(pdsUserName=pds_user_name)
        if len(pds_user_name_str) >= 54:
            self.page.drawString(x=30, y=self.max_height - ((self.font_size + self.margin) * 2) - self.delete_base_line, text=pds_user_name_str[:54])
            self.page.drawString(x=30, y=self.max_height - ((self.font_size + self.margin) * 3) - self.delete_base_line, text=pds_user_name_str[54:])
        else:
            self.page.drawString(x=30, y=self.max_height - ((self.font_size + self.margin) * 2) - self.delete_base_line, text=pds_user_name_str)

        self.page.drawString(x=30, y=self.max_height - ((self.font_size + self.margin) * 5) - self.delete_base_line, text="PDSユーザID:")
        self.page.drawString(x=(self.max_width / 2), y=self.max_height - ((self.font_size + self.margin) * 5) - self.delete_base_line, text=pds_user_id)
        self.page.drawString(x=30, y=self.max_height - ((self.font_size + self.margin) * 7) - self.delete_base_line, text="削除条件:")
        self.page.drawString(x=45, y=self.max_height - ((self.font_size + self.margin) * 8) - self.delete_base_line, text="トランザクションIDの一覧:")
        if transaction_id_setting_str != "トランザクションIDの指定なし":
            self.page.drawString(x=(self.max_width / 2), y=self.max_height - ((self.font_size + self.margin) * 8) - self.delete_base_line, text=transaction_id_setting_str)
            self.page.drawString(x=(self.max_width / 2), y=self.max_height - ((self.font_size + self.margin) * 10) - self.delete_base_line, text="指定されたトランザクションID一覧のファイル")
            write_row_index = 11
            for setting_file_str_slice_index in range(0, len(transaction_id_setting_file_str), self.half_next_row_count):
                if setting_file_str_slice_index + self.half_next_row_count > len(transaction_id_setting_file_str):
                    self.page.drawString(x=(self.max_width / 2), y=self.max_height - ((self.font_size + self.margin) * write_row_index) - self.delete_base_line, text=transaction_id_setting_file_str[setting_file_str_slice_index:])
                else:
                    self.page.drawString(x=(self.max_width / 2), y=self.max_height - ((self.font_size + self.margin) * write_row_index) - self.delete_base_line, text=transaction_id_setting_file_str[setting_file_str_slice_index:setting_file_str_slice_index + self.half_next_row_count])
                write_row_index += 1
                write_row_index = self.next_page_check(write_row_index)

            self.page.drawString(x=30, y=self.max_height - ((self.font_size + self.margin) * write_row_index) - self.delete_base_line, text="削除した個人情報のトランザクションIDの件数:")
            self.page.drawString(x=(self.max_width / 2), y=self.max_height - ((self.font_size + self.margin) * write_row_index) - self.delete_base_line, text=str(delete_count))
            write_row_index += 2
            write_row_index = self.next_page_check(write_row_index)

            self.page.drawString(x=30, y=self.max_height - ((self.font_size + self.margin) * write_row_index) - self.delete_base_line, text="削除した個人情報のトランザクションID一覧のファイル:")
            for file_name_slice_index in range(0, len(file_name), self.half_next_row_count):
                if file_name_slice_index + self.half_next_row_count > len(file_name):
                    self.page.drawString(x=(self.max_width / 2), y=self.max_height - ((self.font_size + self.margin) * write_row_index) - self.delete_base_line, text=file_name[file_name_slice_index:])
                else:
                    self.page.drawString(x=(self.max_width / 2), y=self.max_height - ((self.font_size + self.margin) * write_row_index) - self.delete_base_line, text=file_name[file_name_slice_index:file_name_slice_index + self.half_next_row_count])
                write_row_index += 1
                write_row_index = self.next_page_check(write_row_index)

            self.page.drawCentredString(x=self.max_width / 2, y=((self.font_size + self.margin) * 1) - 5, text=str(self.page_no) + "ページ")

        elif transaction_id_setting_str == "トランザクションIDの指定なし":
            self.page.drawString(x=(self.max_width / 2), y=self.max_height - ((self.font_size + self.margin) * 8) - self.delete_base_line, text=transaction_id_setting_str)
            # 検索条件タイトル作成
            self.page.drawString(x=45, y=self.max_height - ((self.font_size + self.margin) * 9) - self.delete_base_line, text="検索条件:")
            write_row_index = 10

            # 検索用ユーザID
            self.page.drawString(x=60, y=self.max_height - ((self.font_size + self.margin) * write_row_index) - self.delete_base_line, text="検索用ユーザID:")
            if user_id_str is None:
                user_id_str = "指定なし"
            for user_id_str_slice_index in range(0, len(user_id_str), self.half_next_row_count):
                if user_id_str_slice_index + self.half_next_row_count > len(user_id_str):
                    self.page.drawString(x=(self.max_width / 2), y=self.max_height - ((self.font_size + self.margin) * write_row_index) - self.delete_base_line, text=user_id_str[user_id_str_slice_index:])
                else:
                    self.page.drawString(x=(self.max_width / 2), y=self.max_height - ((self.font_size + self.margin) * write_row_index) - self.delete_base_line, text=user_id_str[user_id_str_slice_index:user_id_str_slice_index + self.half_next_row_count])
                write_row_index += 1
                write_row_index = self.next_page_check(write_row_index)

            # 検索用ユーザID
            self.page.drawString(x=60, y=self.max_height - ((self.font_size + self.margin) * write_row_index) - self.delete_base_line, text="検索用ユーザID一致条件:")
            if user_id_match_mode is None:
                user_id_match_mode = "指定なし"
            for user_id_match_mode_slice_index in range(0, len(user_id_match_mode), self.half_next_row_count):
                if user_id_match_mode_slice_index + self.half_next_row_count > len(user_id_match_mode):
                    self.page.drawString(x=(self.max_width / 2), y=self.max_height - ((self.font_size + self.margin) * write_row_index) - self.delete_base_line, text=user_id_match_mode[user_id_match_mode_slice_index:])
                else:
                    self.page.drawString(x=(self.max_width / 2), y=self.max_height - ((self.font_size + self.margin) * write_row_index) - self.delete_base_line, text=user_id_match_mode[user_id_match_mode_slice_index:user_id_match_mode_slice_index + self.half_next_row_count])
                write_row_index += 1
                write_row_index = self.next_page_check(write_row_index)

            # 保存したいデータ形式
            self.page.drawString(x=60, y=self.max_height - ((self.font_size + self.margin) * write_row_index) - self.delete_base_line, text="保存したいデータ形式:")
            if save_data_format_str is None:
                save_data_format_str = "指定なし"
            for save_data_format_slice_index in range(0, len(save_data_format_str), self.half_next_row_count):
                if save_data_format_slice_index + self.half_next_row_count > len(save_data_format_str):
                    self.page.drawString(x=(self.max_width / 2), y=self.max_height - ((self.font_size + self.margin) * write_row_index) - self.delete_base_line, text=save_data_format_str[save_data_format_slice_index:])
                else:
                    self.page.drawString(x=(self.max_width / 2), y=self.max_height - ((self.font_size + self.margin) * write_row_index) - self.delete_base_line, text=save_data_format_str[save_data_format_slice_index:save_data_format_slice_index + self.half_next_row_count])
                write_row_index += 1
                write_row_index = self.next_page_check(write_row_index)

            # 保存したいデータJSONキー
            self.page.drawString(x=60, y=self.max_height - ((self.font_size + self.margin) * write_row_index) - self.delete_base_line, text="保存したいデータJSONキー:")
            if data_json_key is None:
                data_json_key = "指定なし"
            for data_json_key_slice_index in range(0, len(data_json_key), self.half_next_row_count):
                if data_json_key_slice_index + self.half_next_row_count > len(data_json_key):
                    self.page.drawString(x=(self.max_width / 2), y=self.max_height - ((self.font_size + self.margin) * write_row_index) - self.delete_base_line, text=data_json_key[data_json_key_slice_index:])
                else:
                    self.page.drawString(x=(self.max_width / 2), y=self.max_height - ((self.font_size + self.margin) * write_row_index) - self.delete_base_line, text=data_json_key[data_json_key_slice_index:data_json_key_slice_index + self.half_next_row_count])
                write_row_index += 1
                write_row_index = self.next_page_check(write_row_index)

            # 保存したいデータ検索テキスト
            self.page.drawString(x=60, y=self.max_height - ((self.font_size + self.margin) * write_row_index) - self.delete_base_line, text="保存したいデータ検索テキスト:")
            if data_str is None:
                data_str = "指定なし"
            for data_str_slice_index in range(0, len(data_str), self.half_next_row_count):
                if data_str_slice_index + self.half_next_row_count > len(data_str):
                    self.page.drawString(x=(self.max_width / 2), y=self.max_height - ((self.font_size + self.margin) * write_row_index) - self.delete_base_line, text=data_str[data_str_slice_index:])
                else:
                    self.page.drawString(x=(self.max_width / 2), y=self.max_height - ((self.font_size + self.margin) * write_row_index) - self.delete_base_line, text=data_str[data_str_slice_index:data_str_slice_index + self.half_next_row_count])
                write_row_index += 1
                write_row_index = self.next_page_check(write_row_index)

            # 保存したいデータ検索テキスト一致条件
            self.page.drawString(x=60, y=self.max_height - ((self.font_size + self.margin) * write_row_index) - self.delete_base_line, text="保存したいデータ検索テキスト一致条件:")
            if data_match_mode is None:
                data_match_mode = "指定なし"
            for data_match_mode_slice_index in range(0, len(data_match_mode), self.half_next_row_count):
                if data_match_mode_slice_index + self.half_next_row_count > len(data_match_mode):
                    self.page.drawString(x=(self.max_width / 2), y=self.max_height - ((self.font_size + self.margin) * write_row_index) - self.delete_base_line, text=data_match_mode[data_match_mode_slice_index:])
                else:
                    self.page.drawString(x=(self.max_width / 2), y=self.max_height - ((self.font_size + self.margin) * write_row_index) - self.delete_base_line, text=data_match_mode[data_match_mode_slice_index:data_match_mode_slice_index + self.half_next_row_count])
                write_row_index += 1
                write_row_index = self.next_page_check(write_row_index)

            # 保存したいバイナリデータのハッシュ値
            self.page.drawString(x=60, y=self.max_height - ((self.font_size + self.margin) * write_row_index) - self.delete_base_line, text="保存したいバイナリデータのハッシュ値:")
            if image_hash is None:
                image_hash = "指定なし"
            for image_hash_slice_index in range(0, len(image_hash), self.half_next_row_count):
                if image_hash_slice_index + self.half_next_row_count > len(image_hash):
                    self.page.drawString(x=(self.max_width / 2), y=self.max_height - ((self.font_size + self.margin) * write_row_index) - self.delete_base_line, text=image_hash[image_hash_slice_index:])
                else:
                    self.page.drawString(x=(self.max_width / 2), y=self.max_height - ((self.font_size + self.margin) * write_row_index) - self.delete_base_line, text=image_hash[image_hash_slice_index:image_hash_slice_index + self.half_next_row_count])
                write_row_index += 1
                write_row_index = self.next_page_check(write_row_index)

            # 検索日時
            self.page.drawString(x=60, y=self.max_height - ((self.font_size + self.margin) * write_row_index) - self.delete_base_line, text="検索期間:")
            self.page.drawString(x=(self.max_width / 2), y=self.max_height - ((self.font_size + self.margin) * write_row_index) - self.delete_base_line, text=("指定なし" if from_date is None else from_date) + " ～ " + ("指定なし" if to_date is None else to_date))
            write_row_index += 1
            write_row_index = self.next_page_check(write_row_index)

            self.page.drawString(x=30, y=self.max_height - ((self.font_size + self.margin) * write_row_index) - self.delete_base_line, text="削除した個人情報のトランザクションIDの件数")
            self.page.drawString(x=(self.max_width / 2), y=self.max_height - ((self.font_size + self.margin) * write_row_index) - self.delete_base_line, text=str(delete_count))
            write_row_index += 1
            write_row_index = self.next_page_check(write_row_index)

            self.page.drawString(x=30, y=self.max_height - ((self.font_size + self.margin) * write_row_index) - self.delete_base_line, text="削除した個人情報のトランザクションID一覧のファイル:")
            if file_name is None:
                file_name = "指定なし"
            for file_name_slice_index in range(0, len(file_name), self.half_next_row_count):
                if file_name_slice_index + self.half_next_row_count > len(file_name):
                    self.page.drawString(x=(self.max_width / 2), y=self.max_height - ((self.font_size + self.margin) * write_row_index) - self.delete_base_line, text=file_name[file_name_slice_index:])
                else:
                    self.page.drawString(x=(self.max_width / 2), y=self.max_height - ((self.font_size + self.margin) * write_row_index) - self.delete_base_line, text=file_name[file_name_slice_index:file_name_slice_index + self.half_next_row_count])
                write_row_index += 1
                write_row_index = self.next_page_check(write_row_index)

            self.page.drawCentredString(x=self.max_width / 2, y=((self.font_size + self.margin) * 1) - 5, text=str(self.page_no) + "ページ")

        self.page.save()

    def get_pdf_file(self):
        self.pdf_file.seek(0)
        return self.pdf_file
