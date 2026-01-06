import { useState } from "react";

function App() {
  const emptyGrid = Array.from({ length: 9 }, () =>
    Array(9).fill(0)
  );

  const [initialGrid, setInitialGrid] = useState(emptyGrid)
  const [grid, setGrid] = useState(
    Array.from({ length: 9 }, () => Array(9).fill(0))
  )

  const [invalidCells, setInvalidCells] = useState([])
  const [solvedGrid, setSolvedGrid] = useState(null)
  const [showOcrNotice, setShowOcrNotice] = useState(false)

  const samplePuzzle = [
    [5,3,0,0,7,0,0,0,0],
    [6,0,0,1,9,5,0,0,0],
    [0,9,8,0,0,0,0,6,0],
    [8,0,0,0,6,0,0,0,3],
    [4,0,0,8,0,3,0,0,1],
    [7,0,0,0,2,0,0,0,6],
    [0,6,0,0,0,0,2,8,0],
    [0,0,0,4,1,9,0,0,5],
    [0,0,0,0,8,0,0,7,9]
  ];

  const API_BASE = "https://sudoku-solver-backend-w5wk.onrender.com"

  async function solveSudoku() {
    try {
      const res = await fetch($(API_BASE)/solve, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ board: grid })
      })

      if (!res.ok) {
        const err = await res.json()
        alert(err.detail || "Cannot solve invalid Sudoku")
        return
      }

      const data = await res.json()

      if (data.solved) {
        setSolvedGrid(data.board)
      } else {
        alert("No solution exists for this Sudoku")
      }
    } catch (err) {
      console.error("Solve failed", err)
    }
  }

  async function validateGrid(updatedGrid) {
    try {
      const res = await fetch($(API_BASE)/validate, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ board: updatedGrid })
      })

      const data = await res.json()
      setInvalidCells(data.invalid_cells)
    } catch (err) {
      console.error("Validation failed", err)
    }
  }

  async function handleImageUpload(e) {
    const file = e.target.files[0]
    if (!file) return

    const formData = new FormData()
    formData.append("image", file)

    try {
      const res = await fetch($(API_BASE)/ocr, {
        method: "POST",
        body: formData
      })

      if (!res.ok) {
        const err = await res.json()
        alert(err.detail || "OCR failed")
        return
      }

      const data = await res.json()

      setGrid(data.board)
      setSolvedGrid(null)
      setShowOcrNotice(true)
      setInvalidCells([])
      validateGrid(data.board)

    } catch (err) {
      console.error("OCR error", err)
      alert("Failed to read Sudoku from image")
    }
  }

  function handleChange(r, c, value) {
    if (isGiven(r, c)) return 
    const newGrid = grid.map(row => [...row])
    newGrid[r][c] = value
    setGrid(newGrid)
    setSolvedGrid(null)
    setShowOcrNotice(false)
    validateGrid(newGrid)
  }

  function isInvalid(r, c) {
    return invalidCells.some(
      ([row, col]) => row === r && col === c
    )
  }

  function isGridValid() {
    return invalidCells.length === 0
  }

  function isGiven(r, c) {
    return initialGrid[r][c] !== 0
  }

  return (
    <div style={{ padding: "20px" }}>
      <h1>Sudoku Solver</h1>

      <input
        type="file"
        accept="image/*"
        onChange={handleImageUpload}
      />

      <table>
        <tbody>
          {grid.map((row, r) => (
            <tr key={r}>
              {row.map((cell, c) => {
                const displayValue = solvedGrid ? solvedGrid[r][c] : grid[r][c]

                return (
                  <td key={c}>
                    <input
                      type="text"
                      inputMode="numeric"
                      maxLength={1}
                      value={displayValue === 0 ? "" : displayValue}
                      disabled={isGiven(r, c) || solvedGrid !== null}
                      onChange={(e) => {
                        const v = e.target.value
                        if (v === "" || /^[1-9]$/.test(v)) {
                          handleChange(r, c, v === "" ? 0 : Number(v))
                        }
                      }}
                      style={{
                        width: "42px",
                        height: "42px",
                        textAlign: "center",
                        fontSize: "20px",
                        fontWeight: isGiven(r, c) ? "bold" : "normal",
                        color: "#000000",
                        caretColor: "#000000",
                        backgroundColor: isInvalid(r, c)
                          ? "#fecaca"            
                          : isGiven(r, c)
                          ? "#e9d5ff"            
                          : "#ffffff",           
                        borderTop: r % 3 === 0 ? "3px solid #444" : "1px solid #aaa",
                        borderLeft: c % 3 === 0 ? "3px solid #444" : "1px solid #aaa",
                        borderRight: c === 8 ? "3px solid #444" : "1px solid #aaa",
                        borderBottom: r === 8 ? "3px solid #444" : "1px solid #aaa",
                        outline: "none",
                        boxSizing: "border-box",
                      }}
                    />
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
      <div
        style={{
          visibility: showOcrNotice ? "visible":"hidden"
        }}
      >
        Verify the detected sudoku grid<br />
        Correct any incorrect cells before proceeding.
      </div>
      <div style={{ marginTop: "20px" }}>
        <button
          onClick={solveSudoku}
          disabled={!isGridValid()}
          style={{
            marginTop: "20px",
            padding: "10px 16px",
            fontSize: "16px",
            cursor: isGridValid() ? "pointer" : "not-allowed",
            opacity: isGridValid() ? 1 : 0.5
          }}
        >
          Solve Sudoku
        </button>
        <button
          onClick={() => {
            const preset = samplePuzzle.map(row => [...row])
            setInitialGrid(preset)
            setGrid(preset)
            setSolvedGrid(null)
            validateGrid(preset)
          }}
        >
          Load Sample Puzzle
        </button>
      </div>
    </div>
  );

}

export default App;
