# Testing of FlightTickets – app for booking flight tickets from various airlines

FlightTickets is a Django application, and in the scope of this project unit and E2E tests will be provided. For unit tests I will use Pytest, while for E2E tests I will use Cypress. Wherever applicable in the code, I used graph coverage and Edge-pair as a test criteria, and input space partitioning. Namely, for the functions in views.py tests are obtained using these coverage methods. 
### Documentation
The documentation is located 
```markdown
[here](/documentation.pdf)
```


### Run Unit Tests
```markdown
pytest
```

### Run E2E Tests
```markdown
npx cypress open
```
```markdown
python manage.py testserver TicketsApp/fixtures/test_data.json --addrport 127.0.0.1:8000
```
