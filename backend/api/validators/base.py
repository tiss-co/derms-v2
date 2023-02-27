from flask_restful.reqparse import Argument

from flask import Response, abort
import json


class APIArgument(Argument):
    def __init__(self, *args, **kwargs):
        super(APIArgument, self).__init__(*args, **kwargs)

    def handle_validation_error(self, error, bundle_errors):
        help_str = "(%s) " % self.help if self.help else ""
        msg = "[%s]: %s%s" % (self.name, help_str, str(error))
        res = Response(
            json.dumps(
                {
                    "message": msg,
                    "code": 400,
                }
            ),
            mimetype="application/json",
            status=400,
        )
        return abort(res)
