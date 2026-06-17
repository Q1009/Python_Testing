from flask import Flask,render_template,request,redirect,flash,url_for,current_app
from utils import loadClubs, loadCompetitions, getClubByEmail

def create_app(config=None, clubs=None, competitions=None):
    app = Flask(__name__)
    app.secret_key = 'something_special'
    if config:
        app.config.update(config)

    app.config['COMPETITIONS'] = competitions if competitions is not None else loadCompetitions()
    app.config['CLUBS'] = clubs if clubs is not None else loadClubs()

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/showSummary',methods=['POST'])
    def showSummary():
        available_clubs = current_app.config['CLUBS']
        available_competitions = current_app.config['COMPETITIONS']

        if available_clubs is None or available_competitions is None:
            flash("Error loading clubs or competitions data.")
            return redirect(url_for('index'))

        club = getClubByEmail(request.form['email'], available_clubs)
        if club:
            return render_template('welcome.html',club=club,competitions=available_competitions)

        flash("Unfortunately, the email you entered was not found.")
        return redirect(url_for('index'))


    @app.route('/book/<competition>/<club>')
    def book(competition,club):
        available_clubs = current_app.config['CLUBS']
        available_competitions = current_app.config['COMPETITIONS']
        foundClub = [c for c in available_clubs if c['name'] == club][0]
        foundCompetition = [c for c in available_competitions if c['name'] == competition][0]
        if foundClub and foundCompetition:
            return render_template('booking.html',club=foundClub,competition=foundCompetition)
        else:
            flash("Something went wrong-please try again")
            return render_template('welcome.html', club=club, competitions=available_competitions)


    @app.route('/purchasePlaces',methods=['POST'])
    def purchasePlaces():
        available_clubs = current_app.config['CLUBS']
        available_competitions = current_app.config['COMPETITIONS']
        competition = [c for c in available_competitions if c['name'] == request.form['competition']][0]
        club = [c for c in available_clubs if c['name'] == request.form['club']][0]
        placesRequired = int(request.form['places'])
        competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired
        flash('Great-booking complete!')
        return render_template('welcome.html', club=club, competitions=available_competitions)


    # TODO: Add route for points display


    @app.route('/logout')
    def logout():
        return redirect(url_for('index'))

    return app


app = create_app()