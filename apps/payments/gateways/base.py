from abc import ABC, abstractmethod


class BasePaymentGateway(ABC):
    @abstractmethod
    def create_payment(self, order, amount):
        """Create a payment intent/order and return gateway response."""
        pass

    @abstractmethod
    def confirm_payment(self, payment_id):
        """Confirm and capture the payment."""
        pass

    @abstractmethod
    def refund_payment(self, payment_id, amount=None):
        """Refund a payment fully or partially."""
        pass

    @abstractmethod
    def get_payment_status(self, payment_id):
        """Return current status of the payment."""
        pass
