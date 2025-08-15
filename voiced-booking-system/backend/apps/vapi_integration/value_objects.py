from dataclasses import dataclass
from typing import Dict, Any
from datetime import datetime


@dataclass(frozen=True)
class VapiCallId:
    value: str
    
    def __post_init__(self):
        if not self.value or not isinstance(self.value, str):
            raise ValueError("Call ID must be a non-empty string")


@dataclass(frozen=True)
class BusinessSlug:
    value: str
    
    def __post_init__(self):
        if not self.value or not isinstance(self.value, str):
            raise ValueError("Business slug must be a non-empty string")


@dataclass(frozen=True)
class WebhookSignature:
    signature: str
    
    def __post_init__(self):
        if not self.signature:
            raise ValueError("Webhook signature cannot be empty")


@dataclass(frozen=True)
class VapiEventType:
    value: str
    
    VALID_EVENTS = {
        'assistant-request',
        'function-call', 
        'tool-calls',
        'call-started',
        'call-ended',
        'speech-started',
        'speech-ended',
        'transcript',
        'hang',
        'status-update',
        'end-of-call-report'
    }
    
    def __post_init__(self):
        if self.value not in self.VALID_EVENTS:
            raise ValueError(f"Invalid event type: {self.value}")
    
    @property
    def is_call_ended(self) -> bool:
        return self.value == 'call-ended'
    
    @property
    def is_call_started(self) -> bool:
        return self.value == 'call-started'
    
    @property
    def is_function_call(self) -> bool:
        return self.value in ('function-call', 'tool-calls')
    
    @property
    def is_assistant_request(self) -> bool:
        return self.value == 'assistant-request'
    
    @property
    def is_speech_event(self) -> bool:
        return self.value in ('speech-started', 'speech-ended')
    
    @property
    def is_transcript(self) -> bool:
        return self.value == 'transcript'
    
    @property
    def is_end_of_call_report(self) -> bool:
        return self.value == 'end-of-call-report'


@dataclass(frozen=True)
class CallAnalysisData:
    summary: str
    structured_data: Dict[str, Any]
    success_evaluation: str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CallAnalysisData':
        return cls(
            summary=data.get('summary', ''),
            structured_data=data.get('structuredData', {}),
            success_evaluation=data.get('successEvaluation', '')
        )
    
    @property
    def has_appointment_data(self) -> bool:
        return bool(self.structured_data.get('appointment') or 
                   self.structured_data.get('service_name'))


@dataclass(frozen=True)
class AppointmentBookingData:
    service_name: str
    client_name: str
    client_phone: str
    client_email: str
    datetime_iso: str
    notes: str = ''
    
    @classmethod
    def from_structured_data(cls, data: Dict[str, Any]) -> 'AppointmentBookingData':
        return cls(
            service_name=data.get('service_name', ''),
            client_name=data.get('client_name', ''),
            client_phone=data.get('client_phone', ''),
            client_email=data.get('client_email', ''),
            datetime_iso=data.get('datetime', ''),
            notes=data.get('notes', '')
        )
    
    @property
    def is_valid(self) -> bool:
        return bool(self.service_name and self.datetime_iso)
