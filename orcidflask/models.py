from orcidflask import db
from sqlalchemy.sql import func

class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.String(80), unique=False, nullable=False)
    access_token = db.Column(db.String(80), unique=False, nullable=False)
    refresh_token = db.Column(db.String(80), unique=False, nullable=False)
    expires_in = db.Column(db.Integer, nullable=False)
    token_scope = db.Column(db.String(80), unique=False, nullable=False)
    orcid = db.Column(db.String(80), unique=False, nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return '<User %r, access_token=%r, token_scope=%r, orcid=%r' % \
                (self.userId, self.access_token, self.token_scope, self.orcid)
