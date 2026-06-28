import { useState, useEffect } from "react";

function App() {
  const emptyGrid = Array.from({ length: 9 }, () => Array(9).fill(0));
  const emptyBoolGrid = Array.from({ length: 9 }, () => Array(9).fill(false));

  const [givenGrid, setGivenGrid] = useState(emptyBoolGrid);
  const [filledBeforeSolve, setFilledBeforeSolve] = useState(emptyBoolGrid);
  const [grid, setGrid] = useState(emptyGrid);
  const [invalidCells, setInvalidCells] = useState([]);
  const [solvedGrid, setSolvedGrid] = useState(null);
  
  const [statusMsg, setStatusMsg] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [imagePreview, setImagePreview] = useState(null);
  
  const [isBackendConnected, setIsBackendConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(true);

  const samplePuzzle = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9],
  ];

  const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

  useEffect(() => {
    async function wakeBackend() {
      try {
        const res = await fetch(`${API_BASE}/`);
        if (res.ok) {
          setIsBackendConnected(true);
        }
      } catch (err) {
        console.error("Backend not reachable yet", err);
      } finally {
        setIsConnecting(false);
      }
    }
    wakeBackend();
  }, [API_BASE]);

  async function solveSudoku() {
    setFilledBeforeSolve(grid.map((row) => row.map((v) => v !== 0)));
    setStatusMsg("Solving...");
    setIsLoading(true);

    try {
      const res = await fetch(`${API_BASE}/solve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ board: grid }),
      });

      if (!res.ok) {
        const err = await res.json();
        alert(err.detail || "Cannot solve invalid Sudoku");
        setStatusMsg("");
        return;
      }

      const data = await res.json();

      if (data.solved) {
        setSolvedGrid(data.board);
        setStatusMsg("Solved successfully!");
      } else {
        setStatusMsg("");
        alert("No solution exists for this Sudoku");
      }
    } catch (err) {
      console.error("Solve failed", err);
      setStatusMsg("Solve failed.");
    } finally {
      setIsLoading(false);
    }
  }

  async function validateGrid(updatedGrid) {
    try {
      const res = await fetch(`${API_BASE}/validate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ board: updatedGrid }),
      });

      const data = await res.json();
      setInvalidCells(data.invalid_cells);
    } catch (err) {
      console.error("Validation failed", err);
    }
  }

  async function handleImageUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    setIsLoading(true);
    setStatusMsg("Processing image with OCR...");

    const previewUrl = URL.createObjectURL(file);
    setImagePreview(previewUrl);

    const formData = new FormData();
    formData.append("image", file);

    try {
      const res = await fetch(`${API_BASE}/ocr`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "OCR failed");
      }

      const data = await res.json();

      setGrid(data.board);
      setGivenGrid(emptyBoolGrid);
      setSolvedGrid(null);
      setInvalidCells([]);

      validateGrid(data.board);
      setStatusMsg("Verify the detected Sudoku grid and correct any errors.");
    } catch (err) {
      console.error("OCR error", err);
      alert("Failed to read Sudoku from image");
      setImagePreview(null);
      setStatusMsg("");
    } finally {
      setIsLoading(false);
    }
  }

  function handleChange(r, c, value) {
    if (isGiven(r, c)) return;
    const newGrid = grid.map((row) => [...row]);
    newGrid[r][c] = value;
    setGrid(newGrid);
    setSolvedGrid(null);
    setStatusMsg("");
    validateGrid(newGrid);
  }

  function isInvalid(r, c) {
    return invalidCells.some(([row, col]) => row === r && col === c);
  }

  function isGridValid() {
    return invalidCells.length === 0;
  }

  function isGiven(r, c) {
    return givenGrid[r][c];
  }

  return (
    <div className="container">
      <h1 className="title">Sudoku Solver</h1>

      <div className="main-content">
        <div className="left-panel">
          <table className="sudoku-board">
            <tbody>
              {grid.map((row, r) => (
                <tr key={r} className="sudoku-row">
                  {row.map((cell, c) => {
                    const displayValue = solvedGrid ? solvedGrid[r][c] : grid[r][c];
                    
                    let cellClass = "sudoku-cell";
                    if (isGiven(r, c)) cellClass += " given";
                    if (isInvalid(r, c)) cellClass += " invalid";
                    if (solvedGrid && !filledBeforeSolve[r][c]) cellClass += " solved";

                    return (
                      <td key={c}>
                        <input
                          type="text"
                          inputMode="numeric"
                          maxLength={1}
                          value={displayValue === 0 ? "" : displayValue}
                          disabled={isGiven(r, c) || solvedGrid !== null}
                          onChange={(e) => {
                            const v = e.target.value;
                            if (v === "" || /^[1-9]$/.test(v)) {
                              handleChange(r, c, v === "" ? 0 : Number(v));
                            }
                          }}
                          className={cellClass}
                        />
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>

          <div className="controls">
            <button
              onClick={solveSudoku}
              disabled={!isGridValid() || isLoading || !isBackendConnected}
              className="btn primary"
            >
              Solve Puzzle
            </button>
            <button
              onClick={() => {
                const preset = samplePuzzle.map((row) => [...row]);
                setGrid(preset);
                setStatusMsg("");
                setImagePreview(null);
                setGivenGrid(preset.map((row) => row.map((v) => v !== 0)));
                setSolvedGrid(null);
                validateGrid(preset);
              }}
              disabled={!isBackendConnected}
              className="btn"
            >
              Load Sample
            </button>
            <button
              onClick={() => {
                setGrid(emptyGrid);
                setGivenGrid(emptyBoolGrid);
                setSolvedGrid(null);
                setImagePreview(null);
                setStatusMsg("");
                setInvalidCells([]);
              }}
              disabled={!isBackendConnected}
              className="btn"
            >
              Clear
            </button>
          </div>
        </div>

        <div className="right-panel">
          <div className="file-upload-wrapper">
            <button className="btn file-upload-btn" disabled={!isBackendConnected || isLoading}>
              Upload Image for OCR
            </button>
            <input 
              type="file" 
              accept="image/*" 
              onChange={handleImageUpload} 
              disabled={!isBackendConnected || isLoading}
            />
          </div>

          <div className="image-preview-container">
            {imagePreview ? (
              <img src={imagePreview} alt="Uploaded Sudoku" />
            ) : (
              <span style={{ color: "var(--text-muted)" }}>Image Preview</span>
            )}
          </div>
          
          <div className={`status-message ${isLoading || isConnecting ? "loading" : ""}`}>
            {isConnecting ? "Waking up backend, please wait..." : (!isBackendConnected && !isConnecting ? "Cannot connect to backend." : statusMsg)}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
