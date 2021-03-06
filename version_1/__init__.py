from flask_cors import CORS
from flask_restful import Api
from flask import Blueprint
from version_1.resources.role import RoleList, RoleUpdate
from version_1.resources.user import UserList, UserUpdate
from version_1.resources.profile import ProfileList, ProfileUpdate

# Declare the blueprint
v1 = Blueprint('v1', __name__)

# Set up cross-scripting allowed
CORS(v1)

# Set up the API and init the blueprint
api = Api()
api.init_app(v1)

# Set the default route
@v1.route('/')
def show():
    return 'Hello World'

#############################################
########## Resources to Add
#############################################

# Profiles
api.add_resource(ProfileList, '/profiles')
api.add_resource(ProfileUpdate, '/profile/<int:id>')

# Users
api.add_resource(UserList, '/users')
api.add_resource(UserUpdate, '/users/<int:id>')

# Roles
api.add_resource(RoleList, '/roles')
api.add_resource(RoleUpdate, '/roles/<int:id>')
