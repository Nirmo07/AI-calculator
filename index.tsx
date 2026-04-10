// Home.tsx
import { ColorSwatch, Group } from '@mantine/core';
import { Button } from '../../components/ui/button';
import { useEffect, useRef, useState } from 'react';
import axios from 'axios';
import Draggable from 'react-draggable';
import { SWATCHES } from '../../constants';
import { useNavigate } from 'react-router-dom'; // Import useNavigate

declare global {
  interface Window {
    MathJax: {
      Hub: {
        Queue: (commands: (string | [string, number])[]) => void;
        Config: (config: { tex2jax: { inlineMath: string[][] } }) => void;
      };
    };
  }
}

interface Response {
  expr: string;
  result: string;
  assign: boolean;
}

interface DraggableItem {
  id: number; // Unique ID for each Draggable
  latex: string; // LaTeX expression
  position: { x: number; y: number }; // Position of the Draggable
}

export default function Home() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [color, setColor] = useState('rgb(255, 255, 255)');
  const [reset, setReset] = useState(false);
  const [dictOfVars, setDictOfVars] = useState<Record<string, string>>({});
  const [draggableItems, setDraggableItems] = useState<DraggableItem[]>([]);
  const [isErasing, setIsErasing] = useState(false);
  const nodeRef = useRef(null);
  const nextId = useRef(0); // Counter for unique IDs
  const navigate = useNavigate(); // Hook for navigation

  // Initialize canvas and MathJax
  useEffect(() => {
    const canvas = canvasRef.current;

    if (canvas) {
      const ctx = canvas.getContext('2d');
      if (ctx) {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight * 0.8; // Leave space for UI
        ctx.lineCap = 'round';
        ctx.lineWidth = 3;
      }
    }

    const script = document.createElement('script');
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.9/MathJax.js?config=TeX-MML-AM_CHTML';
    script.async = true;
    document.head.appendChild(script);

    script.onload = () => {
      window.MathJax.Hub.Config({
        tex2jax: { inlineMath: [['$', '$'], ['\\(', '\\)']] },
      });
    };

    return () => {
      document.head.removeChild(script);
    };
  }, []);

  // Render LaTeX expressions
  useEffect(() => {
    if (draggableItems.length > 0 && window.MathJax) {
      setTimeout(() => {
        window.MathJax.Hub.Queue(['Typeset', window.MathJax.Hub]);
      }, 0);
    }
  }, [draggableItems]);

  // Reset canvas and state
  useEffect(() => {
    if (reset) {
      resetCanvas();
      setDraggableItems([]);
      setDictOfVars({});
      setReset(false);
      nextId.current = 0; // Reset the ID counter
    }
  }, [reset]);

  // Reset canvas
  const resetCanvas = () => {
    const canvas = canvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
      }
    }
  };

  // Start drawing
  const startDrawing = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.beginPath();
        ctx.moveTo(e.nativeEvent.offsetX, e.nativeEvent.offsetY);
        setIsDrawing(true);
      }
    }
  };

  // Draw on canvas
  const draw = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDrawing) {
      return;
    }
    const canvas = canvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext('2d');
      if (ctx) {
        if (isErasing) {
          // Erase mode
          ctx.globalCompositeOperation = 'destination-out';
          ctx.strokeStyle = 'rgba(0, 0, 0, 1)';
          ctx.lineWidth = 10;
        } else {
          // Draw mode
          ctx.globalCompositeOperation = 'source-over';
          ctx.strokeStyle = color;
          ctx.lineWidth = 3;
        }
        ctx.lineTo(e.nativeEvent.offsetX, e.nativeEvent.offsetY);
        ctx.stroke();
      }
    }
  };

  // Stop drawing
  const stopDrawing = () => {
    setIsDrawing(false);
    const canvas = canvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.globalCompositeOperation = 'source-over'; // Reset to default
      }
    }
  };

  // Toggle erase mode
  const toggleErase = () => {
    setIsErasing((prev) => !prev);
  };

  // Navigate to switch mode page
  const handleSwitchMode = () => {
    navigate('/cam-mode'); // Navigate to the switch mode page
  };

  // Send image to backend for processing
  const runRoute = async () => {
    const canvas = canvasRef.current;
    if (canvas) {
      try {
        const response = await axios.post(`${import.meta.env.VITE_API_URL}/calculate`, {
          image: canvas.toDataURL('image/png'),
          dict_of_vars: dictOfVars,
        });

        const resp = response.data;
        console.log('Response', resp);

        if (resp.status === 'success' && resp.data.length > 0) {
          // Clear the canvas
          resetCanvas();

          resp.data.forEach((data: Response) => {
            if (data.assign) {
              setDictOfVars((prev) => ({
                ...prev,
                [data.expr]: data.result,
              }));
            }

            // Calculate the center of the drawing area
            const ctx = canvas.getContext('2d');
            if (ctx) {
              const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
              let minX = canvas.width,
                minY = canvas.height,
                maxX = 0,
                maxY = 0;

              for (let y = 0; y < canvas.height; y++) {
                for (let x = 0; x < canvas.width; x++) {
                  const i = (y * canvas.width + x) * 4;
                  if (imageData.data[i + 3] > 0) {
                    // Non-transparent pixel
                    minX = Math.min(minX, x);
                    minY = Math.min(minY, y);
                    maxX = Math.max(maxX, x);
                    maxY = Math.max(maxY, y);
                  }
                }
              }

              // Calculate the center of the drawing
              const centerX = (minX + maxX) / 2;
              const centerY = (minY + maxY) / 2;

              // Add new Draggable item
              const newItem: DraggableItem = {
                id: nextId.current++, // Assign a unique ID
                latex: `\\(\\LARGE{\\text{${data.expr} = ${data.result}}}\\)`,
                position: { x: centerX, y: centerY },
              };

              // Append the new item to the existing list
              setDraggableItems((prev) => [...prev, newItem]);
            }
          });
        } else {
          console.warn('No valid responses from Gemini API');
        }
      } catch (error) {
        console.error('Error processing image:', error);
      }
    }
  };

  return (
    <>
      <div className='flex justify-between p-4 bg-gray-800'>
        <div className='flex gap-2'>
          <Button
            onClick={() => setReset(true)}
            className='bg-red-500 hover:bg-red-600 text-white'
          >
            Reset
          </Button>
          <Button
            onClick={toggleErase}
            className={`${isErasing ? 'bg-blue-500' : 'bg-gray-500'} hover:bg-blue-600 text-white`}
          >
            {isErasing ? 'Drawing Mode' : 'Erase Mode'}
          </Button>
          <Button
            onClick={handleSwitchMode}
            className='bg-purple-500 hover:bg-purple-600 text-white'
          >
            Switch Mode
          </Button>
        </div>
        <Group>
          {SWATCHES.map((swatch) => (
            <ColorSwatch key={swatch} color={swatch} onClick={() => setColor(swatch)} />
          ))}
        </Group>
        <Button
          onClick={runRoute}
          className='bg-green-500 hover:bg-green-600 text-white'
        >
          Run
        </Button>
      </div>
      <canvas
        ref={canvasRef}
        id='canvas'
        className='w-full bg-black border border-gray-300'
        style={{ height: '80vh', cursor: isErasing ? 'url("https://www.iconarchive.com/download/i103468/paomedia/small-n-flat/eraser.ico"), auto' : 'crosshair' }}
        onMouseDown={startDrawing}
        onMouseMove={draw}
        onMouseUp={stopDrawing}
        onMouseOut={stopDrawing}
      />

      {draggableItems.map((item) => (
        <Draggable
          key={item.id} // Use unique ID as key
          nodeRef={nodeRef}
          position={item.position} // Use individual position
          onStop={(_, data) => {
            // Update the position of the specific Draggable
            setDraggableItems((prev) =>
              prev.map((prevItem) =>
                prevItem.id === item.id
                  ? { ...prevItem, position: { x: data.x, y: data.y } }
                  : prevItem
              )
            );
          }}
        >
          <div
            ref={nodeRef}
            className="absolute p-2 text-black rounded shadow-md bg-white mt-0"
            style={{ cursor: 'move' }}
          >
            <div className="latex-content">{item.latex}</div>
          </div>
        </Draggable>
      ))}
    </>
  );
}