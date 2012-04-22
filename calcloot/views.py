from datetime import timedelta
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils import timezone
from calcloot.models import Calculation, Expense, Person, Currency
from calcloot.forms import *

def home(request):
    if request.method == 'POST':
        #Form has been submitted
        form = HomeForm(request.POST) #Read in the submitted form
        if form.is_valid():
            #Create a new calculation
            name = form.cleaned_data['name']
            calculation = Calculation(name = name, creation_date = timezone.now())
            calculation.save()
            #Add the calculation to the session for this user
            try:
                request.session['calculations'].add(calculation.id)
            except KeyError:
                request.session['calculations'] = {calculation.id}
            #Set the expiration to 6 months in the future
            request.session.set_expiry(timedelta(30*6))
            #Redirect to the calculation page
            return HttpResponseRedirect('/calculation/' + unicode(calculation.id) + '/' + calculation.hashtag + '/')
    else:
        form = HomeForm() #create new empty form
    try:
        previous_calculations = Calculation.objects.filter(pk__in=request.session['calculations'])
    except KeyError:
        previous_calculations = []
    #Render the home page
    return render_to_response('index.html', {
            'form': form,
            'previous_calculations': previous_calculations
            },
                              context_instance = RequestContext(request))

def calculation(request, calcid, hashtag):
    calculation = get_object_or_404(Calculation, pk = calcid, hashtag = hashtag)
    if request.method == 'POST':
        #Form has been submitted
        form = ExpenseForm(request.POST) #Read in the submitted form
        if form.is_valid():
            form = ExpenseForm(request.POST, instance = Expense(calculation = calculation))
            new_expense = form.save(commit = False)
            new_expense.save()
            for i in calculation.involved.all():
                new_expense.benefactors.add(i)
            #create new empty form
            form = ExpenseForm(instance = calculation.new_expense())
        #else:
            #the form was not valid, give the user a chance to fix.
    else:
        #create new empty form
        form = ExpenseForm(instance = calculation.new_expense())
    form.fields['person'].queryset = calculation.involved.all()
    #Get the final information on who is owing whom how much
    finalcount = calculation.finalcount()

    #Get the form for adding a person
    addpersonform = AddPersonForm()

    #Get all expenses for this calculation in order
    ordered_expenses = calculation.expense_set.all().order_by('id')

    return render_to_response('calculation.html', {
            'calculation': calculation,
            'ordered_expenses': ordered_expenses,
            'form': form,
            'owing': finalcount,
            'addpersonform': addpersonform,
            },
                              context_instance = RequestContext(request))

def add_person(request, calcid, hashtag):
    calculation = get_object_or_404(Calculation, pk = calcid, hashtag = hashtag)
    if request.method == 'POST':
        #Form has been submitted
        form = AddPersonForm(request.POST) #Read in the submitted form
        if form.is_valid():
            new_person = Person(name = form.cleaned_data['name'])
            new_person.save()
            calculation.involved.add(new_person)
            calculation.save()
        #else:
            #the form was not valid, go back to calculation page
    return HttpResponseRedirect(reverse('calculation', args=[calcid, hashtag]))
    

def calculation_delete(request, calcid, hashtag):
    calculation = get_object_or_404(Calculation, pk = calcid, hashtag = hashtag)
    #calculation.delete()
    request.session['calculations'].discard(int(calcid))
    request.session.modified = True
    return HttpResponseRedirect(reverse('home', args=[]))

def expense_delete(request, calcid, hashtag, expenseid):
    calculation = get_object_or_404(Calculation, pk = calcid, hashtag = hashtag)
    expense = get_object_or_404(Expense, pk = expenseid, calculation = calculation)
    expense.delete()
    return HttpResponseRedirect(reverse('calculation', args=[calcid, hashtag]))

def benefactor_delete(request, calcid, hashtag, expenseid, personid):
    calculation = get_object_or_404(Calculation, pk = calcid, hashtag = hashtag)
    expense = get_object_or_404(Expense, pk = expenseid, calculation = calculation)
    person = get_object_or_404(Person, pk = personid)
    expense.benefactors.remove(person)
    return HttpResponseRedirect(reverse('calculation', args=[calcid, hashtag]))

def benefactor_add(request, calcid, hashtag, expenseid, personid):
    calculation = get_object_or_404(Calculation, pk = calcid, hashtag = hashtag)
    expense = get_object_or_404(Expense, pk = expenseid, calculation = calculation)
    person = get_object_or_404(Person, pk = personid)
    expense.benefactors.add(person)
    return HttpResponseRedirect(reverse('calculation', args=[calcid, hashtag]))

