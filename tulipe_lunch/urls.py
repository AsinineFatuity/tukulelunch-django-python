"""tulipe_lunch URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf.urls import url

#to serve my favicon in static folder
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView

#import for serving static files
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
#imports for serving media
from django.conf import settings
from django.conf.urls.static import static

from members import views as members_views


members_patterns=[
    path((''),members_views.home_page,name='home'),
    path('category/<slug:category_slug>',members_views.display_page,name='items_by_category'),
    path('display/',members_views.display_page,name='disp_home'),
    path('thankyou/<int:commitment_id>',members_views.thankyou_page,name='danke_prima'),
    path(('category/<slug:category_slug>/<slug:item_slug>'),members_views.item_page,name='item_detail'),
    path('pledge/add<int:item_id>',members_views.add_pledge,name='add_pledge'),
    path('pledge/remove<int:item_id>',members_views.remove_pledge,name='remove_pledge'),
    path('pledge/delete<int:item_id>',members_views.delete_pledge,name='delete_pledge'),
    path('pledge/',members_views.pledge_detail,name='pledge_detail'),
    path('account/create/',members_views.sign_up_view,name='signup'),
    path('account/signin/',members_views.sign_in_view,name='signin'),
    path('account/signout/',members_views.sign_out_view,name='signout'), 
    path('commitment_history/',members_views.commitment_history,name='commit_history'), 
    path('commitment_detail/<int:commitment_id>',members_views.commitment_details,name='commit_detail'),
    path('search/',members_views.search,name='search'),
    path('contact/',members_views.contact,name='contact'),

]
urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'',include(members_patterns)),
    path(
        "favicon.ico",
        RedirectView.as_view(url=staticfiles_storage.url("favicon.ico")),
    ),
]
if settings.DEBUG: # to serve the static files in development mode
    #for serving static files
    urlpatterns += staticfiles_urlpatterns()
    #for serving media files
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)