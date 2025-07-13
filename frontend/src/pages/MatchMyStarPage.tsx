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
          console.log('Raw WebSocket response:', response); // Debug log
          
          // Try to find the matches array at any depth
          let responseData;
          if (typeof response.response?.response?.response === 'string') {
            const str = response.response.response.response;
            if (isJsonString(str)) {
              responseData = JSON.parse(str);
            } else {
              // Not JSON, treat as plain message
              console.log('Non-JSON string response from backend:', str); // <-- Add this line
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

          console.log('Parsed response data:', responseData);
          console.log('Found matches:', matches);

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
                console.log('MatchMyStar Analysis:', analysis.message);
              }
            } else {
              showSuccess(`Found ${responseData.total_matches} matches!`);
            }
          } else {
            console.log('Response format not recognized, using fallback'); // Debug log
            console.log('ResponseData keys:', Object.keys(responseData || {})); // Debug log
            // Fallback for other response formats
            setMatches([]);
            setAnalysis(null);
            setNoMatchMessage("We couldn't find any compatible matches for you right now. Please check back later as new profiles are added!");
          }
        } catch (error) {
          console.error('Error parsing response:', error);
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

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // setHoroscopeFile(file); // This state was removed, so this line is no longer relevant
      showSuccess(`${file.name} uploaded successfully`);
    }
  };

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

  // Robust summary string parser for all backend formats
  function parseSummaryString(summary: string): { matches: any[]; analysis: string } {
    // Universal field extractor
    function extractField(block: string, field: string): string {
      const regex = new RegExp(`\\*\\*${field}\\*\\*:?\\s*([^\\n]+)`);
      return block.match(regex)?.[1]?.trim() || '';
    }

    // Profile regex: number, name, then all lines until next profile or end
    const profileRegex = /(\d+)\.\s+\*\*([^\*]+)\*\*([\s\S]*?)(?=\n\d+\. \*\*|$)/g;
    const matches = [];
    let match;
    while ((match = profileRegex.exec(summary)) !== null) {
      const name = match[2].trim();
      const block = match[3];
      const age = extractField(block, 'Age');
      const location = extractField(block, 'Location');
      const occupation = extractField(block, 'Occupation');
      // Compatibility Score and Level (with or without parentheses)
      let compatibility_score = 0, compatibility_level = '';
      const compMatch = block.match(/\*\*Compatibility Score\*\*:?\s*(\d+)%\s*(?:\(([^)]+)\))?/);
      if (compMatch) {
        compatibility_score = parseInt(compMatch[1], 10);
        compatibility_level = compMatch[2]?.trim() || '';
      }
      const message_description =
        extractField(block, 'Summary') ||
        extractField(block, 'Description') ||
        extractField(block, 'Message');
      // Astrological details (optional)
      const nakshatra = extractField(block, 'Nakshatra');
      const rashi = extractField(block, 'Rashi');
      matches.push({
        name, age, location, occupation, compatibility_score, compatibility_level, message_description,
        astrological_details: { nakshatra, rashi }
      });
    }
    // Analysis: everything after the last match
    const lastMatch = [...summary.matchAll(profileRegex)].pop();
    const analysis = lastMatch
      ? summary.slice(summary.lastIndexOf(lastMatch[0]) + lastMatch[0].length).trim()
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

              {/* Horoscope Upload */}
              <div>
                <label className="text-sm font-medium flex items-center">
                  <FileText className="mr-2" />
                  Upload Horoscope (Optional)
                </label>
                <div className="mt-2">
                  <Input
                    type="file"
                    accept=".pdf,.jpg,.jpeg,.png"
                    onChange={handleFileUpload}
                  />
                </div>
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
              ) : matches.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <Users className="mx-auto mb-4 h-12 w-12" />
                  {noMatchMessage ? (
                    isMultiProfileSummary(noMatchMessage) ? (
                      (() => {
                        const { matches: parsedMatches, analysis: parsedAnalysis } = parseSummaryString(noMatchMessage);
                        return (
                          <>
                            {parsedAnalysis && (
                              <Card className="border-l-4 border-l-blue-500 bg-blue-50 mb-4">
                                <CardContent className="p-4">
                                  <h3 className="font-semibold text-blue-800 mb-2">📊 Compatibility Analysis</h3>
                                  <p className="text-blue-700 text-base whitespace-pre-line">{parsedAnalysis}</p>
                                </CardContent>
                              </Card>
                            )}
                            {parsedMatches.map((match, index) => (
                              <Card key={index} className={`border-l-4 ${getCompatibilityColor(match.compatibility_score)} shadow-lg hover:shadow-xl transition-shadow duration-300 mb-4`}>
                                <CardContent className="p-6">
                                  <div className="flex justify-between items-start mb-4">
                                    <div className="flex-1">
                                      <div className="flex items-center gap-3 mb-3">
                                        <div className={`w-16 h-16 rounded-full flex items-center justify-center text-white font-bold text-xl ${
                                          match.compatibility_score >= 70 ? 'bg-gradient-to-br from-green-400 to-green-600' :
                                          match.compatibility_score >= 50 ? 'bg-gradient-to-br from-yellow-400 to-yellow-600' :
                                          'bg-gradient-to-br from-red-400 to-red-600'
                                        }`}>
                                          {match.name.charAt(0).toUpperCase()}
                                        </div>
                                        <div>
                                          <h3 className="text-xl font-bold">{match.name}</h3>
                                          <p className="text-sm text-muted-foreground">
                                            {match.age} years • {match.location}
                                          </p>
                                          <p className="text-sm text-muted-foreground">
                                            {match.occupation}
                                          </p>
                                        </div>
                                      </div>
                                    </div>
                                    <div className="text-right">
                                      <Badge 
                                        variant={match.compatibility_score >= 70 ? "default" : match.compatibility_score >= 50 ? "secondary" : "destructive"}
                                        className="mb-2 text-lg px-4 py-2"
                                      >
                                        {match.compatibility_score}% Match
                                      </Badge>
                                      <p className="text-sm font-semibold text-muted-foreground">
                                        {match.compatibility_level}
                                      </p>
                                    </div>
                                  </div>
                                  <div className="border-t pt-4">
                                    <h4 className="font-semibold mb-2 text-gray-800">Astrological Analysis</h4>
                                    <div className="bg-blue-50 p-4 rounded-md">
                                      <p className="text-sm text-gray-700 leading-relaxed">
                                        {match.message_description}
                                      </p>
                                    </div>
                                  </div>
                                </CardContent>
                              </Card>
                            ))}
                          </>
                        );
                      })()
                    ) : (
                      <Card className="mx-auto max-w-lg border-l-4 border-l-blue-500 bg-blue-50">
                        <CardContent className="p-6">
                          <p className="text-gray-700 text-base whitespace-pre-line">
                            {stripMarkdown(noMatchMessage)}
                          </p>
                        </CardContent>
                      </Card>
                    )
                  ) : (
                    <p>No matches found yet. Fill your profile and click "Find Matches" to get started.</p>
                  )}
                </div>
              ) : (
                <div className="space-y-4">
                  {/* Analysis Section */}
                  {analysis && (
                    <Card className="border-l-4 border-l-blue-500 bg-blue-50">
                      <CardContent className="p-4">
                        <h3 className="font-semibold text-blue-800 mb-2">📊 Compatibility Analysis</h3>
                        <div className="space-y-2 text-sm">
                          <p className="text-blue-700"><strong>{analysis.overall_assessment}</strong></p>
                          {analysis.recommendation && (
                            <p className="text-blue-600">{analysis.recommendation}</p>
                          )}
                          {analysis.statistics && (
                            <div className="grid grid-cols-2 gap-2 text-xs">
                              <div>Average Score: <strong>{analysis.statistics.average_score}%</strong></div>
                              <div>Best Score: <strong>{analysis.statistics.highest_score}%</strong></div>
                              <div>Total Matches: <strong>{analysis.statistics.total_matches}</strong></div>
                              <div>Good+ Matches: <strong>{analysis.statistics.good_matches + analysis.statistics.moderate_matches}</strong></div>
                            </div>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  )}
                  
                  {/* Status Message */}
                  {getMatchStatusMessage(matches, analysis) && (
                    <div className="text-center py-3 bg-gray-50 rounded-md">
                      <p className="text-sm font-medium text-gray-700">
                        {getMatchStatusMessage(matches, analysis)}
                      </p>
                    </div>
                  )}
                  
                  {/* Matches Section */}
                  {matches.map((match, index) => (
                    <Card key={index} className={`border-l-4 ${getCompatibilityColor(match.compatibility_score)} shadow-lg hover:shadow-xl transition-shadow duration-300`}>
                      <CardContent className="p-6">
                        {/* Person Details Section */}
                        <div className="flex justify-between items-start mb-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-3">
                              <div className={`w-16 h-16 rounded-full flex items-center justify-center text-white font-bold text-xl ${
                                match.compatibility_score >= 70 ? 'bg-gradient-to-br from-green-400 to-green-600' :
                                match.compatibility_score >= 50 ? 'bg-gradient-to-br from-yellow-400 to-yellow-600' :
                                'bg-gradient-to-br from-red-400 to-red-600'
                              }`}>
                                {match.name.charAt(0).toUpperCase()}
                              </div>
                              <div>
                                <h3 className="text-xl font-bold">{match.name}</h3>
                                <p className="text-sm text-muted-foreground">
                                  {match.age} years • {match.location}
                                </p>
                                <p className="text-sm text-muted-foreground">
                                  {match.occupation}
                                </p>
                              </div>
                            </div>
                            
                            {/* Astrological Details */}
                            {match.astrological_details && (
                              <div className="grid grid-cols-2 gap-3 text-xs bg-gray-50 p-3 rounded-md">
                                {match.astrological_details.nakshatra && (
                                  <div>
                                    <span className="font-semibold">Nakshatra:</span> {match.astrological_details.nakshatra.name}
                                  </div>
                                )}
                                {match.astrological_details.rashi && (
                                  <div>
                                    <span className="font-semibold">Rashi:</span> {match.astrological_details.rashi.name}
                                  </div>
                                )}
                                {match.astrological_details.koot && (
                                  <>
                                    <div>
                                      <span className="font-semibold">Varna:</span> {match.astrological_details.koot.varna}
                                    </div>
                                    <div>
                                      <span className="font-semibold">Gana:</span> {match.astrological_details.koot.gana}
                                    </div>
                                  </>
                                )}
                              </div>
                            )}
                          </div>
                          
                          {/* Compatibility Score */}
                          <div className="text-right">
                            <Badge 
                              variant={match.compatibility_score >= 70 ? "default" : match.compatibility_score >= 50 ? "secondary" : "destructive"}
                              className="mb-2 text-lg px-4 py-2"
                            >
                              {match.compatibility_score}% Match
                            </Badge>
                            <p className="text-sm font-semibold text-muted-foreground">
                              {match.compatibility_level}
                            </p>
                            <div className="text-xs text-muted-foreground mt-1">
                              {match.total_points}/{match.maximum_points} points
                            </div>
                          </div>
                        </div>
                        
                        {/* Compatibility Analysis */}
                        <div className="border-t pt-4">
                          <h4 className="font-semibold mb-2 text-gray-800">Astrological Analysis</h4>
                          <div className="bg-blue-50 p-4 rounded-md">
                            <p className="text-sm text-gray-700 leading-relaxed">
                              {match.message_description || 
                               `Compatibility Score: ${match.compatibility_score}% (${match.total_points}/${match.maximum_points} points). ${match.compatibility_level}.`}
                            </p>
                          </div>
                        </div>
                        
                        {/* Warning for not recommended matches */}
                        {match.message_type === 'not-preferable' && (
                          <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-md">
                            <p className="text-xs text-red-600 font-medium">
                              ⚠️ This match has serious compatibility issues. Consider consulting an astrologer.
                            </p>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  ))}
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