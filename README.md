# MatchMyStar: Indian Astrology-Based Matchmaking with GenAIOS

## Overview
MatchMyStar is an AI-powered matchmaking system that leverages Indian astrology and modern agent orchestration. Built on the GenAIOS platform, it demonstrates multi-agent collaboration, real-time orchestration, and integration with external data sources (Supabase) for the Lead with AI Agents Hackathon 2025.

## Powered by GenAIOS
This project is built on top of [GenAIOS](https://github.com/genai-works-org/genai-agentos), the open-source AI Agent Operating System. GenAIOS provides the agent protocol, orchestration engine, agent registration, and the chat/flow UI that powers the entire agent workflow. All agent communication, orchestration, and flow management in MatchMyStar is handled by GenAIOS, making it easy to build, test, and scale multi-agent systems.

## Features
- **Multi-agent orchestration** using GenAIOS flows
- **Astrology-based matchmaking**: Kundli compatibility, profile filtering, and result formatting
- **Supabase integration** for real user profile storage and querying
- **Modern frontend** for user input and results display
- **Extensible**: Easily add more agents (e.g., OCR, PDF parsing) in the future

## Architecture
- **Frontend**: React/TypeScript (Vite, Tailwind), connects to GenAIOS backend via WebSocket
- **Backend**: GenAIOS AgentOS (Python, FastAPI)
- **Agents**:
  - `astro_data_agent`: Enriches user profile with geocoded coordinates
  - `geocode_agent`: Converts place names to lat/lon
  - `profile_filter_agent`: Fetches matching profiles from Supabase (opposite gender)
  - `kundli_match_agent`: Calculates compatibility for each candidate
  - `results_formatter_agent`: Formats the final matchmaking results
- **Database**: Supabase (Postgres)

## Agent Orchestration Flow
1. **User submits profile** (name, DOB, TOB, place, gender, occupation)
2. **astro_data_agent** enriches profile with coordinates (calls `geocode_agent`)
3. **profile_filter_agent** fetches opposite-gender profiles from Supabase
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

### 3. Set Up Supabase
- Create a Supabase project at [https://app.supabase.com/](https://app.supabase.com/)
- Create a `profiles` table with columns: `id`, `name`, `dob`, `tob`, `place`, `gender`, `occupation`, `lat`, `lon`
- Insert sample profiles via the Table Editor or SQL
- Get your `SUPABASE_URL` and `SUPABASE_KEY` from Project Settings > API
- Set these as environment variables for the agents

### 4. Run the System
- Start backend, agents, and frontend (see GenAIOS docs or use Docker Compose)
- Access the frontend at [http://localhost:3000/matchmystar](http://localhost:3000/matchmystar)

### 5. Test the Workflow
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

---

**Made with ❤️ for the GenAIOS Hackathon**