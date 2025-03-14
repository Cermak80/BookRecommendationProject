# Importing necessary libraries
import DataPreparation  # Only if you want to update dataset while starting the app
from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import book_rec


# uvicorn main:app --host 127.0.0.1 --port 8000 (The code for launching the app on the local server)
# Creating API
app = FastAPI()

app.mount("/Static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    """
    After opening the app and root "/", the function will set up html page to MainPage.html
    :param request:
    :return: templates.TemplateResponse
    """
    #return templates.TemplateResponse(request,"MainPage.html")
    return templates.TemplateResponse("MainPage.html", {"request": request})


@app.get("/get-options")
async def get_options(term: str = Query(""), limit: int = 20):
    """
    The function for the book search system in the slicer. Every time the value in the slicer is changed the function
    filters available books
    :param term: string in the slicer input field
    :param limit: The maximum amount of books that should be displayed (because of performance)
    :return: JSON response with names of related books
    """
    filtered_books = [f for f in book_rec.get_options() if term.lower() in f["Book-Title"].lower()][:limit]

    return JSONResponse(filtered_books)


class SentData(BaseModel):
    ISBN: str


@app.post("/sent-data")
async def receive_data(data: SentData):
    """
    Post function which receives data from the frontend (name of the book), puts it through the recommendation system
    and returns recommended books with the author and photo of the cover
    :param data: Data sent from the frontend (javascript)
    :return: JSON response with status and recommended books (book,Book-Author,Image-URL-L)
    """
    rec_books = book_rec.book_recommendation_engine(data.ISBN)
    rec_books = rec_books.to_dict(orient="records")
    return JSONResponse(content={"status": "success", "rec_books": rec_books})





