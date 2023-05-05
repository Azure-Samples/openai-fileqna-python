# File Q&A with Next.js and Flask

File Q&A is a web app that lets you find answers in your files. You can upload files and ask questions related to their content, and the app will use embeddings and GPT to generate answers from the most relevant files.

## Requirements

To run the app, you need:

- Python 3.7 or higher and pipenv for the Flask server.
- Azure Active Directory authentication.
- Redis with RediSearch (Redis Stack). 
- Node.js and npm for the Next.js client.

## Set-Up and Development

### Environment variables

Set the following environment variables with your own values:

```
AZURE_CLIENT_ID
AZURE_TENANT_ID
AZURE_CLIENT_SECRET
OPENAI_API_BASE
```

### Redis

We'll use [Redis](https://redis.io) as a vector database for this app, including the [RediSearch module](https://github.com/RediSearch/RediSearch).

This app is set up to use Redis Stack on Docker.

Start a version of Redis with RediSearch (Redis Stack) by running the following docker command:

```bash
$ cd server
$ docker compose up -d
```

This also includes the [RedisInsight](https://redis.com/redis-enterprise/redis-insight/) GUI for managing your Redis database which you can view at [http://localhost:8001](http://localhost:8001) once you start the docker container.
Python 3.7 or higher and pipenv for the Flask server.


### Server

Fill out the config.yaml file with your Redis information, index name and environment.

```
cd server
pip install -r requirements.txt
```

Run the Flask server:

```
cd server
bash script/start
```

### Client

Navigate to the client directory and install Node dependencies:

```
cd client
npm install
```

Run the Next.js client in a new terminal:

```
cd client
npm run dev
```


Open [http://localhost:3000](http://localhost:3000) with your browser to see the app.

## Limitations

The app may sometimes generate answers that are not in the files, or hallucinate about the existence of files that are not uploaded.
