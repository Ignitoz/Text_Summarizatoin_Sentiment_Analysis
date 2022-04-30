# -*- coding: utf-8 -*-
"""
Created on Sat Apr 16 13:44:33 2022

@author: VENKATA SANDEEP
"""
import streamlit as st
import re
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from heapq import nlargest
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
import pdfplumber
import text2emotion as te
nlp = spacy.load('en_core_web_sm')

def pdf(file):
    pdf = pdfplumber.open(file)
    n=len(pdf.pages)
    
    text=""
    for page in range(n):
        data = pdf.pages[page].extract_text()
        text=text+" "+data
    pdf.close()
    text =re.sub("\n"," ",text)
    text = re.sub("\x0c"," ",text)
    text = re.sub(r'Chapter \d+'," ",text)
    text = re.sub("Prologue"," ",text)
    text= re.sub(r'• • • •',' ',text)
    text = re.sub(r'\s+',' ',text)
    return text        

def txt(file):
    text=file.read().decode("utf-8", "ignore")
    text =re.sub("\n"," ",text)
    text = re.sub("\x0c"," ",text)
    text = re.sub(r'Chapter \d+'," ",text)
    text = re.sub("Prologue"," ",text)
    text= re.sub(r'• • • •',' ',text)
    text = re.sub(r'\s+',' ',text)
    return text       

def callback():
    st.session_state.button_clicked =True


def summary(text):
    stopwords = list(STOP_WORDS)    
    doc= nlp(text)
    punct = punctuation + '\n' + '“' + '”' 
    word_frequencies= {}
    for word in doc:
        if word.text.lower() not in stopwords:
            if word.text.lower() not in punct:
                if word.text not in word_frequencies.keys():
                    word_frequencies[word.text] =1
                else:
                    word_frequencies[word.text] +=1
    max_frequency = max(word_frequencies.values())
    for word in word_frequencies.keys():
        word_frequencies[word] = word_frequencies[word]/max_frequency
    sentence_tokens = [sent for sent in doc.sents]
    sentence_scores = {}
    for sent in sentence_tokens:
        for word in sent:
            if word.text.lower() in word_frequencies.keys():
                if sent not in sentence_scores.keys():
                    sentence_scores[sent] = word_frequencies[word.text.lower()]
                else:
                    sentence_scores[sent] += word_frequencies[word.text.lower()] 
    select_length = int(len(sentence_tokens)*0.15)
    sumy = nlargest(select_length,sentence_scores,key = sentence_scores.get)
    final_summary = [word.text for word in sumy]
    sumy = ' '.join(final_summary)
    return sumy       

def analysis(text):
    col1, col2 = st.columns([1,1])
    sumy=summary(text)
    sentiment= SentimentIntensityAnalyzer()
    score=sentiment.polarity_scores(sumy)
    if score['compound']<0:
        st.subheader("Negative :( \n")
    elif score['compound']>0 and score['compound']<0.49:
        st.subheader("Neutral \n")
    else :
        st.subheader("Positve :) \n")
    score.pop('compound')
    value = score.values()
    fig1, ax1 = plt.subplots(figsize=(2.1,2))
    ax1.pie(value, labels=['Negative','Neutral','Positive'], autopct='%1.1f%%',normalize=True)
    ax1.axis('equal')  # Equal aspect ratio ensures the pie chart is circular.
    ax1.set_title('Sentiment Analysis')
    col1.pyplot(fig1)
    score=te.get_emotion(sumy)
    fig2, ax2 = plt.subplots(figsize=(2.7,2))
    circle = plt.Circle( (0,0), 0.6, color='white')
    values=score.values()
    labels=score.keys()
    ax2.pie(values, labels=labels, autopct='%1.1f%%',normalize=True)
    ax2.axis('equal')  # Equal aspect ratio ensures the pie chart is circular.
    ax2.set_title('Emotion Analysis \n')
    p=plt.gcf()
    p.gca().add_artist(circle)
    col2.pyplot(fig2)
    

def main():
    st.title("Text Summarization")
    menu = ["Text File","PDF File"]
    choice = st.sidebar.selectbox("Select File Type",menu)
    
    if choice== "Text File" :
        st.subheader("Upload Text File")
        txt_file = st.file_uploader("Upload Text File",type=["txt"])
        if txt_file is not None:
            st.write(type(txt_file))
            file_details = {"filename":txt_file.name,
                            "filetype":txt_file.type,
                            "filesize":txt_file.size}
            
    elif choice == "PDF File" :
         st.subheader("Upload PDF File")
         txt_file = st.file_uploader("Upload PDF File",type=["pdf"])
         if txt_file is not None:
             st.write(type(txt_file))
             file_details = {"filename":txt_file.name,
                             "filetype":txt_file.type,
                             "filesize":txt_file.size}
    st.write("\n\n\n\n\n\n")
    col1, col2 = st.columns([.25,1])
    if txt_file is not None:        
        if txt_file.type == "application/pdf" :
            text= pdf(txt_file)
            
            if col1.button("Summary"):
                sumy= summary(text)
                st.text_area(label ="",value=sumy, height =300)
            if col2.button("Analysis"):
                analysis(text)
        elif txt_file.type == "text/plain" :
            text = txt(txt_file)
            if col1.button("Summary"):
                sumy= summary(text)
                st.text_area(label ="",value=sumy, height =300)
            if col2.button("Analysis"):
                analysis(text)
    else :
        pass        
     
    
            

if __name__ == '__main__':
    main()
            