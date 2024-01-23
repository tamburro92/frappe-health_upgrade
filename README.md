## Health Upgrade

Health customization

#### License

MIT

### How install
https://github.com/D-codE-Hub/Frappe-ERPNext-Version-14--in-Ubuntu-22.04-LTS  

bench init --frappe-branch version-14 frappe-health
cd frappe-health
bench get-app --branch  version-14 erpnext  
bench get-app --branch  version-14 healthcare  
bench get-app tamburro92/frappe-health_upgrade

bench new-site health 
bench --site health install-app erpnext  
bench --site health install-app healthcare  
bench --site health install-app health_upgrade  

bench use health
bench start

# Production
sudo bench setup production ubuntu
sudo chmod o+x /home/ubuntu
bench restart

sudo bench disable-production

### Tested with the following version
frappe 14.57.0  
erpnext 14.52.0  
healthcare 14.0.2  


# TODO after:
Configure Gruppo Medico
Configure "tax-rule" per medico
Configure ""Selling Settings" -> "cust_master_name": "Naming Series" (Creare il Nome Cliente da serie)


# update
you can run git pull bench build and then bench migrate to update doctype.


