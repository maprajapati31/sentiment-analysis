Big Data Analytics Project: Social Media Backend

This folder contains the complete backend server for our project.

The goal of this backend is to provide a simple, fast, and stable CRUD (Create, Read, Update, Delete) API for our application. It is built with Python (Flask) and connects to a MongoDB database.

Section 1: MongoDB Atlas Setup (Do This First!)

Before you can run the code, you need a database. We use a free cloud database from MongoDB Atlas.

Create an Account: Go to cloud.mongodb.com and sign up for a free account.

Build a Free Cluster:

Follow the on-screen steps to create a new project.

Click "Build a Database" and choose the "Shared" (M0 Sandbox) plan. This is free forever.

You can leave the provider (AWS) and region as the default.

Name your cluster (e.g., Cluster0). Click "Create".

Create a Database User:

In the left-hand menu (under SECURITY), click "Database Access".

Click "Add New Database User".

Username: kdp

Password: Nikitadh1 (or whatever password you want to use).

Permissions: Select "Read and write to any database".

Click "Add User".

Allow Network Access:

In the left-hand menu, click "Network Access".

Click "Add IP Address".

Click "ALLOW ACCESS FROM ANYWHERE". This will add the IP 0.0.0.0/0.

Click "Confirm".

Get Your Connection String:

Go back to "Database" and click the "Connect" button on your new cluster.

Select "Connect your application".

Copy the connection string. It will look like this:
mongodb+srv://kdp:<password>@cluster0.xgqltqs.mongodb.net/?appName=Cluster0

This is the uri you must paste into the app.py file.

Section 2: Local Project Setup (For Teammates)

To run this server on your own computer, follow these 4 steps:

Create a Virtual Environment:

# Use 'py' if 'python' doesn't work
py -m venv venv


Activate the Environment:

# On Windows:
.\venv\Scripts\activate


Install All Required Libraries:
(This file requirements.txt is included)

pip install -r requirements.txt


Run the Server (For Yourself):

flask run


The server will now be running at http://127.0.0.1:5000 (which only you can access).

Section 3: How to Share The Server (For Frontend Team)

The frontend team needs to access your server from their computers.

Find Your Local IP Address:

Open a new Command Prompt (not the VS Code one).

Type ipconfig and press Enter.

Look for your "IPv4 Address". It will look something like 192.168.1.10.

Run the Server Publicly:

In your VS Code terminal (with venv active), run this command:

flask run --host=0.0.0.0


This makes your server visible on your local Wi-Fi network.

Tell Your Teammates:

Your server's new address is http://<YOUR_IP_ADDRESS>:5000

(Example: http://192.168.1.10:5000)

The frontend team will use this address for all their API calls.

Section 4: How to Test the API (Using Postman)

Postman is a tool to test your API before the frontend is built.

Test 1: Create a New User (Sign Up)

Method: POST

URL: http://127.0.0.1:5000/signup

Body Tab: Select raw, then select JSON from the dropdown.

Body JSON:

{
  "username": "johndoe",
  "display_name": "John Doe",
  "email": "john.doe@example.com",
  "password": "mypassword1D",
  "age": 30,
  "gender": "male"
}


Click Send. You should get a 201 Created message.

Test 2: Log In

Method: POST

URL: http://127.0.0.1:5000/login

Body Tab: raw -> JSON

Body JSON:

{
  "email": "john.doe@example.com",
  "password": "mypassword1D"
}


Click Send. You will get a 200 OK response. Copy the user_id from this response.
{ "message": "Login successful", "user_id": "6722...c8d9", ... }

Test 3: Create a Post

Method: POST

URL: http://127.0.0.1:5000/posts

Body Tab: raw -> JSON

Body JSON: (Paste the user_id you copied from Test 2)

{
  "author_id": "PASTE_YOUR_USER_ID_HERE",
  "author_username": "johndoe",
  "content": "This is my first post! Testing the API.",
  "hashtags": ["testing", "bigdata"]
}


Click Send. You will get a 201 Created response. Copy the post_id from this response.
{ "message": "Post created successfully", "post_id": "6722...d8e9" }

Test 4: Like the Post

Method: POST

URL: http://127.0.0.1:5000/posts/<post_id>/like (Paste your post_id into the URL)

Body Tab: raw -> JSON

Body JSON: (Paste the user_id from Test 2)

{
  "user_id": "PASTE_YOUR_USER_ID_HERE"
}


Click Send. You will get a 200 OK message ("Post liked").

Section 5: Our Database Schema (The "Structured Data")

This is the most important part of our project. We designed a "structured" NoSQL schema to be fast for the app and powerful for analytics. We have 3 collections:

1. users Collection

Stores all user information. role is used for "admin" vs "user" permissions.

{
  "_id": "ObjectID(...)",
  "username": "john_doe",
  "display_name": "John Doe",
  "email": "john@example.com",
  "password": "a_hashed_password_string",
  "join_date": "ISODate(...)",
  "role": "user",
  "age": 28,
  "gender": "male"
}


2. posts Collection

Stores all posts. author_id links to the users collection. liked_by is an array for complex queries.

{
  "_id": "ObjectID(...)",
  "author_id": "ObjectID(from_users_collection)",
  "author_username": "john_doe",
  "content": "This is my first post! #bigdata",
  "timestamp": "ISODate(...)",
  "category": "Unclassified",
  "like_count": 0,
  "liked_by": [ "ObjectID(user1)", "ObjectID(user2)" ],
  "comment_count": 0,
  "hashtags": ["bigdata", "mongodb"],
  "media_url": "https://.../image.png",
  "location": {
    "type": "Point",
    "coordinates": [-74.0060, 40.7128]
  }
}


3. comments Collection

Stores all comments. post_id links to the posts collection, and author_id links to users.

{
  "_id": "ObjectID(...)",
  "post_id": "ObjectID(from_posts_collection)",
  "author_id": "ObjectID(from_users_collection)",
  "author_username": "jane_doe",
  "comment_text": "Great post! Good luck.",
  "timestamp": "ISODate(...)"
}


Section 6: The "Big Data" Plan (For Apache Spark)

This is why our schema is designed this way. This is the next step of the project.

Problem: When a user creates a post, we save it instantly with "category": "Unclassified". This is fast for the user but bad for analytics.

Solution (The "Processing" Part):
We will run a separate Apache Spark job (e.g., once every hour) that performs an ETL (Extract, Transform, Load) process:

Extract: The Spark job will connect to MongoDB and read all posts WHERE "category" == "Unclassified".

Transform: Spark will use rules-based logic or Machine Learning (ML) to analyze the content and hashtags of each post to determine its real category (e.g., "Tech", "Sports", "News").

Load: Spark will update the post in MongoDB, changing its category from "Unclassified" to the new, correct category (e.g., "category": "Tech").

This design allows our Flask App to be fast (for users) while our Spark Job is powerful (for analytics).

Section 7: API Endpoints (Quick Reference)

This is the full list of API URLs that the backend provides.

Users

Action

Method

URL

Body (JSON)

Success Response

Sign Up

POST

/signup

{ "username", "display_name", "email", "password", "age", "gender" }

201 Created

Log In

POST

/login

{ "email", "password" }

200 OK (returns user_id)

Posts

Action

Method

URL

Body (JSON)

Success Response

Create Post

POST

/posts

{ "author_id", "author_username", "content", ... }

201 Created (returns post_id)

Get All Posts

GET

/posts

(none)

200 OK (returns list of all posts)

Like/Unlike

POST

/posts/<post_id>/like

{ "user_id" }

200 OK ("Post liked" or "Post unliked")

Delete Post

DELETE

/posts/<post_id>

(none)

200 OK ("Post... deleted")

Comments

Action

Method

URL

Body (JSON)

Success Response

Create Comment

POST

/comments

{ "post_id", "author_id", "author_username", "comment_text" }

201 Created
