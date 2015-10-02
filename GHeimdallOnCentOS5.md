# Instructions for using GHeimdall on CentOS5 #

  * First, enable epel repository for TurboGears stuff.
```
# wget http://download.fedora.redhat.com/pub/epel/5/i386/epel-release-5-2.noarch.rpm
# rpm -ivh epel-release-5-2.noarch.rpm
```

  * Second, enable GHeimdall repository.
```
# wget http://gheimdall.googlecode.com/files/gheimdall-repos-5-3.noarch.rpm
# rpm -ivh gheimdall-repos-5-3.noarch.rpm
```
  * Finally, install gheimdall package, configure gheimdall appropriately, and restart httpd. That's all.
```
# yum install gheimdall
# vi /usr/lib/python2.4/site-packages/gheimdall/config/app.cfg
# /etc/init.d/httpd restart
```

  * Now, GHeimdall is not compatible with SELinux. You may have to set SELinux off.
```
# setenforce permissive
```

  * You can access GHeimdall through the URL http://example.com/gheimdall/

Please enjoy!