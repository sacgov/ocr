import datetime
import io

import pytesseract
from PIL import Image
from flask import Flask, request, render_template, redirect, url_for, session

import spacy
import spacy.cli

import importlib.util
spacy_web = importlib.util.find_spec("en_core_web_sm")
if spacy_web is None:
    spacy.cli.download("en_core_web_sm")
from urlextract import URLExtract

nlp = spacy.load("en_core_web_sm")
import en_core_web_sm

nlp = en_core_web_sm.load()


def extract_dates(tokens):
    ents = tokens.ents
    results = [ent.text for ent in ents if ent.label_ == 'DATE']
    return results



app = Flask(__name__)

# Secret key for sessions encryption
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route('/')
def home():
    return render_template("index.html", title="Image Reader")


@app.route('/scanner', methods=['GET', 'POST'])
def scan_file():
    if request.method == 'POST':
        start_time = datetime.datetime.now()
        image_data = request.files['file'].read()

        scanned_text = pytesseract.image_to_string(Image.open(io.BytesIO(image_data)))

        tokens = nlp(scanned_text)
        dates = extract_dates(tokens)
        

        extractor = URLExtract()
        urls = extractor.find_urls(scanned_text)

        print (dates)
        print (urls)

        session['data'] = {
            "text": scanned_text,
            "time": str((datetime.datetime.now() - start_time).total_seconds()),
            "urls":urls,
            "dates": dates,
        }


        

        return redirect(url_for('result'))


@app.route('/result')
def result():
    if "data" in session:
        data = session['data']
        return render_template(
            "result.html",
            title="Result",
            time=data["time"],
            text=data["text"],
            words=len(data["text"].split(" ")),
            urls=data["urls"],
            dates=data["dates"]
        )
    else:
        return "Wrong request method."


if __name__ == '__main__':
    # Setup Tesseract executable path
    app.run(debug=True)
