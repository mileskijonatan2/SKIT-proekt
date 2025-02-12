import pytest
from django.urls import reverse
from django.utils import timezone, duration
from TicketsApp.models import Flight, Airport, Seat, Country, Airline

"""
All tests are obtained using edge-pair coverage criteria or ISP with BCC.
"""

# Egde-pair coverage test path [1, 2, 3]
@pytest.mark.django_db
def test_search_flights_get_method(client):
    """
    Tests the GET request to index/
    """
    response = client.get(reverse('index'))
    assert response.status_code == 200
    # true when the correct template is used
    assert 'searchFlights.html' in (t.name for t in response.templates)
    # true when form is present in the context
    assert 'form' in response.context
    form = response.context['form']
    assert form is not None


# Egde-pair coverage test path [1, 2, 4, 3]
@pytest.mark.django_db
def test_search_flights_invalid_form(client):
    """Tests the POST request to index/ with invalid form."""

    # form with invalid data
    form_data = {
        'departure_country': '',
        'arrival_country': '',
        'date': '',
        'num_passengers': 0,
    }

    # POST request with invalid data
    response = client.post(reverse('index'), data=form_data)
    assert response.status_code == 200
    assert 'searchFlights.html' in (t.name for t in response.templates)
    assert 'form' in response.context
    form = response.context['form']
    assert form.errors  # Ensure there are errors in the form
    assert 'flights' in response.context
    flights = response.context['flights']
    assert flights is None

# C1.1 C2.1 C3.1
# Egde-pair coverage test path [1,2,4,5,6,8,9,3]
@pytest.mark.django_db
def test_search_flights_no_flights(client):
    """
    Tests the POST request to index/ when there are no flights.
    """
    country1 = Country.objects.create(name='United Kingdom', country_code='GBT')
    country2 = Country.objects.create(name='United States', country_code='USA')
    airline = Airline.objects.create(name='Airline1', country=country1, date_established='2000-01-01', num_of_planes=50)
    departure_airport = Airport.objects.create(name="Departure Airport", country=country1, code="DAP", city='City1')
    arrival_airport = Airport.objects.create(name="Arrival Airport", country=country2, code="AAP", city='City2')

    form_data = {
        'departure_country': country1.id,
        'arrival_country': country2.id,
        'date': '2025-01-01',
        'num_passengers': 1,
    }

    response = client.post(reverse('index'), data=form_data)

    assert response.status_code == 200
    assert 'flights' in response.context
    flights = response.context['flights']
    assert len(flights) == 0


# C1.1 C2.1 C3.2 - Happy path
# Egde-pair coverage test path [1,2,4,5,7,8,9,10,11,12,13,9,10,13,9,10,11,13,9,3]
@pytest.mark.django_db
def test_search_flights_flight_found(client):
    """
    Tests the case when only one flight is matching the criteria.
    """
    country1 = Country.objects.create(name='United Kingdom', country_code='GBT')
    country2 = Country.objects.create(name='United States', country_code='USA')
    airline = Airline.objects.create(name='Airline1', country=country1, date_established='2000-01-01', num_of_planes=50)
    departure_airport = Airport.objects.create(name="Departure Airport", country=country1, code="DAP", city='City1')
    arrival_airport = Airport.objects.create(name="Arrival Airport", country=country2, code="AAP", city='City2')
    d_time = timezone.now() + timezone.timedelta(days=1)
    a_time = timezone.now() + timezone.timedelta(days=1, hours=2)
    flight1 = Flight.objects.create(
        flight_number="FL123",
        airline=airline,
        departure_airport=departure_airport,
        arrival_airport=arrival_airport,
        departure_time=d_time,  # future flight
        arrival_time=a_time,
        duration=a_time-d_time,
        price=500,
    )
    flight2 = Flight.objects.create(
        flight_number="FL234",
        airline=airline,
        departure_airport=arrival_airport,
        arrival_airport=departure_airport,
        departure_time=d_time,
        arrival_time=a_time,
        duration=a_time - d_time,
        price=500,
    )
    flight3 = Flight.objects.create(
        flight_number="FL345",
        airline=airline,
        departure_airport=arrival_airport,
        arrival_airport=departure_airport,
        departure_time=d_time,  
        arrival_time=a_time,
        duration=a_time - d_time,
        price=500,
    )

    for i in range(2):
        Seat.objects.create(flight=flight1, seat_number="{i}", class_type="EC", is_available=True, price=(flight1.price+int(float(flight1.price)*0.2)))

    form_data = {
        'departure_country': country1.id,
        'arrival_country': country2.id,
        'date': '',
        'num_passengers': 1,
    }

    response = client.post(reverse('index'), data=form_data)

    assert response.status_code == 200
    assert 'flights' in response.context
    flights = response.context['flights']
    assert len(flights) == 1
    assert flights[0] == flight1


# C1.1 C2.1 C3.3
@pytest.mark.django_db
def test_search_flights_two_flights_found(client):
    """
    Tests the case when more than flight is matching the criteria.
    """
    country1 = Country.objects.create(name='United Kingdom', country_code='GBT')
    country2 = Country.objects.create(name='United States', country_code='USA')
    airline = Airline.objects.create(name='Airline1', country=country1, date_established='2000-01-01', num_of_planes=50)
    departure_airport = Airport.objects.create(name="Departure Airport", country=country1, code="DAP", city='City1')
    arrival_airport = Airport.objects.create(name="Arrival Airport", country=country2, code="AAP", city='City2')
    d_time = timezone.now() + timezone.timedelta(days=1)
    a_time = timezone.now() + timezone.timedelta(days=1, hours=2)
    flight1 = Flight.objects.create(
        flight_number="FL123",
        airline=airline,
        departure_airport=departure_airport,
        arrival_airport=arrival_airport,
        departure_time=d_time,  # future flight
        arrival_time=a_time,
        duration=a_time-d_time,
        price=500,
    )
    flight2 = Flight.objects.create(
        flight_number="FL234",
        airline=airline,
        departure_airport=departure_airport,
        arrival_airport=arrival_airport,
        departure_time=d_time,
        arrival_time=a_time,
        duration=a_time - d_time,
        price=500,
    )
    flight3 = Flight.objects.create(
        flight_number="FL345",
        airline=airline,
        departure_airport=arrival_airport,
        arrival_airport=departure_airport,
        departure_time=d_time,
        arrival_time=a_time,
        duration=a_time - d_time,
        price=500,
    )

    flights = [flight1, flight2, flight3]

    for i in range(2):
        Seat.objects.create(flight=flight1, seat_number=f"{i}", class_type="EC", is_available=True, price=(flight1.price+int(float(flight1.price)*0.2)))

    for i in range(2):
        Seat.objects.create(flight=flight2, seat_number=f"{i}", class_type="EC", is_available=True, price=(flight2.price+int(float(flight2.price)*0.2)))

    form_data = {
        'departure_country': country1.id,
        'arrival_country': country2.id,
        'date': '',
        'num_passengers': 1,
    }

    response = client.post(reverse('index'), data=form_data)

    assert response.status_code == 200
    assert 'flights' in response.context
    flights = response.context['flights']
    assert len(flights) == 2
    assert flights[0] == flight1
    assert flights[1] == flight2
