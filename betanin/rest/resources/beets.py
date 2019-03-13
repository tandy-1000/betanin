# standard library
import datetime

# 3rd party
from flask import abort

# betanin
from betanin import beets
from betanin.rest.base import SecureResource
from betanin.rest.models import request as req_models
from betanin.rest.models import response as resp_models
from betanin.rest.namespaces import beets_ns


@beets_ns.route('/config')
class BeetsResource(SecureResource):
    @staticmethod
    @beets_ns.marshal_list_with(resp_models.beets_config)
    def get():
        'reads the beets config from disk'
        config = beets.get_config()
        if not config:
            return abort(400, 'config does not exist')
        return {
            "time_read": datetime.datetime.now(),
            "config": config,
        }

    @staticmethod
    @beets_ns.doc(parser=req_models.beets_config)
    def put():
        'update the beets config on disk'
        args = req_models.beets_config.parse_args()
        beets.set_config(args['config'])