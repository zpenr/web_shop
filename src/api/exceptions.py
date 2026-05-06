class CustomException(Exception):
    code = 600
    message = "Some Error"

class QueriesException(CustomException):
    code = 800
    message = "Query Error"

class NotEnougthProductException(QueriesException):
    code = 801
    message = "Product quantity at storage smaller than quantity that you want sell"
    