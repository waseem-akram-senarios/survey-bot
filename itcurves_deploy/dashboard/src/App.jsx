import './App.css'
import ThemeRoutes from './routes/index';
import { AuthProvider } from './context/AuthContext';

function App() {
  return (
    <AuthProvider>
      <ThemeRoutes />
    </AuthProvider>
  )
}

export default App
