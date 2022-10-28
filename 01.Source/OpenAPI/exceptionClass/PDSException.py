class PDSException(Exception):

    def __init__(self, *error_info):
        self.error_info_list = []
        self.pgcode = ""
        self.pgerror = ""
        for error in error_info:
            self.error_info_list.append(error)

    def setter(self, pgcode, pgerror):
        self.pgcode = pgcode
        self.message = pgerror
