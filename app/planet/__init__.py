from flask import Blueprint, render_template


# No url_prefix: it would be prepended to static_url_path and force the view
# rule to "/", making Werkzeug redirect /planet -> /planet/.
planet_bp = Blueprint(
    "planet",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/planet/static",
)


@planet_bp.get("/planet")
def island():
    return render_template("planet/index.html")
