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
  const [isLoading, setIsLoading] = useState(false);
  const [formError, setFormError] = useState('');
  const { showSuccess, showError } = useToast();

  // Add WebSocket message handler
  useEffect(() => {
    const handleWebSocketMessage = (response: AgentResponse) => {
      if (response.type === 'agent_response') {
        setMatches([
          typeof response.response.response.response === 'string'
            ? response.response.response.response
            : JSON.stringify(response.response.response.response)
        ]);
        setIsLoading(false);
      }
    };
    websocketService.addMessageHandler(handleWebSocketMessage);
    return () => websocketService.removeMessageHandler(handleWebSocketMessage);
  }, []);

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
    await websocketService.connect();
    const message = {
      message: `Find matches for ${userProfile.name} based on their profile: ${JSON.stringify(userProfile)}`,
      provider: 'genai',
      llm_name: 'default'
    };
    websocketService.sendMessage(message);
  };

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
              {matches.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <Users className="mx-auto mb-4 h-12 w-12" />
                  <p>No matches found yet. Fill your profile and click "Find Matches" to get started.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {matches.map((match, index) => (
                    <Card key={index} className="border-l-4 border-l-green-500">
                      <CardContent className="p-4">
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <h3 className="font-semibold">{match.name}</h3>
                            <p className="text-sm text-muted-foreground">
                              {match.age} years • {match.location}
                            </p>
                            <p className="text-sm text-muted-foreground">
                              {match.occupation}
                            </p>
                          </div>
                          <Badge variant="secondary">
                            {match.compatibility_score}% Match
                          </Badge>
                        </div>
                        <p className="text-sm">{match.summary}</p>
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