# Azure Functions

![Project Image](project-image-url)


---

### Table of Contents
You're sections headers will be used to reference location of destination.

- [Description](#description)
- [What is an Azure Function](#what-is-an-azure-function)
- [Python Script: Reddit](#python-script--reddit)
- [Sentiment Analysis](#sentiment-analysis)
- [SQL Database](#sql-database)
- [Timer Trigger](#timer-trigger)
- [Author Info](#author-info)

---

## Description

In this repository, you will find out about my experience with Azure Functions and how we leveraged it to scrape Reddit posts using the Reddit API in Python. In addition, I set a timer to execute the function at a set interval, and as a result stream real time data from Reddit. 

The content from the Reddit postss were parsed through Azure's Text Analytics tool which conducts sentiment analysis on text. This was used to gather the sentiment from each Reddit post.

Finally the data was stored in several tables in an SQL database and analysed using Power BI.


### Technologies

- Python

    - **praw** package

        Used to connect to the Reddit API and retreive posts

    - **azure.functions**  package

        Used to create azure functions in VSC

    - **smtplib** package

        Used to send emails to verify that the script has executed

    - **azure.ai.textanalytics** package

        Used to coonect to Azure's Text Analytics tool in Python

    - **pyodbc** package

        Used to store the data in an SQL database in Azure

    - **pandas** package

        Used to manipulate and handle the data

- Azure

    Used to host the Azure function and SQL database


[Back To The Top](#azure-functions)

---

## What is an Azure Function

An Azure Function is a serverless computing service that allows developers to run small pieces of code or functions in the cloud without having to manage any infrastructure. These functions can be triggered in response to events such as changes in data, timer-based schedules, or messages from other services. Azure Functions are highly scalable and cost-effective as developers only pay for the amount of time their code runs. Additionally, Azure Functions supports a variety of programming languages and integrates with other Azure services, allowing developers to build complex workflows and applications quickly and easily.

[Back To The Top](#azure-functions)

---

## Python Script: Reddit

This Python script scrapes Reddit posts based on certain parameters. The parameters include:

- **subreedit** - a user defined subreddit

- **title** - user can decide if they want to search for any speciifc words or phrases in the reddit post title

- **flair** - user can decide which flair they would like to filter

- **limit** - number of posts to scrape from Reddit

The content of these posts are then sent to Azure's Text Analytics Tool to conduct sentiment analysis and then all metadata of the posts and their sentiment scores are stored in an SQL database.

To find the python script used go to **reddit_to_sql_trigger / __init__.py** in this repository.

[Back To The Top](#azure-functions)

---

## Azure Text Analytics Tool

Azure's Text Analytics is a powerful natural language processing tool that provides sentiment analysis, key phrase extraction, and language detection. It uses advanced machine learning algorithms to identify and extract valuable insights from textual data in real-time. Sentiment analysis is a particularly useful feature of Text Analytics, as it can be used to gauge the emotional tone of social media posts, customer reviews, and other types of textual content. By analyzing sentiment, businesses can gain a deeper understanding of customer perceptions and make more informed decisions based on that knowledge. Overall, Azure's Text Analytics is an excellent tool for anyone looking to extract valuable insights from textual data quickly and easily.

[Back To The Top](#azure-functions)

---

## SQL Database

Azure's Text Analytics is a powerful natural language processing tool that provides sentiment analysis, key phrase extraction, and language detection. It uses advanced machine learning algorithms to identify and extract valuable insights from textual data in real-time. Sentiment analysis is a particularly useful feature of Text Analytics, as it can be used to gauge the emotional tone of social media posts, customer reviews, and other types of textual content. By analyzing sentiment, businesses can gain a deeper understanding of customer perceptions and make more informed decisions based on that knowledge. Overall, Azure's Text Analytics is an excellent tool for anyone looking to extract valuable insights from textual data quickly and easily.

Below you can see the structure of the tables and how they were linked:

"INSERT ER DIAGRAM HERE"

[Back To The Top](#azure-functions)

---

## Timer Trigger

As mentioned previously I used a timer trigger as part of this Azure function to schedule the execution of the code at a specific interval. This can be easily changed and is denoted as a CRON expression. 
For example:

`0 */15 * * * *` - denotes an interval of 15 minutes.

This allowed a continously updating flow of Reddit data to be analysed and passed into the SQL database.

Below you can see the flow of execution of this Azure function:

"INSERT TIMER DIAGRAM HERE"

[Back To The Top](#azure-functions)

---

## Author Info

LinkedIn - [George Lopez](https://www.linkedin.com/in/george-benjamin-lopez/)

[Back To The Top](#azure-functions)
