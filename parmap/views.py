from django.shortcuts import render
from django.template import RequestContext, loader
from django.shortcuts import render_to_response

# Create your views here.
def other_rs(request):
    context_dict = {
        "map_type": request.GET['keywords__slug__in']
    }
    
    return render_to_response('parmap/other_rs.html', RequestContext(request, context_dict))