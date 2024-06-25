#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
import sys
import dateutil.parser
import babel
from flask import (
    Flask, 
    abort, 
    jsonify, 
    render_template, 
    request, 
    Response, 
    flash, 
    redirect, 
    url_for
)
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

from models import db, Venue, Artist, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)

# COMPLETE connect to a local postgresql database

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):

  if isinstance(value, str):
    date = dateutil.parser.parse(value)
  else:
    date = value 

  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # COMPLETE replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming 
  #       shows per venue.
  data = []
  venues_list = Venue.query.order_by('city', 'name')
  city = venues_list.first().city
  state = venues_list.first().state
  venues_list = venues_list.all()
  venues_list.append(Venue(city='', name=''))

  venues = []
  for v in venues_list:
    num_upcoming_shows = Show.query.filter(Show.time > datetime.now(), 
                                           Show.venue_id == v.id).count()

    if v.city != city:
      venues_by_city = {"city": city, "state": state, "venues": venues}
      data.append(venues_by_city)
      venues = []
      city, state = v.city, v.state
    venues.append({"id": v.id, "name": v.name, "num_upcoming_shows": 
                   num_upcoming_shows})

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # COMPLETE implement search on artists with partial string search. Ensure 
  # it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and 
  # "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  res = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()
  
  data = []
  for v in res:
    data.append({
      "id": v.id,
      "name": v.name,
      "num_upcoming_shows": Show.query.filter(Show.venue_id == v.id,
                                              Show.time<datetime.now()).count()
    })

  response={
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, 
                         search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # COMPLETE replace with real venue data from the venues table, using venue_id
  venue = Venue.query.filter(Venue.id == venue_id).first()
  shows = Show.query.join(Artist).filter(Show.venue_id == venue_id).all()

  past_shows = []
  upcoming_shows = []
  for show in shows:
    show_info = {"artist_id": show.artist_id,
                 "artist_name": show.artist.name,
                 "artist_image_link": show.artist.image_link, 
                 "start_time": show.time}
    if show.time <= datetime.now():
      past_shows.append(show_info)
    else:
      upcoming_shows.append(show_info)

  data = {    
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres.strip('{}').split(','),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.currently_seeking,
    "seeking_description": venue.seeking_content,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
    }
  # data1={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #   "past_shows": [{
  #     "artist_id": 4,
  #     "artist_name": "Guns N Petals",
  #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 2,
  #   "name": "The Dueling Pianos Bar",
  #   "genres": ["Classical", "R&B", "Hip-Hop"],
  #   "address": "335 Delancey Street",
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "914-003-1132",
  #   "website": "https://www.theduelingpianos.com",
  #   "facebook_link": "https://www.facebook.com/theduelingpianos",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 3,
  #   "name": "Park Square Live Music & Coffee",
  #   "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
  #   "address": "34 Whiskey Moore Ave",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "415-000-1234",
  #   "website": "https://www.parksquarelivemusicandcoffee.com",
  #   "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #   "past_shows": [{
  #     "artist_id": 5,
  #     "artist_name": "Matt Quevedo",
  #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [{
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 1,
  # }
  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # COMPLETE insert form data as a new Venue record in the db, instead
  # COMPLETE modify data to be the data object returned from db insertion
  venue_form = VenueForm(request.form, meta={'csrf': False})

  if venue_form.validate():
    try:
      venue = Venue(
        name = venue_form.name.data,
        city = venue_form.city.data,
        state = venue_form.state.data,
        phone = venue_form.phone.data,
        address = venue_form.address.data,
        image_link = venue_form.image_link.data,
        facebook_link = venue_form.facebook_link.data,
        genres = venue_form.genres.data,
        website_link = venue_form.website_link.data,
        currently_seeking = venue_form.seeking_talent.data,
        seeking_content = venue_form.seeking_description.data,
      )

      db.session.add(venue)
      db.session.commit()
    except:
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
  
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')
  
  else:
    message = []
    for field, errors in venue_form.errors.items():
      for err in errors:
        message.append(f"{field}: {err}")
    flash('An error occurred. Venue ' +  request.form['name'] + 
          ' could not be listed.')
    venue_form = VenueForm()
    return render_template('forms/new_venue.html', form=venue_form)

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # COMPLETE Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('index'))
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # COMPLETE replace with real data returned from querying the database
  data = []
  artists = Artist.query.all()

  for artist in artists:
    data.append({"id": artist.id, "name": artist.name})

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # COMPLETE implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  res = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()
  
  data = []
  for a in res:
    data.append({
      "id": a.id,
      "name": a.name,
      "num_upcoming_shows": Show.query.filter(Show.artist_id == a.id,
                                              Show.time<datetime.now()).count()
    })

  response={
    "count": len(data),
    "data": data
  }

  return render_template('pages/search_artists.html', results=response, 
                         search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # COMPLETE replace with real artist data from the artist table, using artist_id
  artist = Artist.query.filter(Artist.id == artist_id).first()

  shows = Show.query.join(Venue).filter(Show.artist_id == artist_id).all()

  past_shows = []
  upcoming_shows = []
  for show in shows:
    show_info = {"venue_id": show.venue_id,
                 "venue_name": show.venue.name,
                 "venue_image_link": show.venue.image_link, 
                 "start_time": show.time}
    if show.time <= datetime.now():
      past_shows.append(show_info)
    else:
      upcoming_shows.append(show_info)

  data = {    
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres.strip('{}""').split(','),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.currently_seeking,
    "seeking_description": artist.seeking_content,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows) 
    }

  # data1={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 5,
  #   "name": "Matt Quevedo",
  #   "genres": ["Jazz"],
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "300-400-5000",
  #   "facebook_link": "https://www.facebook.com/mattquevedo923251523",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "past_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  #   "genres": ["Jazz", "Classical"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "432-325-5432",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 3,
  # }
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.filter_by(id == artist_id)
  artist_data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres.strip('{}""').split(','),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.currently_seeking,
    "seeking_description": artist.seeking_content,
    "image_link": artist.image_link
  }
  form = ArtistForm(data=artist_data)
  
  # COMPLETE populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, 
                         artist=artist_data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # COMPLETE take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist_form = ArtistForm(request.form)
  artist = Artist.query.filter_by(id=artist_id).first()

  if artist_form.validate():
    try:
      artist.name = artist_form.name.data
      artist.city = artist_form.city.data
      artist.state = artist_form.state.data
      artist.phone = artist_form.phone.data
      artist.image_link = artist_form.image_link.data
      artist.facebook_link = artist_form.facebook_link.data
      artist.genres = artist_form.genres.data
      artist.website_link = artist_form.website_link.data
      artist.currently_seeking = artist_form.seeking_talent.data
      artist.seeking_content = artist_form.seeking_description.data
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully updated!')
    except Exception as e:
      db.session.rollback()
    finally:
      db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))
  else:
    message = []
    for field, errors in artist_form.errors.items():
      for err in errors:
        message.append(f"{field}: {err}")
    flash('An error occurred. Artist ' +  request.form['name'] + 
          ' could not be updated.')
    artist_data={
      "id": artist.id,
      "name": artist.name,
      "genres": artist.genres.strip('{}""').split(','),
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website": artist.website_link,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.currently_seeking,
      "seeking_description": artist.seeking_content,
      "image_link": artist.image_link
    }
    form = ArtistForm(data=artist_data)

    return render_template('forms/edit_artist.html', form=form, 
                         artist=artist_data)


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.filter_by(id=venue_id).first()
  venue_data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres.strip('{}""').split(','),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website_link": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.currently_seeking,
    "seeking_description": venue.seeking_content,
    "image_link": venue.image_link
  }
  # COMPLETE populate form with values from venue with ID <venue_id>
  form = VenueForm(data=venue_data)
  return render_template('forms/edit_venue.html', form=form, venue=venue_data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # COMPLETE take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue_form = VenueForm(request.form)
  venue = Venue.query.filter_by(id=venue_id).first()

  if venue_form.validate():
    try:
      venue.name = venue_form.name.data
      venue.city = venue_form.city.data
      venue.state = venue_form.state.data
      venue.address = venue_form.address.data
      venue.phone = venue_form.phone.data
      venue.image_link = venue_form.image_link.data
      venue.facebook_link = venue_form.facebook_link.data
      venue.genres = venue_form.genres.data
      venue.website_link = venue_form.website_link.data
      venue.currently_seeking = venue_form.seeking_talent.data
      venue.seeking_content = venue_form.seeking_description.data
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully updated!')
    except Exception as e:
      db.session.rollback()
    finally:
      db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))
  else:
    message = []
    for field, errors in venue_form.errors.items():
      for err in errors:
        message.append(f"{field}: {err}")
    flash('An error occurred. Venue ' +  request.form['name'] + 
    ' could not be updated.')

    venue_data={
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres.strip('{}""').split(','),
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website_link": venue.website_link,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.currently_seeking,
      "seeking_description": venue.seeking_content,
      "image_link": venue.image_link
    }
    form = VenueForm(data=venue_data)

    return render_template('forms/edit_venue.html', form=form, venue=venue_data)

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # COMPLETE insert form data as a new Venue record in the db, instead
  # COMPLETE modify data to be the data object returned from db insertion

  artist_form = ArtistForm(request.form, meta={'csrf': False})

  if artist_form.validate():
    try:
      artist = Artist(
        name = artist_form.name.data,
        city = artist_form.city.data,
        state = artist_form.state.data,
        phone = artist_form.phone.data,
        genres = artist_form.genres.data,
        image_link = artist_form.image_link.data,
        facebook_link = artist_form.facebook_link.data,
        website_link = artist_form.website_link.data,
        currently_seeking = artist_form.seeking_venue.data,
        seeking_content = artist_form.seeking_description.data,
      )

      db.session.add(artist)
      db.session.commit()
    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
  
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')
    
  else:
    message = []
    for field, errors in artist_form.errors.items():
      for err in errors:
        message.append(f"{field}: {err}")
    flash('An error occurred. Artist ' +  request.form['name'] + 
          ' could not be listed.')
    artist_form = ArtistForm()
    return render_template('forms/new_artist.html', form=artist_form)

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # COMPLETE replace with real venues data.
  data = []
  shows_list = Show.query.order_by("time").all()

  for show in shows_list:
    artist = Artist.query.filter(Artist.id == show.artist_id).first()
    venue = Venue.query.filter(Venue.id == show.venue_id).first()
    data.append({
      "venue_id": show.venue_id,
      "venue_name": venue.name,
      "artist_id": show.artist_id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.time
    })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # COMPLETE insert form data as a new Show record in the db, instead
  show_form =  ShowForm(request.form, meta={'csrf': False})
  
  if show_form.validate():
    try:
      show = Show(
        venue_id = show_form.venue_id.data,
        artist_id = show_form.artist_id.data,
        time = show_form.start_time.data,
      )

      db.session.add(show)
      db.session.commit()
    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
  
    flash('Show was successfully listed!')
    return render_template('pages/home.html')
  else:
    message = []
    for field, errors in show_form.errors.items():
      for err in errors:
        message.append(f"{field}: {err}")
    flash('An error occurred. Show could not be listed.')
    show_form = ShowForm()
    return render_template('forms/new_venue.html', form=show_form)
  

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
