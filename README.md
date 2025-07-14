![GenAIOS Compatible](https://img.shields.io/badge/GenAIOS-Compatible-brightgreen)
![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)
![Hackathon](https://img.shields.io/badge/Lead_with_AI_Agents_2025-Project-orange)
# MatchMyStar: Indian Astrology-Based Matchmaking with GenAIOS

## Overview
MatchMyStar is an AI-powered matchmaking system that leverages Indian astrology and modern agent orchestration. Built on the GenAIOS platform, it demonstrates multi-agent collaboration, real-time orchestration, and integration with external data sources (Supabase) for the Lead with AI Agents Hackathon 2025.
Powered by GenAIOS + Prokerala API + Supabase + OpenStreetMap

## Powered by GenAIOS
This project is built on top of [GenAIOS](https://github.com/genai-works-org/genai-agentos), the open-source AI Agent Operating System. GenAIOS provides the agent protocol, orchestration engine, agent registration, and the chat/flow UI that powers the entire agent workflow. All agent communication, orchestration, and flow management in MatchMyStar is handled by GenAIOS, making it easy to build, test, and scale multi-agent systems.

## Problem Statement
Indian matchmaking systems rely heavily on astrological compatibility (Kundli/Guna Milan). However, current digital solutions either lack personalization or require manual horoscope upload and comparison.
MatchMyStar aims to change that by letting users input simple profile data (DOB, TOB, Place, Gender, etc.) and automatically fetches & ranks potential matches from a profile database using a real astrology engine.

## Features
- **Multi-agent orchestration** using GenAIOS flows
- **Astrology-based matchmaking**: Kundli compatibility via Prokerala API, profile filtering, and result formatting
- **Supabase integration** for real user profile storage and querying
- **OpenStreetMap** for accurate birth coordinates
- **Modern frontend** for user input and results display (React + Tailwind frontend with WebSocket integration)
- **Extensible**: Easily add more agents (e.g., OCR, PDF parsing) in the future

## Architecture
- **Frontend**: React/TypeScript (Vite, Tailwind), connects to GenAIOS backend via WebSocket
- **Backend**: GenAIOS AgentOS
- **Agents**:
  - `astro_data_agent`: Enriches user profile with geocoded coordinates
  - `geocode_agent`: Converts place names to lat/lon
  - `filter_profile_agent`: Fetches matching profiles from Supabase (opposite gender)
  - `kundli_match_agent`: Calculates compatibility for each candidate
  - `results_formatter_agent`: Formats the final matchmaking results
- **Database**: Supabase (Postgres)
- **Prokerala API** performs kundli matching
- **OpenStreetMap** converts birth place to lat/lon

## Agent Orchestration Flow
1. **User submits profile** (name, DOB, TOB, place, gender, occupation)
2. **astro_data_agent** enriches profile with coordinates (calls `geocode_agent`)
3. **filter_profile_agent** fetches opposite-gender profiles from Supabase
4. **kundli_match_agent** runs compatibility for each candidate
5. **results_formatter_agent** formats and returns the results

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/matchmystar-genaios.git
cd matchmystar-genaios
```

### 2. Install Dependencies
- **Backend/Agents**: Use `uv` or `pip` as per GenAIOS docs
- **Frontend**: `cd genai-agentos/frontend && npm install`

### 3. Setup .env
```bash
cp .env-example .env
```

Add the following to your .env:
```env
SUPABASE_URL=<your_supabase_url>
SUPABASE_KEY=<your_supabase_key>

PROKERALA_CLIENT_ID=your_id
PROKERALA_CLIENT_SECRET=your_secret

GEOCODE_AGENT_JWT=...
KUNDLI_MATCH_AGENT_JWT=...
```

### 4. Set Up Supabase
- Create a Supabase project at [https://app.supabase.com/](https://app.supabase.com/)
- Create a `profiles` table with columns: `id`, `name`, `dob`, `tob`, `place`, `gender`, `occupation`, `lat`, `lon`
- Insert sample profiles via the Table Editor or SQL
- Get your `SUPABASE_URL` and `SUPABASE_KEY` from Project Settings > API
- Set these as environment variables for the agents

### 5. Set Up Prokerala Account
- Register a new app at [https://api.prokerala.com/](https://api.prokerala.com/)
- Get your `PROKERALA_CLIENT_ID` and `PROKERALA_CLIENT_SECRET` from Client Info
- Set these as environment variables for the agents

### 6. Registering Agents (Developer-Only, One-Time Setup)
```bash
cd cli
python cli.py login -u <your-username> -p <your-password>
python cli.py register_agent --name kundli_match_agent --description "Matches kundlis using Prokerala"
```
Once registered, copy the JWT tokens and place them in your .env file:
```bash
KUNDLI_MATCH_AGENT_JWT=eyJhbGciOi...
```

### 7. Run the System
- Start backend, agents, and frontend (see GenAIOS docs or use Docker Compose)
### Prerequisites
- Docker + Docker Compose
- `make` installed (use `brew install make` or `sudo apt install make`)
```bash
make up
# or
docker-compose up -d --build
```
- Access the frontend at [http://localhost:3000/matchmystar](http://localhost:3000/matchmystar)

### 8. Test the Workflow
- Fill out the required fields and click "Find Matches"
- The system will orchestrate agents and return real matches

## Hackathon Context
- Built for the Lead with AI Agents Hackathon 2025
- Demonstrates agent orchestration, real data integration, and GenAI Protocol compliance
- See `/docs` and code comments for more details

## Future Enhancements
- Add OCR/PDF parsing for horoscope extraction
- More advanced compatibility logic
- User authentication and profile management

## Demo Preview
See the app in action: [Watch Demo](https://www.loom.com/share/17930b95747444b8b66152f866eb8905?sid=3da2aeae-8067-497c-8c01-e55a56b2794c)

## Documentation
Check out Notion Docs: [MatchMyStar Documentation](https://www.notion.so/MatchMyStar-GenAIOS-Hackathon-Submission-22f043af801e80f683cbd643542431b5?source=copy_link)

---

**Made with ❤️ for the GenAIOS Hackathon**
