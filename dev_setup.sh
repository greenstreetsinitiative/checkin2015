#can check distros with:
#/etc/lsb-release
#/etc/os-release

APT_GET_CMD=$(which apt-get)
#YUM_CMD=$(which yum)
#RMP_CMD=$(which rpm)
#UP2DATE_CMD=$(which up2date)
#BREW_CMD=$(which brew) # for mac users - CAUTION: UNTESTED
#OTHER_CMD=$(which <other installer>)

APT_GET_PACKAGES=$(python2.7 python-dev postgres-9.3 postgres-9.3-2.1-postgis \
                   postgres-9.3-2.1-postgis-scripts \
                   postgresql-server-dev-9.3)

PIP_INSTALLS=$(virtualenv virtualenvwrapper)

if [[ ! -z $APT_GET_CMD ]]; then
    apt-get $DEB_PACKAGE_NAME
#elif [[ ! -z $YUM_CMD ]]; then
#    yum install $YUM_PACKAGE_NAME
#elif [[ ! -z $OTHER_CMD ]]; then
#    $OTHER_CMD <proper arguments>
else
   echo "error can't install package $PACKAGE"
   exit 1;
fi



