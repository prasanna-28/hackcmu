# Missedmylecture

Missedmylecture is a web application designed to help students catch up on missed lectures. By inputting lecture notes, the system uses large language models (LLMs) to generate LaTeX content from the notes and provides relevant YouTube videos on topics within the notes.

## Features

- **React Frontend**: A user-friendly interface built with React.
- **Flask Backend**: A robust backend that processes lecture notes and interfaces with large language models.
- **LaTeX Content Generation**: Automatically generate LaTeX-formatted content based on the lecture notes you provide.
- **YouTube Video Recommendations**: Get curated YouTube videos related to the topics extracted from your lecture notes.

## Tech Stack

- **Frontend**: React
- **Backend**: Flask
- **Language Models**: Powered by large language models (LLMs) to process and analyze notes.
- **LaTeX**: Automatic LaTeX generation for high-quality academic documentation.

## How It Works

1. Upload or paste your lecture notes into the web interface.
2. The system processes the notes using large language models to extract key concepts.
3. LaTeX-formatted content is generated for easy academic reference.
4. Receive YouTube video recommendations that provide additional learning resources on key topics.

## Setup

A Python version greater than 3.9 is required.

First, install all python dependencies.
```pip install -r requirements.txt```

Then, run:
```python backend/app.py```

This will start the backend.

For the frontend, make sure to have npm dev tools installed.

Cd into frontend/missedmylecture and run:
```npm run dev```

Note: a working latex compiler is required.
