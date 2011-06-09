from datetime import datetime,date
from os.path import join
from sys import argv
from xml.sax import parse
from xml.sax.handler import ContentHandler

class SEdb(object):
    def __init__(self):
        self.badges = []
        self.comments = []
        self.posts = {}
        self.post_history = []
        self.users = {}
        self.votes = []

    def validate(self):
        for vote in self.votes:
            if vote.post_id not in self.posts:
                print "Vote %d invalid" % vote.id
            if vote.user_id is not None and vote.user_id not in self.users:
                print "Vote %d invalid" % vote.id

        for badge in self.badges:
            if badge.user_id not in self.users:
                print "Badge %d invalid" % badge.id

        for comment in self.comments:
            if comment.user_id is not None and comment.user_id not in self.users:
                print "Comment %d invalid" % comment.id

        for ph in self.post_history:
            if ph.post_id not in self.posts:
                print "Post History %d invalid" % ph.id

            if ph.user_id is not None and ph.user_id not in self.users:
                print "Post History %d invalid" % ph.id

class Badge(object):
    def __init__(self,data):
        self.user_id = int(data['UserId'])
        self.name = data['Name']
        self.date = datetime.strptime(data['Date']+u" UTC",'%Y-%m-%dT%H:%M:%S.%f %Z')

class Post(object):
    def __init__(self,data):
        self.parent_id = self.owner_user_id = self.comment_count = self.favorite_count = self.answer_count = self.accepted_answer_id =  self.tags = self.title = self.last_editor_display_name = self.closed_date = self.last_editor_user_id = self.last_edit_date = self.community_owned_date = None
        self.id = int(data['Id'])
        self.post_type_id = int(data['PostTypeId'])
        if self.post_type_id == 2:
            self.parent_id = int(data['ParentId'])
        if 'AcceptedAnswerId' in data:
            self.accepted_answer_id = int(data['AcceptedAnswerId'])
        self.creation_date = datetime.strptime(data['CreationDate']+u" UTC",'%Y-%m-%dT%H:%M:%S.%f %Z')
        self.score = int(data['Score'])
        try:
            self.view_count = int(data['ViewCount'])
        except ValueError:
            self.view_count = -1
        self.body = data['Body']
        if 'OwnerUserId' in data:
            self.owner_user_id = int(data['OwnerUserId'])
        if 'LastEditorUserId' in data:
            self.last_editor_user_id = int(data['LastEditorUserId'])
        if 'LastEditorDisplayName' in data:
            self.last_editor_display_name = data['LastEditorDisplayName']
        if 'LastEditDate' in data:
            self.last_edit_date = datetime.strptime(data['LastEditDate']+u" UTC",'%Y-%m-%dT%H:%M:%S.%f %Z')
        self.last_activity_date = datetime.strptime(data['LastActivityDate']+u" UTC",'%Y-%m-%dT%H:%M:%S.%f %Z')
        if 'CommunityOwnedDate' in data:
            self.community_owned_date = datetime.strptime(data['CommunityOwnedDate']+u" UTC",'%Y-%m-%dT%H:%M:%S.%f %Z')
        if 'ClosedDate' in data:
            self.closed_date = datetime.strptime(data['ClosedDate']+u" UTC",'%Y-%m-%dT%H:%M:%S.%f %Z')
        if 'Title' in data:
            self.title = data['Title']
        if 'Tags' in data:
            self.title = data['Tags']
        if 'AnswerCount' in data:
            self.answer_count = int(data['AnswerCount'])
        if 'CommentCount' in data:
            self.comment_count = int(data['CommentCount'])
        if 'FavoriteCount' in data:
            self.favorite_count = int(data['FavoriteCount'])

class User(object):
    def __init__(self,data):
        self.location = self.about_me = self.age = self.website_url = None
        self.id = int(data['Id'])
        self.reputation = int(data['Reputation'])
        self.creation_date = datetime.strptime(data['CreationDate']+u" UTC",'%Y-%m-%dT%H:%M:%S.%f %Z')
        self.display_name = data['DisplayName']
        self.email_hash = data['EmailHash']
        self.last_access_date = datetime.strptime(data['LastAccessDate']+u" UTC",'%Y-%m-%dT%H:%M:%S.%f %Z')
        if 'WebsiteUrl' in data:
            self.website_url = data['WebsiteUrl']
        if 'Location' in data:
            self.location = data['Location']
        if 'Age' in data:
            self.age = int(data['Age'])
        if 'AboutMe' in data:
            self.about_me = data['AboutMe']
        self.views = int(data['Views'])
        self.up_votes = int(data['UpVotes'])
        self.down_votes = int(data['DownVotes'])


class Comment(object):
    def __init__(self,data):
        self.score = self.user_id = None
        self.id = int(data['Id'])
        self.post_id = int(data['PostId'])
        if 'Score' in data:
            self.score = int(data['Score'])
        self.text = data['Text']
        self.creation_date = datetime.strptime(data['CreationDate']+u" UTC",'%Y-%m-%dT%H:%M:%S.%f %Z')
        if 'UserId' in data:
            self.user_id = int(data['UserId'])

class PostHistory(object):
    def __init__(self,data):
        self.user_id = self.user_display_name = self.comment = self.text = self.close_reason_id = None
        self.id = int(data['Id'])
        self.post_history_type_id = int(data['PostHistoryTypeId'])
        self.post_id = int(data['PostId'])
        self.revision_guid = data['RevisionGUID']
        self.creation_date = datetime.strptime(data['CreationDate']+u" UTC",'%Y-%m-%dT%H:%M:%S.%f %Z')
        if 'UserId' in data:
            self.user_id = int(data['UserId'])
        if 'UserDisplayName' in data:
            self.user_display_name = data['UserDisplayName']
        if 'Comment' in data:
            self.comment = data['Comment']
        if 'Text' in data:
            self.text = data['Text']
        if 'CloseReasonId' in data:
            self.close_reason_id = int(data['CloseReasonId'])

class Vote(object):
    def __init__(self,data):
        self.user_id = self.bounty_amount = None
        self.id = int(data['Id'])
        self.post_id = int(data['PostId'])
        self.vote_type_id = int(data['VoteTypeId'])
        y,m,d = data['CreationDate'].split('-',2)
        self.create_date = date(int(y),int(m),int(d))
        if 'UserId' in data:
            self.user_id = int(data['UserId'])
        if 'BountyAmount' in data:
            self.bounty_amount = int(data['BountyAmount'])


class BadgeHandler(ContentHandler):
    def __init__(self,db):
        self.db = db

    def startElement(self, name, attributes):
        if name == 'row':
            self.db.badges.append(Badge(attributes))

class CommentHandler(ContentHandler):
    def __init__(self,db):
        self.db = db

    def startElement(self, name, attributes):
        if name == 'row':
            self.db.comments.append(Comment(attributes))

class PostHistoryHandler(ContentHandler):
    def __init__(self,db):
        self.db = db

    def startElement(self, name, attributes):
        if name == 'row':
            self.db.post_history.append(PostHistory(attributes))

class VoteHandler(ContentHandler):
    def __init__(self,db):
        self.db = db

    def startElement(self, name, attributes):
        if name == 'row':
            self.db.votes.append(Vote(attributes))

class PostHandler(ContentHandler):
    def __init__(self,db):
        self.db = db

    def startElement(self, name, attributes):
        if name == 'row':
            self.db.posts[int(attributes['Id'])] = Post(attributes)

class UserHandler(ContentHandler):
    def __init__(self, db):
        self.db = db

    def startElement(self, name, attributes):
        if name == 'row':
            self.db.users[int(attributes['Id'])] = User(attributes)




def run():
    dir_name = argv[1]
    db = SEdb()
    badge_xml = join(dir_name,'badges.xml')
    parse(badge_xml,BadgeHandler(db))

    post_xml = join(dir_name,'posts.xml')
    parse(post_xml,PostHandler(db))

    users_xml = join(dir_name,'users.xml')
    parse(users_xml,UserHandler(db))

    votes_xml = join(dir_name,'votes.xml')
    parse(votes_xml,VoteHandler(db))

    comments_xml = join(dir_name,'comments.xml')
    parse(comments_xml,CommentHandler(db))

    posthistory_xml = join(dir_name,'posthistory.xml')
    parse(posthistory_xml,PostHistoryHandler(db))

    b = db.badges[0]
    p = db.posts[1]
    u = db.users[2]
    v = db.votes[0]
    c = db.comments[0]
    ph = db.post_history[0]
    print "Ready"

    db.validate()
    
