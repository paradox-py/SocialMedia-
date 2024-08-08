# Social Media APIs

## Overview

This project is a social media API built with Django and Django REST Framework. It provides functionality for user management, friend requests, and authentication. The API supports user registration, login, friend request handling, and user search.

## Project Structure

The project includes several key components:

- **Django App**: Contains models, serializers, views, and other Django-related functionality.
- **Custom Authentication Backend**: Allows users to log in with both email and username.
- **Custom Managers**: Manage custom query operations for user models.

## Key Components

### Custom Authentication Backend

- **CustomBackend**: This authentication backend allows users to log in using either their email or username. It is configured to handle authentication requests based on the provided credentials.

### Custom Managers

- **UserManager**: Manages user creation and handling, including custom user creation methods.

### API Views and Functionality

- **User Registration**: Handles new user registrations. Users can sign up with a username, email, and password.
- **User Login**: Authenticates users via email or username and provides a token for subsequent requests.
- **Friend Request Handling**: Allows users to send, accept, and reject friend requests. Ensures that users cannot send requests to themselves or duplicate requests within a short timeframe.
- **Friend List**: Lists users who have accepted friend requests.
- **Pending Friend Requests**: Lists pending friend requests that the logged-in user has received.
- **User Search**: Enables searching for users by email or username.

## API Endpoints

### User Registration

- **POST /users/signup/**: Registers a new user. Requires `username`, `email`, and `password`.

### User Login

- **POST /users/login/**: Authenticates a user and returns a token. Requires `email` or `username` and `password`.

### Friend Requests

- **POST /users/friend-requests/send/**: Sends a friend request. Requires `receiver_email`. The logged-in user is the sender.
- **PUT /users/friend-requests/update/**: Accepts or rejects a friend request. Requires `id` (of the friend request) and `status` (`accepted` or `rejected`).

### Friend List

- **GET /users/friends-list/**: Lists users who have accepted friend requests with the logged-in user.

### Pending Friend Requests

- **GET /users/pending-requests/**: Lists pending friend requests received by the logged-in user.

### User Search

- **GET /users/search/**: Searches users by email or username. Requires `q` query parameter with the search keyword.

## Setup

1. **Clone the Repository**

    ```bash
    git clone <repository-url>
    cd <project-directory>
    ```

2. **Create a Virtual Environment**

    ```bash
    python -m venv venv
    ```

3. **Activate the Virtual Environment**

    ```bash
    # On Windows
    venv\Scripts\activate

    # On macOS/Linux
    source venv/bin/activate
    ```

4. **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

5. **Apply Migrations**

    ```bash
    python manage.py migrate
    ```

6. **Run the Development Server**

    ```bash
    python manage.py runserver
    ```

## Configuration

- **Settings**: The project uses Django settings for configuration. Ensure you have set up your database and other settings as needed in `settings.py`.

- **Custom Authentication Backend**: Ensure `CustomBackend` is added to the `AUTHENTICATION_BACKENDS` list in `settings.py`.

## Notes

- Ensure you follow the API request formats and provide the necessary data for each endpoint.
- The project includes custom validation to prevent duplicate or invalid friend requests.
- Rate limiting for friend requests is implemented to restrict sending more than 3 requests per minute.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Django](https://www.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
