class PagamentoServiceError(Exception):
    def __init__(self, message, code='PAYMENT_ERROR'):
        self.message = message
        self.code = code
        super().__init__(message)
