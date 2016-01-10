import hashlib
from operator import itemgetter
from django.db import models

class UnsavedForeignKey(models.ForeignKey):
    # A ForeignKey which can point to an unsaved object
    allow_unsaved_instance_assignment = True

class Person(models.Model):
    name = models.CharField(max_length = 200)
    finished = models.BooleanField(default = False)

    def __unicode__(self):
        return self.name

class Currency(models.Model):
    name = models.CharField(max_length = 5)
    rate = models.FloatField()

    class Meta:
        ordering = ["name"]

    def __unicode__(self):
        return self.name

def get_default_currency():
    return Currency.objects.get(name="USD")
    
class Calculation(models.Model):
    name = models.CharField(max_length = 200)
    creation_date = models.DateTimeField(editable = False)
    hashtag = models.CharField(max_length = 20, editable = False)
    involved = models.ManyToManyField(Person, verbose_name = 'persons involved', related_name = 'involved')
    currency = models.ForeignKey(Currency, default = get_default_currency)
    
    def __unicode__(self):
        return self.name + "(" + self.hashtag + ")"
    
    def code_hashtag(self):
        # Need to replace all the non-ascii characters here, or md5 will throw error
        return hashlib.md5(''.join([i if ord(i) < 128 else '?' for i in self.name])).hexdigest()[:10]

    def balance(self):
        owing_dict = {}
        for e in self.expense_set.all():
            for owing in e.owed():
                try:
                    owing_dict[owing[0], owing[1]] += owing[2]
                except KeyError:
                    try:
                        owing_dict[owing[1], owing[0]] -= owing[2]
                    except KeyError:
                        owing_dict[owing[0], owing[1]] = owing[2]
        positive_owing_dict = {}
        for ((a, b), v) in owing_dict.items():
            if v>=0:
                positive_owing_dict[(a,b)] = v
            else:
                positive_owing_dict[(b,a)] = -v
                
        person_balance = {}
        for ((a, b), v) in positive_owing_dict.items():
            try:
                person_balance[a] -= v
            except KeyError:
                person_balance[a] = -v
            try:
                person_balance[b] += v
            except KeyError:
                person_balance[b] = v

        return person_balance

    def transfers(self):
        def sortbalance(b):
            return sorted(b.iteritems(), key = itemgetter(1))
        
        def largest_minus(b):
            return sortbalance(b)[0][0]

        def smallest_larger(b, comp):
            for p, a in sortbalance(b):
                if a + comp > 0:
                    return p
            return sortbalance(b)[-1][0]
        
        def nonzero_exists(b):
            sortedb = sortbalance(b)
            if len(b) == 0:
                return False
            if len(sortedb) == 1:
                return abs(sortedb[0][1]) > 0.001
            return abs(sortedb[0][1]) > 0.001 or abs(sortedb[-1][1]) > 0.001
        balance = self.balance()
        computed_transfers = set()
        i=0
        while nonzero_exists(balance) and i<10:
            i+=1
            largestminus = largest_minus(balance)
            smallestlarger = smallest_larger(balance, balance[largestminus])
            transferamount = max(balance[largestminus], -balance[smallestlarger])
            computed_transfers.add((largestminus, smallestlarger, -transferamount))
            balance[largestminus] -= transferamount
            balance[smallestlarger] += transferamount
        balance_check = self.balance()
        for f,t,a in computed_transfers:
                balance_check[f] += a
                balance_check[t] -= a
        for p, b in balance_check.items():
            assert(abs(b) < 0.01)

        return computed_transfers
        
    def is_finished(self):
        return all([f.finished for f in self.involved.all()])

    def new_expense(self):
        try:
            latest_expense = self.expense_set.all().order_by('id').reverse()[0]
            new_currency = latest_expense.currency
            new_person = latest_expense.person
        except IndexError:
            new_currency = self.currency
            try:
                new_person = self.involved.all()[0]
            except IndexError:
                new_person = Person()

        new_expense = Expense(calculation = self, currency = new_currency, person = new_person)
        return new_expense

    def save(self, *args, **kwargs):
        #Update the hashtag
        self.hashtag = self.code_hashtag()
        super(Calculation, self).save(*args, **kwargs) #Call the original save method

class Expense(models.Model):
    calculation = models.ForeignKey(Calculation)
    person = UnsavedForeignKey(Person, verbose_name = 'person who paid', related_name = 'paying')
    name = models.CharField(max_length = 300, blank = True)
    amount = models.FloatField()
    currency = models.ForeignKey(Currency)
    benefactors = models.ManyToManyField(Person, verbose_name = 'persons benefiting', related_name = 'benefactors')
    
    def amount_in_calculation_currency(self):
        #convert into calculation currency
        return self.amount * (self.calculation.currency.rate / self.currency.rate)

    def owed(self):
        got_money_count = self.benefactors.count()
        return [(b, self.person, self.amount_in_calculation_currency()/got_money_count) for b in self.benefactors.all() if b != self.person]
    

    def __unicode__(self):
        return self.person.name + " paid " + unicode(self.amount) + " " + self.currency.name




# Create your models here.
