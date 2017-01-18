from flask_restful import Resource
from marshmallow import ValidationError
from db.models import Profile, ProfileSchema, db
from sqlalchemy.exc import SQLAlchemyError
from flask import jsonify, make_response, request
from flask_jwt import jwt_required


# http://marshmallow.readthedocs.org/en/latest/quickstart.html#declaring-schemas
# https://github.com/marshmallow-code/marshmallow-jsonapi
schema = ProfileSchema(include_data=('user',))

class ProfileList(Resource):

    @jwt_required()
    def get(self):
        '''
        http://jsonapi.org/format/#fetching
        A server MUST respond to a successful request to fetch an individual resource or resource collection
        with a 200 OK response.

        A server MUST respond with 404 Not Found when processing a request to fetch a single resource that
        does not exist, except when the request warrants a 200 OK response with null as the primary data
        (as described above) a self link as part of the top-level links object
        '''
        profiles_query = Profile.query.all()
        results = schema.dump(profiles_query, many=True).data
        return results

    @jwt_required()
    def post(self):
        '''
        http://jsonapi.org/format/#crud
        A resource can be created by sending a POST request to a URL that represents a collection of resources.
        The request MUST include a single resource object as primary data. The resource object MUST contain at
        least a type member.

        If a POST request did not include a Client-Generated ID and the requested resource has been created
        successfully, the server MUST return a 201 Created status code
        '''
        raw_dict = request.get_json(force=True)
        try:
            # Validate Data
            schema.validate(raw_dict)

            # Save the new dog
            profile_dict = raw_dict['data']['attributes']
            profile = Profile(profile_dict['user_id'])
            for key, value in profile_dict.items():
                if key != 'user_id':
                    setattr(profile, key, value)

            profile.add(profile)

            # Return the new profile information
            query   = Profile.query.get(profile.id)
            results = schema.dump(query).data
            return results, 201

        except ValidationError as err:
            resp = jsonify({"error": err.messages})
            resp.status_code = 403
            return resp

        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            resp.status_code = 403
            return resp


class ProfileUpdate(Resource):
    @jwt_required()
    def get(self, id):
        '''
        http://jsonapi.org/format/#fetching
        A server MUST respond to a successful request to fetch an individual resource or resource collection with
        a 200 OK response.

        A server MUST respond with 404 Not Found when processing a request to fetch a single resource that does not
        exist, except when the request warrants a 200 OK response with null as the primary data (as described above)
        a self link as part of the top-level links object
        '''
        profile_query = Profile.query.get_or_404(id)
        result = schema.dump(profile_query).data
        return result

    @jwt_required()
    def patch(self, id):
        '''
        http://jsonapi.org/format/#crud-updating
        The PATCH request MUST include a single resource object as primary data. The resource object MUST contain
        type and id members.

        If a request does not include all of the attributes for a resource, the server MUST interpret the missing
        attributes as if they were included with their current values. The server MUST NOT interpret missing
        attributes as null values.

        If a server accepts an update but also changes the resource(s) in ways other than those specified by the
        request (for example, updating the updated-at attribute or a computed sha), it MUST return a 200 OK
        response. The response document MUST include a representation of the updated resource(s) as if a GET request was made to the request URL.

        A server MUST return 404 Not Found when processing a request to modify a resource that does not exist.
        '''
        profile = Profile.query.get_or_404(id)
        raw_dict = request.get_json(force=True)

        try:
            schema.validate(raw_dict)
            profile_dict = raw_dict['data']['attributes']
            for key, value in profile_dict.items():
                setattr(profile, key, value)

            profile.update()
            return self.get(id)

        except ValidationError as err:
                resp = jsonify({"error": err.messages})
                resp.status_code = 401
                return resp

        except SQLAlchemyError as e:
                db.session.rollback()
                resp = jsonify({"error": str(e)})
                resp.status_code = 401
                return resp

    @jwt_required()
    def delete(self, id):
        '''
        http://jsonapi.org/format/#crud-deleting
        A server MUST return a 204 No Content status code if a deletion request is successful and no content is returned.
        '''
        profile = Profile.query.get_or_404(id)
        try:
            profile.delete(profile)
            response             = make_response()
            response.status_code = 204
            return response

        except SQLAlchemyError as e:
                db.session.rollback()
                resp = jsonify({"error": str(e)})
                resp.status_code = 401
                return resp
