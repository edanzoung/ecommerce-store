
from store.models import Product,Variation
from accounts.models import UserProfile,Account

def Profile_user(request):
    userprofile=None
    account=None
    if request.user.is_authenticated:
        userprofile = UserProfile.objects.get(user=request.user)
        account = Account.objects.get(id=request.user.id)

    
    return dict(userprofile = userprofile,account = account)