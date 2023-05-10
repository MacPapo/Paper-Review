from app.models import UserV

def is_researcher(user):
    userv = UserV()
    return userv.is_researcher(user)
