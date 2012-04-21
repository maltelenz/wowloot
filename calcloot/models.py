import hashlib
from django.db import models

class Calculation(models.Model):
    name = models.CharField(max_length = 200)
    creation_date = models.DateTimeField(editable = False)
    hashtag = models.CharField(max_length = 20, editable = False)

    def __unicode__(self):
        return self.name + "(" + self.hashtag + ")"

    def code_hashtag(self):
        return hashlib.md5(self.name).hexdigest()[:10]

    def benefactors(self):
        all_expenses = self.expense_set.all()
        benefactors = set({})
        for expense in all_expenses:
            for b in expense.benefactors.all():
                if b not in benefactors:
                    benefactors.add(b)
        return list(benefactors)

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
                
        return positive_owing_dict

    def save(self, *args, **kwargs):
        #Update the hashtag
        self.hashtag = self.code_hashtag()
        super(Calculation, self).save(*args, **kwargs) #Call the original save method

class Currency(models.Model):
    name = models.CharField(max_length = 5)

    def __unicode__(self):
        return self.name

class Person(models.Model):
    name = models.CharField(max_length = 200)

    def __unicode__(self):
        return self.name

class Expense(models.Model):
    calculation = models.ForeignKey(Calculation)
    person = models.ForeignKey(Person, verbose_name = 'person who paid', related_name = 'paying')
    amount = models.FloatField()
    currency = models.ForeignKey(Currency)
    benefactors = models.ManyToManyField(Person, verbose_name = 'persons benefiting', related_name = 'benefactors')

    def owed(self):
        got_money_count = self.benefactors.count()
        return [(b, self.person, self.amount/got_money_count) for b in self.benefactors.all() if b != self.person]
    
    def __unicode__(self):
        return self.person.name + " paid " + unicode(self.amount) + " " + self.currency.name




# Create your models here.
