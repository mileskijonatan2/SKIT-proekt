import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone, duration

from TicketsApp.forms import SeatSelectionForm
from TicketsApp.models import Flight, Airport, Seat, Country, Airline


"""
All tests are obtained using edge-pair coverage criteria or ISP with BCC.
"""

# Edge-pair coverage test path [1, 2, 3]
@pytest.mark.django_db
def test_flight_details_get(client):
    """
    Tests GET request to /flight_details/
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

    for i in range(5):
        Seat.objects.create(flight=flight, seat_number=f"{i + 1}", class_type="EC", is_available=True, price=500)

    user = User.objects.create_user(username='testuser', password='testpassword')
    assert client.login(username='testuser', password='testpassword')

    session = client.session
    session['num_seats'] = '5'
    session.save()

    assert session['num_seats'] == '5'

    response = client.get(reverse('flight details', args=[flight.id]))
    assert response.status_code == 200
    assert 'flight' in response.context
    assert response.context['flight'] == flight
    assert 'seats' in response.context
    assert len(response.context['seats']) == 5
    assert 'form' in response.context
    assert isinstance(response.context['form'], SeatSelectionForm)
    assert 'flightDetails.html' in (t.name for t in response.templates)


# Edge-pair coverage test path [1, 2, 4, 5, 3]
@pytest.mark.django_db
def test_flight_details_post_invalid_form(client):
    """
    Tests POST request to /flight_details/ when form data is invalid.
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

    user = User.objects.create_user(username='testuser', password='testpassword')
    client.login(username='testuser', password='testpassword')

    session = client.session
    session['num_seats'] = '5'
    session.save()

    assert session['num_seats'] == '5'

    invalid_data = {
        'seat_numbers': '',
    }

    response = client.post(reverse('flight details', args=[flight.id]), data=invalid_data)

    assert response.status_code == 200
    assert 'form' in response.context
    assert not response.context['form'].is_valid()
    assert 'flightDetails.html' in (t.name for t in response.templates)

# C1.1 C2.1 C3.1 C4.1 -happy path
# Edge-pair coverage test path [1, 2, 4, 5, 6]
@pytest.mark.django_db
def test_flight_details_post_valid_form(client):
    """
    Tests POST request to /flight_details/ when form data is valid.
    """

    # Test objects creation
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

    seats = list()
    for i in range(5):
        seats.append(Seat.objects.create(flight=flight, seat_number=f"{i + 1}", class_type="EC", is_available=True, price=500))

    user = User.objects.create_user(username='testuser', password='testpassword')
    client.login(username='testuser', password='testpassword')
    valid_data = {
        'seat_1': True,
        'seat_2': True,
    }

    session = client.session
    session['num_seats'] = '2'
    session.save()

    assert session['num_seats'] == '2'
    response = client.post(reverse('flight details', args=[flight.id]), data=valid_data)
    assert response.status_code == 302  # redirect

    # check if the user is redirected to the right url
    expected_url = reverse('passengers details', args=[flight.id])
    assert response.headers.get('Location') == expected_url
