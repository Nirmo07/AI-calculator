import { useEffect, useRef, useState } from 'react';
import { Button } from '../components/ui/button';

export default function CamMode() {
  const videoRef = useRef<HTMLImageElement>(null); // Reference for the video stream
  const [response, setResponse] = useState<string>(''); // State for AI response
  const [isConnected, setIsConnected] = useState<boolean>(false); // State for WebSocket connection
  const wsRef = useRef<WebSocket | null>(null); // Ref to store WebSocket instance

  useEffect(() => {
    // Establish WebSocket connection
    const ws = new WebSocket('ws://localhost:8900/ws');
    wsRef.current = ws; // Store WebSocket instance in ref

    ws.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      if (typeof event.data === 'string') {
        // Handle AI response
        setResponse(event.data);
      } else {
        // Handle video stream (binary data)
        const blob = new Blob([event.data], { type: 'image/jpeg' });
        const url = URL.createObjectURL(blob);
        if (videoRef.current) {
          videoRef.current.src = url;
        }
      }
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    // Cleanup on component unmount
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const handleGoBack = () => {
    // Close WebSocket connection if it's open
    if (wsRef.current) {
      wsRef.current.close();
    }

    // Navigate back
    window.history.back();
  };

  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gray-100 p-4">
      <h1 className="text-2xl font-bold mb-4">Camera Mode</h1>
      <p className="mb-4">Use your hand gestures to draw and interact with the AI.</p>

      {/* Video Stream */}
      <div className="mb-4">
        <img
          ref={videoRef}
          alt="Video Stream"
          className="border-2 border-gray-300 rounded-lg"
          style={{ width: '640px', height: '360px' }}
        />
      </div>

      {/* AI Response */}
      <div className="w-full max-w-2xl bg-white p-4 rounded-lg shadow-md mb-4">
        <h2 className="text-xl font-semibold mb-2">AI Response:</h2>
        <p className="text-gray-700">{response}</p>
      </div>

      {/* Connection Status */}
      <div className="mb-4">
        <p className="text-sm text-gray-600">
          WebSocket Connection: {isConnected ? 'Connected' : 'Disconnected'}
        </p>
      </div>

      {/* Go Back Button */}
      <Button
        onClick={handleGoBack}
        className="bg-blue-500 hover:bg-blue-600 text-white"
      >
        Go Back
      </Button>
    </div>
  );
}