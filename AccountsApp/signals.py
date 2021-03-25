from django.dispatch import Signal

verification_code_sent = Signal(providing_args=["request", "verification"])
verification_link_sent = Signal(providing_args=["request", "verification"])
code_verified = Signal(providing_args=["request", "verification"])
link_verified = Signal(providing_args=["request", "verification"])
password_reset = Signal(providing_args=["request", "verification"])
password_changed = Signal(providing_args=["request", "user"])
signed_in = Signal(providing_args=["request", "user"])
signed_up = Signal(providing_args=["request", "user"])
signed_out = Signal(providing_args=[])