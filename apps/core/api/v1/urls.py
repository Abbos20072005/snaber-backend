from django.urls import path

from apps.core.api.v1.views.aboutus import AboutUsImageView, AboutUsView
from apps.core.api.v1.views.contacts import ContactView
from apps.core.api.v1.views.legal import LegalClientsInfoView
from apps.core.api.v1.views.faqs import FaqCreateListView, FaqDetailUpdateDeleteView
from apps.core.api.v1.views.countries import CountryListView

urlpatterns = [
    path("contact/", ContactView.as_view(), name="contact"),
    path("faq/", FaqCreateListView.as_view(), name="faq"),
    path("faq/<int:id>/", FaqDetailUpdateDeleteView.as_view(), name="faq-detail"),
    path("about-us/", AboutUsView.as_view(), name="about"),
    path("about-us/image/", AboutUsImageView.as_view(), name="about-image"),
    path("legal-info/", LegalClientsInfoView.as_view(), name="legal-info"),
    path("countries/", CountryListView.as_view(), name="country-list"),
]
