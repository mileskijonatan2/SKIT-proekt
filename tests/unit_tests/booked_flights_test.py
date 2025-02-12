from datetime import datetime

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone, duration
from TicketsApp.models import Flight, Airport, Seat, Country, Airline, Booking, Passenger

# C1.1 C2.2 BCC coverage
@pytest.mark.django_db
def test_booked_flights_get(client):

    """
     Checks if the passengers of the logged-in user are rendered on the html template of the response
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

    user = User.objects.create_user(username='testuser', password='testpassword')
    assert client.login(username='testuser', password='testpassword')

    seat = Seat.objects.create(flight=flight, seat_number='A1', class_type="EC", is_available=True, price=500)
    booking = Booking.objects.create(user=user, flight=flight, booking_date=datetime.now(),
                                     total_price=seat.price)
    passenger = Passenger.objects.create(
                    booking=booking,
                    seat=seat,
                    first_name='User1Name',
                    last_name='User1Surname',
                    passport_number='C231232',
                    date_of_birth='1990-03-08',
                    country_of_residence=country1,
    )

    response = client.get(reverse('booked flights'))

    content = response.content.decode('utf-8')
    assert response.status_code == 200
    assert passenger.passport_number in content
    assert f'<h6>{passenger.first_name} {passenger.last_name}</h6>' in content


@pytest.mark.django_db
def test_booked_flights_get_more_users(client):

    """
    Checks if only the passengers form the logged-in user are rendered on the html template, were more users have made bookings
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

    user1 = User.objects.create_user(username='testuser', password='testpassword')
    assert client.login(username='testuser', password='testpassword')

    seat1 = Seat.objects.create(flight=flight, seat_number='A1', class_type="EC", is_available=True, price=500)
    booking = Booking.objects.create(user=user1, flight=flight, booking_date=datetime.now(),
                                     total_price=seat1.price)
    passenger1 = Passenger.objects.create(
                    booking=booking,
                    seat=seat1,
                    first_name='User1Name',
                    last_name='User1Surname',
                    passport_number='C231232',
                    date_of_birth='1990-03-08',
                    country_of_residence=country1,
    )

    client.logout()

    user2 = User.objects.create_user(username='testuser2', password='testpassword2')
    assert client.login(username='testuser2', password='testpassword2')

    seat2 = Seat.objects.create(flight=flight, seat_number='A2', class_type="EC", is_available=True, price=500)
    booking = Booking.objects.create(user=user2, flight=flight, booking_date=datetime.now(),
                                     total_price=seat2.price)
    passenger2 = Passenger.objects.create(
        booking=booking,
        seat=seat2,
        first_name='User2Name',
        last_name='User2Surname',
        passport_number='C124532',
        date_of_birth='1994-03-08',
        country_of_residence=country1,
    )

    response = client.get(reverse('booked flights'))

    content = response.content.decode('utf-8')
    assert response.status_code == 200
    assert passenger1.passport_number not in content
    assert f'<h6>{passenger1.first_name} {passenger1.last_name}</h6>' not in content
    assert passenger2.passport_number in content
    assert f'<h6>{passenger2.first_name} {passenger2.last_name}</h6>' in content

# C1.1 C2.1
@pytest.mark.django_db
def test_booked_flights_get_zero_bookings(client):

    """
     Checks if 0 passengers of the logged-in user are rendered on the html template of the response
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

    user = User.objects.create_user(username='testuser', password='testpassword')
    assert client.login(username='testuser', password='testpassword')

    response = client.get(reverse('booked flights'))

    content = response.content.decode('utf-8')
    assert response.status_code == 200
    assert 'Passport' not in content
