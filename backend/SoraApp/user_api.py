from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from users.authentication import ExpiringTokenAuthentication
from rest_framework.response import Response
from users.models import Announcement, AnnouncementView, FAQ
from users.serializers import FAQSerializer
from django.utils import timezone
from django.db.models import Q

@api_view(['GET'])
@authentication_classes([ExpiringTokenAuthentication])
@permission_classes([IsAuthenticated])
def list_faqs(request):
    """
    Returns all active FAQs ordered by order and creation time.
    """
    faqs = FAQ.objects.filter(is_active=True)
    serializer = FAQSerializer(faqs, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@authentication_classes([ExpiringTokenAuthentication])
@permission_classes([IsAuthenticated])
def list_announcements(request):
    """
    Returns all active announcements ordered by creation time (newest first).
    """
    announcements = Announcement.objects.filter(is_active=True).order_by('-created_at')
    
    # Optional: Mark all as read if user visits the page?
    # For now just list.
    
    data = []
    for a in announcements:
        data.append({
            'id': a.id,
            'title': a.title,
            'content': a.content,
            'created_at': a.created_at
        })
    return Response(data)

@api_view(['GET'])
@authentication_classes([ExpiringTokenAuthentication])
@permission_classes([IsAuthenticated])
def get_unread_announcements(request):
    """
    Returns active announcements with status.
    Used for both Banner (dismissible) and Popup (new announcements).
    """
    user = request.user
    active_announcements = Announcement.objects.filter(is_active=True).order_by('-created_at')
    
    results = []
    
    # Pre-fetch views to minimize queries
    views_map = {
        v.announcement_id: v 
        for v in AnnouncementView.objects.filter(user=user, announcement__in=active_announcements)
    }

    for a in active_announcements:
        view = views_map.get(a.id)
        is_dismissed = False
        if view and view.view_count > 0:
            is_dismissed = True
            
        results.append({
            'id': a.id,
            'title': a.title,
            'content': a.content,
            'created_at': a.created_at,
            'is_dismissed': is_dismissed
        })
            
    return Response(results)

@api_view(['POST'])
@authentication_classes([ExpiringTokenAuthentication])
@permission_classes([IsAuthenticated])
def acknowledge_announcement(request):
    """
    Log a view for an announcement. Increments view_count.
    """
    announcement_id = request.data.get('id')
    if not announcement_id:
        return Response({'error': 'ID required'}, status=400)
        
    try:
        announcement = Announcement.objects.get(id=announcement_id)
        view, created = AnnouncementView.objects.get_or_create(user=request.user, announcement=announcement)
        view.view_count += 1
        view.save()
        return Response({'success': True, 'view_count': view.view_count})
    except Announcement.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)
