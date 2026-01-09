# treks_app/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-and-conditions/', views.terms_and_conditions, name='terms_and_conditions'),
    path('user-agreement/', views.user_agreement, name='user_agreement'),
    path('safety/', views.safety, name='safety'),

    # Blog pages
    path('blogs/', views.blogs, name='blogs'),
    path('blogs/<slug:slug>/', views.blog_detail, name='blog_detail'),

    # Trek pages (DB-based)
    path('treks/', views.treks, name='treks'),
    path('treks/<slug:slug>/', views.trek_detail, name='trek_detail'),

    # Static-card trek detail (uses trek_data.py + card_details.html)
    # path('card-trek/<slug:slug>/', views.trek_detail, name='card_trek_detail'),
    path('card-trek/<slug:slug>/', views.card_trek_detail, name='card_trek_detail'),


    # Search – used by the home page search bar (on submit)
    path('search/', views.search_trek, name='search_trek'),

    # 🔹 NEW: Live suggestions endpoint (used by JS fetch)
    path('search-suggestions/', views.search_suggestions, name='search_suggestions'),

    # Travel Your Way separate listing page
    path('travel-your-way/', views.travel_your_way, name='travel_your_way'),

    # # API endpoints
    path('api/contact/', views.contact_submit, name='contact_submit'),
]


# from django.urls import path
# from . import views

# urlpatterns = [
#     # Main pages
#     path('', views.home, name='home'),
#     path('about/', views.about, name='about'),
#     path('contact/', views.contact, name='contact'),
#     path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
#      path('terms-and-conditions/', views.terms_and_conditions, name='terms_and_conditions'),
#     path('user-agreement/', views.user_agreement, name='user_agreement'),
#     path('safety/', views.safety, name='safety'),
    
#     # Blog pages
#     path('blogs/', views.blogs, name='blogs'),
#     path('blogs/<slug:slug>/', views.blog_detail, name='blog_detail'),
    
#     # Trek pages
#     path('treks/', views.treks, name='treks'),
#     path('treks/<slug:slug>/', views.trek_detail, name='trek_detail'),
    
#     # API endpoints
#     path('api/contact/', views.contact_submit, name='contact_submit'),
# ]