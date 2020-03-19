

def init_app(app):
    from app.blueprints.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.blueprints.main import bp as main_bp
    app.register_blueprint(main_bp)
