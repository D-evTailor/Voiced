from django.utils.translation import gettext_lazy as _

VAPI_CALL_STATUS_CHOICES = [
    ('scheduled', _('Scheduled')),
    ('queued', _('Queued')),
    ('ringing', _('Ringing')),
    ('in_progress', _('In Progress')),
    ('forwarding', _('Forwarding')),
    ('ended', _('Ended'))
]

VAPI_CALL_TYPE_CHOICES = [
    ('inboundPhoneCall', _('Inbound Phone Call')),
    ('outboundPhoneCall', _('Outbound Phone Call')),
    ('webCall', _('Web Call')),
    ('vapi.websocketCall', _('Websocket Call'))
]

VAPI_ENDED_REASON_CHOICES = [
    ('call-start-error-neither-assistant-nor-server-set', _('Neither assistant nor server set')),
    ('call-start-error-server-error', _('Server error')),
    ('assistant-said-end-call-phrase', _('Assistant said end call phrase')),
    ('customer-said-end-call-phrase', _('Customer said end call phrase')),
    ('silence-timed-out', _('Silence timed out')),
    ('max-duration-exceeded', _('Max duration exceeded')),
    ('inactivity-timeout', _('Inactivity timeout')),
    ('pipeline-error-openai-llm-failed', _('OpenAI LLM failed')),
    ('pipeline-error-azure-voice-failed', _('Azure voice failed')),
    ('voicemail', _('Voicemail')),
    ('pipeline-error-function-filler-failed', _('Function filler failed')),
    ('pipeline-error-azure-voice-failed-no-audio', _('Azure voice failed no audio')),
    ('dial-busy', _('Dial busy')),
    ('dial-failed', _('Dial failed')),
    ('dial-no-answer', _('Dial no answer')),
    ('hangup', _('Hangup')),
    ('assistant-not-found', _('Assistant not found')),
    ('assistant-not-invalid', _('Assistant not invalid')),
    ('assistant-forwarded-call', _('Assistant forwarded call')),
    ('assistant-join-timeout', _('Assistant join timeout')),
    ('assistant-left', _('Assistant left'))
]

LANGUAGE_CHOICES = [
    ('es', _('Spanish')),
    ('en', _('English'))
]
