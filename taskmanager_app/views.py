from django.contrib.auth.decorators import login_required

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.middleware.csrf 		import get_token
from django.shortcuts import render

@login_required
def ptm_index(request):
	params = {'csrf_token': get_token(request)}
	return render(request, 'ptmTemplates/index.html', params)
	#return render_to_response('ptmTemplates/index.html', params)