import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import UploadPage from "./pages/UploadPage";
import GalleryPage from "./pages/GalleryPage";
import ChatbotPage from "./pages/ChatbotPage";
import PeoplePage from "./pages/PeoplePage";
import PersonPhotosPage from "./pages/PersonPhotosPage";
import "./App.css";

function App() {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/"              element={<UploadPage />} />
        <Route path="/upload"        element={<UploadPage />} />
        <Route path="/gallery"       element={<GalleryPage />} />
        <Route path="/chat"          element={<ChatbotPage />} />
        <Route path="/people"        element={<PeoplePage />} />
        <Route path="/people/:id"    element={<PersonPhotosPage />} />
      </Routes>
    </Router>
  );
}

export default App;
