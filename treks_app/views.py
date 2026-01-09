from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.core.paginator import Paginator
import json
from django.urls import reverse
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django.shortcuts import render
from treks_app.models import TrekList
from django.db.models import Q
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from datetime import datetime
import requests
from django.conf import settings

@api_view(['POST'])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
def contact_submit(request):
    try:
        # Get data from POST request
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            name = data.get('name')
            email = data.get('email')
            mobile = data.get('mobile')
            user_type = data.get('userType')
            comment = data.get('comment')
        else:
            # Handle form data
            name = request.POST.get('name')
            email = request.POST.get('email')
            mobile = request.POST.get('mobile')
            user_type = request.POST.get('userType')
            comment = request.POST.get('comment')
        
        # Validate required fields
        if not all([name, email, mobile, comment]):
            return JsonResponse({'error': 'All fields are required'}, status=400)
            
        # Create a new Contact object
        contact = Contact(
            name=name,
            email=email,
            mobile=mobile,
            user_type=user_type,
            comment=comment
        )
        contact.save()
        
        return JsonResponse({'message': 'Contact form submitted successfully'}, status=200)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
from .models import (
    Contact, Blog, TrekCategory, TrekOrganizer, Trek, 
    Testimonial, FAQ, SafetyTip, TeamMember, HomepageBanner,
    SocialMedia, ContactInfo,WhatsNew, TopTrek
)


# Create your views here.
# def home(request):
#     featured_treks = Trek.objects.filter(is_featured=True)[:6]
#     featured_testimonials = Testimonial.objects.filter(is_featured=True)[:6]
#     featured_blogs = Blog.objects.filter(is_featured=True)[:3]
#     banners = HomepageBanner.objects.filter(is_active=True).order_by('order')
#     faqs = FAQ.objects.all().order_by('category', 'order')
#     whats_new = WhatsNew.objects.all().order_by('-created_at')[:5]
#     top_treks = TopTrek.objects.all()[:6]

    
#     faq_categories = {}
#     for faq in faqs:
#         if faq.category not in faq_categories:
#             faq_categories[faq.category] = []
#         faq_categories[faq.category].append(faq)
    
#     context = {
#         'featured_treks': featured_treks,
#         'featured_testimonials': featured_testimonials,
#         'featured_blogs': featured_blogs,
#         'banners': banners,
#         'faq_categories': faq_categories,
#         'whats_new': whats_new,
#         'top_treks': top_treks,
#     }
#     return render(request, 'index.html', context)

def home(request):
    featured_treks = TrekList.objects.all().order_by("-created_at")
    
    featured_testimonials = Testimonial.objects.filter(is_featured=True)[:6]
    featured_blogs = Blog.objects.filter(is_featured=True)[:3]
    banners = HomepageBanner.objects.filter(is_active=True).order_by('order')
    faqs = FAQ.objects.all().order_by('category', 'order')
    whats_new = WhatsNew.objects.all().order_by('-created_at')[:5]
    top_treks = TopTrek.objects.all()[:6]

    faq_categories = {}
    for faq in faqs:
        faq_categories.setdefault(faq.category, []).append(faq)

    context = {
        'featured_treks': featured_treks,   # ✅ NOW CORRECT
        'featured_testimonials': featured_testimonials,
        'featured_blogs': featured_blogs,
        'banners': banners,
        'faq_categories': faq_categories,
        'whats_new': whats_new,
        'top_treks': top_treks,
    }
    return render(request, 'index.html', context)

# def home(request):
#     whats_new = WhatsNew.objects.all().order_by('-created_at')[:5]
#     top_treks = TopTrek.objects.all()[:]

#     context = {
#         'whats_new': whats_new,
#         'top_treks': top_treks,
#     }
#     return render(request, 'test.html', context)


def about(request):
    team_members = TeamMember.objects.all().order_by('order')
    context = {
        'team_members': team_members,
    }
    return render(request, 'about.html', context)

def blogs(request):
    all_blogs = Blog.objects.all().order_by('-created_at')[:6]
    paginator = Paginator(all_blogs, 6)  
    
    page_number = request.GET.get('page')
    blogs = paginator.get_page(page_number)
    
    context = {
        'blogs': blogs,
    }
    return render(request, 'blogs.html', context)

def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    recent_blogs = Blog.objects.exclude(id=blog.id).order_by('-created_at')[:3]
    
    context = {
        'blog': blog,
        'recent_blogs': recent_blogs,
    }
    return render(request, 'blog_detail.html', context)

def treks(request):
    category_id = request.GET.get('category')
    difficulty = request.GET.get('difficulty')
    
    all_treks = Trek.objects.all()
    
    # Apply filters if provided
    if category_id:
        all_treks = all_treks.filter(category_id=category_id)
    if difficulty:
        all_treks = all_treks.filter(difficulty=difficulty)
    
    # Get all categories for filter dropdown
    categories = TrekCategory.objects.all()
    
    paginator = Paginator(all_treks, 12)  # Show 12 treks per page
    page_number = request.GET.get('page')
    treks = paginator.get_page(page_number)
    
    context = {
        'treks': treks,
        'categories': categories,
        'selected_category': category_id,
        'selected_difficulty': difficulty,
        'difficulty_choices': Trek.DIFFICULTY_CHOICES,
    }
    return render(request, 'treks.html', context)

def trek_detail(request, slug):
    trek = get_object_or_404(Trek, slug=slug)
    testimonials = trek.testimonials.all()
    similar_treks = Trek.objects.filter(category=trek.category).exclude(id=trek.id)[:3]
    
    context = {
        'trek': trek,
        'testimonials': testimonials,
        'similar_treks': similar_treks,
    }
    return render(request, 'trek_detail.html', context)

def safety(request):
    safety_tips = SafetyTip.objects.all().order_by('order')
    context = {
        'safety_tips': safety_tips,
    }
    return render(request, 'safety.html', context)

# def contact(request):
#     if request.method == "GET":
#         return render(request, "contact.html")

#     # POST → handle form submit
#     if request.method != "POST":
#         return JsonResponse({"error": "Invalid request"}, status=405)

#     try:
#         data = json.loads(request.body)

#         name = data.get("name", "").strip()
#         email_addr = data.get("email", "").strip()
#         mobile = data.get("mobile", "").strip()
#         user_type = data.get("userType", "").strip()
#         message = data.get("comment", "").strip()

#         if not all([name, email_addr, mobile, user_type, message]):
#             return JsonResponse(
#                 {"error": "Please fill all required fields ❌"},
#                 status=400
#             )

#         admin_subject = f"New Contact Enquiry from {name}"
#         admin_message = (
#             f"Name: {name}\n"
#             f"Email: {email_addr}\n"
#             f"Mobile: {mobile}\n"
#             f"I am a: {user_type}\n\n"
#             f"Message:\n{message}"
#         )

#         # Send admin mail
#         send_mail(
#             subject=admin_subject,
#             message=admin_message,
#             from_email="Aorbo Treks <hello@aorbotreks.com>",  
#             recipient_list=["hello@aorbotreks.com"],
#             fail_silently=False,
#         )


#         # Auto-reply mail
#         ctx = {
#             "name": name,
#             "email_addr": email_addr,   
#             "current_year": datetime.now().year,
#             "cta_url": "https://aorbotreks.com",
#             "cta_label": "Visit Our Website",
#         }

#         html_content = render_to_string("treks_app/mail.html", ctx)
#         text_content = strip_tags(html_content)

#         reply = EmailMultiAlternatives(
#             subject="Thank you for contacting us!",
#             body=text_content,
#             from_email="Aorbo Treks <hello@aorbotreks.com>",  
#             to=[email_addr],
#         )

#         reply.attach_alternative(html_content, "text/html")
#         reply.send()

#         return JsonResponse({"message": "Message sent successfully ✅"})

#     except Exception as e:
#         return JsonResponse(
#             {"error": f"Failed to submit form: {str(e)}"},
#             status=500
#         )

# def contact(request):
#     if request.method == "GET":
#         return render(
#             request,
#             "contact.html",
#             {
#                 "RECAPTCHA_SITE_KEY": settings.RECAPTCHA_SITE_KEY
#             }
#         )
#     if request.method != "POST":
#         return JsonResponse({"error": "Invalid request"}, status=405)

#     try:
#         data = json.loads(request.body or "{}")

#         name = data.get("name", "").strip()
#         email_addr = data.get("email", "").strip()
#         mobile = data.get("mobile", "").strip()
#         user_type = data.get("userType", "").strip()
#         message = data.get("comment", "").strip()
#         recaptcha_token = data.get("recaptcha_token")
#         if not all([name, email_addr, mobile, user_type, message, recaptcha_token]):
#             return JsonResponse(
#                 {"error": "Please fill all required fields ❌"},
#                 status=400
#             )
#         recaptcha_response = requests.post(
#             "https://www.google.com/recaptcha/api/siteverify",
#             data={
#                 "secret": settings.RECAPTCHA_SECRET_KEY,
#                 "response": recaptcha_token
#             },
#             timeout=5
#         )

#         recaptcha_result = recaptcha_response.json()

#         if (
#             not recaptcha_result.get("success")
#             or recaptcha_result.get("score", 0) < 0.5
#         ):
#             return JsonResponse(
#                 {"error": "reCAPTCHA verification failed ❌"},
#                 status=400
#             )

#         admin_subject = f"New Contact Enquiry from {name}"
#         admin_message = (
#             f"Name: {name}\n"
#             f"Email: {email_addr}\n"
#             f"Mobile: {mobile}\n"
#             f"I am a: {user_type}\n\n"
#             f"Message:\n{message}"
#         )

#         send_mail(
#             subject=admin_subject,
#             message=admin_message,
#             from_email="Aorbo Treks <hello@aorbotreks.com>",
#             recipient_list=["hello@aorbotreks.com"],
#             fail_silently=False,
#         )
#         ctx = {
#             "name": name,
#             "email_addr": email_addr,
#             "current_year": datetime.now().year,
#             "cta_url": "https://aorbotreks.com",
#             "cta_label": "Visit Our Website",
#         }

#         html_content = render_to_string("treks_app/mail.html", ctx)
#         text_content = strip_tags(html_content)

#         reply = EmailMultiAlternatives(
#             subject="Thank you for contacting us!",
#             body=text_content,
#             from_email="Aorbo Treks <hello@aorbotreks.com>",
#             to=[email_addr],
#         )
#         reply.attach_alternative(html_content, "text/html")
#         reply.send()
#         return JsonResponse({"success": True})

#     except json.JSONDecodeError:
#         return JsonResponse(
#             {"error": "Invalid JSON payload ❌"},
#             status=400
#         )

#     except Exception as e:
#         return JsonResponse(
#             {"error": f"Failed to submit form: {str(e)}"},
#             status=500
#         )

from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from datetime import datetime
import json
import requests


def contact(request):
    # -------- GET --------
    if request.method == "GET":
        return render(
            request,
            "contact.html",
            {"RECAPTCHA_SITE_KEY": settings.RECAPTCHA_SITE_KEY},
        )

    # -------- ONLY POST --------
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=405)

    try:
        data = json.loads(request.body or "{}")

        name = data.get("name", "").strip()
        email_addr = data.get("email", "").strip()
        mobile = data.get("mobile", "").strip()
        user_type = data.get("userType", "").strip()
        message = data.get("comment", "").strip()
        recaptcha_token = data.get("recaptcha_token")

        # -------- Basic validation --------
        if not all([name, email_addr, mobile, user_type, message, recaptcha_token]):
            return JsonResponse(
                {"error": "Please fill all required fields ❌"},
                status=400
            )

        # -------- Verify reCAPTCHA --------
        recaptcha_response = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={
                "secret": settings.RECAPTCHA_SECRET_KEY,
                "response": recaptcha_token,
                "remoteip": request.META.get("REMOTE_ADDR"),
            },
            timeout=5,
        )

        recaptcha_result = recaptcha_response.json()

        # -------- HARD FAIL CONDITIONS --------
        if (
            not recaptcha_result.get("success")
            or recaptcha_result.get("score", 0) < 0.7
            or recaptcha_result.get("action") != "contact_form"
        ):
            return JsonResponse(
                {"error": "reCAPTCHA verification failed ❌"},
                status=400
            )

        # -------- Admin email --------
        admin_subject = f"New Contact Enquiry from {name}"
        admin_message = (
            f"Name: {name}\n"
            f"Email: {email_addr}\n"
            f"Mobile: {mobile}\n"
            f"I am a: {user_type}\n\n"
            f"Message:\n{message}"
        )

        send_mail(
            subject=admin_subject,
            message=admin_message,
            from_email="Aorbo Treks <hello@aorbotreks.com>",
            recipient_list=["hello@aorbotreks.com"],
            fail_silently=False,
        )

        # -------- User auto-reply --------
        ctx = {
            "name": name,
            "email_addr": email_addr,
            "current_year": datetime.now().year,
            "cta_url": "https://aorbotreks.com",
            "cta_label": "Visit Our Website",
        }

        html_content = render_to_string("treks_app/mail.html", ctx)
        text_content = strip_tags(html_content)

        reply = EmailMultiAlternatives(
            subject="Thank you for contacting us!",
            body=text_content,
            from_email="Aorbo Treks <hello@aorbotreks.com>",
            to=[email_addr],
        )
        reply.attach_alternative(html_content, "text/html")
        reply.send()

        return JsonResponse({"success": True})

    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON payload ❌"},
            status=400
        )

    except Exception as e:
        return JsonResponse(
            {"error": f"Failed to submit form: {str(e)}"},
            status=500
        )

    
def privacy_policy(request):
    return render(request, 'privacypolicy.html')
def terms_and_conditions(request):
    return render(request, 'terms_and_conditions.html')
def user_agreement(request):
    return render(request, 'user_agreement.html')

def index(request):
    whats_new = WhatsNew.objects.all().order_by('-date_posted')[:3]
    top_treks = TopTrek.objects.all()[:4]
    return render(request, 'index.html', {
        'whats_new': whats_new,
        'top_treks': top_treks,
    })

def search_trek(request):
    query = request.GET.get("q", "").strip()

    if not query:
        return redirect("home")

    trek = TrekList.objects.filter(
        Q(name__icontains=query) |
        Q(state__icontains=query) |
        Q(tags__name__icontains=query) |
        Q(trek_points__name__icontains=query)
    ).distinct().first()

    if trek:
        return redirect("card_trek_detail", slug=trek.id)

    return redirect("home")


def search_suggestions(request):
    query = request.GET.get("q", "").strip()

    if not query:
        return JsonResponse({"results": []})

    results = []
    seen = set()

    # Match trek name
    treks = (
        TrekList.objects
        .filter(name__istartswith=query)
        .order_by("name")[:10]
    )

    for trek in treks:
        if trek.id in seen:
            continue

        results.append({
            "label": trek.name,
            "type": "trek",
            "trek_name": trek.name,
            "url": reverse("card_trek_detail", args=[trek.id]),
        })
        seen.add(trek.id)

        if len(results) >= 10:
            return JsonResponse({"results": results})

    # 🔹 2. Match trek points (ManyToMany)
    treks_by_point = (
        TrekList.objects
        .filter(trek_points__name__istartswith=query)
        .distinct()[:10]
    )

    for trek in treks_by_point:
        if trek.id in seen:
            continue

        results.append({
            "label": trek.name,
            "type": "point",
            "trek_name": trek.name,
            "url": reverse("card_trek_detail", args=[trek.id]),
        })
        seen.add(trek.id)

        if len(results) >= 10:
            break

    return JsonResponse({"results": results})

def travel_your_way(request):
    selected_tag = request.GET.get("tag")

    if not selected_tag:
        return redirect('home')

    filtered_treks = [
        t for t in TrekList.objects.all()
        if "tags" in t and selected_tag in t["tags"]
    ]
    context = {
        "selected_tag": selected_tag,
        "treks": filtered_treks,
    }
    return render(request, "travel_your_way.html", context)


def card_trek_detail(request, slug):
    trek = get_object_or_404(TrekList, id=slug)

    return render(
        request,
        "card_details.html",
        {
            "trek": trek,
            "TREKS": TrekList.objects.all(),
        }
    )
