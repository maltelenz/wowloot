from calcloot.models import Currency
import simplejson
import urllib2

def update_currencies():
    cdata = simplejson.loads(
        urllib2.urlopen("http://openexchangerates.org/latest.json").read()
        )
    ratedata = cdata['rates']
    for currency, rate in ratedata.items():
        try:
            obj = Currency.objects.get(name = currency)
            obj.rate = rate
        except Currency.DoesNotExist:
            obj = Currency(name = currency, rate = rate)
        obj.save()
    
