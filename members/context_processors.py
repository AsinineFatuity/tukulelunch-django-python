from .models import Category,PledgeItem,Pledge
from .views import pledge_id_fn

def counter(request):
    item_count=0
    if 'admin' in request.path:
        return {}
    else:
        try:
            pledge=Pledge.objects.filter(pledge_id=pledge_id_fn(request)) #specify pledge object in the current session
            #find the current pledged_item in the session and return only a single pledge_items object
            pledge_items=PledgeItem.objects.all().filter(pledge=pledge[:1]) 
            for pledge_item in pledge_items:
                item_count+=pledge_item.quantity
        except Pledge.DoesNotExist:
            item_count=0
    return dict(item_count=item_count)
def menu_links(request):
    links=Category.objects.all()
    return dict(links=links)
