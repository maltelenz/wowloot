import hashlib
from django.db import models

class Person(models.Model):
    name = models.CharField(max_length = 200)

    def __unicode__(self):
        return self.name

class Calculation(models.Model):
    name = models.CharField(max_length = 200)
    creation_date = models.DateTimeField(editable = False)
    hashtag = models.CharField(max_length = 20, editable = False)
    involved = models.ManyToManyField(Person, verbose_name = 'persons involved', related_name = 'involved')

    def __unicode__(self):
        return self.name + "(" + self.hashtag + ")"

    def code_hashtag(self):
        return hashlib.md5(self.name).hexdigest()[:10]

    def finalcount(self):
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

    def new_expense(self):
        try:
            latest_expense = self.expense_set.all().order_by('id').reverse()[0]
            new_currency = latest_expense.currency
            new_person = latest_expense.person
        except IndexError:
            new_currency = Currency.objects.get(name="USD")
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

class Currency(models.Model):
    name = models.CharField(max_length = 5)

    def __unicode__(self):
        return self.name

class Expense(models.Model):
    calculation = models.ForeignKey(Calculation)
    person = models.ForeignKey(Person, verbose_name = 'person who paid', related_name = 'paying')
    name = models.CharField(max_length = 300, blank = True)
    amount = models.FloatField()
    currency = models.ForeignKey(Currency)
    benefactors = models.ManyToManyField(Person, verbose_name = 'persons benefiting', related_name = 'benefactors')
    
    def owed(self):
        got_money_count = self.benefactors.count()
        return [(b, self.person, self.amount/got_money_count) for b in self.benefactors.all() if b != self.person]
    

    def __unicode__(self):
        return self.person.name + " paid " + unicode(self.amount) + " " + self.currency.name




# Create your models here.
