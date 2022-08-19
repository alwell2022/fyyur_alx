#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from operator import contains
import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from sqlalchemy.sql import func
from models import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

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
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  venues = db.session.query(Venue.city, Venue.state).order_by(Venue.city, Venue.state).all()
  data = list()
  for venue in set(venues):
    addr = {"city":'','state':'','venues':[]}
    addrs = set(db.session.query(Venue.city, Venue.state).filter(Venue.city==venue[0], Venue.state==venue[1]).order_by(Venue.city, Venue.state).all())
    for a in addrs:
      addr["city"] = a[0]
      addr["state"] = a[1]
      centers = db.session.query(Venue.id, Venue.name, func.count(Venue.show_list)).join(Show, Show.venue_id==Venue.id).filter(Venue.city==venue[0], Venue.state==venue[1]).group_by(Venue.id).order_by(Venue.id).all()
      for c in centers:
        center = {}
        center["id"] = c[0]
        center["name"] = c[1]
        center["num_upcoming_shows"] = c[2]
        addr["venues"].append(center) 
    data.append(addr)
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  name = request.form.get('search_term', '')
  data = {}
  venues = Venue.query.filter(Venue.name.ilike(f"%{name}%")).all()
  data={
    "count": len(venues),
    "data": venues
  }
  return render_template('pages/search_venues.html', results=data, search_term=name)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  data = {"upcoming_shows":[], "past_shows":[]}
  data['id'] = venue.id
  data['name'] = venue.name
  data['genres'] = venue.genres
  data['address'] = venue.address
  data['city'] = venue.city
  data['state'] = venue.state
  data['phone'] = venue.phone
  data['website'] = venue.website_link
  data['facebook_link'] = venue.facebook_link
  data['seeking_talent'] = venue.seeking_talent
  data['seeking_description'] = venue.seeking_description
  data['image_link'] = venue.image_link

  past_shows = db.session.query(Show.artist_id, Artist.name, Artist.image_link, Show.start_time).join(Artist, Artist.id==Show.artist_id).filter(Show.venue_id==2).\
              filter(Show.start_time < func.now()).order_by(Show.start_time.desc()).all()
  for ps in past_shows:
    past_show = {}
    past_show["artist_id"] = ps[0]
    past_show["artist_name"] = ps[1]
    past_show["artist_image_link"] = ps[2]
    past_show["start_time"] = ps[3]
    data["past_shows"].append(past_show)

  upcoming_shows = db.session.query(Show.artist_id, Artist.name, Artist.image_link, Show.start_time).join(Artist, Artist.id==Show.artist_id).filter(Show.venue_id==venue_id).\
              filter(Show.start_time >= func.now()).order_by(Show.start_time.desc()).all()
  for us in upcoming_shows:
    upcoming_show = {}
    upcoming_show["artist_id"] = us[0]
    upcoming_show["artist_name"] = us[1]
    upcoming_show["artist_image_link"] = us[2]
    upcoming_show["start_time"] = us[3]
    data["upcoming_shows"].append(upcoming_show)
    data["past_shows_count"] = len(data["past_shows"])    
    data["upcoming_shows_count"] = len(data["upcoming_shows"])    

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm(request.form)
  error = False
  data = {'name':''}
  try:
    if form.seeking_talent.data == "y":
      seeking_talent = True
    else:
      seeking_talent = False
    venue = Venue(name=form.name.data, city=form.city.data, state=form.state.data, address=form.address.data, \
      phone=form.phone.data, image_link=form.image_link.data, facebook_link=form.facebook_link.data, \
        genres=form.genres.data, website_link=form.website_link.data, seeking_talent=seeking_talent, seeking_description=form.seeking_description.data)
    db.session.add(venue)
    db.session.commit()
    data['name'] = form.name.data
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if not error:       
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
  else:
    flash('An error occurred. Venue ' + data['name'] + ' could not be listed.') 
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  error = False
  try:
    data = {'name':''}
    print("ID: ",venue_id)
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    data['name'] = venue['name']
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info()) 
  finally:
    db.session.close() 
  if not error:
    flash('Venue ' + data['name'] + ' was successfully deleted!')
  else:
  # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + data['name'] + ' could not be deleted.')     
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = db.session.query(Artist.id, Artist.name).all()
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  name = request.form.get('search_term', '')
  data = {}
 
  artists = Artist.query.filter(Artist.name.ilike(f"%{name}%")).all()
  data={
    "count": len(artists),
    "data": artists
  }

  return render_template('pages/search_artists.html', results=data, search_term=name)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)
  data = {"upcoming_shows":[], "past_shows":[]}
  
  data['id'] = artist.id
  data['name'] = artist.name
  data['genres'] = artist.genres
  data['city'] = artist.city
  data['state'] = artist.state
  data['phone'] = artist.phone
  data['website'] = artist.website_link
  data['facebook_link'] = artist.facebook_link
  data['seeking_venue'] = artist.seeking_venue
  data['seeking_description'] = artist.seeking_description
  data['image_link'] = artist.image_link
    # ---------past shows associated to venue that was selected
  past_shows = db.session.query(Show.venue_id, Venue.name, Venue.image_link, Show.start_time).join(Venue, Venue.id==Show.venue_id).filter(Show.artist_id==artist_id).filter(Show.start_time < func.now()).order_by(Show.start_time.desc()).all()
  for ps in past_shows:
    past_show = {}
    past_show["venue_id"] = ps[0]
    past_show["venue_name"] = ps[1]
    past_show["venue_image_link"] = ps[2]
    past_show["start_time"] = ps[3]
    data["past_shows"].append(past_show)
    # ---------upcoming shows associated to artist that was selected
  up_shows = db.session.query(Show.venue_id, Venue.name, Venue.image_link, Show.start_time).join(Venue, Venue.id==Show.venue_id).filter(Show.artist_id==artist_id).filter(Show.start_time >= func.now()).order_by(Show.start_time.desc()).all()
  for us in up_shows:
    upcoming_show = {}
    upcoming_show["venue_id"] = us[0]
    upcoming_show["venue_name"] = us[1]
    upcoming_show["venue_image_link"] = us[2]
    upcoming_show["start_time"] = us[3]
    data["upcoming_shows"].append(upcoming_show)

  data["past_shows_count"] = len(data["past_shows"])    
  data["upcoming_shows_count"] = len(data["upcoming_shows"])              
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # TODO: populate form with fields from artist with ID <artist_id>
  artist=Artist.query.filter(Artist.id==artist_id).first()
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = Artist.query.get(artist_id)
  form = ArtistForm(request.form)
  error = False
  data = {'name':''}
  try:
    artist.name=form.name.data
    artist.city=form.city.data
    artist.state=form.state.data
    artist.phone=form.phone.data
    artist.image_link=form.image_link.data
    artist.facebook_link=form.facebook_link.data
    artist.genres=form.genres.data
    artist.website_link=form.website_link.data
    if form.seeking_venue.data == "y":
      artist.seeking_venue=True
    else:  
      artist.seeking_venue=False
    artist.seeking_description=form.seeking_description.data
    db.session.add(artist)
    db.session.commit()
    data['name'] = form.name.data    
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if not error:       
      # on successful db update, flash success
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
  else:
      # TODO: on unsuccessful db update, flash an error instead.
    flash('An error occurred. Artist ' + data['name'] + ' could not be updated.')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue=Venue.query.filter(Venue.id==venue_id).first()
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)
  error = False
  data = {'name':''}
  venue = Venue.query.filter_by(id=venue_id).first()
  try:
    venue.name=form.name.data
    venue.city=form.city.data
    venue.state=form.state.data
    venue.addres=form.address.data
    venue.phone=form.phone.data
    venue.image_link=form.image_link.data
    venue.facebook_link=form.facebook_link.data
    venue.genres=form.genres.data
    venue.website_link=form.website_link.data
    if form.seeking_talent.data == "y":
      venue.seeking_talent=True
    else:  
      venue.seeking_talent=False
    venue.seeking_description=form.seeking_description.data
    db.session.add(venue)
    db.session.commit()
    data['name'] = form.name.data     
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if not error:       
      # on successful db update, flash success
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  else:
      # TODO: on unsuccessful db update, flash an error instead.
    flash('An error occurred. Venue ' + data['name'] + ' could not be updated.')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm(request.form)
  error = False
  data = {'name':''}
  Artist.query.filter_by(name=form.name.data).first()
  try:
    if form.seeking_venue.data == "y":
      seeking_venue = True
    else:
      seeking_venue = False
      
    artist = Artist(name=form.name.data, city=form.city.data, state=form.state.data, phone=form.phone.data, \
      image_link=form.image_link.data, facebook_link=form.facebook_link.data, genres=form.genres.data, \
        website_link=form.website_link.data, seeking_venue=seeking_venue, seeking_description=form.seeking_description.data)
    db.session.add(artist)
    db.session.commit()
    data['name'] = form.name.data
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if not error:       
      # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  else:
      # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + data['name'] + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = db.session.query(Show.venue_id, Venue.name, Show.artist_id, Artist.name, Artist.image_link, Show.start_time)\
                .join(Venue, Venue.id==Show.venue_id).join(Artist, Artist.id==Show.artist_id).order_by(Show.start_time.desc()).all()                             
  return render_template('pages/shows.html', shows=shows)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  form = ShowForm(request.form)
  error = False
  venue = Venue.query.filter(Venue.id==form.venue_id.data).first()
  artist = Artist.query.filter(Artist.id==form.artist_id.data).first()
  
  try:
    show = Show(venue_id=venue.id, artist_id=artist.id, start_time=form.start_time.data)
    show.artist_list = artist
    venue.show_list.append(show)
    db.session.add(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if not error:
      # on successful db insert, flash success
    flash('Show was successfully listed!')
  else:
      # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Show could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
