from django.contrib import admin
from .models import SellerRequest,Faq, Setting,Address, Artist,Testemonial, Category, Tag, Painting, Order, OrderItem, Review, Notification,PromoCode,PromoCodeUsage

@admin.register(SellerRequest)
class SellerRequestAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'business_name', 'country', 'created_at')
    search_fields = ('full_name', 'email', 'business_name', 'country')
    list_filter = ('country', 'created_at')
    readonly_fields = ('full_name', 'email', 'phone', 'business_name', 'country', 'description', 'message', 'website', 'created_at')
    ordering = ('-created_at',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class PaintingAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'category', 'price', 'created_at', 'isNew', 'show')
    list_filter = ('artist', 'category', 'tags', 'created_at', 'show')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('tags', 'fav')

    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'price', 'artist', 'category', 'image', 'tags', 'slug', 'show', 'fav')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('created_at',),
        }),
    )

    readonly_fields = ('created_at',)

admin.site.register(Painting, PaintingAdmin)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ('total',)
    fields = ('painting', 'quantity', 'total')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'status', 'subtotal', 'discount', 'total', 'shipping_address')
    list_filter = ('status', 'created_at', 'payed_at', 'shipped_at', 'delivered_at')
    search_fields = ('user__username', 'uuid')
    readonly_fields = ('created_at', 'uuid', 'subtotal', 'discount', 'total', 'shipping_address', 'get_status_date')

    fieldsets = (
        (None, {
            'fields': ('user', 'uuid', 'created_at', 'payed_at', 'shipped_at', 'delivered_at', 'status', 'address', 'promo_code')
        }),
        ('Financials', {
            'fields': ('subtotal', 'discount', 'total')
        }),
    )

    inlines = [OrderItemInline]

admin.site.register(Order, OrderAdmin)

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'painting', 'quantity', 'total')
    list_filter = ('order', 'painting')
    search_fields = ('order__uuid', 'painting__title')

admin.site.register(OrderItem, OrderItemAdmin)


class AddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'first_name', 'last_name', 'email', 'address', 'country', 'state', 'zip_code', 'default', 'status', 'created_at', 'shipping_price')
    list_filter = ('status', 'country', 'state', 'created_at')
    search_fields = ('user__username', 'first_name', 'last_name', 'email', 'address', 'zip_code')
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('user', 'first_name', 'last_name', 'email', 'address', 'address2', 'country', 'state', 'zip_code', 'message', 'shipping_price', 'default', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )

admin.site.register(Address, AddressAdmin)


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'is_read', 'is_message', 'created_at')
    list_filter = ('is_read', 'is_message', 'created_at', 'user')
    search_fields = ('user__username', 'title', 'message')
    readonly_fields = ('created_at',)

    fieldsets = (
        (None, {
            'fields': ('user', 'title', 'message', 'is_read', 'is_message')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
        }),
    )

admin.site.register(Notification, NotificationAdmin)


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'painting', 'created_at')
    list_filter = ('created_at', 'user', 'painting')
    search_fields = ('user', 'comment', 'painting__title')
    readonly_fields = ('created_at',)

    fieldsets = (
        (None, {
            'fields': ('user', 'painting', 'comment')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
        }),
    )

admin.site.register(Review, ReviewAdmin)

class PromoCodeUsageInline(admin.TabularInline):
    model = PromoCodeUsage
    extra = 1

class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount', 'active', 'usage_limit')
    search_fields = ('code',)
    list_filter = ('active',)
    inlines = [PromoCodeUsageInline]

class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name', 'birth_date')
    search_fields = ('name',)
    list_filter = ('birth_date',)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}




class SettingAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'show']
    list_filter = ['show']
    search_fields = ['name', 'email']
    fieldsets = (
        ('General Information', {
            'fields': ('name', 'email', 'phone', 'address')
        }),
        ('Home Page Settings', {
            'fields': (
                'home_painting_hero_1', 'home_painting_hero_2', 'home_painting_hero_3',
                'home_painting_list_1', 'home_painting_list_2', 'home_painting_list_3',
                'home_artist_1', 'home_artist_2', 'home_artist_3',
                'home_image_section_1', 'become_seller_video'
            )
        }),
        ('Story Section', {
            'fields': (
                'home_story_1_image', 'home_story_1_title',
                'home_story_2_image', 'home_story_2_title',
                'home_story_3_image', 'home_story_3_title',
                'home_story_4_image', 'home_story_4_title',
                'home_story_5_image', 'home_story_5_title'
            )
        }),
        ('Core Values', {
            'fields': (
                'core_value_1_title', 'core_value_1_title_description', 'core_value_1_image',
                'core_value_2_title', 'core_value_2_title_description', 'core_value_2_image',
                'core_value_3_title', 'core_value_3_title_description', 'core_value_4_image'
            )
        }),
        ('Testimonials', {
            'fields': ('testimony_1', 'testimony_2', 'testimony_3')
        }),
        ('About Us', {
            'fields': ('hero_about_us_image', 'hero_about_us_description', 'about_image_1', 'about_image_2', 'about_image_3', 'about_story')
        }),
        ('Social Media', {
            'fields': ('facebook', 'twitter', 'instagram', 'pinterest')
        }),
        ('Other Settings', {
            'fields': ('open_hours', 'preview_image', 'team', 'hero_contact_image', 'contact_description', 'show')
        }),
    )



@admin.register(Faq)
class FaqAdmin(admin.ModelAdmin):
    list_display = ('question', 'show', 'created_at', 'updated_at')
    list_filter = ('show', 'created_at')
    search_fields = ('question',)



admin.site.register(Setting, SettingAdmin)



admin.site.register(PromoCode, PromoCodeAdmin)
admin.site.register(Artist, ArtistAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Testemonial)