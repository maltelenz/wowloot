from datetime import timedelta
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils import timezone
from calcloot.models import Calculation, Expense, Person, Currency
from calcloot.forms import *
from calcloot.currency import *

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
            return HttpResponseRedirect('/calculation/' + unicode(calculation.id) + '/' + calculation.hashtag + '/?firstload')
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


def about(request):
    return render_to_response('about.html', {}, context_instance = RequestContext(request))
    

def calculation(request, calcid, hashtag, edit_expense_id = None):
    is_edit = edit_expense_id != None
    calculation = get_object_or_404(Calculation, pk = calcid, hashtag = hashtag)
    #If this is first view for user, add it to session
    try:
        request.session['calculations'].add(calculation.id)
    except KeyError:
        request.session['calculations'] = {calculation.id}
    request.session.modified = True

    if request.method == 'POST':
        #Form has been submitted
        form = ExpenseForm(request.POST) #Read in the submitted form
        if form.is_valid():
            if is_edit:
                #edit existing expense
                existing_expense = get_object_or_404(Expense, pk = edit_expense_id)
                form = ExpenseForm(request.POST, instance = existing_expense)
                form.save()
                #redirect to the 'proper' calculation page
                return HttpResponseRedirect(reverse('calculation', args=[calcid, hashtag]))
                
            else:
                #create new expense
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
        if edit_expense_id != None:
            edit_expense = get_object_or_404(Expense, pk = edit_expense_id)
            form = ExpenseForm(instance = edit_expense)
        else:
            #create new empty form
            form = ExpenseForm(instance = calculation.new_expense()) 
    form.fields['person'].queryset = calculation.involved.all()
    #Get the final information on who is owing whom how much
    balance = calculation.balance()

    #Get the form for adding a person
    #Build up a list of names from previous calculations that might be possible to use
    try:
        previous_calculations = Calculation.objects.filter(pk__in=request.session['calculations'])
    except KeyError:
        previous_calculations = []
    name_list = []
    for previous_c in previous_calculations:
        name_list += [str(p) for p in previous_c.involved.all()]
    #Remove duplicates, and remove names already added to this calculation
    name_list = set(name_list) - set([str(p) for p in calculation.involved.all()])
    addpersonform = AddPersonForm(data_list=name_list)

    #Get the form for changing currency
    currencyform = ChangeCurrencyForm(instance = calculation)
    
    #Get all expenses for this calculation in order
    ordered_expenses = calculation.expense_set.all().order_by('id')
    if is_edit:
        ordered_expenses = ordered_expenses.exclude(pk=edit_expense_id)

    transfers = calculation.transfers()

    return render_to_response('calculation.html', {
            'calculation': calculation,
            'ordered_expenses': ordered_expenses,
            'form': form,
            'owing': balance,
            'addpersonform': addpersonform,
            'is_edit': is_edit,
            'transfers': transfers,
            'currencyform': currencyform,
            'firstload': 'firstload' in request.GET
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
            for e in calculation.expense_set.all():
                e.benefactors.add(new_person)
        #else:
            #the form was not valid, go back to calculation page
    return HttpResponseRedirect(reverse('calculation', args=[calcid, hashtag]))

def delete_person(request, calcid, hashtag, personid):
    calculation = get_object_or_404(Calculation, pk = calcid, hashtag = hashtag)
    person = calculation.involved.get(pk = personid)
    for e in calculation.expense_set.all():
        if e.person == person:
            e.delete()
        else:
            e.benefactors.remove(person)
    calculation.involved.remove(person)
    return HttpResponseRedirect(reverse('calculation', args=[calcid, hashtag]))

def finish_person(request, calcid, hashtag, personid):
    calculation = get_object_or_404(Calculation, pk = calcid, hashtag = hashtag)
    person = calculation.involved.get(pk = personid)
    person.finished = True
    person.save()
    return HttpResponseRedirect(reverse('calculation', args=[calcid, hashtag]))

def unfinish_person(request, calcid, hashtag, personid):
    calculation = get_object_or_404(Calculation, pk = calcid, hashtag = hashtag)
    person = calculation.involved.get(pk = personid)
    person.finished = False
    person.save()
    return HttpResponseRedirect(reverse('calculation', args=[calcid, hashtag]))

def change_currency(request, calcid, hashtag):
    calculation = get_object_or_404(Calculation, pk = calcid, hashtag = hashtag)
    if request.method == 'POST':
        #Form has been submitted
        form = ChangeCurrencyForm(request.POST, instance = calculation) #Read in the submitted form
        if form.is_valid():
            form.save()
        #else:
            #the form was not valid, go back to calculation page
    return HttpResponseRedirect(reverse('calculation', args=[calcid, hashtag]))

def calculation_delete(request, calcid, hashtag):
    calculation = get_object_or_404(Calculation, pk = calcid, hashtag = hashtag)
    #calculation.delete()
    request.session['calculations'].discard(int(calcid))
    request.session.modified = True
    return HttpResponseRedirect(reverse('home', args=[]))

def calculation_share(request, calcid, hashtag):
    calculation = get_object_or_404(Calculation, pk = calcid, hashtag = hashtag)
    full_uri = request.build_absolute_uri(reverse('calculation', args=[calcid, hashtag]))
    email_text = "Someone wants to share the expense calculation \"" + calculation.name + "\" with you on WOWLoot.\n\nYou can access the calculation here: " + full_uri + "\n\n--\nGreetings,\nWOWLoot"
    if request.method == 'POST':
        #Form has been submitted
        form = ShareForm(request.POST) #Read in the submitted form
        if form.is_valid():
            address = form.cleaned_data['address']
            #send email
            send_mail('Shared calculation on WOWLoot: ' + calculation.name, email_text, 'info@wowloot.com', [address], fail_silently = False)
            return HttpResponseRedirect(reverse('calculation', args=[calcid, hashtag]))
        #else:
            #the form was not valid, give chance to fix
    else:
        form = ShareForm() #create new empty form
        
    return render_to_response('share.html', {
            'calculation': calculation,
            'form': form,
            'email_text': email_text,
            'full_uri': full_uri,
            },
                              context_instance = RequestContext(request))

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

