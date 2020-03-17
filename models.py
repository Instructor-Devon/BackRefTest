from app import db
from sqlalchemy.sql import func

likes_table = db.Table('likes', 
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete="cascade"), primary_key=True), 
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id', ondelete="cascade"), primary_key=True))

posts_categories = db.Table('posts_categories',
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id', ondelete="cascade"), primary_key=True), 
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id', ondelete="cascade"), primary_key=True))

# some_user.posts => [Post, Post]
class User(db.Model):	
    __tablename__ = "users"    # optional		
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(45))
    last_name = db.Column(db.String(45))
    pic = db.Column(db.String(45))
    email = db.Column(db.String(45), unique=True)
    password = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, server_default=func.now())    # notice the extra import statement above
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

    posts = db.relationship(
        "Post",
        back_populates="author",
        cascade="all, delete, delete-orphan"
    )

    #NEW!
    likes_sent = db.relationship("Post", secondary=likes_table)
    #posts

    def __repr__(self):
        return f"<User: {self.email}>"

class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="cascade"), nullable=False)
    author = db.relationship('User', foreign_keys=[author_id])

    created_at = db.Column(db.DateTime, server_default=func.now())    # notice the extra import statement above
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

    #NEW! [User1, User2, User3]
    likes_rec = db.relationship("User", secondary=likes_table)
    categories = db.relationship("Category", secondary=posts_categories)

    @property
    def num_likes(self):
        # likes_rec [User1, User2]
        return len(self.likes_rec)

    def __repr__(self):
        return f"<Post: \"{self.content[:5]}...\">"

class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=func.now())    # notice the extra import statement above
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

    posts = db.relationship("Post", secondary=posts_categories)