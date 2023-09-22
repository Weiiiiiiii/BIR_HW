import streamlit as st
import xml.etree.ElementTree as ET
import re
import json
import nltk
nltk.download('punkt')
from bs4 import BeautifulSoup
from collections import OrderedDict
from nltk.tokenize import RegexpTokenizer
import string

st.set_page_config(layout="wide")
st.title("Upload files")
#上傳
upload_files = st.file_uploader(" ", type=["xml","json"], accept_multiple_files=True)

#輸入keyword
search_keyword = st.text_input("Keyword")

labels=[]


if upload_files and search_keyword:
    for upload_file in upload_files:
        if upload_file.name.endswith(".xml"):  #處理xml
            tree = ET.parse(upload_file)
            root = tree.getroot()
            xml_text = ET.tostring(root).decode()
            soup = BeautifulSoup(xml_text, "html.parser")
            
            daterevised_ele = root.find(".//DateRevised")
            year_element = daterevised_ele.find(".//Year")
            month_element = daterevised_ele.find(".//Month")
            day_element = daterevised_ele.find(".//Day")
            year = year_element.text
            month = month_element.text
            day = day_element.text
            date = f"{year}-{month}-{day}"

            PM_id = root.find('.//PMID').text
            
            author_names = []
            title_displayed = False
            n=0

            # 提取所有的AbstractText元素
            abstract_texts = soup.find_all("abstracttext")
            combined_text = " ".join(["".join(abstract.stripped_strings) for abstract in abstract_texts])
        
            for abstract_text in abstract_texts:                                #遍歷所有abstracttext
                abstract_text_content = "".join(abstract_text.stripped_strings)
                highlighted_text = re.sub(
                    f'({search_keyword})',
                    r'<span style="background-color: yellow">\1</span>',
                    abstract_text_content,
                    flags=re.IGNORECASE
                )
                if search_keyword.lower() in abstract_text_content.lower():   #輸入關鍵字後顯示文章
                    keyword_count = combined_text.lower().count(search_keyword.lower())
                    authorlist_ele = root.findall(".//AuthorList//Author")
                    for author in authorlist_ele:
                        fore_ele = author.find(".//ForeName").text
                        last_ele = author.find(".//LastName").text
                        full_name = f"{fore_ele} {last_ele}"
                        author_names.append(full_name)
                    authors_string = ", ".join(author_names)
                    if not title_displayed:                               # 顯示文章title及相關資訊
                        st.image('image\pubmed.jpg',width=200)
                        article_title = root.find(".//ArticleTitle").text
                        st.header(f"{article_title}")
                        st.write(f"<b>PMID: </b>{PM_id}",unsafe_allow_html=True)
                        st.write(f"<b>Author: </b>{authors_string}",unsafe_allow_html=True)
                        st.write(f"<b>Date: </b> {date}",unsafe_allow_html=True)
                        title_displayed = True
         

                        character_count = sum(1 for char in combined_text if char != ' ' and char.isascii()) #計算字元
                        tokenizer = RegexpTokenizer(r'\w+-\w+|\w+')
                        words = nltk.word_tokenize(combined_text)
                        word_count = 0
                        for word in words:
                            if word not in string.punctuation:
                                word_count+=1
                        sentences = nltk.sent_tokenize(combined_text)

                        sentence_count = len(sentences) 
                        statistics = f"Characters: <span style='color: #00CC00;'>{character_count}</span>,  Words: <span style='color: #00CC00;'>{word_count}</span>,  Sentences: <span style='color: #00CC00;'>{sentence_count}</span> , keyword: <span style='color: #00CC00;'>{keyword_count}</span>"
                        st.write(statistics,unsafe_allow_html=True)
                        
                    for abstract_text in root.findall(".//AbstractText"):  #獲取abstracttext的label
                        label = abstract_text.get("Label")
                        labels.append(label)
                        unique_labels = list(OrderedDict.fromkeys(labels))
                        
                    if len(unique_labels)>1 :                                #abstracttext有label時分別顯示label及他的文章 若沒有label則直接顯示文章
                        st.subheader(f"{unique_labels[n]}")
                        st.write(highlighted_text, unsafe_allow_html=True)  
                        n=n+1
                    else:
                        st.write(highlighted_text, unsafe_allow_html=True)   
            labels=[]
       
        elif upload_file.type == "application/json":
            json_data = json.load(upload_file)
    
            for item in json_data:
                text = item.get("Text", "")
                date = item.get("date", "")
                jsonid = item.get("ID", "")
                authorid = item.get("author_id", "")
        
            if search_keyword.lower() in text.lower():
                keyword_count = text.lower().count(search_keyword.lower())
                character_count = sum(1 for char in text if char != ' ' and char.isascii()) #計算字元
                tokenizer = RegexpTokenizer(r'\w+')
                words = tokenizer.tokenize(text)
                sentences = nltk.sent_tokenize(text)
                word_count = len(words)
                sentence_count = len(sentences)
                statistics = f"Characters: <span style='color: #00CC00;'>{character_count}</span>,  Words: <span style='color: #00CC00;'>{word_count}</span>,  Sentences: <span style='color: #00CC00;'>{sentence_count}</span> , keyword: <span style='color: #00CC00;'>{keyword_count}</span>"
                highlighted_text = re.sub(
                f'({search_keyword})',
                r'<span style="background-color: yellow">\1</span>',
                text,
                flags=re.IGNORECASE
                )
                st.image('image\Twitter_logo.jpg',width=200)
                st.header(f"ID: {jsonid}")
                st.subheader(f"Author ID: {authorid}")
                st.write(f"<b>Date: </b> {date}",unsafe_allow_html=True)
                st.write(statistics,unsafe_allow_html=True)
                st.write(highlighted_text, unsafe_allow_html=True)