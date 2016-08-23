# Import section
from flask import Blueprint

blueprint = Blueprint('test',__name__)

@blueprint.route("/test")
def test():
	return "Test function"

