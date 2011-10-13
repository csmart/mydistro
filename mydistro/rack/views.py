from django.http import HttpResponse

def packages_index(request):
  return HttpResponse("Hello from packages_index")

def packages_detail(request, package_id):
  return HttpResponse("Hello from packages_detail")
