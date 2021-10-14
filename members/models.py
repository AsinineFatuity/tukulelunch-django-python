from django.db import models
from django.db.models.deletion import CASCADE
from django.urls import reverse

import datetime

#Category model of the items that I will analogously add and sell to church members
class Category(models.Model):
    name = models.CharField(max_length=250, unique=True)
    slug = models.SlugField(max_length=250, unique=True )
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='category', blank=True)
    #all my category images will be uploaded to the category folder
    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'
    def get_url(self):
        return reverse('items_by_category', args = [self.slug])
    def __str__(self):
        return self.name
#Item model for all the Items (analogous to products) that I analogously "sell" to the church members 
class Item(models.Model):
     name = models.CharField(max_length=250, unique=True)
     slug = models.SlugField(max_length=250, unique=True )
     category = models.ForeignKey(Category, on_delete =models.CASCADE)
     description = models.TextField(blank=True)
     price = models.DecimalField(max_digits=10, decimal_places=2)
     image = models.ImageField(upload_to='item', blank=True)
     #all my item images will be uploaded to the item folder
     stock = models.IntegerField()
     available = models.BooleanField(default=True)
     created = models.DateTimeField(auto_now_add=True)
     updated = models.DateTimeField(auto_now=True)
     #created and updated for when these happened to the product fields will be automatically updated
     class Meta:
        ordering = ('name',)
        verbose_name = 'item'
        verbose_name_plural = 'items'
     def get_url(self):
        #the first is the category slug, the second is the item slug
        return reverse('item_detail', args = [self.category.slug, self.slug])
     def __str__(self):
        return self.name
#my Pledge model is analogous to a cart
class Pledge(models.Model):
    pledge_id = models.CharField(max_length=250, blank = True)
    date_added = models.DateField(auto_now_add = True)

    class Meta:
        db_table = 'Pledge'
        ordering = ['date_added']
    def __str__(self):
        return self.pledge_id
#my PledgeItem model is analogous to a cart item
class PledgeItem(models.Model):
    item = models.ForeignKey(Item, on_delete = models.CASCADE)  
    pledge = models.ForeignKey(Pledge, on_delete = models.CASCADE)
    quantity = models.IntegerField()
    active = models.BooleanField(default = True)

    class Meta:
        db_table = 'PledgeItem'
    def sub_total(self):
        return self.item.price * self.quantity
    def __str__(self):
        return self.item 
#Commitment Model analogous to Orders in the e-commerce world
class Commitment(models.Model):
    token = models.CharField(max_length=250, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2,verbose_name='KES Committed Total')
    name = models.CharField(max_length=20, blank=True)
    email_address = models.EmailField(max_length=250, blank=True,verbose_name='Email Address')
    phone_number = models.CharField(max_length=250, blank=True)
    ministry = models.CharField(max_length=20, blank=True)
    commitment_date = models.DateField()
    deadline = models.DateField()
    class Meta:
        db_table = 'Commitment'
        ordering = ['-commitment_date']
    def __str__(self):
        return str(self.id)
    #to add the deadline to say a week from the commitment date
    def save(self, *args, **kwargs):
        if self.deadline is None:
            self.deadline = self.commitment_date + datetime.timedelta(days=7)
        super(Commitment, self).save(*args, **kwargs)
#CommittedItem Model  analogous to Ordered Items in the e-commerce world
#commitment is analogous to the order as pertains to foreign key
class CommittedItem(models.Model):
    item = models.CharField(max_length=250)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2,verbose_name='KES Price')
    commitment = models.ForeignKey(Commitment,on_delete=CASCADE)
    class Meta:
        db_table='CommittedItem'
    def sub_total(self):
        return self.quantity * self.price
    def __str__(self):
        return self.item 
