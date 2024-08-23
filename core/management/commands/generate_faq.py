from django.core.management.base import BaseCommand
from core.models import Faq

class Command(BaseCommand):
    help = 'Generate 8 legitimate FAQs'

    def handle(self, *args, **kwargs):
        faqs = [
            {"question": "What is the return policy?", "answer": "You can return any painting within 30 days for a full refund."},
            {"question": "Do you offer international shipping?", "answer": "Yes, we ship our paintings worldwide. Shipping fees may vary based on location."},
            {"question": "How can I track my order?", "answer": "Once your order is shipped, we will send you a tracking number via email."},
            {"question": "What payment methods do you accept?", "answer": "We accept Visa, MasterCard, American Express, PayPal, and Stripe."},
            {"question": "Are the paintings framed?", "answer": "Some paintings are framed, while others are not. Please check the product description for details."},
            {"question": "Can I request a custom painting?", "answer": "Yes, we offer custom painting services. Please contact us with your requirements."},
            {"question": "How do I contact customer support?", "answer": "You can contact our customer support via email at support@yourdomain.com or call us at +1-234-567-8901."},
            {"question": "What is the delivery time?", "answer": "Delivery times vary by location but typically range from 5-10 business days."}
        ]

        for faq_data in faqs:
            Faq.objects.create(**faq_data)

        self.stdout.write(self.style.SUCCESS('Successfully created 8 FAQs'))
