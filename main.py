from fastapi import FastAPI

app = FastAPI(
    title="Rocky API",
    description="a REST API using python and mysql",
)

@app.get("/")
async def root():
    return "hola"