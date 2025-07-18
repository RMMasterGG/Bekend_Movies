# Bekend Movies API Documentation

## Base URL
`/API/V1/{Endpoint}/`

## Authentication Endpoints (`/Auth/`)

### Register New User
- **Endpoint**: `POST /register`
- **Description**: Register a new user on the website. Sends a verification code via email.
- **Request Body**:
  - `username` (string, required)
  - `password` (string, required)
  - `email` (email, required)
- **Response**: 
  - 201 Created: User registered successfully, verification email sent
  - 400 Bad Request: Missing required fields or invalid email format
### Verify Email
- **Endpoint**: `GET /verify-email?session_id=&username=`
- **Description**: Verify user's email using the token sent to their email.
- **Response**: 
  - 200 OK: Email verified successfully
  - 400 Bad Request: Invalid or expired token

### User Login
- **Endpoint**: `POST /login`
- **Description**: Authenticate user and return JWT token in response headers.
- **Request Body**: 
  - `email` (string, required)
  - `password` (string, required)
- **Response**: 
  - 200 OK: Returns JWT in Authorization header
  - 401 Unauthorized: Invalid credentials

### User Logout
- **Endpoint**: `POST /logout`
- **Description**: Invalidate the current JWT token (requires authentication).
- **Headers**:
  - `Authorization: Bearer {token}`
- **Response**: 
  - 200 OK: Successfully logged out

### Refresh Token
- **Endpoint**: `POST /refresh`
- **Description**: Generate a new JWT token (requires valid refresh token).
- **Headers**:
  - `Authorization: Bearer {token}`
- **Response**: 
  - 200 OK: Returns new JWT in Authorization header
  - 401 Unauthorized: Invalid or expired token

## Genres Endpoints (`/Genres/`)

### Get All Genres
- **Endpoint**: `GET /`
- **Description**: Retrieve all genres from the database.
- **Response**: 
  - 200 OK: Returns array of genre objects
  - Example: `[{"id": 1, "name": "Action"}, {"id": 2, "name": "Comedy"}]`

### Create New Genre
- **Endpoint**: `POST /` (Admin only)
- **Description**: Add a new genre to the database.
- **Request Body**: 
  - `name` (string, required) - Genre name
- **Response**: 
  - 201 Created: Returns created genre object
  - 400 Bad Request: Missing required fields
  - 401 Unauthorized: Admin privileges required

### Get Genre by ID
- **Endpoint**: `GET /{genre_id}`
- **Description**: Retrieve a specific genre by its ID.
- **Response**: 
  - 200 OK: Returns genre object
  - 404 Not Found: Genre not found

### Delete Genre
- **Endpoint**: `DELETE /{genre_id}` (Admin only)
- **Description**: Remove a genre from the database.
- **Response**: 
  - 204 No Content: Successfully deleted
  - 404 Not Found: Genre not found
  - 401 Unauthorized: Admin privileges required

## Movies Endpoints (`/Movies/`)

### Get All Movies
- **Endpoint**: `GET /`
- **Description**: Retrieve all movies with optional filtering and pagination.
- **Query Parameters**:
  - `page` (number, optional) - Page number
  - `limit` (number, optional) - Items per page
  - `genre` (string, optional) - Filter by genre
  - `year` (number, optional) - Filter by release year
- **Response**: 
  - 200 OK: Returns paginated array of movie objects

### Get Movie by ID
- **Endpoint**: `GET /{movie_id}`
- **Description**: Retrieve detailed information about a specific movie.
- **Response**: 
  - 200 OK: Returns complete movie object with details
  - 404 Not Found: Movie not found

### Create New Movie
- **Endpoint**: `POST /` (Admin only)
- **Description**: Add a new movie to the database.
- **Request Body**: 
  - `title` (string, required)
  - `release_year` (number, required)
  - `description` (string, required)
  - `duration` (number, required) - in minutes
  - `poster_url` (string, optional)
- **Response**: 
  - 201 Created: Returns created movie object
  - 400 Bad Request: Missing required fields

### Update Movie
- **Endpoint**: `PUT /{movie_id}` (Admin only)
- **Description**: Modify movie information.
- **Request Body**: Same as create, all fields optional
- **Response**: 
  - 200 OK: Returns updated movie object
  - 404 Not Found: Movie not found

### Delete Movie
- **Endpoint**: `DELETE /{movie_id}` (Admin only)
- **Description**: Remove a movie from the database.
- **Response**: 
  - 204 No Content: Successfully deleted
  - 404 Not Found: Movie not found

### Manage Movie Genres
- **Add Genres**: `POST /{movie_id}/genres` (Admin only)
  - **Body**: `{ "genre_ids": [1, 2, 3] }`
- **Remove Genres**: `DELETE /{movie_id}/genres` (Admin only)
  - **Body**: `{ "genre_ids": [1, 2] }`

### Manage Movie Cast
Similar endpoints exist for:
- `/{movie_id}/actors` - Add/remove actors
- `/{movie_id}/directors` - Add/remove directors

### Get Movie Reviews
- **Endpoint**: `GET /{movie_id}/reviews`
- **Description**: Retrieve all reviews for a specific movie.
- **Response**: 
  - 200 OK: Returns array of review objects
  - 404 Not Found: Movie not found

## People Endpoints (`/People/`)

### Get All People
- **Endpoint**: `GET /`
- **Description**: Retrieve all people in the database with pagination.
- **Query Parameters**:
  - `page` (number, optional)
  - `limit` (number, optional)
  - `role` (string, optional) - Filter by role (actor, director, etc.)

### Get Person by ID
- **Endpoint**: `GET /{person_id}`
- **Description**: Retrieve detailed information about a specific person.

### Create/Update/Delete People
Similar to movie endpoints (Admin only):
- `POST /` - Create new person
- `PUT /{person_id}` - Update person
- `DELETE /{person_id}` - Delete person

### Get Person's Filmography
- **Endpoint**: `GET /{person_id}/movies`
- **Description**: Retrieve all movies associated with a person.

## Reviews Endpoints (`/Reviews/`)

### Get Review by ID
- **Endpoint**: `GET /{review_id}`
- **Description**: Retrieve a specific review.

### Create Review
- **Endpoint**: `POST /{movie_id}` (Authenticated)
- **Description**: Submit a review for a movie.
- **Request Body**:
  - `rating` (number, required) - 1-5
  - `text` (string, required)

### Update Review
- **Endpoint**: `PUT /{review_id}` (Review author or Admin)
- **Description**: Modify an existing review.

### Delete Review
- **Endpoint**: `DELETE /{review_id}` (Review author or Admin)
- **Description**: Remove a review.

## Error Responses
All endpoints may return:
- 400 Bad Request: Invalid request data
- 401 Unauthorized: Authentication required
- 403 Forbidden: Insufficient permissions
- 404 Not Found: Resource not found
- 500 Internal Server Error: Server error

## Rate Limiting
API is rate limited to 100 requests per minute per IP address.
