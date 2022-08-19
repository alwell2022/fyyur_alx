from app import app, db

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String(255))
    genres = db.Column(db.ARRAY(db.String()), nullable=False)
    website_link = db.Column(db.String(120))
    show_list = db.relationship('Show', backref='lists', cascade='delete-orphan')

    def __repr__(self):
      return f'<Venue id {self.id} name {self.name} city {self.city} state {self.state} genres {self.genres} seeking talent {self.seeking_talent}>'
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()), nullable=False)
    image_link = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String(255))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))

    def __repr__(self):
      return f'<Artist id: {self.id} name {self.name} city {self.city} state {self.state} genres {self.genres} seeking venue {self.seeking_venue}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Show(db.Model):
  __tablename__='show'
  
  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
  start_time = db.Column(db.DateTime, nullable=False)
  # Defining relationship
  artist_list = db.relationship('Artist', backref='shows')

  def __repr__(self) -> str:
      return f'<Show id {self.id} venue id {self.venue_id} artist id {self.artist_id} start time {self.start_time}>'
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
