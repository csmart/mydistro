from rack.models import Arch, Repo, Group, Package, Spin, UserProfile, UserGroup, PackageRating, GroupRating, UserGroupRating
from django.contrib import admin

admin.site.register(Arch)
admin.site.register(Repo)
admin.site.register(Group)
admin.site.register(UserGroup)
admin.site.register(Package)
admin.site.register(Spin)
admin.site.register(UserProfile)
admin.site.register(PackageRating)
admin.site.register(GroupRating)
admin.site.register(UserGroupRating)
