# Social Site Clone Backend

Welcome to the backend of the Social Site Clone app. This Django-based repository offers a dynamic range of features, making it a robust solution for modern web applications.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Setup](#setup)
  - [Environment Variables](#environment-variables)
  - [Installation](#installation)
- [Deployment](#deployment)
- [CORS Configuration](#cors-configuration)
- [User Registration System](#user-registration-system-for-social-site-clone)

## Features

- **Django Rest Framework**: Simplifies building Web APIs.
- **JWT Authentication**: Uses `rest_framework_simplejwt` for secure user authentication.
- **Real-time updates**: Broadcasts likes and comments in real-time using `RedisChannelLayer`.
- **Background Tasks**: Manages asynchronous tasks like HLS video conversion with `background_task`.
- **WhiteNoise**: Efficiently serves static files.
- **Daphne & ASGI**: Provides enhanced performance and concurrency.

## Tech Stack

- **Web Server**: Django and Daphne.
- **Database**: PostgreSQL (with SQLite3 for testing).
- **Real-time Operations**: Redis.
- **Static Files Management**: WhiteNoise.

## Setup

### Environment Variables

Ensure you have these environment variables set (preferably in a `.env` file):

- `SECRET_KEY`: Your Django secret key.
- For PostgreSQL: `DB_PASSWORD`, `DB_HOST`, `DB_PORT`.

### Installation

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd social-site-clone-backend
   ```

1. **Install the required packages**:

   ```bash
   pip install -r requirements.txt
   ```

1. **Set up the database (Ensure PostgreSQL is running if you're using it)**:

   ```bash
   python manage.py migrate
   ```

1. **Start the Daphne server**:
   ```bash
   daphne core.asgi:application
   ```

After following these steps, the Social Site Clone backend should be operational on your local setup. You can access it via the address and port specified by Daphne.

### Deployment

### Warning
The project is currently configured to accept connections from all hosts.

**ALLOWED_HOSTS:** 
This setting is potentially insecure and should be adjusted before moving to a production environment.

### CORS Configuration
CORS (Cross-Origin Resource Sharing) has been pre-configured for local testing scenarios and for a frontend hosted on Netlify. You may need to modify the CORS settings based on your specific production requirements.

### Recommendations:
1. Limit `ALLOWED_HOSTS` to only the domains and subdomains that should serve the application.
2. Adjust CORS settings to whitelist specific origins, ensuring that only trusted sources can interact with your backend.



# User Registration System for Social Site Clone

This document covers the core components of the user registration system for the Social Site Clone.

## Models

### `Profile` Model (`models.py`)

The `Profile` model extends the default Django `User` model, enhancing it with several additional fields:

- **followers**: A many-to-many relationship representing the user's followers, allowing a user to follow other users.
- **username, firstname, lastname**: Basic identity attributes of the user.
- **bio**: A short description or bio of the user.
- **email**: Email associated with the user.
- **profile_picture & cover_image**: Image fields for the user. If not provided, default images are set.
- **created_at**: Timestamp for when the profile was created.

## Features

### Automatic Profile Creation

Whenever a new user signs up, an associated `Profile` instance is automatically created for them. This ensures that every user has a profile ready for additional information and customization.

### Profile Image Upload

Users can upload a custom image that becomes their profile picture. This is handled during the sign-up process, where an image can be passed along with other sign-up details. This feature provides users a way to personalize their profiles from the very start.

## Serializers

### `ProfileSerialzer` (`serializer.py`)

This serializer manages the `Profile` model, converting it into JSON data for easy transmission and vice-versa. Every attribute of the `Profile` model is serialized.

### `UserCreateSerializer` (`serializer.py`)

Handles the creation of a new user:

- Validates that the `email` and `username` are unique.
- Uses Django's built-in utilities for password validation.
- Ensures proper creation of the user instance and setting of its password.

## Signals (`signals.py`)

Django signals are utilized for automation:

1. **create_profile**: Post the creation of a `User` instance, this signal triggers the creation of an associated `Profile` instance.
2. **save_profile**: Whenever a `User` instance is updated, this signal ensures the changes reflect in its linked `Profile` instance, or creates one if none exists.

## Views

### `AvatarPictureUpdateView` (`views.py`)

A dedicated view for updating the user's images:

- Requires user authentication via JWT.
- Accepts new images for `profile_picture` and `cover_image` in base64 format through POST requests.
- Decodes and saves the provided images.
- Returns a success message and the updated user data upon successful execution.

# Django Chunked Content Upload System

This Django project allows users to upload media content in chunks, offering a more efficient and reliable system for large file uploads.

## Key Features:

1. **Chunked Uploading**: Divide large files into manageable chunks for easier uploads.
2. **File Finalization**: After all chunks are uploaded, the server processes and merges them to re-form the original file.
3. **Stable for Unstable Connections**: If an upload fails due to connection issues, you only need to re-upload the failed chunk, not the entire file.

## How it Works:

1. **Prepare the File**:
    - On the client side, divide your file into smaller chunks.
    - Initiate an upload session using the `PostCreateAPIView`.

2. **Upload the Chunks**:
    - For images, use the `PostImageCreateAPIView`.
    - For videos, use the `PostVideoCreateAPIView`.
    - Send chunks one by one to the respective endpoint.

3. **Finalize the Upload**:
    - Once all chunks are uploaded, signal the server to concatenate the chunks and finalize the media file using `FinalizeUploadView`.

## Routes:

- **Create Post**: `post/create/`
- **Add Image Chunk**: `post/add/media/image/`
- **Add Video Chunk**: `post/add/media/video/`
- **Finalize Video**: `post/add/media/video/finalize/`

# HLS Video Processing in My Django Project

In this Django application, I've integrated state-of-the-art video processing capabilities, harnessing the potential of HTTP Live Streaming (HLS) to deliver an optimized video streaming experience.

## What is HLS?

HLS, short for HTTP Live Streaming, is a streaming protocol pioneered by Apple. It's designed to deliver media content, primarily video, over the internet. The core principle behind HLS is segmenting a video file into smaller chunks and creating a playlist for these chunks, ensuring smooth playback across diverse network conditions.

## The HLS Conversion Process I Implemented:

1. **MediaFile Model**:
   - **Reference**: The foundation is the `MediaFile` model (`MediaFile(models.Model)`), where I store video files uploaded by users.
   - **Chunked Uploads**: Through the `append_chunk` method in the `MediaFile` model, I've enabled chunked uploads. This approach ensures that segments of video data can be sent independently, and then the system assembles them in sequence.

2. **Triggering HLS Encoding**:
   - After a video is completely uploaded, the `start_encoding` method in the `MediaFile` model triggers the HLS encoding process. By running this process in the background, the main application remains seamless and user-friendly.

3. **Utilizing FFmpeg**:
   - **Reference**: My `encode_video_to_hls` function taps into FFmpeg for the video conversion.
   - FFmpeg plays a key role in segmenting the video into varying resolutions (like 360p, 720p). This ensures adaptive playback, catering to different devices and internet speeds.

4. **Structured Storage**:
   - The segmented video chunks, along with their master playlist, are organized in a directory (evident from `os.path.join(settings.MEDIA_ROOT, 'hls', str(mediafile.id))`). This neat arrangement ensures swift access during streaming.

5. **Adaptive Streaming Experience**:
   - During playback, the HLS protocol combined with my backend ensures viewers receive the optimal video quality according to their network. Should there be any fluctuation, HLS adjusts accordingly, promising a smooth viewing experience.

## Key Takeaways:

- **Uninterrupted Streaming**: Thanks to HLS, viewers experience minimal buffering, even in fluctuating network scenarios.
- **Optimal Quality**: My system ensures the best possible video quality for every user.
- **Universal Playback**: Whether on mobile devices, desktops, or smart TVs, my solution promises top-notch video streaming.
