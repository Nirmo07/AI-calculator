import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import '@mantine/core/styles.css';
import { MantineProvider } from '@mantine/core';
import Home from './screens/home';
import CamMode from './screens/camMode'; // Import the new camMode component
import './index.css';

// Define the routes
const paths = [
  {
    path: '/',
    element: <Home />, // Home screen
  },
  {
    path: '/cam-mode', // New route for camMode
    element: <CamMode />,
  },
];

// Create the router
const BrowserRouter = createBrowserRouter(paths);

const App = () => {
  return (
    <MantineProvider>
      <RouterProvider router={BrowserRouter} />
    </MantineProvider>
  );
};

export default App;