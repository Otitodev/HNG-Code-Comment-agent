from mangum import Mangum
from app.main import app

# AWS Lambda handler adapted from FastAPI via Mangum
handler = Mangum(app)