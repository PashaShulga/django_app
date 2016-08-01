# from django.shortcuts import render_to_response
# from web.views import get_perm
# from django.contrib import auth
#
#
# def api_home(request):
#     args = {}
#     request_object = auth.get_user(request)
#     if request_object:
#         args.update(get_perm(request))
#     return render_to_response('api.html', args)