import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone, duration

from TicketsApp.forms import PassengerFormSet
from TicketsApp.models import Flight, Airport, Seat, Country, Airline, Booking, Passenger

"""
All tests are obtained using edge-pair coverage criteria or ISP with BCC.
"""


# Test path [1, 2, 3]
@pytest.mark.django_db
def test_passenger_details_get(client):

    """
    Tests passenger details view when GET request is made.
    """

    country1 = Country.objects.create(name='United Kingdom', country_code='GBT')
    country2 = Country.objects.create(name='United States', country_code='USA')
    airline = Airline.objects.create(name='Airline1', country=country1, date_established='2000-01-01', num_of_planes=50)
    departure_airport = Airport.objects.create(name="Departure Airport", country=country1, code="DAP", city='City1')
    arrival_airport = Airport.objects.create(name="Arrival Airport", country=country2, code="AAP", city='City2')
    d_time = timezone.now() + timezone.timedelta(days=1)
    a_time = timezone.now() + timezone.timedelta(days=1, hours=2)
    flight = Flight.objects.create(
        flight_number="FL123",
        airline=airline,
        departure_airport=departure_airport,
        arrival_airport=arrival_airport,
        departure_time=d_time,
        arrival_time=a_time,
        duration=a_time - d_time,
        price=500,
    )

    Seat.objects.create(flight=flight, seat_number='A1', class_type="EC", is_available=True, price=500)

    user = User.objects.create_user(username='testuser', password='testpassword')
    assert client.login(username='testuser', password='testpassword')

    session = client.session
    session['selected_seats'] = ['A1']
    session.save()

    response = client.get(reverse('passengers details', args=[flight.id]))

    assert response.status_code == 200
    assert 'formset' in response.context
    formset = response.context['formset']
    assert isinstance(formset, PassengerFormSet)
    assert formset.initial == [{'seat_number': 'A1'}]


# Test path [1, 2, 4, 5, 3]
@pytest.mark.django_db
def test_passenger_details_post_invalid_form(client):
    """
    Tests passenger details view when POST request with invalid formset is made.
    """
    country1 = Country.objects.create(name='United Kingdom', country_code='GBT')
    airline = Airline.objects.create(name='Airline1', country=country1, date_established='2000-01-01', num_of_planes=50)
    departure_airport = Airport.objects.create(name="Departure Airport", country=country1, code="DAP", city='City1')
    arrival_airport = Airport.objects.create(name="Arrival Airport", country=country1, code="AAP", city='City2')
    d_time = timezone.now() + timezone.timedelta(days=1)
    a_time = timezone.now() + timezone.timedelta(days=1, hours=2)
    flight = Flight.objects.create(
        flight_number="FL123",
        airline=airline,
        departure_airport=departure_airport,
        arrival_airport=arrival_airport,
        departure_time=d_time,
        arrival_time=a_time,
        duration=a_time - d_time,
        price=500,
    )

    Seat.objects.create(flight=flight, seat_number='A1', class_type="EC", is_available=True, price=500)

    user = User.objects.create_user(username='testuser', password='testpassword')
    assert client.login(username='testuser', password='testpassword')
    session = client.session
    session['selected_seats'] = ['A1']
    session.save()

    invalid_data = {
        'form-TOTAL_FORMS': '1',
        'form-INITIAL_FORMS': '0',
        'form-0-first_name': '',
        'form-0-last_name': 'Some_Surname',
        'form-0-passport_number': '123456789',
        'form-0-date_of_birth': '2000-01-01',
        'form-0-country': 'GBT',
    }

    response = client.post(reverse('passengers details', args=[flight.id]), data=invalid_data)

    assert response.status_code == 200
    assert 'formset' in response.context
    formset = response.context['formset']
    assert isinstance(formset, PassengerFormSet)
    assert not formset.is_valid()
    assert 'passengerDetails.html' in (t.name for t in response.templates)


# C1.1 C2.1 C3.1
# Test path [1, 2, 4, 5, 6, 7, 9]
@pytest.mark.django_db
def test_passenger_details_post_valid_form_one_seat_booked(client):
    """
    Tests passenger details view when POST request with valid formset with one booked seat is made.
    """
    country1 = Country.objects.create(name='United Kingdom', country_code='GBT')
    airline = Airline.objects.create(name='Airline1', country=country1, date_established='2000-01-01', num_of_planes=50)
    departure_airport = Airport.objects.create(name="Departure Airport", country=country1, code="DAP", city='City1')
    arrival_airport = Airport.objects.create(name="Arrival Airport", country=country1, code="AAP", city='City2')
    d_time = timezone.now() + timezone.timedelta(days=1)
    a_time = timezone.now() + timezone.timedelta(days=1, hours=2)
    flight = Flight.objects.create(
        flight_number="FL123",
        airline=airline,
        departure_airport=departure_airport,
        arrival_airport=arrival_airport,
        departure_time=d_time,
        arrival_time=a_time,
        duration=a_time - d_time,
        price=500,
    )

    Seat.objects.create(flight=flight, seat_number='A1', class_type="EC", is_available=True, price=500)

    user = User.objects.create_user(username='testuser', password='testpassword')
    assert client.login(username='testuser', password='testpassword')
    session = client.session
    session['selected_seats'] = ['A1']
    session.save()

    valid_formset = {
        'form-TOTAL_FORMS': '1',
        'form-INITIAL_FORMS': '0',
        'form-0-seat_number': 'A1',
        'form-0-first_name': 'User1Name',
        'form-0-last_name': 'User1Surname',
        'form-0-passport_number': 'C167812',
        'form-0-date_of_birth': '2000-01-01',
        'form-0-country': 'GBT',
    }

    response = client.post(reverse('passengers details', args=[flight.id]), data=valid_formset)

    assert response.status_code == 302  # redirect
    expected_url = reverse('booked flights')
    assert response.url == expected_url

    booking = Booking.objects.filter(user=user, flight=flight).first()
    assert booking is not None
    assert booking.total_price == 500

    seat = Seat.objects.get(flight=flight, seat_number='A1')
    assert not seat.is_available

    passenger = Passenger.objects.filter(booking=booking).first()
    assert passenger is not None
    assert passenger.first_name == 'User1Name'
    assert passenger.last_name == 'User1Surname'
    assert passenger.passport_number == 'C167812'
    assert passenger.date_of_birth.strftime('%Y-%m-%d') == '2000-01-01'
    assert passenger.country_of_residence == country1


# Test path [1, 2, 4, 5, 6, 7, 8, 7, 8, 7, 9]
@pytest.mark.django_db
def test_passenger_details_post_valid_form_two_seats_booked(client):
    """
    Tests passenger details view when POST request with valid formset with two booked seat is made.
    """
    country1 = Country.objects.create(name='United Kingdom', country_code='GBT')
    airline = Airline.objects.create(name='Airline1', country=country1, date_established='2000-01-01', num_of_planes=50)
    departure_airport = Airport.objects.create(name="Departure Airport", country=country1, code="DAP", city='City1')
    arrival_airport = Airport.objects.create(name="Arrival Airport", country=country1, code="AAP", city='City2')
    d_time = timezone.now() + timezone.timedelta(days=1)
    a_time = timezone.now() + timezone.timedelta(days=1, hours=2)
    flight = Flight.objects.create(
        flight_number="FL123",
        airline=airline,
        departure_airport=departure_airport,
        arrival_airport=arrival_airport,
        departure_time=d_time,
        arrival_time=a_time,
        duration=a_time - d_time,
        price=500,
    )

    Seat.objects.create(flight=flight, seat_number='A1', class_type="EC", is_available=True, price=500)
    Seat.objects.create(flight=flight, seat_number='B2', class_type="EC", is_available=True, price=500)

    user = User.objects.create_user(username='testuser', password='testpassword')
    assert client.login(username='testuser', password='testpassword')
    session = client.session
    session['selected_seats'] = ['A1', 'B2']
    session.save()

    valid_formset = {
        'form-TOTAL_FORMS': '2',
        'form-INITIAL_FORMS': '0',
        'form-0-seat_number': 'A1',
        'form-0-first_name': 'User1Name',
        'form-0-last_name': 'User1Surname',
        'form-0-passport_number': 'C167812',
        'form-0-date_of_birth': '2000-01-01',
        'form-0-country': 'GBT',
        'form-1-seat_number': 'B2',
        'form-1-first_name': 'User2Name',
        'form-1-last_name': 'User2Surname',
        'form-1-passport_number': 'C727832',
        'form-1-date_of_birth': '2000-01-03',
        'form-1-country': 'GBT',
    }

    response = client.post(reverse('passengers details', args=[flight.id]), data=valid_formset)

    assert response.status_code == 302  # redirect
    expected_url = reverse('booked flights')
    assert response.url == expected_url

    booking = Booking.objects.filter(user=user, flight=flight).first()
    assert booking is not None
    assert booking.total_price == 1000

    seat1 = Seat.objects.get(flight=flight, seat_number='A1')
    seat2 = Seat.objects.get(flight=flight, seat_number='B2')
    assert not seat1.is_available
    assert not seat2.is_available

    passengers = Passenger.objects.filter(booking=booking)
    assert len(passengers) == 2

