#!/usr/bin/python

import sys, os, glob, re, xml.dom.minidom

from datetime import datetime
import sqlite3

sys.path.append('/home/test/mydistro.git')
os.environ['DJANGO_SETTINGS_MODULE'] = 'mydistro.settings'

from django.core.management import setup_environ
from mydistro import settings
from mydistro.rack.models import Package, Repo, Group, Arch, PackageDetails

setup_environ(settings)

# read a filesystems yum database for mydistro

base_path = '/var/cache/yum'

groups_regex = re.compile(r"\-comps\-.*xml$")


def import_static_values():
  a = Arch(name='noarch', description='Architecture Independant')
  a.save()

  a = Arch(name='i386', description='32-bit Architecture')
  a.save()

  a = Arch(name='i686', description='32-bit Architecture')
  a.save()

  a = Arch(name='x86_64', description='64-bit Architecture')
  a.save()


def import_repos_from_path(path):
  for f in glob.glob( os.path.join(path, '*') ):
    if os.path.isdir(f):
      import_repos_from_path(f)
    elif f[-14:] == 'primary.sqlite':
      import_new_repo(f)



def import_groups_from_path(path):
  for f in glob.glob( os.path.join(path, '*') ):
    if os.path.isdir(f):
      import_groups_from_path(f)
    elif groups_regex.search(f):
      import_new_group(f)



def import_new_group(path):
  group = path[len(base_path) + 1:]
  group_components = group.split('/')

  # open XML
  dom = xml.dom.minidom.parse(path)

  for n in dom.getElementsByTagName('group'):
    g = None

    for c in n.childNodes:
      if c.nodeName == 'name' and not c.attributes and c.firstChild != None:
        group_name = c.firstChild.nodeValue

        g = Group.objects.filter(name=group_name)
        if not g:
          g = Group(name=group_name, description='', modify_date=datetime.now())
        else:
          g = g[0]

      elif c.nodeName == 'description' and not c.attributes and c.firstChild != None:
        g.description = c.firstChild.nodeValue

      elif c.nodeName == 'packagelist' and c.firstChild != None:
        if not g:
          continue

        g.save()
        for r in c.childNodes:
          if r.nodeName == 'packagereq' and r.firstChild != None:
            package_name = r.firstChild.nodeValue

            p = Package.objects.filter(name=package_name)

            if p.count() == 1:
              g.packages.add(p[0])
              g.save()
            elif p.count() > 1:
              print "Ambiguous list of package names for: %s. More than 1 encounted." % (package_name)




def import_new_repo(path):
  repo = path[len(base_path) + 1:]
  repo_components = repo.split('/')

  # let's build the arch object
  repo_arch = repo_components[0]

  a = Arch.objects.filter(name=repo_arch)
  if not a:
    a = Arch(name=repo_arch)
    a.save()
  else:
    a = a[0]

  repo_name = repo_components[2]
  repo_ver = repo_components[1]

  # let's build the repo object (but check if it exists first)
  r = Repo.objects.filter(name=repo_name, arch=a)

  if not r:
    r = Repo(name=repo_name, version=repo_ver, modify_date=datetime.now())
    r.save()
    r.arch.add(a)
    r.save()
  else:
    r = r[0]

  '''
  # print some repository love
  print "Repo: %s" % (repo_components[2])
  print "  Arch: %s" % (repo_components[0])
  print "  Version: %s" % (repo_components[1])
  print "  Primary DB: %s" % (path)
  '''

  # open the database for reading and scouring
  conn = sqlite3.connect(path)
  c = conn.cursor()

  c.execute('SELECT name, version, description, rpm_license, url, pkgId, pkgKey, arch, size_installed, size_package FROM packages')

  for l in c:
    # see if our package already exists
    p = Package.objects.filter(name=l[0])

    if l[2] is None:
      package_description = "";
    else:
      package_description = l[2]

    if l[4] is None:
      package_url = "";
    else:
      package_url = l[4]

    '''
    # print some package love
    print "Package: %s" % (l[0])
    print "  Version: %s" % (l[1])
    print "  URL: %s" % (package_url)
    print "  Description: %s" % (l[2])
    print "  License: %s" % (l[3])
    print "  Installed Size: %s" % (l[5])
    print "  UUID: %s" % (l[6])
    '''
    # create as required
    if not p:
      p = Package(name=l[0], version=l[1], description=package_description, license=l[3], url=package_url, package_uuid=l[5], modify_date=datetime.now())
      p.save()

      p_a = Arch.objects.filter(name=l[7])
      if not p_a:
        p_a = Arch(name=l[7], description='unknown arch, please fix.')
        p_a.save()
      else:
        p_a = p_a[0]

      # establish the details specific to the package/arch/repo combination
      d = PackageDetails(package=p, repo=r, arch=p_a, installed_size=l[8], package_size=l[9])
      d.save()

  c.close()


# time this
time_start = datetime.now()

print "Importing static values."
import_static_values()

# start the scan
print "Importing repo information from path: %s." % (base_path)
import_repos_from_path(base_path);

print "Importing group information from path: %s." % (base_path)
import_groups_from_path(base_path);

time_delta = datetime.now() - time_start

print "Total Time: %s" % (str(time_delta))

