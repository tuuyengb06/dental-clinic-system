import re
from datetime import date

import requests
from django.conf import settings


class SMSServiceConfigurationError(Exception):
    pass


class SMSServiceError(Exception):
    pass


class SMSDeliveryUncertainError(SMSServiceError):
    pass


def build_follow_up_message(scheduled_for: date, generic_text: str) -> str:
    message = f"Mời bạn tái khám ngày {scheduled_for:%d/%m}. {generic_text}"
    if len(message.encode("utf-16-be")) // 2 > 70:
        raise SMSServiceError(
            "Reminder exceeds the single-segment Vietnamese SMS length limit."
        )
    return message


def validate_sms_configuration():
    config = (
        settings.TWILIO_ACCOUNT_SID,
        settings.TWILIO_AUTH_TOKEN,
        settings.TWILIO_FROM_NUMBER,
    )
    if not all(config):
        raise SMSServiceConfigurationError(
            "Twilio is not configured. Set the DMS_TWILIO_* variables before sending SMS."
        )


def _normalize_vietnamese_mobile(phone):
    compact = re.sub(r"[\s().-]", "", phone)
    if compact.startswith("0"):
        compact = "+84" + compact[1:]
    elif compact.startswith("84"):
        compact = "+" + compact
    if not re.fullmatch(r"\+84[35789]\d{8}", compact):
        raise SMSServiceError("Patient phone must be a valid Vietnamese mobile number.")
    return compact


def send_sms(phone, message):
    validate_sms_configuration()
    recipient = _normalize_vietnamese_mobile(phone)
    url = (
        "https://api.twilio.com/2010-04-01/Accounts/"
        f"{settings.TWILIO_ACCOUNT_SID}/Messages.json"
    )
    try:
        response = requests.post(
            url,
            auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN),
            data={
                "To": recipient,
                "From": settings.TWILIO_FROM_NUMBER,
                "Body": message,
            },
            timeout=(5, 20),
        )
    except requests.RequestException as error:
        raise SMSDeliveryUncertainError(
            "Twilio request outcome is unknown; verify the provider before retrying."
        ) from error

    if response.status_code >= 400:
        if response.status_code >= 500:
            raise SMSDeliveryUncertainError(
                f"Twilio returned HTTP {response.status_code}; delivery outcome is unknown."
            )
        raise SMSServiceError(f"Twilio returned HTTP {response.status_code}.")
    try:
        data = response.json()
        reference = data["sid"]
    except (KeyError, TypeError, ValueError) as error:
        raise SMSDeliveryUncertainError(
            "Twilio response is invalid; delivery outcome is unknown."
        ) from error
    if not isinstance(reference, str) or not reference:
        raise SMSDeliveryUncertainError(
            "Twilio response has no message reference; delivery outcome is unknown."
        )
    return reference
