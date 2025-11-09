
import hashlib
import uuid
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken,BlacklistedToken
from users.models import Otp

def generate_otp(user):
    otp_code = str(uuid.uuid4().int)[:6]
    hashed_otp = hashlib.sha256(otp_code.encode()).hexdigest()

    # delete old OTPs
    Otp.objects.filter(user=user).delete()

    # save new one
    Otp.objects.create(
        user=user,
        otp=hashed_otp,
    )

    return otp_code


def delete_all_user_tokens(user):
    OutstandingToken.objects.filter(user=user).delete()