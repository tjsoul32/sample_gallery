from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^upload_img/', views.upload_img, name='upload_img'),
    url(r'^upload_check/', views.upload_check, name='upload_check'),
    url(r'^get_imgs/?', views.get_imgs, name='get_imgs'),
    url(r'^get_img_stylized/?', views.get_img_stylized, name='get_img_stylized'),
    url(r'^get_tags/?', views.get_tags, name='get_tags'),
    url(r'^get_types/?', views.get_types, name='get_types'),
]


