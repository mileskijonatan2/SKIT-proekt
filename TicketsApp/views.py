from datetime import datetime

from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from .models import Flight, Seat, Booking, Passenger
from .forms import FlightSearchForm, SeatSelectionForm, PassengerFormSet, Country
from django.contrib.auth.decorators import login_required


def searchFlights(request):
    form = FlightSearchForm()
    flights = None

    if request.method == 'POST':
        form = FlightSearchForm(request.POST)
        if form.is_valid():
            departure_country = form.cleaned_data['departure_country']
            arrival_country = form.cleaned_data['arrival_country']
            date = form.cleaned_data['date']
            num_passengers = form.cleaned_data['num_passengers']
            request.session['num_seats'] = num_passengers
            all_flights = list()

            if date is not None:
                all_flights = Flight.objects.filter(departure_time__date=date)
            else:
                all_flights = Flight.objects.filter(departure_time__gte=datetime.now())  # show all flights whose dep time is after now

            flights = list()
            for i in range(all_flights.count()):
                if all_flights[i].departure_airport.country == departure_country and all_flights[i].arrival_airport.country == arrival_country:
                    num_available_seats = Seat.objects.filter(flight=all_flights[i]).count()
                    if num_available_seats >= num_passengers:
                        flights.append(all_flights[i])

    return render(request, 'searchFlights.html', {'form': form, 'flights': flights})


@login_required(login_url='/login/')
def flightDetails(request, id):
    form = SeatSelectionForm()
    flight = Flight.objects.filter(id=id).get()
    seats = Seat.objects.filter(flight=flight)

    if request.method == 'POST':
        form = SeatSelectionForm(request.POST, available_seats=seats, max_seats=request.session['num_seats'])
        if form.is_valid():
            selected_seats = [seat.split('_')[1] for seat in form.cleaned_data if form.cleaned_data[seat]]
            request.session['selected_seats'] = selected_seats
            return redirect('passengers details', id=id)

    form = SeatSelectionForm(available_seats=seats, max_seats=request.session['num_seats'])
    return render(request, 'flightDetails.html', {'form': form, 'flight': flight, 'seats': seats, 'num_seats': request.session['num_seats']})


@login_required(login_url='/login/')
def passenger_details(request, id):
    flight = Flight.objects.filter(id=id).get()
    selected_seats = request.session.get('selected_seats', [])
    num_passengers = len(selected_seats)
    seats_price = Seat.objects.filter(flight=flight, seat_number__in=selected_seats).aggregate(sum=Sum('price'))['sum']

    if request.method == 'POST':
        formset = PassengerFormSet(request.POST)
        if formset.is_valid():
            booking = Booking.objects.create(user=request.user, flight=flight, booking_date=datetime.now(), total_price=seats_price)
            booking.save()
            for form, seat_number in zip(formset, selected_seats):
                seat = get_object_or_404(Seat, seat_number=seat_number, flight=flight)
                seat.is_available = False
                seat.save()
                passenger_data = form.cleaned_data
                Passenger.objects.create(
                    booking=booking,
                    seat=seat,
                    first_name=passenger_data['first_name'],
                    last_name=passenger_data['last_name'],
                    passport_number=passenger_data['passport_number'],
                    date_of_birth=passenger_data['date_of_birth'],
                    country_of_residence=Country.objects.get(country_code=passenger_data['country']),
                )
            return redirect('booked flights')

    formset = PassengerFormSet(initial=[
        {'seat_number': seat} for seat in selected_seats
    ])
    return render(request, 'passengerDetails.html', {'formset': formset})


@login_required(login_url='/login/')
def booked_flights(request):
    passengers = Passenger.objects.filter(booking__user=request.user)
    return render(request, 'bookedFlights.html', {'passengers': passengers})

