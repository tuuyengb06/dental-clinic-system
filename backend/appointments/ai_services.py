import json
import re
import time
from collections.abc import Mapping
from pathlib import Path

import requests
from django.conf import settings


AI_REQUEST_TIMEOUT = (3, 5)
AI_MAX_ATTEMPTS = 2
AI_RETRY_DELAY_SECONDS = 0.5
PROMPT_DIRECTORY = Path(__file__).resolve().parents[2] / "prompts"


class AIServiceError(Exception):
    pass


class AIServiceConfigurationError(AIServiceError):
    pass


class AIServiceCredentialsError(AIServiceError):
    pass


class AIServiceOutputError(AIServiceError):
    pass


class AIServiceTimeoutError(AIServiceError):
    pass


class AIServiceUnavailableError(AIServiceError):
    pass


def _render_prompt(template_name, **values):
    template_path = PROMPT_DIRECTORY / template_name
    try:
        template = template_path.read_text(encoding="utf-8").strip()
    except OSError as error:
        raise AIServiceError(
            f"Required AI prompt template is unavailable: {template_name}."
        ) from error

    for key, value in values.items():
        placeholder = f"{{{{{key}}}}}"
        if placeholder not in template:
            raise AIServiceError(
                f"AI prompt template is missing placeholder {placeholder}."
            )
        template = template.replace(placeholder, value)
    if re.search(r"\{\{[a-z_]+\}\}", template):
        raise AIServiceError(
            f"AI prompt template contains an unresolved placeholder: {template_name}."
        )
    return template


def _generate_text(
    prompt,
    max_output_tokens,
    system_instruction=None,
    timeout=AI_REQUEST_TIMEOUT,
    max_attempts=AI_MAX_ATTEMPTS,
    thinking_budget=None,
):
    if not settings.GEMINI_API_KEY or not settings.GEMINI_MODEL:
        raise AIServiceConfigurationError(
            "Gemini is not configured. Set DMS_GEMINI_API_KEY before using AI features."
        )

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.GEMINI_MODEL}:generateContent"
    )
    request_data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": max_output_tokens,
        },
    }
    if thinking_budget is not None:
        request_data["generationConfig"]["thinkingConfig"] = {
            "thinkingBudget": thinking_budget,
        }
    if system_instruction:
        request_data["system_instruction"] = {
            "parts": [{"text": system_instruction}]
        }

    response = None
    for attempt in range(max_attempts):
        try:
            response = requests.post(
                url,
                headers={"x-goog-api-key": settings.GEMINI_API_KEY},
                json=request_data,
                timeout=timeout,
            )
        except requests.Timeout as error:
            if attempt == max_attempts - 1:
                raise AIServiceTimeoutError("Gemini request timed out.") from error
            time.sleep(AI_RETRY_DELAY_SECONDS)
            continue
        except requests.ConnectionError as error:
            if attempt == max_attempts - 1:
                raise AIServiceUnavailableError("Gemini could not be reached.") from error
            time.sleep(AI_RETRY_DELAY_SECONDS)
            continue
        except requests.RequestException as error:
            raise AIServiceError("Gemini request failed.") from error

        if response.status_code in (408, 429) or response.status_code >= 500:
            if attempt == max_attempts - 1:
                response.close()
                if response.status_code == 408:
                    raise AIServiceTimeoutError(
                        "Gemini request timed out after all attempts."
                    )
                raise AIServiceUnavailableError(
                    f"Gemini returned HTTP {response.status_code} after all attempts."
                )
            response.close()
            time.sleep(AI_RETRY_DELAY_SECONDS)
            continue
        if response.status_code >= 400:
            response.close()
            if response.status_code in (401, 403):
                raise AIServiceCredentialsError(
                    f"Gemini rejected API credentials (HTTP {response.status_code})."
                )
            if response.status_code in (400, 404):
                raise AIServiceConfigurationError(
                    f"Gemini rejected the model or request configuration (HTTP {response.status_code})."
                )
            raise AIServiceError(f"Gemini returned HTTP {response.status_code}.")
        break

    if response is None:
        raise AIServiceUnavailableError("Gemini could not be reached.")
    try:
        data = response.json()
        if not isinstance(data, Mapping):
            raise AIServiceOutputError("Gemini returned an invalid response.")
        candidates = data.get("candidates")
        if not isinstance(candidates, list) or not candidates:
            raise AIServiceOutputError("Gemini returned an invalid response.")
        candidate = candidates[0]
        if not isinstance(candidate, Mapping):
            raise AIServiceOutputError("Gemini returned an invalid response.")
        finish_reason = candidate.get("finishReason")
        if finish_reason not in (None, "STOP"):
            raise AIServiceOutputError(
                f"Gemini stopped generation before completing the response ({finish_reason})."
            )
        content = candidate.get("content")
        if not isinstance(content, Mapping):
            raise AIServiceOutputError("Gemini returned an invalid response.")
        parts = content.get("parts")
        if not isinstance(parts, list):
            raise AIServiceOutputError("Gemini returned an invalid response.")
        text_parts = []
        for part in parts:
            if not isinstance(part, Mapping):
                raise AIServiceOutputError("Gemini returned an invalid response.")
            if "text" in part and not isinstance(part["text"], str):
                raise AIServiceOutputError("Gemini returned an invalid response.")
            text_parts.append(part.get("text", ""))
        text = "".join(text_parts).strip()
    except (TypeError, ValueError) as error:
        raise AIServiceOutputError("Gemini returned an invalid response.") from error
    finally:
        response.close()
    if not text:
        raise AIServiceOutputError("Gemini returned an empty response.")
    return text


def _redact_clinical_text(text, patient):
    if not isinstance(text, str):
        return text

    text = re.sub(
        r"(?<![\w.+-])[A-Za-z0-9._%+\-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?![\w.+-])",
        "[redacted]",
        text,
    )
    text = re.sub(
        r"(?<!\w)(?:\+?\d[\d\s().-]{7,}\d)(?!\w)",
        "[redacted]",
        text,
    )
    text = re.sub(
        r"(?<!\w)(?:\d{4}[./-]\d{1,2}[./-]\d{1,2}|\d{1,2}[./-]\d{1,2}[./-]\d{2,4})(?!\w)",
        "[redacted]",
        text,
    )
    identifiers = [patient.full_name, patient.patient_code, patient.phone]
    if patient.date_of_birth:
        identifiers.extend(
            (
                patient.date_of_birth.isoformat(),
                patient.date_of_birth.strftime("%d/%m/%Y"),
                patient.date_of_birth.strftime("%d-%m-%Y"),
                patient.date_of_birth.strftime("%d.%m.%Y"),
            )
        )
    for identifier in identifiers:
        if not identifier or not identifier.strip():
            continue
        escaped = re.escape(identifier.strip())
        if identifier == patient.full_name:
            escaped = r"\s+".join(
                re.escape(part) for part in identifier.split()
            )
        text = re.sub(
            rf"(?<!\w){escaped}(?!\w)",
            "[redacted]",
            text,
            flags=re.IGNORECASE,
        )
    return text


def generate_medical_record_summary(record):
    patient = record.appointment.patient

    clinical_data = {
        "diagnosis_as_recorded": _redact_clinical_text(record.diagnosis, patient),
        "treatment_plan_as_recorded": _redact_clinical_text(record.treatment_plan, patient),
        "prescription_as_recorded": _redact_clinical_text(record.prescription or "", patient),
        "clinical_notes_as_recorded": _redact_clinical_text(record.notes or "", patient),
        "services": [
            _redact_clinical_text(name, patient)
            for name in record.services.values_list("name", flat=True)
        ],
        "teeth": list(record.teeth.values_list("code", flat=True)),
    }
    prompt = _render_prompt(
        "medical-record-summary-v1.txt",
        clinical_data=json.dumps(clinical_data, ensure_ascii=False),
    )
    return _generate_text(prompt, max_output_tokens=350)


def generate_generic_follow_up_text():
    text = _generate_text(
        _render_prompt("follow-up-invitation-v1.txt"),
        max_output_tokens=40,
        system_instruction=_render_prompt("follow-up-invitation-system-v1.txt"),
    )
    text = " ".join(text.split()).strip('"“”\'')
    if not text or len(text) > 28 or re.search(r"\d", text):
        raise AIServiceOutputError(
            "Gemini returned reminder text outside the allowed length."
        )
    return text


def generate_service_explanation(service):
    source = {
        "service_name": service.name,
        "service_description": service.description.strip(),
    }
    text = _generate_text(
        _render_prompt(
            "service-explanation-v1.txt",
            service_data=json.dumps(source, ensure_ascii=False),
        ),
        max_output_tokens=180,
        system_instruction=_render_prompt("service-explanation-system-v1.txt"),
    )
    if len(text) > 800:
        raise AIServiceOutputError(
            "Gemini returned a service explanation that is too long."
        )

    disclaimer = (
        "Thông tin chỉ mang tính tham khảo, không thay thế tư vấn hoặc chẩn đoán "
        "của bác sĩ."
    )
    if disclaimer.casefold() not in text.casefold():
        text = f"{text}\n\n{disclaimer}"
    return text


def generate_project_consultation_answer(question):
    prompt = _render_prompt(
        "project-consultation-v1.txt",
        question=json.dumps(question, ensure_ascii=False),
    )
    text = _generate_text(
        prompt,
        max_output_tokens=8192,
        system_instruction=_render_prompt("project-consultation-system-v1.txt"),
        timeout=(3, 60),
        max_attempts=1,
        thinking_budget=(
            0 if settings.GEMINI_MODEL.casefold().startswith("gemini-2.5-") else None
        ),
    )
    if len(text) > 24000:
        raise AIServiceOutputError(
            "Gemini returned a project consultation answer that is too long."
        )
    return text
