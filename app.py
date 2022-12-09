#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for,jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime
from flask_wtf.csrf import CSRFProtect


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
csrf = CSRFProtect(app)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)


from model import *


#----------------------------------------------------------------------------#
# TODO - Done: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://rs@localhost:5432/fyyur'
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  #print('value-----------------', 'type', type(value), 'value', value)
  #date = dateutil.parser.parse(value)
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


#  venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO - Done: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  allVenues=Venue.query.all()
  locations=[]   # city, state
  for venue in allVenues:
    if (venue.city, venue.state) not in locations:
      locations.append((venue.city, venue.state))
  data = []
  for location in locations:
    curData = {}
    curData["city"] = location[0]
    curData["state"] = location[1]
    curData["venues"] = Venue.query.filter_by(city = location[0], state = location[1])
    data.append(curData)

  print('data', data)
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO - Done: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response = {}
  search_term = request.form.get('search_term', '')
  searchVenues = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()  # query return a list
  count = len(searchVenues)

  response["count"] = count
  response["data"] = searchVenues
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO - Done: replace with real venue data from the venues table, using venue_id
  
  venue = Venue.query.get(venue_id)

  if not venue: 
    return render_template('errors/404.html')

  allData = Venue.query.filter_by(id = venue_id).all()
  data = allData[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO -Done: insert form data as a new venue record in the db, instead
  # TODO -Done: modify data to be the data object returned from db insertion
  error = False
  
  try:
    form = VenueForm(request.form)
    #print(form.name)
    #print(form.address)
    #v = form.validate()
    #print(form.errors)

    if form.validate():
      name = request.form['name']
      city = request.form['city']
      state = request.form['state']
      address = request.form['address']
      phone = request.form['phone']
      genres = request.form.getlist('genres')
      image_link = request.form['image_link']
      facebook_link = request.form['facebook_link']
      website = request.form['website_link']
      seeking_talent = True if 'seeking_talent' in request.form else False 
      seeking_description = request.form['seeking_description']

      venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres, image_link=image_link, 
      facebook_link=facebook_link, website=website, seeking_talent=seeking_talent, seeking_description=seeking_description)

      db.session.add(venue)

      db.session.commit()
    else:
      error = True
  
  except Exception as ex:
    print(ex)
    error = True
    db.session.rollback()

  finally:
    db.session.close()
  
  if error: flash('Failed. Venue ' + request.form['name'] + ' was not successfully listed.')
  # on successful db insert, flash success
  if not error: flash('Venue ' + request.form['name'] + ' was successfully listed!')
  
  
  # TODO -Done: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO - Done: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  # Done
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return jsonify({ 'success': True })
  # BONUS CHALLENGE: Implement a button to delete a venue on a venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  

#  artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO - Done: replace with real data returned from querying the database

  data=Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO - Done: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response = {}
  search_term = request.form['search_term']
  #search_term = request.form.get('search_term', '')

  searchArtists = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()  # query return a list
  count = len(searchArtists)
  if searchArtists:
    data = []
    for artist in searchArtists:
      upcoming_shows = Show.query.filter_by(artist_id=artist.id).all()
      curData={
        'id': artist.id,
        'name': artist.name,
        'num_upcoming_shows': len(upcoming_shows)
        }
      data.append(curData)
  response["count"] = count
  response["data"] = data
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO - Done: replace with real artist data from the artist table, using artist_id
  
  allArtists = Artist.query.all()     
  allData = []
  if allArtists:
    for artist in allArtists:         
      
      curData = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "seeking_venue": artist.seeking_venue,
        "image_link":artist.image_link}
      cur_past_shows=[]
      cur_upcoming_shows=[]
      shows=Show.query.filter_by(artist_id=artist_id).all()
      if shows:
        for show in shows:
          if show[start_time] >= datetime.now():
            curVenue=Venue.query.filter_by(venue_id=show.venue_id)
            curShow={
              "venue_id": show.venue_id,
              "venue_name": curVenue.name,
              "venue_image_link": curVenue.image_link,
              "start_time": show.start_time
            }
            cur_upcoming_shows.append(curShow)
          else:
            curVenue=Venue.query.filter_by(venue_id=show.venue_id)
            curShow={
              "venue_id": show.venue_id,
              "venue_name": curVenue.name,
              "venue_image_link": curVenue.image_link,
              "start_time": show.start_time
            }
            cur_past_shows.append(curShow)

      curData['past_shows'] = cur_past_shows
      curData['upcoming_shows'] = cur_upcoming_shows
      allData.append(curData)
 
  data = list(filter(lambda d: d['id'] == artist_id, allData))[0]
  
  if not data: 
    return render_template('errors/404.html')

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  getArtist = Artist.query.get(artist_id)

  if getArtist:
    form.name.data = getArtist.name
    form.genres.data = getArtist.genres
    form.city.data = getArtist.city
    form.state.data = getArtist.state
    form.phone.data =getArtist.phone
    form.website_link.data =getArtist.website
    form.facebook_link.data =getArtist.facebook_link
    form.seeking_venue.data =getArtist.seeking_venue
    form.seeking_description.data =getArtist.seeking_description
    form.image_link.data =getArtist.image_link
  
  #print('ddddd', form.name(class_ = 'form-control', autofocus = True))
  # TODO -Done: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=getArtist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO -Done: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  artist = Artist.query.get(artist_id)
  try:
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form.getlist('genres')
    artist.image_link = request.form['image_link']
    artist.facebook_link = request.form['facebook_link']
    artist.seeking_talent = True if 'seeking_talent' in request.form else False 
    artist.seeking_description = request.form['seeking_description']

    db.session.add(artist)
    db.session.commit()

  except Exception as inst:
    print(inst)
    error = True
    db.session.rollback()

  finally:
    db.session.close()
  
  if error: flash('Failed. Artist ' + request.form['name'] + ' was not successfully updated.')
  # on successful db insert, flash success
  if not error: flash('Artist ' + request.form['name'] + ' was successfully updated!')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  if venue:
    form.name.data = venue.name
    form.genres.data = venue.genres
    form.address.data = venue.address
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.website_link.data = venue.website
    form.facebook_link.data = venue.facebook_link
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description
    form.image_link.data = venue.image_link


  # TODO -Done: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO -Done: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False
  venue = Venue.query.get(venue_id)

  try:
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.genres = request.form.getlist('genres')
    venue.image_link = request.form['image_link']
    venue.facebook_link = request.form['facebook_link']
    venue.website = request.form['website_link']
    venue.seeking_talent = True if 'seeking_talent' in request.form else False 
    venue.seeking_description = request.form['seeking_description']

    db.session.add(venue)
    db.session.commit()
    
  except Exception as inst:
    print(inst)
    error = True
    db.session.rollback()

  finally:
    db.session.close()
  
  if error: flash('Failed. Venue ' + request.form['name'] + ' was not successfully updated.')
  # on successful db insert, flash success
  if not error: flash('Venue ' + request.form['name'] + ' was successfully updated!')
  
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  
  try:
    form = ArtistForm(request.form)
    if form.validate():
      name = request.form['name']
      city = request.form['city']
      state = request.form['state']
      phone = request.form['phone']
      genres = request.form.getlist('genres')
      image_link = request.form['image_link']
      facebook_link = request.form['facebook_link']
      website = request.form['website_link']
      seeking_venue = True if 'seeking_venue' in request.form else False 
      seeking_description = request.form['seeking_description']

      artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, image_link=image_link, 
      facebook_link=facebook_link, website=website, seeking_venue=seeking_venue, seeking_description=seeking_description)

      db.session.add(artist)
      db.session.commit()
    else:
      error = True
  
  except Exception as inst:
    print(inst)
    error = True
    db.session.rollback()

  finally:
    db.session.close()
  
  if error: flash('Failed. Artist ' + request.form['name'] + ' was not successfully listed.')
  # on successful db insert, flash success
  if not error: flash('Artist ' + request.form['name'] + ' was successfully listed!')

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO -Done: replace with real venues data.
  data=[]
  allShows = Show.query.all()

  # if not allShows:
  #   return render_template('errors/404.html')
  print('shows', allShows)
  if allShows:
    for show in allShows:
      print('show time-------', show.start_time)
      venue_name = Venue.query.get(show.venue_id).name
      artist_name = Artist.query.get(show.artist_id).name
      artist_image_link = Artist.query.get(show.artist_id).image_link
      curData = {
        "venue_id": show.venue_id,
        "venue_name": venue_name,
        "artist_id": show.artist_id,
        "artist_name": artist_name,
        "artist_image_link": artist_image_link,
        "start_time": show.start_time
      }
      data.append(curData)
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO -Done: insert form data as a new Show record in the db, instead


  # TODO -Done: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  
  error = False
  
  try:
    form = ShowForm(request.form)

    if form.validate(): 
      artist_id = request.form['artist_id']
      venue_id = request.form['venue_id']
      start_time = request.form['start_time']
      
      show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)

      db.session.add(show)
      db.session.commit()
    else:
      error = True
    
  except Exception as inst:
    print(inst)
    error = True
    db.session.rollback()

  finally:
    db.session.close()
  
  if error: flash('Failed. Show ' + ' was not successfully listed.')
  # on successful db insert, flash success
  if not error: flash('Show ' + ' was successfully listed!')
  
  return render_template('pages/home.html')

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
