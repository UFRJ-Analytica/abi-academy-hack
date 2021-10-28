import sentencepiece as spm
import ctranslate2
from nltk import sent_tokenize
from flask import Flask, json, request, jsonify
from flask_restful import Resource, Api, reqparse
import pandas as pd
import json



def tokenize(text, sp_source_model):
    """Use SentencePiece model to tokenize a sentence
    Args:
        text (str): A sentence to tokenize
        sp_source_model (str): The path to the SentencePiece source model
    Returns:
        List of of tokens of the text.
    """

    sp = spm.SentencePieceProcessor(sp_source_model)
    tokens = sp.encode(text, out_type=str)
    return tokens


def detokenize(text, sp_target_model):
    """Use SentencePiece model to detokenize a sentence
    Args:
        text (list(str)): A sentence to tokenize
        sp_target_model (str): The path to the SentencePiece target model
    Returns:
        String of the detokenized text.
    """

    sp = spm.SentencePieceProcessor(sp_target_model)
    translation = sp.decode(text)
    return translation


def translate(source, ct_model, sp_source_model, sp_target_model, device="cpu"):
    """Use CTranslate model to translate a sentence
    Args:
        source (str): A source sentence to translate
        ct_model (str): The path to the CTranslate model
        sp_source_model (str): The path to the SentencePiece source model
        sp_target_model (str): The path to the SentencePiece target model
        device (str): "cpu" (default) or "cuda"
    Returns:
        Translation of the source text.
    """

    translator = ctranslate2.Translator(ct_model, device)
    source_sentences = sent_tokenize(source)
    source_tokenized = tokenize(source_sentences, sp_source_model)
    translations = translator.translate_batch(source_tokenized, replace_unknowns=True)
    translations = [translation[0]["tokens"] for translation in translations]
    translations_detokenized = detokenize(translations, sp_target_model)
    translation = " ".join(translations_detokenized)

    return translation

app = Flask(__name__)

model = "ende_ctranslate2"
sp_source_model = "sentence-piece-model/source.model"
sp_target_model = "sentence-piece-model/target.model"

@app.route("/fr_en", methods = ['POST'])
def translate_request():
    input_data = request.get_json()
    text = input_data['text']
    text = str.lower(text)

    traducao = translate(text, model, sp_source_model, sp_target_model)

    return jsonify(traducao)

if __name__ == '__main__':
    app.run()  # run our Flask app