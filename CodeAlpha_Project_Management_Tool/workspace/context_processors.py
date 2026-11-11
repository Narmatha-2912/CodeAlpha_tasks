def taskflow_context(request):
    if request.user.is_authenticated:
        from .models import Notification
        return {"unread_notifications": Notification.objects.filter(recipient=request.user, is_read=False).count()}
    return {"unread_notifications": 0}
