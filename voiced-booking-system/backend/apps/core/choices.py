from django.utils.translation import gettext_lazy as _

LANGUAGE_CHOICES = [
    ('es', _('Spanish')),
    ('en', _('English'))
]

CURRENCY_CHOICES = [
    ('EUR', 'Euro'),
    ('USD', 'US Dollar'),
    ('GBP', 'British Pound'),
]

BUSINESS_TYPE_CHOICES = [
    ('salon', _('Hair Salon')),
    ('clinic', _('Medical Clinic')),
    ('restaurant', _('Restaurant')),
    ('spa', _('Spa')),
    ('dental', _('Dental Clinic')),
    ('fitness', _('Fitness Center')),
    ('other', _('Other'))
]

APPOINTMENT_STATUS_CHOICES = [
    ('pending', _('Pending')),
    ('confirmed', _('Confirmed')),
    ('in_progress', _('In Progress')),
    ('completed', _('Completed')),
    ('cancelled', _('Cancelled')),
    ('no_show', _('No Show')),
]

APPOINTMENT_SOURCE_CHOICES = [
    ('online', _('Online')),
    ('phone', _('Phone')),
    ('walk_in', _('Walk-in')),
    ('vapi', _('Voice AI')),
    ('admin', _('Admin')),
]

PAYMENT_STATUS_CHOICES = [
    ('pending', _('Pending')),
    ('paid', _('Paid')),
    ('partial', _('Partial')),
    ('failed', _('Failed')),
    ('refunded', _('Refunded')),
]

CLIENT_SOURCE_CHOICES = [
    ('website', _('Website')),
    ('referral', _('Referral')),
    ('social_media', _('Social Media')),
    ('vapi', _('Voice AI')),
    ('walk_in', _('Walk-in')),
    ('admin', _('Admin')),
]

RESOURCE_TYPE_CHOICES = [
    ('staff', _('Staff')),
    ('room', _('Room')),
    ('equipment', _('Equipment')),
]

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
