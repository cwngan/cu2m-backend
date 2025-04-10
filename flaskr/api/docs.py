from flask_swagger_ui import get_swaggerui_blueprint

route = get_swaggerui_blueprint(
    "/docs",  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    "http://petstore.swagger.io/v2/swagger.json",
    config={"app_name": "Test application"},
)
