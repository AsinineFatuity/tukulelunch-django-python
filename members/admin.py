from django.contrib import admin
from django.contrib.admin.decorators import display
from .models import Category,Item,Commitment,CommittedItem,Payment,GhostPayment

#customize the admin
admin.site.site_header = "Tukule Lunch Admin"
admin.site.site_title = "Tukule Lunch"
admin.site.index_title = "Admin Portal"
# Register your models here.

class ItemAdmin(admin.ModelAdmin):
    list_display=['name','price','stock','available','created','updated']
    list_editable=['price','stock','available']
    prepopulated_fields={'slug':('name',)}
    list_per_page=20
admin.site.register(Item,ItemAdmin)
class CategoryAdmin(admin.ModelAdmin):
    list_display=['name','slug']
    prepopulated_fields={'slug':('name',)}
    list_per_page=20
admin.site.register(Category,CategoryAdmin)

class CommittedItemAdmin(admin.TabularInline):
    model = CommittedItem
    fieldsets = [
        ('Item',{'fields':['item'],}),
        ('Quantity',{'fields':['quantity'],}),
        ('Unit Price',{'fields':['price'],}), 
    ]
    readonly_fields=['item','quantity','price']
    #remove the delete option
    can_delete = False
    #remove extra blank rows
    max_num = 0
#@admin.register(Payment)
class PaymentAdmin(admin.TabularInline):
    model = Payment
    readonly_fields = ['total_paid']
    list_editable = ['amount_paid','date_paid']
    fieldsets = [
        ('Amount Paid',{'fields':['amount_paid'],}),
        ('Date Paid',{'fields':['date_paid'],}),
        ('Total Paid',{'fields':['total_paid'],}), 
    ]
    def get_name(self,obj):
        return obj.pay_commitment.name
    def get_phone(self,obj):
        return obj.pay_commitment.phone_number
    def has_delete_permission(self, request,obj=None):
        return False
    def has_add_permission(self, request,obj=None):
        return True
    #remove the delete option
    can_delete = False
@admin.register(Commitment)
class CommitmentAdmin(admin.ModelAdmin):
    list_display = ['id','name','phone_number','ministry','commitment_date','honoured']
    list_display_links = ('name',)
    list_editable = ['honoured']
    search_fields = ['name','ministry','phone_number']
    readonly_fields=['name','email_address','ministry','phone_number','commitment_date','total','deadline','token']
    fieldsets = [
        ('COMMITMENT INFORMATION',{'fields':['total'],}),
        ('ADDRESS INFORMATION',{'fields':['name','phone_number','email_address'],}),
        ('TIMELINES INFORMATION',{'fields':['commitment_date','deadline'],}),
    ]
    inlines = [
        CommittedItemAdmin,PaymentAdmin
    ]
    def has_delete_permission(self, request,obj=None):
        return False
    def has_add_permission(self, request):
        return False     
@admin.register(GhostPayment)
class GhostPaymentAdmin(admin.ModelAdmin):
    list_display = ['name','phone_number','amount_paid','date_paid']
    def has_delete_permission(self, request,obj=None):
        return False
