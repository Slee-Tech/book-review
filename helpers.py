import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps



def lookup(api_key, books_isbn):
    
    #Contact API
   
    response = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": api_key, "isbns": books_isbn})
    info = response.json()
    return info
        
    