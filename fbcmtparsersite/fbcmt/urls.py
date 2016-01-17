from django.conf.urls import url, include
from django.views.generic import TemplateView
from . import views
'''
from .views import UserList, UserDetail
from .views import PostList, PostDetail, UserPostList
from .views import PhotoList, PhotoDetail, PostPhotoList

user_urls = [
    url(r'^(?P<username>[0-9a-zA-Z_-]+)/posts$', UserPostList.as_view(), name='userpost-list'),
    url(r'^(?P<username>[0-9a-zA-Z_-]+)$', UserDetail.as_view(), name='user-detail'),
    url(r'^$', UserList.as_view(), name='user-list')
]

post_urls = [
    url(r'^(?P<pk>\d+)/photos$', PostPhotoList.as_view(), name='postphoto-list'),
    url(r'^(?P<pk>\d+)$', PostDetail.as_view(), name='post-detail'),
    url(r'^$', PostList.as_view(), name='post-list')
]

photo_urls = [
    url(r'^(?P<pk>\d+)$', PhotoDetail.as_view(), name='photo-detail'),
    url(r'^$', PhotoList.as_view(), name='photo-list')
]
'''

facebook_graph_urls = [
    url(r'^$', views.FacebookGraphAPI),
    url(r'^comments$', views.FacebookGraphAPI_get_comments)
]

google_drive_urls = [
    url(r'^ss/new$', views.GoogleDriveAPI_new_spreadsheet)
]

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='index.html')),
    url(r'^fbghapi/', include(facebook_graph_urls)),
    url(r'^ggdrvapi/', include(google_drive_urls)),
    #url(r'^users/', include(user_urls)),
    #url(r'^posts/', include(post_urls)),
    #url(r'^photos/', include(photo_urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]