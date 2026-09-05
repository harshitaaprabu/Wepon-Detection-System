from alertupload_rest.serializers import UploadAlertSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.core.mail import send_mail
from threading import Thread
import re
from django.conf import settings
from django.http import JsonResponse
from twilio.rest import Client


def start_new_thread(function):
    def decorator(*args, **kwargs):
        t = Thread(target=function, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()
    return decorator


@api_view(['POST'])
def post_alert(request):
    serializer = UploadAlertSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        identify_email_sms(serializer)
    else:
        return JsonResponse({'error': 'Unable to Process data!'}, status=400)

    return Response(request.META.get('HTTP_AUTHORIZATION'))


# ✅ FIXED FUNCTION
def identify_email_sms(serializer):
    receiver = serializer.data['alert_receiver']
    print("Receiver:", receiver)

    # Simple and safe email check
    if "@" in receiver:
        print("Valid Email → Sending Email")
        send_email(serializer)   # 🔥 NOW EMAIL WILL SEND

    # Mobile number check (optional for future SMS)
    elif receiver.startswith("+"):
        print("Valid Mobile Number")
        send_sms(serializer)

    else:
        print("Invalid Email or Mobile number")

@start_new_thread
def send_sms(serializer):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    message = client.messages.create(body=prepare_alert_message(serializer),
                                    from_=settings.TWILIO_NUMBER,
                                    to=serializer.data['alert_receiver'])


@start_new_thread
def send_email(serializer):
    print("🔥 EMAIL FUNCTION CALLED")

    send_mail(
        subject='Weapon Detected!',
        message=prepare_alert_message(serializer),
        from_email=settings.EMAIL_HOST_USER,  # ✅ use settings
        recipient_list=[serializer.data['alert_receiver']],
        fail_silently=False,
    )


def prepare_alert_message(serializer):
    image_data = split(serializer.data['image'], ".")
    uuid = image_data[0]

    uuid = uuid.lstrip("/")

    # ✅ fixed missing slash
    url = 'http://127.0.0.1:8000/alert/' + uuid

    return '🚨 Weapon Detected!\nView alert at ' + url


def split(value, key):
    return str(value).split(key)