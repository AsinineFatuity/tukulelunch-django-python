from django.contrib import admin
from .models import Category,Item,Commitment,CommittedItem
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
        ('Price',{'fields':['price'],}),    
    ]
    readonly_fields=['item','quantity','price']
    #remove the delete option
    can_delete = False
    #remove extra blank rows
    max_num = 0
    


@admin.register(Commitment)
class CommitmentAdmin(admin.ModelAdmin):
    list_display = ['name','phone_number','ministry','email_address','commitment_date']
    list_display_links = ('name',)
    search_fields = ['name','ministry']
    readonly_fields=['name','email_address','ministry','phone_number','commitment_date','total','deadline','token']
    fieldsets = [
        ('COMMITMENT INFORMATION',{'fields':['total'],}),
        ('ADDRESS INFORMATION',{'fields':['name','phone_number','email_address'],}),
        ('TIMELINES INFORMATION',{'fields':['commitment_date','deadline'],}),
    ]
    inlines = [
        CommittedItemAdmin
    ]
    def has_delete_permission(self, request,obj=None):
        return False
    def has_add_permission(self, request):
        return False
