from datetime import timedelta
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
            form.save()
            form = ExpenseForm(instance = Expense(calculation = calculation)) #create new empty form
        #else:
            #the form was not valid, give the user a chance to fix.
    else:
        form = ExpenseForm(instance=Expense(calculation = calculation)) #create new empty form
    
    #Get the final information on who is owing whom how much
    finalcount = calculation.finalcount()

    return render_to_response('calculation.html', {
            'calculation': calculation,
            'form': form,
            'owing': finalcount
            },
                              context_instance = RequestContext(request))

