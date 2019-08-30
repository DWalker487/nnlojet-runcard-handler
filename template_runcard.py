import os
dictCard = {
    &dictionary&
}

&dbname&
arcbase = os.path.expanduser("~/jobscripts/.arc/jobs_{0}.dat".format(os.path.basename(__file__).replace(".py","")))

# Optional values
# sockets_active = 5
# port = 8888

# You can overwrite any value in your header by specifying the same attribute here. 
# E.g to set the number of jobs 99999 for this runcard, you could include the line
# producRun = 999999

# You can even import and use other functions here, such as the following to auto pick the
# CE with most cores free
# import get_site_info
# ce_base = get_site_info.get_most_free_cores()
# or use the aliases defined at the top of get_site_info.py
# ce_base = get_site_info.liverpool
import src.dbapi as dbapi
baseSeed = dbapi.get_next_seed(dbname=dbname)
