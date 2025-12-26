import { useState } from "react";

function App() {
  const emptyGrid = Array.from({ length: 9 }, () =>
    Array(9).fill(0)
  );

  const [solved, setSolved] = useState(false);
  const [board, setBoard] = useState(emptyGrid);
  const [initialBoard, setInitialBoard] = useState(emptyGrid);

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

  async function solveSudoku() {
    const response = await fetch("http://127.0.0.1:8000/solve", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ board })
    });

    const data = await response.json();

    if (data.solved) {
      setBoard(data.board);
      setSolved(true);
    }

  }


  return (
    <div style={{ padding: "20px" }}>
      <h1>Sudoku Solver</h1>

      <table>
        <tbody>
          {board.map((row, r) => (
            <tr key={r}>
              {row.map((cell, c) => {
                const isOriginal = initialBoard[r][c] !== 0;
                const isSolvedCell =
                  solved && initialBoard[r][c] === 0 && board[r][c] !== 0;

                return (
                  <td key={c}>
                    <input
                      type="text"
                      inputMode="numeric"
                      maxLength={1}
                      value={cell === 0 ? "" : cell}
                      disabled={isSolvedCell}
                      onChange={(e) => {
                        const v = e.target.value;

                        if (v === "" || /^[1-9]$/.test(v)) {
                          const value = v === "" ? 0 : Number(v);

                          const newBoard = board.map(row => [...row]);
                          const newInitial = initialBoard.map(row => [...row]);

                          newBoard[r][c] = value;
                          newInitial[r][c] = value;

                          setBoard(newBoard);
                          setInitialBoard(newInitial);
                          setSolved(false);
                        }
                      }}
                      style={{
                        width: "42px",
                        height: "42px",
                        textAlign: "center",
                        fontSize: "20px",
                        fontWeight: isOriginal ? "bold" : "normal",
                        color: "#ffffff",
                        caretColor: "#ffffff",
                        backgroundColor: isOriginal ? "#7c3aed" : "#1f1f1f",
                        borderTop:
                          r % 3 === 0 ? "3px solid #f5f5f5" : "1px solid #888",
                        borderLeft:
                          c % 3 === 0 ? "3px solid #f5f5f5" : "1px solid #888",
                        borderRight:
                          c === 8 ? "3px solid #f5f5f5" : "1px solid #888",
                        borderBottom:
                          r === 8 ? "3px solid #f5f5f5" : "1px solid #888",
                        outline: "none",
                        boxSizing: "border-box"
                      }}
                    />
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>

      <div style={{ marginTop: "20px" }}>
        <button onClick={solveSudoku} style={{ marginRight: "10px" }}>
          Solve
        </button>

        <button
          onClick={() => {
            const sample = samplePuzzle.map(row => [...row]);
            setBoard(sample);
            setInitialBoard(sample);
            setSolved(false);
          }}
        >
          Load Sample Puzzle
        </button>
      </div>
    </div>
  );

}

export default App;
