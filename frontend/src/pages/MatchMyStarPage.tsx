import { useEffect, useState } from 'react';
import { Upload, Heart, Users, Calendar, MapPin, FileText } from 'lucide-react';
import { MainLayout } from '@/components/layout/MainLayout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/useToast';
import { tokenService } from '@/services/apiService';
import { websocketService } from '@/services/websocketService';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import '@/styles/markdown.css';
// import { AgentResponse } from '@/types/websocket';

// Temporary type for AgentResponse
type AgentResponse = {
  type: string;
  response: any;
};

interface MatchProfile {
  name: string;
  age: number;
  location: string;
  occupation: string;
  compatibility_score: number;
  summary: string;
  photo?: string;
}

const MatchMyStarPage = () => {
  const [userProfile, setUserProfile] = useState({
    name: '',
    dob: '',
    tob: '',
    place: '',
    gender: '',
    occupation: ''
  });
  const [matches, setMatches] = useState<any[]>([]);
  const [analysis, setAnalysis] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [formError, setFormError] = useState('');
  const [noMatchMessage, setNoMatchMessage] = useState("");
  const { showSuccess, showError } = useToast();

  const isJsonString = (str: string) => {
    try {
      const parsed = JSON.parse(str);
      // Only treat as JSON if it's an object or array
      return typeof parsed === 'object' && parsed !== null;
    } catch {
      return false;
    }
  };

  // Add WebSocket message handler
  useEffect(() => {
    const handleWebSocketMessage = (response: AgentResponse) => {
      if (response.type === 'agent_response') {
        try {
          
          // Try to find the matches array at any depth
          let responseData;
          if (typeof response.response?.response?.response === 'string') {
            const str = response.response.response.response;
            if (isJsonString(str)) {
              responseData = JSON.parse(str);
            } else {
              // Not JSON, treat as plain message
              setMatches([]);
              setAnalysis(null);
              setNoMatchMessage(str || "We couldn't find any compatible matches for you right now. Please check back later as new profiles are added!");
              setIsLoading(false);
              return;
            }
          } else if (response.response?.response?.response) {
            responseData = response.response.response.response;
          } else if (response.response?.response) {
            responseData = response.response.response;
          } else {
            responseData = response.response;
          }

          // Try to find matches at any depth
          let matches = responseData.matches;
          let analysis = responseData.analysis;
          if (!matches && responseData.response && responseData.response.matches) {
            matches = responseData.response.matches;
            analysis = responseData.response.analysis;
          }

          if (matches && Array.isArray(matches) && matches.length > 0) {
            setMatches(matches);
            setAnalysis(analysis || null);
            setNoMatchMessage(""); // Clear any previous no-match message
            
            // Show analysis if available
            if (analysis) {
              const analysis = responseData.analysis;
              if (analysis.overall_assessment) {
                showSuccess(analysis.overall_assessment);
              }
              if (analysis.message) {
                // console.log('MatchMyStar Analysis:', analysis.message);
              }
            } else {
              showSuccess(`Found ${responseData.total_matches} matches!`);
            }
          } else {
            // Fallback for other response formats
            setMatches([]);
            setAnalysis(null);
            setNoMatchMessage("We couldn't find any compatible matches for you right now. Please check back later as new profiles are added!");
          }
        } catch (error) {
          setMatches([{
            name: 'Response',
            age: 0,
            location: 'Unknown',
            occupation: 'Unknown',
            compatibility_score: 0,
            summary: typeof response.response?.response?.response === 'string'
              ? response.response.response.response
              : JSON.stringify(response.response?.response?.response)
          }]);
          setAnalysis(null);
        }
        setIsLoading(false);
      }
    };
    websocketService.addMessageHandler(handleWebSocketMessage);
    return () => websocketService.removeMessageHandler(handleWebSocketMessage);
  }, [showSuccess]);

  // Update handleSubmit to use WebSocket
  const handleSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setFormError('');
    // Validation
    if (!userProfile.name || !userProfile.dob || !userProfile.tob || !userProfile.place || !userProfile.gender) {
      setFormError('All fields are required.');
      return;
    }
    setIsLoading(true);
    setMatches([]); // Clear previous matches
    setAnalysis(null); // Clear previous analysis
    setNoMatchMessage(""); // Clear any previous no-match message
    await websocketService.connect();
    const message = {
      message: `Find matches for ${userProfile.name} based on their profile: ${JSON.stringify(userProfile)}`,
      provider: 'genai',
      llm_name: 'default'
    };
    websocketService.sendMessage(message);
  };

  // Helper function to get compatibility color
  const getCompatibilityColor = (score: number) => {
    if (score >= 70) return 'border-l-green-500';
    if (score >= 50) return 'border-l-yellow-500';
    return 'border-l-red-500';
  };

  // Helper function to get match status message
  const getMatchStatusMessage = (matches: any[], analysis: any) => {
    if (!matches || matches.length === 0) return "";
    
    // Use the filtering message from backend if available
    if (analysis && analysis.filtering_message) {
      return analysis.filtering_message;
    }
    
    // Fallback logic
    const goodMatches = matches.filter(m => m.compatibility_score >= 70);
    const moderateMatches = matches.filter(m => m.compatibility_score >= 50 && m.compatibility_score < 70);
    const lowMatches = matches.filter(m => m.compatibility_score < 50);
    
    if (goodMatches.length > 0) {
      return `Found ${goodMatches.length} good match(es) with strong compatibility!`;
    } else if (moderateMatches.length > 0) {
      return `Found ${moderateMatches.length} moderate match(es) with potential.`;
    } else if (lowMatches.length > 0) {
      return `Limited compatibility found. Showing the best available match.`;
    }
    
    return "";
  };

  // Robust summary string parser for all backend formats, skips intro text
  function parseSummaryString(summary: string): { matches: any[]; analysis: string } {
    // Universal field extractor
    function extractField(block: string, field: string): string {
      const regex = new RegExp(`\\*\\*${field}\\*\\*:?\\s*([^\\n]+)`);
      return block.match(regex)?.[1]?.trim() || '';
    }

    // Start parsing from the first match block
    const firstProfileIdx = summary.search(/\d+\. \*\*([^\*]+)\*\*/);
    const relevant = firstProfileIdx !== -1 ? summary.slice(firstProfileIdx) : summary;

    // Profile regex: number, name, then all lines until next profile or end
    const profileRegex = /(\d+)\.\s+\*\*([^\*]+)\*\*([\s\S]*?)(?=\n\d+\. \*\*|$)/g;
    const matches = [];
    let match;
    while ((match = profileRegex.exec(relevant)) !== null) {
      const name = match[2].trim();
      const block = match[3];
      const age = extractField(block, 'Age');
      const location = extractField(block, 'Location');
      const occupation = extractField(block, 'Occupation');
      let compatibility_score = 0, compatibility_level = '';
      const compMatch = block.match(/\*\*Compatibility Score\*\*:?\s*(\d+)%\s*(?:\(([^)]+)\))?/);
      if (compMatch) {
        compatibility_score = parseInt(compMatch[1], 10);
        compatibility_level = compMatch[2]?.trim() || '';
      }
      const message_description =
        extractField(block, 'Summary') ||
        extractField(block, 'Description') ||
        extractField(block, 'Message') ||
        extractField(block, 'Recommendation');
      // Astrological details (optional)
      const nakshatra = extractField(block, 'Nakshatra');
      const rashi = extractField(block, 'Rashi');
      matches.push({
        name, age, location, occupation, compatibility_score, compatibility_level, message_description,
        astrological_details: { nakshatra, rashi }
      });
    }
    // Analysis: everything after the last match
    const lastMatch = [...relevant.matchAll(profileRegex)].pop();
    const analysis = lastMatch
      ? relevant.slice(relevant.lastIndexOf(lastMatch[0]) + lastMatch[0].length).trim()
      : '';
    return { matches, analysis };
  }

  function isMultiProfileSummary(str: string) {
    // Looks for at least two numbered profile sections
    return (str.match(/\n\d+\.\s+\*\*/g) || []).length >= 2;
  }

  function stripMarkdown(md: string) {
    // Remove Markdown bold, headings, etc. for a clean info card
    return md
      .replace(/[#*_`>-]/g, '') // Remove markdown symbols
      .replace(/\n{2,}/g, '\n') // Collapse multiple newlines
      .trim();
  }

  // Filtering logic for matches
  function getFilteredMatches(matches: any[]) {
    // 1. Get all 'good' matches
    let goodMatches = matches.filter(m => m.message_type === 'good');
    // 2. If there are good matches, show up to 5 of them
    let filteredMatches;
    if (goodMatches.length > 0) {
      filteredMatches = goodMatches.slice(0, 5);
    } else {
      // 3. If no good matches, show only the best bad match
      let badMatches = matches.filter(m => m.message_type === 'bad');
      if (badMatches.length > 0) {
        const bestBad = badMatches.reduce((best, m) =>
          m.compatibility_score > (best?.compatibility_score || 0) ? m : best, null
        );
        filteredMatches = bestBad ? [bestBad] : [];
      } else {
        filteredMatches = [];
      }
    }
    return filteredMatches;
  }

  function getCompatibilityLabel(score: number) {
    if (score >= 70) return "Good Compatibility";
    if (score >= 50) return "Moderate Compatibility";
    return "Low Compatibility";
  }

  // Fallback extraction for plain string responses
  function extractMainInfoFromFallback(str: string) {
    const name = str.match(/\*\*Name\*\*: ([^\n]+)/)?.[1]?.trim() ||
                 str.match(/\d+\. \*\*([^\*]+)\*\*/)?.[1]?.trim() || '';
    const age = str.match(/\*\*Age\*\*: ([^\n]+)/)?.[1]?.trim() || '';
    const location = str.match(/\*\*Location\*\*: ([^\n]+)/)?.[1]?.trim() || '';
    const occupation = str.match(/\*\*Occupation\*\*: ([^\n]+)/)?.[1]?.trim() || '';
    const compatibility = str.match(/\*\*Compatibility Score\*\*: ([^\n]+)/)?.[1]?.trim() || '';
    const summary = str.match(/\*\*Summary\*\*: ([^\n]+)/)?.[1]?.trim()
      || str.match(/\*\*Description\*\*: ([^\n]+)/)?.[1]?.trim()
      || str.match(/\*\*Message\*\*: ([^\n]+)/)?.[1]?.trim()
      || str.match(/\*\*Recommendation\*\*: ([^\n]+)/)?.[1]?.trim()
      || '';
    return { name, age, location, occupation, compatibility, summary };
  }

  // Helper to extract a field by label from a string
  function extractFieldByLabel(str: string, label: string) {
    const regex = new RegExp(`\\*\\*${label}\\*\\*:?\\s*([^\\n]+)`);
    return str.match(regex)?.[1]?.trim() || '';
  }

  // Parser for fielded string profiles (e.g., '- **Name**: ...')
  function parseFieldedStringProfile(str: string) {
    const name = extractFieldByLabel(str, 'Name');
    const age = extractFieldByLabel(str, 'Age');
    const location = extractFieldByLabel(str, 'Location');
    const occupation = extractFieldByLabel(str, 'Occupation');
    const compatibility = extractFieldByLabel(str, 'Compatibility Score');
    const summary = extractFieldByLabel(str, 'Summary') ||
                    extractFieldByLabel(str, 'Description') ||
                    extractFieldByLabel(str, 'Message') ||
                    extractFieldByLabel(str, 'Recommendation');
    // Astrological details (optional)
    const nakshatra = extractFieldByLabel(str, 'Nakshatra');
    const rashi = extractFieldByLabel(str, 'Rashi');
    const koot = extractFieldByLabel(str, 'Koot Details');
    return {
      name, age, location, occupation, compatibility, summary,
      astrological_details: { nakshatra, rashi, koot }
    };
  }

  // Add a helper to determine if a string is a fielded profile
  function isFieldedProfile(str: string) {
    return /- \*\*Name\*\*:/.test(str);
  }

  // Helper: sanitize markdown to ensure blank lines before headings
  function sanitizeMarkdown(md: string) {
    // Ensure there is a blank line before every heading (##, ###, etc.)
    return md.replace(/([^\n])\n(#+ )/g, '$1\n\n$2');
  }

  // Fallback rendering (when all parsing fails)
  return (
    <MainLayout currentPage="MatchMyStar">
      <div className="container mx-auto p-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-center mb-2">
            <Heart className="inline-block mr-2 text-red-500" />
            MatchMyStar
          </h1>
          <p className="text-center text-muted-foreground">
            Find your perfect match using Indian astrology
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Profile Form */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Users className="mr-2" />
                Your Profile
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">Name</label>
                  <Input
                    value={userProfile.name}
                    onChange={(e) => setUserProfile({...userProfile, name: e.target.value})}
                    placeholder="Your name"
                    required
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Gender</label>
                  <select
                    value={userProfile.gender}
                    onChange={(e) => setUserProfile({...userProfile, gender: e.target.value})}
                    className="w-full p-2 border rounded-md"
                    required
                  >
                    <option value="">Select gender</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">Date of Birth</label>
                  <Input
                    type="date"
                    value={userProfile.dob}
                    onChange={(e) => setUserProfile({...userProfile, dob: e.target.value})}
                    required
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Time of Birth</label>
                  <Input
                    type="time"
                    value={userProfile.tob}
                    onChange={(e) => setUserProfile({...userProfile, tob: e.target.value})}
                    required
                  />
                </div>
              </div>

              <div>
                <label className="text-sm font-medium">Birth Place</label>
                <Input
                  value={userProfile.place}
                  onChange={(e) => setUserProfile({...userProfile, place: e.target.value})}
                  placeholder="City, State"
                  required
                />
              </div>

              <div>
                <label className="text-sm font-medium">Occupation</label>
                <Input
                  value={userProfile.occupation}
                  onChange={(e) => setUserProfile({...userProfile, occupation: e.target.value})}
                  placeholder="Your profession"
                />
              </div>

              {formError && <div className="text-red-500 text-sm">{formError}</div>}
              <Button 
                onClick={handleSubmit} 
                disabled={isLoading}
                className="w-full"
              >
                {isLoading ? "Finding Matches..." : "Find Matches"}
              </Button>
            </CardContent>
          </Card>

          {/* Results */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Heart className="mr-2 text-red-500" />
                Your Matches
              </CardTitle>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="text-center py-8 text-muted-foreground">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto mb-4"></div>
                  <p>Finding your perfect match...</p>
                </div>
              ) : (
                <div className="mx-auto max-w-2xl">
                  <div className="markdown-body">
                    {(() => {
                      // Prefer the fallback markdown string if present, else try to stringify the matches/analysis
                      const markdown = noMatchMessage ||
                        (matches && matches.length > 0
                          ? `# Match Results\n` + matches.map((m, i) => `## ${i+1}. ${m.name || 'Unknown'}\n- **Age:** ${m.age || ''}\n- **Location:** ${m.location || ''}\n- **Occupation:** ${m.occupation || ''}\n- **Compatibility Score:** ${m.compatibility_score || ''}%\n- **Message:** ${m.message_description || ''}`).join('\n\n')
                          : 'No matches found.');
                      const sanitized = sanitizeMarkdown(markdown);
                      return <ReactMarkdown remarkPlugins={[remarkGfm]}>{sanitized}</ReactMarkdown>;
                    })()}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </MainLayout>
  );
};

export default MatchMyStarPage; 