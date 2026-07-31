
class TestPurchase:
	def test_purchase_places_with_valid_request_shows_confirmation_and_deducts_points(self, client, login_as_valid_user):
		"""Case 1 — valid purchase: confirmation message displayed and points/places deducted."""
		login_as_valid_user()
		response = client.post(
			'/purchase_places',
			data={
				'competition': 'Fall Classic',
				'places': '5',
			},
			follow_redirects=True,
		)

		assert response.status_code == 200
		assert b"Booking complete: 5 places purchased." in response.data
		assert b"Points available: 8" in response.data
		assert b"Number of Places: 8" in response.data

		competition = next(c for c in client.application.config['COMPETITIONS'] if c['name'] == 'Fall Classic')
		club = next(c for c in client.application.config['CLUBS'] if c['name'] == 'Simply Lift')
		assert competition['number_of_places'] == '8'
		assert club['points'] == '8'

	def test_purchase_places_when_competition_is_complete(self, client, login_as_valid_user):
		"""Case 2 — competition complete: message indicating that the competition is no longer open."""
		login_as_valid_user()
		competition = next(c for c in client.application.config['COMPETITIONS'] if c['name'] == 'Fall Classic')
		competition['number_of_places'] = '0'

		response = client.post(
			'/purchase_places',
			data={
				'competition': 'Fall Classic',
				'places': '1',
			},
			follow_redirects=True,
		)

		assert response.status_code == 200
		assert b"This competition is no longer open for booking." in response.data

	def test_purchase_places_more_than_available_places(self, client, login_as_valid_user):
		"""Case 3 — request exceeds available places: denial with explicit message."""
		login_as_valid_user()
		competition = next(c for c in client.application.config['COMPETITIONS'] if c['name'] == 'Fall Classic')
		competition['number_of_places'] = '3'

		response = client.post(
			'/purchase_places',
			data={
				'competition': 'Fall Classic',
				'places': '5',
			},
			follow_redirects=True,
		)

		assert response.status_code == 200
		assert b"Not enough places available in this competition." in response.data
		assert competition['number_of_places'] == '3'

	def test_purchase_places_more_than_twelve(self, client, login_as_valid_user):
		"""Case 4 — request exceeds 12 places: denial to ensure fairness."""
		# If done in multiple times, the club can book more than 12 places, but not in a single request.
		login_as_valid_user()
		response = client.post(
			'/purchase_places',
			data={
				'competition': 'Fall Classic',
				'places': '13',
			},
			follow_redirects=True,
		)

		assert response.status_code == 200
		assert b"You cannot book more than 12 places per competition." in response.data

	def test_purchase_places_more_than_club_points(self, client, login_as_valid_user):
		"""Case 5 — request exceeds club points: denial with explicit message."""
		login_as_valid_user()
		club = next(c for c in client.application.config['CLUBS'] if c['name'] == 'Simply Lift')
		club['points'] = '4'
		response = client.post(
			'/purchase_places',
			data={
				'competition': 'Fall Classic',
				'places': '5',
			},
			follow_redirects=True,
		)

		assert response.status_code == 200
		assert b"Not enough points available in your club to book the requested number of places." in response.data
		assert club['points'] == '4'

	def test_purchase_multiple_times_accumulates_points_and_places(self, client, login_as_valid_user):
		"""Case 6 — multiple purchases: points and places are correctly updated after several purchases."""
		login_as_valid_user()
		# Premier achat
		response1 = client.post(
			'/purchase_places',
			data={
				'competition': 'Fall Classic',
				'places': '3',
			},
			follow_redirects=True,
		)
		assert response1.status_code == 200
		assert b"Booking complete: 3 places purchased." in response1.data
		assert b"Points available: 10" in response1.data
		assert b"Number of Places: 10" in response1.data

		# Deuxième achat
		response2 = client.post(
			'/purchase_places',
			data={
				'competition': 'Fall Classic',
				'places': '4',
			},
			follow_redirects=True,
		)
		assert response2.status_code == 200
		assert b"Booking complete: 4 places purchased." in response2.data
		assert b"Points available: 6" in response2.data
		assert b"Number of Places: 6" in response2.data

	def test_purchase_12_places_in_multiple_requests(self, client, login_as_valid_user):
		"""Case 7 — booking 12 places in multiple requests: the club cannot book more than 12 places in total."""
		login_as_valid_user()
		# Premier achat de 6 places
		response1 = client.post(
			'/purchase_places',
			data={
				'competition': 'Fall Classic',
				'places': '6',
			},
			follow_redirects=True,
		)
		assert response1.status_code == 200
		assert b"Booking complete: 6 places purchased." in response1.data
		assert b"Points available: 7" in response1.data
		assert b"Number of Places: 7" in response1.data

		# Deuxième achat de 6 places
		response2 = client.post(
			'/purchase_places',
			data={
				'competition': 'Fall Classic',
				'places': '6',
			},
			follow_redirects=True,
		)
		assert response2.status_code == 200
		assert b"Booking complete: 6 places purchased." in response2.data
		assert b"Points available: 1" in response2.data
		assert b"Number of Places: 1" in response2.data

		# Troisième tentative d'achat de 1 place (total de 13 places)
		response3 = client.post(
			'/purchase_places',
			data={
				'competition': 'Fall Classic',
				'places': '1',
			},
			follow_redirects=True,
		)
		assert response3.status_code == 200
		assert b"You cannot book more than 12 places per competition." in response3.data
		assert b"Points available: 1" in response3.data
		assert b"Number of Places: 1" in response3.data

	def test_purchase_requires_login(self, client):
		"""Case 8 — user not logged in: purchase denied and redirect to index."""
		response = client.post(
			'/purchase_places',
			data={
				'competition': 'Fall Classic',
				'places': '1',
			},
			follow_redirects=True,
		)
		assert response.status_code == 200
		assert b"Please log in first." in response.data
		assert b"Welcome to the GUDLFT Registration Portal!" in response.data