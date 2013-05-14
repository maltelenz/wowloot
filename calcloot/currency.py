from calcloot.models import Currency
from wowloot import settings
import simplejson
import urllib2

def update_currencies():
    cdata = simplejson.loads(
        urllib2.urlopen("http://openexchangerates.org/latest.json?app_id=" + settings.OPEN_EXCHANGE_APP_ID).read()
        )
    ratedata = cdata['rates']
    for currency, rate in ratedata.items():
        try:
            obj = Currency.objects.get(name = currency)
            obj.rate = rate
        except Currency.DoesNotExist:
            obj = Currency(name = currency, rate = rate)
        obj.save()
    
