import "./App.css";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import StartingInterface from "./components/pages/startingInterface/StartingInterface";
import GetDisabilityInterface from "./components/pages/getDisabilityInterface/GetDisabilityInterface";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<StartingInterface />} />
        <Route path="/next" element={<GetDisabilityInterface />} />
      </Routes>
    </Router>
  );
}

export default App;
