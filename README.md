# si507_final_project

## data source
1. Yelp Fusion API (api_key needed, should go to https://www.yelp.com/developers/documentation/v3/get_started to apply)
   i save my api_key in secret.py file
2. wikipedia page web scrap

## data process 
1. init: create tables in database and update glocal variable
2. function insert_table_from_api and insert_table_from_scrap: insert cache data into database
3. plot_prepare: prepare data and style go generate image

## user guide
1. in commandlind, run > python app.py
2. then you will see a url like 127.0.0.1:5000 type url+\ for example 127.0.0.1:5000/ to start 
3. you will need type city name first， try to type in "Ann Arbor","Seattle" etc (first character in each word should be upper-letter)
4. choose category, type in like "bars"
