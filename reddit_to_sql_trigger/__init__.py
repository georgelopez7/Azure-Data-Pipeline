import datetime
import azure.functions as func
import smtplib
from email.mime.text import MIMEText
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import praw
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
import pyodbc
import pandas as pd
import logging
import string

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    # ------------------------------------------------------------------------------
    # Date and Time for email
    now = datetime.datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    # --------------------------------------------------------------------------------
    # Email Confirmation
    def email_send(body):
        sender = "<email-of-sender>"
        recipient = "<email-of-recipient>"

        msg = MIMEText(body)
        msg["Subject"] = "Running script in Python"
        msg["From"] = sender
        msg["To"] = recipient

        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login("<email-of-sender>", "<email-password>")
            smtp.sendmail(sender, [recipient], msg.as_string())
    # --------------------------------------------------------------------------------
    def getposts(subreddit_name, flair_filter=None, title_filter=None, limit=None):
        # create a Reddit instance with PRAW
        reddit = praw.Reddit(
            client_id='client-id',
            client_secret='client-secret',
            user_agent='your_user_agent')

        # get the subreddit object
        subreddit = reddit.subreddit(subreddit_name)

        # build the search query
        query = ''
        if flair_filter:
            query += f'flair:"{flair_filter}"'
        if title_filter:
            query += f' title:"{title_filter}"'

        # get the top posts with the specified flair and title, with a limit on the number of posts
        top_posts = subreddit.search(query, sort='new', limit=limit, syntax='lucene')

        # create a list to store the filtered posts
        filtered_posts = []

        # iterate over the filtered posts and add their title, author, url, and score to the list
        for post in top_posts:
            if post.selftext != "":

                # create a dictionary of post information
                post_dict = {'id': post.id,
                            'title': post.title,
                            'author': str(post.author),
                            'content': post.selftext,
                            'post_timestamp': post.created_utc,
                            'url': post.url,
                            'score': post.score}
                print('This is the id!',post_dict['id'],type(post_dict['id']))
                print('This is the title!',post_dict['title'],type(post_dict['title']))
                print('This is the author!',post_dict['author'],type(post_dict['author']))
                print('This is the content!',post_dict['content'],type(post_dict['content']))
                print('This is the timestamp!',post_dict['post_timestamp'],type(post_dict['post_timestamp']))
                print('This is the url!',post_dict['url'],type(post_dict['url']))
                print('This is the score!',post_dict['score'],type(post_dict['score']))



                # append the post dictionary to the filtered posts list
                filtered_posts.append(post_dict)
        filtered_posts_df = pd.DataFrame(data = filtered_posts)
        # return the list of dictionaries
        return filtered_posts_df, filtered_posts

    def sentiment_analysis(list_of_dicts):
        credential = AzureKeyCredential('<azure-credentials>')
        text_analytics_client = TextAnalyticsClient(endpoint = 'https://reddit-sentiment-analysis.cognitiveservices.azure.com/', credential = credential)

        # Iterate through documents as azure limits to 10 documents per request
        start = 0
        end = len(list_of_dicts)
        step = 10

        doc_id, doc_positive, doc_neutral, doc_negative = [],[],[],[]

        # Extract the content from each post
        content = []
        for doc in list_of_dicts:
            text = doc['title'] + ' ' + doc['content']

            if len(text)>5120:
                content.append(text[0:5119])
            else:
                content.append(text)
            doc_id.append(doc['id'])

        # Calculate the sentiment for the posts containing text
        for i in range(start, end, step):
            x = i
            response = text_analytics_client.analyze_sentiment(content[x:x+step])
        
            for doc in response:

                doc_positive.append(doc.confidence_scores.positive)
                doc_neutral.append(doc.confidence_scores.neutral)
                doc_negative.append(doc.confidence_scores.negative)

        # Store results in dataframe
        doc_sentiment = pd.DataFrame({
            'id': doc_id,
            'positive': doc_positive,
            'neutral': doc_neutral,
            'negative': doc_negative
        })
        return doc_sentiment

    def to_sql_server(table_name, dataframe, table_type):
        
        # Upload to Azure SQL Database

        server = '<azure-server>'
        database = '<azure-database-name>'
        username = '<server-username>'
        password = '<sever-password>'   
        driver= '{ODBC Driver 17 for SQL Server}'


        cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
        cursor = cnxn.cursor()
        # Create new table if it doesn't exist
        if table_type == 0:
            cursor.execute(f"""IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = '{table_name}')
            BEGIN
            CREATE TABLE {table_name} (
                doc_id varchar(15),
                positive FLOAT,
                neutral FLOAT,
                negative FLOAT,
                PRIMARY KEY(doc_id)
            )
            END """)

            # Insert Dataframe into SQL Server:
            for index, row in dataframe.iterrows():
                cursor.execute(f"""IF NOT EXISTS (SELECT * FROM dbo.{table_name} WHERE doc_id = ?)
                BEGIN
                INSERT INTO dbo.{table_name} (doc_id,positive,neutral,negative) values(?,?,?,?)
                END""", row.id, row.id, row.positive, row.neutral, row.negative)

            # email_send(f'APPENDED the blob at {dt_string}')
            cnxn.commit()
            cursor.close()

        elif table_type == 1:
            print('Lets create the table!')
            print('This is the table name',table_name)
            cursor.execute(f'''IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = '{table_name}')
                    BEGIN
                    CREATE TABLE {table_name} (
                        doc_id varchar(15),
                        title varchar(MAX),
                        author varchar(100),
                        content varchar(MAX),
                        post_timestamp FLOAT,
                        url varchar(1000),
                        score int,
                        PRIMARY KEY(doc_id)
                    )
                    END''')
            print('Table created!')
            for index, row in dataframe.iterrows():
                cursor.execute(f"""IF NOT EXISTS (SELECT * FROM dbo.{table_name} WHERE doc_id = ?)
                BEGIN
                INSERT INTO dbo.{table_name} (doc_id, title, author, content, post_timestamp, url, score) values(?,?,?,?,?,?,?)
                END""", row.id, row.id, row.title, row.author, row.content, row.post_timestamp, row.url, row.score)
            
            # email_send(f'APPENDED the blob at {dt_string}')
            cnxn.commit()
            cursor.close()
        else:
            print('It broke when inserting')

    book_list = [
        "chatgpt plus",
        "chatgpt",
        "chatgpt free",
        "at capacity",
        "openai",
        "gpt3",
        "gpt4"
    ]

    for book in book_list:
        posts_df, posts_json = getposts('chatgpt',title_filter=book, limit=300)
        sentiment_df = sentiment_analysis(posts_json)
        print('this is the book name',book[-1])
        print('this is the df',posts_df)
        to_sql_server(f"{book.replace(' ','_').lower().translate(str.maketrans('', '', string.punctuation))}_metadata", posts_df, 1)
        to_sql_server(f"{book.replace(' ','_').lower().translate(str.maketrans('', '', string.punctuation))}_sentiment", sentiment_df, 0)


    email_send(f'ChatGPT tables have been updated at: {dt_string}')
    logging.info('Python timer trigger function ran at %s', utc_timestamp)
