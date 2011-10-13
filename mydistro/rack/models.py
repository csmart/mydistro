from django.db import models
from django.contrib.auth.models import User

#
# SYSTEM SPECIFIC MODELS
#
class Arch(models.Model):
  name = models.CharField(max_length=16)
  description = models.TextField()

  def __unicode__(self):
    return self.name

  class Meta:
    ordering = ('name',)



class Repo(models.Model):
  name = models.CharField(max_length=256)
  url = models.CharField(max_length=256)

  arch = models.ManyToManyField(Arch)

  version = models.CharField(max_length=256)

  modify_date = models.DateTimeField('date modified');

  def __unicode__(self):
    return self.name

  class Meta:
    ordering = ('name',)



class Package(models.Model):
  # package summary
  name = models.CharField(max_length=256)
  description = models.TextField()
  version = models.CharField(max_length=32)
  license = models.CharField(max_length=256)
  url = models.CharField(max_length=256)

  # package rating
  score_aggregate = models.FloatField(default=0)
  score_votes = models.IntegerField(default=0)

#  score_popularity = models.IntegerField(default=0)

  # pins
#  total_pins_add = models.IntegerField(default=0)
#  total_pins_rem = models.IntegerField(default=0)

  # repositories can contain many packages and packages can belong to multiple repositories.
  repository = models.ManyToManyField(Repo, through='PackageArch')

  modify_date = models.DateTimeField('date modified')

  def __unicode__(self):
    return self.name

  class Meta:
    ordering = ('name',)





class PackageArch(models.Model):
  repo = models.ForeignKey(Repo)
  package = models.ForeignKey(Package)

  arch = models.ForeignKey(Arch)

  package_size = models.IntegerField()
  installed_size = models.IntegerField()

  package_uuid = models.CharField(max_length=64)



class Group(models.Model):
  name = models.CharField(max_length=256)
  description = models.TextField()

  modify_date = models.DateTimeField('date modified');

  packages = models.ManyToManyField(Package)

  # group rating
  score_aggregate = models.FloatField(default=0)
  score_votes = models.IntegerField(default=0)

  def __unicode__(self):
    return self.name

  class Meta:
    ordering = ('name',)



#
# USER SPECIFIC MODELS
#

class Spin(models.Model):
  name = models.CharField(max_length=256, help_text='The name of this spin.')
  language = models.TextField(default='english')
  timezone = models.TextField(default='Australia/Sydney')
  root_passwd = models.TextField()
  base_kickstart = models.TextField()

  group_add = models.ManyToManyField(Group)
  package_add = models.ManyToManyField(PackageArch)

  def __unicode__(self):
    return self.name

  class Meta:
    ordering = ('name',)



class UserGroup(Group):
  visibility = models.IntegerField(default=0)



class UserProfile(models.Model):
  # user's details
  url = models.URLField()
  alias = models.TextField()
  user = models.ForeignKey(User, unique=True)

  # user's spins
  spins = models.ManyToManyField(Spin)

  # user's custom groups
  user_groups = models.ManyToManyField(UserGroup, related_name='user_groups')

  # user's ratings
  package_ratings = models.ManyToManyField(Package, through='PackageRating')
  group_ratings = models.ManyToManyField(Group, through='GroupRating')
  user_group_ratings = models.ManyToManyField(UserGroup, through='UserGroupRating', related_name='user_group_ratings')


#
# RATINGS
#
class Rating(models.Model):
  comment = models.TextField(help_text='Your comments on this package.')
  score = models.IntegerField(default=0, help_text='Your score for this package.')

  modify_date = models.DateTimeField('date modified')



class PackageRating(Rating):
  user_profile = models.ForeignKey(UserProfile)
  package = models.ForeignKey(Package)



class GroupRating(Rating):
  user_profile = models.ForeignKey(UserProfile)
  group = models.ForeignKey(Group)



class UserGroupRating(Rating):
  user_profile = models.ForeignKey(UserProfile)
  user_group = models.ForeignKey(UserGroup)


