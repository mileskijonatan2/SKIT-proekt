from django import forms
from django.core.exceptions import ValidationError
from django.forms.widgets import DateInput
from django.forms import formset_factory
from .models import Country


class FlightSearchForm(forms.Form):
    departure_country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        label='Origin',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    arrival_country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        label='Destination',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date = forms.DateField(
        label='Date of Flight',
        required=False,
        widget=DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control'
            }
        )
    )
    num_passengers = forms.IntegerField(
        widget=forms.NumberInput(attrs={'min': 1, 'max': 100, 'step': 1, 'class': 'form-control'}),
        label='Passengers'
    )

class SeatSelectionForm(forms.Form):
    def __init__(self, *args, max_seats=1, **kwargs):
        available_seats = kwargs.pop('available_seats', [])
        super(SeatSelectionForm, self).__init__(*args, **kwargs)
        self.max_seats = int(max_seats)

        for seat in available_seats:
            if seat.is_available:
                self.fields[f'seat_{seat.seat_number}'] = forms.BooleanField(
                    required=False,
                    label=f'{seat.seat_number}',
                    widget=forms.CheckboxInput(attrs={'class': 'seat-checkbox'})
                )
            else:
                self.fields[f'seat_{seat.seat_number}'] = forms.BooleanField(
                    required=False,
                    label=f'{seat.seat_number}',
                    widget=forms.CheckboxInput(attrs={'class': 'seat-checkbox not-available', 'disabled': 'disabled'})
                )

    def clean(self):
        cleaned_data = super().clean()
        selected_seats = [seat for seat in cleaned_data if cleaned_data[seat]]

        if len(selected_seats) < self.max_seats:
            raise ValidationError(f"You need to select exactly {self.max_seats} seats.")
        elif len(selected_seats) > self.max_seats:
            raise ValidationError(f"You can only select a maximum of {self.max_seats} seats.")

        return cleaned_data


class PassengerForm(forms.Form):
    seat_number = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}), label="Seat Number")
    first_name = forms.CharField(max_length=100, label="First Name")
    last_name = forms.CharField(max_length=100, label="Last Name")
    passport_number = forms.CharField(max_length=50, label="Passport Number")
    date_of_birth = forms.DateField(widget=forms.SelectDateWidget(years=range(1920, 2025)), label="Date of Birth")
    country = forms.ChoiceField(choices=[], label="Country")

    def __init__(self, *args, **kwargs):
        super(PassengerForm, self).__init__(*args, **kwargs)

        # Fetch all countries from the database
        countries = Country.objects.all()

        # Dynamically set the country choices
        self.fields['country'].choices = [('', 'Select Country')] + [
            (country.country_code, f"{country.name} - {country.country_code}") for country in countries
        ]


PassengerFormSet = formset_factory(PassengerForm, extra=0)
