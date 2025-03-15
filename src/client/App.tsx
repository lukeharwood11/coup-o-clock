import './App.css';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { HomePage } from './pages/home-page/home.page';
import { RoomsPage } from './pages/rooms-page/rooms.page';
import { GamePage } from './pages/game-page/GamePage.page';

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/rooms" element={<RoomsPage />} />
                <Route path="/play" element={<GamePage />} />
                <Route path="*" element={<Navigate to="/" />} />
            </Routes>
        </Router>
    );
}
export default App;
