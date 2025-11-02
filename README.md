 📝 Expressly — Full Stack CRUD Web App (React + Flask + MongoDB)

### ✨ Overview
**Expressly** is a full-stack web application built using React (Vite) on the frontend and Flask (Python) on the backend.  
It demonstrates a complete CRUD workflow — Create, Read, Update, and Delete — along with optional features like Likes, Hashtags, Media URLs, and Location.  

Users can:
- Create new posts with text, image links, hashtags, and locations.
- View all posts dynamically.
- Update or delete only their posts.
- Like posts and see updated counts instantly.

⚙️ Tech Stack

| Layer | Technology |
|-------|-------------|
| **Frontend** | React (Vite) + Tailwind CSS |
| **Backend** | Flask (Python) |
| **Database** | MongoDB (via Flask’s PyMongo) |
| **API Client** | Axios |
| **Authentication** | Simple author-based login using username and author ID |

💡 Features

✅ **Create Posts** – Add a new post with description, media URL, location, and hashtags  
✅ **Read Posts** – Fetch all posts dynamically from MongoDB  
✅ **Update Posts** – Edit post content (only for logged-in users who created it)  
✅ **Delete Posts** – Restrict deletion to the post creator  
✅ **Like Posts** – Users can like any post  
✅ **Hashtags** – Include social-style hashtags
✅ **Frontend-Backend Integration** – Fully connected through REST APIs  
✅ **Simple Login System** – Only authenticated users can modify their own posts  
