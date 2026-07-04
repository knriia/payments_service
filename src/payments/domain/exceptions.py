class PaymentDomainError(Exception):
    pass


class InvalidPaymentAmount(PaymentDomainError):
    pass


class InvalidStatusTransition(PaymentDomainError):
    pass
