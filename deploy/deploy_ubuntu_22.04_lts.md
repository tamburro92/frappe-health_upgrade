# Frappe-ERPNext-Version-14--in-Ubuntu-22.04-LTS
A complete Guide to Install Frappe/ERPNext version 14  in Ubuntu 22.04 LTS

sudo apt update -y
sudo apt upgrade -y

sudo apt-get install git

sudo apt-get install python3-dev
sudo apt-get install python3-setuptools python3-pip
sudo apt-get install virtualenv
sudo apt install python3.10-venv
#sudo apt install python3-venv


sudo apt-get install software-properties-common
sudo apt install mariadb-server
sudo mysql_secure_installation


  In order to log into MariaDB to secure it, we'll need the current
  password for the root user. If you've just installed MariaDB, and
  haven't set the root password yet, you should just press enter here.

  Enter current password for root (enter for none): # PRESS ENTER
  OK, successfully used password, moving on...
  
  
  Switch to unix_socket authentication [Y/n] Y
  Enabled successfully!
  Reloading privilege tables..
   ... Success!

  Change the root password? [Y/n] Y
  New password: 
  Re-enter new password: 
  Password updated successfully!
  Reloading privilege tables..
   ... Success!

  Remove anonymous users? [Y/n] Y
   ... Success!

   Disallow root login remotely? [Y/n] Y
   ... Success!

   Remove test database and access to it? [Y/n] Y
   - Dropping test database...
   ... Success!
   - Removing privileges on test database...
   ... Success!

   Reload privilege tables now? [Y/n] Y
   ... Success!


sudo apt-get install libmysqlclient-dev


sudo nano /etc/mysql/mariadb.conf.d/50-server.cnf

    [server]
    user = mysql
    pid-file = /run/mysqld/mysqld.pid
    socket = /run/mysqld/mysqld.sock
    basedir = /usr
    datadir = /var/lib/mysql
    tmpdir = /tmp
    lc-messages-dir = /usr/share/mysql
    bind-address = 127.0.0.1
    query_cache_size = 16M
    log_error = /var/log/mysql/error.log

    [mysqld]
    innodb-file-format=barracuda
    innodb-file-per-table=1
    innodb-large-prefix=1
    character-set-client-handshake = FALSE
    character-set-server = utf8mb4
    collation-server = utf8mb4_unicode_ci      

    [mysql]
    default-character-set = utf8mb4

sudo service mysql restart

sudo apt-get install redis-server

sudo apt install curl 
curl https://raw.githubusercontent.com/creationix/nvm/master/install.sh | bash
source ~/.profile
nvm install 16

sudo apt-get install npm
sudo npm install -g yarn

sudo apt-get install xvfb libfontconfig wkhtmltopdf

sudo -H pip3 install frappe-bench==5.10.1

### Install wkhtmltopdf (with patched qt) (NOT FROM APT)
https://discuss.frappe.io/t/print-pdf-header-footer-not-showing-letterhead/85030/6
sudo apt-get install xfonts-75dpi
wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.jammy_arm64.deb
sudo dpkg -i wkhtmltox_0.12.6.1-2.jammy_arm64.deb
sudo cp /usr/local/bin/wkhtmlto* /usr/bin/
sudo chmod a+x /usr/bin/wk*

### Install Site
bench init --frappe-branch version-14 frappe-venus
bench new-site venus
bench use venus

bench get-app --branch  version-14 erpnext
bench get-app --branch  version-14 healthcare
bench get-app tamburro92/frappe-venus

bench --site venus install-app erpnext healthcare venus 

### import data
...

### Step 16 setup production
    
sudo bench setup production {user}
bench restart

#bench disable-production


### BACKUP / RESTORE
bench --site {site} backup --with-files
bench --site {site} restore {path/to/database/file}
     --with-public-files {path/to/public/archive}
     --with-private-files {path/to/private/archive}

     --force

### UPDATE IN PRODUCTION
bench update --reset



