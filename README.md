# 🐍 GenAI Agents Infrastructure

This repository provides the complete infrastructure for running GenAI agents, including:

* Backend
* Router
* Master Agents
* PostgreSQL Database
* Frontend

## 📦 Prerequisites

Make sure you have the following installed:

* [Docker](https://www.docker.com/)
* [Docker Compose](https://docs.docker.com/compose/)
* [`make`](https://www.gnu.org/software/make/) (optional)

  * macOS: `brew install make`
  * Linux: `sudo apt-get install make`

## 🚀 Local Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/genai-works-org/genai_monorepo.git
   cd genai_monorepo/
   ```

2. Create a `.env` file by copying the example:

   ```bash
   cp .env-example .env
   ```

   * A `.env` file **should be present** for configuration.
   * All variables in `.env-example` are commented.
     You can customize any environment setting by **uncommenting** the relevant line and providing a new value.

3. Start the infrastructure:

   ```bash
   make up
   # or alternatively
   docker compose up
   ```

4. After startup:

   * Swagger API Docs: [http://localhost:8000/docs#/](http://localhost:8000/docs#/)
   * Frontend UI: [http://localhost:8001/](http://localhost:8001/)

## 🌐 Ngrok Setup (Optional)

Ngrok can be used to expose the local WebSocket endpoint.

1. Install Ngrok:

   * macOS (Homebrew): `brew install ngrok/ngrok/ngrok`
   * Linux: `sudo snap install ngrok`

2. Authenticate Ngrok:

   * Sign up or log in at [ngrok dashboard](https://dashboard.ngrok.com).
   * Go to the **"Your Authtoken"** section and copy the token.
   * Run the command:

     ```bash
     ngrok config add-authtoken <YOUR_AUTH_TOKEN>
     ```

3. Start a tunnel to local port 8080:

   ```bash
   ngrok http 8080
   ```

4. Copy the generated WebSocket URL and update the `ws_url` field in:

   ```
   genai_session.session.GenAISession
   ```

---

## 📎 Repository Link

👉 [GitHub Repository](https://github.com/genai-works-org/genai_monorepo)

---

## 💎 Environment Variables

| Variable                    | Description                                                          | Example / Default                                                             |
|-----------------------------|----------------------------------------------------------------------|-------------------------------------------------------------------------------|
| `FRONTEND_PORT`             | Port to start a frontend    | `3000` - default. Can be changed by run in terminal ` source FRONTEND_PORT=<your_port>`  |
| `ROUTER_WS_URL`             | WebSocket URL for the `router` container                             | `ws://router:8080/ws` - host is either `localhost` or `router` container name |
| `SECRET_KEY`                | Secret key for cryptographic operations - JWT/ LLM config encryption | `$(openssl rand -hex 32)`                                                     |
| `POSTGRES_HOST`             | PostgreSQL Host                                                      | `postgres`                                                                    |
| `POSTGRES_USER`             | PostgreSQL Username                                                  | `mycustompostgresuser`                                                        |
| `POSTGRES_PASSWORD`         | PostgreSQL Password                                                  | `mycustompostgrespassword`                                                    |
| `POSTGRES_DB`               | PostgreSQL Database Name                                             | `genai_db`                                                                    |
| `POSTGRES_PORT`             | PostgreSQL Port                                                      | `5432`                                                                        |
| `DEBUG`                     | Enable/disable debug mode - Server/ ORM logging                      | `True` / `False`                                                              |
| `MASTER_AGENT_API_KEY`      | API key for the Master Agent - internal identifier                   | `e1adc3d8-fca1-40b2-b90a-7b48290f2d6a::master_server_ml`                      |
| `MASTER_BE_API_KEY`         | API key for the Master Backend - internal identifier                 | `7a3fd399-3e48-46a0-ab7c-0eaf38020283::master_server_be`                      |
| `BACKEND_CORS_ORIGINS`      | Allowed CORS origins for the `backend`                               | `["*"]`, `["http://localhost"]`                                               |
| `DEFAULT_FILES_FOLDER_NAME` | Default folder for file storage - Docker file volume path            | `/files`                                                                      |
| `CLI_BACKEND_ORIGIN_URL`    | `backend` URL for CLI access                                         | `http://localhost:8000`                                                       |
